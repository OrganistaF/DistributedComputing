#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/socket.h>
#include <stdbool.h>

#define TCP_PORT 5000
#define UDP_PORT 5001
#define MAX_PLAYERS 2
#define BOARD_SIZE 3

// Valid users
const char *valid_users[][2] = {
    {"user1", "1234"},
    {"user2", "5678"}
};

// Game state
typedef enum {
    GAME_ACTIVE,
    GAME_WIN_X,
    GAME_WIN_O,
    GAME_DRAW
} GameResult;

typedef struct {
    char board[BOARD_SIZE][BOARD_SIZE];
    char current_player;
    int player_sockets[MAX_PLAYERS];
    struct sockaddr_in player_udp[MAX_PLAYERS];
    int active;
    pthread_mutex_t lock;
} GameState;

GameState game_state;

int authenticate_user(char *username, char *password) {
    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (strcmp(username, valid_users[i][0]) == 0 &&
            strcmp(password, valid_users[i][1]) == 0) {
            return 1;
        }
    }
    return 0;
}

void init_game() {
    memset(&game_state, 0, sizeof(game_state));
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            game_state.board[i][j] = ' ';
        }
    }
    game_state.current_player = 'X';
    game_state.active = 0;
    for (int i = 0; i < MAX_PLAYERS; i++) {
        game_state.player_sockets[i] = -1;
    }
    pthread_mutex_init(&game_state.lock, NULL);
}

void *handle_client(void *arg) {
    int client_socket = *(int *)arg;
    free(arg);

    char buffer[1024] = {0};
    char username[50], password[50];

    int bytes = read(client_socket, buffer, sizeof(buffer));
    printf("Received from client: %s\n", buffer);
    sscanf(buffer, "%s %s", username, password);

    if (authenticate_user(username, password)) {
        printf("Player authenticated: %s\n", username);
        write(client_socket, "OK\n", 3);
        char udp_info[50];
        snprintf(udp_info, sizeof(udp_info), "UDP_PORT %d\n", UDP_PORT);
        write(client_socket, udp_info, strlen(udp_info));

        // Assign symbol based on connection order.
        int player_num;
        pthread_mutex_lock(&game_state.lock);
        player_num = game_state.active;
        game_state.active++;
        pthread_mutex_unlock(&game_state.lock);

        char symbol_msg[20];
        if (player_num == 0) {
            snprintf(symbol_msg, sizeof(symbol_msg), "SYMBOL X\n");
        } else {
            snprintf(symbol_msg, sizeof(symbol_msg), "SYMBOL O\n");
        }
        write(client_socket, symbol_msg, strlen(symbol_msg));

        memset(buffer, 0, sizeof(buffer));
        read(client_socket, buffer, sizeof(buffer));
        printf("Received UDP_READY: %s\n", buffer);
        int udp_port;
        sscanf(buffer, "UDP_READY %d", &udp_port);

        struct sockaddr_in udp_addr;
        socklen_t addr_len = sizeof(udp_addr);
        getpeername(client_socket, (struct sockaddr*)&udp_addr, &addr_len);
        udp_addr.sin_port = htons(udp_port);

        pthread_mutex_lock(&game_state.lock);
        game_state.player_udp[player_num] = udp_addr;
        game_state.player_sockets[player_num] = socket(AF_INET, SOCK_DGRAM, 0);
        printf("[Server] Player %d UDP ready on port %d\n", player_num, udp_port);
        if (game_state.active == MAX_PLAYERS) {
            printf("[Server] Both players connected, sending START message.\n");
            for (int i = 0; i < MAX_PLAYERS; i++) {
                char start_msg[] = "START\n";
                printf("[Server] Sending START to player %d at %s:%d\n", i,
                       inet_ntoa(game_state.player_udp[i].sin_addr),
                       ntohs(game_state.player_udp[i].sin_port));
                sendto(game_state.player_sockets[i], start_msg, strlen(start_msg), 0,
                       (struct sockaddr*)&game_state.player_udp[i], sizeof(game_state.player_udp[i]));
            }
            // Do NOT reinitialize game state here, so that turn information remains valid.
        }
        pthread_mutex_unlock(&game_state.lock);
    } else {
        write(client_socket, "ERROR\n", 6);
    }
    close(client_socket);
    return NULL;
}

int main() {
    int tcp_fd, udp_fd;
    struct sockaddr_in tcp_addr, udp_addr;
    int addrlen = sizeof(tcp_addr);

    init_game();

    tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
    tcp_addr.sin_family = AF_INET;
    tcp_addr.sin_addr.s_addr = INADDR_ANY;
    tcp_addr.sin_port = htons(TCP_PORT);
    bind(tcp_fd, (struct sockaddr *)&tcp_addr, sizeof(tcp_addr));
    listen(tcp_fd, MAX_PLAYERS);

    udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    udp_addr.sin_family = AF_INET;
    udp_addr.sin_addr.s_addr = INADDR_ANY;
    udp_addr.sin_port = htons(UDP_PORT);
    bind(udp_fd, (struct sockaddr *)&udp_addr, sizeof(udp_addr));

    printf("Server waiting for connections...\n");
    printf("TCP port: %d, UDP port: %d\n", TCP_PORT, UDP_PORT);

    while (1) {
        int *client_socket = malloc(sizeof(int));
        *client_socket = accept(tcp_fd, (struct sockaddr *)&tcp_addr, (socklen_t*)&addrlen);
        pthread_t tid;
        pthread_create(&tid, NULL, handle_client, client_socket);
        pthread_detach(tid);
    }

    close(tcp_fd);
    close(udp_fd);
    return 0;
}

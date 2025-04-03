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
    pthread_mutex_init(&game_state.lock, NULL);
}

void broadcast_message(int udp_fd, const char *message) {
    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (game_state.player_udp[i].sin_port != 0) {
            sendto(udp_fd, message, strlen(message), 0,
                   (struct sockaddr*)&game_state.player_udp[i],
                   sizeof(game_state.player_udp[i]));
        }
    }
}

void check_winner(int udp_fd) {
    // Check rows, columns, and diagonals for a winner
    char winner = ' ';
    // ... (Implement win checking logic here)

    GameResult result = GAME_ACTIVE;
    if (winner != ' ') {
        result = (winner == 'X') ? GAME_WIN_X : GAME_WIN_O;
    } else if (/* Check for draw */) {
        result = GAME_DRAW;
    }

    if (result != GAME_ACTIVE) {
        char msg[50];
        snprintf(msg, sizeof(msg), "GAME_OVER %d %d %c\n", row, col, winner);
        broadcast_message(udp_fd, msg);
        init_game(); // Reset for new game
    }
}

void *udp_listener(void *arg) {
    int udp_fd = *(int *)arg;
    char buffer[1024];
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);

    while (1) {
        ssize_t bytes = recvfrom(udp_fd, buffer, sizeof(buffer)-1, 0,
                                (struct sockaddr*)&client_addr, &addr_len);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            pthread_mutex_lock(&game_state.lock);
            // Example: Handle MOVE command from client
            if (strncmp(buffer, "MOVE", 4) == 0) {
                int row, col;
                char symbol;
                sscanf(buffer, "MOVE %d %d %c", &row, &col, &symbol);
                if (row >= 0 && row < BOARD_SIZE && col >=0 && col < BOARD_SIZE &&
                    game_state.board[row][col] == ' ' &&
                    game_state.current_player == symbol) {
                    game_state.board[row][col] = symbol;
                    game_state.current_player = (symbol == 'X') ? 'O' : 'X';
                    // Broadcast the move to all players
                    char msg[50];
                    snprintf(msg, sizeof(msg), "MOVE %d %d %c\n", row, col, symbol);
                    broadcast_message(udp_fd, msg);
                    check_winner(udp_fd);
                }
            }
            pthread_mutex_unlock(&game_state.lock);
        }
    }
    return NULL;
}

void *handle_client(void *arg) {
    int client_socket = *(int *)arg;
    free(arg);
    char buffer[1024];
    char username[50], password[50];

    read(client_socket, buffer, sizeof(buffer));
    sscanf(buffer, "%s %s", username, password);

    if (authenticate_user(username, password)) {
        write(client_socket, "OK\n", 3);
        write(client_socket, "UDP_PORT 5001\n", 14);

        int player_num;
        pthread_mutex_lock(&game_state.lock);
        player_num = game_state.active;
        game_state.active++;
        pthread_mutex_unlock(&game_state.lock);

        char symbol_msg[20];
        snprintf(symbol_msg, sizeof(symbol_msg), "SYMBOL %c\n", (player_num == 0) ? 'X' : 'O');
        write(client_socket, symbol_msg, strlen(symbol_msg));

        // Read client's UDP port
        read(client_socket, buffer, sizeof(buffer));
        int udp_port;
        sscanf(buffer, "UDP_READY %d", &udp_port);

        // Get client's IP from TCP connection
        struct sockaddr_in tcp_addr;
        socklen_t tcp_len = sizeof(tcp_addr);
        getpeername(client_socket, (struct sockaddr*)&tcp_addr, &tcp_len);
        // Set UDP address for the client
        game_state.player_udp[player_num] = tcp_addr;
        game_state.player_udp[player_num].sin_port = htons(udp_port);

        // Start game if both players are ready
        if (game_state.active == MAX_PLAYERS) {
            broadcast_message(udp_fd, "START\n");
        }
    } else {
        write(client_socket, "ERROR\n", 6);
    }
    close(client_socket);
    return NULL;
}

int main() {
    int tcp_fd, udp_fd;
    struct sockaddr_in addr;
    init_game();

    // TCP setup
    tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
    addr.sin_family = AF_INET;
    addr.sin_port = htons(TCP_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    bind(tcp_fd, (struct sockaddr*)&addr, sizeof(addr));
    listen(tcp_fd, MAX_PLAYERS);

    // UDP setup
    udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    addr.sin_port = htons(UDP_PORT);
    bind(udp_fd, (struct sockaddr*)&addr, sizeof(addr));

    // Start UDP listener thread
    pthread_t tid;
    pthread_create(&tid, NULL, udp_listener, &udp_fd);
    pthread_detach(tid);

    printf("Server running...\n");
    while (1) {
        int *client_sock = malloc(sizeof(int));
        *client_sock = accept(tcp_fd, NULL, NULL);
        pthread_create(&tid, NULL, handle_client, client_sock);
        pthread_detach(tid);
    }

    close(tcp_fd);
    close(udp_fd);
    return 0;
}

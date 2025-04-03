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

const char *valid_users[][2] = {
    {"user1", "1234"},
    {"user2", "5678"}
};

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

GameResult check_winner(GameState *game) {
    // Check rows
    for (int i = 0; i < BOARD_SIZE; i++) {
        if (game->board[i][0] != ' ' &&
            game->board[i][0] == game->board[i][1] &&
            game->board[i][1] == game->board[i][2]) {
            return (game->board[i][0] == 'X') ? GAME_WIN_X : GAME_WIN_O;
        }
    }

    // Check columns
    for (int j = 0; j < BOARD_SIZE; j++) {
        if (game->board[0][j] != ' ' &&
            game->board[0][j] == game->board[1][j] &&
            game->board[1][j] == game->board[2][j]) {
            return (game->board[0][j] == 'X') ? GAME_WIN_X : GAME_WIN_O;
        }
    }

    // Check diagonals
    if (game->board[0][0] != ' ' &&
        game->board[0][0] == game->board[1][1] &&
        game->board[1][1] == game->board[2][2]) {
        return (game->board[0][0] == 'X') ? GAME_WIN_X : GAME_WIN_O;
    }
    if (game->board[0][2] != ' ' &&
        game->board[0][2] == game->board[1][1] &&
        game->board[1][1] == game->board[2][0]) {
        return (game->board[0][2] == 'X') ? GAME_WIN_X : GAME_WIN_O;
    }

    // Check for draw
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (game->board[i][j] == ' ') {
                return GAME_ACTIVE;
            }
        }
    }
    return GAME_DRAW;
}

void *udp_handler(void *arg) {
    int udp_fd = *(int *)arg;
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    char buffer[1024];

    while (1) {
        ssize_t bytes = recvfrom(udp_fd, buffer, sizeof(buffer) - 1, 0, (struct sockaddr*)&client_addr, &addr_len);
        if (bytes <= 0) continue;
        buffer[bytes] = '\0';

        if (strncmp(buffer, "MOVE", 4) == 0) {
            int row, col;
            if (sscanf(buffer, "MOVE %d %d", &row, &col) != 2) continue;

            pthread_mutex_lock(&game_state.lock);

            // Find player index
            int player_index = -1;
            for (int i = 0; i < MAX_PLAYERS; i++) {
                if (memcmp(&client_addr.sin_addr, &game_state.player_udp[i].sin_addr, sizeof(struct in_addr)) == 0 &&
                    client_addr.sin_port == game_state.player_udp[i].sin_port) {
                    player_index = i;
                    break;
                }
            }

            if (player_index == -1 || player_index >= game_state.active) {
                pthread_mutex_unlock(&game_state.lock);
                continue;
            }

            char player_symbol = (player_index == 0) ? 'X' : 'O';
            if (game_state.current_player != player_symbol) {
                pthread_mutex_unlock(&game_state.lock);
                continue;
            }

            if (row < 0 || row >= BOARD_SIZE || col < 0 || col >= BOARD_SIZE || game_state.board[row][col] != ' ') {
                pthread_mutex_unlock(&game_state.lock);
                continue;
            }

            game_state.board[row][col] = player_symbol;
            GameResult result = check_winner(&game_state);

            // Broadcast move
            char move_msg[50];
            snprintf(move_msg, sizeof(move_msg), "MOVE %d %d %c\n", row, col, player_symbol);
            for (int i = 0; i < MAX_PLAYERS; i++) {
                if (game_state.player_sockets[i] != -1) {
                    sendto(game_state.player_sockets[i], move_msg, strlen(move_msg), 0,
                           (struct sockaddr*)&game_state.player_udp[i], sizeof(game_state.player_udp[i]));
                }
            }

            if (result != GAME_ACTIVE) {
                char result_msg[50];
                const char *res_str = result == GAME_WIN_X ? "X" : result == GAME_WIN_O ? "O" : "DRAW";
                snprintf(result_msg, sizeof(result_msg), "GAME_OVER %s %d %d %c\n", res_str, row, col, player_symbol);
                for (int i = 0; i < MAX_PLAYERS; i++) {
                    if (game_state.player_sockets[i] != -1) {
                        sendto(game_state.player_sockets[i], result_msg, strlen(result_msg), 0,
                               (struct sockaddr*)&game_state.player_udp[i], sizeof(game_state.player_udp[i]));
                    }
                }
                init_game(); // Reset for new game
            } else {
                game_state.current_player = (player_symbol == 'X') ? 'O' : 'X';
            }

            pthread_mutex_unlock(&game_state.lock);
        }
    }
    return NULL;
}

void *handle_client(void *arg) {
    int client_socket = *(int *)arg;
    free(arg);
    char buffer[1024] = {0};
    char username[50], password[50];

    int bytes = read(client_socket, buffer, sizeof(buffer));
    sscanf(buffer, "%s %s", username, password);

    if (authenticate_user(username, password)) {
        write(client_socket, "OK\n", 3);
        char udp_info[50];
        snprintf(udp_info, sizeof(udp_info), "UDP_PORT %d\n", UDP_PORT);
        write(client_socket, udp_info, strlen(udp_info));

        int player_num;
        pthread_mutex_lock(&game_state.lock);
        player_num = game_state.active;
        game_state.active++;
        pthread_mutex_unlock(&game_state.lock);

        char symbol_msg[20];
        snprintf(symbol_msg, sizeof(symbol_msg), "SYMBOL %c\n", (player_num == 0) ? 'X' : 'O');
        write(client_socket, symbol_msg, strlen(symbol_msg));

        read(client_socket, buffer, sizeof(buffer));
        int udp_port;
        sscanf(buffer, "UDP_READY %d", &udp_port);

        struct sockaddr_in udp_addr;
        socklen_t addr_len = sizeof(udp_addr);
        getpeername(client_socket, (struct sockaddr*)&udp_addr, &addr_len);
        udp_addr.sin_port = htons(udp_port);

        pthread_mutex_lock(&game_state.lock);
        game_state.player_udp[player_num] = udp_addr;
        game_state.player_sockets[player_num] = socket(AF_INET, SOCK_DGRAM, 0);

        if (game_state.active == MAX_PLAYERS) {
            printf("Both players connected, sending START.\n");
            for (int i = 0; i < MAX_PLAYERS; i++) {
                sendto(game_state.player_sockets[i], "START\n", 6, 0,
                       (struct sockaddr*)&game_state.player_udp[i], sizeof(game_state.player_udp[i]));
            }
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

    pthread_t udp_thread;
    pthread_create(&udp_thread, NULL, udp_handler, &udp_fd);
    pthread_detach(udp_thread);

    printf("Server running...\n");
    while (1) {
        int *client_socket = malloc(sizeof(int));
        *client_socket = accept(tcp_fd, NULL, NULL);
        pthread_t tid;
        pthread_create(&tid, NULL, handle_client, client_socket);
        pthread_detach(tid);
    }

    close(tcp_fd);
    close(udp_fd);
    return 0;
}
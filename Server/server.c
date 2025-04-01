#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <sys/select.h>
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
}

GameResult check_game_state() {
    char board[BOARD_SIZE][BOARD_SIZE];
    memcpy(board, game_state.board, sizeof(board));

    // Check rows
    for (int i = 0; i < BOARD_SIZE; i++) {
        if (board[i][0] != ' ' && board[i][0] == board[i][1] && board[i][1] == board[i][2]) {
            return (board[i][0] == 'X') ? GAME_WIN_X : GAME_WIN_O;
        }
    }

    // Check columns
    for (int j = 0; j < BOARD_SIZE; j++) {
        if (board[0][j] != ' ' && board[0][j] == board[1][j] && board[1][j] == board[2][j]) {
            return (board[0][j] == 'X') ? GAME_WIN_X : GAME_WIN_O;
        }
    }

    // Check diagonals
    if (board[0][0] != ' ' && board[0][0] == board[1][1] && board[1][1] == board[2][2]) {
        return (board[0][0] == 'X') ? GAME_WIN_X : GAME_WIN_O;
    }
    if (board[0][2] != ' ' && board[0][2] == board[1][1] && board[1][1] == board[2][0]) {
        return (board[0][2] == 'X') ? GAME_WIN_X : GAME_WIN_O;
    }

    // Check for draw
    bool is_draw = true;
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == ' ') {
                is_draw = false;
                break;
            }
        }
        if (!is_draw) break;
    }

    return is_draw ? GAME_DRAW : GAME_ACTIVE;
}

void handle_move(int player_num, int row, int col) {
    if (player_num == 0 && game_state.current_player != 'X') return;
    if (player_num == 1 && game_state.current_player != 'O') return;

    if (row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE &&
        game_state.board[row][col] == ' ') {
        game_state.board[row][col] = game_state.current_player;

        GameResult result = check_game_state();

        char move_msg[64];
        if (result == GAME_ACTIVE) {
            game_state.current_player = (game_state.current_player == 'X') ? 'O' : 'X';
            snprintf(move_msg, sizeof(move_msg), "MOVE %d %d %c", row, col, game_state.board[row][col]);
        } else {
            const char* result_str;
            switch(result) {
                case GAME_WIN_X: result_str = "X"; break;
                case GAME_WIN_O: result_str = "O"; break;
                case GAME_DRAW: result_str = "DRAW"; break;
                default: result_str = "UNKNOWN";
            }
            snprintf(move_msg, sizeof(move_msg), "GAME_OVER %s %d %d %c", result_str, row, col, game_state.board[row][col]);
            game_state.active = 0;
        }

        for (int i = 0; i < MAX_PLAYERS; i++) {
            if (game_state.player_sockets[i] != -1) {
                sendto(game_state.player_sockets[i], move_msg, strlen(move_msg), 0,
                      (struct sockaddr*)&game_state.player_udp[i], sizeof(game_state.player_udp[i]));
            }
        }
    }
}

void handle_client(int client_socket, int player_num) {
    char buffer[1024] = {0};
    char username[50], password[50];

    read(client_socket, buffer, 1024);
    sscanf(buffer, "%s %s", username, password);

    if (authenticate_user(username, password)) {
        write(client_socket, "OK", 2);
        printf("Player %d authenticated: %s\n", player_num, username);

        char udp_info[50];
        snprintf(udp_info, sizeof(udp_info), "UDP_PORT %d", UDP_PORT);
        write(client_socket, udp_info, strlen(udp_info));

        read(client_socket, buffer, 1024);

        struct sockaddr_in udp_addr;
        socklen_t addr_len = sizeof(udp_addr);
        getpeername(client_socket, (struct sockaddr*)&udp_addr, &addr_len);

        int udp_port;
        sscanf(buffer, "UDP_READY %d", &udp_port);
        udp_addr.sin_port = htons(udp_port);

        game_state.player_udp[player_num] = udp_addr;
        game_state.player_sockets[player_num] = socket(AF_INET, SOCK_DGRAM, 0);
        game_state.active++;

        printf("Player %d UDP ready on port %d\n", player_num, udp_port);

        if (game_state.active == MAX_PLAYERS) {
            printf("Game starting!\n");
            for (int i = 0; i < MAX_PLAYERS; i++) {
                char start_msg[] = "START";
                sendto(game_state.player_sockets[i], start_msg, strlen(start_msg), 0,
                      (struct sockaddr*)&game_state.player_udp[i], sizeof(game_state.player_udp[i]));
            }
            init_game();
        }
    } else {
        write(client_socket, "ERROR", 5);
    }

    close(client_socket);
    exit(0);
}

int main() {
    int tcp_fd, udp_fd;
    struct sockaddr_in tcp_addr, udp_addr;
    int addrlen = sizeof(tcp_addr);
    int player_count = 0;
    pid_t child_pids[MAX_PLAYERS] = {0};

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

    while (player_count < MAX_PLAYERS) {
        int client_socket = accept(tcp_fd, (struct sockaddr *)&tcp_addr, (socklen_t*)&addrlen);

        pid_t pid = fork();
        if (pid == 0) {
            close(tcp_fd);
            close(udp_fd);
            handle_client(client_socket, player_count);
        } else if (pid > 0) {
            child_pids[player_count] = pid;
            player_count++;
            printf("Players connected: %d/%d\n", player_count, MAX_PLAYERS);
        } else {
            perror("fork failed");
            close(client_socket);
        }
    }

    fd_set read_fds;
    struct timeval tv;

    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(udp_fd, &read_fds);

        tv.tv_sec = 1;
        tv.tv_usec = 0;

        int retval = select(udp_fd + 1, &read_fds, NULL, NULL, &tv);

        if (retval == -1) {
            perror("select");
        } else if (retval) {
            char buffer[1024];
            struct sockaddr_in client_addr;
            socklen_t client_len = sizeof(client_addr);

            int n = recvfrom(udp_fd, buffer, sizeof(buffer), 0,
                            (struct sockaddr*)&client_addr, &client_len);

            if (n > 0) {
                buffer[n] = '\0';
                printf("Received UDP: %s\n", buffer);

                int row, col, player_num = -1;

                for (int i = 0; i < MAX_PLAYERS; i++) {
                    if (memcmp(&client_addr, &game_state.player_udp[i], sizeof(client_addr)) == 0) {
                        player_num = i;
                        break;
                    }
                }

                if (player_num != -1 && sscanf(buffer, "MOVE %d %d", &row, &col) == 2) {
                    handle_move(player_num, row, col);
                }
            }
        }
    }

    close(tcp_fd);
    close(udp_fd);
    return 0;
}

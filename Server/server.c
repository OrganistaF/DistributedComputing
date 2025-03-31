#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/wait.h>

#define PORT 5000
#define MAX_PLAYERS 2

//usuarios validos 
const char *valid_users[][2] = {
    {"user1", "1234"},
    {"user2", "5678"}
};

int authenticate_user(char *username, char *password) {
    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (strcmp(username, valid_users[i][0]) == 0 && 
            strcmp(password, valid_users[i][1]) == 0) {
            return 1;
        }
    }
    return 0;
}

/**
 * maneja la conexion con un cliente (jugador)
 * @param client_socket socket del cliente
 */
void handle_client(int client_socket, int player_num) {
    char buffer[1024] = {0};
    char username[50], password[50];
    
    //recibe las credenciales
    read(client_socket, buffer, 1024);
    sscanf(buffer, "%s %s", username, password);
    
    //valida
    if (authenticate_user(username, password)) {
        write(client_socket, "OK", 2);
        printf("Jugador %d autenticado: %s\n", player_num, username);
        
        // Esperar señal READY
        char status[10];
        read(client_socket, status, sizeof(status));
        if (strcmp(status, "READY") == 0) {
            printf("Jugador %d (%s) recibió READY\n", player_num, username);
        }
    } else {
        write(client_socket, "ERROR", 5); //credenciales invalidas
    }
    
    close(client_socket);
    // El hijo debe terminar después de manejar al cliente
    exit(0);
}

int main() {
    int server_fd, client_sockets[MAX_PLAYERS] = {0};
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    int player_count = 0;
    pid_t child_pids[MAX_PLAYERS] = {0};
    
    //crear el socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    //configurar y aceptar las conexiones
    bind(server_fd, (struct sockaddr *)&address, sizeof(address));
    listen(server_fd, MAX_PLAYERS);
    
    printf("Servidor esperando conexiones...\n");
    
    // Aceptar conexiones hasta tener MAX_PLAYERS
    while (player_count < MAX_PLAYERS) {
        client_sockets[player_count] = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        
        //crear proceso hijo para cada jugador
        pid_t pid = fork();
        if (pid == 0) { // Proceso hijo
            close(server_fd);
            handle_client(client_sockets[player_count], player_count+1);
        } else if (pid > 0) { // Proceso padre
            child_pids[player_count] = pid;
            player_count++;
            printf("Jugadores conectados: %d/%d\n", player_count, MAX_PLAYERS);
        } else {
            perror("Error al crear proceso hijo");
            close(client_sockets[player_count]);
        }
    }
    
    // cuando haya dos juagdores manda mensaje
    if (player_count == MAX_PLAYERS) {
        printf("¡Partida lista! Notificando a todos los jugadores...\n");
        for (int i = 0; i < MAX_PLAYERS; i++) {
            write(client_sockets[i], "READY", 5);
            printf("Notificación enviada al jugador %d\n", i+1);
            
            // Esperar confirmación del hijo antes de cerrar
            int status;
            waitpid(child_pids[i], &status, 0);
        }
    }

    // Mantener el servidor activo
    while (1) {
        sleep(1); 
    }
    
    
    return 0;
}

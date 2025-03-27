#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>

#define PORT 5000
#define BUFFER_SIZE 1024

// Credenciales válidas
const char *USERNAME1 = "user1";
const char *PASSWORD1 = "1234";
const char *USERNAME2 = "user2";
const char *PASSWORD2 = "5678";

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};
    char response[100];

    // Crear socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        perror("Error al crear el socket");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Asociar socket al puerto
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Error al enlazar");
        exit(EXIT_FAILURE);
    }

    // Escuchar conexiones entrantes
    if (listen(server_fd, 5) < 0) {
        perror("Error al escuchar");
        exit(EXIT_FAILURE);
    }

    printf("Servidor esperando conexiones en el puerto %d...\n", PORT);

    while (1) {
        // Aceptar nueva conexión
        new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (new_socket < 0) {
            perror("Error al aceptar conexión");
            continue;  // No detener el servidor si hay un error
        }

        // Crear un proceso hijo con fork
        pid_t pid = fork();
        
        if (pid < 0) {
            perror("Error al crear proceso hijo");
            close(new_socket);
            continue;
        }

        if (pid == 0) {  // Proceso hijo
            close(server_fd);  // El hijo no necesita el socket del servidor
            
            // Leer datos del cliente
            read(new_socket, buffer, sizeof(buffer));
            printf("Datos recibidos: %s\n", buffer);

            char user[50], pass[50];
            sscanf(buffer, "%s %s", user, pass);

            // Validar credenciales
            if ((strcmp(user, USERNAME1) == 0 && strcmp(pass, PASSWORD1) == 0) ||
                (strcmp(user, USERNAME2) == 0 && strcmp(pass, PASSWORD2) == 0)) {
                strcpy(response, "OK");
                printf("Cliente autenticado: %s\n", user);
            } else {
                strcpy(response, "ERROR");
                printf("Autenticación fallida\n");
            }

            // Enviar respuesta al cliente
            send(new_socket, response, strlen(response), 0);
            printf("Respuesta enviada: %s\n", response);

            close(new_socket);  // Cerrar conexión con el cliente
            exit(0);  // Terminar proceso hijo
        } else {
            // Proceso padre: cerrar el socket del cliente y seguir esperando más conexiones
            close(new_socket);
        }
    }

    close(server_fd);
    return 0;
}

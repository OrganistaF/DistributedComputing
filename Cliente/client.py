import socket

# Configuración del servidor
HOST = "127.18.2.2"
PORT = 5000

def send_credentials(username, password):
    """Envía las credenciales al servidor y devuelve la respuesta."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        # Enviar credenciales
        credentials = f"{username} {password}"
        client_socket.send(credentials.encode())

        # Recibir respuesta
        response = client_socket.recv(1024).decode()
        client_socket.close()

        return "dentro" if response == "OK" else "Credenciales incorrectas"

    except ConnectionRefusedError:
        return "Error de conexión"

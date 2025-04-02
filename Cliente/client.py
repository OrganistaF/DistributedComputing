import socket

HOST = "127.18.2.2"
PORT = 5000

def send_credentials(username, password):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(f"{username} {password}".encode())
            
            # Primera respuesta (OK/ERROR)
            response = s.recv(1024).decode()
            if response == "OK":
                print("Autenticado. Esperando inicio de partida...")
                
                # Esperar segunda notificación (READY)
                status = s.recv(1024).decode()
                if status == "READY":
                    print("¡Partida lista! Iniciando juego...")
                    # Devolver estado y username
                    return True, "READY", username
            return False, "Error de autenticación", ""
    except Exception as e:
        return False, f"Error: {str(e)}", ""
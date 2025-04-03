import socket
import threading


class TicTacToeClient:
    def __init__(self, host="127.18.2.2", tcp_port=5000, udp_port=5001):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.game_active = False
        self.player_symbol = None
        self.current_turn = None
        self.gui_callback = None
        self.username = ""

    def connect(self, username, password):
        self.username = username
        try:
            self.tcp_socket.connect((self.host, self.tcp_port))
            self.tcp_socket.sendall(f"{username} {password}".encode())

            response = self.tcp_socket.recv(1024).decode()
            if response == "OK":
                print("Authenticated. Getting UDP info...")

                udp_info = self.tcp_socket.recv(1024).decode()
                if udp_info.startswith("UDP_PORT"):
                    self.udp_port = int(udp_info.split()[1])

                    self.udp_socket.bind(('0.0.0.0', 0))
                    local_udp_port = self.udp_socket.getsockname()[1]

                    self.tcp_socket.sendall(f"UDP_READY {local_udp_port}".encode())

                    threading.Thread(target=self.udp_listener, daemon=True).start()
                    return True, "Authentication successful"
            return False, "Authentication failed"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def udp_listener(self):
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                message = data.decode()
                print(f"Received UDP message: {message}")

                if message == "START":
                    self.game_active = True
                    self.player_symbol = 'X' if self.udp_socket.getsockname()[1] % 2 == 0 else 'O'
                    self.current_turn = 'X'
                    print(f"Game started! You are player {self.player_symbol}")
                    if self.gui_callback:
                        self.gui_callback('start', None, None, None)

                elif message.startswith("MOVE"):
                    parts = message.split()
                    row, col, symbol = int(parts[1]), int(parts[2]), parts[3]
                    self.current_turn = self.player_symbol
                    if self.gui_callback:
                        self.gui_callback('move', row, col, symbol)

                elif message.startswith("GAME_OVER"):
                    parts = message.split()
                    result = parts[1]
                    row, col, symbol = int(parts[2]), int(parts[3]), parts[4]

                    self.game_active = False
                    if self.gui_callback:
                        self.gui_callback('game_over', result, row, col, symbol)

            except Exception as e:
                print(f"UDP error: {str(e)}")
                break

    def send_move(self, row, col):
        if self.game_active and self.current_turn == self.player_symbol:
            message = f"MOVE {row} {col}"
            self.udp_socket.sendto(message.encode(), (self.host, self.udp_port))
            self.current_turn = 'O' if self.player_symbol == 'X' else 'X'
            return True
        return False

    def close(self):
        self.tcp_socket.close()
        self.udp_socket.close()
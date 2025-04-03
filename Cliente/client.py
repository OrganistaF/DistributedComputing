import socket
import threading


class TicTacToeClient:
    def __init__(self, host="127.0.0.1", tcp_port=5000, udp_port=5001):
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
            print(f"Attempting to connect to {self.host}:{self.tcp_port}")
            self.tcp_socket.connect((self.host, self.tcp_port))
            self.tcp_socket.sendall(f"{username} {password}\n".encode())
            print("Credentials sent, waiting for server response...")

            response = self._readline(self.tcp_socket)
            print(f"Received: {response}")
            if response.strip() == "OK":
                udp_info = self._readline(self.tcp_socket)
                print(f"Received UDP info: {udp_info}")
                if udp_info.startswith("UDP_PORT"):
                    self.udp_port = int(udp_info.split()[1])
                    # Read the symbol assignment
                    symbol_line = self._readline(self.tcp_socket)
                    if symbol_line.startswith("SYMBOL"):
                        self.player_symbol = symbol_line.split()[1].strip()
                        print(f"Assigned symbol: {self.player_symbol}")
                    self.udp_socket.bind(('0.0.0.0', 0))
                    local_udp_port = self.udp_socket.getsockname()[1]
                    self.tcp_socket.sendall(f"UDP_READY {local_udp_port}\n".encode())
                    threading.Thread(target=self.udp_listener, daemon=True).start()
                    return True, "Authentication successful"
            print("Authentication failed or invalid response.")
            return False, "Authentication failed"
        except Exception as e:
            print(f"Exception during connect: {str(e)}")
            return False, f"Error: {str(e)}"

    def _readline(self, sock):
        """Helper to read from the socket until a newline is encountered."""
        data = b""
        while True:
            chunk = sock.recv(1)
            if not chunk:
                break
            data += chunk
            if chunk == b'\n':
                break
        return data.decode()

    def udp_listener(self):
        while True:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                message = data.decode().strip()
                print(f"Received UDP message: {message}")

                if message == "START":
                    self.game_active = True
                    # Do not change self.player_symbol; use the symbol assigned by the server.
                    self.current_turn = 'X'  # The game starts with 'X'
                    print(f"Game started! You are player {self.player_symbol}")
                    if self.gui_callback:
                        self.gui_callback('start', None, None, None)

                elif message.startswith("MOVE"):
                    parts = message.split()
                    row, col, symbol = int(parts[1]), int(parts[2]), parts[3]
                    # Only update current_turn if the move comes from the opponent.
                    if symbol != self.player_symbol:
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
            message = f"MOVE {row} {col}\n"
            self.udp_socket.sendto(message.encode(), (self.host, self.udp_port))
            # Do not flip the turn locally; rely on the server's broadcast.
            return True
        return False

    def close(self):
        self.tcp_socket.close()
        self.udp_socket.close()
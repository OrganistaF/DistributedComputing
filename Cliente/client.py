import socket
import threading


class TicTacToeClient:
    def __init__(self, host="172.19.0.2", tcp_port=5000, udp_port=5001):
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
            # Send credentials terminated by newline
            self.tcp_socket.sendall(f"{username} {password}\n".encode())

            # Read response line (e.g., "OK")
            response = self._readline(self.tcp_socket)
            if response.strip() == "OK":
                print("Authenticated. Getting UDP info...")

                udp_info = self._readline(self.tcp_socket)
                if udp_info.startswith("UDP_PORT"):
                    self.udp_port = int(udp_info.split()[1])

                    # Bind UDP socket and send UDP_READY with newline
                    self.udp_socket.bind(('0.0.0.0', 0))
                    local_udp_port = self.udp_socket.getsockname()[1]
                    self.tcp_socket.sendall(f"UDP_READY {local_udp_port}\n".encode())

                    threading.Thread(target=self.udp_listener, daemon=True).start()
                    return True, "Authentication successful"
            return False, "Authentication failed"
        except Exception as e:
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
                    # Assume the server is the source of truth.
                    # Optionally, let the server send the assigned symbol.
                    if self.player_symbol is None:
                        # Fallback: decide based on local UDP port parity
                        self.player_symbol = 'X' if self.udp_socket.getsockname()[1] % 2 == 0 else 'O'
                    self.current_turn = 'X'
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
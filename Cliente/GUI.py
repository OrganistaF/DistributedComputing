import pygame
import sys
from pygame import mixer
from client import TicTacToeClient

# Initialize pygame and mixer
pygame.init()
mixer.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Game states
LOGIN = 0
MENU = 1
GAME = 2
END = 3
ABOUT = 4

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_SIZE = 3

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tic Tac Toe')

# Fonts
font_xl = pygame.font.Font(None, 100)
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 24)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, font=font_medium):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # Border

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


def load_image(name, scale=1.0):
    try:
        image = pygame.image.load(name)
        if scale != 1.0:
            new_width = int(image.get_width() * scale)
            new_height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image
    except:
        print(f"Image {name} not found. Using placeholder.")
        surf = pygame.Surface((100, 100))
        surf.fill(PURPLE if "x" in name.lower() else YELLOW if "o" in name.lower() else BLUE)
        return surf


class TicTacToeGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tic Tac Toe')

        self.lose_sound = None
        self.win_sound = None
        self.click_sound = None

        # Game variables
        self.current_player = 'X'
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game_state = LOGIN
        self.player_name = ''
        self.winner = None
        self.game_mode = None
        self.current_user = ""
        self.username = ""
        self.password = ""
        self.active_input = "username"
        self.message = ""

        # Images
        self.x_image = load_image('img/x.png', 0.8)
        self.o_image = load_image('img/o.png', 0.8)

        # Sounds
        try:
            self.click_sound = mixer.Sound('sfx/click.mp3')
            self.win_sound = mixer.Sound('sfx/win.mp3')
            self.lose_sound = mixer.Sound('sfx/lose.mp3')
        except:
            print("Sound files not found. Continuing without sound.")

        # Network client
        self.client = TicTacToeClient()
        self.client.gui_callback = self.handle_network_event

    def handle_network_event(self, event_type, *args):
        if event_type == 'start':
            self.game_state = GAME
            self.reset_game()
        elif event_type == 'move':
            row, col, symbol = args
            self.board[row][col] = symbol
            self.current_player = 'O' if symbol == 'X' else 'X'
        elif event_type == 'game_over':
            result, row, col, symbol = args
            self.board[row][col] = symbol
            self.winner = result if result != 'DRAW' else 'draw'
            self.game_state = END

    def reset_game(self):
        self.board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.winner = None

    def check_winner(self):
        """Check if there's a winner or a draw"""
        # Check rows
        for row in range(BOARD_SIZE):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != '':
                return self.board[row][0]

        # Check columns
        for col in range(BOARD_SIZE):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]

        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]

        # Check for draw
        if all(self.board[row][col] != '' for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)):
            return 'draw'

        return None

    def play_sound(self, sound):
        """Play a sound effect if available"""
        try:
            sound.play()
        except:
            pass

    def draw_login_screen(self):
        """Draw the login screen"""
        self.screen.fill(WHITE)

        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Login box
        login_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 180, 300, 300)
        pygame.draw.rect(self.screen, WHITE, login_box, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, login_box, 2, border_radius=15)

        # Title
        title = font_medium.render("Login", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(title, title_rect)

        # User
        username_label = font_small.render("Username:", True, BLACK)
        self.screen.blit(username_label, (SCREEN_WIDTH // 2 - 130, 260))

        username_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 290, 260, 40)
        pygame.draw.rect(self.screen, LIGHT_GRAY if self.active_input == "username" else WHITE,
                         username_rect, border_radius=5)
        pygame.draw.rect(self.screen, DARK_BLUE if self.active_input == "username" else BLACK,
                         username_rect, 2, border_radius=5)

        # Password
        password_label = font_small.render("Password:", True, BLACK)
        self.screen.blit(password_label, (SCREEN_WIDTH // 2 - 130, 340))

        password_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 370, 260, 40)
        pygame.draw.rect(self.screen, LIGHT_GRAY if self.active_input == "password" else WHITE,
                         password_rect, border_radius=5)
        pygame.draw.rect(self.screen, DARK_BLUE if self.active_input == "password" else BLACK,
                         password_rect, 2, border_radius=5)

        password_text = font_small.render("*" * len(self.password), True, BLACK)
        self.screen.blit(password_text, (password_rect.x + 10, password_rect.y + 10))

        # Login button
        login_button = Button(SCREEN_WIDTH // 2 - 100, 430, 200, 40, "Login", BLUE, DARK_BLUE)
        login_button.draw(self.screen)

        # Message after login
        if self.message:
            color = GREEN if self.message == "Login successful" else RED
            msg_text = font_small.render(self.message, True, color)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 530))
            self.screen.blit(msg_text, msg_rect)

        return login_button

    def draw_menu_screen(self):
        """Draw the main menu screen"""
        self.screen.fill(WHITE)

        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Welcome message
        welcome_text = font_large.render(f"Welcome, {self.current_user}!", True, WHITE)
        welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(welcome_text, welcome_rect)

        # Game title
        title = font_xl.render("Tic Tac Toe", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(title, title_rect)

        # Buttons
        local_button = Button(SCREEN_WIDTH // 2 - 150, 300, 300, 60, "Local Game", BLUE, DARK_BLUE)
        online_button = Button(SCREEN_WIDTH // 2 - 150, 380, 300, 60, "Online Game", GREEN, (0, 200, 0))
        about_button = Button(SCREEN_WIDTH // 2 - 150, 460, 300, 60, "About", PURPLE, (100, 0, 100))
        logout_button = Button(SCREEN_WIDTH // 2 - 150, 540, 300, 40, "Logout", RED, (200, 0, 0), font=font_small)

        local_button.draw(self.screen)
        online_button.draw(self.screen)
        about_button.draw(self.screen)
        logout_button.draw(self.screen)

        return local_button, online_button, about_button, logout_button

    def draw_about_screen(self):
        """Draw the about screen"""
        self.screen.fill(WHITE)

        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # About box
        about_box = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        pygame.draw.rect(self.screen, WHITE, about_box, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, about_box, 2, border_radius=15)

        # Title
        title = font_large.render("About Tic Tac Toe", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Content
        lines = [
            "Tic Tac Toe Game",
            "Created with Pygame",
            "Get 3 in a row to win!",
            "",
            "Ana Maria Guzman Solís",
            "Jorge Alberto Fong Alvarez",
            "Luis Felipe Organista Mendez",
            "Professor Dr. Juan Carlos Lopez Pimentel",
            "Distributed Computing",
        ]

        # Calculate if we need to adjust spacing for too much content
        total_height = len(lines) * 30
        available_height = SCREEN_HEIGHT - 350  # Approximate space between title and back button

        line_spacing = 30  # Default spacing
        if total_height > available_height:
            line_spacing = max(20, available_height // len(lines))  # Reduce spacing if needed, but not below 20

        for i, line in enumerate(lines):
            text = font_small.render(line, True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 220 + i * line_spacing))

        # Back button
        back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 120, 200, 50, "Back", BLUE, DARK_BLUE)
        back_button.draw(self.screen)

        return back_button

    def draw_game_screen(self):
        """Draw the game screen"""
        self.screen.fill(WHITE)

        # Draw game board
        board_size = 400
        board_x = (SCREEN_WIDTH - board_size) // 2
        board_y = (SCREEN_HEIGHT - board_size) // 2

        # Draw board background
        pygame.draw.rect(self.screen, LIGHT_GRAY, (board_x, board_y, board_size, board_size))

        # Draw grid lines
        cell_size = board_size // BOARD_SIZE
        for i in range(1, BOARD_SIZE):
            # Vertical lines
            pygame.draw.line(self.screen, BLACK, (board_x + i * cell_size, board_y),
                             (board_x + i * cell_size, board_y + board_size), 3)
            # Horizontal lines
            pygame.draw.line(self.screen, BLACK, (board_x, board_y + i * cell_size),
                             (board_x + board_size, board_y + i * cell_size), 3)

        # Draw X's and O's
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 'X':
                    x_pos = board_x + col * cell_size + cell_size // 2
                    y_pos = board_y + row * cell_size + cell_size // 2
                    if self.x_image:
                        x_rect = self.x_image.get_rect(center=(x_pos, y_pos))
                        self.screen.blit(self.x_image, x_rect)
                    else:
                        pygame.draw.line(self.screen, RED, (x_pos - 30, y_pos - 30), (x_pos + 30, y_pos + 30), 5)
                        pygame.draw.line(self.screen, RED, (x_pos + 30, y_pos - 30), (x_pos - 30, y_pos + 30), 5)
                elif self.board[row][col] == 'O':
                    x_pos = board_x + col * cell_size + cell_size // 2
                    y_pos = board_y + row * cell_size + cell_size // 2
                    if self.o_image:
                        o_rect = self.o_image.get_rect(center=(x_pos, y_pos))
                        self.screen.blit(self.o_image, o_rect)
                    else:
                        pygame.draw.circle(self.screen, BLUE, (x_pos, y_pos), 30, 5)

        # Draw current player indicator
        player_text = font_medium.render(f"Current Player: {self.current_player}", True, BLACK)
        self.screen.blit(player_text, (20, 20))

        # Draw back button
        back_button = Button(20, SCREEN_HEIGHT - 70, 150, 50, "Menu", RED, (200, 0, 0))
        back_button.draw(self.screen)

        return back_button

    def draw_end_screen(self):
        """Draw the end game screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Result box
        result_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(self.screen, WHITE, result_box, border_radius=15)
        pygame.draw.rect(self.screen, BLACK, result_box, 2, border_radius=15)

        # Result text
        if self.winner == 'draw':
            result_text = font_large.render("It's a Draw!", True, BLACK)
        else:
            result_text = font_large.render(f"Player {self.winner} Wins!", True, BLACK)

        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(result_text, result_rect)

        # Buttons
        menu_button = Button(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50, 150, 50, "Main Menu", BLUE, DARK_BLUE)
        replay_button = Button(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 50, 150, 50, "Play Again", GREEN,
                               (0, 200, 0))

        menu_button.draw(self.screen)
        replay_button.draw(self.screen)

        return menu_button, replay_button

    def handle_login_events(self, event, login_button, mouse_pos):
        """Handle events for the login screen"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.active_input = "password" if self.active_input == "username" else "username"
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            else:
                if event.unicode.isprintable():
                    if self.active_input == "username" and len(self.username) < 20:
                        self.username += event.unicode
                    elif self.active_input == "password" and len(self.password) < 20:
                        self.password += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Text field selection
            username_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 290, 260, 40)
            password_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 370, 260, 40)

            if username_rect.collidepoint(x, y):
                self.active_input = "username"
            elif password_rect.collidepoint(x, y):
                self.active_input = "password"
            elif login_button.is_clicked(mouse_pos, event):
                success, msg = self.client.connect(self.username, self.password)
                if success:
                    self.current_user = self.username
                    self.game_state = MENU
                    self.message = "Login successful"
                else:
                    self.message = msg

    def handle_menu_events(self, event, buttons, mouse_pos):
        """Handle events for the menu screen"""
        local_button, online_button, about_button, logout_button = buttons

        if event.type == pygame.MOUSEBUTTONDOWN:
            if local_button.rect.collidepoint(mouse_pos):
                self.game_mode = 'local'
                self.reset_game()
                self.game_state = GAME
                self.play_sound(self.click_sound)
            elif online_button.rect.collidepoint(mouse_pos):
                self.game_mode = 'online'
                self.reset_game()
                self.game_state = GAME
                self.play_sound(self.click_sound)
            elif about_button.rect.collidepoint(mouse_pos):
                self.game_state = ABOUT
                self.play_sound(self.click_sound)
            elif logout_button.rect.collidepoint(mouse_pos):
                self.game_state = LOGIN
                self.play_sound(self.click_sound)

    def handle_about_events(self, event, back_button, mouse_pos):
        """Handle events for the about screen"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.rect.collidepoint(mouse_pos):
                self.game_state = MENU
                self.play_sound(self.click_sound)

    def handle_game_events(self, event, back_button, mouse_pos):
        """Handle events for the game screen with turn validation."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button.rect.collidepoint(mouse_pos):
                self.game_state = MENU
                self.play_sound(self.click_sound)
                return

            board_size = 400
            board_x = (SCREEN_WIDTH - board_size) // 2
            board_y = (SCREEN_HEIGHT - board_size) // 2
            cell_size = board_size // BOARD_SIZE

            if board_x <= mouse_pos[0] <= board_x + board_size and board_y <= mouse_pos[1] <= board_y + board_size:
                col = (mouse_pos[0] - board_x) // cell_size
                row = (mouse_pos[1] - board_y) // cell_size

                if self.board[row][col] == '' and self.winner is None:
                    if self.game_mode == 'online':
                        print(
                            f"[GUI] Player symbol: {self.client.player_symbol}, Current turn: {self.client.current_turn}")
                        if self.client.current_turn != self.client.player_symbol:
                            print("[GUI] Not your turn!")
                            return
                        if self.client.send_move(row, col):
                            self.board[row][col] = self.client.player_symbol
                            self.play_sound(self.click_sound)
                        else:
                            print("[GUI] Failed to send move.")
                    elif self.game_mode == 'local':
                        self.board[row][col] = self.current_player
                        self.play_sound(self.click_sound)
                        self.winner = self.check_winner()
                        if self.winner:
                            if self.winner != 'draw':
                                self.play_sound(self.win_sound)
                            else:
                                self.play_sound(self.lose_sound)
                            self.game_state = END
                        else:
                            self.current_player = 'O' if self.current_player == 'X' else 'X'

    def handle_end_events(self, event, buttons, mouse_pos):
        """Handle events for the end screen"""
        menu_button, replay_button = buttons

        if event.type == pygame.MOUSEBUTTONDOWN:
            if menu_button.rect.collidepoint(mouse_pos):
                self.game_state = MENU
                self.play_sound(self.click_sound)
            elif replay_button.rect.collidepoint(mouse_pos):
                self.reset_game()
                if self.game_mode == 'online':
                    # For online games, wait for server to start new game
                    pass
                else:
                    self.game_state = GAME
                self.play_sound(self.click_sound)

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.game_state == LOGIN:
                    login_button = self.draw_login_screen()
                    self.handle_login_events(event, login_button, mouse_pos)
                elif self.game_state == MENU:
                    buttons = self.draw_menu_screen()
                    for button in buttons:
                        button.check_hover(mouse_pos)
                    self.handle_menu_events(event, buttons, mouse_pos)
                elif self.game_state == ABOUT:
                    back_button = self.draw_about_screen()
                    back_button.check_hover(mouse_pos)
                    self.handle_about_events(event, back_button, mouse_pos)
                elif self.game_state == GAME:
                    back_button = self.draw_game_screen()
                    back_button.check_hover(mouse_pos)
                    self.handle_game_events(event, back_button, mouse_pos)
                elif self.game_state == END:
                    buttons = self.draw_end_screen()
                    for button in buttons:
                        button.check_hover(mouse_pos)
                    self.handle_end_events(event, buttons, mouse_pos)

            # Draw the appropriate screen
            if self.game_state == LOGIN:
                login_button = self.draw_login_screen()
                login_button.check_hover(mouse_pos)

                # Show username text
                username_text = font_small.render(self.username, True, BLACK)
                self.screen.blit(username_text, (SCREEN_WIDTH // 2 - 120, 300))
            elif self.game_state == MENU:
                buttons = self.draw_menu_screen()
                for button in buttons:
                    button.check_hover(mouse_pos)
            elif self.game_state == ABOUT:
                back_button = self.draw_about_screen()
                back_button.check_hover(mouse_pos)
            elif self.game_state == GAME:
                back_button = self.draw_game_screen()
                back_button.check_hover(mouse_pos)
            elif self.game_state == END:
                buttons = self.draw_end_screen()
                for button in buttons:
                    button.check_hover(mouse_pos)

            pygame.display.flip()

        self.client.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TicTacToeGUI()
    game.run()
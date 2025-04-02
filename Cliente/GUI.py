import pygame
import pygame
import sys
import os
from pygame import mixer
from client import send_credentials  # Importar la función del cliente

# Initialize pygame and mixer
pygame.init()
mixer.init()

# Colores
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

# Game variables
current_player = 'X'
board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
game_state = LOGIN
player_name = ''
winner = None
game_mode = None  # 'local' or 'online'
current_user = ""
username = ""
password = ""
active_input = "username"
message = ""
click_sound = None
win_sound = None
draw_sound = None

# Sounds
try:
    click_sound = mixer.Sound('click.mp3')
    win_sound = mixer.Sound('win.mp3')
    draw_sound = mixer.Sound('draw.wav')
    lose_sound = mixer.Sound('lose.mp3')
except:
    print("Sound files not found. Continuing without sound.")

# Load assets
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

# Try to load images, use colored squares if not found // si no pongo imagenes no me sirve el login desoues de iniciar sesion
x_image = load_image('img/x.png', 0.8)
o_image = load_image('img/o.png', 0.8)


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
#
# # Configuración de pantalla
# WIDTH, HEIGHT = 400, 300
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Inicio de Sesión")
#
# # Fuente
# font = pygame.font.Font(None, 30)
#
# # Variables de los campos de entrada
# username = ""
# password = ""
# active_input = "username"  # Campo activo
# message = ""
# screen_state = "login"  # "login" o "acerca_de"

def draw_login_screen():
    """Dibuja la pantalla de inicio de sesión"""
    screen.fill(WHITE)

    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    # Login box
    login_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 180, 300, 300)
    pygame.draw.rect(screen, WHITE, login_box, border_radius=15)
    pygame.draw.rect(screen, BLACK, login_box, 2, border_radius=15)

    # Title
    title = font_medium.render("Login", True, BLACK)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 210))
    screen.blit(title, title_rect)

    # User
    username_label = font_small.render("Username:", True, BLACK)
    screen.blit(username_label, (SCREEN_WIDTH // 2 - 130, 260))

    username_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 290, 260, 40)
    pygame.draw.rect(screen, LIGHT_GRAY if active_input == "username" else WHITE, username_rect, border_radius=5)
    pygame.draw.rect(screen, DARK_BLUE if active_input == "username" else BLACK, username_rect, 2, border_radius=5)
    
    # Password
    password_label = font_small.render("Password:", True, BLACK)
    screen.blit(password_label, (SCREEN_WIDTH // 2 - 130, 340))

    password_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 370, 260, 40)
    pygame.draw.rect(screen, LIGHT_GRAY if active_input == "password" else WHITE, password_rect, border_radius=5)
    pygame.draw.rect(screen, DARK_BLUE if active_input == "password" else BLACK, password_rect, 2, border_radius=5)

    password_text = font_small.render("*" * len(password), True, BLACK)
    screen.blit(password_text, (password_rect.x + 10, password_rect.y + 10))

    # Login button
    login_button = Button(SCREEN_WIDTH // 2 - 100, 430, 200, 40, "Login", BLUE, DARK_BLUE)
    login_button.draw(screen)
    #
    # # Button "About"
    # about_button = Button(SCREEN_WIDTH // 2 - 100, 480, 200, 40, "About", GRAY, LIGHT_GRAY, BLACK, font_small)
    # about_button.draw(screen)

    # message after login
    if message:
        color = GREEN if message == "Login successful" else RED
        msg_text = font_small.render(message, True, color)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 530))
        screen.blit(msg_text, msg_rect)

    return login_button, about_button


def draw_about_screen():
    """Dibuja la pantalla de 'Acerca de'"""
    # screen.blit(background_img, (0, 0))
    screen.fill(WHITE)

    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    # Welcome message
    welcome_text = font_large.render(f"Welcome, {current_user}!", True, WHITE)
    welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(welcome_text, welcome_rect)

    # Game title
    title = font_xl.render("Tic Tac Toe", True, WHITE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 180))
    screen.blit(title, title_rect)

    # Buttons
    local_button = Button(SCREEN_WIDTH // 2 - 150, 300, 300, 60, "Local Game", BLUE, DARK_BLUE)
    online_button = Button(SCREEN_WIDTH // 2 - 150, 380, 300, 60, "Online Game", GREEN, (0, 200, 0))
    about_button = Button(SCREEN_WIDTH // 2 - 150, 460, 300, 60, "About", PURPLE, (100, 0, 100))
    logout_button = Button(SCREEN_WIDTH // 2 - 150, 540, 300, 40, "Logout", RED, (200, 0, 0), font=font_small)

    local_button.draw(screen)
    online_button.draw(screen)
    about_button.draw(screen)
    logout_button.draw(screen)

    return local_button, online_button, about_button, logout_button


def draw_menu_screen():
    """Draw the main menu screen"""
    # screen.blit(background_img, (0, 0))
    screen.fill(WHITE)

    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    # Welcome message
    welcome_text = font_large.render(f"Welcome, {current_user}!", True, WHITE)
    welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    screen.blit(welcome_text, welcome_rect)

    # Game title
    title = font_xl.render("Tic Tac Toe", True, WHITE)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 180))
    screen.blit(title, title_rect)

    # Buttons
    local_button = Button(SCREEN_WIDTH // 2 - 150, 300, 300, 60, "Local Game", BLUE, DARK_BLUE)
    online_button = Button(SCREEN_WIDTH // 2 - 150, 380, 300, 60, "Online Game", GREEN, (0, 200, 0))
    about_button = Button(SCREEN_WIDTH // 2 - 150, 460, 300, 60, "About", PURPLE, (100, 0, 100))
    logout_button = Button(SCREEN_WIDTH // 2 - 150, 540, 300, 40, "Logout", RED, (200, 0, 0), font=font_small)

    local_button.draw(screen)
    online_button.draw(screen)
    about_button.draw(screen)
    logout_button.draw(screen)

    return local_button, online_button, about_button, logout_button


def draw_about_screen():
    """Draw the about screen"""
    # screen.blit(background_img, (0, 0))
    screen.fill(WHITE)

    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # About box
    about_box = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
    pygame.draw.rect(screen, WHITE, about_box, border_radius=15)
    pygame.draw.rect(screen, BLACK, about_box, 2, border_radius=15)

    # Title
    title = font_large.render("About Tic Tac Toe", True, BLACK)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
    screen.blit(title, title_rect)

    # Content
    lines = [
        "Tic Tac Toe Game",
        "Version 1.0",
        "",
        "Created with Pygame",
        "",
        "This game features:",
        "- Local multiplayer",
        "- Online multiplayer (coming soon)",
        "- Beautiful UI",
        "- Sound effects",
        "Add teamates, proffesor, and subject",
        "Developed as a learning project"
    ]

    for i, line in enumerate(lines):
        text = font_small.render(line, True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 220 + i * 30))

    # Back button
    back_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 120, 200, 50, "Back", BLUE, DARK_BLUE)
    back_button.draw(screen)

    return back_button


def draw_game_screen():
    """Draw the game screen"""
    screen.fill(WHITE)

    # Draw game board
    board_size = 400
    board_x = (SCREEN_WIDTH - board_size) // 2
    board_y = (SCREEN_HEIGHT - board_size) // 2

    # Draw board background
    pygame.draw.rect(screen, LIGHT_GRAY, (board_x, board_y, board_size, board_size))

    # Draw grid lines
    cell_size = board_size // BOARD_SIZE
    for i in range(1, BOARD_SIZE):
        # Vertical lines
        pygame.draw.line(screen, BLACK, (board_x + i * cell_size, board_y),
                         (board_x + i * cell_size, board_y + board_size), 3)
        # Horizontal lines
        pygame.draw.line(screen, BLACK, (board_x, board_y + i * cell_size),
                         (board_x + board_size, board_y + i * cell_size), 3)

    # Draw X's and O's
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == 'X':
                x_pos = board_x + col * cell_size + cell_size // 2
                y_pos = board_y + row * cell_size + cell_size // 2
                if x_image:
                    x_rect = x_image.get_rect(center=(x_pos, y_pos))
                    screen.blit(x_image, x_rect)
                else:
                    pygame.draw.line(screen, RED, (x_pos - 30, y_pos - 30), (x_pos + 30, y_pos + 30), 5)
                    pygame.draw.line(screen, RED, (x_pos + 30, y_pos - 30), (x_pos - 30, y_pos + 30), 5)
            elif board[row][col] == 'O':
                x_pos = board_x + col * cell_size + cell_size // 2
                y_pos = board_y + row * cell_size + cell_size // 2
                if o_image:
                    o_rect = o_image.get_rect(center=(x_pos, y_pos))
                    screen.blit(o_image, o_rect)
                else:
                    pygame.draw.circle(screen, BLUE, (x_pos, y_pos), 30, 5)

    # Draw current player indicator
    player_text = font_medium.render(f"Current Player: {current_player}", True, BLACK)
    screen.blit(player_text, (20, 20))

    # Draw back button
    back_button = Button(20, SCREEN_HEIGHT - 70, 150, 50, "Menu", RED, (200, 0, 0))
    back_button.draw(screen)

    return back_button


def draw_end_screen():
    """Draw the end game screen"""
    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Result box
    result_box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
    pygame.draw.rect(screen, WHITE, result_box, border_radius=15)
    pygame.draw.rect(screen, BLACK, result_box, 2, border_radius=15)

    # Result text
    if winner == 'draw':
        result_text = font_large.render("It's a Draw!", True, BLACK)
    else:
        result_text = font_large.render(f"Player {winner} Wins!", True, BLACK)

    result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(result_text, result_rect)

    # Buttons
    menu_button = Button(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50, 150, 50, "Main Menu", BLUE, DARK_BLUE)
    replay_button = Button(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 50, 150, 50, "Play Again", GREEN, (0, 200, 0))

    menu_button.draw(screen)
    replay_button.draw(screen)

    return menu_button, replay_button


def check_winner():
    """Check if there's a winner or a draw"""
    # Check rows
    for row in range(BOARD_SIZE):
        if board[row][0] == board[row][1] == board[row][2] != '':
            return board[row][0]

    # Check columns
    for col in range(BOARD_SIZE):
        if board[0][col] == board[1][col] == board[2][col] != '':
            return board[0][col]

    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != '':
        return board[0][2]

    # Check for draw
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == '':
                return None  # Game still ongoing

    return 'draw'  # Draw


def reset_game():
    """Reset the game state"""
    global board, current_player, winner
    board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    current_player = 'X'
    winner = None


def handle_login_events(event):
    """Handle events for the login screen"""

    global username, password, active_input, message
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_TAB:
            active_input = "password" if active_input == "username" else "username"
        elif event.key == pygame.K_BACKSPACE:
            if active_input == "username":
                username = username[:-1]
            else:
                password = password[:-1]
        else:
            # Solo permitir caracteres visibles (no teclas especiales)
            if event.unicode.isprintable():
                if active_input == "username" and len(username) < 20:
                    username += event.unicode
                elif active_input == "password" and len(password) < 20:
                    password += event.unicode
    
    elif event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        # Selección de campo de texto
        username_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 290, 260, 40)
        password_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 370, 260, 40)
        
        if username_rect.collidepoint(x, y):
            active_input = "username"
        elif password_rect.collidepoint(x, y):
            active_input = "password"


def handle_menu_events(event, buttons):
    """Handle events for the menu screen"""
    global game_state, game_mode

    local_button, online_button, about_button, logout_button = buttons

    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        if local_button.rect.collidepoint(pos):
            game_mode = 'local'
            reset_game()
            game_state = GAME
            play_sound(click_sound)
        elif online_button.rect.collidepoint(pos):
            # Online mode not fully implemented yet
            game_mode = 'online'
            reset_game()
            game_state = GAME
            play_sound(click_sound)
        elif about_button.rect.collidepoint(pos):
            game_state = ABOUT
            play_sound(click_sound)
        elif logout_button.rect.collidepoint(pos):
            game_state = LOGIN
            play_sound(click_sound)


def handle_about_events(event, back_button):
    """Handle events for the about screen"""
    global game_state

    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        if back_button.rect.collidepoint(pos):
            game_state = MENU
            play_sound(click_sound)


def handle_game_events(event, back_button):
    """Handle events for the game screen"""
    global current_player, game_state, winner

    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()

        # Check if back button was clicked
        if back_button.rect.collidepoint(pos):
            game_state = MENU
            play_sound(click_sound)
            return

        # Check if a board cell was clicked
        board_size = 400
        board_x = (SCREEN_WIDTH - board_size) // 2
        board_y = (SCREEN_HEIGHT - board_size) // 2
        cell_size = board_size // BOARD_SIZE

        if board_x <= pos[0] <= board_x + board_size and board_y <= pos[1] <= board_y + board_size:
            col = (pos[0] - board_x) // cell_size
            row = (pos[1] - board_y) // cell_size

            if board[row][col] == '' and winner is None:
                board[row][col] = current_player
                play_sound(click_sound)

                # Check for winner
                winner = check_winner()
                if winner:
                    if winner != 'draw':
                        play_sound(win_sound)
                    else:
                        play_sound(draw_sound)
                    game_state = END
                else:
                    # Switch player
                    current_player = 'O' if current_player == 'X' else 'X'


def handle_end_events(event, buttons):
    """Handle events for the end screen"""
    global game_state

    menu_button, replay_button = buttons

    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = pygame.mouse.get_pos()
        if menu_button.rect.collidepoint(pos):
            game_state = MENU
            play_sound(click_sound)
        elif replay_button.rect.collidepoint(pos):
            reset_game()
            game_state = GAME
            play_sound(click_sound)


def play_sound(sound):
    """Play a sound effect if available"""
    try:
        sound.play()
    except:
        pass


# actualizados
# Main game loop
clock = pygame.time.Clock() # Add this at initialization
running = True
while running:
    # Keep the game running at 60 FPS
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    #EVENTOS PARA LOS BOTONES

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle events based on current game state
        if game_state == LOGIN:
            login_button, about_button = draw_login_screen()
            handle_login_events(event)  

            # Luego manejar clics en botones
            if event.type == pygame.MOUSEBUTTONDOWN:
                if login_button.rect.collidepoint(mouse_pos):
                    #Autenticacion con el server ya hecho 
                    auth_success, auth_message, _ = send_credentials(username, password)
                    if auth_success:
                        current_user = username
                        game_state = MENU
                        message = "Login successful"
                        play_sound(click_sound)
                    else:
                        message = auth_message
                elif about_button.rect.collidepoint(mouse_pos):
                    game_state = ABOUT
                    play_sound(click_sound)

        elif game_state == MENU:
            buttons = draw_menu_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_menu_events(event, buttons)

        elif game_state == ABOUT:
            back_button = draw_about_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_about_events(event, back_button)

        elif game_state == GAME:
            back_button = draw_game_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_game_events(event, back_button)

        elif game_state == END:
            buttons = draw_end_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                handle_end_events(event, buttons)

    if game_state == LOGIN:
        login_button, about_button = draw_login_screen()
        login_button.check_hover(mouse_pos)
        about_button.check_hover(mouse_pos)
        
        # Mostrar texto de usuario actual
        username_text = font_small.render(username, True, BLACK)
        screen.blit(username_text, (SCREEN_WIDTH // 2 - 120, 300))
    elif game_state == MENU:
        buttons = draw_menu_screen()
        for button in buttons:
            button.check_hover(mouse_pos)
    elif game_state == ABOUT:
        back_button = draw_about_screen()
        back_button.check_hover(mouse_pos)
    elif game_state == GAME:
        back_button = draw_game_screen()
        back_button.check_hover(mouse_pos)
    elif game_state == END:
        buttons = draw_end_screen()
        for button in buttons:
            button.check_hover(mouse_pos)

    pygame.display.flip()
pygame.quit()
sys.exit()

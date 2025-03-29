import pygame
from client import send_credentials  # Importar la función del cliente

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Inicializar Pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Inicio de Sesión")

# Fuente
font = pygame.font.Font(None, 30)

# Variables de los campos de entrada
username = ""
password = ""
active_input = "username"  # Campo activo
message = ""
screen_state = "login"  # "login" o "acerca_de"

def draw_login_screen():
    """Dibuja la pantalla de inicio de sesión"""
    screen.fill(WHITE)
    
    # Título
    screen.blit(font.render("Inicio de Sesión", True, BLACK), (140, 30))
    
    # Usuario
    screen.blit(font.render("Usuario:", True, BLACK), (50, 80))
    pygame.draw.rect(screen, GRAY if active_input == "username" else BLACK, (150, 75, 200, 30), 2)
    screen.blit(font.render(username, True, BLACK), (160, 80))
    
    # Contraseña
    screen.blit(font.render("Contraseña:", True, BLACK), (50, 130))
    pygame.draw.rect(screen, GRAY if active_input == "password" else BLACK, (150, 125, 200, 30), 2)
    screen.blit(font.render("*" * len(password), True, BLACK), (160, 130))

    # Botón de inicio
    pygame.draw.rect(screen, BLACK, (150, 180, 100, 40))
    screen.blit(font.render("Iniciar", True, WHITE), (175, 190))

    # Botón "Acerca de"
    pygame.draw.rect(screen, BLACK, (150, 230, 100, 40))
    screen.blit(font.render("Acerca de", True, WHITE), (160, 240))

    # Mensaje de respuesta
    if message:
        color = GREEN if message == "dentro" else RED
      #  screen.blit(font.render(message, True, color), (140, 270))

def draw_about_screen():
    """Dibuja la pantalla de 'Acerca de'"""
    screen.fill(WHITE)
    screen.blit(font.render("Acerca de", True, BLACK), (140, 30))

    # Botón "Regresar"
    pygame.draw.rect(screen, BLACK, (150, 230, 100, 40))
    screen.blit(font.render("Regresar", True, WHITE), (160, 240))

def handle_events():
    """Maneja los eventos del programa"""
    global running, active_input, username, password, message, screen_state, current_user

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if screen_state == "login":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_input = "password" if active_input == "username" else "username"
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                elif event.key == pygame.K_RETURN:
                    success, msg, current_user = send_credentials(username, password)
                    if success:
                        screen_state = "game"
                    else:
                        message = msg
                else:
                    if active_input == "username" and len(username) < 20:
                        username += event.unicode
                    elif active_input == "password" and len(password) < 20:
                        password += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 150 <= x <= 350 and 75 <= y <= 105:
                    active_input = "username"
                elif 150 <= x <= 350 and 125 <= y <= 155:
                    active_input = "password"
                elif 150 <= x <= 250 and 180 <= y <= 220:
                    success, msg, current_user = send_credentials(username, password)
                    if success:
                        screen_state = "game"
                    else:
                        message = msg
                elif 150 <= x <= 250 and 230 <= y <= 270:
                    screen_state = "acerca_de"

        elif screen_state == "acerca_de":
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 150 <= x <= 250 and 230 <= y <= 270:
                    screen_state = "login"

    return True

#ESTO LO PODEMOS PONER EN UNA CLASE APRTE 
def draw_game_screen():
    """Dibuja la pantalla del juego"""
    screen.fill(WHITE)
    # Mostrar el nombre de usuario
    screen.blit(font.render(f"Jugador: {current_user}", True, BLACK), (140, 30))
    screen.blit(font.render("Partida en curso", True, BLACK), (140, 70))

# Añadir variable global para el usuario actual
current_user = ""

# Bucle principal
running = True
while running:
    if screen_state == "login":
        draw_login_screen()
    elif screen_state == "acerca_de":
        draw_about_screen()
    elif screen_state == "game":
        draw_game_screen()

    running = handle_events()
    pygame.display.flip()

pygame.quit()
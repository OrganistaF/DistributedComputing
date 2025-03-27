import pygame
from client import send_credentials  # Importar la función del cliente

#GUI de inicio de sesion
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

# Bucle principal
running = True
while running:
    screen.fill(WHITE)

    if screen_state == "login":
        # Pantalla de inicio de sesion
        title_text = font.render("Inicio de Sesión", True, BLACK)
        screen.blit(title_text, (140, 30))

        # Usuario
        username_text = font.render("Usuario:", True, BLACK)
        screen.blit(username_text, (50, 80))
        pygame.draw.rect(screen, GRAY if active_input == "username" else BLACK, (150, 75, 200, 30), 2)
        user_surface = font.render(username, True, BLACK)
        screen.blit(user_surface, (160, 80))

        # Contraseña
        password_text = font.render("Contraseña:", True, BLACK)
        screen.blit(password_text, (50, 130))
        pygame.draw.rect(screen, GRAY if active_input == "password" else BLACK, (150, 125, 200, 30), 2)
        pass_surface = font.render("*" * len(password), True, BLACK)
        screen.blit(pass_surface, (160, 130))

        # Botón de login
        pygame.draw.rect(screen, BLACK, (150, 180, 100, 40))
        login_text = font.render("Iniciar", True, WHITE)
        screen.blit(login_text, (175, 190))

        # Botón para cambiar a acerca de
        pygame.draw.rect(screen, BLACK, (150, 230, 100, 40))
        change_screen_text = font.render("Acerca de", True, WHITE)
        screen.blit(change_screen_text, (160, 240))

        # Mensaje de respuesta
        if message:
            color = GREEN if message == "dentro" else RED
            response_text = font.render(message, True, color)
            screen.blit(response_text, (120, 270))

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_input = "password" if active_input == "username" else "username"

                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]

                elif event.key == pygame.K_RETURN:
                    message = send_credentials(username, password)

                else:
                    if active_input == "username" and len(username) < 20:
                        username += event.unicode
                    elif active_input == "password" and len(password) < 20:
                        password += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Cambiar el campo activo
                if 150 <= x <= 350 and 75 <= y <= 105:
                    active_input = "username"
                elif 150 <= x <= 350 and 125 <= y <= 155:
                    active_input = "password"
                elif 150 <= x <= 250 and 180 <= y <= 220:
                    message = send_credentials(username, password)

                # Cambiar a la pantalla de registro
                elif 150 <= x <= 250 and 230 <= y <= 270:
                    screen_state = "acerca_de"

    elif screen_state == "acerca_de":
        # Pantalla de registro
        title_text = font.render("Acerca de", True, BLACK)
        screen.blit(title_text, (140, 30))


        # Botón para regresar a la pantalla de inicio de sesión
        pygame.draw.rect(screen, BLACK, (150, 230, 100, 40))
        back_to_login_text = font.render("Regresar", True, WHITE)
        screen.blit(back_to_login_text, (160, 240))

        # Manejo de eventos para la pantalla de registro
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Cambiar el campo activo
                if 150 <= x <= 250 and 230 <= y <= 270:
                    screen_state = "login"  # Regresar a la pantalla de inicio de sesión

    pygame.display.flip()

pygame.quit()

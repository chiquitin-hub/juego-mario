import pygame
import sys
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros Clone")

# Colores
WHITE = (255, 255, 255)
BLUE = (0, 128, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

# Reloj para controlar FPS
clock = pygame.time.Clock()
FPS = 60

# Clase Jugador
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.color = RED
        self.score = 0
    
    def update(self, platforms):
        # Aplicar gravedad
        self.vel_y += self.gravity
        
        # Actualizar posición
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Comprobar límites de pantalla
        if self.x < 0:
            self.x = 0
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width
        
        # Comprobar colisión con el suelo
        self.on_ground = False
        if self.y + self.height > HEIGHT:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True
        
        # Comprobar colisión con plataformas
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and 
                self.y + self.height > platform.y and 
                self.y + self.height < platform.y + platform.height + 10 and 
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
    
    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
    
    def move_left(self):
        self.vel_x = -5
    
    def move_right(self):
        self.vel_x = 5
    
    def stop(self):
        self.vel_x = 0
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

# Clase Plataforma
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = BROWN
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

# Clase Enemigo
class Enemy:
    def __init__(self, x, y, width, height, vel_x):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel_x = vel_x
        self.color = GREEN
    
    def update(self, platforms):
        self.x += self.vel_x
        
        # Cambiar dirección si llega a los bordes
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.vel_x *= -1
        
        # Comprobar si está en una plataforma
        on_platform = False
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and 
                self.y + self.height == platform.y):
                on_platform = True
                break
        
        # Cambiar dirección si llega al borde de una plataforma
        if not on_platform:
            for platform in platforms:
                if (self.x + self.width > platform.x and 
                    self.x < platform.x + platform.width and 
                    self.y + self.height == platform.y):
                    if self.vel_x > 0 and self.x + self.width >= platform.x + platform.width:
                        self.vel_x *= -1
                    elif self.vel_x < 0 and self.x <= platform.x:
                        self.vel_x *= -1
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

# Clase Moneda
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.color = YELLOW
        self.collected = False
    
    def draw(self, surface):
        if not self.collected:
            pygame.draw.ellipse(surface, self.color, (self.x, self.y, self.width, self.height))

# Crear plataformas
platforms = [
    Platform(0, HEIGHT - 40, WIDTH, 40),  # Suelo
    Platform(100, 450, 200, 20),
    Platform(400, 350, 200, 20),
    Platform(200, 250, 200, 20),
    Platform(500, 150, 200, 20)
]

# Crear enemigos
enemies = [
    Enemy(150, 430, 30, 20, 2),
    Enemy(450, 330, 30, 20, -2),
    Enemy(250, 230, 30, 20, 2)
]

# Crear monedas
coins = [
    Coin(150, 400),
    Coin(450, 300),
    Coin(250, 200),
    Coin(550, 100)
]

# Crear jugador
player = Player(50, HEIGHT - 100)

# Función para mostrar texto
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# Función para comprobar colisiones
def check_collisions():
    # Colisión con monedas
    for coin in coins:
        if (not coin.collected and 
            player.x < coin.x + coin.width and 
            player.x + player.width > coin.x and 
            player.y < coin.y + coin.height and 
            player.y + player.height > coin.y):
            coin.collected = True
            player.score += 10
    
    # Colisión con enemigos
    for enemy in enemies:
        if (player.x < enemy.x + enemy.width and 
            player.x + player.width > enemy.x and 
            player.y < enemy.y + enemy.height and 
            player.y + player.height > enemy.y):
            # Si el jugador está cayendo sobre el enemigo
            if player.vel_y > 0 and player.y + player.height < enemy.y + enemy.height / 2:
                enemies.remove(enemy)
                player.vel_y = -8  # Rebote
                player.score += 20
            else:
                # Reiniciar posición del jugador
                player.x = 50
                player.y = HEIGHT - 100
                player.score -= 10
                if player.score < 0:
                    player.score = 0

# Pantalla de inicio
def show_start_screen():
    screen.fill(BLUE)
    draw_text(screen, "Super Mario Bros Clone", 48, WIDTH // 2 - 200, HEIGHT // 4, WHITE)
    draw_text(screen, "Flechas para moverse, Espacio para saltar", 22, WIDTH // 2 - 180, HEIGHT // 2, WHITE)
    draw_text(screen, "Presiona cualquier tecla para comenzar", 22, WIDTH // 2 - 160, HEIGHT * 3/4, WHITE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

# Bucle principal del juego
def game_loop():
    running = True
    game_over = False
    
    while running:
        # Control de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Control de teclas
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                if event.key == pygame.K_RIGHT:
                    player.move_right()
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_r:
                    return True  # Reiniciar juego
            
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    player.stop()
        
        # Actualizar
        player.update(platforms)
        for enemy in enemies:
            enemy.update(platforms)
        check_collisions()
        
        # Comprobar si se han recogido todas las monedas
        all_coins_collected = all(coin.collected for coin in coins)
        if all_coins_collected:
            game_over = True
        
        # Dibujar
        screen.fill(BLUE)
        
        # Dibujar plataformas
        for platform in platforms:
            platform.draw(screen)
        
        # Dibujar monedas
        for coin in coins:
            coin.draw(screen)
        
        # Dibujar enemigos
        for enemy in enemies:
            enemy.draw(screen)
        
        # Dibujar jugador
        player.draw(screen)
        
        # Mostrar puntuación
        draw_text(screen, f"Puntuación: {player.score}", 30, 10, 10)
        
        # Mostrar mensaje de victoria
        if game_over:
            draw_text(screen, "¡Has ganado! Presiona R para reiniciar", 40, WIDTH // 2 - 250, HEIGHT // 2)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return False

# Bucle principal del programa
def main():
    show_start_screen()
    restart = True
    
    while restart:
        restart = game_loop()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

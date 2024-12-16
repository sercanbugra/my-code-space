import pygame
import math

# Pygame başlangıcı
pygame.init()

# Ekran boyutları ve renkler
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Ekranı oluşturma
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Savaşı")

# Tank ve mermi ayarları
tank1_pos = [100, HEIGHT - 50]
tank2_pos = [WIDTH - 100, HEIGHT - 50]
tank_width, tank_height = 40, 20
bullet_radius = 5
gravity = 0.1

# Canlar
tank1_health = 3
tank2_health = 3

# Yazı tipi
font = pygame.font.SysFont("Arial", 24)
input_font = pygame.font.SysFont("Arial", 18)

# Kullanıcıdan input al
angle = None
speed = None

# Sıra
turn = 1  # 1: Tank 1'in sırası, 2: Tank 2'nin sırası

def draw_tanks():
    pygame.draw.rect(screen, RED, (tank1_pos[0], tank1_pos[1], tank_width, tank_height))
    pygame.draw.rect(screen, BLUE, (tank2_pos[0], tank2_pos[1], tank_width, tank_height))

def draw_health():
    tank1_health_text = font.render(f"Tank 1: {tank1_health} HP", True, RED)
    tank2_health_text = font.render(f"Tank 2: {tank2_health} HP", True, BLUE)
    screen.blit(tank1_health_text, (10, 10))
    screen.blit(tank2_health_text, (WIDTH - 200, 10))

def draw_angle_speed_prompt():
    if turn == 1:
        prompt_text = input_font.render(f"Tank 1: Açı (0-90): {angle if angle is not None else '---'} Hız (10-50): {speed if speed is not None else '---'}", True, BLACK)
    else:
        prompt_text = input_font.render(f"Tank 2: Açı (0-90): {angle if angle is not None else '---'} Hız (10-50): {speed if speed is not None else '---'}", True, BLACK)
    
    screen.blit(prompt_text, (WIDTH // 2 - 200, HEIGHT - 50))

def draw_input_boxes():
    # Açı ve hız giriş kutuları
    pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 200, HEIGHT - 80, 150, 30))
    pygame.draw.rect(screen, GRAY, (WIDTH // 2 + 50, HEIGHT - 80, 150, 30))
    
    # Açı ve hız yazıları
    angle_text = input_font.render("Açı: ", True, BLACK)
    speed_text = input_font.render("Hız: ", True, BLACK)
    
    screen.blit(angle_text, (WIDTH // 2 - 190, HEIGHT - 75))
    screen.blit(speed_text, (WIDTH // 2 + 60, HEIGHT - 75))

def fire_bullet(x, y, angle, speed):
    angle_rad = math.radians(angle)
    vx = speed * math.cos(angle_rad)
    vy = -speed * math.sin(angle_rad)
    return x, y, vx, vy

def check_collision(bullet_x, bullet_y, target_x, target_y):
    return (target_x <= bullet_x <= target_x + tank_width and
            target_y <= bullet_y <= target_y + tank_height)

# Ana döngü
running = True
clock = pygame.time.Clock()

bullet = None

while running:
    screen.fill(WHITE)
    draw_tanks()
    draw_health()
    draw_input_boxes()

    # Kullanıcı inputu için prompt
    draw_angle_speed_prompt()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Kullanıcıdan açı ve hız bilgisi alındığında mermi ateşleme
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and angle is not None and speed is not None and not bullet:
                # Açı ve hız girildiyse, mermi ateşle
                if turn == 1:
                    bullet = fire_bullet(tank1_pos[0] + tank_width // 2, tank1_pos[1], angle, speed)
                else:
                    bullet = fire_bullet(tank2_pos[0] + tank_width // 2, tank2_pos[1], 180 - angle, speed)

                # Sıra değişir
                turn = 2 if turn == 1 else 1
                angle = None
                speed = None

        # Açı ve hız girişi
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and angle is None:
                angle = int(input("Açı (0-90): "))
            elif event.key == pygame.K_h and speed is None:
                speed = int(input("Hız (10-50): "))

    # Mermi hareketi
    if bullet:
        bullet_x, bullet_y, vx, vy = bullet
        bullet_x += vx
        bullet_y += vy
        vy += gravity
        pygame.draw.circle(screen, BLACK, (int(bullet_x), int(bullet_y)), bullet_radius)

        # Çarpışma kontrolü
        if check_collision(bullet_x, bullet_y, tank2_pos[0], tank2_pos[1]) and turn == 1:
            tank2_health -= 1
            bullet = None
            turn = 2
        elif check_collision(bullet_x, bullet_y, tank1_pos[0], tank1_pos[1]) and turn == 2:
            tank1_health -= 1
            bullet = None
            turn = 1

        # Mermi ekran dışına çıkarsa
        if bullet_x < 0 or bullet_x > WIDTH or bullet_y > HEIGHT:
            bullet = None
            turn = 2 if turn == 1 else 1

    # Oyunu kazananı kontrol et
    if tank1_health <= 0 or tank2_health <= 0:
        winner_text = "Tank 1 Kazandı!" if tank2_health <= 0 else "Tank 2 Kazandı!"
        winner_surface = font.render(winner_text, True, GREEN)
        screen.blit(winner_surface, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

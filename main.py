import math
import random
import sys
import pygame
from pygame import mixer

# Initialize pygame
pygame.init()

# Create the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Load images
intro_image = pygame.image.load('intro_image.png')
background = pygame.image.load('bgimage3.png')
background_height = background.get_height()
scroll = 0
scroll_speed = 1

icon = pygame.image.load('logo.png')
playerImg = pygame.image.load('player2.png')
bulletImg = pygame.image.load('bullet.png')

# Images for levels 4 and 5
asteroidImg = pygame.image.load('asteroid.png')
fuelImg = pygame.image.load('fuel.png')
bossImg = pygame.image.load('boss.png')
bossProjectileImg = pygame.image.load('boss_projectile.png')

# Sound
mixer.music.load("background.wav")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Galactic Defender")
pygame.display.set_icon(icon)

# Player
playerX = 370
playerY = 480  # Fixed Y position
playerX_change = 0
playerY_change = 0
player_speed = 5
player_angle = 0

# Enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 7

# Asteroid
asteroidImg = []
asteroidX = []
asteroidY = []
asteroidY_change = []
num_of_asteroids = 8
min_asteroid_speed = 1
max_asteroid_speed = 5

# Bullet
bulletX = 0
bulletY = 480
bullet_speed = 15
bullet_state = "ready"

# Score and Level
score_value = 0
level_value = 1
font = pygame.font.Font('freesansbold.ttf', 32)
over_font = pygame.font.Font('freesansbold.ttf', 64)

# Level 2 timer
level2_start_time = 0
level2_duration = 20000  # 20 seconds

# Near miss
near_miss_distance = 30
near_miss_recorded = [False] * num_of_asteroids

# Level 4 variables
asteroids = []
fuel_pods = []
fuel_level = 100
fuel_consumption_rate = 0.05
level4_start_time = 0
level4_duration = 60000
level4_enemies = []  # New variable for level 4 enemies

# Level 5 variables
boss_health = 100
boss_x = 400
boss_y = 100
boss_projectiles = []
boss_attack_timer = 0
boss_attack_interval = 2000
boss_hitbox_size = 80  # Larger hitbox for easier targeting
enemies = []

def intro_page():
    start_time = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        screen.blit(intro_image, (0, 0))
        pygame.display.flip()

        if pygame.time.get_ticks() - start_time >= 5000:
            return

        pygame.time.Clock().tick(60)

def initialize_game_objects():
    global enemyImg, enemyX, enemyY, enemyX_change, enemyY_change
    global asteroidImg, asteroidX, asteroidY, asteroidY_change

    for i in range(num_of_enemies):
        enemyImg.append(pygame.image.load('enemy.png'))
        enemyX.append(random.randint(0, screen_width - 64))
        enemyY.append(random.randint(50, 150))
        enemyX_change.append(6)
        enemyY_change.append(10)

    for i in range(num_of_asteroids):
        asteroidImg.append(pygame.image.load('asteroid.png'))
        asteroidX.append(random.randint(0, screen_width - 64))
        asteroidY.append(random.randint(-500, -50))
        asteroidY_change.append(random.uniform(min_asteroid_speed, max_asteroid_speed))

def reset_asteroids():
    global near_miss_recorded
    for i in range(num_of_asteroids):
        asteroidX[i] = random.randint(0, screen_width - 64)
        asteroidY[i] = random.randint(-500, -50)
        asteroidY_change[i] = random.uniform(min_asteroid_speed, max_asteroid_speed)
        near_miss_recorded[i] = False

def reset_level4():
    global asteroids, fuel_pods, fuel_level, level4_start_time, level4_enemies
    asteroids = [
        {
            'x': random.randint(0, screen_width - 64),
            'y': random.randint(-500, -50),
            'speed': random.uniform(1, 3)
        } for _ in range(6)  # Reduced number of asteroids to accommodate enemies
    ]
    fuel_pods = [
        {
            'x': random.randint(0, screen_width - 32),
            'y': random.randint(-500, -50),
            'speed': random.uniform(1, 2)
        } for _ in range(3)
    ]
    # Initialize level 4 enemies
    level4_enemies = [
        {
            'x': random.randint(0, screen_width - 64),
            'y': random.randint(50, 150),
            'speed': 3,
            'direction': 1
        } for _ in range(4)
    ]
    fuel_level = 100
    level4_start_time = pygame.time.get_ticks()

def reset_level5():
    global boss_health, boss_x, boss_y, boss_projectiles, boss_attack_timer, asteroids, fuel_pods, enemies
    boss_health = 100
    boss_x = 400
    boss_y = 100
    boss_projectiles = []
    boss_attack_timer = 0
    
    # Initialize enemies for level 5
    enemies = [
        {
            'x': random.randint(0, screen_width - 64),
            'y': random.randint(50, 150),
            'speed': random.uniform(2, 4),
            'direction': 1
        } for _ in range(5)
    ]
    
    # Add fewer asteroids for level 5
    asteroids = [
        {
            'x': random.randint(0, screen_width - 64),
            'y': random.randint(-500, -50),
            'speed': random.uniform(1, 2.5)
        } for _ in range(5)
    ]
    
    # Add fuel pods for level 5
    fuel_pods = [
        {
            'x': random.randint(0, screen_width - 32),
            'y': random.randint(-500, -50),
            'speed': random.uniform(1, 1.5)
        } for _ in range(2)
    ]

def show_score():
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (10, 10))

def show_level():
    level = font.render("Level : " + str(level_value), True, (255, 255, 255))
    screen.blit(level, (10, 50))

def show_fuel():
    fuel_text = font.render(f"Fuel: {int(fuel_level)}%", True, (255, 255, 255))
    screen.blit(fuel_text, (10, 90))

def show_boss_health():
    # Draw health bar above the boss
    bar_width = 100
    bar_height = 10
    bar_x = boss_x + (128 - bar_width) // 2  # Center above boss
    bar_y = boss_y - 20  # Position above boss
    
    # Background bar (red)
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    # Health bar (green)
    health_width = int((boss_health / 100) * bar_width)
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
    
    # Percentage text
    health_text = font.render(f"{boss_health}%", True, (255, 255, 255))
    text_rect = health_text.get_rect()
    text_rect.centerx = bar_x + bar_width // 2
    text_rect.bottom = bar_y - 5
    screen.blit(health_text, text_rect)

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))

def game_won_text():
    won_text = over_font.render("YOU WON!", True, (255, 255, 255))
    screen.blit(won_text, (200, 250))

def draw_background():
    global scroll
    screen.blit(background, (0, scroll))
    screen.blit(background, (0, scroll - background_height))
    scroll += scroll_speed
    if scroll >= background_height:
        scroll = 0

def player(x, y, angle):
    rotated_player = pygame.transform.rotate(playerImg, angle)
    new_rect = rotated_player.get_rect(center=playerImg.get_rect(topleft=(x, y)).center)
    screen.blit(rotated_player, new_rect.topleft)

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def asteroid(x, y, i):
    screen.blit(asteroidImg[i], (x, y))

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

def draw_asteroid(x, y):
    screen.blit(asteroidImg[0], (x, y))

def draw_fuel_pod(x, y):
    screen.blit(fuelImg, (x, y))

def draw_boss(x, y):
    screen.blit(bossImg, (x, y))

def draw_boss_projectile(x, y):
    screen.blit(bossProjectileImg, (x, y))

def draw_enemy(x, y):
    screen.blit(enemyImg[0], (x, y))

def is_collision(x1, y1, x2, y2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance < 27

def is_asteroid_collision(x1, y1, x2, y2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance < 50

def is_near_miss(x1, y1, x2, y2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return near_miss_distance < distance < near_miss_distance + 20

def handle_events():
    global playerX_change, bulletX, bulletY, bullet_state, player_angle
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -player_speed
            if event.key == pygame.K_RIGHT:
                playerX_change = player_speed
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bulletSound = mixer.Sound("laser.mp3")
                bulletSound.play()
                bulletX = playerX
                bulletY = playerY
                fire_bullet(bulletX, bulletY)
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                playerX_change = 0
    return True

def update_player():
    global playerX
    playerX += playerX_change
    
    # Keep player within screen bounds
    if level_value < 4:
        playerX = playerX % screen_width
    else:
        playerX = max(0, min(playerX, screen_width - 64))
        
def update_bullet():
    global bulletX, bulletY, bullet_state
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bullet_speed
        
        if bulletY <= 0:
            bulletY = playerY
            bulletX = playerX
            bullet_state = "ready"

def level_1():
    global score_value, level_value, level2_start_time, bullet_state, bulletY
    for i in range(num_of_enemies):
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= screen_width - 64:
            enemyX_change[i] *= -1
            enemyY[i] += enemyY_change[i]

        if is_collision(enemyX[i], enemyY[i], playerX, playerY):
            game_over_text()
            return False

        if is_collision(enemyX[i], enemyY[i], bulletX, bulletY):
            explosionSound = mixer.Sound("explosion.mp3")
            explosionSound.play()
            bulletY = playerY
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, screen_width - 64)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    if score_value >= 10:
        level_value = 2
        level2_start_time = pygame.time.get_ticks()
        reset_asteroids()
    return True

def level_2():
    global level_value, score_value, max_asteroid_speed
    current_time = pygame.time.get_ticks()
    time_elapsed = current_time - level2_start_time

    if time_elapsed < level2_duration:
        for i in range(num_of_asteroids):
            asteroidY[i] += asteroidY_change[i]

            if asteroidY[i] > screen_height:
                asteroidX[i] = random.randint(0, screen_width - 64)
                asteroidY[i] = random.randint(-500, -50)
                asteroidY_change[i] = random.uniform(min_asteroid_speed, max_asteroid_speed)
                near_miss_recorded[i] = False

            if is_asteroid_collision(asteroidX[i], asteroidY[i], playerX, playerY):
                game_over_text()
                return False

            if not near_miss_recorded[i] and is_near_miss(asteroidX[i], asteroidY[i], playerX, playerY):
                score_value += 1
                near_miss_recorded[i] = True

            asteroid(asteroidX[i], asteroidY[i], i)

        if time_elapsed % 5000 == 0:
            max_asteroid_speed += 0.5
            for i in range(num_of_asteroids):
                asteroidY_change[i] = random.uniform(min_asteroid_speed, max_asteroid_speed)
    else:
        level_value = 3
        reset_asteroids()
    return True

def level_3():
    global score_value, level_value, planets_visited, playerY, planet_angles, playerX, player_angle
    all_planets_visited = True
    for i in range(num_of_planets):
        if not planets_visited[i]:
            planet_angles[i] += planet_rotation_speed
            if planet_angles[i] >= 360:
                planet_angles[i] = 0

            planet(planetX[i], planetY[i], i, planet_angles[i])

            if is_collision(planetX[i], planetY[i], playerX, playerY):
                score_value += 3
                planets_visited[i] = True
                landingSound = mixer.Sound("landing.mp3")
                landingSound.play()
                playerY = planetY[i] - 64
                player_angle = planet_angles[i]  # Make spaceship rotate with the planet

            all_planets_visited = False

    if all_planets_visited:
        level_value = 4
        planets_visited = [False] * num_of_planets

    return True

def main_game_loop():
    global playerX, bullet_state, bulletX, bulletY
    running = True
    clock = pygame.time.Clock()
    
    while running:
        draw_background()
        running = handle_events()
        if not running:
            break
            
        update_player()
        update_bullet()

        if level_value == 1:
            running = level_1()
        elif level_value == 2:
            running = level_2()
        elif level_value == 3:
            running = level_3()
        elif level_value == 4:
            running = level_4()
        elif level_value == 5:
            running = level_5()

        player(playerX, playerY, player_angle)
        show_score()
        show_level()
        pygame.display.update()
        clock.tick(60)

    pygame.time.wait(2000)

if __name__ == "__main__":
    intro_page()
    initialize_game_objects()
    main_game_loop()
    pygame.quit()
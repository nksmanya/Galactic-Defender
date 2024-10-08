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
powerup = pygame.image.load('powerup.png')
powerup = pygame.transform.scale(powerup, (32, 32))

# Sound
mixer.music.load("background.wav")
mixer.music.play(-1)

# Caption and Icon
pygame.display.set_caption("Galactic Defender")
pygame.display.set_icon(icon)

# Player
playerX = 370
playerY = 480
playerX_change = 0
playerY_change = 0
player_speed = 5
launch_distance = 100
is_launched = False
launch_speed = 20
player_angle = 0
player_rotation_speed = 2

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

# Planets
planetImg = []
planetX = []
planetY = []
planet_angles = []
num_of_planets = 3
planets_visited = [False] * num_of_planets
planet_rotation_speed = 1

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
level2_duration = 20000  # 20 seconds in milliseconds

# Near miss
near_miss_distance = 30
near_miss_recorded = [False] * num_of_asteroids

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
    global planetImg, planetX, planetY, planet_angles, planets_visited

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
        
for i in range(num_of_planets):
        planetImg.append(pygame.image.load('planet.png'))
        planetX.append(100 + i * 200)  # Spread planets horizontally
        planetY.append(100 + i * 100)  # Move planets diagonally down
        planet_angles.append(0)
    
planets_visited = [False] * num_of_planets

def reset_asteroids():
    global near_miss_recorded
    for i in range(num_of_asteroids):
        asteroidX[i] = random.randint(0, screen_width - 64)
        asteroidY[i] = random.randint(-500, -50)
        asteroidY_change[i] = random.uniform(min_asteroid_speed, max_asteroid_speed)
        near_miss_recorded[i] = False

def show_score():
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (10, 10))

def show_level():
    level = font.render("Level : " + str(level_value), True, (255, 255, 255))
    screen.blit(level, (10, 50))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))

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
    if is_launched or playerY_change < 0:
        screen.blit(powerup, (x + 16, y + 64))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def asteroid(x, y, i):
    screen.blit(asteroidImg[i], (x, y))
    
def planet(x, y, i, angle):
    if not planets_visited[i]:
        rotated_planet = pygame.transform.rotate(planetImg[i], angle)
        new_rect = rotated_planet.get_rect(center=planetImg[i].get_rect(topleft=(x, y)).center)
        screen.blit(rotated_planet, new_rect.topleft)


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))

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
    global playerX_change, playerY_change, bulletX, bulletY, bullet_state, is_launched, player_angle
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -player_speed
                player_angle += player_rotation_speed
            if event.key == pygame.K_RIGHT:
                playerX_change = player_speed
                player_angle -= player_rotation_speed
            if event.key == pygame.K_DOWN:
                playerY_change = player_speed
            if event.key == pygame.K_SPACE and bullet_state == "ready":
                bulletSound = mixer.Sound("laser.mp3")
                bulletSound.play()
                bulletX = playerX
                bulletY = playerY
                fire_bullet(bulletX, bulletY)
            if event.key == pygame.K_l and level_value == 3 and not is_launched:
                is_launched = True
                launch_sound = mixer.Sound("launch.mp3")
                launch_sound.play()
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                playerX_change = 0
                player_angle = 0
            if event.key == pygame.K_DOWN:
                playerY_change = 0
    return True

def update_player():
    global playerX, playerY, is_launched
    if is_launched and level_value == 3:
        playerY -= launch_speed
        if playerY <= screen_height - launch_distance:
            is_launched = False
    else:
        playerX += playerX_change
        playerY += playerY_change
    
    playerX = playerX % screen_width
    playerY = max(0, min(playerY, screen_height - 64))

def update_bullet():
    global bulletX, bulletY, bullet_state
    if bullet_state == "fire":
        fire_bullet(bulletX, bulletY)
        bulletY -= bullet_speed
        
        if bulletY <= 0:
            bulletY = playerY
            bulletX = playerX
            bullet_state = "ready"
    
    bulletX = bulletX % screen_width
    bulletY = bulletY % screen_height

def level_1():
    global score_value, level_value, level2_start_time, bullet_state, bulletY
    for i in range(num_of_enemies):
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= screen_width - 64:
            enemyX_change[i] *= -1
            enemyY[i] += enemyY_change[i]

        # Check for collision with player
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
    global score_value, level_value, bullet_state, bulletY, max_asteroid_speed

    # Update and display each enemy
    for i in range(num_of_enemies):
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= screen_width - 64:
            enemyX_change[i] *= -1
            enemyY[i] += enemyY_change[i]

        # Check collision with player
        if is_collision(enemyX[i], enemyY[i], playerX, playerY):
            game_over_text()
            return False

        # Check collision with bullet
        if is_collision(enemyX[i], enemyY[i], bulletX, bulletY):
            explosionSound = mixer.Sound("explosion.mp3")
            explosionSound.play()
            bulletY = playerY
            bullet_state = "ready"
            score_value += 1
            enemyX[i] = random.randint(0, screen_width - 64)
            enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    # Update and display each asteroid
    for i in range(num_of_asteroids):
        asteroidY[i] += asteroidY_change[i]

        # Respawn asteroid if it goes off-screen
        if asteroidY[i] > screen_height:
            asteroidX[i] = random.randint(0, screen_width - 64)
            asteroidY[i] = random.randint(-500, -50)
            asteroidY_change[i] = random.uniform(min_asteroid_speed, max_asteroid_speed)
            near_miss_recorded[i] = False

        # Check for collision with player
        if is_asteroid_collision(asteroidX[i], asteroidY[i], playerX, playerY):
            game_over_text()
            return False

        # Register near miss
        if not near_miss_recorded[i] and is_near_miss(asteroidX[i], asteroidY[i], playerX, playerY):
            score_value += 1
            near_miss_recorded[i] = True

        asteroid(asteroidX[i], asteroidY[i], i)

    # Gradually increase speed
    if score_value % 5 == 0 and score_value != 0:  # Increase speed every 5 points
        max_asteroid_speed += 0.02
        for j in range(num_of_enemies):
            enemyX_change[j] += 0.01

    # Transition to level 3
    if score_value >= 20:
        level_value = 3
        reset_asteroids()  # Reset asteroids for the next level

    return True


def main_game_loop():
    global playerX, playerY, player_angle
    running = True
    clock = pygame.time.Clock()
    while running:
        draw_background()

        running = handle_events()
        update_player()
        update_bullet()

        if level_value == 1:
            running = level_1()
        elif level_value == 2:
            running = level_2()
        elif level_value == 3:
            running = level_3()
        else:
            game_over_text()
            running = False

        player(playerX, playerY, player_angle)
        show_score()
        show_level()
        pygame.display.update()
        clock.tick(60)

intro_page()
initialize_game_objects()
main_game_loop()
pygame.quit()
import pygame
import random
from sprites import *

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Shooter")
clock = pygame.time.Clock()
bg_original = pygame.image.load('assets/fon.png')
bg_image = pygame.transform.scale(bg_original, (800, 600))

# Загрузка звуков
try:
    dark_sound = pygame.mixer.Sound('assets/DarkSouls.mp3')
    boom_sound = pygame.mixer.Sound('assets/Boom.mp3')
    dead_asteroid_sound = pygame.mixer.Sound('assets/DeadAsteroid.mp3')
    shoot_sound = pygame.mixer.Sound('assets/OneShoot.mp3')
    powerup_sound = pygame.mixer.Sound('assets/PowerUp.mp3')
    music_sound = pygame.mixer.Sound('assets/Music.mp3')
    spawning_sound = pygame.mixer.Sound('assets/terraria.mp3')
    pygame.mixer.music.load('assets/Music.mp3')
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)
    print("Звуки загружены успешно")
except FileNotFoundError as e:
    print(f"Ошибка: не найден звуковой файл - {e}")
    boom_sound = None
    dead_asteroid_sound = None
    shoot_sound = None
    powerup_sound = None

# Группы спрайтов
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
heart_sprites = pygame.sprite.Group()
bosses = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()  # Новая группа для бонусов

ship = Ship(WIDTH // 2 - 25, HEIGHT - 60)
all_sprites.add(ship)

lives = 3
score = 0
font = pygame.font.Font(None, 36)

# Флаг, появился ли уже босс (чтобы не спавнить несколько)
boss1_spawned = False

# Переменные для стрельбы
space_pressed = False
last_shot_time = 0
BASE_SHOT_DELAY = 500  # Базовая задержка 0.5 секунды
current_shot_delay = BASE_SHOT_DELAY  # Текущая задержка

# Переменные для бонуса
powerup_active = False
powerup_end_time = 0
POWERUP_DURATION = 5000  # 8 секунд действия
SHOT_DELAY_BOOST = 250  # Ускоренная стрельба 0.15 секунды


def update_hearts():
    heart_sprites.empty()
    for i in range(lives):
        heart = Hp(10 + i * 40, 10)
        heart_sprites.add(heart)
        all_sprites.add(heart)


update_hearts()

spawn_timer = 0

running = True
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))
    screen.blit(bg_image, (0, 0))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= current_shot_delay:
                    bullet = Bullet(ship.rect.centerx, ship.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    if shoot_sound:
                        shoot_sound.play()
                    last_shot_time = current_time
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False

    # Проверка окончания действия бонуса
    current_time = pygame.time.get_ticks()
    if powerup_active and current_time >= powerup_end_time:
        powerup_active = False
        current_shot_delay = BASE_SHOT_DELAY
        print("Бонус закончился! Скорость стрельбы нормальная")

    # Автострельба
    if space_pressed:
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time >= current_shot_delay:
            bullet = Bullet(ship.rect.centerx, ship.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            if shoot_sound:
                shoot_sound.play()
            last_shot_time = current_time

    # Обновление спрайтов
    keys = pygame.key.get_pressed()
    ship.update(keys)
    bullets.update()
    asteroids.update()
    powerups.update()  # Обновляем бонусы

    # Обновление боссов и их стрельба
    for boss in bosses:
        if boss.update():  # если пора стрелять
            boss_bullet = BossBullet(boss.rect.centerx, boss.rect.bottom)
            all_sprites.add(boss_bullet)
            boss_bullets.add(boss_bullet)
    boss_bullets.update()

    # Спавн астероидов
    spawn_timer += 1
    if spawn_timer > 30:
        spawn_timer = 0
        asteroid_type = random.choices([1, 2], weights=[70, 30])[0]
        asteroid = Asteroid(random.randint(0, WIDTH - 40), asteroid_type)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

    # --- Столкновения пуль игрока с астероидами ---
    for bullet in bullets:
        collided = pygame.sprite.spritecollide(bullet, asteroids, False)
        for asteroid in collided:
            bullet.kill()
            if asteroid.take_damage():
                if dead_asteroid_sound:
                    dead_asteroid_sound.play()
                score += asteroid.points

                # Шанс выпадения бонуса (30% для больших, 15% для маленьких)
                drop_chance = 0.1 if asteroid.asteroid_type == 2 else 0.05
                if random.random() < drop_chance:
                    powerup = PowerUp(asteroid.rect.centerx, asteroid.rect.centery)
                    all_sprites.add(powerup)
                    powerups.add(powerup)

                # Если это большой метеорит, создаём два маленьких
                if asteroid.asteroid_type == 2:
                    # Ограничиваем позиции, чтобы не выходили за границы
                    pos1_x = max(0, min(asteroid.rect.centerx - 20, WIDTH - 40))
                    pos2_x = max(0, min(asteroid.rect.centerx + 20, WIDTH - 40))
                    small_asteroid1 = Asteroid(pos1_x, 1)
                    small_asteroid2 = Asteroid(pos2_x, 1)
                    small_asteroid1.rect.y = asteroid.rect.centery
                    small_asteroid2.rect.y = asteroid.rect.centery
                    all_sprites.add(small_asteroid1, small_asteroid2)
                    asteroids.add(small_asteroid1, small_asteroid2)
                asteroid.kill()
            break

    # --- Столкновения пуль игрока с боссом ---
    for bullet in bullets:
        collided = pygame.sprite.spritecollide(bullet, bosses, False)
        for boss in collided:
            bullet.kill()
            if boss.take_damage():
                score += boss.points
                if dead_asteroid_sound:
                    dead_asteroid_sound.play(-1)
                    dark_sound.stop()
                    music_sound.play(-1)
            break

    # --- Столкновение корабля с бонусами ---
    collected = pygame.sprite.spritecollide(ship, powerups, True)
    for powerup in collected:
        if powerup_sound:
            powerup_sound.play()

        powerup_active = True
        powerup_end_time = pygame.time.get_ticks() + POWERUP_DURATION
        current_shot_delay = SHOT_DELAY_BOOST


    # --- Столкновение корабля с астероидами ---
    if pygame.sprite.spritecollide(ship, asteroids, True):
        lives -= 1
        if lives <= 0:
            if boom_sound:
                boom_sound.play()
            pygame.time.wait(500)
            running = False
        else:
            for heart in heart_sprites:
                heart.kill()
            heart_sprites.empty()
            update_hearts()

    # --- Столкновение корабля с пулями босса ---
    if pygame.sprite.spritecollide(ship, boss_bullets, True):
        lives -= 1
        if lives <= 0:
            if boom_sound:
                boom_sound.play()
            pygame.time.wait(500)
            running = False
        else:
            for heart in heart_sprites:
                heart.kill()
            heart_sprites.empty()
            update_hearts()

    # --- Спавн босса при достижении 250 очков (один раз) ---
    if score >= 10 and not boss1_spawned and len(bosses) == 0:
        boss = Boss(random.randint(100, WIDTH - 100), 50)
        all_sprites.add(boss)
        bosses.add(boss)
        boss1_spawned = True
        spawning_sound.set_volume(1000)
        spawning_sound.play()
        if dark_sound:
            dark_sound.set_volume(0.5)
            dark_sound.play()

    # Отрисовка
    all_sprites.draw(screen)

    # Полоска здоровья босса
    for boss in bosses:
        health_percent = boss.health / 10
        bar_width = 200
        bar_height = 15
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 30

        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width * health_percent, bar_height))

        boss_text = font.render("БОСС", True, (255, 100, 100))
        screen.blit(boss_text, (WIDTH // 2 - 30, 5))

    # Отображение счёта
    score_text = font.render(f"Счёт: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 50))

    # Отображение активного бонуса
    if powerup_active:
        time_left = max(0, (powerup_end_time - pygame.time.get_ticks()) // 1000)
        boost_text = font.render(f"УСКОРЕНИЕ: {time_left}с", True, (0, 255, 0))
        screen.blit(boost_text, (WIDTH - 180, 10))

        # Полоска времени бонуса
        powerup_percent = (powerup_end_time - pygame.time.get_ticks()) / POWERUP_DURATION
        bar_width = 150
        bar_height = 8
        bar_x = WIDTH - 170
        bar_y = 40
        pygame.draw.rect(screen, (0, 100, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * powerup_percent, bar_height))

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()

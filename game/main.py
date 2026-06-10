import pygame
import random
from sprites import Ship, Bullet, Asteroid, Hp

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Shooter")
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)

# Загрузка фона
bg_original = pygame.image.load('assets/fon.png')
bg_image = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))

# ===== ЗАГРУЗКА ЗВУКОВ =====
try:
    boom_sound = pygame.mixer.Sound('assets/Boom.mp3')
    dead_asteroid_sound = pygame.mixer.Sound('assets/DeadAsteroid.mp3')
    shoot_sound = pygame.mixer.Sound('assets/OneShoot.mp3')
    pygame.mixer.music.load('assets/Music.mp3')
    print("Звуки загружены успешно")
except FileNotFoundError as e:
    print(f"Ошибка: не найден звуковой файл - {e}")
    boom_sound = None
    dead_asteroid_sound = None
    shoot_sound = None

# Настройки звука (громкость от 0 до 1)
music_volume = 0.5
sfx_volume = 0.7

# Применяем начальную громкость
if boom_sound:
    boom_sound.set_volume(sfx_volume)
    dead_asteroid_sound.set_volume(sfx_volume)
    shoot_sound.set_volume(sfx_volume)
pygame.mixer.music.set_volume(music_volume)


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 3)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action()
                else:
                    return self.text.lower().replace(" ", "_")
        return None


class Slider:
    def __init__(self, x, y, width, label, initial_value=0.5):
        self.rect = pygame.Rect(x, y, width, 10)
        self.knob_radius = 8
        self.label = label
        self.value = initial_value
        self.dragging = False
        self.font = pygame.font.Font(None, 28)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        knob_x = self.rect.x + self.value * self.rect.width
        pygame.draw.circle(screen, BLUE, (int(knob_x), self.rect.centery), self.knob_radius)
        pygame.draw.circle(screen, WHITE, (int(knob_x), self.rect.centery), self.knob_radius, 2)

        label_text = self.font.render(f"{self.label}: {int(self.value * 100)}%", True, WHITE)
        screen.blit(label_text, (self.rect.x, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_x = self.rect.x + self.value * self.rect.width
            if abs(event.pos[0] - knob_x) <= self.knob_radius and \
                    abs(event.pos[1] - self.rect.centery) <= self.knob_radius:
                self.dragging = True
            elif self.rect.collidepoint(event.pos):
                new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                self.value = (new_x - self.rect.x) / self.rect.width
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = (new_x - self.rect.x) / self.rect.width
            return True
        return False


def show_menu():
    global music_volume, sfx_volume

    start_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50,
                          "Начать игру", GREEN, (0, 200, 0), action=lambda: "start")
    settings_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50,
                             "Настройки", BLUE, (0, 150, 200), action=lambda: "settings")
    quit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50,
                         "Выйти из игры", RED, (200, 0, 0), action=lambda: "quit")

    buttons = [start_button, settings_button, quit_button]
    in_settings = False

    music_slider = Slider(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, "Громкость музыки", music_volume)
    sfx_slider = Slider(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, "Громкость звуков", sfx_volume)
    back_button = Button(WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 40, "Назад", GRAY, DARK_GRAY, action=lambda: "back")

    while True:
        screen.blit(bg_image, (0, 0))

        title_font = pygame.font.Font(None, 74)
        title_text = title_font.render("Asteroid Shooter", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        if not in_settings:
            for button in buttons:
                button.draw(screen)
        else:
            settings_title = pygame.font.Font(None, 48).render("НАСТРОЙКИ", True, WHITE)
            settings_rect = settings_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
            screen.blit(settings_title, settings_rect)
            music_slider.draw(screen)
            sfx_slider.draw(screen)
            back_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if not in_settings:
                for button in buttons:
                    result = button.handle_event(event)
                    if result == "start":
                        return True
                    elif result == "quit":
                        return False
                    elif result == "settings":
                        in_settings = True
            else:
                music_changed = music_slider.handle_event(event)
                if music_changed:
                    music_volume = music_slider.value
                    pygame.mixer.music.set_volume(music_volume)

                sfx_changed = sfx_slider.handle_event(event)
                if sfx_changed:
                    sfx_volume = sfx_slider.value
                    if boom_sound:
                        boom_sound.set_volume(sfx_volume)
                        dead_asteroid_sound.set_volume(sfx_volume)
                        shoot_sound.set_volume(sfx_volume)

                back_result = back_button.handle_event(event)
                if back_result == "back":
                    in_settings = False

        clock.tick(60)


def reset_game():
    """Полностью сбрасывает состояние игры"""
    global all_sprites, bullets, asteroids, heart_sprites, ship, lives, score, spawn_timer, space_pressed, last_shot_time, paused

    all_sprites.empty()
    bullets.empty()
    asteroids.empty()
    heart_sprites.empty()

    ship = Ship(WIDTH // 2 - 25, HEIGHT - 60)
    all_sprites.add(ship)

    lives = 3
    score = 0
    spawn_timer = 0
    space_pressed = False
    last_shot_time = 0
    paused = False

    update_hearts()


def update_hearts():
    """Обновляет отображение сердечек"""
    heart_sprites.empty()
    for i in range(lives):
        heart = Hp(10 + i * 40, 10)
        heart_sprites.add(heart)
        all_sprites.add(heart)


# Показываем меню перед началом игры
if not show_menu():
    pygame.quit()
    exit()

# Запускаем музыку
if not pygame.mixer.music.get_busy():
    pygame.mixer.music.play(-1)

# Инициализация игры
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
heart_sprites = pygame.sprite.Group()

ship = Ship(WIDTH // 2 - 25, HEIGHT - 60)
all_sprites.add(ship)

lives = 3
update_hearts()

score = 0
font = pygame.font.Font(None, 36)
spawn_timer = 0

# Переменные для стрельбы с задержкой
space_pressed = False
last_shot_time = 0
SHOT_DELAY = 500  # миллисекунд

paused = False
running = True

while running:
    clock.tick(60)
    screen.fill(BLACK)
    screen.blit(bg_image, (0, 0))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not paused:
                space_pressed = True
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time >= SHOT_DELAY:
                    bullet = Bullet(ship.rect.centerx, ship.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    if shoot_sound:
                        shoot_sound.play()
                    last_shot_time = current_time
            if event.key == pygame.K_ESCAPE:
                paused = not paused
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False

    # Автоматическая стрельба при зажатой кнопке
    if not paused and space_pressed:
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time >= SHOT_DELAY:
            bullet = Bullet(ship.rect.centerx, ship.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            if shoot_sound:
                shoot_sound.play()
            last_shot_time = current_time

    if not paused:
        # Обновление спрайтов
        keys = pygame.key.get_pressed()
        ship.update(keys)
        bullets.update()
        asteroids.update()

        # Спавн астероидов
        spawn_timer += 1
        if spawn_timer > 30:
            spawn_timer = 0
            asteroid_type = random.choices([1, 2], weights=[70, 30])[0]
            asteroid = Asteroid(random.randint(0, WIDTH - 40), asteroid_type)
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

        # Столкновения пуль с астероидами
        for bullet in bullets:
            collided = pygame.sprite.spritecollide(bullet, asteroids, False)
            for asteroid in collided:
                bullet.kill()
                if asteroid.take_damage():
                    if dead_asteroid_sound:
                        dead_asteroid_sound.play()
                    score += asteroid.points
                break

        # Столкновение корабля с астероидами
        dtp = pygame.sprite.spritecollide(ship, asteroids, True)
        if dtp:
            lives -= 1
            if lives <= 0:
                if boom_sound:
                    boom_sound.play()
                pygame.time.wait(500)
                pygame.mixer.music.stop()

                if show_menu():
                    reset_game()
                    pygame.mixer.music.play(-1)
                else:
                    running = False
                continue
            else:
                for heart in heart_sprites:
                    heart.kill()
                heart_sprites.empty()
                update_hearts()

    # Отрисовка
    all_sprites.draw(screen)

    # Отображение счёта
    score_text = font.render(f"Счёт: {score}", True, WHITE)
    screen.blit(score_text, (10, 50))

    # Отображение паузы
    if paused:
        pause_font = pygame.font.Font(None, 74)
        pause_text = pause_font.render("ПАУЗА", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_text, pause_rect)

        continue_text = font.render("Нажмите ESC для продолжения", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(continue_text, continue_rect)

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()
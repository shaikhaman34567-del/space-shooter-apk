import os
# Android configuration settings (APK ke liye zaroori hain)
os.environ['KIVY_ORIENTATION'] = 'Portrait'

import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# --- RESPONSIVE DISPLAY SETUP ---
# PC par testing ke liye default size, phone par yeh auto-scale ho jayega
BASE_WIDTH, BASE_HEIGHT = 480, 800

# Get actual screen resolution (Android par yeh full screen lega)
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w if info.current_w > 0 else BASE_WIDTH
SCREEN_HEIGHT = info.current_h if info.current_h > 0 else BASE_HEIGHT

# Create surface based on actual screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN if info.current_w > 0 else 0)
pygame.display.set_caption("Touch Space Shooter Pro")

# Scaling factors (taaki touch coordinates coordinates sahi se match hon)
SCALE_X = SCREEN_WIDTH / BASE_WIDTH
SCALE_Y = SCREEN_HEIGHT / BASE_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

clock = pygame.time.Clock()
FPS = 60

# --- GAME OBJECTS ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Size dynamic according to screen scale
        self.w = int(50 * SCALE_X)
        self.h = int(40 * SCALE_Y)
        self.image = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        
        # Responsive Spaceship Drawing
        pygame.draw.polygon(self.image, CYAN, [(self.w // 2, 0), (0, self.h), (self.w, self.h)])
        pygame.draw.polygon(self.image, WHITE, [(self.w // 2, int(10 * SCALE_Y)), (int(10 * SCALE_X), int(35 * SCALE_Y)), (int(40 * SCALE_X), int(35 * SCALE_Y))])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - int(50 * SCALE_Y)
        self.radius = self.w // 2
        self.shoot_delay = 140  
        self.last_shot = pygame.time.get_ticks()

    def update(self, touch_pos):
        if touch_pos:
            # Touch coordinates ko game ki scaling se align karna
            target_x = touch_pos[0]
            target_y = touch_pos[1] - int(40 * SCALE_Y) # Finger ke thoda upar ship dikhega taaki ungli ke peeche chupe nahi

            # Lerp (Linear Interpolation) for butter-smooth movement
            self.rect.centerx += (target_x - self.rect.centerx) * 0.25
            self.rect.centery += (target_y - self.rect.centery) * 0.25
            
            # Screen Boundaries Check
            if self.rect.left < 0: self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
            if self.rect.top < SCREEN_HEIGHT // 2: self.rect.top = SCREEN_HEIGHT // 2 
            if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

    def shoot(self, bullets_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets_group.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.size = int(random.randint(35, 55) * SCALE_X)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        color = random.choice([RED, MAGENTA, YELLOW])
        pygame.draw.ellipse(self.image, color, [0, 0, self.size, self.size])
        pygame.draw.ellipse(self.image, BLACK, [self.size//4, self.size//4, self.size//2, self.size//2])
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randrange(-150, -40)
        
        # Speed scales with screen height so gameplay feels same on all devices
        self.speedy = random.randint(int(3 * SCALE_Y), int((5 + level) * SCALE_Y))
        self.speedx = random.randint(-int(1 * SCALE_X), int(1 * SCALE_X))
        self.radius = self.size // 2

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speedx = -self.speedx
            
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.size)
            self.rect.y = random.randrange(-100, -40)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((int(6 * SCALE_X), int(16 * SCALE_Y)))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -int(14 * SCALE_Y)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        size = random.randint(4, 7)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedx = random.randint(-6, 6)
        self.speedy = random.randint(-6, 6)
        self.lifetime = random.randint(12, 28)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# --- UTILITIES ---
font_name = pygame.font.get_default_font()
def draw_text(surf, text, size, x, y, color=WHITE):
    # Font size handles scaling
    scaled_size = int(size * SCALE_X)
    font = pygame.font.Font(font_name, scaled_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def create_particles(x, y, color, group):
    for _ in range(12):
        p = Particle(x, y, color)
        group.add(p)

# --- MAIN GAME LOOP ---
def main_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    level = 1
    lives = 3
    game_over = False
    is_touching = False
    touch_pos = None

    # Starfield Background
    stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.randint(1, 3)] for _ in range(40)]

    def spawn_enemies(num):
        for _ in range(num):
            e = Enemy(level)
            all_sprites.add(e)
            enemies.add(e)

    spawn_enemies(5)

    running = True
    while running:
        clock.tick(FPS)

        # 1. Improved Event Handling for Android Touch/PC Mouse
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Universal Input Management (Mouse + Touch Screen)
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                is_touching = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    touch_pos = event.pos
                else:
                    touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))

            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
                is_touching = False
                touch_pos = None

            elif event.type == pygame.MOUSEMOTION and is_touching:
                touch_pos = event.pos
            elif event.type == pygame.FINGERMOTION and is_touching:
                touch_pos = (int(event.x * SCREEN_WIDTH), int(event.y * SCREEN_HEIGHT))

            # Restart game on touch if Game Over
            if game_over and (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN):
                main_game()
                return

        # 2. Logic Update
        if not game_over:
            # Background Star Move
            for star in stars:
                star[1] += star[2]
                if star[1] > SCREEN_HEIGHT:
                    star[1] = 0
                    star[0] = random.randint(0, SCREEN_WIDTH)

            if is_touching and touch_pos:
                player.update(touch_pos)
                player.shoot(bullets)
            
            bullets.update()
            enemies.update()
            particles.update()

            all_sprites.add(bullets)
            all_sprites.add(particles)

            # Difficulty Scaling
            if score > level * 600:
                level += 1
                if len(enemies) < 10:  # Enemy cap taaki game crash na ho
                    spawn_enemies(1)

            # Bullet vs Enemy Collision
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True, pygame.sprite.collide_circle)
            for hit in hits:
                score += 50
                create_particles(hit.rect.centerx, hit.rect.centery, hit.image.get_at((hit.size//2, hit.size//2)), particles)
                e = Enemy(level)
                all_sprites.add(e)
                enemies.add(e)

            # Player vs Enemy Collision
            player_hits = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_circle)
            for hit in player_hits:
                lives -= 1
                create_particles(player.rect.centerx, player.rect.centery, CYAN, particles)
                create_particles(hit.rect.centerx, hit.rect.centery, RED, particles)
                
                e = Enemy(level)
                all_sprites.add(e)
                enemies.add(e)
                
                if lives <= 0:
                    game_over = True

        # 3. Drawing / Rendering
        screen.fill(BLACK)

        # Draw Starfield
        for star in stars:
            pygame.draw.circle(screen, WHITE, (star[0], star[1]), star[2])

        all_sprites.draw(screen)

        # Scaled UI Text Layout
        draw_text(screen, f"SCORE: {score}", 18, SCREEN_WIDTH // 5, int(15 * SCALE_Y))
        draw_text(screen, f"LEVEL: {level}", 18, SCREEN_WIDTH // 2, int(15 * SCALE_Y), YELLOW)
        draw_text(screen, f"LIVES: {lives}", 18, (SCREEN_WIDTH // 5) * 4, int(15 * SCALE_Y), RED)

        if game_over:
            draw_text(screen, "GAME OVER", 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - int(40 * SCALE_Y), RED)
            draw_text(screen, f"FINAL SCORE: {score}", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(15 * SCALE_Y), WHITE)
            draw_text(screen, "Tap anywhere to Restart", 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(65 * SCALE_Y), GREEN)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_game()

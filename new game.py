import pygame 
import sys 
import math
import random

# Initialize Pygame 
pygame.init() 

# Screen dimensions 
SCREEN_WIDTH = 800 
SCREEN_HEIGHT = 600 
LEVEL_WIDTH = 2400 

# Colors 
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0) 
RED = (255, 0, 0) 
GREEN = (34, 139, 34)
LINE_WHITE = (240, 240, 240)
RGB = (0, 128, 128) 
BLUE = (0, 0, 255) 
YELLOW = (255, 215, 0) 
ORANGE = (255, 165, 0) 

# Create screen 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
pygame.display.set_caption("Soccer Penalty Shootout Platformer") 
clock = pygame.time.Clock() 

# ===== PLAYER ===== 
class Player(pygame.sprite.Sprite): 
    def __init__(self, x, y): 
        super().__init__() 
        try:
            self.image = pygame.image.load('soccerguy.png').convert_alpha() 
            self.image = pygame.transform.scale(self.image, (33, 44)) 
        except pygame.error:
            self.image = pygame.Surface((33, 44))
            self.image.fill(BLUE)
            
        self.rect = self.image.get_rect() 
        self.rect.x = x 
        self.rect.y = y 
        self.vel_y = 0 
        self.vel_x = 0 
        self.is_jumping = False 
        self.gravity = 0.6 
        self.jump_power = -15 
        self.speed = 5 
        self.level_width = LEVEL_WIDTH 

    def handle_input(self, keys): 
        if keys[pygame.K_LEFT]: 
            self.vel_x = -self.speed 
        elif keys[pygame.K_RIGHT]: 
            self.vel_x = self.speed 
        else: 
            self.vel_x = 0 
        if keys[pygame.K_SPACE] and not self.is_jumping: 
            self.vel_y = self.jump_power 
            self.is_jumping = True 

    def apply_gravity(self): 
        self.vel_y += self.gravity 
        self.rect.y += self.vel_y 
        if self.rect.y > SCREEN_HEIGHT: 
            return False 
        return True 

    def update(self, platforms): 
        self.rect.x += self.vel_x 
        if self.rect.x < 0: 
            self.rect.x = 0 
        if self.rect.x > self.level_width - self.rect.width: 
            self.rect.x = self.level_width - self.rect.width 

        for platform in platforms: 
            if self.vel_y > 0 and self.rect.bottom >= platform.rect.top and self.rect.top < platform.rect.top: 
                if self.rect.right > platform.rect.left and self.rect.left < platform.rect.right: 
                    self.rect.bottom = platform.rect.top 
                    self.vel_y = 0 
                    self.is_jumping = False 

    def draw(self, surface, camera_x): 
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y)) 

# ===== PLATFORM ===== 
class Platform(pygame.sprite.Sprite): 
    def __init__(self, x, y, width, height): 
        super().__init__() 
        self.image = pygame.Surface((width, height)) 
        self.image.fill(RGB) 
        self.rect = self.image.get_rect() 
        self.rect.x = x 
        self.rect.y = y 

    def draw(self, surface, camera_x): 
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y)) 

# ===== COIN ===== 
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 30
        self.base_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.collected = False
        self.animation_timer = 0.0
        self._generate_soccer_pixel_art()

    def _generate_soccer_pixel_art(self):
        pygame.draw.circle(self.base_image, YELLOW, (15, 15), 14)
        pygame.draw.circle(self.base_image, WHITE, (15, 15), 11)
        pygame.draw.rect(self.base_image, BLACK, (13, 13, 5, 5))

    def update(self):
        self.animation_timer += 0.08

    def draw(self, surface, camera_x):
        if not self.collected:
            scale_factor = abs(math.sin(self.animation_timer))
            new_width = max(1, int(self.size * scale_factor))
            spin_frame = pygame.transform.scale(self.base_image, (new_width, self.size))
            center_offset = (self.size - new_width) // 2
            surface.blit(spin_frame, (self.rect.x - camera_x + center_offset, self.rect.y))

# ===== KICKABLE SOCCER BALL =====
class SoccerBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (10, 10), 10)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.is_kicked = False

    def kick(self):
        if not self.is_kicked:
            self.vel_x = 12
            self.vel_y = random.choice([-2, -4, -6, 0, 2]) 
            self.is_kicked = True

    def update(self):
        if self.is_kicked:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

# ===== AI GOALIE =====
class Goalie(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1
        self.speed = 4

    def update(self):
        self.rect.y += self.speed * self.direction
        if self.rect.y <= 360 or self.rect.y >= 510:
            self.direction *= -1

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

# ===== ENEMY (SOCCER DEFENDER) ===== 
class Enemy(pygame.sprite.Sprite): 
    def __init__(self, x, y): 
        super().__init__() 
        try:
            # Using soccerdefender.png for the enemy
            self.image = pygame.image.load('soccerdefender.png').convert_alpha() 
            self.image = pygame.transform.scale(self.image, (40, 50)) 
        except pygame.error:
            self.image = pygame.Surface((40, 50))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect() 
        self.rect.x = x 
        self.rect.y = y 
        self.speed = 2 
        self.direction = 1 
        self.left_bound = x - 80 
        self.right_bound = x + 80 

    def update(self): 
        self.rect.x += self.speed * self.direction 
        if self.rect.x <= self.left_bound or self.rect.x >= self.right_bound: 
            self.direction *= -1 

    def draw(self, surface, camera_x): 
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y)) 

# ===== GAME SYSTEM ===== 
class Game: 
    def __init__(self): 
        self.player = Player(50, 400) 
        self.camera_x = 0 
        self.platforms = [ 
            Platform(0, SCREEN_HEIGHT - 40, LEVEL_WIDTH, 40), 
            Platform(200, 450, 150, 20), 
            Platform(500, 400, 150, 20), 
            Platform(100, 300, 150, 20), 
            Platform(600, 300, 150, 20), 
            Platform(900, 500, 140, 20), 
            Platform(1150, 420, 150, 20), 
            Platform(1400, 350, 150, 20), 
            Platform(1700, 460, 140, 20), 
            Platform(1950, 320, 180, 20),
            Platform(2100, 560, 300, 40) 
        ] 
        self.coin = Coin(1200, 370) 
        self.enemy = Enemy(1550, 430) 
        self.goal_net_rect = pygame.Rect(2340, 350, 50, 210)
        self.goalie = Goalie(2300, 400)
        self.soccer_ball = SoccerBall(2180, 535)
        self.score = 0 
        self.game_over = False 
        self.won = False 
        self.shootout_mode = False

    def handle_events(self): 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                return False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.shootout_mode:
                    self.soccer_ball.kick()
        return True 

    def update(self): 
        keys = pygame.key.get_pressed() 
        self.player.handle_input(keys) 
        if not self.player.apply_gravity(): self.game_over = True 
        self.player.update(self.platforms) 
        self.enemy.update() 
        self.coin.update()

        if not self.coin.collected and self.player.rect.colliderect(self.coin.rect): 
            self.coin.collected = True 
            self.score += 10 

        if self.player.rect.colliderect(self.enemy.rect): 
            self.game_over = True 

        if self.player.rect.x >= 2100:
            self.shootout_mode = True

        if self.shootout_mode:
            self.goalie.update()
            self.soccer_ball.update()
            if self.soccer_ball.rect.colliderect(self.goalie.rect):
                self.soccer_ball = SoccerBall(2180, 535) 
            if self.goal_net_rect.colliderect(self.soccer_ball.rect):
                self.won = True
            self.camera_x = LEVEL_WIDTH - SCREEN_WIDTH
        else:
            target_camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2 
            self.camera_x = max(0, min(target_camera_x, LEVEL_WIDTH - SCREEN_WIDTH)) 

    def draw(self): 
        screen.fill(WHITE) 
        
        if self.shootout_mode:
            pygame.draw.rect(screen, LINE_WHITE, (2150 - self.camera_x, 350, 250, 210), 3) 
            pygame.draw.rect(screen, BLACK, (self.goal_net_rect.x - self.camera_x, self.goal_net_rect.y, self.goal_net_rect.width, self.goal_net_rect.height), 2)
            self.goalie.draw(screen, self.camera_x)
            self.soccer_ball.draw(screen, self.camera_x)

        for platform in self.platforms: 
            platform.draw(screen, self.camera_x) 
            
        self.coin.draw(screen, self.camera_x) 
        self.enemy.draw(screen, self.camera_x) 
        self.player.draw(screen, self.camera_x) 

        font = pygame.font.Font(None, 36) 
        score_text = font.render(f"Score: {self.score}", True, BLACK) 
        screen.blit(score_text, (10, 10)) 

        if self.game_over: 
            text = font.render("STOPPED BY DEFENDER! GAME OVER - Press R", True, RED) 
            screen.blit(text, (200, 250)) 
        if self.won: 
            text = font.render("GOAL!!! YOU WIN! - Press R", True, BLACK) 
            screen.blit(text, (180, 250)) 
            
        pygame.display.flip() 

    def run(self): 
        while True: 
            if not self.handle_events(): break 
            if not self.game_over and not self.won: 
                self.update() 
            self.draw()
            if (self.game_over or self.won) and pygame.key.get_pressed()[pygame.K_r]: 
                self.__init__() 
            clock.tick(60) 
        pygame.quit() 
        sys.exit() 

if __name__ == "__main__": 
    Game().run()
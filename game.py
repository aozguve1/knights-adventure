import pgzrun
from pygame.rect import Rect
import random

TITLE = "Knight's Adventure"
WIDTH = 800
HEIGHT = 600
MENU, PLAYING, GAME_OVER = 0, 1, 2
game_state = MENU
sound_enabled = True

COLORS = {
    'brown': (139, 69, 19),
    'dark_brown': (101, 67, 33),
    'gold': (255, 215, 0),
    'light_brown': (205, 133, 63),
    'stone': (169, 169, 169),
    'sky': (135, 206, 235)
}

class Platform:
    def __init__(self, x, y, width):
        self.rect = Rect(x, y, width, 20)

class Player:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT - 100
        self.velocity_y = 0
        self.jumping = False
        self.direction = 1
        self.frame = 0
        self.animation_timer = 0
        self.health = 100
        self.current_sprite = 'player_idle1'
        self.score = 0
        self.won = False
        self.is_hurt = False
        self.on_platform = False
        self.hurt_timer = 0
        
    def update(self):
        if self.is_hurt:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.is_hurt = False
                
        self.velocity_y += 0.5
        next_y = self.y + self.velocity_y
        self.on_platform = False
        player_rect = Rect(self.x, next_y, 40, 40)
        
        if next_y > HEIGHT - 100:
            self.y = HEIGHT - 100
            self.velocity_y = 0
            self.jumping = False
        else:
            for platform in platforms:
                if player_rect.colliderect(platform.rect):
                    if self.velocity_y > 0 and self.y + 40 <= platform.rect.y + 10:
                        self.y = platform.rect.y - 40
                        self.velocity_y = 0
                        self.jumping = False
                        self.on_platform = True
                        break
            if not self.on_platform:
                self.y = next_y
                
        if keyboard.left or keyboard.right:
            self.animation_timer += 1
            if self.animation_timer >= 10:
                self.frame = (self.frame + 1) % 2
                self.current_sprite = f'player_walk{self.frame + 1}'
                self.animation_timer = 0

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.direction = 1
        self.frame = 0
        self.patrol_start = x
        self.patrol_end = x + 200
        self.current_sprite = f'{enemy_type}_walk1'
        
    def update(self):
        self.x += self.direction * 2
        if self.x > self.patrol_end:
            self.direction = -1
        elif self.x < self.patrol_start:
            self.direction = 1
        self.frame = (self.frame + 1) % 20
        if self.frame % 10 == 0:
            self.current_sprite = f'{self.type}_walk{(self.frame // 10) + 1}'

class Coin:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 20, 20)
        self.x = x
        self.y = y

player = Player()
platforms = [Platform(200, HEIGHT - 200, 150), Platform(500, HEIGHT - 300, 150)]
enemies = [Enemy(300, HEIGHT - 100, "zombie"), Enemy(500, HEIGHT - 100, "soldier")]
coins = [Coin(random.randint(100, WIDTH-100), HEIGHT - 70),
        Coin(220, HEIGHT - 230), Coin(280, HEIGHT - 230),
        Coin(520, HEIGHT - 330), Coin(580, HEIGHT - 330)]

start_button = Rect(250, 200, 300, 60)
sound_button = Rect(250, 300, 300, 60)
exit_button = Rect(250, 400, 300, 60)

def check_coin_collection():
    global coins, game_state
    player_rect = Rect(player.x, player.y, 40, 40)
    for coin in coins[:]:
        if player_rect.colliderect(coin.rect):
            coins.remove(coin)
            if sound_enabled:
                sounds.coin.play()
            player.score += 10
    if len(coins) == 0:
        game_state = GAME_OVER
        player.won = True

def check_enemy_collision():
    global game_state
    player_rect = Rect(player.x, player.y, 40, 40)
    for enemy in enemies:
        if player_rect.colliderect(Rect(enemy.x, enemy.y, 40, 40)):
            player.health -= 1
            player.is_hurt = True
            player.hurt_timer = 20
            if player.health <= 0:
                game_state = GAME_OVER
            if sound_enabled:
                sounds.click.play()

def update():
    if game_state == PLAYING:
        player.update()
        if keyboard.left:
            player.x -= 5
            player.direction = -1
        if keyboard.right:
            player.x += 5
            player.direction = 1
        for enemy in enemies:
            enemy.update()
        check_coin_collection()
        check_enemy_collision()

def draw():
    screen.clear()
    if game_state == MENU:
        screen.fill(COLORS['light_brown'])
        screen.draw.text("Knight's Adventure", center=(400, 100), fontsize=64, color=COLORS['gold'])
        for button in [start_button, sound_button, exit_button]:
            screen.draw.filled_rect(button, COLORS['stone'])
        screen.draw.text("Start Quest", center=(400, 230), fontsize=36, color=COLORS['gold'])
        screen.draw.text(f"Sound: {'On' if sound_enabled else 'Off'}", center=(400, 330), fontsize=36, color=COLORS['gold'])
        screen.draw.text("Exit Kingdom", center=(400, 430), fontsize=36, color=COLORS['gold'])
    
    elif game_state == PLAYING:
        screen.fill(COLORS['sky'])
        for platform in platforms:
            screen.draw.filled_rect(platform.rect, COLORS['brown'])
        screen.draw.filled_rect(Rect(0, HEIGHT - 40, WIDTH, 40), COLORS['brown'])
        screen.draw.filled_rect(Rect(10, 50, (200 * player.health) // 100, 20), (0, 255, 0))
        screen.draw.text(f"Gold: {player.score}", topleft=(10, 10), fontsize=32, color=COLORS['gold'])
        screen.blit('player_hurt' if player.is_hurt else player.current_sprite, (player.x, player.y))
        for enemy in enemies:
            screen.blit(enemy.current_sprite, (enemy.x, enemy.y))
        for coin in coins:
            screen.draw.filled_circle((coin.x + 10, coin.y + 10), 10, COLORS['gold'])
    
    elif game_state == GAME_OVER:
        screen.fill(COLORS['dark_brown'])
        message = "VICTORY!" if player.won else "YOU ARE DEAD"
        screen.draw.text(message, center=(400, 200), fontsize=64, color=COLORS['gold'])
        screen.draw.text(f"Final Gold: {player.score}", center=(400, 400), fontsize=32, color=COLORS['gold'])
        screen.draw.text("Click to Return", center=(400, 500), fontsize=32, color=COLORS['gold'])

def start_game():
    global game_state, player, coins, enemies
    game_state = PLAYING
    player = Player()
    coins = [Coin(random.randint(100, WIDTH-100), HEIGHT - 70),
            Coin(220, HEIGHT - 230), Coin(280, HEIGHT - 230),
            Coin(520, HEIGHT - 330), Coin(580, HEIGHT - 330)]
    enemies = [Enemy(300, HEIGHT - 100, "zombie"), Enemy(500, HEIGHT - 100, "soldier")]
    if sound_enabled:
        sounds.click.play()
        try:
            music.play('medieval_theme')
            music.set_volume(0.5)
        except:
            pass

def on_mouse_down(pos):
    global game_state, sound_enabled
    if game_state == MENU:
        if start_button.collidepoint(pos):
            start_game()
        elif sound_button.collidepoint(pos):
            sound_enabled = not sound_enabled
            if sound_enabled:
                try:
                    music.unpause()
                except:
                    music.play('medieval_theme')
            else:
                music.pause()
        elif exit_button.collidepoint(pos):
            quit()
    elif game_state == GAME_OVER:
        game_state = MENU

def on_key_down(key):
    if game_state == PLAYING and key == keys.SPACE and (not player.jumping and (player.y == HEIGHT - 100 or player.on_platform)):
        player.velocity_y = -12
        player.jumping = True
        if sound_enabled:
            sounds.jump.play()

try:
    music.play('medieval_theme')
    music.set_volume(0.5)
except:
    pass

pgzrun.go()
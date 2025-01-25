import pgzrun
from pygame.rect import Rect
import random
import math

TITLE = "Knight's Adventure"

WIDTH = 800
HEIGHT = 600

MENU = 0
PLAYING = 1
GAME_OVER = 2
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

class Player:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT - 100
        self.velocity_y = 0
        self.jumping = False
        self.direction = 1
        self.frame = 0
        self.animation_timer = 0
        self.idle_frame = 0
        self.idle_timer = 0
        self.health = 100
        self.current_sprite = 'player_idle1'
        self.score = 0
        self.won = False
        self.hurt_timer = 0  
        self.is_hurt = False  
        
    def update(self):
        self.velocity_y += 0.5
        self.y += self.velocity_y
        
        if self.y > HEIGHT - 100:
            self.y = HEIGHT - 100
            self.velocity_y = 0
            self.jumping = False
            
        if self.is_hurt:
            self.hurt_timer += 1
            if self.hurt_timer >= 20: 
                self.is_hurt = False
                self.hurt_timer = 0
            return  
            
        if keyboard.left or keyboard.right:
            self.animate_walk()
        else:
            self.animate_idle()
            
    def animate_walk(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.frame = (self.frame + 1) % 2
            self.current_sprite = f'player_walk{self.frame + 1}'
            self.animation_timer = 0

    def animate_idle(self):
        self.idle_timer += 1
        if self.idle_timer >= 20: 
            self.idle_frame = (self.idle_frame + 1) % 2
            self.current_sprite = f'player_idle{self.idle_frame + 1}'
            self.idle_timer = 0

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type  
        self.direction = 1
        self.frame = 0
        self.animation_timer = 0
        self.patrol_start = x
        self.patrol_end = x + 200
        self.current_sprite = f'{enemy_type}_idle'
        
    def update(self):
        self.x += self.direction * 2
        if self.x > self.patrol_end:
            self.direction = -1
        elif self.x < self.patrol_start:
            self.direction = 1
            
        self.animate_walk()
            
    def animate_walk(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.frame = (self.frame + 1) % 2
            self.current_sprite = f'{self.type}_walk{self.frame + 1}'
            self.animation_timer = 0

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = Rect(x, y, 20, 20)  

class Menu:
    def __init__(self):
        self.options = [
            {"text": "Start Game", "action": self.start_game},
            {"text": "Sound: On", "action": self.toggle_sound},
            {"text": "Quit", "action": self.quit_game}
        ]
        self.selected = 0
        self.sound_on = True

player = Player()
enemies = [
    Enemy(300, HEIGHT - 100, "zombie"),
    Enemy(500, HEIGHT - 100, "soldier")
]
coins = [
    Coin(random.randint(100, WIDTH-100), HEIGHT - 70) for _ in range(5)
]

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
        enemy_rect = Rect(enemy.x, enemy.y, 40, 40)
        if player_rect.colliderect(enemy_rect):
            player.health -= 1
            player.is_hurt = True  
            player.hurt_timer = 0  
            if player.health <= 0:
                game_state = GAME_OVER
            if sound_enabled:
                sounds.click.play()

def update():
    global game_state
    
    if game_state == PLAYING:
        player.update()
        
        # Karakter hareketi
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
        
        screen.draw.text("Knight's Adventure", center=(400, 100), 
                        fontsize=64, color=COLORS['gold'], 
                        shadow=(2, 2), scolor=COLORS['dark_brown'])
        
        for button in [start_button, sound_button, exit_button]:
            screen.draw.filled_rect(button, COLORS['stone'])
            screen.draw.rect(button, COLORS['dark_brown'])
        
        screen.draw.text("Start Quest", center=(400, 230), 
                        fontsize=36, color=COLORS['gold'])
        screen.draw.text("Sound: " + ("On" if sound_enabled else "Off"), 
                        center=(400, 330), fontsize=36, color=COLORS['gold'])
        screen.draw.text("Exit Kingdom", center=(400, 430), 
                        fontsize=36, color=COLORS['gold'])
    
    elif game_state == PLAYING:

        screen.fill(COLORS['sky'])
        
        screen.draw.filled_rect(Rect(0, HEIGHT - 40, WIDTH, 40), COLORS['brown'])
        
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 50

        screen.draw.filled_rect(

            Rect(health_bar_x, health_bar_y, health_bar_width, health_bar_height),
            (255, 0, 0) 

        )
        
        current_health_width = (health_bar_width * player.health) // 100
        if current_health_width > 0: 
            screen.draw.filled_rect(
                Rect(health_bar_x, health_bar_y, current_health_width, health_bar_height),
                (0, 255, 0)  
            )
            
        screen.draw.rect(
            Rect(health_bar_x, health_bar_y, health_bar_width, health_bar_height),
            (0, 0, 0)  
        )
        
        screen.draw.text(f"Gold: {player.score}", topleft=(10, 10), 
                        fontsize=32, color=COLORS['gold'])
        
        if player.is_hurt:
            sprite_name = 'player_hurt'
        else:
            sprite_name = player.current_sprite
        screen.blit(sprite_name, (player.x, player.y))
        
        for enemy in enemies:
            screen.blit(enemy.current_sprite, (enemy.x, enemy.y))
                
        for coin in coins:
            screen.draw.filled_circle((coin.x + 10, coin.y + 10), 10, COLORS['gold'])
            
    elif game_state == GAME_OVER:
        screen.fill(COLORS['dark_brown'])
        if player.won:
            screen.draw.text("VICTORY!", center=(400, 200), 
                        fontsize=64, color=COLORS['gold'], 
                        shadow=(2, 2), scolor='black')
            screen.draw.text("All Treasures Collected!", center=(400, 300), 
                        fontsize=32, color=COLORS['gold'])
        else:
            screen.draw.text("YOU ARE DEAD", center=(400, 200), 
                        fontsize=64, color=COLORS['gold'], 
                        shadow=(2, 2), scolor='black')
            
        screen.draw.text(f"Final Gold: {player.score}", center=(400, 400), 
                        fontsize=32, color=COLORS['gold'])
        screen.draw.text("Click to Return to Castle", center=(400, 500), 
                        fontsize=32, color=COLORS['gold'])

def start_game():
    global game_state, player, coins, enemies
    game_state = PLAYING
    player = Player()
    coins = [
        Coin(random.randint(100, WIDTH-100), HEIGHT - 70) for _ in range(5)
    ]
    enemies = [
        Enemy(300, HEIGHT - 100, "zombie"),
        Enemy(500, HEIGHT - 100, "soldier")
    ]
    if sound_enabled:
        sounds.click.play()
        try:
            music.play('medieval_theme')
            music.set_volume(0.5)
        except:
            print("Unable to upoload music files")

def on_mouse_down(pos):
    global game_state, sound_enabled, player
    
    if game_state == MENU:
        if start_button.collidepoint(pos):
            start_game()
        elif sound_button.collidepoint(pos):
            sound_enabled = not sound_enabled
            if sound_enabled:
                sounds.click.play()
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
    if game_state == PLAYING:
        if key == keys.SPACE and not player.jumping:
            player.velocity_y = -12
            player.jumping = True
            if sound_enabled:
                sounds.jump.play()

try:
    music.play('medieval_theme')
    music.set_volume(0.5)
except:
    print("Unable to upoload music files")

pgzrun.go()

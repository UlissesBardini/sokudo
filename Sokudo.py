# Game Development: Sokudo
import pygame
import random

# Initialize
pygame.init()

# Constants
FPS = 120
WIDTH, HEIGHT = 1000, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
MY_FONT = pygame.font.SysFont("monospace", 20)
mouse = pygame.mouse
mouse.set_visible(True)

# Title
pygame.display.set_caption("Sokudo")

# Icon
ICON = pygame.image.load('assets/sprites/Icon.png')
pygame.display.set_icon(ICON)

# Cursor Animations
CURSOR_IMG = []
for i in range(4):
    CURSOR_IMG.append(pygame.image.load("assets/sprites/Cursor" + str(i) + ".png"))

# Cursor Constants
ACERTOS_MAX = 2
DELAY_SPAWN = FPS * 2
WHITE = 255,255,255
BLACK = 0,0,0

# Fonts
TITLE_FONT = pygame.font.SysFont('lucidasans', 30, False, False)
MENU_FONT = pygame.font.SysFont('lucidasans', 70, False, False)

# Sound Effects
MISS_SFX = pygame.mixer.Sound("assets/sfx/miss.wav")
SCORE_SFX = pygame.mixer.Sound("assets/sfx/score.wav")
WELCOME_SFX = pygame.mixer.Sound("assets/sfx/welcome.wav")

class Cursor:
    def __init__(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.vida = 4
        self.sprite_index = 3
        self.sprite = CURSOR_IMG[self.sprite_index]

    def draw(self):
        SCREEN.blit(self.sprite, (self.x, self.y))

    def move(self):
        self.x = pygame.mouse.get_pos()[0] - self.sprite.get_width()/2
        self.y = pygame.mouse.get_pos()[1] - self.sprite.get_height()/2
    
    def diminuir_vida(self):
        if self.vida > 0:
            self.vida -= 1
            if self.sprite_index > 0:
                self.sprite_index -= 1
        self.sprite = CURSOR_IMG[self.sprite_index]


class Alvo:
    TURN_GREEN = FPS * 1.7
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    RADIUS = 24
    DESPAWN = FPS

    def __init__(self, x: int, y: int, nivel: int):
        self.x, self.y = x, y
        self.color = self.RED
        self.radius = self.RADIUS
        self.turn_green: int = max(
            self.TURN_GREEN - (nivel * FPS * 0.15), FPS/5)
        self.lifetime = 0
        self.despawn: int = max(self.DESPAWN - (nivel * FPS * 0.08), FPS/5)
        self.clickable = False

    def draw(self):
        pygame.draw.circle(SCREEN, self.color, (self.x, self.y), self.radius)

    def life_counter(self):
        self.lifetime += 1
        if self.lifetime >= self.turn_green:
            self.color = self.GREEN
            self.clickable = True
        else:
            self.color = self.RED
            self.clickable = False

    def collide(self, obj):
        offset_x = abs(self.x - (obj.x + obj.sprite.get_width()/2))
        offset_y = abs(self.y - (obj.y + obj.sprite.get_height()/2))
        return offset_x < 16 and offset_y < 16

def main_menu():
    running = True
    WELCOME_SFX.play()
    while running:
        text_title = MENU_FONT.render("sokudo", True, WHITE)
        button_text = TITLE_FONT.render("Play", True, BLACK)
        SCREEN.blit(text_title, (WIDTH/2 - text_title.get_width()/2, HEIGHT/2 - text_title.get_height()/2))
        button = pygame.Rect(WIDTH/2-200/2, HEIGHT/2-50/2+100, 200, 50)
        pygame.draw.rect(SCREEN, WHITE, button)
        SCREEN.blit(button_text, (WIDTH/2 - button_text.get_width()/2, HEIGHT/2 - button_text.get_height()/2+100))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(pygame.mouse.get_pos()):
                    main()
                    running = False
    pygame.quit()

# Loop
def main():
    alvos = []
    spawn_delay_counter:int = 0
    clock = pygame.time.Clock()
    nivel:int = 0
    acertos:int = 0
    score:int = 0
    cursor = Cursor()
    perdeu = False
    show_score_time:int = 0
    mouse.set_visible(False)
    running = True

    def game_over_text():
        texto_lost = TITLE_FONT.render("Game Over!", True, WHITE)
        texto_score = TITLE_FONT.render("Your Score: " + str(score), True, WHITE)
        SCREEN.blit(texto_lost, (WIDTH/2 - texto_lost.get_width()/2, HEIGHT/2 - texto_lost.get_height()/2 - texto_score.get_height() - 10))
        SCREEN.blit(texto_score, (WIDTH/2 - texto_score.get_width()/2, HEIGHT/2 - texto_score.get_height()/2))

    def draw(cursor):
        SCREEN.fill((0, 0, 0))
        for alvo in alvos:
            alvo.draw()
            alvo.life_counter()
        if not perdeu:
            cursor.draw()
        else:
            game_over_text()
        pygame.display.update()

    while running:
        clock.tick(FPS)
        cursor.move()
        draw(cursor)

        if perdeu == True:
            if show_score_time == FPS * 5:
                running = False
            else:
                show_score_time += 1
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for alvo in alvos:
                    if alvo.clickable == True and alvo.collide(cursor):
                        alvos.remove(alvo)
                        acertos += 1
                        score += 100 - round(max((alvo.lifetime - alvo.turn_green) * 100 / Alvo.DESPAWN, 10))
                        SCORE_SFX.play()
                        print(str(score))
                    else:
                        MISS_SFX.play()
                        alvos.remove(alvo)
                        cursor.diminuir_vida()
            
        if cursor.vida == 0:
            perdeu = True
            continue

        for alvo in alvos:
            if alvo.lifetime > alvo.turn_green + alvo.despawn:
                MISS_SFX.play()
                alvos.remove(alvo)
                cursor.diminuir_vida()

        if acertos == ACERTOS_MAX:
            nivel += 1
            acertos = 0

        if spawn_delay_counter > max(DELAY_SPAWN - (nivel * 0.18), FPS/5):
            alvos.append(Alvo(random.randrange(Alvo.RADIUS * 2, WIDTH - Alvo.RADIUS * 2),
                        random.randrange(Alvo.RADIUS * 2, HEIGHT - Alvo.RADIUS * 2), nivel))
            spawn_delay_counter = 0

        spawn_delay_counter += 1

main_menu()
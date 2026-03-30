import sys
import threading
import pygame
import rclpy
from renderer import draw_map
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_HEIGHT, TILE_WIDTH, FPS
from score import ScoreSystem
from map_node import main as map_main
from pylon_camera_aruco import Pac_Coords, main as pylon_main
from ghost import Pacman, Ghost
import gamestate
import time

# Map Farben
WALL_COLOR = (255, 255, 255)
ROAD_COLOR = (0, 0, 0)

# Setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Highscore aus Datei laden
with open("highscore.txt", "r") as f:
    highscore = int(f.read())

# ROS2 starten und die nötigen Nodes in Threads laufen lassen
rclpy.init(args=None)
ros_thread = threading.Thread(target=map_main)     # Map/Topic-Node
pylon_thread = threading.Thread(target=pylon_main) # Kamera/Koordinaten
ros_thread.start()
pylon_thread.start()

gamestate.score_system = ScoreSystem()

# Sprite-Gruppe
all_sprites = pygame.sprite.Group()

# Pacman initial auf Kamerakoordinaten setzen (vorher gab's Polling auf 0/0)
pacman = Pacman((Pac_Coords.x_proj, Pac_Coords.y_proj))
print(f"pacman coords: {pacman.rect.centerx},{pacman.rect.centery}")

# Geister an Start-Tiles erzeugen
ghost1 = Ghost("images/Inky.png",   (1, 1),   "images/vulnerableghost.png", None, all_sprites)
ghost2 = Ghost("images/Blinky.png", (1, 25),  "images/vulnerableghost.png", None, all_sprites)
ghost3 = Ghost("images/Clyde.png",  (47, 25), "images/vulnerableghost.png", None, all_sprites)
ghost4 = Ghost("images/Pinky.png",  (47, 1),  "images/vulnerableghost.png", None, all_sprites)
gamestate.ghosts = [ghost1, ghost2, ghost3, ghost4]

all_sprites.add(pacman, ghost1, ghost2, ghost3, ghost4)

# Font laden (Fallback auf Systemfont, falls TTF fehlt)
try:
    font = pygame.font.Font("font/Press_Start_2P/PressStart2P-Regular.ttf", int(2 * TILE_HEIGHT))
except Exception:
    font = pygame.font.SysFont(None, int(2 * TILE_HEIGHT))

# Musik + kleines Intro (Map zeigen, dann starten)
pygame.mixer.init()
pygame.mixer.music.load("sounds/pacmanmusic.mp3")
screen.fill((0, 0, 0))
draw_map(screen)
pygame.display.flip()
time.sleep(6)               # kurzes Intro-Delay
pygame.mixer.music.play(0)  # Opening-Musik starten (einmalig)

# --- Haupt-Loop: Events → Update → Render ---
running = True 
while running:
    # ESC/Window-Close beendet das Spiel
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Endbildschirm (Victory/Game Over) mit Score/Highscore
    if gamestate.score_system.getstate() == "Victory" or gamestate.score_system.getstate() == "Game Over":
        screen.fill((0, 0, 0))
        if gamestate.score_system.value > highscore:
            highscore = gamestate.score_system.value
            with open("highscore.txt", "w") as f:
                f.write(str(highscore))
        score_text = font.render(gamestate.score_system.getstate(), True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        screen.blit(font.render("Score:  " + f"{gamestate.score_system.value}", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
        screen.blit(font.render("Highscore: " + f"{highscore}", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100))
        pygame.display.flip()
    else:
        # Spiellogik updaten
        all_sprites.update()
        gamestate.score_system.update(pacman, gamestate.ghosts)

        # Render
        screen.fill((0, 0, 0))
        draw_map(screen)
        gamestate.score_system.draw(screen, font)
        all_sprites.draw(screen)
        score_text = font.render(f"{gamestate.score_system.value}", True, (255, 0, 0))
        screen.blit(score_text, (900, TILE_HEIGHT))
    pygame.display.flip()
    clock.tick(FPS)  

try:
    if rclpy.ok():
        rclpy.shutdown()
except Exception:
    pass
ros_thread.join(timeout=1.0)

pygame.quit()
sys.exit()


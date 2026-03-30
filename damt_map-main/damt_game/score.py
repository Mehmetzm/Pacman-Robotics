import pygame
import random
from settings import TILE_WIDTH, TILE_HEIGHT, SCREEN_HEIGHT, SCREEN_WIDTH, MAP
import pygame
pygame.init()
pygame.mixer.init()

# einfache Sprite-Klassen für Items auf der Map
class Pellet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

class SuperPellet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

class Cherry(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))


# Punktesystem + Logik für Pellets, Superpellets und Cherries
class ScoreSystem:
    def __init__(self, frightened_ms=30000):
        # Sounds
        self.eatghost = pygame.mixer.Sound("sounds/eatghost.mp3")
        self.eatpellet = pygame.mixer.Sound("sounds/Chomp.mp3")
        self.gameover = pygame.mixer.Sound("sounds/gameover.mp3")
        self.eatcherry = pygame.mixer.Sound("sounds/fruit.mp3")
        self.spiel = "active"
        self.value = 0
        self.frightened_ms = frightened_ms
        self.ghost_eat_chain = 0  # zählt Geisterkette für Punkte(Funktion wurde entfernt, da Geister auch nicht respwnen etc.)

        # normale Pellets erzeugen aus MAP
        pellet_size = int(min(TILE_WIDTH, TILE_HEIGHT) * 0.4)
        pellet_img = pygame.Surface((pellet_size, pellet_size), pygame.SRCALPHA)
        pygame.draw.circle(pellet_img, (255, 255, 0), (pellet_size // 2, pellet_size // 2), pellet_size // 2)
        self.pellets = pygame.sprite.Group()
        for r, row in enumerate(MAP):
            for c, cell in enumerate(row):
                if cell == ".":
                    cx = c * TILE_WIDTH + TILE_WIDTH // 2
                    cy = r * TILE_HEIGHT + TILE_HEIGHT // 2
                    self.pellets.add(Pellet(cx, cy, pellet_img))

        # Superpellets vorbereiten
        super_size = int(min(TILE_WIDTH, TILE_HEIGHT) * 0.8)
        super_img = pygame.Surface((super_size, super_size), pygame.SRCALPHA)
        pygame.draw.circle(super_img, (255, 255, 0), (super_size // 2, super_size // 2), super_size // 2)
        self.super_img = super_img
        self.superpellets = pygame.sprite.Group()
        # alle Stellen im Labyrinth, wo Pellets liegen könnten
        self.valid_positions = [
            (c * TILE_WIDTH + TILE_WIDTH // 2, r * TILE_HEIGHT + TILE_HEIGHT // 2)
            for r, row in enumerate(MAP)
            for c, cell in enumerate(row) if cell == "."]
        self.SUPER_SPAWN_TIME = 60000  # respawn Zeit
        self.last_super_spawn = pygame.time.get_ticks()
        self.spawn_random_super()

        # Cherry vorbereiten (wird skaliert)
        cherry_img = pygame.image.load('images/Cherry.png').convert_alpha()
        cherry_size = int(min(TILE_WIDTH, TILE_HEIGHT) * 0.6)
        cherry_img = pygame.transform.scale(cherry_img, (cherry_size, cherry_size))
        self.cherry_img = cherry_img
        self.cherries = pygame.sprite.Group()
        self.CHERRY_SPAWN_TIME = 30000
        self.last_cherry_spawn = pygame.time.get_ticks()

    def spawn_random_super(self):
        # nur spawnen, wenn keiner vorhanden ist
        if not self.superpellets and self.valid_positions:
            pos = random.choice(self.valid_positions)
            self.superpellets.add(Cherry(pos[0], pos[1], self.super_img))

    def spawn_random_cherry(self):
        # gleiches Prinzip wie bei Superpellets
        if not self.cherries and self.valid_positions:
            pos = random.choice(self.valid_positions)
            self.cherries.add(Cherry(pos[0], pos[1], self.cherry_img))

    def _any_frightened(self, ghosts):
        # check ob noch ein Geist im frightened Zustand ist
        return any(getattr(g, "state", None) == "frightened" for g in ghosts)

    def update(self, pacman, ghosts):
        now = pygame.time.get_ticks()

        # normale Pellets essen
        eaten_pellets = pygame.sprite.spritecollide(pacman, self.pellets, True)
        if eaten_pellets:
            self.eatpellet.play()
            self.value += len(eaten_pellets) * 10
        if not self.pellets:
            self.spiel = "Victory"  # Sieg wenn alle Pellets weg sind

        # Super-Pellets -> Geister werden frightened
        eaten_super = pygame.sprite.spritecollide(pacman, self.superpellets, True)
        if eaten_super:
            self.value += len(eaten_super) * 50
            self.ghost_eat_chain = 0
            for g in ghosts:
                if hasattr(g, "set_frightened"):
                    g.set_frightened(self.frightened_ms)

        # respawn für Superpellets nach Zeit
        if now - self.last_super_spawn > self.SUPER_SPAWN_TIME:
            self.spawn_random_super()
            self.last_super_spawn = now

        # Geisterkollision
        collided_ghosts = pygame.sprite.spritecollide(pacman, ghosts, False)
        for g in collided_ghosts:
            if getattr(g, "state", None) == "frightened":
                self.eatghost.play()
                self.value += 200
                if hasattr(g, "respawn"):
                    g.respawn()
                g.start_respawn()   # extra Aufruf
            elif getattr(g, "state", None) == "normal":
                self.gameover.play()
                self.spiel = "Game Over"  # Pacman verliert

        # Kette resetten wenn keine frightened-Geister da sind
        if not self._any_frightened(ghosts):
            self.ghost_eat_chain = 0

        # Cherries essen
        eaten_cherries = pygame.sprite.spritecollide(pacman, self.cherries, True)
        if eaten_cherries:
            self.eatcherry.play()
            self.value += len(eaten_cherries) * 100

        # Cherries respawnen
        if now - self.last_cherry_spawn > self.CHERRY_SPAWN_TIME:
            self.spawn_random_cherry()
            self.last_cherry_spawn = now

    # Export Methoden -> geben Positionen zurück
    def export_pellets(self):
        return [(int(pellet.rect.centerx), int(pellet.rect.centery)) for pellet in self.pellets]
    
    def export_superpellets(self):
        return [(int(sp.rect.centerx), int(sp.rect.centery)) for sp in self.superpellets]
    
    def export_cherry(self):
        return [(int(ch.rect.centerx), int(ch.rect.centery)) for ch in self.cherries]

    def draw(self, surface, font):
        # Objekte auf Spielfeld zeichnen
        self.pellets.draw(surface)
        self.superpellets.draw(surface)
        self.cherries.draw(surface)
    
    def getstate(self):
        return self.spiel  # aktueller Spielzustand (active, Victory, Game Over)

        
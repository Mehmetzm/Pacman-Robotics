import pygame, random
from fractions import Fraction
from settings import TILE_WIDTH, TILE_HEIGHT, MAP
from pylon_camera_aruco import Pac_Coords
pygame.init()
pygame.mixer.init()

# Zeiten für frightened-Zustand und Blinken
FRIGHTENED_MS     = 30000
BLINK_LAST_MS     = 2000
BLINK_INTERVAL_MS = 150


# Pacman bewegt sich nur nach Koordinaten aus Pac_Coords
class Pacman(pygame.sprite.Sprite):  
    def __init__(self, start_center: tuple[int, int]):
        super().__init__()
        img = pygame.Surface((130, 130), pygame.SRCALPHA)  # leere Fläche
        #pygame.draw.circle(img, (255, 255, 255), (65, 65), 70)
        self.image = img
        self.rect = self.image.get_rect(center=start_center)

    def set_position(self, x: int, y: int) -> None:
        self.rect.center = (x-75, y-25)  # Offset wegen Projektion

    def update(self):
        self.set_position(Pac_Coords.x_proj, Pac_Coords.y_proj)  # holt sich neue Position jedes Frame
        pass


# Ghost-Klasse: bewegt sich zufällig durchs Labyrinth, kann frightened werden
class Ghost(pygame.sprite.Sprite):
    def __init__(self,
                 image_path: str,
                 start_tile: tuple[int, int],
                 frightened_image_path: str = "vulnerableghost.png",
                 frightened_blink_image_path: str | None = None,
                 sprite_group=None):
        super().__init__()

        self.respawn_time = 30000  # Zeit bis Respawn
        self._respawn_at = 0
        self._waiting_for_respawn = False

        # Bilder laden (normal, frightened, ggf. blinkend)
        normal = pygame.image.load(image_path).convert_alpha()
        self.normal_image = pygame.transform.scale(normal, (TILE_WIDTH, TILE_HEIGHT)).copy()

        frightened = pygame.image.load(frightened_image_path).convert_alpha()
        self.frightened_image = pygame.transform.scale(frightened, (TILE_WIDTH, TILE_HEIGHT)).copy()

        self.frightened_blink_image = None
        if frightened_blink_image_path:
            fb = pygame.image.load(frightened_blink_image_path).convert_alpha()
            self.frightened_blink_image = pygame.transform.scale(fb, (TILE_WIDTH, TILE_HEIGHT)).copy()

        self.image = self.normal_image

        # Startposition ins Zentrum vom Tile setzen
        cx = int(start_tile[0] * TILE_WIDTH  + TILE_WIDTH / 2)
        cy = int(start_tile[1] * TILE_HEIGHT + TILE_HEIGHT / 2)
        self.start_tile = start_tile
        self.rect = self.image.get_rect()
        self.rect.center = (cx, cy)
        self.start_center = (cx, cy)

        # Geschwindigkeit berechnen anhand Tile-Verhältnis, damit  es flüssig aussieht
        frac = Fraction(TILE_HEIGHT / TILE_WIDTH).limit_denominator()
        self.speed = TILE_WIDTH / frac.denominator
        self.move_limitw = TILE_WIDTH  // self.speed
        self.move_limith = (TILE_HEIGHT / TILE_WIDTH) * frac.denominator

        # Bewegungsdaten
        self.way = "right"
        self.history = ""
        self.move_counter = 0

        # State-Infos
        self.state = "normal"      # "normal" oder "frightened"
        self.frightened_until = 0
        self._blink_toggle = False
        self._next_blink_at = 0

    # wird aufgerufen, wenn Pacman ein Superpellet frisst
    def set_frightened(self, duration_ms: int = FRIGHTENED_MS) -> None:
        now = pygame.time.get_ticks()
        pygame.mixer.music.load("sounds/vulnerableghost.mp3")
        pygame.mixer.music.play(6)
        self.image.set_alpha(255)
        self.state = "frightened"
        self.frightened_until = now + duration_ms
        self.image = self.frightened_image
        self._blink_toggle = False
        self._next_blink_at = now + BLINK_INTERVAL_MS

    # Zustand und Sprite-Bild aktualisieren (Blinken vor Ablauf)
    def _update_state_and_image(self) -> None:
        if self.state != "frightened":
            return
        now = pygame.time.get_ticks()
        if now >= self.frightened_until:
            self.state = "normal"
            self.image = self.normal_image
            return
        remaining = self.frightened_until - now
        if remaining <= BLINK_LAST_MS and now >= self._next_blink_at:
            self._blink_toggle = not self._blink_toggle
            self._next_blink_at = now + BLINK_INTERVAL_MS
            if self.frightened_blink_image:
                self.image = self.frightened_blink_image if self._blink_toggle else self.frightened_image
            else:
                self.image = self.normal_image if self._blink_toggle else self.frightened_image
        elif remaining > BLINK_LAST_MS:
            self.image = self.frightened_image

    def is_inside_map(self, row: int, col: int) -> bool:
        return 0 <= row < len(MAP) and 0 <= col < len(MAP[0])

    def update(self) -> None:
        # Falls tot -> warten bis Respawn
        if self._waiting_for_respawn:
            if pygame.time.get_ticks() >= self._respawn_at:
                self.state = "normal"
                self.image = self.normal_image
                self.image.set_alpha(255)
                self._waiting_for_respawn = False
            return
        self.image.set_alpha(255)

        # frightened-State checken (blinken usw.)
        self._update_state_and_image()

        # aktuelle Tile-Position bestimmen
        col = int(self.rect.centerx // TILE_WIDTH)
        row = int(self.rect.centery // TILE_HEIGHT)

        # neue Richtung nur am Tile-Mittelpunkt wählen
        if self.move_counter == 0:
            direction: list[str] = []

            # mögliche Wege checken (keine Rückkehr direkt)
            if self.is_inside_map(row, col + 1) and MAP[row][col + 1] == "." and self.history != "right":
                direction.append("right")
            if self.is_inside_map(row + 1, col) and MAP[row + 1][col] == "." and self.history != "down":
                direction.append("down")
            if self.is_inside_map(row, col - 1) and MAP[row][col - 1] == "." and self.history != "left":
                direction.append("left")
            if self.is_inside_map(row - 1, col) and MAP[row - 1][col] == "." and self.history != "up":
                direction.append("up")

            if direction:
                self.way = random.choice(direction)
                self.move_counter = self.move_limitw if self.way in ("right", "left") else self.move_limith

        # Bewegung in gewählter Richtung
        if self.way == "right":
            self.rect.centerx += self.speed
            self.history = "left"
        elif self.way == "down":
            self.rect.centery += self.speed
            self.history = "up"
        elif self.way == "left":
            self.rect.centerx -= self.speed
            self.history = "right"
        elif self.way == "up":
            self.rect.centery -= self.speed
            self.history = "down"

        self.move_counter -= 1

    # Respawn starten(Respawn entfernt, damit Pacman einfacher gewinnen kann)
    def start_respawn(self):    
        self._waiting_for_respawn = True
        self._respawn_at = pygame.time.get_ticks() + self.respawn_time
        self.image.set_alpha(0)
        self.rect.center = (-1000, -1000)  # ausserhalb der Map

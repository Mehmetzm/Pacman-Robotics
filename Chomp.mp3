import pygame
from settings import TILE_WIDTH, TILE_HEIGHT, WALL_COLOR, ROAD_COLOR, MAP
#Map zeichnen
def draw_map(screen):
    for row_idx, row in enumerate(MAP):
        for col_idx, cell in enumerate(row):
            x = col_idx * TILE_WIDTH
            y = row_idx * TILE_HEIGHT

            if cell == '.':
                pygame.draw.rect(screen, WALL_COLOR, (x, y, TILE_WIDTH, TILE_HEIGHT))
            elif cell == 'W':
                road_w = TILE_WIDTH * 0.4
                road_h = TILE_HEIGHT * 0.4
                offset_x = (TILE_WIDTH - road_w) / 2
                offset_y = (TILE_HEIGHT - road_h) / 2
                pygame.draw.rect(screen, ROAD_COLOR, (x + offset_x, y + offset_y, road_w, road_h))

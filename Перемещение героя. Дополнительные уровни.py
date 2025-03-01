import pygame
import os
import sys

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 501, 501
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Перемещение героя')

clock = pygame.time.Clock()
FPS = 50


def load_image(filename, color_key=None):
    full_path = os.path.join('data', filename)
    if not os.path.isfile(full_path):
        print(f"Файл с изображением '{full_path}' не найден")
        sys.exit()
    image = pygame.image.load(full_path)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    file_path = os.path.join('data', filename)
    with open(file_path, 'r') as file:
        level_map = [line.strip() for line in file]
    max_width = max(map(len, level_map))
    return [line.ljust(max_width, '.') for line in level_map]


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    player = None
    level_width = len(level[0])
    level_height = len(level)
    for y in range(level_height):
        for x in range(level_width):
            cell = level[y][x]
            if cell == '.':
                Tile('empty', x, y)
            elif cell == '#':
                Tile('wall', x, y)
            elif cell == '@':
                Tile('empty', x, y)
                player = Player(x, y)
    return player, level_width, level_height


def quit_game():
    pygame.quit()
    sys.exit()


def show_start_screen():
    intro_text = [
        "ЗАСТАВКА",
        "",
        "Правила игры",
        "Если в правилах несколько строк,",
        "приходится выводить их построчно"
    ]

    background = pygame.transform.scale(load_image('fon.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_y = 50
    for line in intro_text:
        text_surface = font.render(line, True, pygame.Color('black'))
        text_rect = text_surface.get_rect()
        text_y += 10
        text_rect.top = text_y
        text_rect.x = 10
        text_y += text_rect.height
        screen.blit(text_surface, text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            TILE_SIZE * pos_x + 15, TILE_SIZE * pos_y + 5)

    def move(self, direction):
        previous_position = self.rect.copy()
        if direction == 'up' and self.rect.y - TILE_SIZE >= 0:
            self.rect.y -= TILE_SIZE
        elif direction == 'down' and self.rect.y + TILE_SIZE <= (level_height - 1) * TILE_SIZE:
            self.rect.y += TILE_SIZE
        elif direction == 'left' and self.rect.x - TILE_SIZE >= 0:
            self.rect.x -= TILE_SIZE
        elif direction == 'right' and self.rect.x + TILE_SIZE <= (level_width - 1) * TILE_SIZE:
            self.rect.x += TILE_SIZE

        for tile in tiles_group:
            if tile.rect.colliderect(self.rect) and tile.tile_type == 'wall':
                self.rect = previous_position
                break


if __name__ == '__main__':
    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mar.png')
    TILE_SIZE = 50

    try:
        level_name = input('Введите название карты или "default": ')
        if level_name == 'default':
            level_name = 'map1.txt'
        player, level_width, level_height = generate_level(load_level(level_name))
    except Exception as e:
        print(f"Ошибка: {e}")
        quit_game()

    show_start_screen()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move('up')
                elif event.key == pygame.K_DOWN:
                    player.move('down')
                elif event.key == pygame.K_LEFT:
                    player.move('left')
                elif event.key == pygame.K_RIGHT:
                    player.move('right')

        screen.fill((255, 255, 255))
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

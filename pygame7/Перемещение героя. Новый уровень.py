import pygame
import os
import sys

SCREEN_WIDTH, SCREEN_HEIGHT = 700, 700
FPS = 50

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Перемещение героя')
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name):
    path = os.path.join('data', name)
    if not os.path.isfile(path):
        print(f"Файл с изображением '{path}' не найден")
        sys.exit()
    return pygame.image.load(path)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

TILE_SIZE = 50


def load_level(filename):
    with open(os.path.join('data', filename), 'r') as file:
        level_map = [line.strip() for line in file]
    max_width = max(len(line) for line in level_map)
    return [line.ljust(max_width, '.') for line in level_map]


def generate_level(level, flag=True, x_pos=None, y_pos=None):
    new_player = None
    tiles_group.empty()
    for y in range(len(level)):
        for x in range(len(level[y])):
            if y == y_pos and x == x_pos:
                Tile('empty', x, y)
                player_group.empty()
                new_player = Player(x, y)
                level[y] = level[y][:x] + '@' + level[y][x + 1:]
            elif level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@' and flag:
                Tile('empty', x, y)
                new_player = Player(x, y)
            else:
                Tile('empty', x, y)
    return new_player, x, y, level


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "", "Правила игры", "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]
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
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, x, y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(TILE_SIZE * x + 15, TILE_SIZE * y + 5)

    def move(self, direction):
        global player, level_x, level_y, level_map
        last_pos = self.rect.copy()
        if direction == 'up' and self.rect.y - 55 >= 0:
            self.rect.y -= TILE_SIZE
            if self.check_collision():
                self.rect = last_pos
            else:
                x, y = self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE
                y += 1
                level_map = move_level_down(level_map)
                player, level_x, level_y, level_map = generate_level(level_map, False, x, y)

        if direction == 'down' and self.rect.y + 95 <= level_y * TILE_SIZE:
            self.rect.y += TILE_SIZE
            if self.check_collision():
                self.rect = last_pos
            else:
                x, y = self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE
                y -= 1
                level_map = move_level_up(level_map)
                player, level_x, level_y, level_map = generate_level(level_map, False, x, y)

        if direction == 'right' and self.rect.x + 55 <= level_x * TILE_SIZE:
            self.rect.x += TILE_SIZE
            if self.check_collision():
                self.rect = last_pos
            else:
                x, y = self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE
                x -= 1
                level_map = move_level_left(level_map)
                player, level_x, level_y, level_map = generate_level(level_map, False, x, y)

        if direction == 'left' and self.rect.x - 55 >= 0:
            self.rect.x -= TILE_SIZE
            if self.check_collision():
                self.rect = last_pos
            else:
                x, y = self.rect.x // TILE_SIZE, self.rect.y // TILE_SIZE
                x += 1
                level_map = move_level_right(level_map)
                player, level_x, level_y, level_map = generate_level(level_map, False, x, y)

    def check_collision(self):
        for tile in tiles_group:
            if tile.rect.colliderect(self.rect) and tile.tile_type == 'wall':
                return True
        return False


def move_level_up(level):
    level.append(level.pop(0))
    return level


def move_level_down(level):
    level.insert(0, level.pop())
    return level


def move_level_left(level):
    return [row[1:] + row[0] for row in level]


def move_level_right(level):
    return [row[-1] + row[:-1] for row in level]


if __name__ == '__main__':
    try:
        map_name = input('Введите название карты или "default" для стандартной: ')
        if map_name == 'default':
            map_name = 'map4.txt'
        level_map = load_level(map_name)
        player, level_x, level_y, level_map = generate_level(level_map)
    except Exception as e:
        print(f'Ошибка: {e}')
        terminate()

    start_screen()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move('up')
                if event.key == pygame.K_DOWN:
                    player.move('down')
                if event.key == pygame.K_RIGHT:
                    player.move('right')
                if event.key == pygame.K_LEFT:
                    player.move('left')
        screen.fill((0, 0, 0))
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

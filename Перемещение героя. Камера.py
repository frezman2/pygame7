import pygame
import os
import sys

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 501, 501
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Перемещение героя')

clock = pygame.time.Clock()
FPS = 50


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return [line.ljust(max_width, '.') for line in level_map]


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, x, y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    bg = pygame.transform.scale(load_image('fon.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')

TILE_SIZE = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x, TILE_SIZE * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(TILE_SIZE * pos_x + 15, TILE_SIZE * pos_y + 5)

    def move(self, direction):
        last_pos = self.rect.copy()
        if direction == 'up' and self.rect.y - 55 >= 0:
            self.rect.y -= TILE_SIZE
        if direction == 'down' and self.rect.y + 95 <= level_y * TILE_SIZE:
            self.rect.y += TILE_SIZE
        if direction == 'right' and self.rect.x + 55 <= level_x * TILE_SIZE:
            self.rect.x += TILE_SIZE
        if direction == 'left' and self.rect.x - 55 >= 0:
            self.rect.x -= TILE_SIZE
        for tile in tiles_group:
            if tile.rect.colliderect(self.rect) and tile.tile_type == 'wall':
                self.rect = last_pos
                break


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - SCREEN_HEIGHT // 2)


if __name__ == '__main__':
    try:
        new_map = input('Введите название желаемой карты либо напишите default для открытия стандартной карты: ')
        if new_map == 'default':
            new_map = 'map1.txt'
        player, level_x, level_y = generate_level(load_level(new_map))
    except Exception:
        print('Ошибка!')
        terminate()

    pygame.init()
    pygame.display.set_caption('Перемещение героя')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    start_screen()

    camera = Camera()
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
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

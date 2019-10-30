import pygame
import sys
import random

pygame.init()
pygame.key.set_repeat(200, 70)

# размеры всего поля в клетках
WIDTH_FIELD = 100
HEIGHT_FIELD = 7

# размеры экрана в пикселях
WIDTH_SCREEN = 675
HEIGHT_SCREEN = 525
SIZE_SCREEN = WIDTH_SCREEN, HEIGHT_SCREEN
screen = pygame.display.set_mode(SIZE_SCREEN)
clock = pygame.time.Clock()

# параметры цикла
FPS = 50
STEP = 75

#счёт
global corn_score
corn_score = 0
global grass_score
grass_score = 0

# генерируем уровень в файл
tiles = ['.', '#', 'x']
# . = поле
# x - сорняк
#  - кукуруза
# - @ - трактор
field = []
line = []
flag = True
for _ in range(HEIGHT_FIELD + 1):
    for _ in range(WIDTH_FIELD):
        line.append(random.choice(tiles))
    if flag:
        line[0] = '@'
        flag = False
    field.append(''.join(line))
    line = []

f = open('field.txt', 'wt')
for lines in field:
    f.write(lines + '\n')
f.close()

# создаём группы спрайтов
player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
corn_group = pygame.sprite.Group()
flower_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

# метод загрузки изображения из фйла
def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
    return image

# читаем уровень из файла
def load_level(filename):
    # level_map - список строк из файла
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map

# отображаем уровень на экране
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('field', x, y)
            elif level[y][x] == '#':
                Tile_corn('corn', x, y)
            elif level[y][x] == 'x':
                Tile_flower('flower', x, y)
            elif level[y][x] == '@':
                Tile('field', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y

# выход
def terminate():
    pygame.quit()
    sys.exit()

#финальная заставка
def game_over():
    global corn_score
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH_SCREEN, HEIGHT_SCREEN))
    screen.blit(fon, (0, 0))
    head = "Ваш счёт: {}".format(corn_score)
    font = pygame.font.Font(None, 40)
    text_coord = 150
    string_rendered = font.render(head, 1, pygame.Color('darkgreen'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 50
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)

# Стартовая заставка
def start_screen():
    global grass_score
    intro_text = ["",
                  "Трактор должен собрать урожай кукурузы,",
                  "объезжая сорняки.",
                  "Если трактор собрал 10 сорняков, игра заканчивается.",
                  "Нажмите любую клавишу."]
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH_SCREEN, HEIGHT_SCREEN))
    screen.blit(fon, (0, 0))
    head = "Правила игры"
    font = pygame.font.Font(None, 40)
    text_coord = 150
    string_rendered = font.render(head, 1, pygame.Color('darkgreen'))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = text_coord
    intro_rect.x = 50
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)

    font = pygame.font.Font(None, 30)
    text_coord = 150
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('darkgreen'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

# задаём набор элементов поля
tile_images = {'field': load_image('field.png'), 'corn': load_image('corn.png'), 'flower': load_image('flower.png')}
player_image = load_image('car.png')

# размер клетки
tile_width = tile_height = 75

# определяет положение клетки
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

# расставляем кукурузы
class Tile_corn(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, corn_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def update(self, *args):
        # трактор собрал кукурузу
        global corn_score
        if pygame.sprite.spritecollideany(self, player_group):
            self.kill()
            Tile('field', self.pos_x, self.pos_y)
            corn_score += 1

# расставляем сорняки
class Tile_flower(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, flower_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.pos_x = pos_x
        self.pos_y = pos_y

    def update(self, *args):
        # трактор взял сорняк
        global grass_score
        if pygame.sprite.spritecollideany(self, player_group):
            self.kill()
            Tile('field', self.pos_x, self.pos_y)
            grass_score += 1

# определяет положение игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

# камера
class Camera:
    # зададим начальный сдвиг камеры и размер поля для возможности реализации циклического сдвига
    def __init__(self, field_size):
        self.dx = 0
        self.dy = 0
        self.field_size = field_size
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        # вычислим координату, если она уехала влево за границу экрана
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.field_size[0] + 1) * obj.rect.width
        # вычислим координату, если она уехала вправо за границу экрана
        if obj.rect.x >= (self.field_size[0]) * obj.rect.width:
            obj.rect.x += -obj.rect.width * (1 + self.field_size[0])
        obj.rect.y += self.dy
        # вычислим координату, если она уехала вверх за границу экрана
        if obj.rect.y < -obj.rect.height:
            obj.rect.y += (self.field_size[1] + 1) * obj.rect.height
        # вычислим координату, если она уехала вниз за границу экрана
        if obj.rect.y >= (self.field_size[1]) * obj.rect.height:
            obj.rect.y += -obj.rect.height * (1 + self.field_size[1])
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH_SCREEN // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT_SCREEN // 2)

# вызов стартовой заставки
start_screen()

# создаём уровень
player, level_x, level_y = generate_level(load_level("field.txt"))
camera = Camera((level_x, level_y))

#игровой цикл
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.rect.x -= STEP
            if event.key == pygame.K_RIGHT:
                player.rect.x += STEP
            if event.key == pygame.K_UP:
                player.rect.y -= STEP
            if event.key == pygame.K_DOWN:
                player.rect.y += STEP
        if grass_score == 10:
            game_over()

    camera.update(player)

    for sprite in all_sprites:
        camera.apply(sprite)

    tiles_group.draw(screen)
    player_group.draw(screen)
    all_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)

terminate()
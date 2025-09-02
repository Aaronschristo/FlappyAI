from random import choice, randint
from sys import exit
import os
import neat
import pygame as pg
import base64
import pickle

pg.mixer.pre_init(frequency=44100, size=16, channels=1, buffer=512)
pg.init()


class Bird(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = [pg.image.load('graphics/Bird/upflap.png').convert_alpha(),
                       pg.image.load('graphics/Bird/midflap.png').convert_alpha(),
                       pg.image.load('graphics/Bird/downflap.png').convert_alpha()]
        self.index = 0
        self.gravity = 0.3
        self.velocity = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(midbottom=(50, randint(200, 550)))
        self.mask = pg.mask.from_surface(self.image)

    def jump(self):
        if self.velocity > -4 and self.running:
            self.velocity = -8
            #wing_sound.play()

    def animate(self):
        self.index += 0.1
        if self.index > len(self.frames):
            self.index = 0
        self.image = self.frames[int(self.index)]

        self.angle = -(self.velocity / 6) * 45
        if self.angle < -25:
            self.angle = -25

        rect = self.rect
        self.image = pg.transform.rotozoom(self.image, self.angle, 1)
        self.rect = self.image.get_rect(center=rect.center)

    def out(self):
        if self.rect.top < -20 or self.rect.bottom > 570:
            return True

        return False

    def update(self, running):
        self.running = running
        self.animate()
        self.rect.bottom += self.velocity
        self.velocity += self.gravity
        #self.jump()


class Pipe(pg.sprite.Sprite):
    def __init__(self, color, pos):
        super().__init__()
        if color == 'Red':
            self.frame = pg.image.load('graphics/pipe-red.png').convert_alpha()
        else:
            self.frame = pg.image.load('graphics/pipe-green.png').convert_alpha()

        self.image = self.frame
        self.rect = self.image.get_rect(midtop=(800, pos))
        self.mask = pg.mask.from_surface(self.image)

    def move(self):
        self.rect.left -= 8
        if self.rect.left < -100:
            self.kill()

    def update(self):
        self.move()


class UpPipe(pg.sprite.Sprite):
    def __init__(self, color, pos):
        super().__init__()
        if color == 'Red':
            self.frame = pg.image.load('graphics/pipe-red.png').convert_alpha()
        else:
            self.frame = pg.image.load('graphics/pipe-green.png').convert_alpha()

        self.image = pg.transform.flip(self.frame, False, True)
        self.rect = self.image.get_rect(midtop=(800, pos))
        self.rect.bottom = self.rect.top - 200

    def move(self):
        self.rect.left -= 8
        if self.rect.left < -100:
            self.kill()

    def update(self):
        self.move()


def ground_animation():
    ground_rect.left -= 8
    if ground_rect.right < 0:
        ground_rect.left = 0
    screen.blit(ground, ground_rect)
    ground_rect.left = ground_rect.right
    screen.blit(ground, ground_rect)
    ground_rect.left -= 800

def display(content, font, center, flair=False, color=None):
    text = font.render(content, False, (64, 64, 64))
    text_rect = text.get_rect(center=center)
    if color is not None:
        bg_surf = pg.Surface(text_rect.size)
        bg_surf.fill(color)
        screen.blit(bg_surf, text_rect)
        bg_surf = pg.Surface(text_rect.size)
        bg_surf.fill(color)
        screen.blit(bg_surf, crown_rect)
    if flair:
        crown_rect.right = text_rect.left - 5
        screen.blit(crown, crown_rect)
    screen.blit(text, text_rect)

def draw(pipes, upPipes, bird, running, score, hi_score):
    screen.fill((192, 232, 236))
    screen.blit(sky, (0, 0))
    pipes.draw(screen)
    upPipes.draw(screen)
    ground_animation()
    bird.draw(screen)
    display(str(score // 10), score_font, (400, 30))
    display(str(hi_score), hi_score_font, (700, 25), True)

def update(pipes, upPipes, bird, running, score, hi_score):
    pipes.update()
    upPipes.update()
    bird.update(running)

def collision(bird, pipes, upPipes):
    if pg.sprite.spritecollide(bird, pipes, False) or pg.sprite.spritecollide(bird, upPipes,
                                                                                     False) or bird.out():
        if pg.sprite.spritecollide(bird, pipes, False, pg.sprite.collide_mask) or pg.sprite.spritecollide(
                bird, upPipes, False, pg.sprite.collide_mask) or bird.out():
            bird.kill()
            return True

    return False

def clear(bird, pipes, upPipes):
    pg.display.update()
    bird.rect.bottom = 550
    bird.velocity = 0
    pipes.empty()
    upPipes.empty()

def add_sprites(Sprite, group, count):
    for i in range(count):
        group.add(Sprite())

def encode(num):
    num = bytes(num)
    for i in range(10):
        num = base64.b64encode(num)

    pickle.dump(str(num).removeprefix("b'").removesuffix("'"), open('hi_score.pickle', 'wb'), pickle.HIGHEST_PROTOCOL)

def decode(file):
    num = str(pickle.load(open(file, 'rb')))
    for i in range(10):
        num = base64.b64decode(num)

    return (len(str(num))-3)//4

def save_high_score(score):
    global hi_score 
    if score // 10 > hi_score:
         hi_score = score // 10
         encode(hi_score)

def save_bird(obj):
    pickle.dump(obj, open('bird.pickle', 'wb'), pickle.HIGHEST_PROTOCOL)

def get_pipe_y(pipes, x):
    for pipe in pipes:
        if pipe.rect.centerx > x:
            return pipe.rect.top

screen = pg.display.set_mode((800, 600))
pg.display.set_caption('Flappy Bird')
pg.display.set_icon(pg.image.load('favicon.ico').convert_alpha())

sky = pg.image.load('graphics/Sky.png').convert()

ground = pg.image.load('graphics/base.png').convert()
ground_rect = ground.get_rect(topleft=(0, 550))

wing_sound = pg.mixer.Sound('audio/sfx_wing.wav')
wing_sound.set_volume(0.17)

score_sound = pg.mixer.Sound('audio/sfx_point.wav')
score_sound.set_volume(0.17)

crown = pg.image.load('graphics/crown.png')
crown_rect = crown.get_rect(midbottom=(600, 37))

score_font = pg.font.Font('04B_19.ttf', 50)
hi_score_font = pg.font.Font('04B_19.ttf', 40)
title_font = pg.font.Font('04B_19.ttf', 100)
text_font = pg.font.Font('04B_19.ttf', 25)
your_score_font = pg.font.Font('04B_19.ttf', 50)

clock = pg.time.Clock()

title_pos = (400, 290)
text_pos = (400, 450)
your_score_pos = (400, 450)

score = 0
hi_score = decode('hi_score.pickle')
draw_sprites = True

pipes = pg.sprite.Group()
upPipes = pg.sprite.Group()
birds = pg.sprite.Group()


def game(genomes, config):
    global score
    global hi_score

    score = 0

    nets = []
    ge = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        ge.append(g)

    running = True

    color = choice(['Red', 'Green', 'Green'])
    pos = randint(300, 500)
    pipes.add(Pipe(color, pos))
    upPipes.add(UpPipe(color, pos))

    fps = 60000
    timer = 54
    cycles = 0

    screen.fill((192, 232, 236))

    add_sprites(Bird, birds, len(genomes))

    birds_list = birds.sprites()
    pipe_y = 0

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                save_high_score(score)
                pg.quit()
                exit()
        if cycles == timer:
            cycles = 0
            color = choice(['Red', 'Green', 'Green'])
            pos = randint(300, 500)
            pipes.add(Pipe(color, pos))
            upPipes.add(UpPipe(color, pos))

        if running:
            score += 1
            birds_list = birds.sprites()
            bird_x = birds_list[0].rect.centerx
            last_pipe_y = pipe_y
            pipe_y = get_pipe_y(pipes, bird_x)
            award = False
            if last_pipe_y != pipe_y:
                award = True

            upPipe_y = pipe_y - 150

            if draw_sprites:
                draw(pipes, upPipes, birds, running, score, hi_score)
            else:

                display(str(score // 10), score_font, (400, 30), color=(192, 232, 236))
                display(str(hi_score), hi_score_font, (700, 25), True)

            update(pipes, upPipes, birds, running, score, hi_score)

            for x, bird in enumerate(birds_list):
                ge[x].fitness += 0.1
                if award:
                    ge[x].fitness += 5
                y = bird.rect.centery

                outputs = nets[x].activate((y, abs(y - pipe_y), abs(y - upPipe_y)))

                if outputs[0] > 0:
                    bird.jump()

                if collision(bird, pipes, upPipes):
                    ge[x].fitness -= 1
                    nets.pop(x)
                    ge.pop(x)
                    birds_list.pop(x)



            for g in ge:
                g.fitness += 5

            if not birds_list:
                clear(bird, pipes, upPipes)
                running = False
                save_high_score(score)

        pg.display.update()
        clock.tick(fps)
        cycles += 1


def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(game, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)

#!/usr/bin/env python3
"""
1. background
2. collisions with walls
3. make the map
4. sprite work
5. sound and music
6. menu
* * *
- agents
- improved controls
- animations
- statistics screen
- timer
"""

import pygame
import math
import csv

class App:
    def __init__(self):
        pygame.init()
        self.running = True

        self.size = self.width, self.height = 1024, 768

        # actual display
        self.screen = pygame.display.set_mode(self.size)
        # surface everything is blitted to
        self.display = pygame.Surface((1024, 768))

        self.clock = pygame.time.Clock()
        self.dragging = None

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        # left click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # check if we clicked on Guerrilla
            for guerrilla in Guerrilla.group:
                # if mouse intersects with guerrilla
                if guerrilla.rect.collidepoint(event.pos):
                   self.dragging = guerrilla
                   pygame.mouse.set_visible(False)
                   Target.group.add(Target(event.pos))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging is not None:
                self.dragging.target = event.pos
                self.dragging = None
                Target.group.sprite.destroy()
                pygame.mouse.set_visible(True)
        elif event.type == pygame.MOUSEMOTION:
            pass

    def on_loop(self):
        # check difference between current time and starting time
        # determine probability based on time played
        # check if something happens (agent, generator, prison ...)
        Target.group.update(pygame.mouse.get_pos())
        Guerrilla.group.update(Army.group, Generator.group, Prison.group)

        if self.generator_action >= Generator.WAVE:
            Generator.group.update(Army.group, Guerrilla.group)
            self.generator_action = 0
        if self.army_action >= Army.STEP:
            Army.group.update()
            self.army_action = 0

        self.generator_action += 16
        self.army_action += 16

    def on_render(self):
        # blank screen for new drawing
        self.display.blit(self.poland, (0, 0))
        #self.display.fill((255, 255, 255))
        # render each sprite
        Boundary.group.draw(self.display)
        Army.group.draw(self.display)
        Prison.group.draw(self.display)
        Generator.group.draw(self.display)
        Guerrilla.group.draw(self.display)
        Target.group.draw(self.display)

        # blit virtual screen to actual display
        self.screen.blit(self.display, (0, 0))
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_run(self):
        # load map
        self.poland = pygame.image.load("assets/sprites/poland.png")
        # load coordinates of boundary tiles and create them as sprites
        Boundary.set_boundary("assets/boundary.txt")

        # record time that game starts
        # initialize all the sprites
        self.generator_action = 0
        self.army_action = 0

        Army.group.add(Army(50, 25, 90))
        Army.group.add(Army(51, 25, 90))
        Army.group.add(Army(50, 26, 90))
        Army.group.add(Army(51, 26, 90))
        Generator.group.add(Generator(750, 350, 30))
        Guerrilla.group.add(Guerrilla(100, 50))
        Prison.group.add(Prison(170,170))

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(60)

        self.on_cleanup()

class Army(pygame.sprite.Sprite):
    group = pygame.sprite.Group()  #??
    instances = {}
    CUTOFF = 30  # lowest transparency
    SPREADRATE = 20 
    STEP = 250 # milliseconds
    DIM = 16

    def __init__(self, x, y, communism):
        """Communism must start between 30 and 90."""
        super().__init__()

        self.x, self.y = x, y
        self.communism = communism

        self.image = pygame.Surface([Army.DIM, Army.DIM])
        self.image.fill((218, 10, 10))

        # alpha range: 30-90% 
        if self.communism < 30:
            self.image.set_alpha(0.3 * 255)
        elif self.communism > 90:
            self.image.set_alpha(0.9 * 255)
        else:
            self.image.set_alpha((self.communism / 100) * 255)

        # Fetch rectangle object with dimensions of image
        # Update object position by setting rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.topleft = [x * Army.DIM, y * Army.DIM]

        Army.instances[f'{self.x},{self.y}'] = self
        #Army.group.add(self)

    def destroy(self):
        Army.group.remove(self)
        del Army.instances[f'{self.x},{self.y}']

    def update(self):
        super().update()
        # Check communism level
        if self.communism <= 0:
            self.destroy()
        else:
            # determine communism available to spread
            self.spread = self.communism - self.CUTOFF
            if self.spread > Army.SPREADRATE:
                self.spread = Army.SPREADRATE
            if self.spread > 0:
                # check neighbors
                self.keys = [f'{self.x},{self.y + 1}',
                             f'{self.x},{self.y - 1}',
                             f'{self.x + 1},{self.y}',
                             f'{self.x - 1},{self.y}',
                             f'{self.x - 1},{self.y + 1}',
                             f'{self.x - 1},{self.y - 1}',
                             f'{self.x + 1},{self.y + 1}',
                             f'{self.x + 1},{self.y - 1}']
                
                # delete invalid objects
                for key in self.keys:
                    if key in Army.instances and Army.instances[key].communism >= self.communism:
                        self.keys.remove(key)
                    # also remove cubes that would be on a boundary
                    elif key in Boundary.instances:
                        self.keys.remove(key)

                # spread communism to valid objects
                # can only spread to things with communism less than self
                for key in self.keys:
                    if key not in Army.instances:
                        # decompose key
                        self.xs, self.ys = key.split(',')
                        # instantiate
                        Army.group.add(Army(int(self.xs), int(self.ys), int(self.spread/len(self.keys))))
                        # remove some communism from self
                        self.communism -= int(self.spread/len(self.keys))
                        # donate communism
                    else:
                        Army.instances[key].communism += int(self.spread/len(self.keys))
                        # remove some communism from self
                        self.communism -= int(self.spread/len(self.keys))

        # Update alpha value to represent communism level
        if self.communism < 30:
            self.image.set_alpha(0.3 * 255)
        elif self.communism > 90:
            self.image.set_alpha(0.9 * 255)
        else:
            self.image.set_alpha((self.communism / 100) * 255)
        
class Agent(pygame.sprite.Sprite):
    group = pygame.sprite.Group()  #??
    MAX_SPEED = 2
    DETECTION_RADIUS = 5
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([32, 32])
        self.image.fill ((256, 165, 0))

        self.x, self.y = x, y
        self.vel_x, self.vel_y = 0, 0
        self.target = self.x, self.y

        # Fetch rectangle object with dimensions of image
        # Update object position by setting rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

    def update(self, guerrilla_group):
        super().update()

        # check for collisions with guerillas and destroy them
        self.guerrilla_collisions = pygame.sprite.spritecollide(self, guerrilla_group, True)

        # find closest target
        #for guerrilla in guerrilla_group):
        
        
class Target(pygame.sprite.Sprite):
    group = pygame.sprite.GroupSingle()

    def __init__(self, mouse_pos):
        super().__init__()

        self.image = pygame.Surface([Guerrilla.DIM, Guerrilla.DIM])
        self.image.fill ((0, 255, 0))
        self.image.set_alpha(0.6 * 255)

        self.x, self.y = mouse_pos
        
        self.rect = self.image.get_rect()
        self.rect.center = list(mouse_pos)

    def destroy(self):
        Target.group.remove(Target.group.sprite)

    def update(self, mouse_pos):
        super().update()

        self.rect = self.rect.move(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        self.x, self.y = mouse_pos

class Guerrilla(pygame.sprite.Sprite):
    group = pygame.sprite.Group()
    MAX_SPEED = 2
    ATTACK_RADIUS = 1.5
    ATTACK_STRENGTH = 1 
    TOLERANCE = MAX_SPEED * 0.25
    DIM = 32

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([Guerrilla.DIM, Guerrilla.DIM])
        self.image.fill ((0, 255, 0))

        self.x, self.y = x, y
        self.vel_x, self.vel_y = 0, 0
        self.target = self.x, self.y

        # Fetch rectangle object with dimensions of image
        # Update object position by setting rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

#        Guerrilla.group.add(self)

    def destroy(self):
        Guerrilla.group.remove(self)

    def update(self, army_group, generator_group, prison_group):
        super().update()

        # check for direct intersections with army objects
        self.army_collisions = pygame.sprite.spritecollide(self, army_group, False)
        # delete guerrilla object
        if len(self.army_collisions) > 0:
            self.destroy()

        # check for collisions with generators
        self.generator_collisions = pygame.sprite.spritecollide(self, generator_group, True)

        # check for collisions with prisons
        self.prison_collisions = pygame.sprite.spritecollide(self, prison_group, False)
        # add soldiers
        for prison in self.prison_collisions:
            Guerrilla.group.add(Guerrilla(prison.x, prison.y))
            # delete prison
            prison_group.remove(prison)

        # moving
        if abs(self.target[0] - self.x) > Guerrilla.TOLERANCE and abs(self.target[1] - self.y) > Guerrilla.TOLERANCE:
            # calculate velocity vector
            self.xs = self.target[0] - self.x
            self.ys = self.target[1] - self.y
            self.norm = math.sqrt((self.xs**2 + self.ys**2))
            self.unit = self.xs/self.norm, self.ys/self.norm

            # create pixel scaled velocity
            self.vel_x = int(self.unit[0] * Guerrilla.MAX_SPEED)
            self.vel_y = int(self.unit[1] * Guerrilla.MAX_SPEED)

            # check move for collisions
            self.rect = self.rect.move(self.vel_x, self.vel_y)
            self.army_collisions = pygame.sprite.spritecollide(self, army_group, False)

            # if there are collisions, do not move
            if len(self.army_collisions) > 0:
                self.rect = self.rect.move(-self.vel_x, -self.vel_y)
            else:
                self.x += self.vel_x
                self.y += self.vel_y

        # attacking
        self.army_collisions = pygame.sprite.spritecollide(self, army_group, False, pygame.sprite.collide_circle_ratio(Guerrilla.ATTACK_RADIUS)) #??
        if len(self.army_collisions) > 0:
            self.closest = [0, math.sqrt(((self.army_collisions[0].x * Army.DIM)**2)+((self.army_collisions[0].y * Army.DIM)**2))]
            for i, army in enumerate(self.army_collisions):
                # identify closest army unit
                distance = math.sqrt(((self.army_collisions[i].x * Army.DIM)**2)+((self.army_collisions[i].y * Army.DIM)**2))
                if distance > self.closest[1]:
                    self.closest = [i, distance]

            closest_army = self.army_collisions[self.closest[0]]
            closest_army.communism -= Guerrilla.ATTACK_STRENGTH
            # if we lowered health to 0 or below, delete this instance of army
            if closest_army.communism <= 0:
                del Army.instances[f'{closest_army.x},{closest_army.y}']
                Army.group.remove(closest_army)
            

class Generator(pygame.sprite.Sprite):
    group = pygame.sprite.Group()  #??
    TRIGGER = 4 # number of guerrillas to trigger soviets
    DETECTION = 200 # detection radius for soviet reinforcements
    WAVE = 2000 # milliseconds
    RATIO = 1.5

    def __init__(self, x, y, rate):
        super().__init__()

        self.x, self.y = x, y
        self.BASE_RATE = rate
        self.rate = self.BASE_RATE 
        self.image = pygame.Surface([32, 32])
        self.image.fill ((0, 0, 0))

        # Fetch rectangle object with dimensions of image
        # Update object position by setting rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]


    def update(self, army_group, guerrilla_group):
        super().update()

        # identify army objects within radius
        self.army_collisions = pygame.sprite.spritecollide(self, army_group, False, pygame.sprite.collide_circle_ratio(Generator.RATIO)) #??
        # increase communism values
        for army in self.army_collisions:
            army.communism += self.rate

        self.rate = self.BASE_RATE
        # check if guerrillas within radius
        self.guerrilla_collisions = pygame.sprite.spritecollide(self, guerrilla_group, False, pygame.sprite.collide_circle_ratio(Generator.DETECTION))
        if len(self.guerrilla_collisions) >= Generator.TRIGGER:
            for guerrilla in self.guerrilla_collisions:
                self.ally_collisions = pygame.sprite.spritecollide(self, guerrilla_group, False, pygame.sprite.collide_circle_ratio(Generator.DETECTION/2))
                if len(self.ally_collision) >= Generator.TRIGGER:
                    # send soviet reinforcements
                    self.rate *= 5
            
class Prison(pygame.sprite.Sprite):
    group = pygame.sprite.Group()

    def __init__(self, x, y):
        super().__init__()
        self.x, self.y = x, y
        self.image = pygame.Surface([32, 32])

        self.image.fill ((0, 0, 255))

        # Fetch rectangle object with dimensions of image
        # Update object position by setting rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class Boundary(pygame.sprite.Sprite):
    group = pygame.sprite.Group()
    instances = []
    
    def __init__(self, x, y):
        super().__init__()

        # debug version
        self.image = pygame.Surface([16, 16])
        self.image.fill ((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]

        #self.rect = pygame.Rect(x, y, 16, 16)
    @staticmethod
    def set_boundary(filename):
        with open(filename) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                Boundary.group.add(Boundary(int(row[0]), int(row[1])))
                Boundary.instances.append(f"{int(int(row[0])/16)},{int(int(row[1])/16)}")

if __name__ == "__main__":
    game = App()
    game.on_run()


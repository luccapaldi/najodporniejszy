#!/usr/bin/env python3

import pygame
import math

class App:
    def __init__(self):
        pygame.init()
        self.running = True

        self.size = self.width, self.height = 480, 270

        # actual display
        self.screen = pygame.display.set_mode(self.size)
        # surface everything is blitted to
        self.display = pygame.Surface((480, 270))

        self.clock = pygame.time.Clock()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def on_loop(self):
        # check difference between current time and starting time
        # determine probability based on time played
        # check if something happens (agent, generator, prison ...)
        pass

    def on_render(self):
        self.display.fill((255, 255, 255))
        # blit virtual screen to actual display
        self.screen.blit(self.display, (0, 0))
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_run(self):
        # record time that game starts
        # initialize all the sprites

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(60)

        self.on_cleanup()

class Army(pygame.sprite.Sprite):
    self.army_group = pygame.sprite.group()  #??
    self.instances = {}
    self.CUTOFF = 30  # lowest transparency
    self.SPREADRATE = 10 

    def __init__(self, x, y, communism):
        super().__init__()

        self.x, self.y = x, y
        self.dim = 16
        self.communism = communism

        self.image = pygame.Surface([self.dim, self.dim])
        self.image.fill((218, 10, 10))

        # alpha range: 30-90% 
        self.image.set_alpha((self.communism + 30) * 2.55)
        Army.instances[f'{self.x},{self.y}'] = self
        Army.army_group.add(self)

    def destroy(self):
        Army.army_group.remove(self)
        del Army.instances[f'{self.x},{self.y}']

    def update(self):
        super().update()
        # Check communism level
        if self.communism < self.CUTOFF:
            self.destroy()
             
        else:
            # determine communism available to spread
            self.spread = self.communism - self.CUTOFF
            if spread > Army.SPREADRATE:
                self.spread = Army.SPREADRATE
            
            # check neighbors
            self.keys = [f'{self.x},{self.y + self.dim}',
                    f'{self.x},{self.y - self.dim}',
                    f'{self.x + self.dim},{self.y}',
                    f'{self.x - self.dim},{self.y}',
                    f'{self.x - self.dim},{self.y + self.dim}',
                    f'{self.x - self.dim},{self.y - self.dim}',
                    f'{self.x + self.dim},{self.y + self.dim}',
                    f'{self.x + self.dim},{self.y - self.dim}']
            
            # delete invalid objects
            for key in self.keys:
                if key in Army.instances and Army.instances[key].communism >= self.communism:
                    self.keys.remove(key)

            # spread communism to valid objects
            # can only spread to things with communism less than self
            for key in self.keys:
                if key not in Army.instances:
                    # decompose key
                    self.xs, self.ys = key.split(',')
                    # instantiate
                    Army.army_group.add(int(self.xs), int(self.ys), int(self.spread/len(self.keys)))
                # donate communism
                else:
                    Army.instances[key].communism += int(self.spread/len(self.keys))
        
class Agent(pygame.sprite.Sprite):
    pass

class Guerrilla(pygame.sprite.Sprite):
    self.guerrilla_group = pygame.sprite.group()  #??
    self.MAX_SPEED = 20
    self.ATTACK_RADIUS = 4
    self.ATTACK_STRENGTH = 1 

    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([32, 32])
        self.image.fill ((0, 255, 0))

        self.x, self.y = x, y
        self.vel_x, self.vel_y = 0, 0
        self.target = self.x, self.y

        Guerrilla.guerrilla_group.add(self)

    def destroy(self):
        Army.army_group.remove(self)

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
            Guerrilla.guerrilla_group.add(Guerrilla(prison.x, prison.y))
            # delete prison
            self.prison_collisions.remove(prison)

        # moving
        if self.target != self.x, self.y:
            # calculate velocity vector
            self.xs = self.target[0] - self.x
            self.ys = self.target[1] - self.y
            self.norm = math.sqrt((xs**2 + ys**2))
            self.unit = self.xs/self.norm, self.ys/self.norm

            # create pixel scaled velocity
            self.vel_x = int(self.unit[0] * Guerrilla.MAX_SPEED)
            self.vel_y = int(self.unit[1] * Guerrilla.MAX_SPEED)

            # store old position
            self.old_x, self.old_y = self.x, self.y

            # check move for collisions
            self.x += self.vel_x
            self.y += self.vel_y
            self.army_collisions = pygame.sprite.spritecollide(self, army_group, False)

            # if there are collisions, do not move
            if len(self.army_collisions) > 0:
                self.x = self.old_x
                self.y = self.old_y

        # attacking
        self.army_collisions = pygame.sprite.spritecollide(self, army_group, False, collided=collide_circle_ratio(Guerrilla.ATTACK_RADIUS)) #??
        for army in self.army_collisions:
            army.communism -= Guerrilla.ATTACK_STRENGTH

class Generator(pygame.sprite.Sprite):
    self.TRIGGER = 4 # number of guerrillas to trigger soviets
    self.DETECTION = 200 # detection radius for soviet reinforcements

    def __init__(self, x, y, rate):
        super().__init__()

        self.x, self.y = x, y
        self.BASE_RATE = rate
        self.rate = self.BASE_RATE 
        self.ratio = 1.0
        self.image = pygame.Surface([32, 32])
        self.image.fill ((0, 0, 0))

    def update(self, army_group, guerrilla_group):
        super().update()

        # identify army objects within radius
        self.army_collisions = pygame.sprite.spritecollide(self, army_group, False, collided=collide_circle_ratio(self.ratio)) #??
        # increase communism values
        for army in self.army_collisions:
            army.communism += self.rate

        self.rate = self.BASE_RATE
        # check if guerrillas within radius
        self.guerrilla_collisions = pygame.sprite.spritecollide(self, guerrilla_group, False, collided=collide_circle_ratio(Generator.DETECTION))
        if len(guerrilla_collisions) >= Generator.TRIGGER:
            for guerrilla in guerrilla_collisions:
                self.ally_collisions = pygame.sprite.spritecollide(self, guerrilla_group, False, collided=collide_circle_ratio(Generator.DETECTION/2))
                if len(self.ally_collision) >= Generator.TRIGGER:
                    # send soviet reinforcements
                    self.rate *= 5
            
class Prison(pygame.sprite.Sprite):
    def __init__(self, x, y, inmates):
        super().__init__()
        self.x, self.y = x, y
        self.image = pygame.Surface([32, 32])

        self.image.fill ((0, 0, 255))

        self.inmates = inmates

    def update(self):
        super().update()
        # release soldiers

if __name__ == "__main__":
    game = App()
    game.on_run()


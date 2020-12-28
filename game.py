#!/usr/bin/env python3

import pygame

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
    def __init__(self, x, y, communism):
        super().__init__()

        self.x, self.y = x, y

        self.image = pygame.Surface([16,16])
        self.image.fill((218, 10, 10))
        self.image.set_alpha(communism)

    def update(self):
        super().update()
        # spreading
        # check communism level
        # if above cutoff, spread
        # check neighboring Army instances
        # exclude any with max communism
        # divide communism spread value + excess above 100%
        # if all neighbors have max communism, spread excess evenly
        # if less than 8 neighbors, then create army unit to occupy unoccupied spaces given it has enough communism to do so

        
class Agent(pygame.sprite.Sprite):
    pass

class Guerrilla(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.x, self.y = x, y

        self.image = pygame.Surface([32, 32])
        self.image.fill ((0, 255, 0))
        self.vel_x, self.vel_y = 0, 0
        self.target = self.x, self.y

    def update(self):
        super().update()
        #self.vel_x = self.target[0] - self.x
        self.x += self.vel_x
        self.y += self.vel_y
        # check intersections
        # if intersecting with army, dead
        # if intersecting with prison, destroy prison sprite and release soldier
        # if intersecting with other guerillam, don't
        # check how many guerillas are close becuase if above limit, spawn soviet reinforcements

class Structure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.x, self.y = x, y

        self.image = pygame.Surface([32, 32])

    def update(self):
        super().update()

class Generator(Structure):
    def __init__(self, x, y):
        super().__init__()

        self.image.fill ((0, 0, 0))

    def update(self, army_list):
        super().update()
        # iterate through list of army elements and calculate distance from each element to the Generator structure to determine all units within a certain radius of generator
        # increase communism for each element of the army within that radius

class Prison(Structure):
    def __init__(self, x, y, inmates):
        super().__init__()

        self.image.fill ((0, 0, 255))

        self.inmates = inmates

    def update(self):
        super().update()
        # release soldiers

if __name__ == "__main__":
    game = App()
    game.on_run()

    

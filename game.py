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
        pass

    def on_render(self):
        self.display.fill((255, 255, 255))
        # blit virtual screen to actual display
        self.screen.blit(self.display, (0, 0))
        pygame.display.update()

    def on_cleanup(self):
        pygame.quit()

    def on_run(self):
        # initialize all the sprites

        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(60)

        self.on_cleanup()


if __name__ == "__main__":
    game = App()
    game.on_run()

    

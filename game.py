from faulthandler import is_enabled
import pygame as pg
from pygame.locals import *
import pygame_menu
from column import Column
from score import Score
import random
# from menu import pauseMenu

class pauseMenu(pygame_menu.Menu):
    
    def __init__(self, width, height):
        super().__init__('Pause', width, height)

        self.back = False
        self.add.button('Resume', action=self.disable)
        self.add.button('Back to main menu', action=self.set_back)
    
    def set_back(self):
        self.back = True
    

class Game:

    def __init__(self, gameConfig, lvlConfig):
        self.screen = pg.display.get_surface()
        self.gameConfig = gameConfig
        self.lvlConfig = lvlConfig

        # Variables
        self.speed = gameConfig.speed
        self.active = gameConfig.default_active

        self.columns = []
        self.col_group = pg.sprite.Group()
        self.input_group = pg.sprite.Group()
        self.score = pg.sprite.GroupSingle(Score(
            1, self.gameConfig.font, self.gameConfig.score_rect
        ))

        self.__setGraphics()
    
    def __setGraphics(self):
        for i in range(self.lvlConfig.columns):
            col_rect = pg.Rect(
                self.gameConfig.board_left + i * self.gameConfig.col_width,
                self.gameConfig.board_top,
                self.gameConfig.col_width,
                self.gameConfig.col_height)

            col = Column(
                self.gameConfig,
                self.lvlConfig,
                col_rect,
                self.col_group,
                self.input_group)
            self.columns.append(col)

    def pause(self):
        pause = pauseMenu(self.screen.get_width(), self.screen.get_height())
        pause.mainloop(self.screen)

    def render(self):
        self.screen.fill((0, 0, 0))
        for col in self.columns:
            col.image.fill((0, 0, 0), col.inside)
            col.render_equations()
            col.update(self.speed / self.gameConfig.fps)
        self.col_group.draw(self.screen)
        self.input_group.draw(self.screen)
        self.score.draw(self.screen)
    
    # Running the game
    def run(self):
       
        self.columns[self.active].activate()
        clock = pg.time.Clock()

        GENERATE = USEREVENT + 1 # Generate new equation event
        pg.time.set_timer(GENERATE, self.lvlConfig.gen_frequency)

        SPEEDUP = USEREVENT + 2  # Increase the game speed
        pg.time.set_timer(SPEEDUP, self.lvlConfig.inc_frequency)

        pause = pauseMenu(self.screen.get_width(), self.screen.get_height())
        pause.disable()
        while 1:
            if pause.back:
                return
            events = pg.event.get()
            for event in events:
                if event.type == QUIT:
                    return
                elif event.type == GENERATE:
                    # Generate new equation for a random column
                    # (even generation)
                    self.columns[random.randrange(0, self.lvlConfig.columns)].generate_eq()
                elif event.type == SPEEDUP:
                    self.speed *= self.config.increment
                elif event.type == KEYDOWN:

                    k = event.key
                    # Change active column to one to the left
                    if k == K_LEFT:
                        self.columns[self.active].deactivate()
                        self.active = (self.active - 1) % self.lvlConfig.columns
                        self.columns[self.active].activate()
                    
                    # Change active column to one to the right
                    elif k == K_RIGHT:
                        self.columns[self.active].deactivate()
                        self.active = (self.active + 1) % self.lvlConfig.columns
                        self.columns[self.active].activate()

                    # Get input into the active column's input field
                    elif k in [K_BACKSPACE, K_MINUS] or k in range(K_0, K_9 + 1):
                        self.columns[self.active].get_input(event.key)
                    
                    # Check the input entered into the active field
                    # And update the score
                    elif k == K_RETURN:
                        self.columns[self.active].check(self.speed, self.score)

                    elif k == K_ESCAPE:
                        pause.enable()

            if pause.is_enabled():
                pause.draw(self.screen)
                pause.update(events)
            else:
                self.render()

            clock.tick(self.gameConfig.fps)
            pg.display.flip()

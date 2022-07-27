import pygame as pg
from pygame.locals import *
from column import Column
from score import Score
from menu import pauseMenu, gameoverMenu
import random

# The main game class
class Game:

    def __init__(self, gameConfig, lvlConfig):
        self.screen = pg.display.get_surface()
        self.gameConfig = gameConfig
        self.lvlConfig = lvlConfig

        # Variables
        self.speed = gameConfig.speed
        self.active = gameConfig.default_active

        # Columns
        self.col_group = pg.sprite.Group()
        self.input_group = pg.sprite.Group()

        # The score
        self.score = pg.sprite.GroupSingle(Score(
            lvlConfig.lvl, lvlConfig.columns, self.gameConfig.font, self.gameConfig.score_rect
        ))

        self.__setGraphics()
    
    # Set columns to their correct positions
    def __setGraphics(self):
        self.columns_rect = pg.Rect(
            self.gameConfig.board_left,
            self.gameConfig.board_top,
            self.gameConfig.col_width * self.lvlConfig.columns,
            self.gameConfig.col_height + self.gameConfig.input_height
        )
        for i in range(self.lvlConfig.columns):
            col_rect = pg.Rect(
                self.gameConfig.board_left + i * self.gameConfig.col_width,
                self.gameConfig.board_top,
                self.gameConfig.col_width,
                self.gameConfig.col_height)
            col = Column(
                i,
                self.gameConfig,
                self.lvlConfig,
                col_rect,
                self.col_group,
                self.input_group)
    
    def reset(self, active_col):
        self.score.sprite.reset()
        for col in self.col_group.sprites():
            col.reset()
        self.speed = self.gameConfig.speed
        active_col.deactivate()
        active_col = self.col_group.sprites()[self.gameConfig.default_active]
        active_col.activate()

    # Running the game
    def run(self):
       
        clock = pg.time.Clock()
        # self.columns[self.active].activate()
        active_col = self.col_group.sprites()[self.gameConfig.default_active]
        active_col.activate()

        GENERATE = USEREVENT + 1 # Generate new equation event
        pg.time.set_timer(GENERATE, self.lvlConfig.gen_frequency)

        SPEEDUP = USEREVENT + 2  # Increase the game speed event
        pg.time.set_timer(SPEEDUP, self.lvlConfig.inc_frequency)

        # Create menus
        pauseM = pauseMenu(self.screen.get_width(), self.screen.get_height())
        pauseM.disable()

        gameoverM = gameoverMenu(self.columns_rect.width, self.columns_rect.height)
        gameoverM.set_absolute_position(self.columns_rect.left, self.columns_rect.top)
        gameoverM.disable()

        paused = False # Paused iff either pause or gameover menu is active

        self.screen.fill((0, 0, 0))
        pg.display.flip()
        while 1:
            events = pg.event.get()
            for event in events:
                if event.type == QUIT:
                    return

                # Check game-related events iff not paused
                if not paused:

                    if event.type == GENERATE:
                        # Generate new equation for a random column
                        self.col_group.sprites()[random.randrange(0, self.lvlConfig.columns)].generate_eq()
                    
                    elif event.type == SPEEDUP:
                        self.speed *= self.gameConfig.increment
                    
                    elif event.type == KEYDOWN:

                        k = event.key
                        # Change active column to one to the left or the right
                        if k in [K_LEFT, K_RIGHT]:
                            active_col.deactivate()
                            if k == K_LEFT:
                                new_active = active_col.index - 1
                            else:
                                new_active = active_col.index + 1
                            new_active %= self.lvlConfig.columns
                            active_col = self.col_group.sprites()[new_active]
                            active_col.activate() 

                        # Get input into the active column's input field
                        elif k in [K_BACKSPACE, K_MINUS] or k in range(K_0, K_9 + 1):
                            active_col.get_input(event.key)
                        
                        # Check the input entered into the active field
                        # And update the score
                        elif k == K_RETURN:
                            active_col.check(self.speed, self.score)

                        # Pause the game
                        elif k == K_ESCAPE:
                            paused = True
                            pauseM.enable()

            # Display pause menu
            if pauseM.is_enabled():
                pauseM.draw(self.screen)
                pauseM.update(events)
                pg.display.flip()

                if pauseM.back_to_menu:
                    pauseM.disable()
                    return
            
            # Display gameover menu
            elif gameoverM.is_enabled():
                gameoverM.draw(self.screen)
                gameoverM.update(events)
                pg.display.flip()

                if gameoverM.back_to_menu:
                    gameoverM.disable()
                    return
                elif gameoverM.restart:
                    gameoverM.restart = False
                    self.reset(active_col)
                    gameoverM.disable()
            
            # Else display and update the game
            else:
                self.screen.fill((0, 0, 0))

                # Check for gameover when updating columns
                # (whether an equation hits the bottom)
                paused = False
                for col in self.col_group.sprites():
                    gameover = col.update(self.speed / self.gameConfig.fps)
                    if gameover:
                        paused = True
                        gameoverM.enable()
                        break
                self.col_group.draw(self.screen)
                self.input_group.draw(self.screen)
                self.score.draw(self.screen)

                pg.display.flip()

            clock.tick(self.gameConfig.fps)

    

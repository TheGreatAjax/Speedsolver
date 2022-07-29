import pygame as pg
from pygame.locals import *
from column import Column
from score import Score
from menu import menuEnum, pauseMenu, gameoverMenu
import random

# The main game class
class Game:

    def __init__(self, gameConfig, lvlConfig):

        # Save the config
        self.screen = pg.display.get_surface()
        self.gameConfig = gameConfig
        self.lvlConfig = lvlConfig

        # Variables
        self.game_speed = gameConfig.speed
        self.generation_frequency = lvlConfig.gen_frequency
        self.active = gameConfig.default_active

        # Columns
        self.col_group = pg.sprite.Group()
        self.input_group = pg.sprite.Group()

        # The score
        self.score = pg.sprite.GroupSingle(Score(
            lvlConfig.lvl,
            lvlConfig.columns,
            pg.font.Font(self.gameConfig.font_path, 30),
            self.gameConfig.score_rect
        ))

        # Events
        self.GENERATE = USEREVENT + 1 # Generate new equation event
        self.SPEEDUP = USEREVENT + 2  # Increase the game speed event

        self.paused = False

        self.__setGraphics()
    
    # Create and set columns to their correct positions
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
            self.col_group.add(Column(
                i,
                self.gameConfig,
                self.lvlConfig,
                col_rect,
                self.input_group))
        self.columns = self.col_group.sprites() # Alias
        self.active_col = self.columns[self.gameConfig.default_active]
    
    def reset(self):
        self.score.sprite.reset()
        for col in self.columns:
            col.reset()
        self.game_speed = self.gameConfig.speed
        self.generation_frequency = self.lvlConfig.gen_frequency

        self.active_col.deactivate()
        self.active_col = self.columns[self.gameConfig.default_active]
        self.active_col.activate()

        pg.time.set_timer(self.GENERATE, self.generation_frequency)
        pg.time.set_timer(self.SPEEDUP, self.lvlConfig.inc_frequency)

        pg.event.clear()

        self.paused = False

    def run(self):
       
        clock = pg.time.Clock()
        self.active_col = self.columns[self.gameConfig.default_active]
        self.active_col.activate()

        pg.time.set_timer(self.GENERATE, self.lvlConfig.gen_frequency)
        pg.time.set_timer(self.SPEEDUP, self.lvlConfig.inc_frequency)

        # Create menus
        pauseM = pauseMenu(self.screen.get_width(), self.screen.get_height())
        pauseM.disable()

        gameoverM = gameoverMenu(self.columns_rect.width, self.columns_rect.height)
        gameoverM.set_absolute_position(self.columns_rect.left, self.columns_rect.top)
        gameoverM.disable()

        self.paused = False # paused iff either pause or gameover menu is active

        self.screen.fill((0, 0, 0))
        pg.display.flip()
        while 1:
            events = pg.event.get()
            for event in events:
                if event.type == QUIT:
                    return

                # Check game-related events iff not self.paused
                if not self.paused:

                    if event.type == self.GENERATE:
                        # Generate new equation for a random column
                        self.columns[random.randrange(0, self.lvlConfig.columns)].generate_eq()
                    
                    elif event.type == self.SPEEDUP:
                        self.game_speed *= self.gameConfig.increment
                        self.generation_frequency = self.generation_frequency // self.gameConfig.increment
                        pg.time.set_timer(self.GENERATE, int(self.generation_frequency))

                    elif event.type == KEYDOWN:

                        k = event.key
                        # Change active column to one to the left or the right
                        if k in [K_LEFT, K_RIGHT]:
                            self.active_col.deactivate()
                            if k == K_LEFT:
                                new_active = self.active_col.index - 1
                            else:
                                new_active = self.active_col.index + 1
                            new_active %= self.lvlConfig.columns
                            self.active_col = self.columns[new_active]
                            self.active_col.activate() 

                        # Get input into the active column's input field
                        elif k in [K_BACKSPACE, K_MINUS] or k in range(K_0, K_9 + 1):
                            self.active_col.get_input(event.key)
                        
                        # Check the input entered into the active field
                        # And update the score
                        elif k == K_RETURN:
                            self.active_col.check(self.game_speed, self.score)

                        # Pause the game
                        elif k == K_ESCAPE:
                            self.paused = True
                            pauseM.enable()

            # Display pause menu
            if pauseM.is_enabled():
                pauseM.draw(self.screen)
                pauseM.update(events)
                pg.display.flip()

                if pauseM.state == menuEnum.BACK_TO_MENU:
                    pauseM.disable()
                    return
                elif pauseM.state == menuEnum.RESUME:
                    pauseM.state = menuEnum.OPEN
                    pauseM.disable()
                    self.screen.fill((0, 0, 0))
                    pg.display.flip()
            
            # Display gameover menu
            elif gameoverM.is_enabled():
                gameoverM.draw(self.screen)
                gameoverM.update(events)
                pg.display.flip()

                if gameoverM.state == menuEnum.BACK_TO_MENU:
                    gameoverM.disable()
                    return
                elif gameoverM.state == menuEnum.RESTART:
                    gameoverM.state = menuEnum.OPEN
                    gameoverM.disable()
                    self.reset()
                    self.screen.fill((0, 0, 0))
                    pg.display.flip()
            
            # Else display and update the game
            else:
                self.screen.fill((0, 0, 0))

                # Draw the game elements
                self.col_group.draw(self.screen)
                self.input_group.draw(self.screen)
                self.score.draw(self.screen)

                # Check for gameover when updating columns
                # (whether an equation hits the bottom)
                self.paused = False
                for col in self.columns:
                    gameover = col.update(self.game_speed / self.gameConfig.fps)
                    if gameover:
                        gameoverM.enable()
                        self.paused = True
                        break

                # Update only parts of the screen containing 
                # the game elements
                pg.display.update([self.columns_rect, self.gameConfig.score_rect])

            clock.tick(self.gameConfig.fps)

    

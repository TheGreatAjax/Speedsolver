import pygame as pg
from pygame.locals import *
import pygame_menu
from column import Column
from score import Score
import random

class pauseMenu(pygame_menu.Menu):
    
    def __init__(self, width, height):
        super().__init__('Pause', width, height,
             theme=pygame_menu.themes.THEME_DARK)
        self.back_to_menu = False
        self.add.button('Resume', action=self.quit)
        self.add.button('Back to Main', action=self.set_back)
    
    def quit(self):
        self.disable()
        pg.event.set_allowed(None)
    def set_back(self):
        self.back_to_menu = True
    
class gameoverMenu(pygame_menu.Menu):

    def __init__(self, width, height):
        mytheme = pygame_menu.themes.THEME_SOLARIZED.copy()
        mytheme.background_color = (0, 0, 0, 0)
        mytheme.title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE
        super().__init__('GAME OVER!', width, height, theme=mytheme)

        self.restart = False
        self.back_to_menu = False
        self.add.button('Restart', action=self.set_restart)
        self.add.button('Back to Main', action=self.set_back)
        self.add.button('Quit', action=pygame_menu.events.EXIT)
    
    def set_restart(self):
        self.restart = True
    def set_back(self):
        self.back_to_menu = True

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
            lvlConfig.lvl, self.gameConfig.font, self.gameConfig.score_rect
        ))

        self.__setGraphics()
    
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
                self.gameConfig,
                self.lvlConfig,
                col_rect,
                self.col_group,
                self.input_group)
            self.columns.append(col)  
    
    def reset(self):
        self.score.sprite.reset()
        for col in self.columns:
            col.reset()
        self.speed = self.gameConfig.speed
        self.columns[self.active].deactivate()
        self.active = self.gameConfig.default_active
        self.columns[self.active].activate()

    # Running the game
    def run(self):
       
        clock = pg.time.Clock()
        self.columns[self.active].activate()

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

                if not paused:
                    if event.type == GENERATE:
                        # Generate new equation for a random column
                        # (even generation)
                        self.columns[random.randrange(0, self.lvlConfig.columns)].generate_eq()
                    elif event.type == SPEEDUP:
                        self.speed *= self.gameConfig.increment
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

                        # Pause the game
                        elif k == K_ESCAPE:
                            paused = True
                            pauseM.enable()

            if pauseM.is_enabled():
                pauseM.draw(self.screen)
                pauseM.update(events)
                pg.display.flip()

                if pauseM.back_to_menu:
                    pauseM.disable()
                    return
            
            elif gameoverM.is_enabled():
                gameoverM.draw(self.screen)
                gameoverM.update(events)
                pg.display.flip()

                if gameoverM.back_to_menu:
                    gameoverM.disable()
                    return
                elif gameoverM.restart:
                    gameoverM.restart = False
                    self.reset()
                    gameoverM.disable()
            else:
                self.screen.fill((0, 0, 0))
                self.col_group.draw(self.screen)
                self.input_group.draw(self.screen)
                self.score.draw(self.screen)
                paused = False
                for col in self.columns:
                    gameover = col.update(self.speed / self.gameConfig.fps)
                    if gameover:
                        paused = True
                        gameoverM.enable()
                        break
                # pg.display.update([self.columns_rect, self.gameConfig.score_rect])
                pg.display.flip()

            clock.tick(self.gameConfig.fps)

    

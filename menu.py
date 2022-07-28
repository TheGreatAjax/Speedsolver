import pygame_menu
from enum import Enum

class menuEnum(Enum):
    OPEN = 0,
    BACK_TO_MENU = 1,
    RESUME = 2,
    RESTART = 3

class pauseMenu(pygame_menu.Menu):
    
    def __init__(self, width, height):
        super().__init__('Pause', width, height,
             theme=pygame_menu.themes.THEME_DARK)
        self.state = menuEnum.OPEN
        self.add.button('Resume', action=self.resume)
        self.add.button('Back to Main', action=self.set_back)
    
    def resume(self):
        self.state = menuEnum.RESUME
    def set_back(self):
        self.state = menuEnum.BACK_TO_MENU
    
class gameoverMenu(pygame_menu.Menu):

    def __init__(self, width, height):
        mytheme = pygame_menu.themes.THEME_SOLARIZED.copy()
        mytheme.background_color = (0, 0, 0, 0)
        mytheme.title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_NONE
        super().__init__('GAME OVER!', width, height, theme=mytheme)

        self.state = menuEnum.OPEN
        self.add.button('Restart', action=self.set_restart)
        self.add.button('Back to Main', action=self.set_back)
        self.add.button('Quit', action=pygame_menu.events.EXIT)
    
    def set_restart(self):
        self.state = menuEnum.RESTART
    def set_back(self):
        self.state = menuEnum.BACK_TO_MENU

class mainMenu(pygame_menu.Menu):

    def __init__(self, width, height, play_action):
        super().__init__('Speedsolver', width, height,
                     theme=pygame_menu.themes.THEME_DARK)
        self.play_action = play_action
        self.add.button('Play!', action=self.start)
        self.dif = self.add.selector('Difficulty: ', [
            ('Easy', 1),
            ('Medium', 2),
            ('Hard', 3)
        ])
        self.cols = self.add.selector('Tracks: ', [
            (str(i), i) for i in range(4, 7) 
        ])

        self.add.button('Exit', action=pygame_menu.events.EXIT)

    def start(self):
        dif = self.dif.get_value()[0][1]
        cols = self.cols.get_value()[0][1]
        self.play_action(dif, cols)


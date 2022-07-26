import pygame_menu

class pauseMenu(pygame_menu.Menu):
    
    def __init__(self, width, height):
        super().__init__('Pause', width, height,
             theme=pygame_menu.themes.THEME_DARK)
        self.back_to_menu = False # Whether 'Back to Main' button was pressed
        self.add.button('Resume', action=self.disable)
        self.add.button('Back to Main', action=self.set_back)
    
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
        self.add.button('Exit', action=pygame_menu.events.EXIT)

    def start(self):
        self.play_action(self.dif.get_value()[0][1])


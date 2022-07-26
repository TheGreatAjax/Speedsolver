import pygame
import pygame_menu
from game import Game
from config import load_config, load_level

class mainMenu(pygame_menu.Menu):

    def __init__(self, width, height):
        super().__init__('Speedsolver', width, height,
                     theme=pygame_menu.themes.THEME_DARK)
        self.lvl = 1
        self.add.button('Play!', action=self.start)
        self.add.selector('Difficulty: ', [
            ('Easy', 1),
            ('Medium', 2),
            ('Hard', 3)
        ], onchange=self.change_dif)
        self.add.button('Exit', action=pygame_menu.events.EXIT)
    
    def start(self):
        config = load_config()
        lvlConfig = load_level(self.lvl)
        game = Game(config, lvlConfig)
        game.run()
    
    def change_dif(self, selected_val, dif):
        self.lvl = dif



from game import Game
from config import staticConfig, levelConfig, load_config, load_level
import pygame as pg
import pygame_menu as pg_menu

class mainMenu(pg_menu.Menu):
    def __init__(self, title, width, height):
        super().__init__(title, width, height)
        self.lvl = 1
        self.config = load_config()
        self.add.button('Play!', self.start)
        self.add.selector('Difficulty: ', [
            ('Easy', 1),
            ('Medium', 2),
            ('Hard', 3)
        ], onchange=self.change_dif)
        self.add.button('Exit', action=pg_menu.events.EXIT)
    
    def start(self):
        lvlConfig = load_level(self.lvl)
        game = Game(self.config, lvlConfig)
        game.run()
    
    def change_dif(self, selected_val, dif):
        self.lvl = dif

def main():
    pg.init()

    # Create the main screen
    width, height = 1240, 800
    screen = pg.display.set_mode((width, height))
    main = mainMenu('Speedsolver', width, height)
    main.mainloop(screen)

if __name__ == '__main__':
    main()
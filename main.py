
from pygame import init, display
from menu import mainMenu
from game import Game
from config import load_config, load_level

def start(lvl, cols=4):
    config = load_config()
    lvlConfig = load_level(lvl, cols)
    game = Game(config, lvlConfig)
    game.run()

def main():
    init()

    # Create the main screen
    width, height = 1240, 800
    screen = display.set_mode((width, height))

    # Create and run the main menu
    main = mainMenu(width, height, play_action=start)
    main.mainloop(screen)

if __name__ == '__main__':
    main()
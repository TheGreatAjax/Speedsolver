
from email.policy import default
from game import Config, Game
import pygame as pg

def main():
    pg.init()

    # Create the main screen
    width, height = 1240, 800
    screen = pg.display.set_mode((width, height))

    config = Config(
        board_left = int(width * 0.1),
        board_top = 10,
        columns = 4,
        col_width = int(width * 0.2),
        col_height = int(height * 0.9),
        border_width = 1,
        highlighted_width = 3,
        input_height = int(height * 0.9 * 0.1),
        speed = 100,
        increment = 1,
        default_active=0,
        font=pg.font.Font(None, int(width * 0.2 * 0.3)),
        fps=60,
        gen_frequency=500
    )
    game = Game(config)
    game.run()

if __name__ == '__main__':
    main()
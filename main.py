
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
        board_top = -1,
        columns = 4,
        col_width = int(width * 0.1),
        col_height = int(height * 0.9),
        input_height = int(height * 0.9 * 0.1),
        border_width = 1,
        highlighted_width = 3,
        speed = 100,
        increment = 100 * 0.1,
        default_active=0,
        font=pg.font.Font(None, int(width * 0.2 * 0.2)),
        fps=60,
        gen_frequency=1000,
        inc_frequency=10000,
        score_rect=pg.Rect(
            int(width * 0.8),
            10,
            int(width * 0.2),
            300
        )
    )
    game = Game(config)
    game.run()

if __name__ == '__main__':
    main()
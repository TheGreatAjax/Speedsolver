import pygame as pg

class staticConfig:
    def __init__(self, *,
            board_left:     int,  # Position of the board
                                  # relative to the screen        
            board_top:      int,
            col_width:      int,  # Columns' dimensions
            col_height:     int,
            border_width:   int,  # Width of a column's border
            highlighted_width:int,# Width of a highlighed border 
            input_height:   int,  # Height of the input field
            speed:          int,  # Speed with which
                                  # equations are falling
                                  # Pixels per seconds
            increment:      int,  # Speed increment
            default_active: int,  # Index of the column
                                  # active by default
            font:           pg.font.Font,
            score_rect:     pg.Rect,# Score's positioning
            fps:            int,
    ):
                self.board_left = board_left
                self.board_top = board_top
                self.col_width = col_width
                self.col_height = col_height
                self.border_width = border_width
                self.highlighted_width = highlighted_width
                self.input_height = input_height
                self.speed = speed
                self.increment = increment
                self.default_active = default_active
                self.font = font
                self.score_rect = score_rect
                self.fps = fps

class levelConfig:
    def __init__(self, *,
            lvl:            int,
            columns:        int, # Number of columns
            gen_frequency:  int, # Frequency with which new
                                 # Equations get generated
                                 # Used in pg.clock.set_timer()
            inc_frequency:  int, # Frequency with which 
                                 # The speed gets increased
            operands_range: int, # Maximum number of operands for equation
            operands_max:   int, # Maximum value an equation can contain
            operations:      list # Operators in the equations 
        ):
        self.lvl = lvl
        self.columns = columns
        self.gen_frequency = gen_frequency
        self.inc_frequency = inc_frequency
        self.operands_range = operands_range
        self.operands_max = operands_max
        self.operations = operations

def load_config():
    width, height = pg.display.get_surface().get_size()
    gameConfig = staticConfig(
        board_left = int(width * 0.1),
        board_top = -1,
        col_width = int(width * 0.1),
        col_height = int(height * 0.9),
        input_height = int(height * 0.9 * 0.1),
        border_width = 1,
        highlighted_width = 3,
        default_active=0,
        speed = 500,
        increment = 1.1,
        font=pg.font.Font(None, int(width * 0.2 * 0.2)),
        fps=60,
        score_rect=pg.Rect(
            int(width * 0.8),
            10,
            int(width * 0.2),
            300
        )
    )
    return gameConfig

def load_level(lvl, cols=4):
    if lvl == 1:
        return levelConfig(
            lvl=1,
            columns=cols,
            gen_frequency=2000,
            inc_frequency=60000,
            operands_range=2,
            operands_max=9,
            operations=['+', '-', '*']
        )
    elif lvl == 2:
        pass
    else:
        pass
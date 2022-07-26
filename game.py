import pygame as pg
from pygame.locals import *
from score import Score
import random
from collections import deque

# Struct containing all game's variables
class Config:
    def __init__(self, *,
            board_left:     int,  # Position of the board
                                  # relative to the screen        
            board_top:      int,
            col_width:      int,  # Columns' dimensions
            col_height:     int,
            border_width:   int,  # Width of a column's border
            highlighted_width:int,# Width of a highlighed border 
            columns:        int,  # Number of columns
            input_height:   int,  # Height of the input field
            speed:          int,  # Speed with which
                                  # equations are falling
                                  # Pixels per seconds
            increment:      int,  # Speed increment
            default_active: int,  # Index of the column
                                  # active by default
            font:           pg.font.Font,# Font size for equations
            score_rect:     pg.Rect,
            fps:            int,
            gen_frequency,        # Frequency with which new
                                 # Equations get generated
                                 # Used in pg.clock.set_timer()
            inc_frequency        # Frequency with which 
                                 # The speed gets increased
                ):

                self.board_left = board_left
                self.board_top = board_top
                self.columns = columns
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
                self.get_frequency = gen_frequency
                self.inc_frequency = inc_frequency

# Equation which falls from the top of the screen
class Equation(pg.sprite.Sprite):

    operands = [str(i) for i in range(1, 10)] # Possible operands
    operations = ['+', '-', '*'] # Possible operators

    def __init__(self, col, ops, font, eq_group):
        super().__init__(eq_group)
        self.ops = ops # How many operands equation contains
        self.repr = random.choice(self.operands) # String representation of the equation
                                                 # operand-operation-operand-...
        for _ in range (1, ops):
            self.repr += random.choice(self.operations)
            self.repr += random.choice(self.operands)
        
        self.result = eval(self.repr) # Solution

        # Initing the text
        self.image = font.render(self.repr, 0, pg.Color('white')) # Which is text
        text_w = self.image.get_width()
        text_h = self.image.get_height()
        self.rect = pg.Rect(    # Place in the upper middle of its column
            col.rect.width // 2 - text_w // 2,
            col.rect.top,
            text_w,
            text_h
        )

class Column(pg.sprite.Sprite):
    def __init__(self,
                 rect: pg.Rect,
                 border_width,
                 highlighted_width,
                 input_height,
                 font,
                 col_group,
                 input_group):
        super().__init__(col_group)
        self.rect = rect
        self.border_width = border_width
        self.highlighted_width = highlighted_width
        self.input_height = input_height
        self.font = font

        # Draw the column
        self.image = pg.Surface(self.rect.size)
        pg.draw.rect(self.image, pg.Color('white'),
                    ((0, 0), self.rect.size), self.border_width)
        self.inside = pg.Rect(  # The column's rect without its borders
            self.border_width,
            self.border_width,
            self.rect.width - self.border_width*2,
            self.rect.height - self.border_width*2
        )
                
        # The input field
        self.input_field = pg.sprite.Sprite(input_group)
        self.input_field.image = pg.Surface((self.rect.width, input_height))

        # Move it to the bottom of the column
        self.input_field.rect = self.input_field.image.get_rect().move( 
            self.rect.left, self.rect.top + self.rect.height
        )
        pg.draw.rect(
            self.input_field.image,
            pg.Color('white'),
            ((0, 0), self.input_field.rect.size),
            self.border_width)

        self.input_repr = str() # Input text
        self.equations = deque() # The list of equations
        self.equation_group = pg.sprite.Group()
    
    def update(self, speed):
        for eq in self.equations:
            eq.rect.top += speed
    
    def render_equations(self):
        self.equation_group.draw(self.image)
    
    def generate_eq(self):
        new_eq = Equation(
            self,
            random.randint(2, 3), 
            self.font, 
            self.equation_group
        )

        # Generate only if it doesn't stack right
        # on top of the last equation in the column
        if (self.equations and
            new_eq.rect.top + new_eq.rect.height*2 >= self.equations[-1].rect.top):
            self.equation_group.remove(new_eq)
        else:
            self.equations.append(new_eq)

    # Get input from the input field
    def get_input(self, key):
        changed = False
        if key == K_BACKSPACE and self.input_repr != '':
            self.input_repr = self.input_repr[:-1]
            changed = True
        elif (key == K_MINUS and self.input_repr == ''
            or key in range(K_0, K_9 + 1)):
            self.input_repr += chr(key)
            changed = True
        
        if changed:
            self.update_input()
    
    # Update the input parameters -
    # render the text in the center of the input field
    def update_input(self):
            input_text = self.font.render(
                self.input_repr, 0, pg.Color('white')
            )
            input_x = (self.input_field.rect.width // 2 
                - input_text.get_width() // 2)
            input_y = (self.input_field.rect.height // 2
                - input_text.get_height() // 2)

            inside_input = (
                self.highlighted_width,
                self.highlighted_width,
                self.input_field.rect.width - self.highlighted_width*2,
                self.input_field.rect.height - self.highlighted_width*2
            )
            self.input_field.image.fill((0, 0, 0), inside_input)
            self.input_field.image.blit(
                input_text,
                (input_x, input_y))


    # Highlight the input field
    def activate(self): 
        pg.draw.rect(
            self.input_field.image,
            pg.Color('white'),
            ((0, 0), self.input_field.rect.size),
            self.highlighted_width)
    
    # Dehilight
    def deactivate(self):
        # Remove (blacken) the highlighted border
        pg.draw.rect(
            self.input_field.image,
            pg.Color('black'),
            ((0, 0), self.input_field.rect.size),
            self.highlighted_width)
        self.input_repr = ''
        self.update_input()
        pg.draw.rect(
            self.input_field.image,
            pg.Color('white'),
            ((0, 0), self.input_field.rect.size),
            self.border_width)
    
    # Validate the entered input
    def validate(self, speed, score):

        # If there is input entered and 
        # there are equations on the track
        if self.input_repr not in ['', '-'] and self.equations:

            # Correct input
            last_eq = self.equations[0]
            if self.input_repr == str(last_eq.result):
                self.equation_group.remove(last_eq)
                self.equations.popleft()
                self.input_repr = ''
                self.update_input()
                score.update(abs(last_eq.result))
            
            # Incorrent
            # Punishment - move the equation down
            else:
                last_eq.rect.top += speed
                score.update(-abs(int(self.input_repr)))


class Game:

    def __init__(self, config: Config):
        self.screen = pg.display.get_surface()
        self.config = config

        # Variables
        self.speed = self.config.speed
        self.active = config.default_active

        # Set the columns
        self.columns = []
        self.col_group = pg.sprite.Group()
        self.input_group = pg.sprite.Group()
        for i in range(self.config.columns):
            col_rect = pg.Rect(
                self.config.board_left + i * self.config.col_width,
                self.config.board_top,
                self.config.col_width,
                self.config.col_height)

            col = Column(
                col_rect,
                self.config.border_width,
                self.config.highlighted_width,
                self.config.input_height,
                self.config.font,
                self.col_group,
                self.input_group)
            self.columns.append(col)
    
    # Running the game
    def run(self):
        score = pg.sprite.GroupSingle(Score(
            1, self.config.font, self.config.score_rect
        ))
        self.columns[self.active].activate()
        clock = pg.time.Clock()

        GENERATE = USEREVENT + 1 # Generate new equation event
        pg.time.set_timer(GENERATE, self.config.get_frequency)

        SPEEDUP = USEREVENT + 2  # Increase the game speed
        pg.time.set_timer(SPEEDUP, self.config.inc_frequency)
        while 1:
            for event in pg.event.get():
                if event.type == QUIT:
                    return
                elif event.type == GENERATE:
                    # Generate new equation for a random column
                    # (even generation)
                    self.columns[random.randrange(0, self.config.columns)].generate_eq()
                elif event.type == SPEEDUP:
                    self.speed += self.config.increment
                elif event.type == KEYDOWN:

                    k = event.key
                    # Change active column to one to the left
                    if k == K_LEFT:
                        self.columns[self.active].deactivate()
                        self.active = (self.active - 1) % self.config.columns
                        self.columns[self.active].activate()
                    
                    # Change active column to one to the right
                    elif k == K_RIGHT:
                        self.columns[self.active].deactivate()
                        self.active = (self.active + 1) % self.config.columns
                        self.columns[self.active].activate()

                    # Get input into the active column's input field
                    elif k in [K_BACKSPACE, K_MINUS] or k in range(K_0, K_9 + 1):
                        self.columns[self.active].get_input(event.key)
                    elif k == K_RETURN:
                        self.columns[self.active].validate(self.speed, score)
                        
            

            self.screen.fill((0, 0, 0))
            for col in self.columns:
                col.image.fill((0, 0, 0), col.inside)
                col.update(self.speed / self.config.fps)
                col.render_equations()
            self.col_group.draw(self.screen)
            self.input_group.draw(self.screen)
            score.draw(self.screen)
            clock.tick(self.config.fps)
            pg.display.flip()


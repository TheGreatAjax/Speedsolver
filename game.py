import pygame as pg
from pygame.locals import *
import random

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
            increment:      int,  # Speed increment
            default_active: int,  # Index of the column
                                  # active by default
            font:           pg.font.Font  # Font size for equations
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

# Equation which falls from the top of the screen
class Equation():

    operands = [str(i) for i in range(1, 10)] # Possible operands
    operations = ['+', '-', '*'] # Possible operators

    def __init__(self, col, ops, font):
        self.ops = ops # How many operands equation contains
        self.repr = random.choice(self.operands) # String representation of the equation
                                                 # operand-operation-operand-...
        for _ in range (1, ops):
            self.repr += random.choice(self.operations)
            self.repr += random.choice(self.operands)
        
        self.result = eval(self.repr) # Solution

        # Initing the text
        self.text = font.render(self.repr, 0, pg.Color('white'))
        self.text_w = self.text.get_width()
        self.text_h = self.text.get_height()

        # Set the position relative to the column's top-left corner
        self.text_x = col.rect.width // 2 - self.text_w // 2
        self.text_y = col.rect.top


class Column(pg.sprite.Sprite):
    def __init__(self, rect: pg.Rect, border_width, highlighted_width, input_height, font, col_group, input_group):
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
                
        # The input field
        self.input_field = pg.sprite.Sprite(input_group)
        self.input_field.image = pg.Surface((self.rect.width, input_height))
        self.input_field.rect = self.input_field.image.get_rect().move(
            self.rect.left, self.rect.top + self.rect.height
        )
        pg.draw.rect(
            self.input_field.image,
            pg.Color('white'),
            ((0, 0), self.input_field.rect.size),
            self.border_width)

        # The text
        self.input_repr = str() 

        # The list of equations
        self.equations = list()
    
    def update(self, speed):
        for eq in self.equations:
            eq.text_y += speed
    
    # Draw the column's content onto it
    def render(self):

        inside = (
            self.border_width,
            self.border_width,
            self.rect.width - self.border_width*2,
            self.rect.height - self.border_width*2
        )
        self.image.fill((0, 0, 0), inside)

        for eq in self.equations:
            self.image.blit(eq.text, (eq.text_x, eq.text_y))
    
    def generate_eq(self):
        self.equations.append(Equation(
            self, random.randrange(2, 3), self.font
        ))

    # Get input from the input field
    # key is assumed to be either backspace or a number
    def get_input(self, key):
        changed = False
        if key == K_BACKSPACE and self.input_repr != '':
            self.input_repr = self.input_repr[:-1]
            changed = True
        else:
            self.input_repr += chr(key)
            changed = True
        
        # Update the input parameters -
        # render the text in the center of the input field
        if changed:
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
        pg.draw.rect(
            self.input_field.image,
            pg.Color('white'),
            ((0, 0), self.input_field.rect.size),
            self.border_width)

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
                -1,
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

    # # Draw the columns on the screen
    # def draw(self):
    #     self.screen.fill((0, 0, 0))
    #     self.col_group.update()
    #     self.col_group.draw(self.screen)
    #     pg.display.flip()
    
    def pause():
        pass

    # Running the game
    def run(self):
        self.columns[0].generate_eq()
        self.columns[self.active].activate()
        while 1:
            for event in pg.event.get():
                if event.type == QUIT:
                    return
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
                    # elif k == K_SPACE:
                    #     self.
                    elif k == K_BACKSPACE or k in range(K_0, K_9 + 1):
                        self.columns[self.active].get_input(event.key)
            

            self.screen.fill((0, 0, 0))
            self.col_group.update(self.speed)
            self.col_group.draw(self.screen)
            self.input_group.draw(self.screen)
            pg.display.flip()


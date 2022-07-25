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
    def __init__(self, rect: pg.Rect, border_width, highlighted_width, input_height, font, col_group):
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

        # Input text rendering parameters
        self.input_rect = pg.Rect(
                           0,
                           self.rect.height - input_height,
                           self.rect.width,
                           input_height) # Place it on the bottom of the column
        pg.draw.rect(self.image, pg.Color('white'),
                    self.input_rect, self.border_width)  # Draw the border

        # The text
        self.input_repr = str()

        # Positon - relative to the column
        self.input_x = self.input_rect.centerx
        self.input_y = self.input_rect.centery
        self.input_text = self.font.render('', 0, pg.Color('white'))

        self.equations = list()
    
    # Draw the column's content on the screen
    def render(self, screen):

        inside = self.rect.clip((
            self.rect.left,
            self.rect.top,
            self.rect.width - self.highlighted_width,
            self.rect.height - self.highlighted_width))
        self.image.fill((0, 0, 0), inside)

        for eq in self.equations:
            self.image.blit(eq.text, (eq.text_x, eq.text_y))
        
        # Draw the input
        self.image.blit(self.input_text, (self.input_x, self.input_y))
    
    def generate_eq(self):
        self.equations.append(Equation(
            self, random.randrange(2, 3), self.font
        ))

    # Get input from the input field
    # key is assumed to be aither backspace or a number
    def get_input(self, key):
        changed = False
        if key == K_BACKSPACE and self.input_repr != '':
            self.input_repr = self.input_repr[:-1]
            changed = True
        else:
            self.input_repr += chr(key)
            changed = True
        
        # Update the input parameters -
        # place the text in the center of the input field
        if changed:
            self.input_text = self.font.render(
                self.input_repr, 0, pg.Color('white')
            )
            self.input_x = self.input_rect.centerx - self.input_text.get_width() // 2
            self.input_y = self.input_rect.centery - self.input_text.get_height() // 2

    # Highlight the input field
    def activate(self):
        pg.draw.rect(self.image, pg.Color('white'),
                 self.input_rect, self.highlighted_width)  
    
    # Dehilight
    def deactivate(self):
        # Remove (blacken) the highlighted border
        pg.draw.rect(self.image, pg.Color('black'), 
            self.input_rect, self.highlighted_width)
        pg.draw.rect(self.image, pg.Color('white'),
            self.input_rect, self.highlighted_width) 

class Game:

    # Methods
    def __init__(self, config: Config):
        self.screen = pg.display.get_surface()
        self.config = config

        # Variables
        self.speed = self.config.speed
        self.active = config.default_active

        # Set the columns
        self.columns = []
        self.col_group = pg.sprite.Group()
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
                self.col_group)
            self.columns.append(col)
        
    def update(self):

        # Move all the equations down
        for col in self.columns:
            for eq in col.equations:
                eq.text_y += self.config.speed

    # Draw the columns on the screen
    def draw(self):
        self.screen.fill((0, 0, 0))
        for col in self.columns:
            col.render(self.screen)
        self.col_group.draw(self.screen)
        pg.display.flip()
    
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
                    elif k == K_SPACE:
                        self.update() 
                    elif k == K_BACKSPACE or k in range(K_0, K_9 + 1):
                        self.columns[self.active].get_input(event.key)
            
            self.draw()



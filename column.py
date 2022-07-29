import pygame as pg
from pygame.locals import *
from equation import Equation
from collections import deque

class Column(pg.sprite.Sprite):
    def __init__(self,
                 index,
                 gameConfig,
                 lvlConfig,
                 rect: pg.Rect,
                 input_group):
        super().__init__()
        self.index = index
        self.border_width = gameConfig.border_width
        self.highlighted_width = gameConfig.highlighted_width
        self.input_height = gameConfig.input_height
        self.lvlConfig = lvlConfig
        self.font = pg.font.Font(gameConfig.font_path, 16)
        self.rect = rect

        self.input_repr = str() # Input text
        self.equations = deque() # The list of equations
        self.equation_group = pg.sprite.Group()
        
        # The input field
        self.input_field = pg.sprite.Sprite(input_group)
        self.input_field.image = pg.Surface((self.rect.width, gameConfig.input_height))
      
        self.__setGraphics()

    # Place the column and its input field in correct position
    def __setGraphics(self):

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

        # Draw the input field
        # on the bottom of the column
        self.input_field.rect = self.input_field.image.get_rect().move( 
            self.rect.left, self.rect.top + self.rect.height
        )
        pg.draw.rect(
            self.input_field.image,
            pg.Color('white'),
            ((0, 0), self.input_field.rect.size),
            self.border_width)

        self.inside_input = (
            self.highlighted_width,
            self.highlighted_width,
            self.input_field.rect.width - self.highlighted_width*2,
            self.input_field.rect.height - self.highlighted_width*2
        )
    
    # Render and move down the equations
    # Return True if gameover, False otherwise
    def update(self, speed):

        self.image.fill((0, 0, 0), self.inside)
        self.equation_group.draw(self.image)

        # Check for gameover -
        # whether the first equation hits the bottom
        if self.equations:
            first = self.equations[0]
            if (first.rect.top + speed + first.rect.height
                     >= self.rect.top + self.rect.height):
                return True

        for eq in self.equations:
            eq.rect.top += speed
        return False
        
    # Generate new equation for the column
    def generate_eq(self):
        new_eq = Equation(
            self,
            self.font, 
            self.lvlConfig,
            self.equation_group
        )

        # Generate only if it doesn't stack
        # on top of the last equation in the column
        if (self.equations and
            new_eq.rect.top + new_eq.rect.height*2 >= self.equations[-1].rect.top):
            self.equation_group.remove(new_eq)
        else:
            self.equations.append(new_eq)

    def get_input(self, key):

        # Backspace can be pressed only on non-empty string
        if key == K_BACKSPACE:
            if self.input_repr != '':
                self.input_repr = self.input_repr[:-1]

        # Minus can be inserted only in the beginning
        elif key == K_MINUS:
            if self.input_repr == '':
                self.input_repr += chr(key)

        else:
            # Make sure the input isn't too long
            if len(self.input_repr + chr(key)) > 5:
                return
            else:
                self.input_repr += chr(key)
        
        self.update_input()
    
    # Render the text in the center of the input field
    def update_input(self):
            input_text = self.font.render(
                self.input_repr, 0, pg.Color('white')
            )
            input_x = (self.input_field.rect.width // 2 
                - input_text.get_width() // 2)
            input_y = (self.input_field.rect.height // 2
                - input_text.get_height() // 2)

           
            self.input_field.image.fill((0, 0, 0), self.inside_input)
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
    
    # Dehighlight
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

        self.input_repr = ''
        self.update_input()
    
    # Whether entered input matches first equation
    def check(self, speed, score):

        # If there is input entered and 
        # there are equations on the track
        if self.input_repr not in ['', '-'] and self.equations:

            last_eq = self.equations[0]

            # Correct input
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

    def reset(self):
        self.equation_group.empty()
        self.input_repr = str()
        self.update_input()
        self.equations = deque()
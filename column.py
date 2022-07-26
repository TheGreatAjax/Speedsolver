import pygame as pg
from pygame.locals import *
from equation import Equation
from collections import deque

class Column(pg.sprite.Sprite):
    def __init__(self,
                 gameConfig,
                 lvlConfig,
                 rect: pg.Rect,
                 col_group,
                 input_group):
        super().__init__(col_group)
        self.border_width = gameConfig.border_width
        self.highlighted_width = gameConfig.highlighted_width
        self.input_height = gameConfig.input_height
        self.lvlConfig = lvlConfig
        self.font = gameConfig.font
        self.rect = rect

        self.input_repr = str() # Input text
        self.equations = deque() # The list of equations
        self.equation_group = pg.sprite.Group()
        
        # The input field
        self.input_field = pg.sprite.Sprite(input_group)
        self.input_field.image = pg.Surface((self.rect.width, gameConfig.input_height))

      
        self.__setGraphics()

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
        

    
    def update(self, speed):
        for eq in self.equations:
            eq.rect.top += speed
    
    def render_equations(self):
        self.equation_group.draw(self.image)
    
    def generate_eq(self):
        new_eq = Equation(
            self,
            self.font, 
            self.lvlConfig,
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
    
    # check the entered input
    def check(self, speed, score):

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
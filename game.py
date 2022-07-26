import pygame as pg
from pygame.locals import *
from score import Score
import random
from collections import deque

# Equation which falls from the top of the screen
class Equation(pg.sprite.Sprite):

    def __init__(self, col, font, lvlConfig, eq_group):
        super().__init__(eq_group)
        self.range = lvlConfig.operands_range
        self.operands = [str(i) for i in range(1, lvlConfig.operands_max + 1)]
        self.operations = lvlConfig.operations

        self.repr = self.generate()
        self.result = eval(self.repr) # Solution

        self.__setGraphics(col, font)

    
    def __setGraphics(self, col, font):
        self.image = font.render(self.repr, 0, pg.Color('white')) # Which is text
        text_w = self.image.get_width()
        text_h = self.image.get_height()
        self.rect = pg.Rect(    # Place in the upper middle of its column
            col.rect.width // 2 - text_w // 2,
            col.rect.top,
            text_w,
            text_h
        )

    # Generate the equation
    def generate(self):
        eq = random.choice(self.operands) # String representation of the equation
                                                 # operand-operation-operand-...
        for _ in range (1, self.range):
            eq += random.choice(self.operations)
            eq += random.choice(self.operands)
        return eq


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

    def __init__(self, gameConfig, lvlConfig):
        self.screen = pg.display.get_surface()
        self.gameConfig = gameConfig
        self.lvlConfig = lvlConfig

        # Variables
        self.speed = gameConfig.speed
        self.active = gameConfig.default_active

        # Set the columns
        self.columns = []
        self.col_group = pg.sprite.Group()
        self.input_group = pg.sprite.Group()

        self.__setGraphics()
    
    def __setGraphics(self):
        for i in range(self.lvlConfig.columns):
            col_rect = pg.Rect(
                self.gameConfig.board_left + i * self.gameConfig.col_width,
                self.gameConfig.board_top,
                self.gameConfig.col_width,
                self.gameConfig.col_height)

            col = Column(
                self.gameConfig,
                self.lvlConfig,
                col_rect,
                self.col_group,
                self.input_group)
            self.columns.append(col)

    
    # Running the game
    def run(self):
        score = pg.sprite.GroupSingle(Score(
            1, self.gameConfig.font, self.gameConfig.score_rect
        ))
        self.columns[self.active].activate()
        clock = pg.time.Clock()

        GENERATE = USEREVENT + 1 # Generate new equation event
        pg.time.set_timer(GENERATE, self.lvlConfig.gen_frequency)

        SPEEDUP = USEREVENT + 2  # Increase the game speed
        pg.time.set_timer(SPEEDUP, self.lvlConfig.inc_frequency)
        while 1:
            for event in pg.event.get():
                if event.type == QUIT:
                    return
                if event.type == GENERATE:
                    # Generate new equation for a random column
                    # (even generation)
                    self.columns[random.randrange(0, self.lvlConfig.columns)].generate_eq()
                if event.type == SPEEDUP:
                    self.speed *= self.config.increment
                if event.type == KEYDOWN:

                    k = event.key
                    # Change active column to one to the left
                    if k == K_LEFT:
                        self.columns[self.active].deactivate()
                        self.active = (self.active - 1) % self.lvlConfig.columns
                        self.columns[self.active].activate()
                    
                    # Change active column to one to the right
                    elif k == K_RIGHT:
                        self.columns[self.active].deactivate()
                        self.active = (self.active + 1) % self.lvlConfig.columns
                        self.columns[self.active].activate()

                    # Get input into the active column's input field
                    elif k in [K_BACKSPACE, K_MINUS] or k in range(K_0, K_9 + 1):
                        self.columns[self.active].get_input(event.key)
                    elif k == K_RETURN:
                        self.columns[self.active].validate(self.speed, score)
            

            self.screen.fill((0, 0, 0))
            for col in self.columns:
                col.image.fill((0, 0, 0), col.inside)
                col.render_equations()
                col.update(self.speed / self.gameConfig.fps)
            self.col_group.draw(self.screen)
            self.input_group.draw(self.screen)
            score.draw(self.screen)
            clock.tick(self.gameConfig.fps)
            pg.display.flip()


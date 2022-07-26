import pygame as pg
import random

# Equation which falls from the top of the screen
class Equation(pg.sprite.Sprite):

    def __init__(self, col, font, lvlConfig, eq_group):
        super().__init__(eq_group)
        self.range = random.randint(2, lvlConfig.operands_range) # Range of numbers of operands
        self.operands = [str(i) for i in range(1, lvlConfig.operands_max + 1)] # The operands
        self.operations = lvlConfig.operations # The operations

        self.repr = self.generate()
        self.result = eval(self.repr) # Solution

        self.__setGraphics(col, font)

    # Place in the middle top of its column
    def __setGraphics(self, col, font):
        self.image = font.render(self.repr, 0, pg.Color('white')) # Which is text
        text_w = self.image.get_width()
        text_h = self.image.get_height()
        self.rect = pg.Rect(    
            col.rect.width // 2 - text_w // 2,
            col.rect.top,
            text_w,
            text_h
        )

    def generate(self):
        eq = random.choice(self.operands) # String representation of the equation
                                          # operand-operation-operand-...
        for _ in range (1, self.range):
            op = random.choice(self.operations)
            eq += op
            eq += random.choice(self.operands)
        
        return eq
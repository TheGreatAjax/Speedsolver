import pygame as pg

class Score(pg.sprite.Sprite):

    def __init__(self, level, font, dim):
        super().__init__()
        self.level = level
        self.font = font
        self.__score = 0
        self.image = font.render('0', 0, pg.Color('white'))
        self.rect = dim

    def update(self, points):
        self.__score += points * self.level
        self.image = self.font.render(str(self.__score), 0, pg.Color('white'))
    
    def reset(self):
        self.__score = 0
        self.image = self.font.render('0', 0, pg.Color('white'))
import pygame
from src.settings import *
from src.framework.ui import Widget

class StaticImage(Widget):
    def __init__(self, x, y, w, h, image):
        super().__init__(x, y, w, h)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = pygame.transform.scale(image, (w, h))

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class StaticText(Widget):
    def __init__(self, x, y, text, font_size, color):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font_size = font_size
        self.color = color
        
        self.font = get_font("./fonts/Futura-Light.otf", font_size)

    def draw(self, surface):
        surface.blit(self.font.render(self.text, True, self.color), (self.rect.left, self.rect.top))
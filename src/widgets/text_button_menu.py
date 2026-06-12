import pygame
from src.settings import *
from src.framework.ui import Widget, TextButton

UNDERLINE_COLOR = (125, 125, 125)

class TextButtonMenu(Widget):
    """ 战地风格纯文字按钮 """
    def __init__(self, x, y, w, font_size=24):
        super().__init__(x, y, w, 0) # 宽高稍后计算
        self.x = x
        self.y = y
        self.font_size = font_size
        self.buttons = []
        self.selected_button_index = 0
        
    def add_menu_item(self, text, callback=None):
        button = TextButton(text, self.x, self.y, self.font_size, callback) # 位置稍后计算
        self.buttons.append(button)

    def handle_event(self, event):
        super().handle_event(event)
        
        if event.type == pygame.MOUSEMOTION:
            index = 0
            for button in self.buttons:
                hovered = button.rect.collidepoint(event.pos)
                if hovered:
                    self.selected_button_index = index
                    break
                
                index = index + 1
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                button.handle_event(event)

    def draw(self, surface):
        self.rect.height = self.buttons[0].rect.height
        #if len(self.buttons) > 0:
        #    self.buttons[self.selected_button_index].hovered = True
        
        pygame.draw.line(surface, UNDERLINE_COLOR, 
                         (self.rect.left, self.rect.bottom + 5),
                         (self.rect.right, self.rect.bottom + 5), 2)

        left = self.x
        
        index = 0
        for button in self.buttons:
            button.rect.left = left
            
            if index == self.selected_button_index:
                button.hovered = True
            else:
                button.hovered = False
                
            button.draw(surface)
            
            left = left + button.rect.width + 32
            index = index + 1
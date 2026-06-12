import pygame
from src.settings import *
from src.framework.ui import Widget, BattleCard

class BattleCardMenu(Widget):
    def __init__(self, x, y, h, font_size=24):
        super().__init__(x, y, 0, h) # 宽高稍后计算
        self.font_size = font_size
        self.cards = []
        self.selected_card_index = -1
        
    def add_new_card(self, title, subtitle, w, image=None, callback=None):
        card = BattleCard(title, subtitle, self.rect.left, self.rect.top, w, self.rect.height, image, callback) # 位置稍后计算
        self.cards.append(card)
        
    def clear_cards(self):
        self.cards.clear()

    def handle_event(self, event):
        super().handle_event(event)
        
        if event.type == pygame.MOUSEMOTION:
            index = 0
            for card in self.cards:
                hovered = card.rect.collidepoint(event.pos)
                card.hovered = hovered
                index = index + 1
                    
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in self.cards:
                if card.rect.collidepoint(event.pos):
                    card.handle_event(event)

    def draw(self, surface):
        
        left = self.rect.left
        
        index = 0
        for card in self.cards:
            card.rect.left = left
            card.rect.top = self.rect.top
            card.draw(surface)
            
            left = left + card.rect.width + 8
            index = index + 1
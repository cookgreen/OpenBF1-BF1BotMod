import pygame
from src.settings import *
from src.framework.ui import Widget

class Panel(Widget):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.widgets = []
        
    def add_new_widget(self, widget):
        widget.rect.left = widget.rect.left + self.x
        widget.rect.top = widget.rect.top + self.y
        self.widgets.append(widget)
        
    def clear_widgets(self):
        self.widgets.clear()

    def handle_event(self, event):
        for widget in self.widgets:
            widget.handle_event(event)

    def draw(self, surface):
        for widget in self.widgets:
            widget.draw(surface)
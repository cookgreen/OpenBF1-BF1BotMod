import pygame
from src.settings import *

UNDERLINE_COLOR = (243, 243, 243)
BAR_RECT_COLOR = (0, 0, 0, 160)

class Widget:
    """ 所有 UI 组件的基类 """
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.hovered = False
        self.active = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        return self.hovered

    def draw(self, surface):
        pass

class TextButton(Widget):
    """ 战地风格纯文字按钮 """
    def __init__(self, text, x, y, font_size=24, callback=None):
        super().__init__(x, y, 0, 0) # 宽高稍后计算
        self.text = text
        self.font_light = get_font("./fonts/Futura-Light.otf", font_size)
        self.font_bold = get_font("./fonts/Futura-Light.otf", font_size)
        self.font = self.font_light
        self.callback = callback # 点击后的回调函数
        
        # 计算尺寸
        surf = self.font.render(text, True, WHITE)
        self.rect.size = surf.get_size()

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.callback:
                self.callback() # 触发回调

    def draw(self, surface):
        color = WHITE if self.hovered else UNDERLINE_COLOR
        
        # 下划线动画
        if self.hovered:
            self.font = self.font_bold
            pygame.draw.line(surface, color, 
                             (self.rect.left, self.rect.bottom + 5),
                             (self.rect.right, self.rect.bottom + 5), 2)
        else:
            self.font = self.font_light
        
        text_surf = self.font.render(self.text, True, color)
        surface.blit(text_surf, self.rect.topleft)

class BattleCard(Widget):
    def __init__(self, title, subtitle, x, y, w, h, image=None, callback=None):
        super().__init__(x, y, w, h)
        self.bar_height = self.rect.height * 0.32
        self.padding = self.bar_height * 0.25
        self.title = title
        self.subtitle = subtitle
        self.image = image
        self.callback = callback
        
        self.title_font = get_font("./fonts/Futura-Bold.otf", 18)
        self.sub_font = get_font("./fonts/Futura-Light.otf", 20)

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.callback:
                self.callback()

    def draw(self, surface):
        # 1. 图片区
        img_h = self.rect.height - self.bar_height
        img_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, img_h)
        
        if self.image:
            # 简单的裁剪/缩放以适应
            scaled = pygame.transform.scale(self.image, (self.rect.width, img_h))
            surface.blit(scaled, img_rect.topleft)
        else:
            pygame.draw.rect(surface, (50, 60, 70), img_rect)

        # 悬停遮罩
        if self.hovered:
            # 文字
            t_surf = self.title_font.render(self.title, True, BLACK)
            s_surf = self.sub_font.render(self.subtitle, True, (100, 100, 100))
            
            # 2. 底部白条
            bar_rect = pygame.Rect(self.rect.left, self.rect.bottom - self.bar_height, self.rect.width, self.bar_height)
            shape_surf = pygame.Surface(pygame.Rect(bar_rect).size, pygame.SRCALPHA)
        
            # Draw the rectangle onto the temporary surface using the RGBA color
            pygame.draw.rect(shape_surf, WHITE, shape_surf.get_rect())
            surface.blit(shape_surf, bar_rect)
            
            surface.blit(t_surf, (bar_rect.left + self.padding, bar_rect.top + self.padding))
            surface.blit(s_surf, (bar_rect.left + self.padding, bar_rect.top + self.padding*2))
        else:
            # 文字
            t_surf = self.title_font.render(self.title, True, WHITE)
            s_surf = self.sub_font.render(self.subtitle, True, (182, 182, 182))
            
            # 2. 底部白条
            bar_rect = pygame.Rect(self.rect.left, self.rect.bottom - self.bar_height, self.rect.width, self.bar_height)
            shape_surf = pygame.Surface(pygame.Rect(bar_rect).size, pygame.SRCALPHA)
        
            # Draw the rectangle onto the temporary surface using the RGBA color
            pygame.draw.rect(shape_surf, BAR_RECT_COLOR, shape_surf.get_rect())
            surface.blit(shape_surf, bar_rect)
            
            surface.blit(t_surf, (bar_rect.left + self.padding, bar_rect.top + self.padding))
            surface.blit(s_surf, (bar_rect.left + self.padding, bar_rect.top + self.padding*2))
            

        

class UIManager:
    """ UI 管理器：负责统一处理所有组件 """
    def __init__(self):
        self.widgets = []

    def add(self, widget):
        self.widgets.append(widget)

    def handle_event(self, event):
        for w in self.widgets:
            w.handle_event(event)

    def draw(self, surface):
        for w in self.widgets:
            w.draw(surface)
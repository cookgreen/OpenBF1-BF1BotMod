# src/framework/ui.py (追加)

import pygame
import glm
from src.settings import *
from src.graphics import project_point # 复用我们之前的投影函数

class SpawnPointIcon(Widget):
    def __init__(self, name, world_pos, is_base=False, team="blue"):
        super().__init__(0, 0, 30, 30) 
        self.name = name
        self.world_pos = glm.vec3(world_pos)
        self.is_base = is_base
        self.team = team 
        self.selected = False
        self.visible = False 

    def update_screen_pos(self, cam_matrix, screen_size):
        """ 每一帧计算屏幕位置 """
        res = project_point(self.world_pos, cam_matrix, (screen_size[0]/2, screen_size[1]/2))
        
        if res:
            self.rect.center = (res[0], res[1])
            self.visible = True
        else:
            self.visible = False

    def draw(self, surface):
        if not self.visible: return

        # 颜色逻辑
        if self.team == "blue":
            base_color = (100, 180, 255) # 战地蓝
        elif self.team == "red":
            base_color = (255, 80, 80)   # 战地红
        else:
            base_color = (200, 200, 200) # 中立白

        # 如果被选中，变成绿色
        if self.selected:
            base_color = (100, 255, 100)
            # 选中时画个外圈光晕
            pygame.draw.circle(surface, (100, 255, 100, 100), self.rect.center, 25, 2)

        # 绘制图标
        if self.is_base:
            # 基地是圆形的
            pygame.draw.circle(surface, (0, 0, 0, 150), self.rect.center, 15) 
            pygame.draw.circle(surface, base_color, self.rect.center, 15, 2) 
            # 里面画个简单的图案 (比如房子)
            pygame.draw.rect(surface, base_color, (self.rect.centerx-5, self.rect.centery-5, 10, 10))
        else:
            # 据点是菱形的
            cx, cy = self.rect.center
            pts = [(cx, cy-15), (cx+15, cy), (cx, cy+15), (cx-15, cy)]
            pygame.draw.polygon(surface, (0, 0, 0, 150), pts) 
            pygame.draw.polygon(surface, base_color, pts, 2) 
            
            # 写名字 (A, B)
            font = get_font(18, bold=True)
            text = font.render(self.name, True, base_color)
            tr = text.get_rect(center=self.rect.center)
            surface.blit(text, tr)
            
        # 悬停高亮
        if self.hovered:
            pygame.draw.circle(surface, WHITE, self.rect.center, 4, 0)
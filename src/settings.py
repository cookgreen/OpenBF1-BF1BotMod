import pygame

# 屏幕设置
WIDTH, HEIGHT = 1280, 720

# 颜色定义
SKY_COLOR = (0.1, 0.1, 0.15) # OpenGL清屏色 (0-1)

# 坦克颜色 (0-255)
PLAYER_BODY = (70, 80, 50)
PLAYER_TOP  = (90, 100, 60)
ENEMY_BODY = (100, 40, 40)
ENEMY_TOP  = (140, 60, 60)

TURRET_BODY = (160, 140, 60)
TURRET_TOP  = (180, 160, 80)
BARREL_COLOR = (30, 30, 30)

# 其他颜色
SHELL_COLOR = (255, 255, 0)
INFANTRY_COLOR = (50, 50, 200)
EXPLOSION_COLOR = (255, 50, 0)

# 游戏参数
GRAVITY = 50.0
FPS = 50.0

PLANE_BODY = (200, 200, 200) # 机身白/灰
PLANE_WING = (180, 50, 50)   # 机翼红 (致敬红男爵)
PROP_COLOR = (50, 50, 50)    # 螺旋桨黑

# FPS 颜色
SKIN_COLOR = (210, 160, 120) # 皮肤色
GUN_METAL  = (80, 80, 80)    # 枪身灰
GUN_HANDLE = (40, 20, 10)    # 握把褐
MUZZLE_FLASH = (255, 200, 50) # 枪口火焰

# 颜色 (BF1 风格)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BF_ORANGE = (255, 100, 50)
DARK_BG = (30, 35, 40, 200) # 带透明度的深色背景

def get_font(font_path, size, bold=True):
    return pygame.font.Font(font_path, size)



def create_box(w, l, h, color, offset=(0,0,0)):
    hw, hl, hh = w/2, l/2, h/2
    ox, oy, oz = offset
    
    verts = [
        # Top (Z+)
        -hw+ox, hl+oy, hh+oz, 0,0,1, *color,  hw+ox, hl+oy, hh+oz, 0,0,1, *color,  hw+ox,-hl+oy, hh+oz, 0,0,1, *color,
        -hw+ox, hl+oy, hh+oz, 0,0,1, *color,  hw+ox,-hl+oy, hh+oz, 0,0,1, *color, -hw+ox,-hl+oy, hh+oz, 0,0,1, *color,
        # Bottom (Z-)
        -hw+ox,-hl+oy,-hh+oz, 0,0,-1, *color, hw+ox,-hl+oy,-hh+oz, 0,0,-1, *color, hw+ox, hl+oy,-hh+oz, 0,0,-1, *color,
        -hw+ox,-hl+oy,-hh+oz, 0,0,-1, *color, hw+ox, hl+oy,-hh+oz, 0,0,-1, *color, -hw+ox, hl+oy,-hh+oz, 0,0,-1, *color,
        # Front (Y+)
        -hw+ox, hl+oy,-hh+oz, 0,1,0, *color,  hw+ox, hl+oy,-hh+oz, 0,1,0, *color,  hw+ox, hl+oy, hh+oz, 0,1,0, *color,
        -hw+ox, hl+oy,-hh+oz, 0,1,0, *color,  hw+ox, hl+oy, hh+oz, 0,1,0, *color, -hw+ox, hl+oy, hh+oz, 0,1,0, *color,
        # Back (Y-)
        -hw+ox,-hl+oy, hh+oz, 0,-1,0, *color, hw+ox,-hl+oy, hh+oz, 0,-1,0, *color, hw+ox,-hl+oy,-hh+oz, 0,-1,0, *color,
        -hw+ox,-hl+oy, hh+oz, 0,-1,0, *color, hw+ox,-hl+oy,-hh+oz, 0,-1,0, *color, -hw+ox,-hl+oy,-hh+oz, 0,-1,0, *color,
        # Right (X+)
         hw+ox, hl+oy,-hh+oz, 1,0,0, *color,  hw+ox,-hl+oy,-hh+oz, 1,0,0, *color,  hw+ox,-hl+oy, hh+oz, 1,0,0, *color,
         hw+ox, hl+oy,-hh+oz, 1,0,0, *color,  hw+ox,-hl+oy, hh+oz, 1,0,0, *color,  hw+ox, hl+oy, hh+oz, 1,0,0, *color,
        # Left (X-)
        -hw+ox,-hl+oy,-hh+oz, -1,0,0, *color, -hw+ox, hl+oy,-hh+oz, -1,0,0, *color, -hw+ox, hl+oy, hh+oz, -1,0,0, *color,
        -hw+ox,-hl+oy,-hh+oz, -1,0,0, *color, -hw+ox, hl+oy, hh+oz, -1,0,0, *color, -hw+ox,-hl+oy, hh+oz, -1,0,0, *color,
    ]
    return verts
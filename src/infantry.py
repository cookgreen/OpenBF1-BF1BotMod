import glm
from src.settings import *
from src.graphics import create_cube_vbo
from src.terrain import get_z

class Infantry:
    def __init__(self, ctx, prog, x, y):
        self.pos = glm.vec3(x, y, 0)
        self.alive = True
        self.speed = 8.0
        self.vao = create_cube_vbo(ctx, prog, 1.5, 1.5, 4, INFANTRY_COLOR, pivot_bottom=False)
        self.height = 4.0
        
    def update(self, dt, target_pos):
        if not self.alive: return
        
        direction = target_pos - self.pos
        dist = glm.length(direction)
        
        if dist > 5.0: 
            direction = glm.normalize(direction)
            self.pos.x += direction.x * self.speed * dt
            self.pos.y += direction.y * self.speed * dt
            
        self.pos.z = get_z(self.pos.x, self.pos.y) + self.height/2
        
    def render(self, prog):
        if not self.alive: return
        m = glm.translate(glm.mat4(1), self.pos)
        prog['m_model'].write(m)
        self.vao.render()
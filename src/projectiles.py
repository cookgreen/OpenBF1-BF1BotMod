# src/projectiles.py
import glm
from src.settings import *
from src.graphics import create_cube_vbo
from src.terrain import get_z

class Explosion:
    def __init__(self, ctx, prog, pos):
        self.pos = pos
        self.life = 1.0
        self.scale = 0.1
        self.vao = create_cube_vbo(ctx, prog, 2, 2, 2, EXPLOSION_COLOR, False)
        
    def update(self, dt):
        self.life -= dt * 2.0
        self.scale += dt * 10.0
        
    def render(self, prog):
        if self.life <= 0: return
        m = glm.translate(glm.mat4(1), self.pos)
        m = glm.scale(m, glm.vec3(self.scale))
        prog['m_model'].write(m)
        self.vao.render()

class Shell:
    def __init__(self, pos, dir_vec, owner_id, shared_vao):
        self.pos = pos
        self.vel = dir_vec * 150.0
        self.alive = True
        self.lifetime = 3.0
        self.owner_id = owner_id 
        self.radius = 1.0 
        self.vao = shared_vao 
        
    def update(self, dt):
        self.pos += self.vel * dt
        self.vel.z -= GRAVITY * dt 
        
        if self.pos.z <= get_z(self.pos.x, self.pos.y):
            self.alive = False
            return "ground"
            
        self.lifetime -= dt
        if self.lifetime <= 0: self.alive = False
        return "fly"

    def render(self, prog):
        m = glm.translate(glm.mat4(1), self.pos)
        prog['m_model'].write(m)
        self.vao.render()
import glm
import math
import random
import pygame
import numpy as np
from src.settings import *

class Bullet:
    def __init__(self, ctx, prog, pos, directory, speed):
        self.ctx = ctx
        self.prog = prog
        
        self.pos = pos
        self.vel = directory * speed
        self.life = 2.0 # 2秒寿命
        self.bullet_vao = self.create_bullet_mesh()
        
    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt
        
    def create_bullet_mesh(self):
        data = create_box(0.2, 1.0, 0.2, (1.0, 1.0, 0)) # 黄色长条
        vbo = self.ctx.buffer(np.array(data, dtype='f4').tobytes())
        return self.ctx.vertex_array(self.prog, [(vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')])
        
    def render(self, prog):
        m = glm.translate(glm.mat4(1), self.pos)
        prog['m_model'].write(m)
        self.bullet_vao.render()
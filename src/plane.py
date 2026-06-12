import glm
import math
import random
import pygame
import numpy as np
from src.settings import *
from src.graphics import create_cube_vbo
from src.bullet import Bullet
from src.terrain import get_z

class Plane:
    def __init__(self, ctx, prog, x, y, z, is_player=False, uid=0, shell_vao=None):
        self.pos = glm.vec3(x, y, z)
        self.ctx = ctx
        self.prog = prog
        # 欧拉角
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.transform = glm.translate(glm.mat4(1), self.pos)
        
        self.speed = 60.0 # 初始速度
        self.target_speed = 40.0
        self.prop_spin = 0.0
        
        self.is_player = is_player
        self.uid = uid
        self.alive = True
        self.shell_vao = shell_vao
        self.cooldown = 0.0
        
        self.prop_angle = 0.0
        
        self.plane_vao = self.create_plane_mesh()
        self.prop_vao = self.create_prop_mesh()
        self.bullets = []
        
    
    def create_plane_mesh(self):
        data = []
        # 颜色
        WHITE = (0.8, 0.8, 0.8)
        RED   = (0.7, 0.2, 0.2)
        GREY  = (0.3, 0.3, 0.3)
        BLACK = (0.1, 0.1, 0.1)
        
        # 机身
        data += create_box(2, 10, 2, WHITE)
        # 上机翼
        data += create_box(12, 3, 0.2, RED, (0, 1, 2.5))
        # 下机翼
        data += create_box(10, 3, 0.2, RED, (0, 1, 0))
        # 支柱
        data += create_box(0.2, 0.2, 2.5, GREY, (-4, 1, 1.25))
        data += create_box(0.2, 0.2, 2.5, GREY, (4, 1, 1.25))
        # 尾翼
        data += create_box(4, 2, 0.2, RED, (0, -4, 0.5))
        data += create_box(0.2, 2, 3, RED, (0, -4, 1.5))
        # 起落架
        data += create_box(0.5, 0.5, 1.5, BLACK, (-1, 2, -1.5))
        data += create_box(0.5, 0.5, 1.5, BLACK, (1, 2, -1.5))
        
        vbo = self.ctx.buffer(np.array(data, dtype='f4').tobytes())
        return self.ctx.vertex_array(self.prog, [(vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')])

    # 螺旋桨
    def create_prop_mesh(self):
        data = create_box(6, 0.2, 0.5, (0.2, 0.2, 0.2)) # 横
        data += create_box(0.5, 0.2, 6, (0.2, 0.2, 0.2)) # 竖
        vbo = self.ctx.buffer(np.array(data, dtype='f4').tobytes())
        return self.ctx.vertex_array(self.prog, [(vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')])
    
    def update(self, dt, target_type, target_pos=None):
        #if self.hp <= 0: return # 坠毁逻辑暂时略过
        
        # 速度控制
        self.speed += (self.target_speed - self.speed) * dt
        self.prop_spin += self.speed * 20 * dt
        
        # 玩家控制 (基于局部坐标系的旋转)
        if self.is_player:
            self.handle_player_input(dt)
        elif target_pos:
            self.handle_ai(dt, target_type, target_pos)
        
        # 移动：沿着当前的 Forward 向量移动
        # 获取当前矩阵的前方向量 (Y轴)
        # 矩阵列：0=Right(X), 1=Forward(Y), 2=Up(Z), 3=Pos
        forward = glm.vec3(self.transform[1]) 
        self.pos += forward * self.speed * dt
        
        # 更新矩阵的位置部分
        self.transform[3] = glm.vec4(self.pos, 1.0)
            
        self.cooldown -= dt
        
        self.bullets = []

    def handle_player_input(self, dt):
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_rel()
        
        # W/S 加速
        if keys[pygame.K_w]: self.target_speed = 80.0
        elif keys[pygame.K_s]: self.target_speed = 20.0
        else: self.target_speed = 40.0
        
        # 鼠标控制： Pitch (上下) & Roll (左右)
        pitch_input = -my * 0.003
        roll_input = -mx * 0.003
        
        # 键盘辅助： Yaw (Q/E) & Roll (A/D)
        yaw_input = 0.0
        if keys[pygame.K_q]: yaw_input += 1.0 * dt
        if keys[pygame.K_e]: yaw_input -= 1.0 * dt
        if keys[pygame.K_a]: roll_input += 2.0 * dt
        if keys[pygame.K_d]: roll_input -= 2.0 * dt
        
        self.transform = glm.rotate(self.transform, pitch_input, glm.vec3(1, 0, 0))
        
        self.transform = glm.rotate(self.transform, roll_input, glm.vec3(0, 1, 0))
        
        self.transform = glm.rotate(self.transform, yaw_input, glm.vec3(0, 0, 1))
    
    def handle_ai(self, dt, target_type, target_pos):
        if target_type == "Surface":
            self.handle_ai_ground(dt, target_pos)
        elif target_type == "Air":
            self.handle_ai_air(dt, target_pos)
            
    def handle_ai_ground(self, dt, target_pos):
        # AI 逻辑
        # 目标是玩家坦克
        
        # 计算目标方向
        diff = target_pos - self.pos
        dist = glm.length(diff)
        
        # 水平目标角度
        target_yaw = math.atan2(-diff.x, diff.y)
        
        # 垂直目标角度 (俯冲)
        target_pitch = math.atan2(diff.z - self.pos.z, glm.length(glm.vec2(diff.x, diff.y)))
        
        # 转向目标
        yaw_diff = target_yaw - self.yaw
        # 角度归一化
        while yaw_diff > math.pi: yaw_diff -= 2*math.pi
        while yaw_diff < -math.pi: yaw_diff += 2*math.pi
        
        self.yaw += yaw_diff * 1.0 * dt
        # AI 转弯时也带点侧倾
        self.roll = -yaw_diff * 0.5
        
        # 俯仰控制
        if dist > 300:
            # 距离远，保持高度巡航
            target_h = target_pos.z + 80
            if self.pos.z < target_h: self.pitch = 0.2
            else: self.pitch = -0.1
        else:
            # 距离近，俯冲攻击
            # 防止撞地：如果太低就强行拉起
            if self.pos.z < target_pos.z + 20:
                self.pitch = 0.8 # 拉起
            else:
                self.pitch = target_pitch # 瞄准
                
                # 3. 开火 (只有俯冲且对准时)
                if abs(yaw_diff) < 0.2 and dist < 200:
                    return True # 请求开火
        
        self.speed = 50.0 # AI 恒定速度
        return False
            
    
    def handle_ai_air(self, dt, target_pos):
        # AI 简单的追踪逻辑
        to_target = target_pos - self.pos
        dist = glm.length(to_target)
        if dist < 0.1: return
        to_target = glm.normalize(to_target)
        
        # 获取当前朝向
        forward = glm.vec3(self.transform[1])
        right = glm.vec3(self.transform[0])
        up = glm.vec3(self.transform[2])
        
        # 计算误差
        # 如果目标在上方，dot > 0 -> 需要 Pitch Up
        # 如果目标在右方，dot > 0 -> 需要 Yaw/Roll Right
        pitch_err = glm.dot(to_target, up)
        yaw_err = glm.dot(to_target, right)
        
        # AI 操作
        self.transform = glm.rotate(self.transform, pitch_err * 2.0 * dt, glm.vec3(1,0,0))
        # AI 转向主要靠 Roll + Pitch (像真实飞机一样)
        self.transform = glm.rotate(self.transform, -yaw_err * 2.0 * dt, glm.vec3(0,1,0))
        
        # 速度
        self.target_speed = 50.0
        
        # 开火
        angle = glm.acos(glm.clamp(glm.dot(forward, to_target), -1, 1))
        if angle < 0.2 and dist < 300:
            self.bullets.append(self.shoot())
    
    def shoot(self):
        if self.cooldown > 0: return None
        self.cooldown = 0.1
        
        # 炮口位置 (矩阵变换)
        # 假设炮口在机头前方 5 单位
        offset = glm.vec4(0, 6, 0, 1)
        spawn_pos = glm.vec3(self.transform * offset)
        
        # 速度方向 (机头朝向)
        direction = glm.vec3(self.transform[1]) # Y轴
        
        # 加上飞机自身速度
        return Bullet(self.ctx, self.prog, spawn_pos, direction, self.speed + 100.0)
        
    def render(self, prog):
        # 渲染机身
        prog['m_model'].write(self.transform)
        self.plane_vao.render()
        
        # 渲染螺旋桨 (父子层级)
        # 先把螺旋桨放到机头 (局部 Y=5)
        m_prop = glm.translate(self.transform, glm.vec3(0, 5, 0))
        # 再自转
        m_prop = glm.rotate(m_prop, self.prop_spin, glm.vec3(0, 1, 0))
        
        prog['m_model'].write(m_prop)
        self.prop_vao.render()
        
        for bullet in self.bullets:
            bullet.render(prog)
        if self.is_player:
            self.render_camera(prog)
    
    def render_camera(self, prog):
        # 摄像机跟随逻辑
        # 摄像机位于飞机后方
        target_pos = self.pos
        
        # 获取飞机矩阵的方向向量
        fwd = glm.vec3(self.transform[1]) # Y轴
        up = glm.vec3(self.transform[2])  # Z轴
        
        # 刚性跟随位置
        cam_pos = target_pos - fwd * 40.0 + up * 15.0
        
        # LookAt 矩阵
        # 摄像机位置，看向目标(飞机前方一点)，上向量(随飞机翻滚)
        view = glm.lookAt(cam_pos, target_pos + fwd * 20.0, up)
        
        # 投影矩阵
        proj = glm.perspective(glm.radians(60), WIDTH/HEIGHT, 0.1, 2000.0)
        
        prog['m_proj'].write(proj)
        prog['m_view'].write(view)
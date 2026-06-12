import glm
import math
import pygame
from src.settings import *
from src.graphics import create_cube_vbo
from src.terrain import get_z
from src.projectiles import Shell

class FPSPlayer:
    def __init__(self, ctx, prog, x, y, uid=0, shell_vao=None):
        # 位置 (眼睛的高度)
        self.uid = uid
        self.pos = glm.vec3(x, y, get_z(x,y) + 2.0)
        self.yaw = 0.0
        self.pitch = 0.0
        self.speed = 0.0
        
        self.alive = True
        self.shell_vao = shell_vao
        self.cooldown = 0.0
        
        # --- 武器状态 ---
        self.bob_timer = 0.0 # 用于走路晃动
        self.recoil_offset = 0.0 # 后坐力
        self.sway_offset = glm.vec2(0, 0) # 武器惯性
        
        self.vao_gun_body = create_cube_vbo(ctx, prog, 1.2, 6.0, 1.2, GUN_METAL, False)
        
        self.vao_gun_barrel = create_cube_vbo(ctx, prog, 0.4, 3.0, 0.4, (20,20,20), False)
        
        self.vao_gun_handle = create_cube_vbo(ctx, prog, 0.8, 1.0, 2.5, GUN_HANDLE, False)
        
        self.vao_arm = create_cube_vbo(ctx, prog, 1.0, 5.0, 1.0, SKIN_COLOR, False)

    def update(self, dt, target_info=None): # target_info 占位，保持接口一致
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_rel()
        
        sensitivity = 0.003
        self.yaw -= mx * sensitivity
        self.pitch -= my * sensitivity
        self.pitch = max(-1.5, min(1.5, self.pitch)) # 限制抬头低头
        
        # 计算惯性 (Sway) - 让枪转得慢一点
        target_sway_x = mx * 0.002
        target_sway_y = my * 0.002
        # 插值平滑
        self.sway_offset.x += (target_sway_x - self.sway_offset.x) * 5 * dt
        self.sway_offset.y += (target_sway_y - self.sway_offset.y) * 5 * dt
        
        # --- 2. 移动控制 ---
        move_speed = 15.0 # 跑步速度
        if keys[pygame.K_LSHIFT]: move_speed = 25.0
        
        # 计算平面移动向量
        # Y+ 是前, Z+ 是上
        forward = glm.vec3(-math.sin(self.yaw), math.cos(self.yaw), 0)
        right = glm.vec3(math.cos(self.yaw), math.sin(self.yaw), 0)
        
        move_dir = glm.vec3(0)
        if keys[pygame.K_w]: move_dir += forward
        if keys[pygame.K_s]: move_dir -= forward
        if keys[pygame.K_d]: move_dir += right
        if keys[pygame.K_a]: move_dir -= right
        
        is_moving = False
        if glm.length(move_dir) > 0.1:
            is_moving = True
            move_dir = glm.normalize(move_dir)
            self.pos += move_dir * move_speed * dt
            
            # 走路摇晃 (Bobbing)
            self.bob_timer += dt * 15.0
        else:
            # 站立呼吸
            self.bob_timer += dt * 2.0
            
        # --- 地形贴合 (FPS 模式) ---
        ground_z = get_z(self.pos.x, self.pos.y)
        eye_height = 4.0 # 眼睛离地高度
        
        # 简单的重力/跳跃逻辑可以加在这里，暂时做成贴地走
        self.pos.z = ground_z + eye_height
        
        # --- 射击 ---
        self.recoil_offset *= 0.8 # 后坐力恢复
        self.cooldown -= dt
        
        if pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
            return self.shoot()
            
        return None

    def shoot(self):
        if self.cooldown > 0: return None
        self.cooldown = 0.1 # 冲锋枪射速
        self.recoil_offset = 0.5 # 产生后坐力
        
        # 计算枪口位置 (世界坐标)
        # 这里的计算比较复杂，为了简化，直接从摄像机位置发射
        # 稍微偏右下一点，模拟从枪口出来
        
        # 视线方向
        direction = glm.vec3(
            -math.sin(self.yaw) * math.cos(self.pitch),
            math.cos(self.yaw) * math.cos(self.pitch),
            math.sin(self.pitch)
        )
        
        # 枪口位置：摄像机位置 + 前方一点 + 右方一点 - 下方一点
        right = glm.cross(direction, glm.vec3(0,0,1))
        # 简单的偏移
        start_pos = self.pos + direction * 2.0 + right * 0.5
        
        return Shell(start_pos, direction, 0, self.shell_vao)

    def render(self, prog):
        # FPS 渲染的关键：
        # 枪和手必须始终画在摄像机前面，不能穿墙。
        # 这里用矩阵计算放到摄像机前方。
        
        # 基础矩阵：放在摄像机位置
        m_view_base = glm.translate(glm.mat4(1), self.pos)
        
        # 旋转：跟随视角
        m_view_base = glm.rotate(m_view_base, self.yaw, glm.vec3(0,0,1))
        m_view_base = glm.rotate(m_view_base, self.pitch, glm.vec3(1,0,0)) # 绕X轴抬头
        
        # --- 武器晃动计算 (Weapon Sway & Bob) ---
        # 走路时的上下左右摆动 (Lissajous curve 风格)
        bob_x = math.cos(self.bob_timer) * 0.1
        
        result = math.sin(self.bob_timer)
        if result < 0:
            result = result * -1
        
        bob_y = result * 0.1 # 走路像波浪
        
        # 3. 枪的定位 (相对于摄像机)
        # 右手持枪：向右(X+) 1.2，向下(Z-) 1.5，向前(Y+) 2.5
        gun_offset = glm.vec3(1.2 - self.sway_offset.x, 2.5 - self.recoil_offset, -1.5 - self.sway_offset.y + bob_y)
        
        m_gun = glm.translate(m_view_base, gun_offset)
        
        # 渲染枪身
        prog['m_model'].write(m_gun)
        self.vao_gun_body.render()
        
        # 渲染枪管 (向前伸出)
        m_barrel = glm.translate(m_gun, glm.vec3(0, 3.5, 0.2)) # 稍微偏上一点
        prog['m_model'].write(m_barrel)
        self.vao_gun_barrel.render()
        
        # 渲染握把 (向下伸出)
        # 稍微向后旋转一点，符合握持姿势
        m_handle = glm.translate(m_gun, glm.vec3(0, -1.0, -1.5))
        m_handle = glm.rotate(m_handle, glm.radians(15), glm.vec3(1,0,0))
        prog['m_model'].write(m_handle)
        self.vao_gun_handle.render()
        
        # --- 渲染手臂 ---
        # 右臂 (连接到枪)
        # 从摄像机右下角伸出来
        arm_r_offset = glm.vec3(1.5, 1.0, -2.5 + bob_y) 
        m_arm_r = glm.translate(m_view_base, arm_r_offset)
        # 旋转手臂指向枪
        m_arm_r = glm.rotate(m_arm_r, glm.radians(-20), glm.vec3(1,0,0)) # 抬起
        m_arm_r = glm.rotate(m_arm_r, glm.radians(-10), glm.vec3(0,0,1)) # 向内
        prog['m_model'].write(m_arm_r)
        self.vao_arm.render()
        
        # 左臂 (托住枪或者是战术动作)
        # 你的图里左手也在，假设是托着枪身
        arm_l_offset = glm.vec3(-1.0, 1.5, -2.5 + bob_y)
        m_arm_l = glm.translate(m_view_base, arm_l_offset)
        m_arm_l = glm.rotate(m_arm_l, glm.radians(-30), glm.vec3(1,0,0))
        m_arm_l = glm.rotate(m_arm_l, glm.radians(20), glm.vec3(0,0,1))
        prog['m_model'].write(m_arm_l)
        self.vao_arm.render()
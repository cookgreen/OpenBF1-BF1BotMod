# src/camera.py
import math
import pygame
import glm

class Camera:
    def __init__(self, prog):
        self.prog = prog
        self.yaw = 0.0
        self.pitch = 0.5
        self.dist = 60.0
        self.pos = glm.vec3(0,0,0)
        self.up = glm.vec3(0,0,1) # 默认世界向上
        
    def update_free(self, target_pos):
        """ 坦克模式：鼠标控制摄像机旋转 """
        mx, my = pygame.mouse.get_rel()
        self.yaw += mx * 0.005
        self.pitch -= my * 0.005
        self.pitch = max(0.1, min(1.5, self.pitch))
        
        cam_x = target_pos.x + self.dist * math.sin(self.yaw) * math.cos(self.pitch)
        cam_y = target_pos.y + self.dist * math.cos(self.yaw) * math.cos(self.pitch)
        cam_z = target_pos.z + self.dist * math.sin(self.pitch)
        
        self.pos = glm.vec3(cam_x, cam_y, cam_z)
        # 坦克模式下，Up 永远是 Z 轴
        view = glm.lookAt(self.pos, target_pos + glm.vec3(0,0,5), glm.vec3(0,0,1))
        
        self.prog['m_view'].write(view)
        self.prog['view_pos'].write(self.pos)
        return self.yaw

    def update_locked(self, target_pos, target_model_matrix):
        """ 
        飞机模式：摄像机定死在载具后方 
        target_model_matrix: 飞机的旋转/位移矩阵
        """
        # 计算摄像机在“局部空间”的位置
        offset_local = glm.vec4(0, -80, 20, 1.0) 
        
        # 变换到“世界空间”
        cam_world_pos = target_model_matrix * offset_local
        self.pos = glm.vec3(cam_world_pos)
        
        # 计算 Up 向量
        up_local = glm.vec4(0, 0, 1, 0)
        world_up = glm.vec3(target_model_matrix * up_local)
        
        # LookAt
        target_center = target_pos + glm.vec3(target_model_matrix * glm.vec4(0,0,5,0))
        
        view = glm.lookAt(self.pos, target_center, world_up)
        
        self.prog['m_view'].write(view)
        self.prog['view_pos'].write(self.pos)
        
        return 0 
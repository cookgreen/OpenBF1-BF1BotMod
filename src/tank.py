import pygame
import math
import glm
from src.settings import *
from src.graphics import create_cube_vbo
from src.terrain import get_z
from src.projectiles import Shell

class RealTank:
    def __init__(self, ctx, prog, resource_mgr, vehicle_id, x, y, is_player=True, uid=0, shell_vao=None):
        self.pos = glm.vec3(x, y, 0)
        self.hull_yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.turret_rel_yaw = 0.0
        self.speed = 0.0
        self.is_player = is_player
        self.uid = uid
        self.alive = True
        self.shell_vao = shell_vao
        
        self.resource_mgr = resource_mgr
        self.current_play_sound = None
        
        self.sound_quene = []
        
        self.w, self.l, self.h = 10, 18, 6
        
        self.cooldown = 0
        
        self.mesh_hull = resource_mgr.get_model("model_french_ft_tank_hull")
        self.mesh_chas = resource_mgr.get_model("model_french_ft_tank_chas")
        self.mesh_turret = resource_mgr.get_model("model_french_ft_tank_turrent")
        
        self.muzzle_offset = glm.vec3(0, 1.5, 0.5) # 这里的单位取决于 OBJ 的单位

    def update(self, dt, target_info):
        if not self.alive: return None
        
        fire_request = False
        
        if not pygame.mixer.get_busy() and self.sound_quene:
            key_to_play = self.sound_quene.pop(0)
            self.resource_mgr.sound[key_to_play].play()
        
        if not self.is_player:
            player_pos = target_info
            diff = player_pos - self.pos
            target_aim = math.atan2(-diff.x, diff.y)
            
            target_rel = target_aim - self.hull_yaw
            angle_diff = target_rel - self.turret_rel_yaw
            while angle_diff > math.pi: angle_diff -= 2*math.pi
            while angle_diff < -math.pi: angle_diff += 2*math.pi
            self.turret_rel_yaw += angle_diff * 3.0 * dt
            
            dist = glm.length(diff)
            if dist > 80:
                hull_diff = target_aim - self.hull_yaw
                while hull_diff > math.pi: hull_diff -= 2*math.pi
                while hull_diff < -math.pi: hull_diff += 2*math.pi
                if abs(hull_diff) > 0.1: self.hull_yaw += hull_diff * 1.0 * dt
                self.speed += (40 - self.speed) * dt 
            else:
                self.speed *= 0.9 
            
            if abs(angle_diff) < 0.2 and dist < 150:
                fire_request = True
                
        else:
            cam_yaw_radians = target_info
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: self.speed = 50
            elif keys[pygame.K_s]: self.speed -= 15
            else: self.speed *= 0.9
            
            if abs(self.speed) > 0.5:
                turn = 2.0 * dt * (-1 if self.speed < 0 else 1)
                if keys[pygame.K_a]: self.hull_yaw += turn
                if keys[pygame.K_d]: self.hull_yaw -= turn
                
                if self.current_play_sound and self.current_play_sound != "btlfld1_heavy_tank_moving":
                    self.resource_mgr.sound[self.current_play_sound].stop()
                    
                self.current_play_sound = "btlfld1_heavy_tank_moving"
                self.sound_quene.clear()
                self.sound_quene.append(self.current_play_sound)
            else:
                if self.current_play_sound and self.current_play_sound != "btlfld1_heavy_tank_idle":
                    self.resource_mgr.sound[self.current_play_sound].stop()
                    
                self.current_play_sound = "btlfld1_heavy_tank_idle"
                self.sound_quene.clear()
                self.sound_quene.append(self.current_play_sound)
            
            target_world = cam_yaw_radians*-1 + math.pi
            target_rel = target_world - self.hull_yaw
            diff = target_rel - self.turret_rel_yaw
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            self.turret_rel_yaw += diff * 5.0 * dt
            
            print(self.speed)
            
            if pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
                fire_request = True

        self.pos.x += -math.sin(self.hull_yaw) * self.speed * dt
        self.pos.y += math.cos(self.hull_yaw) * self.speed * dt
        
        z_ground = get_z(self.pos.x, self.pos.y)
        z_f = get_z(self.pos.x - math.sin(self.hull_yaw)*5, self.pos.y + math.cos(self.hull_yaw)*5)
        z_b = get_z(self.pos.x + math.sin(self.hull_yaw)*5, self.pos.y - math.cos(self.hull_yaw)*5)
        target_pitch = math.atan2(z_f - z_b, 10)
        
        z_r = get_z(self.pos.x + math.cos(self.hull_yaw)*3, self.pos.y + math.sin(self.hull_yaw)*3)
        z_l = get_z(self.pos.x - math.cos(self.hull_yaw)*3, self.pos.y - math.sin(self.hull_yaw)*3)
        target_roll = math.atan2(z_l - z_r, 6)
        
        self.pos.z = z_ground + self.h/2
        self.pitch += (target_pitch - self.pitch) * 5 * dt
        self.roll += (target_roll - self.roll) * 5 * dt
        
        self.cooldown -= dt
        if fire_request and self.cooldown <= 0:
            return self.shoot()
        return None

    def shoot(self):
        self.cooldown = 1.5
        
        m_hull = glm.translate(glm.mat4(1), self.pos)
        m_hull = glm.rotate(m_hull, self.hull_yaw, glm.vec3(0,0,1))
        m_hull = glm.rotate(m_hull, self.pitch, glm.vec3(1,0,0))
        m_hull = glm.rotate(m_hull, self.roll, glm.vec3(0,1,0))
        
        m_turret = glm.translate(m_hull, glm.vec3(0, 0, self.h/2))
        m_turret = glm.rotate(m_turret, self.turret_rel_yaw, glm.vec3(0,0,1))
        
        m_barrel = glm.translate(m_turret, glm.vec3(0, 5, 2))
        m_barrel = glm.rotate(m_barrel, glm.radians(-90), glm.vec3(1,0,0))
        
        muzzle_local = glm.vec4(0, 0, 20, 1) 
        muzzle_world = m_barrel * muzzle_local
        start_pos = glm.vec3(muzzle_world)
        
        direction = glm.normalize(glm.vec3(m_barrel * glm.vec4(0,0,1,0)))
        direction.z += 0.2
        direction = glm.normalize(direction)
        
        return Shell(start_pos, direction, self.uid, self.shell_vao)

    def render(self, prog):
        if not self.alive: return
        
        scale_factor = 5 
        m_scale = glm.scale(glm.mat4(1), glm.vec3(scale_factor))
        
        m_model_fix = glm.rotate(glm.mat4(1), glm.radians(90), glm.vec3(1, 0, 0))
        m_model_fix = glm.rotate(m_model_fix, glm.radians(180), glm.vec3(0, 1, 0))
        
        m_body = glm.translate(glm.mat4(1), self.pos)
        m_body = glm.rotate(m_body, self.hull_yaw, glm.vec3(0,0,1)) 
        m_body = glm.rotate(m_body, self.pitch, glm.vec3(1,0,0))    
        m_body = glm.rotate(m_body, self.roll, glm.vec3(0,1,0))     
        
        m_hull_render = m_body * m_scale * m_model_fix
        
        prog['m_model'].write(m_hull_render)
        if self.mesh_chas: self.mesh_chas.render()
        if self.mesh_hull: self.mesh_hull.render()
        
        turret_h_offset = 12 
        
        m_turret = glm.translate(m_body, glm.vec3(0, 0, turret_h_offset))
        
        m_turret = glm.rotate(m_turret, self.turret_rel_yaw, glm.vec3(0,0,1))
        
        m_turret_render = m_turret * m_scale * m_model_fix
        
        prog['m_model'].write(m_turret_render)
        if self.mesh_turret: self.mesh_turret.render()
        
        prog['use_texture'].value = False

class Tank:
    def __init__(self, ctx, prog, x, y, is_player=True, uid=0, shell_vao=None):
        self.pos = glm.vec3(x, y, 0)
        self.hull_yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.turret_rel_yaw = 0.0
        self.speed = 0.0
        self.is_player = is_player
        self.uid = uid
        self.alive = True
        self.shell_vao = shell_vao
        
        self.w, self.l, self.h = 10, 18, 6
        
        c_hull = PLAYER_BODY if is_player else ENEMY_BODY
        c_top  = PLAYER_TOP if is_player else ENEMY_TOP
        c_turret = TURRET_BODY
        
        self.vao_hull = create_cube_vbo(ctx, prog, self.w, self.l, self.h, c_hull, False)
        self.vao_turret = create_cube_vbo(ctx, prog, 8, 10, 5, c_turret, True)
        self.vao_barrel = create_cube_vbo(ctx, prog, 2, 2, 20, BARREL_COLOR, True)
        
        self.cooldown = 0.0

    def update(self, dt, target_info):
        if not self.alive: return None
        
        fire_request = False
        
        if not self.is_player:
            player_pos = target_info
            diff = player_pos - self.pos
            target_aim = math.atan2(-diff.x, diff.y)
            
            target_rel = target_aim - self.hull_yaw
            angle_diff = target_rel - self.turret_rel_yaw
            while angle_diff > math.pi: angle_diff -= 2*math.pi
            while angle_diff < -math.pi: angle_diff += 2*math.pi
            self.turret_rel_yaw += angle_diff * 3.0 * dt
            
            dist = glm.length(diff)
            if dist > 80:
                hull_diff = target_aim - self.hull_yaw
                while hull_diff > math.pi: hull_diff -= 2*math.pi
                while hull_diff < -math.pi: hull_diff += 2*math.pi
                if abs(hull_diff) > 0.1: self.hull_yaw += hull_diff * 1.0 * dt
                self.speed += (40 - self.speed) * dt 
            else:
                self.speed *= 0.9 
            
            if abs(angle_diff) < 0.2 and dist < 150:
                fire_request = True
                
        else:
            cam_yaw_radians = target_info
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: self.speed += 50 * dt
            elif keys[pygame.K_s]: self.speed -= 50 * dt
            else: self.speed *= 0.9
            
            if abs(self.speed) > 0.5:
                turn = 2.0 * dt * (-1 if self.speed < 0 else 1)
                if keys[pygame.K_a]: self.hull_yaw += turn
                if keys[pygame.K_d]: self.hull_yaw -= turn
            
            target_world = cam_yaw_radians*-1 + math.pi
            target_rel = target_world - self.hull_yaw
            diff = target_rel - self.turret_rel_yaw
            while diff > math.pi: diff -= 2*math.pi
            while diff < -math.pi: diff += 2*math.pi
            self.turret_rel_yaw += diff * 5.0 * dt
            
            if pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
                fire_request = True

        self.pos.x += -math.sin(self.hull_yaw) * self.speed * dt
        self.pos.y += math.cos(self.hull_yaw) * self.speed * dt
        
        z_ground = get_z(self.pos.x, self.pos.y)
        z_f = get_z(self.pos.x - math.sin(self.hull_yaw)*5, self.pos.y + math.cos(self.hull_yaw)*5)
        z_b = get_z(self.pos.x + math.sin(self.hull_yaw)*5, self.pos.y - math.cos(self.hull_yaw)*5)
        target_pitch = math.atan2(z_f - z_b, 10)
        
        z_r = get_z(self.pos.x + math.cos(self.hull_yaw)*3, self.pos.y + math.sin(self.hull_yaw)*3)
        z_l = get_z(self.pos.x - math.cos(self.hull_yaw)*3, self.pos.y - math.sin(self.hull_yaw)*3)
        target_roll = math.atan2(z_l - z_r, 6)
        
        self.pos.z = z_ground + self.h/2
        self.pitch += (target_pitch - self.pitch) * 5 * dt
        self.roll += (target_roll - self.roll) * 5 * dt
        
        self.cooldown -= dt
        if fire_request and self.cooldown <= 0:
            return self.shoot()
        return None

    def shoot(self):
        self.cooldown = 1.5
        
        m_hull = glm.translate(glm.mat4(1), self.pos)
        m_hull = glm.rotate(m_hull, self.hull_yaw, glm.vec3(0,0,1))
        m_hull = glm.rotate(m_hull, self.pitch, glm.vec3(1,0,0))
        m_hull = glm.rotate(m_hull, self.roll, glm.vec3(0,1,0))
        
        m_turret = glm.translate(m_hull, glm.vec3(0, 0, self.h/2))
        m_turret = glm.rotate(m_turret, self.turret_rel_yaw, glm.vec3(0,0,1))
        
        m_barrel = glm.translate(m_turret, glm.vec3(0, 5, 2))
        m_barrel = glm.rotate(m_barrel, glm.radians(-90), glm.vec3(1,0,0))
        
        muzzle_local = glm.vec4(0, 0, 20, 1) 
        muzzle_world = m_barrel * muzzle_local
        start_pos = glm.vec3(muzzle_world)
        
        direction = glm.normalize(glm.vec3(m_barrel * glm.vec4(0,0,1,0)))
        direction.z += 0.2
        direction = glm.normalize(direction)
        
        return Shell(start_pos, direction, self.uid, self.shell_vao)

    def render(self, prog):
        if not self.alive: return
        
        m_hull = glm.translate(glm.mat4(1), self.pos)
        m_hull = glm.rotate(m_hull, self.hull_yaw, glm.vec3(0,0,1))
        m_hull = glm.rotate(m_hull, self.pitch, glm.vec3(1,0,0))
        m_hull = glm.rotate(m_hull, self.roll, glm.vec3(0,1,0))
        prog['m_model'].write(m_hull)
        self.vao_hull.render()
        
        m_turret = glm.translate(m_hull, glm.vec3(0, 0, self.h/2))
        m_turret = glm.rotate(m_turret, self.turret_rel_yaw, glm.vec3(0,0,1))
        prog['m_model'].write(m_turret)
        self.vao_turret.render()
        
        m_barrel = glm.translate(m_turret, glm.vec3(0, 5, 2))
        m_barrel = glm.rotate(m_barrel, glm.radians(-90), glm.vec3(1,0,0))
        prog['m_model'].write(m_barrel)
        self.vao_barrel.render()
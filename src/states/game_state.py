import pygame
import moderngl
import glm
import math
import random
import numpy as np

from src.framework.state_machine import State
from src.framework.ui import UIManager, TextButton, BattleCard
from src.settings import *
from src.graphics import get_program, create_cube_vbo
from src.terrain import create_terrain
from src.camera import Camera
from src.tank import Tank, RealTank
from src.naval import Naval
from src.infantry import Infantry
from src.projectiles import Explosion
from src.plane import Plane 
from src.fps_player import FPSPlayer
from src.resources import ResourceManager

class GameState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.ui = UIManager()
        
        self.ctx = manager.ctx
        self.prog = manager.prog
        
        self.terrain_vao, self.terrain_verts = create_terrain(self.ctx, self.prog)
        shared_shell_vao = create_cube_vbo(self.ctx, self.prog, 1.5, 3, 1.5, SHELL_COLOR, False)
        
        
        self.cam = Camera(self.prog)
        self.game_objects = []
        
        self.player = RealTank(self.ctx, self.prog, self.resource_mgr, "ft17_tank", 0, 0, is_player=True, uid=len(self.game_objects), shell_vao=shared_shell_vao)
        #player = Tank(ctx, prog, 0, 0, is_player=True, uid=len(game_objects), shell_vao=shared_shell_vao)

        self.enemies = []
        for i in range(2):
            ex, ey = random.randint(100, 300), random.randint(100, 300)
            tank = Tank(self.ctx, self.prog, ex, ey, is_player=False, uid=i+1, shell_vao=shared_shell_vao)
            self.enemies.append(tank)
            self.game_objects.append(tank)
        
        self.infantry_list = []
        for i in range(10):
            ix, iy = random.randint(-200, 200), random.randint(-200, 200)
            inf = Infantry(self.ctx, self.prog, ix, iy)
            self.infantry_list.append(inf)
            self.game_objects.append(inf)
        
        self.enemy_planes = []
        for i in range(2):
            # 生成在空中 (Z=80)
            px = random.randint(-200, 200)
            py = random.randint(-200, 200)
            e_plane = Plane(self.ctx, self.prog, px, py, 80, is_player=False, uid=100+i, shell_vao=shared_shell_vao)
            self.enemy_planes.append(e_plane)
            self.game_objects.append(e_plane)

        #player = Plane(ctx, prog, 0, 0, 100, is_player=True, uid=len(game_objects), shell_vao=shared_shell_vao)
        
        #player = FPSPlayer(ctx, prog, 0, 0, uid=len(game_objects), shell_vao=shared_shell_vao)

        self.shells = []
        self.explosions = []
        
        proj = glm.perspective(glm.radians(45), WIDTH/HEIGHT, 1.0, 1000.0)
        self.prog['m_proj'].write(proj)
        self.prog['sun_dir'].write(glm.vec3(0.2, 0.5, 0.8))
    
    def handle_event(self, event):
        self.ui.handle_event(event)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); exit()

    def update(self, dt):
        self.ctx.clear(0.45, 0.48, 0.52)
        
        #cam_yaw = cam.update(player.pos)
        
        # 更新玩家 (无论是坦克还是飞机)
        p_shell = self.player.update(dt, self.cam.yaw) # 注意：如果是飞机，第二个参数没用，但也传进去无妨
        
        # 更新逻辑
        if isinstance(self.player, FPSPlayer):
            # 直接把摄像机绑在玩家眼睛上
            self.cam.pos = self.player.pos
            self.cam.yaw = self.player.yaw
            self.cam.pitch = self.player.pitch
            # 手动更新 View 矩阵
            # 视线方向
            fwd = glm.vec3(
                -math.sin(self.cam.yaw) * math.cos(self.cam.pitch),
                math.cos(self.cam.yaw) * math.cos(self.cam.pitch),
                math.sin(self.cam.pitch)
            )
            view = glm.lookAt(self.cam.pos, self.cam.pos + fwd, glm.vec3(0,0,1))
            self.prog['m_view'].write(view)
            self.prog['view_pos'].write(cam.pos)
            
            # 更新玩家
            p_shell = self.player.update(dt) # FPSPlayer 不需要 target_info
        else:
            if isinstance(self.player, Plane):
                pass
                # 飞机模式：锁定跟随
                #cam.update_locked(player.pos, player.model_matrix)
            else:
                # 坦克模式：自由旋转
                self.cam.update_free(self.player.pos)
        
        # 飞机的 update 有点不同，如果是飞机作为player，需要修改一下调用
        if isinstance(self.player, Plane):
            # 飞机的 update 需要 target_info (AI用)，玩家用不到
            if self.player.handle_player_input(dt): # 如果按了空格返回True
                s = self.player.shoot()
                if s: self.shells.append(s)
            self.player.update(dt) # 物理更新
        else:
            # 坦克的 update
            p_shell = self.player.update(dt, self.cam.yaw)
            if p_shell: self.shells.append(p_shell)
        
        # 更新敌方飞机
        for plane in self.enemy_planes:
            target_type = ""
            
            if isinstance(self.player, Plane):
                target_type = "Air"
            else:
                target_type = "Surface"
            
            # 必须传入 player.pos 作为 target_info
            p_shell = plane.update(dt, target_type, self.player.pos) 
            if p_shell:
                self.shells.append(p_shell)
        
        for e in self.enemies:
            e_shell = e.update(dt, self.player.pos)
            if e_shell: self.shells.append(e_shell)
    
        for inf in self.infantry_list:
            inf.update(dt, self.player.pos)
            if inf.alive and self.player.alive:
                if glm.distance(self.player.pos, inf.pos) < 12.0:
                    inf.alive = False
                    self.explosions.append(Explosion(self.ctx, self.prog, inf.pos))
    
        # 修正炮弹命中检测逻辑 (支持打飞机)
        for s in self.shells[:]:
            res = s.update(dt)
            hit = False
            
            if res == "ground":
                self.explosions.append(Explosion(self.ctx, self.prog, s.pos))
                self.shells.remove(s)
                continue
                
            # 目标列表：玩家 + 敌人坦克 + 敌机
            all_targets = [self.player] + self.enemies + self.enemy_planes
            for t in all_targets:
                if t.alive and t.uid != s.owner_id:
                    # 飞机的碰撞半径稍微大一点
                    hit_radius = 15.0 if isinstance(t, Plane) else 10.0
                    if glm.distance(s.pos, t.pos) < hit_radius:
                        t.alive = False
                        self.explosions.append(Explosion(self.ctx, self.prog, t.pos))
                        self.shells.remove(s)
                        hit = True
                        break
            if hit: continue
            
            for inf in self.infantry_list:
                if inf.alive and glm.distance(s.pos, inf.pos) < 5.0:
                    inf.alive = False
                    self.explosions.append(Explosion(ctx, prog, inf.pos))
                    self.shells.remove(s)
                    hit = True
                    break
            
            if not s.alive and not hit:
                self.shells.remove(s)
    
        for ex in self.explosions[:]:
            ex.update(dt)
            if ex.life <= 0: self.explosions.remove(ex)
    
        self.prog['m_model'].write(glm.mat4(1))

    def draw(self):
        self.terrain_vao.render(moderngl.TRIANGLES, vertices=self.terrain_verts)
        
        if self.player.alive: self.player.render(self.prog)
        for e in self.enemies: e.render(self.prog)
        for plane in self.enemy_planes: plane.render(self.prog)
        for inf in self.infantry_list: inf.render(self.prog)
        
        for s in self.shells: s.render(self.prog)
        for ex in self.explosions: ex.render(self.prog)
        
        pygame.display.flip()
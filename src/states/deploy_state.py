# src/states/deploy_state.py
import pygame
import glm
import math
from src.framework.state_machine import State
from src.widgets.spawn_point_icon import SpawnPointIcon
from src.framework.ui import UIManager
from src.framework.ui_renderer import UIRenderer
from src.settings import *

class DeployState(State):
    def __init__(self, manager, game_world_data):
        super().__init__(manager)
        
        self.world = game_world_data
        
        self.deploy_cam_pos = glm.vec3(0, 0, 300)
        self.deploy_cam_yaw = 0
        self.deploy_cam_pitch = 1.57 # 90度 (垂直向下)
        
        self.ui_renderer = UIRenderer(manager.ctx, WIDTH, HEIGHT)
        self.ui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.ui = UIManager()
        
        # --- 创建重生点 ---
        self.spawn_points = [
            SpawnPointIcon("BASE", (0, -400, 0), is_base=True, team="blue"),
            SpawnPointIcon("A", (0, 0, 20), team="neutral"),
            SpawnPointIcon("B", (200, 200, 10), team="red"),
        ]
        
        # 默认选中基地
        self.selected_spawn = self.spawn_points[0]
        self.spawn_points[0].selected = True
        
        for sp in self.spawn_points:
            self.ui.add(sp)
            
        bar_y = HEIGHT - 80
        self.class_buttons = []
        classes = ["ASSAULT", "MEDIC", "SUPPORT", "SCOUT"]
        
        for i, cls_name in enumerate(classes):
            btn = TextButton(cls_name, WIDTH//2 - 200 + i*100, bar_y, font_size=20)
            
            btn.callback = lambda c=cls_name, b=btn: self.select_class(c, b)
            self.ui.add(btn)
            self.class_buttons.append(btn)
            
        self.current_class = "SCOUT"
        self.class_buttons[3].hovered = True # 借用 hovered 状态模拟选中高亮
        
        self.deploy_btn = TextButton("DEPLOY", WIDTH//2 - 40, HEIGHT - 130, font_size=32)
        self.deploy_btn.callback = self.on_deploy
        self.ui.add(self.deploy_btn)

    def select_class(self, class_name, btn_obj):
        self.current_class = class_name
        print(f"Selected Class: {class_name}")
        
    def on_deploy(self):
        print(f"Deploying as {self.current_class} at {self.selected_spawn.name}!")
        
        #from src.states.game_state import GameState
        #
        #self.world['player'].pos = glm.vec3(self.selected_spawn.world_pos)
        #self.world['player'].pos.z += 5 # 防止卡地里
        #self.world['player'].alive = True
        #self.world['player'].hp = 100
        #
        #self.manager.change_state(GameState, world_data=self.world)

    def handle_event(self, event):
        self.ui.handle_event(event)
        
        # 处理点击重生点
        if event.type == pygame.MOUSEBUTTONDOWN:
            for sp in self.spawn_points:
                if sp.hovered:
                    # 取消其他选中
                    for other in self.spawn_points: other.selected = False
                    # 选中当前
                    sp.selected = True
                    self.selected_spawn = sp

    def update(self, dt):
        # 可以在这里做摄像机缓慢平移效果 (Ambient movement)
        self.deploy_cam_pos.y += 5 * dt 
        if self.deploy_cam_pos.y > 100: self.deploy_cam_pos.y = -100

    def draw(self):
        ctx = self.manager.ctx
        prog = self.world['prog'] # 获取 Shader 程序
        
        # 渲染 3D 背景 (上帝视角)
        # -----------------------------------
        ctx.clear(*SKY_COLOR)
        ctx.enable(moderngl.DEPTH_TEST)
        
        # 构建上帝视角矩阵
        # LookAt: 从天上往下看 (0,0,0)
        view = glm.lookAt(self.deploy_cam_pos, glm.vec3(0,0,0), glm.vec3(0,1,0)) # Y轴为上(在顶视图里)
        prog['m_view'].write(view)
        prog['view_pos'].write(self.deploy_cam_pos)
        
        # 调用 World 里的渲染函数
        prog['m_model'].write(glm.mat4(1))
        self.world['terrain_vao'].render(moderngl.TRIANGLES, vertices=self.world['terrain_verts'])
        
        for e in self.world['enemies']: e.render(prog)
        
        
        # 渲染 UI (HUD)
        # -----------------------------------
        self.ui_surface.fill((0,0,0,0)) # 清空透明
        
        # 更新重生点图标的屏幕位置
        proj = glm.perspective(glm.radians(45), WIDTH/HEIGHT, 1.0, 1000.0)
        cam_matrix = proj * view
        
        for sp in self.spawn_points:
            sp.update_screen_pos(cam_matrix, (WIDTH, HEIGHT))
        
        # 绘制 UI 组件
        self.ui.draw(self.ui_surface)
        
        # 绘制顶部信息条 (Top Bar)
        
        # 蓝条
        pygame.draw.rect(self.ui_surface, (50, 150, 255), (WIDTH//2 - 300, 30, 250, 10))
        # 红条
        pygame.draw.rect(self.ui_surface, (255, 50, 50), (WIDTH//2 + 50, 30, 200, 10))
        # 分数
        score_font = get_font(30, bold=True)
        self.ui_surface.blit(score_font.render("245", True, WHITE), (WIDTH//2 - 50, 20))
        
        # 提交给 OpenGL
        self.ui_renderer.render(self.ui_surface)
        
        pygame.display.flip()
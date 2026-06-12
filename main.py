import pygame
import moderngl
from src.settings import *
from src.framework.state_machine import StateManager
from src.graphics import get_program
from src.states.menu_state import MenuState
#from src.states.deploy_state import DeployState
from src.resources import ResourceManager

def main():
    pygame.init()
    
    icon_image = pygame.image.load('assets\logo.png')
    pygame.display.set_icon(icon_image)
    pygame.display.set_caption("Battlefield 1 Bot Mod")
    
    display_info = pygame.display.Info()
    actual_screen_width = display_info.current_w
    actual_screen_height = display_info.current_h
    
    # 设置 OpenGL 
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    screen = pygame.display.set_mode((actual_screen_width, actual_screen_height), pygame.OPENGL | pygame.DOUBLEBUF |pygame.FULLSCREEN | pygame.SRCALPHA)
    
    # 创建 Context
    ctx = moderngl.create_context()
    ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
    
    prog = get_program(ctx)
    
    res_mgr = ResourceManager(ctx, prog, asset_path="assets")
    # Assets -> Materials -> Models
    res_mgr.load_assets_xml("assets.xml")
    res_mgr.load_materials_xml("materials.xml")
    res_mgr.load_vehicles_xml("vehicles.xml")
    # 将加载好的 Mesh 存入字典供游戏使用
    models_dict = res_mgr.load_models_xml("model.xml")
    
    # 初始化状态机，进入菜单状态
    manager = StateManager(ctx, prog, res_mgr, screen)
    manager.change_state(MenuState)
    
    clock = pygame.time.Clock()
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            manager.handle_event(event)
            
        manager.update(dt)
        manager.draw()

if __name__ == "__main__":
    main()
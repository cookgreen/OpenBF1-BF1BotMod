import pygame
import random
from src.framework.state_machine import State
from src.framework.ui import UIManager, TextButton, BattleCard
from src.framework.ui_renderer import UIRenderer
from src.widgets.text_button_menu import TextButtonMenu
from src.widgets.battle_card_menu import BattleCardMenu
from src.widgets.panel import Panel
from src.states.game_state import GameState
from src.widgets.static_image import StaticImage, StaticText
from src.settings import *

class MenuState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.ui = UIManager()
        self.ui_renderer = UIRenderer(manager.ctx, WIDTH, HEIGHT)
        self.ui_surface = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
        
        self.logo = pygame.transform.scale(self.resource_mgr.images["logo.png"], (63, 63))
        self.logo_text = pygame.transform.scale(self.resource_mgr.images["logo-text.png"], (200, 63))
        
        self.home_page_first_card_images = ["card1.jpg", "card10.jpg", "card12.jpg"]
        self.home_page_second_card_images = ["card2.jpg", "card5.jpg", "card8.jpg", "card9.jpg", "card11.jpg"]
        
        # --- 布局 ---
        # 顶部导航
        self.top_menu = TextButtonMenu(80, 50, 800)
        self.top_menu.add_menu_item("HOME", callback=self.top_menu_home)
        self.top_menu.add_menu_item("CUSTOM BATTLE", callback=self.top_menu_custom)
        self.top_menu.add_menu_item("TOOL", callback=self.top_menu_tool)
        self.ui.add(self.top_menu)
        
        
        self.main_panel = Panel(80, 130, WIDTH, HEIGHT)
        text = StaticText(0, 0, "Good evening, Commander.", 36, WHITE)
        card_menu = BattleCardMenu(0, 70, 350)
        card_menu.add_new_card("ALL MODES", "ALL MAPS", 550, self.resource_mgr.images[random.choice(self.home_page_first_card_images)])
        card_menu.add_new_card("QUICK MATCH", "ALL MAPS", 400, self.resource_mgr.images[random.choice(self.home_page_second_card_images)])
        self.main_panel.add_new_widget(text)
        self.main_panel.add_new_widget(card_menu)
        
        self.ui.add(self.main_panel)

        # 背景图
        self.bg_surf = pygame.Surface((WIDTH, HEIGHT))
        self.bg_surf.fill((255, 255, 255)) 
                                
        #pygame.mixer.music.load(self.resource_mgr.music["btlfld1_menu"])
        #try: 
        #    pygame.mixer.music.play(loops=-1)
        #except Exception as e: 
        #    print(f"Menu music failed: {e}")
    
    def top_menu_home(self):
        self.resource_mgr.sound["UI_SliderTick_Wave"].play()
        
        self.main_panel.clear_widgets()
        text = StaticText(0, 0, "Good evening, Commander.", 36, WHITE)
        card_menu = BattleCardMenu(0, 70, 350)
        card_menu.add_new_card("ALL MODES", "ALL MAPS", 550, self.resource_mgr.images[random.choice(self.home_page_first_card_images)])
        card_menu.add_new_card("QUICK MATCH", "ALL MAPS", 400, self.resource_mgr.images[random.choice(self.home_page_second_card_images)])
        self.main_panel.add_new_widget(text)
        self.main_panel.add_new_widget(card_menu)
    
    def top_menu_custom(self):
        self.resource_mgr.sound["UI_SliderTick_Wave"].play()
        
        self.main_panel.clear_widgets()
        card_menu = BattleCardMenu(0, 0, 350)
        card_menu.add_new_card("CUSTOM BATTLE", "ALL MAP", 400, self.resource_mgr.images["card3.jpg"], self.battle_card_start_game)
        self.main_panel.add_new_widget(card_menu)
    
    def top_menu_tool(self):
        self.resource_mgr.sound["UI_SliderTick_Wave"].play()
        
        self.main_panel.clear_widgets()
        card_menu = BattleCardMenu(0, 0, 350)
        card_menu.add_new_card("TERRAIN EDITIOR", "EDIT THE MAP", 400, self.resource_mgr.images["card4.jpg"])
        self.main_panel.add_new_widget(card_menu)
    
    def battle_card_start_game(self):
        print("ENTER!")
        self.manager.change_state(GameState)
    
    def handle_event(self, event):
        self.ui.handle_event(event)

    def update(self, dt):
        pass

    def draw(self):
        screen = self.manager.screen
        self.ui_surface.blit(self.resource_mgr.images["default-background.png"], (0, 0))
        
        self.ui_surface.blit(self.logo, (WIDTH-310, 30))
        self.ui_surface.blit(self.logo_text, (WIDTH-230, 30))
        
        self.ui.draw(self.ui_surface)
        
        self.manager.ctx.clear(0, 0, 0)
        
        self.ui_renderer.render(self.ui_surface)
        
        pygame.display.flip()
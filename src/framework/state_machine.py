class State:
    """ 状态基类 """
    def __init__(self, manager):
        self.manager = manager
        self.ctx = manager.ctx # 传递 OpenGL 上下文
        self.prog = manager.prog
        self.resource_mgr = manager.resource_mgr

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass

class StateManager:
    """ 状态管理器：持有当前状态 """
    def __init__(self, ctx, prog, resource_mgr, screen):
        self.ctx = ctx
        self.prog =  prog
        self.resource_mgr = resource_mgr
        self.screen = screen
        self.current_state = None

    def change_state(self, new_state_class):
        self.current_state = new_state_class(self)

    def handle_event(self, event):
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, dt):
        if self.current_state:
            self.current_state.update(dt)

    def draw(self):
        if self.current_state:
            self.current_state.draw()
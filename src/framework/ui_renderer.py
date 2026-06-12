import pygame
import moderngl
import numpy as np

class UIRenderer:
    def __init__(self, ctx, width, height):
        self.ctx = ctx
        self.width = width
        self.height = height
        
        # --- 1. UI Shader (极简版) ---
        # 只需要把纹理贴在屏幕上，不需要光照、矩阵
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    v_uv = in_uv;
                    // 直接映射到屏幕坐标 (-1 到 1)
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D ui_texture;
                in vec2 v_uv;
                out vec4 f_color;
                void main() {
                    f_color = texture(ui_texture, v_uv);
                }
            '''
        )
        
        # --- 2. 全屏四边形 (Full Screen Quad) ---
        # 坐标: x, y (范围 -1 到 1)
        # UV: u, v (范围 0 到 1)
        # 注意：Pygame 的图像原点在左上角，OpenGL 纹理原点在左下角
        # 所以这里的 UV y轴可能需要翻转，或者在上传时处理
        vertices = np.array([
            # x, y, u, v
            -1.0,  1.0, 0.0, 0.0, # 左上
            -1.0, -1.0, 0.0, 1.0, # 左下
             1.0,  1.0, 1.0, 0.0, # 右上
             1.0, -1.0, 1.0, 1.0, # 右下
        ], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog, 
            [(self.vbo, '2f 2f', 'in_vert', 'in_uv')]
        )
        
        # --- 3. 创建空纹理对象 ---
        # 预先分配显存，每帧只需要 write 数据，不需要重新创建 texture (性能关键!)
        self.texture = self.ctx.texture((width, height), 4)
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST) # 保持像素清晰，不模糊
        self.texture.swizzle = 'BGRA' # Pygame 默认是 BGRA 顺序，这里纠正为 RGBA

    def render(self, pygame_surface):
        """
        将 Pygame Surface 渲染到 OpenGL 窗口上
        """
        # 1. 获取像素数据 (极速)
        # Pygame surface 数据在 CPU，我们需要拿到 bytes
        texture_data = pygame_surface.get_view('1')
        
        # 2. 写入显存
        self.texture.write(texture_data)
        
        # 3. 渲染
        self.ctx.enable(moderngl.BLEND) # 开启混合，支持 UI 透明背景
        self.texture.use(location=0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        self.ctx.disable(moderngl.BLEND)
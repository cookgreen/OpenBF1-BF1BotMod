# src/graphics.py
import numpy as np
import moderngl

# --- Shader ---
VERTEX_SHADER = '''
    #version 330
    uniform mat4 m_proj;
    uniform mat4 m_view;
    uniform mat4 m_model;

    in vec3 in_position;
    in vec3 in_normal;
    in vec2 in_texcoord; // 纹理坐标
    in vec3 in_color;    // 顶点颜色

    out vec3 v_pos;
    out vec3 v_normal;
    out vec2 v_uv;
    out vec3 v_color;

    void main() {
        vec4 world_pos = m_model * vec4(in_position, 1.0);
        v_pos = world_pos.xyz;
        mat3 normal_matrix = transpose(inverse(mat3(m_model)));
        v_normal = normalize(normal_matrix * in_normal);
        
        v_uv = in_texcoord;
        v_color = in_color;
        
        gl_Position = m_proj * m_view * world_pos;
    }
'''

FRAGMENT_SHADER = '''
    #version 330
    in vec3 v_pos;
    in vec3 v_normal;
    in vec2 v_uv;
    in vec3 v_color;

    out vec4 f_color;

    uniform vec3 sun_dir;
    uniform vec3 view_pos;
    
    // 纹理
    uniform sampler2D tex_diffuse;
    uniform sampler2D tex_normal;
    uniform sampler2D tex_specular;
    uniform bool use_texture; // 颜色贴图
    uniform bool use_normal_map; // 法线贴图
    uniform bool use_specular_map; // 高光贴图

    void main() {
        // 光照
        vec3 norm = normalize(v_normal);
        vec3 light = normalize(sun_dir);
        float diff = max(dot(norm, light), 0.2);
        
        // 核心混合逻辑：如果有纹理，就用纹理；否则用顶点颜色
        vec3 object_color = v_color;
        if (use_texture) {
            // 有贴图：采样纹理 * 顶点颜色(通常是白色)
            vec4 tex_col = texture(tex_diffuse, v_uv);
            object_color = tex_col.rgb * v_color; 
        } else {
            // 无贴图：直接用顶点颜色 (比如飞机的红色、地形的褐色)
            object_color = v_color;
        }
        // 高光反射
        vec3 view_dir = normalize(view_pos - v_pos);
        vec3 reflect_dir = reflect(-light, norm);
        
        float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32);
        vec3 specular = vec3(0.4) * spec; 

        vec3 final_color = diff * object_color;
        f_color = vec4(final_color, 1.0);
    }
'''

def get_program(ctx):
    return ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

# --- 立方体生成器 ---
def create_cube_vbo(ctx, prog, w, l, h, color, pivot_bottom=False):
    hw, hl = float(w) / 2.0, float(l) / 2.0
    z_min = 0.0 if pivot_bottom else float(-h) / 2.0
    z_max = float(h) if pivot_bottom else float(h) / 2.0
    
    # 颜色归一化
    cr, cg, cb = float(color[0])/255.0, float(color[1])/255.0, float(color[2])/255.0
    
    # 8个顶点 (元组)
    p0 = (-hw, hl, z_max); p1 = (hw, hl, z_max)
    p2 = (hw, -hl, z_max); p3 = (-hw, -hl, z_max)
    p4 = (-hw, hl, z_min); p5 = (hw, hl, z_min)
    p6 = (hw, -hl, z_min); p7 = (-hw, -hl, z_min)
    
    data = []

    def add_face(a, b, c, d, nx, ny, nz):
        # 三角形 1: a-b-c
        # 顶点 a
        data.extend([a[0], a[1], a[2], nx, ny, nz, 0.0, 0.0, cr, cg, cb])
        # 顶点 b
        data.extend([b[0], b[1], b[2], nx, ny, nz, 0.0, 0.0, cr, cg, cb])
        # 顶点 c
        data.extend([c[0], c[1], c[2], nx, ny, nz, 0.0, 0.0, cr, cg, cb])
        
        # 三角形 2: a-c-d
        # 顶点 a
        data.extend([a[0], a[1], a[2], nx, ny, nz, 0.0, 0.0, cr, cg, cb])
        # 顶点 c
        data.extend([c[0], c[1], c[2], nx, ny, nz, 0.0, 0.0, cr, cg, cb])
        # 顶点 d
        data.extend([d[0], d[1], d[2], nx, ny, nz, 0.0, 0.0, cr, cg, cb])

    # 顶面 (0, 0, 1)
    add_face(p0, p3, p2, p1, 0.0, 0.0, 1.0)
    # 底面 (0, 0, -1)
    add_face(p7, p4, p5, p6, 0.0, 0.0, -1.0)
    # 前面 (0, 1, 0)
    add_face(p4, p1, p5, p0, 0.0, 1.0, 0.0)
    # 后面 (0, -1, 0)
    add_face(p3, p6, p2, p7, 0.0, -1.0, 0.0)
    # 右面 (1, 0, 0)
    add_face(p1, p2, p6, p5, 1.0, 0.0, 0.0)
    # 左面 (-1, 0, 0)
    add_face(p0, p4, p7, p3, -1.0, 0.0, 0.0)
    
    vbo_data = np.array(data, dtype='f4')
    
    vbo = ctx.buffer(vbo_data.tobytes())
    return ctx.vertex_array(prog, [(vbo, '3f 3f 2f 3f', 'in_position', 'in_normal', 'in_texcoord', 'in_color')])
import math
import numpy as np
import moderngl

def get_z(x, y):
    return math.sin(x*0.02)*math.cos(y*0.02)*10 + math.sin(x*0.05 + y*0.05)*5

def create_terrain(ctx, prog):
    size, step = 400, 10
    data = []
    c_dark = [0.3, 0.2, 0.1]; c_light = [0.4, 0.25, 0.15]
    
    # UV 占位符 (0, 0)
    uv = [0, 0]
    
    for x in range(-size, size, step):
        for y in range(-size, size, step):
            z1 = get_z(x, y); z2 = get_z(x+step, y); z3 = get_z(x, y+step); z4 = get_z(x+step, y+step)
            n = [0, 0, 1]
            c = c_light if (x+y)%(step*2)==0 else c_dark
            
            data.extend([x,y,z1] + n + uv + c)
            data.extend([x+step,y,z2] + n + uv + c)
            data.extend([x,y+step,z3] + n + uv + c)
            
            data.extend([x+step,y,z2] + n + uv + c)
            data.extend([x+step,y+step,z4] + n + uv + c)
            data.extend([x,y+step,z3] + n + uv + c)
            
    vbo = ctx.buffer(np.array(data, dtype='f4').tobytes())
    return ctx.vertex_array(prog, [(vbo, '3f 3f 2f 3f', 'in_position', 'in_normal', 'in_texcoord', 'in_color')]), len(data)//11 
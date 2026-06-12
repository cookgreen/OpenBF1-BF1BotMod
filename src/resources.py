# src/resources.py
import os
import xml.etree.ElementTree as ET
import pygame
import numpy as np
from PIL import Image # 用于加载纹理

class Mesh:
    def __init__(self, ctx, program, vao, texture_diffuse, texture_normal=None, texture_specular=None):
        self.ctx = ctx
        self.prog = program
        self.vao = vao
        self.tex_d = texture_diffuse
        self.tex_n = texture_normal
        self.tex_s = texture_specular

    def render(self):
        # 开启纹理模式
        self.prog['use_texture'].value = True
        
        if self.tex_d:
            self.tex_d.use(location=0)
            self.prog['tex_diffuse'].value = 0
        
        #if self.tex_n:
        #    self.tex_n.use(location=1)
        #    self.prog['tex_normal'].value = 1
        #    self.prog['use_normal_map'].value = True
        #else:
        #    self.prog['use_normal_map'].value = False
        #
        #if self.tex_s:
        #    self.tex_s.use(location=2)
        #    self.prog['tex_specular'].value = 2
        #    self.prog['use_specular_map'].value = True
        #else:
        #    self.prog['use_specular_map'].value = False

        self.vao.render()

class ResourceManager:
    def __init__(self, ctx, prog, asset_path="./"):
        self.ctx = ctx
        self.prog = prog
        self.asset_path = asset_path
        self.data_path = "./data"
        
        self.images = {} # key: Image Object
        self.sound = {} # key: Sound Object
        self.music = {} # key: Music Object
        self.fonts = {} # key: Music Object
        self.textures = {} # key: Texture Object
        self.meshes = {}   # key: Mesh Object (raw data)
        self.materials = {} # key: Material Config
        self.vehicles =  {}
        
        # 预设路径
        self.path_img = "./assets"
        self.path_snd = "./sound"
        self.path_fnt = "./fonts"
        self.path_msc = "./music"
        self.path_tex = "./textures"
        self.path_mdl = "./models"

    def load_assets_xml(self, xml_file):
        tree = ET.parse(os.path.join(self.data_path, xml_file))
        root = tree.getroot()
        
        # 预加载所有纹理
        for asset in root.findall("Asset"):
            if asset.get("type") == "Image":
                key = asset.get("key")
                filename = asset.get("file")
                self.load_image(key, filename)
            elif asset.get("type") == "Sound":
                key = asset.get("key")
                filename = asset.get("file")
                self.load_sound(key, filename)
            elif asset.get("type") == "Music":
                key = asset.get("key")
                filename = asset.get("file")
                self.load_music(key, filename)
            elif asset.get("type") == "Font":
                key = asset.get("key")
                filename = asset.get("file")
                self.load_font(key, filename)
            elif asset.get("type") == "Texture":
                key = asset.get("key")
                filename = asset.get("file")
                self.load_texture(key, filename)
            elif asset.get("type") == "Model":
                key = asset.get("key")
                filename = asset.get("file")
                self.load_obj(key, filename)
        
        #print(self.images)
        #print(self.sound)
        #print(self.music)
        #print(self.textures)
        #print(self.materials)

    def load_image(self, key, filename, scale_to=None):
        """Loads, optionally scales, and converts an image."""
        filepath = os.path.join(self.path_img, filename)
        try:
            image = pygame.image.load(filepath)
            
            if scale_to: image = pygame.transform.scale(image, scale_to)
            
            if image.get_alpha() is not None or '.png' in filename.lower(): 
                image = image.convert_alpha()
            else:
                image = image.convert()
            self.images[key] = image
            print(f"[Resource] Loaded image: {filename}")
            return image
        except pygame.error as e:
            print(f"  Warning: Could not load image {filepath}: {e}")

    def load_sound(self, key, filename, volume=1):
        """Loads a sound file, handling potential errors."""
        filepath = os.path.join(self.path_snd, filename)
        
        if not filepath:
            print(f"  Warning: Sound file '{filename}' with path '{filepath}' not found in any search path.")
            return
            
        if not os.path.exists(filepath): 
            print(f"  Warning: Sound file not found: {filepath}")
        try: 
            sound = pygame.mixer.Sound(filepath); 
            sound.set_volume(volume); 
            print(f"[Resource] Loaded sound: {filename}"); 
            self.sound[key] = sound
        except pygame.error as e: 
            print(f"  Warning: Could not load sound {filepath}: {e}");

    def load_music(self, key, filename):
        """Loads a sound file, handling potential errors."""
        filepath = os.path.join(self.path_msc, filename)
        
        if not filepath:
            print(f"  Warning: Sound file '{filename}' with path '{filepath}' not found in any search path.")
            return
            
        if not os.path.exists(filepath): 
            print(f"  Warning: Sound file not found: {filepath}");
        try: 
            print(f"[Resource] Loaded Music: {filename}"); 
            self.music[key] = filepath
        except pygame.error as e: 
            print(f"  Warning: Could not load sound {filepath}: {e}");

    def load_font(self, key, filename):
        """Loads a sound file, handling potential errors."""
        filepath = os.path.join(self.path_fnt, filename)
        
        if not filepath:
            print(f"  Warning: font file '{filename}' with path '{filepath}' not found in any search path.")
            return
            
        if not os.path.exists(filepath): 
            print(f"  Warning: font file not found: {filepath}");
        try: 
            print(f"[Resource] Loaded Font: {filename}"); 
            self.fonts[key] = filepath
        except pygame.error as e: 
            print(f"  Warning: Could not load font {filepath}: {e}");
    
    def load_materials_xml(self, xml_file):
        tree = ET.parse(os.path.join(self.data_path, xml_file))
        root = tree.getroot()
        
        for mat in root.findall("Material"):
            mat_id = mat.get("id")
            mat_data = {"Diffuse": None, "NormalMap": None, "Specular": None}
            
            textures = mat.find("Textures")
            if textures is not None:
                for tex in textures.findall("Texture"):
                    slot = tex.get("key") # Diffuse, NormalMap...
                    file_key = tex.get("file")
                    if file_key in self.textures:
                        mat_data[slot] = self.textures[file_key]
            
            self.materials[mat_id] = mat_data

    def load_models_xml(self, xml_file):
        self.built_meshes = {}
        tree = ET.parse(os.path.join(self.data_path, xml_file))
        root = tree.getroot()
        
        for model in root.findall("Model"):
            model_id = model.get("id")
            obj_key = model.get("file")
            mat_id = model.get("material")
            
            if obj_key in self.meshes and mat_id in self.materials:
                # 原始 OBJ 数据: Pos(3) + Norm(3) + UV(2)
                raw_data = np.frombuffer(self.meshes[obj_key], dtype='f4')
                vertex_count = len(raw_data) // 8
                
                # 插入 Color 数据
                new_data = []
                for i in range(vertex_count):
                    base = i * 8
                    new_data.extend(raw_data[base : base+8])
                    new_data.extend([1.0, 1.0, 1.0])
                
                vbo_data = np.array(new_data, dtype='f4').tobytes()
                mat = self.materials[mat_id]
                
                vbo = self.ctx.buffer(vbo_data)
                vao = self.ctx.vertex_array(
                    self.prog, 
                    [(vbo, '3f 3f 2f 3f', 'in_position', 'in_normal', 'in_texcoord', 'in_color')]
                )
                
                mesh = Mesh(self.ctx, self.prog, vao, mat["Diffuse"], mat["NormalMap"], mat["Specular"])
                self.built_meshes[model_id] = mesh
                
        #return built_meshes

    def load_texture(self, key, filename):
        path = os.path.join(self.path_tex, filename)
        try:
            img = Image.open(path).convert('RGBA')
            
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            texture = self.ctx.texture(img.size, 4, img.tobytes())
            texture.build_mipmaps()
            texture.anisotropy = 32.0
            self.textures[key] = texture
            print(f"[Resource] Loaded texture: {key}")
        except Exception as e:
            print(f"[Error] Failed to load texture {filename}: {e}")
            
    def load_vehicles_xml(self, xml_file):
        filepath = os.path.join(self.data_path, xml_file)
        if not os.path.exists(filepath):
            print(f"[Error] Vehicle XML not found: {filepath}")
            return {}

        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            for vehicle_node in root.findall("Vehicle"):
                v_id = vehicle_node.get("id")
                v_data = {
                    "name": vehicle_node.get("name"),
                    "components": {},
                    "physics": {},
                    "combat": {}
                }

                comp_root = vehicle_node.find("VehicleComponents")
                if comp_root is not None:
                    for comp in comp_root.findall("VehicleComponent"):
                        c_type = comp.get("Type")
                        c_model = comp.get("model")
                        
                        comp_data = {"model": c_model, "params": {}}

                        param_list = comp.find("VehicleComponentParametersList")
                        if param_list is not None:
                            for params in param_list.findall("VehicleComponentParameters"):
                                p_name = params.get("Name")
                                p_values = {}
                                for p in params.findall("VehiclePhysicsParameter"):
                                    key = p.get("Key")
                                    val = self._try_parse_number(p.text)
                                    p_values[key] = val
                                comp_data["params"][p_name] = p_values
                        
                        v_data["components"][c_type] = comp_data

                phys_root = vehicle_node.find("VehiclePhysics")
                if phys_root is not None:
                    phys_list = phys_root.find("VehiclePhysicsParametersList")
                    if phys_list is not None:
                        for params in phys_list.findall("VehiclePhysicsParameters"):
                            p_name = params.get("Name")
                            p_values = {}
                            for p in params.findall("VehiclePhysicsParameter"):
                                key = p.get("Key")
                                val = self._try_parse_number(p.text)
                                p_values[key] = val
                            v_data["physics"][p_name] = p_values

                combat_root = vehicle_node.find("VehicleCombat")
                if combat_root is not None:
                    combat_params = combat_root.find("VehicleCombatParameters")
                    if combat_params is not None:
                        for p in combat_params.findall("VehicleCombatParameter"):
                            key = p.get("key")
                            val = self._try_parse_number(p.text)
                            v_data["combat"][key] = val

                self.vehicles[v_id] = v_data
                print(f"[Resource] Loaded vehicle: {v_id}")

        except ET.ParseError as e:
            print(f"[Error] XML Parsing Failed: {e}")

    def _try_parse_number(self, text):
        if not text: return 0
        try:
            val = float(text)
            if val.is_integer():
                return int(val)
            return val
        except ValueError:
            return text # 转换失败就返回原字符串

    def load_obj(self, key, filename):
        path = os.path.join(self.path_mdl, filename)
        vertices = []
        normals = []
        texcoords = []
        faces = []

        try:
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('#'): continue
                    vals = line.split()
                    if not vals: continue
                    
                    if vals[0] == 'v':
                        vertices.append(list(map(float, vals[1:4])))
                    elif vals[0] == 'vn':
                        normals.append(list(map(float, vals[1:4])))
                    elif vals[0] == 'vt':
                        texcoords.append(list(map(float, vals[1:3])))
                    elif vals[0] == 'f':
                        face = []
                        for v in vals[1:]:
                            w = v.split('/')
                            vi = int(w[0]) - 1
                            vti = int(w[1]) - 1 if len(w) > 1 and w[1] else 0
                            vni = int(w[2]) - 1 if len(w) > 2 and w[2] else 0
                            face.append((vi, vti, vni))
                        
                        if len(face) == 3:
                            faces.append(face)
                        elif len(face) == 4:
                            faces.append([face[0], face[1], face[2]])
                            faces.append([face[0], face[2], face[3]])

            data = []
            for face in faces:
                for vi, vti, vni in face:
                    # Position (x, y, z)
                    data.extend(vertices[vi])
                    # Normal (nx, ny, nz)
                    if normals and vni < len(normals):
                        data.extend(normals[vni])
                    else:
                        data.extend([0, 0, 1])
                    # UV (u, v)
                    if texcoords and vti < len(texcoords):
                        data.extend(texcoords[vti])
                    else:
                        data.extend([0, 0])
            
            self.meshes[key] = np.array(data, dtype='f4').tobytes()
            print(f"[Resource] Loaded model: {key}")
            
        except Exception as e:
            print(f"[Error] Failed to load model {filename}: {e}")
            
    def get_model(self, key):
        return self.built_meshes.get(key)
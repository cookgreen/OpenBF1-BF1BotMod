#version 330
in vec3 v_normal;
in vec3 v_color;
in vec3 v_pos;
out vec4 f_color;
uniform vec3 sun_dir;
uniform vec3 view_pos;

void main() {
    float ambient = 0.3;
    vec3 norm = normalize(v_normal);
    vec3 light = normalize(sun_dir);
    float diff = max(dot(norm, light), 0.0);
    
    vec3 viewDir = normalize(view_pos - v_pos);
    vec3 reflectDir = reflect(-light, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = vec3(0.3) * spec; 
    
    vec3 result = (ambient + diff) * v_color + specular;
    f_color = vec4(result, 1.0);
}
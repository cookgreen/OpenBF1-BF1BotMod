#version 330
uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
in vec3 in_position;
in vec3 in_normal;
in vec3 in_color;
out vec3 v_normal;
out vec3 v_color;
out vec3 v_pos;
void main() {
    vec4 world_pos = m_model * vec4(in_position, 1.0);
    v_pos = world_pos.xyz;
    mat3 normal_matrix = transpose(inverse(mat3(m_model)));
    v_normal = normalize(normal_matrix * in_normal);
    v_color = in_color;
    gl_Position = m_proj * m_view * world_pos;
}
#version 130

in vec4 v_Position;
in vec3 v_Normal;
in vec2 v_texCoord;

struct Material 
{
	vec3 specular;
	float shininess;
};

struct PointLight 
{
	vec3 position;
	vec3 color;
	float ambient_strength;
	float diffuse_strength;
	float specular_strength;

	// Attenuation.
	float constant;
	float linear;
	float quadratic;
};

uniform Material u_Material;
uniform PointLight u_PointLight;
uniform vec3 u_ViewPos;
uniform sampler2D u_texture;

void main()
{
	// Texture
	vec4 tex_color = texture(u_texture, v_texCoord);

	// Light
    vec3 light_direction = normalize(u_PointLight.position - v_Position.xyz);
	vec3 norm = normalize(v_Normal);
	vec3 view_direction = normalize(u_ViewPos - v_Position.xyz);
	vec3 reflect_direction = reflect(-light_direction, norm);

    // Ambient
	vec3 ambient = u_PointLight.ambient_strength * u_PointLight.color * tex_color.rgb;

    // Difuse
	float diff = max(dot(norm, -light_direction), 0.0);
	vec3 diffuse = diff * u_PointLight.diffuse_strength * u_PointLight.color * tex_color.rgb;

    // Specular
	float spec = pow(max(dot(view_direction, reflect_direction), 0.0), u_Material.shininess * 128);
	vec3 specular = u_PointLight.specular_strength * spec * u_PointLight.color * u_Material.specular;

    // Attenuation
	float distance = length(u_PointLight.position - v_Position.xyz);
	float attenuation = 1.0 / (u_PointLight.constant + u_PointLight.linear * distance + u_PointLight.quadratic * distance * distance);

	vec3 result = (ambient + diffuse + specular) * attenuation;
    gl_FragColor = vec4(result, 1.0);
};
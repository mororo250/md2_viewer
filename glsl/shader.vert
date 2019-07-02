 #version 130

out vec4 v_Position;
out vec3 v_Normal;
out vec2 v_texCoord;

void main()
{
   gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
   v_Position = gl_Vertex;
   v_Normal = gl_NormalMatrix * gl_Normal;
   v_texCoord = gl_MultiTexCoord0.st;
};

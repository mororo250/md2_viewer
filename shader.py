from OpenGL.GL import *
from enum import Enum

class Shader:
    def __init__(self):
        self.__shader_program = 0
        self.__createShader()
       
    def __compileShader(self, source, shader_type):
        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, source)
        glCompileShader(shader_id)

        # Test compilation.
        if not glGetShaderiv(shader_id, GL_COMPILE_STATUS):
            info = glGetShaderInfoLog(shader_id) 
            print("Shader complation file")
            print(info)
        return shader_id

    def __createShader(self):
        self.__shader_program = glCreateProgram()
        
        vertex_id = self.__compileShader(open("glsl/shader.vert", "r"), GL_VERTEX_SHADER)
        frag_id = self.__compileShader(open("glsl/shader.frag", "r"), GL_FRAGMENT_SHADER)

        glAttachShader(self.__shader_program, vertex_id)
        glAttachShader(self.__shader_program, frag_id)
        glLinkProgram(self.__shader_program)

        glDeleteShader(vertex_id)
        glDeleteShader(frag_id)

        if not glGetProgramiv(self.__shader_program, GL_LINK_STATUS):
            info = glGetProgramInfoLog(self.__shader_program)
            print("Link error:")
            print(info)
    
    def bind(self):
        glUseProgram(self.__shader_program)
    
    @staticmethod
    def unbind():
        glUseProgram(0)

    def GetProgram(self):
        return self.__shader_program
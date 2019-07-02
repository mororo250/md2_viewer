# Opengl Imports
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from pcx import *

class white_texture:
    width = 1
    height = 1
    pixels = [255, 255, 255, 255]

class texture:
    def __init__(self, file_name = "white texture"):
        if ".pcx" in file_name or ".PCX" in file_name:
            new_texture = pcx_loader()
            if new_texture.load_texture_file(file_name, True) != True:
                raise Exception("Texture can not be loaded")
        elif file_name == "white texture":
            new_texture = white_texture()
        else:
            raise Exception("File has not an acceptable type")
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, new_texture.width, new_texture.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, new_texture.pixels )

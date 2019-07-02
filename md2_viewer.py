# OpenGl
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

# Others
import argparse
import sys

# In files
from pre_calculated_md2 import *
from MD2_loader import *
from pcx import *
from shader import *
from texture import *
from timer import *

DINAMIC = 0
STATIC = 1

class MasterRender:
    def __init__(self):
        self.camera_pos = [0.0, 0.0, -3.5]
        self.light_pos = [0.0, 2.0, -1.5]

        # Argments:
        parser = argparse.ArgumentParser(description = "Opengl library for view .md2 file")
        parser.add_argument("-f", "--filepath_md2", nargs = '?', type = str, help = "file path for md2 file")
        parser.add_argument("-t", "--texture", nargs = '?', type = str, help = "file path for texture file, it's supported .pcx and .bmp files")
        parser.add_argument("-skin", nargs = '?', type = int, help = "index of skin to be used")
        parser.add_argument("-s", "--state", nargs = '?', default = False , type = bool, help = "if is true only the first frame will be rendered")

        args = parser.parse_args()

        # Glut context
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(640, 400)
        glutCreateWindow("MD2 Model Loader")

        glClearColor(0.,0.,0.,1.)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        self.md2_models = []
        # Print configuration and load md2_models.
        if args.filepath_md2 is not None:
            print("Md2 file: %s" % args.filepath_md2)
            self.md2_models.append(md2_model(args.filepath_md2))
            if args.texture is not None:
                print("texture file: %s" % args.texture)
                self.md2_models[0].load_texture(args.texture)
            elif args.skin is not None:
                self.md2_models[0].load_skin(args.skin)
        else:
            print("Open default scene")
            self.md2_models.append(md2_model("models/ogros.md2"))
            self.md2_models[0].load_texture("models/igdosh.pcx")
            self.md2_models.append(md2_model("models/Weapon.md2"))
            self.md2_models[1].load_texture("models/Weapon.pcx")
            if args.texture is not None or args.skin is not None:
                raise argparse.ArgumentTypeError("You need to specify Md2 file to specify texture")

        if args.state == True:
            self.state = STATIC
        else:
            self.state = DINAMIC
            for aux in self.md2_models:
                if  aux.header.num_frames == 1:
                    print("State set to static since there is just one frame in the md2 file")
                    self.state = STATIC
                    break

        for aux in self.md2_models:
            self.__setup_model(aux)

        glDisable( GL_LIGHTING )

        glMatrixMode(GL_PROJECTION)
        gluPerspective(40.,1.,1.,40.)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                  0,0,0,
                  0,1,0)
        glPushMatrix()

        # Create shader Program
        self.__program = Shader()

        # Start timer
        timer_instance = timer.get_instance()
        timer_instance.start()

    def __setup_model(self, model):
        # If there isn't a file path define use one of the skins specified in the md2 file
        if model.texture == None:
            model.load_skin()
        
        # If there isn't a texture avavailable load a 1 x 1 white texture
        if  model.texture == None:
            model.load_white_texture()

        # Fix scale
        scale = 0.025
        for x in range(0, model.header.num_xyz * model.header.num_frames):
            model.vertices[x].x *= scale
            model.vertices[x].y *= scale
            model.vertices[x].z *= scale

    def __drawModel(self, model):
        if self.state == DINAMIC:
            model.animate()
            model.interpolate()

        # Binde model's texture
        glBindTexture( GL_TEXTURE_2D, model.texture.id)
        
        # Draw model
        i = 0
        while model.glcmds[i]:
            aux = model.glcmds[i]
            i += 1
            if aux < 0:
                glBegin(GL_TRIANGLE_FAN)
                aux = -aux
            else:
                glBegin(GL_TRIANGLE_STRIP)

            for j in range(aux, 0, -1):           
                # Texture coordinates
                if model.is_texture_loaded == True:
                    glTexCoord2f( struct.unpack('f', struct.pack('i', model.glcmds[i]))[0], struct.unpack('f', struct.pack('i', model.glcmds[i + 1]))[0] )

                # parse triangle's normal (for the lighting)
                glNormal3fv( anorms[model.normals[ model.curr_anim.curr_frame * model.header.num_xyz + model.glcmds[ i + 2] ] ])

                # draw the vertex
                glVertex3fv( model.vertices[ model.curr_anim.curr_frame * model.header.num_xyz + model.glcmds[ i + 2] ].get_as_array() )
                i += 3
            glEnd()

    def __SetUniform(self, program):
        # Material.
        glUniform3f(glGetUniformLocation(program.GetProgram(), "u_Material.specular"), 0.1, 0.1, 0.1)
        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_Material.shininess"), 0.6)

        # Light.
        glUniform3f(glGetUniformLocation(program.GetProgram(), "u_PointLight.position"), self.light_pos[0], self.light_pos[1], self.light_pos[2])
        glUniform3f(glGetUniformLocation(program.GetProgram(), "u_PointLight.color"), 1.0, 1.0, 1.0)
        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_PointLight.ambient_strength"), 0.2)
        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_PointLight.diffuse_strength"), 2.0)
        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_PointLight.specular_strength"), 2.0)

        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_PointLight.constant"), 1.0)
        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_PointLight.linear"), 0.9)
        glUniform1f(glGetUniformLocation(program.GetProgram(), "u_PointLight.quadratic"), 0.032)

        # Others.
        glUniform1i(glGetUniformLocation(program.GetProgram(), "u_texture"), 0)
        glUniform3f(glGetUniformLocation(program.GetProgram(), "u_ViewPos"), self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])

    def __special(self, key, x, y):
       # change animation if scene is dinamic.
       if self.state == DINAMIC:
            if key == GLUT_KEY_UP:
                for aux in self.md2_models:
                    aux.change_animation(aux.curr_anim.anim_id + 1)
            elif key == GLUT_KEY_DOWN:
                for aux in self.md2_models:
                        aux.change_animation(aux.curr_anim.anim_id + 1)


    

    def __display(self):
        # shading
        self.__program.bind()
        self.__SetUniform(self.__program)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        timer_instance = timer.get_instance()
        timer_instance.update()

        sys.stdout.write("\rfps = %f" %(timer_instance.get_fps()))
        sys.stdout.flush()

        glRotate( 270, 1.0, 0.0, 0.0)
        glRotatef( 90, 0.0, 0.0, 1.0 )
        
        # Reverse the orientation of front-facing polygons because gl command list's triangles have clockwise winding
        glPushAttrib( GL_POLYGON_BIT )
        glFrontFace( GL_CW )

	    # Enable backface culling
        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

        for aux in self.md2_models:
            self.__drawModel(aux)

        glDisable( GL_CULL_FACE )
        glPopAttrib()

        glPopMatrix()

        Shader.unbind()
        glutSwapBuffers()
        glutPostRedisplay() # Redraw as fast as possible.
        return


    def run(self):
        glutDisplayFunc(self.__display)
        glutSpecialFunc(self.__special)

        glutMainLoop()
        return

def main():
    render = MasterRender()
    render.run()

if __name__ == '__main__': main()
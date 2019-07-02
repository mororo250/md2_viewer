import os
import struct

from typing import NamedTuple
from functools import partial

from timer import *
from texture import *

# initialize the 21 MD2 model animations
# first, last, fps
anim_names = [
    "STAND",
    "RUN",
    "ATTACK",
    "PAIN_A",
    "PAIN_B",
    "PAIN_C",
    "JUMP",
    "FLIP",
    "SALUTE",
    "FALLBACK",
    "WAVE",
    "POINT",
    "CROUCH_STAND",
    "CROUCH_WALK",
    "CROUCH_ATTACK",
    "CROUCH_PAIN",
    "CROUCH_DEATH",
    "DEATH_FALLBACK",
    "DEATH_FALLFORWARD",
    "DEATH_FALLBACKSLOW",
    "BOOM"
]

anim_list = [
	[   0,  39,  9 ],	# STAND
	[  40,  45, 10 ],	# RUN
	[  46,  53, 10 ],	# ATTACK
	[  54,  57,  7 ],	# PAIN_A
	[  58,  61,  7 ],	# PAIN_B
	[  62,  65,  7 ],	# PAIN_C
	[  66,  71,  7 ],	# JUMP
	[  72,  83,  7 ],	# FLIP
	[  84,  94,  7 ],	# SALUTE
	[  95, 111, 10 ],	# FALLBACK
	[ 112, 122,  7 ],	# WAVE
	[ 123, 134,  6 ],	# POINT
	[ 135, 153, 10 ],	# CROUCH_STAND
	[ 154, 159,  7 ],	# CROUCH_WALK
	[ 160, 168, 10 ],	# CROUCH_ATTACK
	[ 169, 172,  7 ],	# CROUCH_PAIN
	[ 173, 177,  5 ],	# CROUCH_DEATH
	[ 178, 183,  7 ],	# DEATH_FALLBACK
	[ 184, 189,  7 ],	# DEATH_FALLFORWARD
	[ 190, 197,  7 ],	# DEATH_FALLBACKSLOW
	[ 198, 198,  5 ]	# BOOM
    ]

def from_bytes_to_float(data):
    return struct.unpack('f', data)[0]

class md2_anim():

    def __init__(self, first_frame, end_frame, fps, idx):
        self.first_frame = first_frame
        self.end_frame = end_frame
        
        self.fps = fps
        self.last_time = 0
        self.anim_id = idx      # Id of the animation in the animation list. # -1 for out of range animation
    
        self.curr_frame = self.first_frame
        if self.first_frame != self.end_frame:
            self.next_frame = self.first_frame + 1
        else:
            self.next_frame = self.first_frame
    
    def get_name(self):
        return anim_names[self.anim_id]


class md2_vec3i():

    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def get_as_array(self):
        array = [self.x, self.y, self.z]
        return array

    # byte array with 6 elements - short in c
    @staticmethod
    def from_bytes(data, byte_order): 
        vec3 = md2_vec3i() 
        vec3.x = int.from_bytes(data[0:2], byteorder = byte_order)
        vec3.y = int.from_bytes(data[2:4], byteorder = byte_order)
        vec3.z = int.from_bytes(data[4:6], byteorder = byte_order)
        return vec3
    
    # byte array with 3 elements - char in c
    @staticmethod
    def from_bytes_compressed(data, byte_order):
        vec3 = md2_vec3i()
        vec3.x = data[0]
        vec3.y = data[1]
        vec3.z = data[2]
        return vec3

class md2_vec3f():

    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def get_as_array(self):
        array = [self.x, self.y, self.z]
        return array

    # byte array with 12 elements
    @staticmethod
    def from_bytes(data): 
        vec3 = md2_vec3f()
        vec3.x = from_bytes_to_float(data[0:4])
        vec3.y = from_bytes_to_float(data[4:8])
        vec3.z = from_bytes_to_float(data[8:12])
        return vec3

class md2_texCoord(NamedTuple):
    s: int
    t: int

class md2_triangle(NamedTuple):
    vertex: md2_vec3i     # vertices indexes
    st: md2_vec3i         # Tex coord indexes

class md2_vertex(NamedTuple):
    position: md2_vec3i
    normal_index: int

class md2_frame(NamedTuple):
    scale: md2_vec3f
    translate: md2_vec3f
    name: str
    verts_index: int


class md2_header:
    def __init__(self, md2):
        if md2.read(4).decode("utf-8") != "IDP2":
            print("ERROR!!! invalid file")
            return
        if int.from_bytes(md2.read(4), byteorder='little') != 8:
            print("Invalid version")
            return 
        self.skin_width = int.from_bytes(md2.read(4), byteorder='little')         # width of the texture
        self.skin_height = int.from_bytes(md2.read(4), byteorder = 'little')      # height of the texture
        self.frame_size = int.from_bytes(md2.read(4), byteorder = 'little')       # size of one frame in byte
        self.num_skins = int.from_bytes(md2.read(4), byteorder = 'little')        # number of textures
        self.num_xyz = int.from_bytes(md2.read(4), byteorder = 'little')          # number of vertices
        self.num_st = int.from_bytes(md2.read(4), byteorder = 'little')           # number of texture coordinates
        self.num_tris = int.from_bytes(md2.read(4), byteorder = 'little')         # number of triangles
        self.num_glcmds = int.from_bytes(md2.read(4), byteorder = 'little')       # number of opengl commands
        self.num_frames = int.from_bytes(md2.read(4), byteorder = 'little')       # total number of frames
        self.ofs_skins = int.from_bytes(md2.read(4), byteorder = 'little')        # offset to skin names (64 bytes each)
        self.ofs_st = int.from_bytes(md2.read(4), byteorder = 'little')           # offset to s-t texture coordinates
        self.ofs_tris = int.from_bytes(md2.read(4),byteorder = 'little')          # offset to triangles
        self.ofs_frames = int.from_bytes(md2.read(4), byteorder = 'little')       # offset to frame data
        self.ofs_glcmds = int.from_bytes(md2.read(4), byteorder = 'little')       # offset to opengl commands
        self.ofs_end = int.from_bytes(md2.read(4), byteorder = 'little')          # offset to end of file

class md2_model():

    def __init__(self, file_path):
        # Texture:
        self.texture = None
        self.is_texture_loaded = False
        # Idex of skin beeing used.
        # -1 None of the skins are beeing used.
        # >= 0 one of the skins is beeing used. 
        self.skin_used = -1

        self.path = os.path.dirname(file_path)
        with open(file_path, "rb") as md2:
            # Header:
            self.header = md2_header(md2)

            # Load skin file names
            md2.seek(self.header.ofs_skins)
            self.skins = [None] * self.header.num_skins
            for i in range(0, self.header.num_skins):
                self.skins[i] = md2.read(64).decode("utf-8", "ignore")

            # Load Tex Coord
            md2.seek(self.header.ofs_st)
            self.texCoords = [None] * self.header.num_st
            for i in range(0, self.header.num_st):
                self.texCoords[i] = md2_texCoord(int.from_bytes(md2.read(2), 'little'), int.from_bytes(md2.read(2), 'little'))

            # Load triangles
            md2.seek(self.header.ofs_tris)
            total_num_triangles = self.header.num_tris * self.header.num_frames
            self.triangles = [None] * total_num_triangles
            for i in range(0, total_num_triangles):
                self.triangles[i] = md2_triangle(md2_vec3i.from_bytes(md2.read(6), 'little'), md2_vec3i.from_bytes(md2.read(6), 'little'))

            # Load frames
            self.frames = [None] * self.header.num_frames
            self.vertices = [None] * self.header.num_xyz * self.header.num_frames # md2_vec3f
            self.normals =  [None] * self.header.num_xyz * self.header.num_frames
            for i in range(0, self.header.num_frames):
                start_point =  i * self.header.frame_size
                md2.seek(self.header.ofs_frames + start_point)
                self.frames[i] = md2_frame(
                    md2_vec3f.from_bytes(md2.read(12)), md2_vec3f.from_bytes(md2.read(12)), 
                    md2.read(16).decode("utf-8", "ignore"), start_point)
                for j in range(self.header.num_xyz * i, self.header.num_xyz * (i + 1) ):
                    vertex = md2_vertex(md2_vec3i.from_bytes_compressed(md2.read(3), 'little'), int.from_bytes(md2.read(1), 'little'))
                    self.vertices[j] = md2_vec3f(vertex.position.x * self.frames[i].scale.x + self.frames[i].translate.x, vertex.position.y * self.frames[i].scale.y  + self.frames[i].translate.y, vertex.position.z * self.frames[i].scale.z + self.frames[i].translate.z)
                    self.normals[j] = vertex.normal_index

            # Load OpenGl commands      
            md2.seek(self.header.ofs_glcmds)
            self.glcmds = [None] * self.header.num_glcmds
            for i in range(0, self.header.num_glcmds):
                self.glcmds[i] = int.from_bytes(md2.read(4), 'little', signed = True)

            # Create frame vertices list
            self.frame_vertices = [None] * self.header.num_xyz
            for i in range(0, self.header.num_xyz):
                self.frame_vertices[i] = md2_vec3f()
                self.frame_vertices[i].__dict__ = self.vertices[i].__dict__.copy()

        # Animation info
        self.curr_anim = md2_anim(anim_list[0][0], anim_list[0][1], anim_list[0][2], 0)
        
    def load_texture(self, file_path):
        self.is_texture_loaded = True
        self.texture = texture(file_path)

    def load_skin(self, idx = -1):
        if idx == -1:
            for i in range(0, self.header.num_skins):
                file_path = self.path + '/' + self.skins[i]
                file_path = file_path.rstrip('\x00')
                if os.path.isfile(file_path):
                    self.texture = texture(file_path)
                    slef.skin_used = i
                    print("texture file: %s" % file_path)
                    return
            print("None of the skins in md2 exists")
            return 
        else:
            if idx < 0 or idx >= self.header.num_skins:
                file_path = self.path + + '/' + self.skins[idx]
                file_path.strip()
                if os.path.isfile(file_path):
                    self.texture = texture(file_path)
                    slef.skin_used = i
                    print("texture file: %s" % file_path)
            else:
                raise Exception("skin`s Index out of range.")

    def load_white_texture(self):
        self.texture = texture()

    def animate(self):
        timer_instance = timer.get_instance()
        if self.curr_anim.last_time == 0:
            self.last_time = timer_instance.curr_time
        if (timer_instance.curr_time - self.curr_anim.last_time) > (1.0 / self.curr_anim.fps):
            self.curr_anim.last_time = timer_instance.curr_time
            self.curr_anim.curr_frame = self.curr_anim.next_frame
            self.curr_anim.next_frame += 1
            if self.curr_anim.next_frame > self.curr_anim.end_frame:
                self.curr_anim.next_frame = self.curr_anim.first_frame
    
    def interpolate(self):
        if self.curr_anim.first_frame == self.curr_anim.end_frame:
            return
        timer_instance = timer.get_instance()

        interpol = self.curr_anim.fps * (timer_instance.curr_time - self.curr_anim.last_time)
        frame_info_pos = self.curr_anim.curr_frame * self.header.num_xyz
        if (self.curr_anim.next_frame != 0):
            next_frame_info_pos = frame_info_pos + self.header.num_xyz
            for i in range(0, self.header.num_xyz):
                self.frame_vertices[i].x = self.vertices[frame_info_pos + i].x + interpol * (self.vertices[next_frame_info_pos + i].x - self.vertices[frame_info_pos + i].x)
                self.frame_vertices[i].y = self.vertices[frame_info_pos + i].y + interpol * (self.vertices[next_frame_info_pos + i].y - self.vertices[frame_info_pos + i].y)
                self.frame_vertices[i].z = self.vertices[frame_info_pos + i].z + interpol * (self.vertices[next_frame_info_pos + i].z - self.vertices[frame_info_pos + i].z)
        else:
            for i in range(0, self.header.num_xyz):
                self.frame_vertices[i].__dict__ = self.vertices[frame_info_pos + i].__dict__.copy()

    def change_animation(self, idx):
        if idx == self.curr_anim.anim_id:
            return
        if idx < 21 and idx >= 0:
            if self.curr_anim.end_frame > self.header.num_frames -1:
                print("This animation is not available in this file")
                self.curr_anim = md2_anim(anim_list[0][0], anim_list[0][1], anim_list[0][2], 0)
                print("Set animation to %s " % anim_names[0])
            else:
                self.curr_anim = md2_anim(anim_list[idx][0], anim_list[idx][1], anim_list[idx][2], idx)
                print("Set animation to %s" % anim_names[idx])
        else:
            idx = 0
            self.curr_anim = md2_anim(anim_list[0][0], anim_list[0][1], anim_list[0][2], 0)
            print("Set animation to %s" % anim_names[0])


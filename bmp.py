import os
from scipy import misc

class bmp_loader:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.pixels = []

    def load_texture_file(self, filename, flipvert = False):
        with open(filename, "rb") as bmp:
            # Find size of the file.
            bmp.seek(0, os.SEEK_END)
            file_size = bmp.tell()
           # Go back to the beggining of the file.
            bmp.seek(0)

            bmp_type = int.from_bytes(bmp.read(2), byteorder='little')
            bmp_size = int.from_bytes(bmp.read(4), byteorder='little')          # Size of BMP dile in bytes(unreliable)
            bmp_reserved1 = int.from_bytes(bmp.read(2), byteorder='little')
            bmp_reserved2 = int.from_bytes(bmp.read(2), byteorder='little')     
            offset = int.from_bytes(bmp.read(4), byteorder='little')            # Offset to start of image data in byte

            bmp.seek(30) #compression type
            compression_type = int.from_bytes(bmp.read(4), byteorder='little')
            
            if compression_type < 0 or compression_type > 3:
                # OS/2 Header 
                bmp.seek(14)
                size_header = int.from_bytes(bmp.read(4), byteorder='little')
                self.width = int.from_bytes(bmp.read(2), byteorder='little')
                self.height = int.from_bytes(bmp.read(2), byteorder='little')
                num_planes = int.from_bytes(bmp.read(2), byteorder='little')
                bits_per_pixel = int.from_bytes(bmp.read(2), byteorder='little')

                compression_type = -1
            else:
                # Windows Header Format:
                bmp.seek(14)
                size_header = int.from_bytes(bmp.read(4), byteorder='little')
                self.width = int.from_bytes(bmp.read(4), byteorder='little')
                self.height = int.from_bytes(bmp.read(4), byteorder='little')
                num_planes = int.from_bytes(bmp.read(2), byteorder='little')
                bits_per_pixel = int.from_bytes(bmp.read(2), byteorder='little')

                compression_type = int.from_bytes(bmp.read(4), byteorder='little')
                size_of_img = int.from_bytes(bmp.read(4), byteorder='little')
                hor_res = int.from_bytes(bmp.read(4), byteorder='little')           # Horizontal resolution in pixels per meter (Unreliable)
                vert_res = int.from_bytes(bmp.read(4), byteorder='little')          # Vertical resolution in pixels per meter (Unreliable)

                number_of_colors = int.from_bytes(bmp.read(4), byteorder='little')
                number_of_important_colors = int.from_bytes(bmp.read(4), byteorder='little')

                # Read the palette:
                idx = 0
                pixels = [0] * 4 * self.height * self.width

                if compression_type == -1 or compression_type == 0:
                    for i in range(self.height - 1, 0, -1):
                        if flipvert:
                            idx = i * self.width * 4
                            # RGB 1 bits
                            if bits_per_pixel == 1:
                                for col in range(0, self.width / 8, 1):

                                                                   
            return True

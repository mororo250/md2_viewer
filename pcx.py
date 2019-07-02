import os
import numpy

# --------------------------------------------------
# LoadFilePCX() - load a Zsoft PCX image [.pcx]
#
# parameters :
#    - filename [in]  : image source file
#    - pixels	 [out] : 32 bits rgba image data
#    - width    [out] : image width in pixels
#    - height   [out] : image height in pixels
#    - flipvert [in]  : flip vertically
#
# return value :
#    - -1 : no image data
#    -  0 : failure
#    -  1 : success
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# accepted image formats :
#     # RLE 8 bits / version 5
# ------

class pcx_loader:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.pixels = []

    def load_texture_file(self, filename, flipvert = False):
        with open(filename, "rb") as pcx:
            # Find size of the file.
            pcx.seek(0, os.SEEK_END)
            file_size = pcx.tell()
           # Go back to the beggining of the file.
            pcx.seek(0)

            manufacturer = int.from_bytes(pcx.read(1), byteorder='little')
            version = int.from_bytes(pcx.read(1), byteorder='little')
            encoding = int.from_bytes(pcx.read(1), byteorder='little')
            bits_per_pixel = int.from_bytes(pcx.read(1), byteorder='little')

            x = int.from_bytes(pcx.read(2), byteorder='little')
            y = int.from_bytes(pcx.read(2), byteorder='little')
            self.width = int.from_bytes(pcx.read(2), byteorder='little')
            self.height = int.from_bytes(pcx.read(2), byteorder='little')
            horzRes = int.from_bytes(pcx.read(2), byteorder='little')
            vertRes = int.from_bytes(pcx.read(2), byteorder='little')

            palette = int.from_bytes(pcx.read(4), byteorder='little')
            reserved = int.from_bytes(pcx.read(1), byteorder='little')
            numColorPlanes = int.from_bytes(pcx.read(1), byteorder='little')

            bytesPerScanLine = int.from_bytes(pcx.read(2), byteorder='little')
            paletteType = int.from_bytes(pcx.read(2), byteorder='little')
            horzSize = int.from_bytes(pcx.read(2), byteorder='little')
            vertSize = int.from_bytes(pcx.read(2), byteorder='little')

            padding = pcx.read(54).decode("utf-8", "ignore")

            if manufacturer != 10 or version != 5 or encoding != 1 or bits_per_pixel != 8:
                return False

            self.width = self.width - x + 1
            self.height = self.height - y + 1

            data = [None] * self.width * self.height

            pcx.seek(128)
            idx = 0
            while idx < self.width * self.height:
                aux = pcx.read(1)
                if aux[0] > 0xbf:
                    num_repeat = 0x3f & aux[0]
                    aux = pcx.read(1)
                    for i in range(0, num_repeat):
                        data[idx] = int.from_bytes(aux, byteorder='little')
                        idx += 1
                else:
                    data[idx] = int.from_bytes(aux, byteorder='little')
                    idx += 1
            # The palette is located at the 769th last byte of the file.
            pcx.seek(-769, os.SEEK_END)
            buffer = pcx.read()
            # Verify the palette; first char must be equal to 12
            if buffer[0] != 12:
                return False

            # Memory for 32 bits rgba data
            self.pixels = [0] * self.width * self.height * 4

            idx = 0
            for i in range(self.height - 1, 0, -1):
                if flipvert:
                    idx = i * self.width * 4
                for j in range(0, self.width):
                    color = 3 * data[i * self.width + j] + 1

                    self.pixels[idx] = buffer[color]
                    self.pixels[idx + 1] = buffer[color + 1]
                    self.pixels[idx + 2] = buffer[color + 2]
                    self.pixels[idx + 3] = 255
                    idx += 4
            return True

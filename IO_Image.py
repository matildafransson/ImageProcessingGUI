from PIL import Image
import numpy as np
import fabio.tifimage as tif
import os



def readOneTempImage(path):
    f = open(path)
    lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.replace(',','.')

    data = lines[17:]
    data_np = np.loadtxt(data)

    return data_np





class IO_Image():
    def __init__(self,mainPath):
        self.path = mainPath

    def readOneImage(self):

        image = np.array(Image.open(self.path))
        vol = np.zeros((1, image.shape[0], image.shape[1]))
        vol[0] = image
        return vol

    def readAllImages(self, frame_skip):
        index = 0
        newPath_list = []
        for pathIm in self.path:
            if pathIm.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif')):
                #np.flip(pathIm)
                flag_temp = False
                newPath_list.append(pathIm)
            elif pathIm.lower().endswith(('.asc')):
                flag_temp = True
                newPath_list.append(pathIm)


        for i, pathIm in enumerate(newPath_list):
            if i%frame_skip == 0:
                if flag_temp == False:
                    image = np.array(Image.open(pathIm))
                else:
                    image = readOneTempImage(pathIm)
                #image = np.flip(image)
                print(pathIm)
                if i == 0:
                    vol = np.zeros((int(len(self.path)/frame_skip)+1, image.shape[0], image.shape[1]))
                vol[int(index/frame_skip), :, :] = image
            index += 1
        return vol

    def SaveAllImages(self,vol):
        for i in range (0, vol.shape[0]):
            filename = self.path + '_' + str(i).zfill(6) +'.tiff'
            print(vol[i])
            self.saveFloat(vol[i], filename)


    def saveFloat(self, data, filename):

        #data = np.asarray(data, np.float32)
        tif.TifImage(data=data).write(filename)

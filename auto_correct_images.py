from PIL import Image
import numpy as np
import fabio.tifimage as tif

def readAllImages(path):
    index = 0
    newPath_list = []
    for pathIm in path:
        if pathIm.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.tif')):
            # np.flip(pathIm)
            newPath_list.append(pathIm)
            image = np.array(Image.open(pathIm))

path = U:/projects/whaitiri/Data/mi1354/id19

Data = readAllImages
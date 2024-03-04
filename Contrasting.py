import os
import numpy as np
from PIL import Image
import fabio.tifimage as tif
import re
import matplotlib.pyplot as plt

def saveFloat(data, filename):
    tif.TifImage(data=data).write(filename)

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

if __name__ == '__main__':
    input_path = 'U:\\whaitiri\Data\\data_processing_mi1354\\New_Corrections\\'
    output_path = 'U:\\whaitiri\\Data\\data_processing_mi1354\\Gabor filtering\\'

    list_folders = []
    list_exp_names = []

#
    for folder in os.listdir(input_path):
        if ('M50_SP_Exp51' in folder):
            path = input_path + folder
            list_folders.append(path)
            name = folder.split('_')
            print(name)
            exp_name = name[0] + '_' + name[1] + '_' + name[2]
            list_exp_names.append(exp_name)
    print(list_exp_names)
    print(list_folders)

    for  j, folder in enumerate(list_folders):
        print(folder)
        for frames in os.listdir(folder):
            if ('Frames' in frames) and not ('Frames_contrasted' in frames):
                path = folder + '\\' + frames
                print(path)

        if ('P42A_NP_Exp13' in folder):
            start_min = 0.6068
            start_max = 0.8859
            end_min = 0.1549
            end_max = 0.4868

        if ('P42A_NP_Exp21' in folder):
            start_min = 0.4801
            start_max = 0.7700
            end_min = -0.0979
            end_max = 0.2935

        if ('M50_SP_Exp51' in folder):
            start_min = 0.6126
            start_max = 0.9441
            end_min = 0.2166
            end_max = 0.6293

        if ('M50_PP_Exp52' in folder):
            start_min = 0.5317
            start_max = 0.8026
            end_min = 0.2294
            end_max = 0.5767

        if ('M50_NP_Exp41' in folder):
            start_min = 0.4731
            start_max = 0.8859
            end_min = 0.1549
            end_max = 0.4868

        if ('P42A_SP_Exp5' in folder):
            start_min = 0.6945
            start_max = 1.0023
            end_min = 0.0905
            end_max = 0.4837

        if ('P42A_ST_Exp2' in folder):
            start_min = 0.1184
            start_max = 0.4083
            end_min = -0.3602
            end_max = 0.2843

        if ('M50_SP_Exp3' in folder):
            start_min = 0.0732
            start_max = 0.5105
            end_min = -0.1204
            end_max = 0.3196

        list_images = []
        for i, im in enumerate(os.listdir(path)):

            if 'cfg' not in im:
                pathIm = path + '\\' + im
                list_images.append(pathIm)
                if i == 1:
                    image = (Image.open(pathIm))
                    width = int((np.round(image.size[0] * 0.5)))
                    height = int((np.round(image.size[1] * 0.5)))
                    image = image.resize((width, height))


        list_images = natural_sort(list_images)

        vol = np.zeros((int(len(list_images)), image.size[1], image.size[0]))

        for i, pathIm in enumerate(list_images):
            print('loading ',pathIm )
            image = (Image.open(pathIm))
            image = image.resize((width, height))
            image = np.array(image)

            image[np.isinf(image)] = np.mean(image[np.isinf(image) == 0 ])
            vol[int(i), :, :] = image

        #vol[vol > 10.0] = 1.0

        mean_start = np.mean(vol[0])
        mean_end = np.mean(vol[-1])
        Bmin = (mean_start * end_min - start_min * mean_end) / (mean_start - mean_end)
        Amin = (start_min - Bmin) / mean_start
        Bmax = (mean_start * end_max - start_max * mean_end) / (mean_start - mean_end)
        Amax = (start_max - Bmax) / mean_start

        output_library = output_path + list_exp_names[j] + '\\' + 'Frames_contrasted'

        if not os.path.exists(output_library):
            os.makedirs(output_library)

        for i in range (0, vol.shape[0]):

            slice = vol[i]
            mean_value = np.mean(np.mean(slice))
            minimumValueS = (mean_value * Amin) + Bmin
            maximumValueS = (mean_value * Amax) + Bmax

            a = (1.0)/(maximumValueS-minimumValueS)
            b = - a * minimumValueS
            new_slice = a*slice+b

            #plt.imshow(slice)
            #plt.show()

            filename = output_library + '\\' + str(i).zfill(6) +'.tiff'
            saveFloat(new_slice, filename)
            print(filename)

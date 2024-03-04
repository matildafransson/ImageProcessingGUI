import vtk
import numpy as np


def image_float_to_int8(vol, minValue, maxValue):
    """
    Format the volume to a 0-255 image uint16
    """
    vol = (255 * (vol - minValue)) / (maxValue - minValue)
    vol = vol.astype(np.uint8)
    vol[vol < 0] = 0
    vol[vol > 255] = 255

    return vol

def import_numpy_array( np_array, minValue, maxValue):
    data_importer = vtk.vtkImageImport()
    np_array = image_float_to_int8(np_array, minValue, maxValue)
    shape_data = np_array.shape
    data_importer.CopyImportVoidPointer(np_array, np_array.nbytes)
    data_importer.SetDataScalarTypeToUnsignedChar()
    data_importer.SetNumberOfScalarComponents(1)
    data_importer.SetDataExtent(0, shape_data[2] - 1, 0, shape_data[1] - 1, 0, shape_data[0] - 1)
    data_importer.SetWholeExtent(0,shape_data[2] - 1, 0, shape_data[1] - 1, 0, shape_data[0] - 1)
    return data_importer

def save_mesh(path, mc):
        plyWriter = vtk.vtkPLYWriter()
        plyWriter.SetFileName(path)
        plyWriter.SetInputConnection(mc.GetOutputPort())
        plyWriter.Write()

def MarchingCube(image, threshold, path):


    sx = image.shape[0]-1
    sy = image.shape[1]-1
    sz = image.shape[2]-1

    image[0,0,0]= 1
    image[0, sy,0]= 1
    image[0,0,sz] =1
    image[0,sy,sz] =1
    image[sx, 0,0 ] =1
    image[sx,0,sz] =1
    image[sx,sy,0] =1
    image[sx,sy,sz] = 1
    min_value = np.min(image)
    max_value = np.max(image)
    thresholdValue = int((255.0 * (threshold - min_value)) / (max_value - min_value))

    data_importer = import_numpy_array(image,min_value,max_value)


    threshold = vtk.vtkImageThreshold()
    threshold.SetInputConnection(data_importer.GetOutputPort())
    threshold.ThresholdByLower(thresholdValue)  # remove all soft tissue
    threshold.ReplaceInOn()
    threshold.SetInValue(0)
    threshold.ReplaceOutOn()
    threshold.SetOutValue(1)
    threshold.Update()

    mc = vtk.vtkMarchingCubes()
    mc.SetInputConnection(threshold.GetOutputPort())
    mc.ComputeNormalsOn()
    mc.GenerateValues(1, 1, 1)
    #mc.SetValue(0, threshold)
    mc.Update()

    save_mesh(path, mc)

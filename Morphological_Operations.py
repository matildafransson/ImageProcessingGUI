import SimpleITK as sitk

import numpy as np

def imageFromNumpyToITK(vol):
    vol = vol.astype(np.uint8)
    return sitk.GetImageFromArray(vol)


def imageFromITKToNumpy(vol):
    return sitk.GetArrayFromImage(vol)

def closing(data,radius):
    closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
    closing_filter.SetKernelRadius(radius)

    data_itk = imageFromNumpyToITK(data)
    output_itk = closing_filter.Execute(data_itk)
    return imageFromITKToNumpy(output_itk)

def dilate(data,radius):
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelRadius(radius)

    data_itk = imageFromNumpyToITK(data)
    output_itk = dilate_filter.Execute(data_itk)
    return imageFromITKToNumpy(output_itk)

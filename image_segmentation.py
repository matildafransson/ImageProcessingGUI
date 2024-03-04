import SimpleITK as sitk
import numpy as np

def imageFromNumpyToITK(vol):
    return sitk.GetImageFromArray(vol)


def imageFromITKToNumpy(vol):
    return sitk.GetArrayFromImage(vol)


def SegConnectedThreshold(vol, val_min, val_max, seedListToSegment):
    ITK_Vol = imageFromNumpyToITK(vol)

    segmentationFilter = sitk.ConnectedThresholdImageFilter()

    for seed in seedListToSegment:
        seedItk = (seed[0], seed[1], seed[2])
        segmentationFilter.AddSeed(seedItk)

    segmentationFilter.SetLower(val_min)
    segmentationFilter.SetUpper(val_max)
    segmentationFilter.SetReplaceValue(1)
    ITK_Vol = segmentationFilter.Execute(ITK_Vol)
    image = imageFromITKToNumpy(ITK_Vol)

    return image.astype(np.uint8)
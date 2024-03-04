import numpy as np
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt

class Processing_Correction ():


    def _normalization(self, proj, ref, dark=[]):

        if len(dark) == 0:
            #plt.imshow(proj)
            #plt.show()
            #plt.imshow(ref)
            #plt.show()
            result = -np.log10(proj/ref)

        else:
            result = -np.log10((proj-dark)/(ref-dark))
        result[result > 100] = 0
        result[result < -100] = 0
        return result

    def normalizationAllImages(self, vol_proj, vol_ref, vol_dark=[]):

        if not len(vol_dark) == 0:
            mean_dark = np.mean(vol_dark)
        else:
            mean_dark = []

        median_ref = np.median(vol_ref, axis=0)

        vol_out = np.zeros((vol_proj.shape[0],vol_proj.shape[1], vol_proj.shape[2]))

        for i in range(0, vol_proj.shape[0]):
            slice = vol_proj[i]

            vol_out[i] = self._normalization(slice, median_ref,mean_dark)

        return vol_out

    def createReferences(self,vol_proj, nr_proj, sigma, dev=False):


        mean_dark = []

        ref_vol = np.copy(vol_proj[:nr_proj])
        for i in range(0, ref_vol.shape[0]):
            ref_vol[i] = gaussian_filter(ref_vol[i], sigma=sigma)
        median_ref = np.median(ref_vol, axis=0)

        vol_out = np.zeros((vol_proj.shape[0], vol_proj.shape[1], vol_proj.shape[2]))

        for i in range(0, vol_proj.shape[0]):

            print(i)
            slice = vol_proj[i]

            vol_out[i] = self._normalization(slice, median_ref,mean_dark)

        return vol_out


import pickle
import numpy as np
import functools


# from Masa
def assign_loggrid(x, y, xmin, xmax, xsteps, ymin, ymax, ysteps):
    """
    Computes indices of 2D grids. Only used when we use shear weight that is binned by S/N and size ratio.
    """
    from math import log10
    # return x and y indices of data (x,y) on a log-spaced grid that runs from [xy]min to [xy]max in [xy]steps

    logstepx = log10(xmax/xmin)/xsteps
    logstepy = log10(ymax/ymin)/ysteps

    indexx = (np.log10(x/xmin)/logstepx).astype(int)
    indexy = (np.log10(y/ymin)/logstepy).astype(int)

    indexx = np.maximum(indexx,0)
    indexx = np.minimum(indexx, xsteps-1)
    indexy = np.maximum(indexy,0)
    indexy = np.minimum(indexy, ysteps-1)

    return indexx,indexy


def _find_shear_weight(dat, wgt_dict, snmin, snmax, sizemin, sizemax, steps, mdet_mom):

    """
    Assigns shear weights to the objects based on the grids.
    """

    if wgt_dict is None:
        weights = np.ones(len(dat))
        return weights

    shear_wgt = wgt_dict['weight']
    smoothing = True
    if smoothing:
        from scipy.ndimage import gaussian_filter
        smooth_response = gaussian_filter(wgt_dict['response'], sigma=2.0)
        shear_wgt = (smooth_response/wgt_dict['meanes'])**2
    indexx, indexy = assign_loggrid(np.array(dat[mdet_mom+'_s2n']), np.array(dat[mdet_mom+'_T_ratio']), snmin, snmax, steps, sizemin, sizemax, steps)
    weights = np.array([shear_wgt[x, y] for x, y in zip(indexx, indexy)])

    return weights


def _get_shear_weights(dat, gal_weight_file, shape_err=False):
    if shape_err:
        return 1/(0.22**2 + 0.5*(np.array(dat['gauss_g_cov_1_1']) + np.array(dat['gauss_g_cov_2_2'])))
    else:
        with open(gal_weight_file, 'rb') as handle:
            wgt_dict = pickle.load(handle)
            snmin = wgt_dict['xedges'][0]
            snmax = wgt_dict['xedges'][-1]
            sizemin = wgt_dict['yedges'][0]
            sizemax = wgt_dict['yedges'][-1]
            steps = len(wgt_dict['xedges'])-1
        shear_wgt = _find_shear_weight(dat, wgt_dict, snmin, snmax, sizemin, sizemax, steps, 'gauss')
        return shear_wgt


def _wmean(q,w):
    return np.sum(q*w)/np.sum(w)


get_shear_weights = functools.partial(
    _get_shear_weights,
    gal_weight_file="/pscratch/sd/m/myamamot/des-y6-analysis/y6_measurement/v6/inverse_variance_weight_v6.pickle",
)


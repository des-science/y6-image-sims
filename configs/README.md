# configs

## results

| config | m mean | m std (3σ) | c mean | c std (3σ) | # tiles | mfrac |
|---|---|---|---|---|---|---|
| grid-bright | -3.927e-05 | 2.934e-04 | -1.034e-06 | 6.997e-06 | 400 | 0.5 |
| grid-bright | -2.375e-04 | 2.694e-04 | -1.291e-06 | 6.410e-06 | 400 | 0.4 |
| grid-bright | -3.289e-04 | 2.423e-04 | 1.109e-06 | 5.787e-06 | 400 | 0.3 |
| grid-bright | -3.240e-04 | 2.147e-04 | 4.876e-07 | 5.331e-06 | 400 | 0.2 |
| grid-bright | -2.593e-04 | 1.467e-04 | -5.426e-08 | 3.413e-06 | 398 | 0.1 |
| grid-bright | -2.117e-04 | 1.396e-04 | -4.128e-08 | 3.192e-06 | 400 | 0.09 |
| grid-bright | -2.143e-04 | 1.264e-04 | -8.010e-07 | 3.002e-06 | 400 | 0.08 |
| grid-bright | -2.168e-04 | 1.128e-04 | -4.582e-07 | 2.790e-06 | 400 | 0.07 |
| grid-bright | -1.729e-04 | 1.080e-04 | -9.203e-07 | 2.521e-06 | 400 | 0.06 |
| grid-bright | -1.261e-04 | 9.797e-05 | -5.816e-07 | 2.376e-06 | 400 | 0.05 |
| grid-bright | -1.601e-05 | 8.365e-05 | -1.276e-07 | 1.996e-06 | 400 | 0.04 |
| grid-bright | 9.062e-05 | 6.291e-05 | -5.879e-07 | 1.537e-06 | 400 | 0.03 |
| grid-bright | 1.689e-04 | 3.670e-05 | -4.854e-07 | 1.066e-06 | 400 | 0.02 |
| grid-bright | 2.560e-04 | 2.492e-05 | -3.936e-07 | 8.238e-07 | 400 | 0.01 |
| grid-bright-shear | -2.179e-04 | 1.756e-04 | -1.144e-06 | 3.160e-06 | 400 | 0.1 |
| grid-bright-shear | 1.805e-04 | 4.367e-05 | -7.719e-07 | 9.682e-07 | 400 | 0.02 |
| grid-bright-nomask | 3.246e-04 | 2.283e-05 | 5.672e-07 | 1.072e-06 | 196 | 0.1 |
| grid-bright-pixel | 5.715e-05 | 3.310e-04 | -3.774e-07 | 6.972e-06 | 98 | 0.1 |
| grid-bright-interp | -1.614e-04 | 1.789e-04 | -2.546e-06 | 4.085e-06 | 300 | 0.1 |
| grid-bright-interp-psf-nse (snr: 5000) | -2.489e-04 | 3.043e-04 | -1.579e-05 | 7.583e-06 | 100 | 0.1 |
| grid-bright-interp-psf-nse (snr: 400) | -2.026e-04 | 2.053e-04 | -5.774e-05 | 1.853e-05 | 200 | 0.1 |
| grid-bright-interp-psf-nse (snr: 200) | -1.976e-04 | 2.311e-04 | 2.681e-05 | 3.526e-05 | 200 | 0.1 |
| grid-bright-interp-psf-nse (snr: 150) | -1.660e-04 | 2.692e-04 | 1.309e-05 | 4.195e-05 | 300 | 0.1 |
| grid-bright-interp-psf-nse (snr: 100) | 2.001e-02 | 2.729e-03 | 8.470e-04 | 4.101e-04 | 300 | 0.1 |
| grid-bright-piff | -3.074e-04 | 3.511e-04 | -3.331e-06 | 8.011e-06 | 98 | 0.1 |
| grid-bright-piff-nomask | 3.238e-04 | 4.616e-05 | -6.013e-07 | 1.762e-06 | 98 | 0.1 |
| grid-faint | 2.658e-04 | 1.742e-03 | 9.420e-06 | 5.215e-05 | 1000 | 0.1 |
| rand-bright | -4.370e-04 | 6.369e-04 | -8.816e-06 | 2.734e-05 | 600 | 0.1 |
| rand |  |  |  |  |  |  |
| rand-faint | -3.889e-03 | 9.114e-03 | -1.379e-05 | 1.621e-04 | 99 | 0.1 |
| fiducial-no-piff | 1.110e-02 | 2.322e-02 | -2.645e-03 | 6.824e-04 | 92 | 0.1 |

## descriptions

### grid-bright

- bright exponential galaxies
- grid distribution
- Gaussian PSF

### grid-bright-pixel

- bright exponential galaxies
- grid distribution
- interpolated pixelated Gaussian PSF

### grid-bright-interp

- bright exponential galaxies
- grid distribution
- gaussian PSF (analyzed as interpolated pixelated)

### grid-bright-interp-psf-nse

- bright exponential galaxies
- grid distribution
- gaussian PSF (analyzed as interpolated pixelated with noise)

### grid-bright-piff

- bright exponential galaxies
- grid distribution
- Piff PSF

### grid-bright-piff-nomask

- bright exponential galaxies
- grid distribution
- Piff PSF
- no masking

### grid-faint

- faint exponential galaxies
- grid distribution
- Gaussian PSF

### rand-bright

- bright exponential galaxies
- bright exponential stars
- random distribution (with shearing scene)
- Gaussian PSF

### rand-piff

- cosmos galaxies
- random distribution (with shearing scene)
- gaia & sim stars
- Piff PSF

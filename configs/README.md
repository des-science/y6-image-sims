# configs

## results

|	config	|	m mean	|	m std (3σ)	|	c mean	|	c std (3σ)	|	# tiles	|
|---|---|---|---|---|---|
|	grid-bright	|	8.101e-04	|	6.405e-04	|		|		|	98	|
|	grid-bright-pixel	|	4.685e-04	|	7.454e-04	|		|		|	84	|
|	grid-bright-interp	|	-1.614e-04	|	1.789e-04	|	-2.546e-06	|	4.085e-06	|	300	|
|	grid-bright-interp-psf-nse (snr: 5000)	|	-2.489e-04	|	3.043e-04	|	-1.579e-05	|	7.583e-06	|	100	|
|	grid-bright-interp-psf-nse (snr: 400)	|	-2.026e-04	|	2.053e-04	|	-5.774e-05	|	1.853e-05	|	200	|
|	grid-bright-interp-psf-nse (snr: 200)	|	-1.976e-04	|	2.311e-04	|	2.681e-05	|	3.526e-05	|	200	|
|	grid-bright-interp-psf-nse (snr: 150)	|	-1.660e-04	|	2.692e-04	|	1.309e-05	|	4.195e-05	|	300	|
|	grid-bright-interp-psf-nse (snr: 100)	|	2.001e-02	|	2.729e-03	|	8.470e-04	|	4.101e-04	|	300	|
|	grid-bright-piff	|	-9.042e-04	|	6.831e-04	|		|		|	98	|
|	grid-bright-piff-nomask	|	-2.146e-04	|	1.384e-04	|		|		|	98	|
|	grid-faint	|	2.658e-04	|	1.742e-03	|	9.420e-06	|	5.215e-05	|	1000	|
| rand-bright	| -3.495e-04	| 7.871e-04	| 6.018e-07	| 3.540e-05	| 400	|
|	rand	|		|		|		|		|		|
|	rand-faint	|		|		|		|		|		|

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

# configs

## results

|	config	|	m mean	|	m std (3σ)	|	c mean	|	c std (3σ)	|	# tiles	|
|---|---|---|---|---|---|
|	grid-bright	|	8.101e-04	|	6.405e-04	|		|		|	98	|
|	grid-bright-pixel	|	4.685e-04	|	7.454e-04	|		|		|	84	|
|	grid-bright-interp	|	5.847e-04	|	6.573e-04	|		|		|	98	|
|	grid-bright-piff	|	-9.042e-04	|	6.831e-04	|		|		|	98	|
|	grid-bright-piff-nomask	|	-2.146e-04	|	1.384e-04	|		|		|	98	|
|	grid-faint	|	2.658e-04	|	1.742e-03	|	9.420e-06	|	5.215e-05	|	1000	|
|	rand-bright	|		|		|		|		|		|
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

### rand

- cosmos galaxies
- random distribution
- gaia & sim stars [TODO]
- Gaussian PSF

### rand-piff

- cosmos galaxies
- random distribution
- gaia & sim stars [TODO]
- Piff PSF

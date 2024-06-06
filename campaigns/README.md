# campaigns

| config | # tiles | constant shear | redshift shear | mdet | bfd |
|---|---|---|---|---|---|
| fiducial | 1000 | ✓ | ✓ | ✓ | ✓ |
| no_stars| 400 | ✓ | | ✓ | ✓ |
| median_color | 400 | ✓ | | ✓ | |
| grid_median_color| 400 | ✓ | | ✓ | |
| grid | 400 | ✓ | | | ✓ |

This is an in-progress place to hold onto the submission scripts for the final calibration campaigns.

## [calibration](./calibration/)

- fiducial: full-featured image simulation
- no_stars: no stars are simulated (flux set to 0)

## [mdet](./mdet/)

- median_color: PSFs evaluated at the median galaxy color (i.e., the color used for the mdet catalogs)
- grid-median_color: galaxies placed on a grid with PSFs evaluated at the median galaxy color

## [bfd](./bfd/)

- grid: galaxies placed on a grid

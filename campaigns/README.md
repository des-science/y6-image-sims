# campaigns

| config | # tiles | constant shear (2) | redshift shear (10) | mdet | bfd | description | ≈ node hours / tile / shear | ≈ node hours |
|---|---|---|---|---|---|---|---|---|
| [fiducial](fiducial.yaml) | 1000 | ✓ | ✓ | ✓ | ✓ | full-featured image simulation | 4 | 48,000 |
| [no_stars](no_stars.yaml) | 400 | ✓ | | ✓ | ✓ | no stars are simulated (flux set to 0) | 4 | 3,200 |
| [median_color](median_color.yaml) | 400 | ✓ | | ✓ | | PSFs evaluated at the median galaxy color (i.e., the color used for the mdet catalogs) | 2 | 1,600 |
| [grid-median_color](grid-median_color.yaml) | 400 | ✓ | | ✓ | | galaxies placed on a grid with PSFs evaluated at the median galaxy color | 2 | 1,600 |
| [grid](grid.yaml) | 400 | ✓ | | ✓ | ✓ | galaxies placed on a grid | 4 | 3,200 |
| [grid-exp](grid-exp.yaml) | 100 | ✓ | | ✓ | | bright exponentials placed on a grid with PSFs evaluated at the median galaxy color | 2 | 400 |


- constant shear: (0.02, 0.00) and (-0.02, 0.00) for z ∈ [0, 6]
- redshift shear: (0.02, 0.00) inside slice, (-0.02, 0.00) outside slice
- redshift slices: [0.0, 0.3], [0.3, 0.6], [0.6, 0.9], [0.9, 1.2], [1.2, 1.5], [1.5, 1.8], [1.8, 2.1], [2.1, 2.4], [2.4, 2.7], [2.7, 6.0]

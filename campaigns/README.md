# campaigns

| config | # tiles | constant shear | redshift shear | mdet | bfd |
|---|---|---|---|---|---|
| [fiducial](fiducial.yaml) | 1000 | ✓ | ✓ | ✓ | ✓ |
| [no_stars](no_stars.yaml) | 400 | ✓ | | ✓ | ✓ |
| [median_color](median_color.yaml) | 400 | ✓ | | ✓ | |
| [grid_median_color](grid_median_color.yaml) | 400 | ✓ | | ✓ | |
| [grid](grid.yaml) | 400 | ✓ | | | ✓ |

- fiducial: full-featured image simulation
- no_stars: no stars are simulated (flux set to 0)
- median_color: PSFs evaluated at the median galaxy color (i.e., the color used for the mdet catalogs)
- grid-median_color: galaxies placed on a grid with PSFs evaluated at the median galaxy color
- grid: galaxies placed on a grid

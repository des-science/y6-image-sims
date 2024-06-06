# campaigns

| config | # tiles | constant shear | redshift shear | mdet | bfd | description | ≈ node hours / tile / shear | ≈ node hours |
|---|---|---|---|---|---|---|---|---|
| [fiducial](fiducial.yaml) | 1000 | ✓ | ✓ | ✓ | ✓ | full-featured image simulation | 4 | 48,000 |
| [no_stars](no_stars.yaml) | 400 | ✓ | | ✓ | ✓ | no stars are simulated (flux set to 0) | 4 | 3,200 |
| [median_color](median_color.yaml) | 400 | ✓ | | ✓ | | PSFs evaluated at the median galaxy color (i.e., the color used for the mdet catalogs) | 2 | 1,600 |
| [grid-median_color](grid-median_color.yaml) | 400 | ✓ | | ✓ | | galaxies placed on a grid with PSFs evaluated at the median galaxy color | 2 | 1,600 |
| [grid](grid.yaml) | 400 | ✓ | | | ✓ | galaxies placed on a grid | 2 | 1,600 |

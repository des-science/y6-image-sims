# campaigns

| config | # tiles | constant shear | redshift shear | mdet | bfd | description |
|---|---|---|---|---|---|---|
| [fiducial](fiducial.yaml) | 1000 | ✓ | ✓ | ✓ | ✓ | full-featured image simulation |
| [no_stars](no_stars.yaml) | 400 | ✓ | | ✓ | ✓ | no stars are simulated (flux set to 0) |
| [median_color](median_color.yaml) | 400 | ✓ | | ✓ | | PSFs evaluated at the median galaxy color (i.e., the color used for the mdet catalogs) |
| [grid-median_color](grid-median_color.yaml) | 400 | ✓ | | ✓ | | galaxies placed on a grid with PSFs evaluated at the median galaxy color |
| [grid](grid.yaml) | 400 | ✓ | | | ✓ | galaxies placed on a grid |

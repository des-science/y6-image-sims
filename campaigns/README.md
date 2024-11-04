# campaigns

| config | # tiles | constant shear (2) | redshift shear (10) | mdet | bfd | description | ≈ node hours / tile / shear | ≈ node hours |
|---|---|---|---|---|---|---|---|---|
| [fiducial](fiducial.yaml) | 1000 | ✓ | ✓ | ✓ | ✓ | full-featured image simulation | 4 | 48,000 |
| [no_stars](no_stars.yaml) | 400 | ✓ | | ✓ | ✓ | no stars are simulated (flux set to 0) | 4 | 3,200 |
| [median_color](median_color.yaml) | 400 | ✓ | | ✓ | | PSFs evaluated at the median galaxy color (i.e., the color used for the mdet catalogs) | 2 | 1,600 |
| [grid-median_color](grid-median_color.yaml) | 400 | ✓ | | ✓ | | galaxies placed on a grid with PSFs evaluated at the median galaxy color | 2 | 1,600 |
| [grid](grid.yaml) | 400 | ✓ | | ✓ | ✓ | galaxies placed on a grid | 4 | 3,200 |
| [grid-exp](grid-exp.yaml) | 100 | ✓ | | ✓ | | bright exponentials placed on a grid with PSFs evaluated at the median galaxy color | 2 | 400 |

---

- constant shear: (0.02, 0.00) and (-0.02, 0.00) for z ∈ [0, 6]
- redshift shear: (0.02, 0.00) inside slice, (-0.02, 0.00) outside slice
- redshift slices: [0.0, 0.3], [0.3, 0.6], [0.6, 0.9], [0.9, 1.2], [1.2, 1.5], [1.5, 1.8], [1.8, 2.1], [2.1, 2.4], [2.4, 2.7], [2.7, 6.0]

---

grid-exp
| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |
|---|---|---|---|---|---|---|
| -2.657e-04 | 1.024e-04 | -8.789e-07 | 1.839e-06 | 1.838e-07 | 1.815e-06 | 97 |

grid-median_color
| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |
|---|---|---|---|---|---|---|
| -4.275e-03 | 9.904e-03 | 5.132e-05 | 3.748e-04 | 8.455e-06 | 3.726e-04 | 395 |

grid
| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |
|---|---|---|---|---|---|---|
| -3.831e-03 | 1.009e-02 | 2.938e-05 | 3.755e-04 | -5.480e-05 | 3.724e-04 | 395 |

no_stars
| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |
|---|---|---|---|---|---|---|
| 3.517e-03 | 9.477e-03 | 5.952e-05 | 3.920e-04 | 3.816e-05 | 4.118e-04 | 395 |

median_color
| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |
|---|---|---|---|---|---|---|
| 3.420e-03 | 9.813e-03 | 9.797e-05 | 3.986e-04 | 8.296e-05 | 4.142e-04 | 395 |

fiducial
| m mean | 3 * m std | c_1 mean | 3 * c_1 std | c_2 mean | 3 * c_2 std | # tiles |
|---|---|---|---|---|---|---|
| 3.455e-03 | 9.709e-03 | 6.292e-05 | 3.987e-04 | 1.062e-05 | 4.170e-04 | 395 |

---

fiducial - median_color
| dm mean | 3 * dm std | dc_1 mean | 3 * dc_1 std | dc_2 mean | 3 * dc_2 std | # tiles |
|---|---|---|---|---|---|---|
| 3.453e-05 | 2.017e-03 | -3.505e-05 | 2.466e-05 | -7.234e-05 | 2.487e-05 | 395 |


fiducial - no_stars
| dm mean | 3 * dm std | dc_1 mean | 3 * dc_1 std | dc_2 mean | 3 * dc_2 std | # tiles |
|---|---|---|---|---|---|---|
| -6.255e-05 | 3.675e-03 | 3.396e-06 | 6.545e-05 | -2.754e-05 | 6.581e-05 | 395 |


grid - grid_median_color
| dm mean | 3 * dm std | dc_1 mean | 3 * dc_1 std | dc_2 mean | 3 * dc_2 std | # tiles |
|---|---|---|---|---|---|---|
| 4.443e-04 | 1.697e-03 | -2.194e-05 | 2.228e-05 | -6.325e-05 | 2.155e-05 | 395 |

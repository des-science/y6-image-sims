import des_y6utils


def get_selection(data, version=6):
    # msk = (
    #     ((data["mask_flags"] & (~16)) == 0)
    #     & (data["gauss_flags"] == 0)
    #     & (data["gauss_psf_flags"] == 0)
    #     & (data["gauss_obj_flags"] == 0)
    #     & (data["psfrec_flags"] == 0)
    # )

    # MASK_TILEDUPE = 2**4
    # apply this to sims to handle edge effects of tiles
    # msk = ((data["mask_flags"] & (~16)) == 0)
    data["mask_flags"] = data["mask_flags"] & (~16)

    msk = des_y6utils.mdet.make_mdet_cuts(data, str(version))

    # apply other selections as in data
    msk &= (
        (data['psfrec_flags'] == 0) &
        (data['gauss_flags'] == 0) &
        (data['gauss_s2n'] > 5) &
        (data['pgauss_T_flags'] == 0) &
        (data['pgauss_s2n'] > 5) &
        (data['pgauss_band_flux_flags_g'] == 0) &
        (data['pgauss_band_flux_flags_r'] == 0) &
        (data['pgauss_band_flux_flags_i'] == 0) &
        (data['pgauss_band_flux_flags_z'] == 0) &
        (data['mask_flags'] == 0) &
        (data['shear_bands'] == '123')
    )

    # apply metadetect cuts
    # msk &= des_y6utils.mdet.make_mdet_cuts(data, str(version))
    # msk &= data["gauss_T_ratio"] > 0.5
    # msk &= data["gauss_s2n"] > 10
    # msk &= data["mfrac"] < 0.1

    return msk



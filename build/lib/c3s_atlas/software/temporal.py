import xarray


def infer_freq(ds: xarray.Dataset):
    """
    Infer the frequency of time values in the given xarray Dataset.

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset containing time values.

    Returns
    -------
    str
        The inferred frequency of time values. If only one time value is present,
        it returns 'MS' (Month Start); otherwise, it infers the frequency using
        xarray's infer_freq function and returns the result as a string.
    """
    if len(ds.time) == 1:
        return "MS"
    else:
        dataset_frequency = xarray.infer_freq(ds.time)
        return dataset_frequency

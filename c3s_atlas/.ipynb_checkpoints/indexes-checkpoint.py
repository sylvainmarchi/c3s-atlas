import xarray as xr
import numpy as np

def heating_degree_days(
    tas: xr.DataArray | None = None,
    tasmax: xr.DataArray | None = None,
    tasmin: xr.DataArray | None = None,
    freq: str = "YS",
    thresh: float = 15.5,
 ) -> xr.DataArray:
    """
    Heating Degree days following Spinoni et al. (2014).

    Parameters
    ----------
    tas: xarray.DataArray,
        DataArray storing the variable tas
    tasmax: xarray.DataArray,
        DataArray storing the variable tasmax
    tasmin: xarray.DataArray,
        DataArray storing the variable tasmin
    freq : str
        Resampling frequency.
    thresh : float, optional
        threshold in Celsius degrees above which heating degree days are computed,
        by default 15

    Returns
    -------
    xarray.DataArray
        DataArray storing the variable hdd accumulated at the desire temporal resolution.

    Notes
    -----
    The Heating Degree Days (HDD) are a measure of how much (in degrees) and
    for how many days the daily mean temperature was below a specific threshold.
    """
    if tas is None or tasmax is None or tasmin is None:
        raise ValueError("tas, tasmax, and tasmin must all be provided")

    hdd = xr.zeros_like(tas.copy())
    #hdd = tas.copy(deep=True)
    mask = thresh >= tasmax.values
    hdd = xr.where(mask, thresh - tas, hdd)
    mask = np.logical_and(thresh >= tas, thresh < tasmax.values)
    hdd = xr.where(mask, 0.5 * (thresh - tasmin) - 0.25 * (tasmax - thresh), hdd)
    mask = np.logical_and(thresh >= tasmin.values, thresh < tas)
    hdd = xr.where(mask, 0.25 * (thresh - tasmin), hdd)
    mask = thresh <= tasmin.values
    hdd = xr.where(mask, 0, hdd)

    return hdd.resample(time = freq).sum()

def cooling_degree_days(
    tas: xr.DataArray | None = None,
    tasmax: xr.DataArray | None = None,
    tasmin: xr.DataArray | None = None,
    freq: str = "YS",
    thresh: float = 22,
 ) -> xr.DataArray:
    """

    Cooling Degree days following Spinoni et al. (2014).

    Parameters
    ----------
    tas: xarray.DataArray,
        DataArray storing the variable tas
    tasmax: xarray.DataArray,
        DataArray storing the variable tasmax
    tasmin: xarray.DataArray,
        DataArray storing the variable tasmin
    freq : str
        Resampling frequency.
    thresh : float, optional
        threshold in Celsius degrees below which cooling degree days are computed, by default 15

    Returns
    -------
    xarray.DataArray
        DataArray storing the variable cdd accumulated at annual temporal resolution

    Notes
    -----
    The Cooling Degree Days (CDD) are a measure of how much (in degrees) and for
    how many days the daily mean temperature was above a specific threshold
    A high CDD number means that the outdoor temperature is well above the
    summer comfort temperature and that a high amount of energy
    would subsequently be required to cool down buildings.
    """
    if tas is None or tasmax is None or tasmin is None:
        raise ValueError("tas, tasmax, and tasmin must all be provided")

    cdd = xr.zeros_like(tas.copy())
    #cdd = tas.copy(deep=True)
    mask = thresh >= tasmax
    cdd = xr.where(mask, 0, cdd)
    mask = (thresh >= tas) & (thresh < tasmax)
    cdd = xr.where(mask, 0.25 * (tasmax - thresh), cdd)
    mask = (thresh >= tasmin) & (thresh < tas)
    cdd = xr.where(mask, 0.5 * (tasmax - thresh) - 0.25 * (thresh - tasmin), cdd)
    mask = thresh <= tasmin
    cdd = xr.where(mask, tas - thresh, cdd)

    return cdd.resample(time = freq).sum()


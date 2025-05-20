import xarray
import cftime
import re

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

def add_time(ds: xarray.Dataset) -> xarray.Dataset:
    """
    Decodes the 'time' coordinate in an xarray Dataset when it is opened with decode_times=False.
    It uses the 'units' and 'calendar' attributes from the 'time' variable to reconstruct the dates.

    Parameters:
        ds (xr.Dataset): An xarray dataset with a non-decoded time coordinate 
                         (opened with decode_times=False).

    Returns:
        xr.Dataset: A new dataset with the 'time' coordinate decoded to datetime objects
                    (either pandas.DatetimeIndex or cftime objects, depending on the calendar).
    
    Raises:
        ValueError: If no 'time' variable is found or the time units are invalid.
    """
    if "time" not in ds.variables:
        raise ValueError("No 'time' variable found in the dataset.")
    
    time_var = ds["time"]
    time_units = time_var.attrs.get("units", "")
    calendar = time_var.attrs.get("calendar", "standard")  # Default calendar

    # Parse the units string, e.g., "days since 1850-01-01"
    match = re.match(r"(\w+) since ([0-9\- :Tt]+)", time_units)
    if not match:
        raise ValueError(f"Could not interpret time units: '{time_units}'")
    
    unit, reference_date_str = match.groups()

    # Convert numeric time values to dates using cftime
    time_vals = time_var.values
    dates = cftime.num2date(time_vals, units=time_units, calendar=calendar)

    # Attempt to convert to pandas datetime if calendar is compatible
    try:
        time = pd.to_datetime(dates)
    except Exception:
        time = dates  # fallback to cftime objects for non-standard calendars

    # Assign decoded time coordinate
    ds = ds.assign_coords(time=("time", time))

    return ds

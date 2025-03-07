import datetime
from typing import Union

import cftime
import pandas
import xarray
from dateutil.relativedelta import relativedelta

from c3s_atlas.aggregation import AggregationFunction, aggregate_in_time
from c3s_atlas.errors import InferFrequencyError
from c3s_atlas.logger import get_logger
from c3s_atlas.temporal import infer_freq
from c3s_atlas.units import convert_units

logger = get_logger(name="Homogenization-fixers")


def fix_time(dataset: xarray.Dataset):
    """
    Adjust time-related attributes and values in the input dataset to a standardized format.

    Parameters
    ----------
    dataset : xarray.Dataset
        The input xarray Dataset containing time-related data.

    Returns
    -------
    xarray.Dataset
        A modified Dataset with time attributes adjusted to a standardized format.
    """
    if "time_counter" in dataset.dims:
        dataset = dataset.rename({"time_counter": "time"})
    dataset_frequency, coerced = infer_dataset_frequency(dataset)
    if dataset_frequency == "MS" or dataset_frequency == "YS":
        #logger.info(
        #    "The data is in monthly resolution, "
        #    "so there's no need to adjust the calendar, instead, "
        #    "we will apply a resampling process to standarize the time values"
        #)
        dataset = dataset.resample(time=dataset_frequency).mean()
        if (
            type(dataset.time.values[0]) == cftime._cftime.DatetimeNoLeap
            or type(dataset.time.values[0]) == cftime._cftime.Datetime360Day
            or type(dataset.time.values[0]) == cftime.DatetimeJulian
        ):
            datetime_object = [
                datetime.datetime(year=d.year, month=d.month, day=d.day)
                for d in dataset.time.values
            ]
            dataset["time"] = datetime_object
        return dataset
    else:
        dataset = fix_non_standard_calendar(dataset, coerced, dataset_frequency)
        return dataset


def fix_non_standard_calendar(
    dataset: xarray.Dataset, coerced, dataset_frequency
) -> xarray.Dataset:
    """
    Fix non-standard calendars.

    Function to change time with different calendar, if the frequency of the data is
    monthly just change the datatype,  if the frequency is daily calendars
    e.g UK models with leap year are solved

    Parameters
    ----------
    dataset (xarray.Dataset): data stored by dimensions

    Returns
    -------
    dataset (xarray.Dataset): dataset with the correct calendar
    """
    logger.info(f"Fixing calendar for {dataset}")
    dataset = dataset.assign_coords(time=coerced)
    if coerced[-1].month == 12 and coerced[-1].day == 30:
        real_time = pandas.date_range(
            start=coerced[0],
            end=coerced[-1] + datetime.timedelta(days=1),
            freq=dataset_frequency,
        )
    else:
        real_time = pandas.date_range(
            start=coerced[0].replace(day=1), end=coerced[-1], freq=dataset_frequency
        )
    # Removing 29 (no leap years) and 30 feb
    dataset = dataset.where(~dataset.time.isnull(), drop=True)
    # Filling missing dates (31 of every month)
    dataset = dataset.reindex({"time": real_time}, method="ffill")
    return dataset


def infer_dataset_frequency(dataset):
    """
    Infer dataset frequency (daily, monthly, ...).

    Function to infer the time frequency of the dataset and return the new time
    object in daily or hourly format

    Parameters
    ----------
    dataset (xarray.Dataset): data stored by dimensions

    Returns
    -------
    dataset_frequency (str): frequency of the dataset
    coerced (pandas.Datetime): dates stored in pandas object
    """
    try:
        dataset_frequency = infer_freq(dataset)
        if dataset_frequency == "D":
            string_dates = [str(d)[:10] for d in dataset.time.values]
        elif (
            dataset_frequency == "H"
            or dataset_frequency == "6H"
            or dataset_frequency == "h"
            or dataset_frequency == "3H"
        ):
            string_dates = [str(d) for d in dataset.time.values]
        elif dataset_frequency == "MS":
            string_dates = [str(d)[:10] for d in dataset.time.values]
        elif dataset_frequency is None or dataset_frequency == "30D":
            string_dates = [str(d)[:10] for d in dataset.time.values]
            dataset_frequency = "MS"
        elif "AS" in dataset_frequency or "YS" in dataset_frequency:
            string_dates = [str(d)[:10] for d in dataset.time.values]
            dataset_frequency = "YS"
    except InferFrequencyError:
        raise InferFrequencyError(
            f"Cannot infer the frequency of the dataset: {dataset}"
        )
    coerced = pandas.to_datetime(string_dates, errors="coerce")
    return dataset_frequency, coerced


def fix_inverse_latitudes(
    dataset: xarray.Dataset, project: str, latname: str = "lat"
) -> xarray.Dataset:
    """
    Sorts the dataset along the latitude dimension.

    Parameters
    ----------
    dataset : xarray.Dataset
        The dataset to be processed.
    project : str
        The name of the project.
    latname : str, optional
        The name of the latitude dimension, by default "lat".

    Returns
    -------
    xarray.Dataset
        The processed dataset.

    """
    latname = latname if "cordex" not in project else "lon"
    if "cordex" not in project and len(dataset.lat.shape) != 2:
        dataset = dataset.sortby(latname)
    return dataset


def check_temporal_resolution(dataset: xarray.Dataset):
    """
    Check the temporal resolution of the time index in an xarray dataset.

    Parameters
    ----------
    dataset : xarray.Dataset
        Dataset containing a 'time' dimension.

    Raises
    ------
    ValueError
        If the inferred temporal resolution is not 'D' (Day) or 'MS' (Month Start).
    """
    freq = pandas.infer_freq(dataset.time)

    # Check if the inferred frequency is within acceptable range
    if freq not in ["D", "MS"]:
        raise ValueError(
            f"The inferred temporal resolution ({freq}) is not 'D' or 'MS'."
        )


def fix_360_longitudes(
    dataset: xarray.Dataset, project: str, lonname: str = "lon"
) -> xarray.Dataset:
    """
    Fix longitude values.

    Function to transform datasets where longitudes are in (0, 360) to (-180, 180).

    Parameters
    ----------
    dataset (xarray.Dataset): data stored by dimensions
    project (str): project of the process e.g CMIP6, CORDEX...
    lonname (str): name of the longitude dimension

    Returns
    -------
    dataset (xarray.Dataset): data with the new longitudes
    """
    lonname = lonname if "cordex" not in project else "lon"
    lon = dataset[lonname]
    if lon.max().values > 180 and lon.min().values >= 0:
        dataset[lonname] = dataset[lonname].where(lon <= 180, other=lon - 360)
    if "cordex" not in project and len(dataset.lat.shape) != 2:
        dataset = dataset.reindex(**{lonname: sorted(dataset[lonname])})
    return dataset


def fix_spatial_coord_names(dataset: xarray.Dataset) -> xarray.Dataset:
    """
    Fix the coordinates names for spatial coordinates (x, y, lon, lat, ...).

    Function to renaming all spatial coords into lon and lat to chunk more easily later

    Parameters
    ----------
    dataset (xarray.Dataset): data stored by dimensions

    Returns
    -------
     dataset (xarray.Dataset): data with the remaining coordinates "lon" and "lat"
    """
    coordinate_mappings = {
        ("rlon", "rlat", "longitude", "latitude"): {
            "rlon": "x",
            "rlat": "y",
            "longitude": "lon",
            "latitude": "lat",
        },
        ("nav_lon", "nav_lat"): {"nav_lon": "lon", "nav_lat": "lat"},
        ("i", "j", "longitude", "latitude"): {
            "i": "x",
            "j": "y",
            "longitude": "lon",
            "latitude": "lat",
        },
        ("rlon", "rlat"): {"rlon": "x", "rlat": "y"},
        ("nj", "ni"): {"ni": "x", "nj": "y"},
        ("lon", "lat"): {"lon": "lon", "lat": "lat"},
        ("x", "y"): {"x": "lon", "y": "lat"},
        ("longitude", "latitude"): {"longitude": "lon", "latitude": "lat"},
    }
    for coords, mapping in coordinate_mappings.items():
        if all(coord in dataset.dims or coord in dataset.coords for coord in coords):
            if coords == ("lon", "lat"):
                logger.info("Dataset has already the correct names for its coordinates")
                return dataset
            logger.info(f"Fixing coordinates names: {mapping}")
            return dataset.rename(mapping)


def adding_coords(ds: xarray.Dataset):
    """
    Adding dimensions to coordinates if needed.

    Parameters
    ----------
    ds : xarray.Dataset
        The input Dataset to be reordered.

    Returns
    -------
    xarray.Dataset
        The dataset with the coordinates.

    """
    if "x" in ds.dims and "x" not in ds.coords:
        ds = ds.assign_coords({"x": ds.x, "y": ds.y})
        return ds
    else:
        return ds


def reorder_dimensions(ds: xarray.Dataset):
    """
    Reorders the dimensions of an xarray Dataset.

    Parameters
    ----------
    ds : xarray.Dataset
        The input Dataset to be reordered.

    Returns
    -------
    xarray.Dataset
        The reordered Dataset.

    """
    if list(ds.dims) == ["time", "x", "y"]:
        ds = ds.transpose("time", "y", "x")
    return ds


def resampled_by_temporal_aggregation(
    ds: xarray.Dataset, var_mapping: Union[dict, None]
):
    """
    Resample by time.

    Function to resample the hourly data to daily infer the aggregation function

    Parameters
    ----------
    ds (xarray.Dataset): data stored by dimensions
    var_mapping (dict): dictionary for mapping the variables of the different datasets

    Returns
    -------
    ds (xarray.Dataset): daily data stored by dimensions
    """
    # first infer the dataset frequency
    ds_freq = infer_freq(ds)
    if ds_freq == "H" or ds_freq == "h" or ds_freq == "6H" or ds_freq == "3H":
        logger.info(
            "The dataset is in hourly resolution, we need to resample it to "
            "daily resolution"
        )
        # load the temporal aggregation from the mapping
        var_name = list(ds.data_vars)[0]
        if var_name == "pr":
            ds["time"] = [
                pandas.to_datetime(x) - relativedelta(hours=1) for x in ds.time.values
            ]
        temporal_agg = var_mapping["aggregation"][var_name]
        temporal_agg_function = AggregationFunction(temporal_agg)
        # apply the resample and the aggregation method
        ds = aggregate_in_time(ds, temporal_agg_function)
        logger.info("Dataset resampled to daily resolution")
    else:
        logger.info(
            "The dataset is in daily or monthly resolution, we don't need to "
            "resample it from hourly frequency"
        )
    check_temporal_resolution(ds)
    return ds


def rename_and_delete_variables(
    ds: xarray.Dataset, variable: str, var_mapping: Union[dict, None]
) -> xarray.Dataset:
    """
    Remove unused data.

    Function to remove variables and dimensions not used.

    Parameters
    ----------
    ds (xarray.Dataset): data stored by dimensions
    variable (str): variable to rename
    var_mapping (dict): dictionary for mapping the variables of the different datasets

    Returns
    -------
    xarray.Dataset: dataset with unnecessary coordinates removed
    """
    # select the main variable
    if variable not in list(ds.data_vars):
        try:
            var_name = var_mapping["dataset_variable"][variable]
        except KeyError:
            logger.info(
                "There is no variable to rename in the "
                "map variables configuration file, "
                "assuming the dataset variable name"
            )
            var_name = variable
    else:
        var_name = variable
    # rename variable
    ds = ds.rename_vars({var_name: variable})
    # drop height as dimensions
    if "height" in ds.dims:
        ds = ds.squeeze("height")
    # adding height coordinate
    ds = ds.assign_coords({"height": 2.0})
    # avoiding useless variables
    ds = ds[[variable]]
    # delete useless dimensions
    main_coords = ["time", "lon", "lat", "height", "x", "y"]
    if sorted(list(ds.coords)) != sorted(main_coords):
        dim_to_remove = [dim for dim in list(ds.coords) if dim not in main_coords]
        ds = ds.drop_vars(dim_to_remove)
    return ds

def standard_names(ds: xarray.Dataset) -> xarray.Dataset:
    """
    Function to include standar-names to coordinate variables
    
    Parameters
        ----------
        ds: xarray.Dataset,
            xarray Dataset
    
        Returns
        -------
        xarray.Dataset
            Dataset with standar names for coordinates variables
        
    """
    if ('lat' in ds.variables) and ('lon' in ds.variables):
        ds.lat.attrs['standard_name'] = 'latitude'
        ds.lon.attrs['standard_name'] = 'longitude'
    if ('latitude' in ds.variables) and ('longitude' in ds.variables):
        ds.latitude.attrs['standard_name'] = 'latitude'
        ds.longitude.attrs['standard_name'] = 'longitude'
    if 'time' in ds.variables:
        ds.time.attrs['standard_name'] = 'time'

    return ds

def apply_fixers(ds, variable, project_id, map_variables):
    """
    Apply the data fixers to the data.

    Parameters
    ----------
    ds (xarray.Dataset): data stored by dimensions

    Returns
    -------
    ds (xarray.Dataset): data with the spatial, time and units fixers applied
    """
    ds = fix_spatial_coord_names(ds)
    ds = fix_time(ds)
    ds = rename_and_delete_variables(ds, variable, map_variables)
    ds = convert_units(ds, project = project_id)
    ds = fix_360_longitudes(ds, project = project_id)
    ds = fix_inverse_latitudes(ds, project = project_id)
    ds = resampled_by_temporal_aggregation(ds, map_variables)
    ds = reorder_dimensions(ds)
    ds = adding_coords(ds)
    ds = standard_names(ds)
    return ds

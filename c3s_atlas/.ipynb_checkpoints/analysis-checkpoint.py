import xarray as xr
import array as arr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
import regionmask
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
import regionmask
import cartopy.feature as cfeature
import scipy as sp

from c3s_atlas.utils import(
 count_years)

def mean_values_map(ds, var, model, mode,  diff = None, months=None, season=None,
                    period=slice('2081', '2100'),
                    baseline_period=slice('1981', '2010'), GWLs_ds = None):
    '''
    Divides the provided data into 3 categories of robustness for each latitude and longitude.

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset containing the climate data.
    var : str
        The name of the variable to calculate robustness for.
    mode : str
        The mode of calculation. Can be 'climatology' or 'change'.
    model : str
        The model used for the calculations.
    diff : str
        The type of difference calculation. Can be 'abs' for absolute difference or 'rel' for relative difference.
    months : list, optional
        Specific months to include in the calculation. If provided, it overrides the season parameter. Default is None.
    season : str, optional
        The season for which to calculate the mean. Can be 'Annual', 'DJF', 'MAM', 'JJA', or 'SON'. Default is 'Annual'.
    period : slice, optional
        The period for which to calculate robustness. Default is slice('2081', '2100').
    baseline_period : slice, optional
        The baseline period for calculating the mean baseline. Default is slice('1981', '2010').
    ds_GWLs: xarray Dataset, optional
        The dataset containing the variable mean for global warning levels. Default is None.
    Returns
    -------
    ds_mean : xarray.DataArray
        The dataset with the mean values calculated according to the specified mode and difference type.
    '''
    
    # If specific months are provided, select only those months from the dataset
    if season:
        ds = ds.sel(time=ds['time.month'].isin(season))
        if GWLs_ds is not None:
            GWLs_ds = GWLs_ds.sel(month = GWLs_ds['month'].isin(season))
        
    # Calculate the mean based on the selected mode
    if model in ["ERA5", "ERA5-Land", "E-OBS", "ORAS5"]:# models that don't have member                          
        if mode == 'climatology':
            ds = ds.sel(time = period)
            ds_mean = ds[var].mean('time', skipna=True)
        elif mode == 'change':
            ds_baseline = ds[var].sel(time=baseline_period).mean('time', skipna=True)
            ds_period = ds[var].sel(time=period).mean('time', skipna=True)
            if diff == 'abs':
                ds_mean = ds_period - ds_baseline
            elif diff == 'rel':
                ds_mean = (ds_period - ds_baseline) / abs(ds_baseline) * 100
    else:
        if mode == 'climatology':
            ds_mean = ds[var].mean(dim=['time','member'], skipna=True)
        elif mode == 'change':
            if GWLs_ds is not None:
                ds_period = GWLs_ds[var].mean(dim=['month','member'], skipna=True)
            else:
                ds_period = ds[var].sel(time=period).mean(dim=['time','member'], skipna=True)
            ds_baseline = ds[var].sel(time=baseline_period).mean(dim=['time','member'], skipna=True)
            if diff == 'abs':
                ds_mean = ds_period - ds_baseline
            elif diff == 'rel':
                ds_mean = (ds_period - ds_baseline) / abs(ds_baseline) * 100
    return ds_mean

def categories_robustness(ds, var, months = None, season = None, period=slice('2081', '2100'),
                          baseline_period=slice('1981', '2010'), GWLs_ds = None):
    '''
    Divides the provided data into 3 categories of robustness for each latitude and longitude.

    Parameters
    ----------
    ds : xarray.Dataset
        Data stored by dimensions.
    var : str
        The name of the variable to calculate robustness for.
    months : list, optional
        Specific months to include in the calculation, overrides season if provided. Default is None.
    season : str, optional
        The season for which to calculate the mean ('Annual', 'DJF', 'MAM', 'JJA', 'SON').
    period : slice, optional
        The period for which to calculate robustness. Default is slice('2081', '2100').
    baseline_period : slice, optional
        The baseline period for calculating the mean baseline. Default is slice('1981', '2010').
    ds_GWLs: xarray Dataset, optional
        The dataset containing the variable grouped by month for global warning levels.. Default is None.
    Returns
    -------
    categories : xr.DataArray
        Matrix with the data divided into the categories.
    '''

    
     # If specific months are provided, select only those months from the dataset
    if season:
        ds = ds.sel(time=ds['time.month'].isin(season))
        if GWLs_ds is not None:
            GWLs_ds = GWLs_ds.sel(month = GWLs_ds['month'].isin(season))
    
    # Select the dataset for the given period
    if GWLs_ds is not None:
        mean_period = GWLs_ds[var].mean(dim=['month'], skipna=True)
        years_count = 20
    else:
        mean_period = ds[var].sel(time=period).mean(dim='time', skipna=True)
        # count the years of period
        years_count = count_years(period)
    
    # Select the dataset for the baseline period
    mean_baseline = ds[var].sel(time=baseline_period).mean(dim = 'time', skipna=True)
    
    # Change 
    change = mean_baseline - mean_period
    
    # Determine the sign of the change
    sign_change = np.sign(change)
    
    # Initialize an empty DataArray to store the sign of the change for each grid point
    sign_models = xr.DataArray(np.zeros_like(sign_change.isel(member=0)),
                               coords={'lat': sign_change['lat'], 'lon': sign_change['lon']},
                               dims=['lat', 'lon'])

    
    # Calculate the sum of the sign of the change for each grid point
    for i in sign_change['lon'].values:
        for j in sign_change['lat'].values:
            sign_models.loc[dict(lat=j, lon=i)] = sign_change.sel(lat=j, lon=i).sum()

                              
    # Select the dataset for 1971 -2005
    ds_reference_ys = ds.sel(time=slice('1971', '2005')).resample(time = 'YS').mean()
                              
    # Calculate the standard deviation of temperature across years
    std = ds_reference_ys.std(dim='time')

    # Calculate the variability using a specified threshold
    threshold = 1.645 * np.sqrt(2/years_count) * std #error
    
    # Create a mask to identify significant changes
    significant_change_mask = abs(threshold[var]) < abs(change)
    
    # Initialize a DataArray to count the number of models indicating significant change
    num_models = xr.DataArray(np.zeros_like(threshold[var].isel(member = 0)), 
                              coords={'lat': threshold['lat'], 'lon': threshold['lon']},
                              dims=['lat', 'lon'])   
                                  
    # Iterate over each latitude, longitude, and model
    for i in threshold['lon'].values:
        for j in threshold['lat'].values:
            for m in threshold['member'].values:
                # Increment the count if there is a significant change
                if significant_change_mask.sel(lat=j, lon=i, member=m).values:
                    num_models.loc[dict(lat=j, lon=i)] += 1  
                              
    # Calculate the total number of members
    total_members = len(ds['member'].values)
    
    # Create a DataArray to store the categories
    categories = xr.DataArray(np.zeros_like(threshold[var].isel(member = 0)), 
                                  coords={'lat': threshold['lat'], 'lon': threshold['lon']}, 
                                  dims=['lat', 'lon'])


    # Iterate over each longitude and latitude
    for i in num_models['lon'].values:
        for j in num_models['lat'].values:
            # Category (i): Areas with significant change and high model agreement
            # 60 because it is 1 and -1, so if 80% agrees it is 80% (same sign) 20% (other sign)
            if abs(sign_models.sel(lat=j, lon=i)) >= 0.60 * total_members and num_models.sel(lat=j, lon=i) >= (2/3) * total_members:
                categories.loc[dict(lat=j, lon=i)] = 1
            # Category (ii): Areas with no change or no robust change
            elif num_models.sel(lat=j, lon=i) < (2/3) * total_members:
                categories.loc[dict(lat=j, lon=i)] = 2
            # Category (iii): Areas with significant change but low agreement
            elif num_models.sel(lat=j, lon=i) >= (2/3) * total_members and abs(sign_models.sel(lat=j, lon=i)) < 0.60 * total_members:
                categories.loc[dict(lat=j, lon=i)] = 3
    
    return categories, sign_models, num_models

def annual_weighted_average(ds, var, season = None, months = None, 
                            trend = False, trend_period = slice('1950','2020')):
    '''''
    This function calculates the mean weighted (cos(lat)) of a specific variable over the years in an xarray dataset.
    
    Parameters:
    ----------
    ds: xarray Dataset
        The dataset containing the variable.
    var: str
        The name of the variable to calculate the mean for.
     season: str
         The season for which to calculate the mean ('Annual', 'DJF', 'MAM', 'JJA', 'SON').
    months: list
        Specific months to include in the calculation, overrides season if provided.
    
    Returns:
    ----------
    ds_years: xarray DataArray
            The dataset with the variable's mean calculated over the years.
    '''''
     # If specific months are provided, select only those months from the dataset
    if season:
        ds = ds.sel(time=ds['time.month'].isin(season))
          
    dates = pd.to_datetime(ds['time'].values)
    years = np.array([date.year for date in dates])
    ds_w_years = ds.assign_coords(year=('time', years))
    ds_years = ds_w_years[var].groupby('year').mean(dim=['time'], skipna=True)
    #add weights
    weights = np.cos(np.deg2rad(ds_years['lat']))
    ds_years_weighted = ds_years.weighted(weights).mean(dim=['lat', 'lon'], skipna=True)
    
    if trend == True:
        # Perform linear regression
        results = sp.stats.linregress(ds_years_weighted.sel(year = trend_period).year, 
                                      ds_years_weighted.sel(year = trend_period).values)
        return ds_years_weighted, results
    else:    
        return ds_years_weighted
    
def monthly_weighted_average(ds, var, mode = None, diff = None, baseline_period=None, period = None, ds_GWLs = None):
    '''
    This function calculates the mean weighted (cos(lat)) of a specific variable over the months in an xarray dataset.
    
    Parameters:
    ----------
    ds: xarray Dataset
        The dataset containing the variable.
    var: str
        The name of the variable to calculate the mean for.
    mode: (str, optional): 
        The calculation mode, can be "climatology" or "change". Default is None.
    diff: str, optional
        Type of difference to calculate ("abs" for absolute, "rel" for relative). Default is None.
    baseline_period: slice, optional
        The time period to be considered as the baseline for calculating the mean. Default is None.
    period: slice, optional
        The time period to calculate the mean for in "change" mode. Default is None.
    ds_GWLs: xarray Dataset, optional
        The dataset containing the variable grouped by month. Default is None.
    
    Returns:
    ----------
    ds_months_weighted: xarray DataArray
        The dataset with the variable's mean calculated over the months, with weights applied.
    '''
    if mode == "climatology":
        # Extracting month information from the time dimension
        dates = pd.to_datetime(ds['time'].values)
        months = np.array([date.month for date in dates])
        # Assigning month coordinates to the dataset
        ds_w_months = ds.assign_coords(month=('time', months))
        
        # Calculating mean for each month
        ds_months = ds_w_months[var].groupby('month').mean(dim='time', skipna=True)
    
        weights = np.cos(np.deg2rad(ds_months['lat']))
        ds_months_weighted = ds_months.weighted(weights).mean(dim=['lat', 'lon'], skipna=True)
    if mode == "change":
        # Extracting month information from the time dimension
        dates = pd.to_datetime(ds['time'].values)
        months = np.array([date.month for date in dates])
        # Assigning month coordinates to the dataset
        ds_w_months = ds.assign_coords(month=('time', months))
        if ds_GWLs is not None:
            weights_GWLs = np.cos(np.deg2rad(ds_GWLs['lat']))
            ds_months_weighted_period = ds_GWLs[var].weighted(weights_GWLs).mean(
                dim=['lat', 'lon'], skipna=True)
        else:
            # Calculating mean for each month
            ds_months = ds_w_months[var].sel(time = period).groupby('month').mean(
                dim='time', skipna=True)
            weights = np.cos(np.deg2rad(ds_months['lat']))
            
            # Adding weights based on latitude
            ds_months_weighted_period = ds_months.weighted(weights).mean(
                dim=['lat', 'lon'], skipna=True)
                
        # Calculating mean for each month within the baseline period   
        ds_months_baseline = ds_w_months[var].sel(time = baseline_period).groupby('month').mean(dim='time', skipna=True)
        weights = np.cos(np.deg2rad(ds_months_baseline['lat']))
        ds_months_weighted_baseline = ds_months_baseline.weighted(weights).mean(
            dim=['lat', 'lon'], skipna=True)

        # Calculating the difference if specified
        if diff== 'abs':
            ds_months_weighted=ds_months_weighted_period - ds_months_weighted_baseline
        elif diff== 'rel':
            ds_months_weighted=(ds_months_weighted_period - ds_months_weighted_baseline)/abs(ds_months_weighted_baseline) * 100
    return ds_months_weighted

def seasonal_stripes(ds,var, model):
    """
    Reshape the dataset into a matrix with months and years as dimensions.

    Parameters
    ----------
    ds : xr.Dataset
        The filtered ds
    var : str
        The name of the variable
    model : str
        The model used for the calculations.
    Returns
    -------
    xr.DataArray
        DataArray reshaped with months and years as dimensions.
    """
    if model in ["ERA5", "ERA5-Land", "E-OBS", "ORAS5"]:# models that don't have member 
        mean=ds[var]
    else:
        mean=ds[var].mean(dim=['member'])
    
    # Extract year and month from the time coordinate
    mean = mean.assign_coords(year=('time', mean['time.year'].values))
    mean = mean.assign_coords(month=('time', mean['time.month'].values))
    
    # Group by year and month and take the mean for each group
    reshaped = mean.groupby('year').apply(lambda x: x.groupby('month').mean(dim='time'))

    #add weights
    weights = np.cos(np.deg2rad(reshaped['lat']))
    reshaped_weighted = reshaped.weighted(weights).mean(dim=['lat', 'lon'], skipna=True)

    return reshaped_weighted

def significance_trends(ds, var, season = None, trend_period = slice('1950','2020')):
    """
    This function calculates and returns p-values for linear regression trends
    of a variable (`var`) across a specified time period (`trend_period`) for
    each latitude-longitude point in an xarray.Dataset (`ds`).
    
    Args:
      ds : xarray.Dataset 
      The input dataset containing the variable and time dimension.
      var: str
      The name of the variable in the dataset for which to calculate trends.
      trend_period :  list
      A list of two integers representing the start and end year
          of the trend period (inclusive).
    
    Returns:
      list: A list of dictionaries, each containing:
          - 'lat': Latitude value of the data point.
          - 'lon': Longitude value of the data point.
          - 'pvalue': p-value from the linear regression for this point.
    """
    if season:
        ds = ds.sel(time=ds['time.month'].isin(season))
        
    dates = pd.to_datetime(ds['time'].values)
    years = np.array([date.year for date in dates])
    ds_w_years = ds.assign_coords(year=('time', years))
    ds_years = ds_w_years.groupby('year').mean(dim=['time'], skipna=True)
    ds_years = ds_years.sel(year= trend_period)
    results = []  # Initialize a list to store results
    
    # Initialize a list to store significance points
    slope_matrix = np.full((len(ds.lat.values), len(ds.lon.values)), np.nan)
    pvalue_matrix = np.full((len(ds.lat.values), len(ds.lon.values)), np.nan)
    
    for lat_idx, lat in enumerate(ds.lat.values):
        for lon_idx, lon in enumerate(ds.lon.values):
            sub_ds = ds_years.sel(lat=lat, lon=lon)
            # Ensure the lengths match between variable and time
            result = sp.stats.linregress(sub_ds.year, sub_ds[var].values)  # Perform linear regression
            # store results
            pvalue_matrix[lat_idx, lon_idx] = result.pvalue
            slope_matrix[lat_idx, lon_idx] = result.slope

    ds['slope'] = (["lat", "lon"], slope_matrix)
    ds['pvalue'] = (["lat", "lon"], pvalue_matrix)
    
    return ds


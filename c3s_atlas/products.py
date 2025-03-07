import matplotlib.pyplot as plt
import xarray as xr
import array as arr
import numpy as np
import pandas as pd
import regionmask
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Patch

from c3s_atlas.utils import (
    get_attribute
)

def climate_stripe_plot(ds, var, attrs, mode, diff = "abs", season = 'Annual', period = None,
                        baseline_period=slice(1850, 1870), cmap = 'seismic', cbar_value=0) -> plt.Figure:
    """
    Plot climate stripes for a given dataset, based on the temporal aggregation.

    Parameters
    ----------
    ds : xr.Dataset
        The dataset containing temperature data.
    mode : str
        Mode of aggregation (e.g., 'monthly', 'seasonal', 'annual').
    diff : str
        Type of difference ('abs' for absolute, 'rel' for relative).
    season : list
        List of months (integers) representing the season (e.g., [12, 1, 2] for DJF).
    period : slice, optional
        The time period to consider for the plot. Default is 1850 to 2014.
    baseline_period : slice, optional
        The baseline period for comparison. Default is 1850 to 1870.
    cmap : str, optional
        The colormap for the plot. Default is 'seismic'.
    cbar_value : float, optional
        Value for centering the colorbar. Default is 0.

    Returns
    -------
    plt.Figure
        The matplotlib figure containing the climate stripes plot.
    """
    # select period
    ds = ds.loc[dict(year=period)]
    # Calculate the reference difference
    if mode == 'change':
        # Calculate absolute or relative difference
        if diff == "abs":
            values = ds - ds.loc[dict(year=baseline_period)].mean('year')
        elif diff == "rel":
            values = ((ds - ds.loc[dict(year=baseline_period)].mean('year')) /
                      abs(ds.loc[dict(year=baseline_period)].mean('year'))) * 100
    elif mode == 'climatology':
         values = ds
    
    values = values.transpose()  # Transpose the values for plotting
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(20, 10))

    if cbar_value == 0:
        max_values = values.max()
        min_values = values.min()
        if diff == 'rel':
            max_values = abs(values).max()
            min_values = - max_values
            
    else:
        max_value=abs(cbar_value)

        
    if attrs.get("project") in ["ERA5", "ERA5-Land", "E-OBS", "ORAS5"]: # project that don't have menber
        img = ax.pcolormesh(values.year, 1, values.transpose(), 
                            cmap = cmap, vmin = min_values.values.item(), 
                            vmax = max_values.values.item())  
    else:
        img = ax.pcolormesh(values.year, values.member, values.transpose(), 
                            cmap = cmap, vmin = min_values.values.item(), 
                            vmax = max_values.values.item())
        
        # Set ticks and labels for x-axis (member IDs)
        ax.set_yticks(np.arange(len(values.member_id)))
        ax.set_yticklabels(values.member_id.values)


    # Add colorbar
    cbar = fig.colorbar(img, ax=ax, extend='both')
    
    #set title
    name_var = get_attribute("variable", var)
    units = get_attribute("units", attrs.get("unit"))
    if units == None:
        units = attrs.get("unit")
    if diff == 'rel':
        units = "%"
    if mode == 'climatology':
        title = f'{name_var} ({units}) - {attrs.get("project")} - {mode}  - {attrs.get("scenario")}  - ({attrs.get("season_name")})'
    else:
         title = f'{name_var} ({units})- {attrs.get("project")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop}) - {attrs.get("scenario")}  - ({attrs.get("season_name")})'
    ax.set_title(title)
    
    return plt  # Return the plot object

def hatched_map_plot(ds, var, attrs, mode, diff = None, categories = None, period = None,
                     baseline_period = None, GWLs = None, cmap = 'Wistia_r', pvalue = 0.05):
    '''
    Plots the different areas of robustness on the map.
    
    Parameters:
    ----------
    ds : xr.Dataset
        The dataset containing the background data for the map.
    var : str
        The variable to be plotted.
    attrs : dict
        Additional attributes for the plot.
    mode : str
        The mode of plotting.
    diff : xr.DataArray, optional
        The difference data to be plotted.
    categories : list or tuple of str, optional
        The three different categories of robustness.
    period : str, optional
        The period of time considered.
    baseline_period : str, optional
        The baseline period for comparison.
    pvalue : float, optional
        Level of significance for the trend analysis
    
    Returns:
    -------
    plt.Figure
        The matplotlib figure containing the hatched map of robustness.
    '''

    fig = plt.figure(figsize=(60, 10))
    ax = fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())

    if mode == "trends":
        # Adjust colormap based on your preference
        max_values = np.nanmax(abs(ds['slope']*10))
        min_values = - max_values
        p = (ds['slope']*10).plot(cmap = cmap, vmin = min_values, vmax = max_values, ax = ax, cbar_kwargs={"label": f"Units: {attrs.get('unit')} per decade"})
         # Get latitude and longitude values
        lons, lats = np.meshgrid(ds.lon, ds.lat)
        
        #non significance trends
        ax.contourf(
            lons, lats, (ds['slope']*10).where(ds['pvalue'] > pvalue),
            transform=ccrs.PlateCarree(),
            colors='none',
            hatches='xxxx',
        )
         
        #Manually create legend
        legend_elements = [
            Patch(facecolor='none', edgecolor='black', hatch='', 
                  label='Significant trend (original color)'),
            Patch(facecolor='none', edgecolor='black', hatch='xxxx', 
                  label='Non significant trends')]
        ax.legend(handles=legend_elements, loc='center left', 
                  bbox_to_anchor=(0, -0.1),
                  prop={'size': 14})

    else:
        max_values = abs(ds).max().values.item()
        min_values = - max_values
        ds.plot(cmap = cmap, vmin = min_values, vmax = max_values)
    if mode == "change":
        # Get latitude and longitude values
        lons, lats = np.meshgrid(categories.lon, categories.lat)
        
        # Plot hatched areas for category 1shrink
        ax.contourf(
            lons, lats, categories.where(categories == 1),
            transform=ccrs.PlateCarree(),
            colors='none',
            hatches='',
        )
        
        # Plot hatched areas for category 2
        ax.contourf(
            lons, lats, categories.where(categories == 2),
            transform=ccrs.PlateCarree(),
            colors='none',
            hatches='\\\\',
        )
        
        # Plot hatched areas for category 3
        ax.contourf(
            lons, lats, categories.where(categories == 3),
            transform=ccrs.PlateCarree(),
            colors='none',
            hatches='xxxx',
        )
        
        # Manually create legend
        legend_elements = [
            Patch(facecolor='none', edgecolor='black', hatch='', 
                  label='Robust signal'),
            Patch(facecolor='none', edgecolor='black', hatch='\\\\\\\\', 
                  label='No change or no robust signal'),
            Patch(facecolor='none', edgecolor='black', hatch='xxxx', 
                  label='Conflicting signal')
        ]
        ax.legend(handles=legend_elements, loc='center left', 
                  bbox_to_anchor=(0, -0.1),
                  prop={'size': 14})
    
    # Add coastline
    ax.add_feature(cfeature.COASTLINE)

    #set title
    name_var = get_attribute("variable", var)
    units = get_attribute("units", attrs.get("unit"))
    if units == None:
        units = attrs.get("unit")
    if mode == 'climatology':
        title = f'{name_var} ({units}) - {attrs.get("project")} - {mode}  - {attrs.get("scenario")}  - ({attrs.get("season_name")})'
    elif GWLs:
         title = f'{name_var} ({units})- {attrs.get("project")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop})  - {attrs.get("scenario")}  - (warning {GWLs}°C ) - ({attrs.get("season_name")})'
    elif mode == 'change':
        title = f'{name_var} ({units})- {attrs.get("project")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop})  - {attrs.get("scenario")}  - ({period.start} - {period.stop}) - ({attrs.get("season_name")})'

    else:
        title = f'{name_var} ({units})- {attrs.get("project")} - {mode}  - {attrs.get("scenario")}  - ({period.start} - {period.stop}) - ({attrs.get("season_name")})'
    ax.set_title(title)

def annual_cycle(ds, var, attrs, mode, diff = None, 
                 baseline_period = slice('1850', '1870'), 
                 period = slice('2081', '2100'), GWLs = None):
    '''
    Function to visualize the annual cycle of climate data.

    Parameters:
    -----------
    ds : xarray.Dataset
        Input dataset containing climate data.
    var : str
        Name of the variable to analyze.
    attrs : dict
        Dictionary with the attributes.
    mode : str
        Mode of the analysis. Default is 'climatology'.
    diff : str, optional
        Type of difference to calculate ('abs' for absolute, 'rel' for relative, etc.). Default is None.
    baseline_period : slice, optional
        Baseline period for calculating mean baseline. Default is slice('1850', '1870').
    period : slice, optional
        Time period to consider for the analysis. Default is slice('2081', '2100').
    GWLs : xarray.Dataset, optional
        String containing the global warming level. Default is None.

    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure object containing the time series plot.
    '''
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(20, 15))
    
    if attrs.get("project") in ["ERA5", "ERA5-Land", "E-OBS"]:# project that don't have menber
        # Calculate mean line
        mean_change = ds
    else:
        members = ds['member'].count().values
        # Calculate mean line
        mean_change = ds.mean('member')
        time_plot = ds
    
        # Calculate change for each member and plot
        for m in range(members):
            time_plot.sel(member=m).plot(ax=ax, color='red', linewidth=0.5, linestyle = ':')
        ax.plot([], color='red', linewidth=0.25, linestyle = ":" ,label = attrs.get("project"))# to add it to the legend
        
        # Calculate percentiles and fill between them
        upper_90th_percentile = np.nanpercentile(time_plot, 90,
                                                 axis=time_plot.dims.index('member'))
        lower_10th_percentile = np.nanpercentile(time_plot, 10,
                                                 axis=time_plot.dims.index('member'))
        upper_75th_percentile = np.nanpercentile(time_plot, 75,
                                                 axis=time_plot.dims.index('member'))
        lower_25th_percentile = np.nanpercentile(time_plot, 25,
                                                 axis=time_plot.dims.index('member'))
        ax.fill_between(mean_change['month'], 
                        upper_90th_percentile, lower_10th_percentile, color='red',
                        alpha=0.25, label='P10 to P90')
        ax.fill_between(mean_change['month'],
                        upper_75th_percentile, lower_25th_percentile, color='red',
                        alpha=0.3,label='P25 to P75')
    
    # Plot the mean line
    mean_change.plot(ax=ax, color='red', linewidth=2, label='P50 (Median)')

    #set title
    name_var = get_attribute("variable", var)
    units = get_attribute("units", attrs.get("unit"))
    if units == None:
        units = attrs.get("unit")
    if diff == 'rel':
        units = "%"
    if mode == 'climatology':
        title = f'{name_var} ({units}) - {attrs.get("project")} - {mode}  - {attrs.get("scenario")}'
    elif GWLs:
         title = f'{name_var} ({units})- {attrs.get("project")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop})  - {attrs.get("scenario")}  - (warning {GWLs}°C ) - ({attrs.get("season_name")})'
    else:
        title = f'{name_var} ({units})- {attrs.get("project")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop})  - {attrs.get("scenario")}  - ({period.start} - {period.stop}) - ({attrs.get("season_name")})'
    ax.set_title(title)

    #add horizontal lines
    yticks = ax.get_yticks()
    for ytick in yticks:
        ax.hlines(y = ytick, xmin = mean_change['month'].min(), 
                  xmax = mean_change['month'].max(),
                  colors = 'grey', linewidth = 0.5, linestyles = '--')
    
    # Add labels to axes
    ax.set_xlabel('Months')
    
    # Add legend
    ax.set_xticks(np.arange(1, 13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.legend()
    
    # Return the figure
    return fig

def time_series(ds, var, attrs, mode = 'climatology', diff = 'abs', 
                ds_baseline = None, season = 'Annual', 
                period = None, baseline_period = None, GWL = None, GWLs = None,
                results = None, trend_period = slice('1950','2020')):
    '''
    Function to visualize time series of climate data.

    Parameters:
    -----------
    ds : xarray.Dataset
        Input dataset containing climate data.
    var : str
        Name of the variable to analyze.
    attrs : dict
        Dictionary with the attributes for the variable (e.g., long_name, units).
    mode : str, optional
        Mode of the analysis. Default is 'climatology'.
    diff : str, optional
        Type of difference to calculate ('abs' for absolute, 
        'rel' for relative, etc.). Default is 'abs'.
    ds_baseline : xarray.Dataset, optional
        Baseline dataset to compare against. Default is None.
    season : str, optional
        Season to consider for the analysis. Default is 'Annual'.
    period : slice, optional
        Time period to consider for the analysis. Default is None.
    baseline_period : slice, optional
        Baseline period for calculating mean baseline. Default is None.
    GWL : str, optional
        Global warming level. Default is None.
    GWLs : xarray.Dataset, optional
        Dataset containing global warming levels. Default is None.

    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure object containing the time series plot.
    '''      
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(20, 15))

     #get units
    name_var = get_attribute("variable", var)
    units = get_attribute("units", attrs.get("unit"))
    if units == None:
        units = attrs.get("unit")
    if attrs.get("project") in ["ERA5", "ERA5-Land", "E-OBS", "ORAS5"]:# project that don't have menber
        if mode == 'change':
            if diff =='abs':
                mean_change = ds - ds.sel(year=baseline_period).mean('year')
            elif diff == 'rel':
                mean_change = (ds - ds.sel(year=baseline_period).mean('year'))
                abs(ds.sel(year=baseline_period).mean('year')) * 100
        elif mode == 'climatology':
            mean_change = ds
        elif mode == 'trend':
            mean_change = ds
            # Extract slope (m) and intercept (b) from the regression results
            slope = results.slope
            intercept = results.intercept
            # Calculate the fitted line using the slope and intercept
            fitted_line = slope * ds.sel(year = trend_period).year + intercept
            fitted_line.plot(color = 'grey',
                             label= f'Trend {slope.round(5)*10} {units} per decade (p_value {results.pvalue.round(4)})')
    else:
        members = ds['member'].count().values
                        
        # Calculate mean line
        if mode == 'change':
            if diff =='abs':
                mean_change = ds.mean('member') - ds.sel(year=baseline_period).mean()
                time_plot = ds - ds.sel(year=baseline_period).mean('year')
            elif diff == 'rel':
                mean_change = (ds.mean('member') - ds.sel(year=baseline_period).mean())
                abs(ds.sel(year=baseline_period).mean()) * 100
                time_plot = (ds - ds.sel(year=baseline_period).mean('year'))
                abs(ds.sel(year=baseline_period).mean('year')) * 100
        elif mode == 'climatology':
            mean_change = ds.mean('member')
            time_plot = ds 
        
        # Calculate change for each member and plot
        for m in range(members):
            time_plot.sel(member=m).plot(ax=ax, color='red', linewidth=0.5, linestyle = ':')
            
        upper_90th_percentile = np.nanpercentile(time_plot, 90,
                                                 axis = time_plot.dims.index('member'))
        lower_10th_percentile = np.nanpercentile(time_plot, 10,
                                                 axis = time_plot.dims.index('member'))
        upper_75th_percentile = np.nanpercentile(time_plot, 75,
                                                 axis = time_plot.dims.index('member'))
        lower_25th_percentile = np.nanpercentile(time_plot, 25,
                                                 axis = time_plot.dims.index('member'))
        ax.fill_between(mean_change['year'], upper_90th_percentile, lower_10th_percentile, 
                        color='red', alpha=0.25, label='P10 to P90')
        ax.fill_between(mean_change['year'], upper_75th_percentile, lower_25th_percentile, 
                        color='red', alpha=0.3,label='P25 to P75')

    mean_change.plot(ax=ax, color='red', linewidth=2, label='P50 (Median)')
                    
    # Shade period baseline period in gray
    if GWL is not None:
        for member, mean_period in GWL.items():
            ax.axvspan(int(mean_period.split('-')[0]), 
                       int(mean_period.split('-')[1] ), color='gray', alpha=0.1)
        ax.axvspan(attrs.get("actual_year"), attrs.get("actual_year"), color='gray',
                   alpha=0.1, label = "Reference Period")# for the legend
    elif mode == 'trend':
        ax.axvspan(int(trend_period.start), int(trend_period.stop), color='gray', alpha=0.5)
    else:
        ax.axvspan(int(period.start), int(period.stop), 
                   color='gray', alpha=0.5, label='Reference Period')


    if mode == 'change':
        ax.axvspan(int(baseline_period.start), int(baseline_period.stop), 
                   color='gray', alpha=0.3, label='Baseline')

    #add vertical line for actual year
    ax.axvline(x=attrs.get("actual_year"), color='darkgrey', linewidth = 0.5)
                    
    # Add horizontal lines
    yticks = ax.get_yticks()
    for ytick in yticks:
        ax.hlines(y = ytick, xmin = mean_change['year'].min(), 
                  xmax = mean_change['year'].max(),
                  colors = 'lightgrey', linewidth = 0.25,linestyles = '--')
   #set title
    if mode in ['climatology','trend' ]:
        title = f'{name_var} ({units}) - {attrs.get("model")} - {mode}  - {attrs.get("scenario")} '
    elif GWLs:
         title = f'{name_var} ({units})- {attrs.get("model")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop})  - {attrs.get("scenario")}  - (warning {GWLs}°C ) - ({attrs.get("season name")})'
    else:
        title = f'{name_var} ({units})- {attrs.get("model")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop})  - {attrs.get("scenario")}  - ({period.start} - {period.stop}) - ({attrs.get("season name")})'
    ax.set_title(title)
    
    # Add labels to axes
    ax.set_xlabel('Years')

    # Remove the ylabel
    ax.set_ylabel('')
    
    # Add legend
    ax.plot([], color='red', linewidth=0.5,linestyle = ':', label= attrs.get('Project'))
    ax.legend()
    
    # Return the figure
    return fig

def seasonal_stripe_plot(ds, var, attrs,  mode, diff = None, 
                         period=slice(1850, 2014),
                         baseline_period=slice(1850, 1870), 
                         cmap='seismic', cbar_value=0) -> plt.Figure:
    """
    Plot climate stripes for a given dataset, based on the temporal aggregation.

    Parameters
    ----------
    ds : xr.Dataset
        The dataset containing temperature data.
    mode : str
        Mode of aggregation (e.g., 'monthly', 'seasonal', 'annual').
    difference : str
        Type of difference ('abs' for absolute, 'rel' for relative).
    season : list
        List of months (integers) representing the season (e.g., [12, 1, 2] for DJF).
    period : slice, optional
        The time period to consider for the plot. Default is 1850 to 2014.
    baseline_period : slice, optional
        The baseline period for comparison. Default is 1850 to 1870.
    cmap : str, optional
        The colormap for the plot. Default is 'seismic'.
    cbar_value : float, optional
        Value for centering the colorbar. Default is 0.

    Returns
    -------
    plt.Figure
        The matplotlib figure containing the climate stripes plot.
    """
                            
    # Calculate the reference difference
    if mode == 'change':
        ds_baseline = ds.loc[dict(year=baseline_period)].mean('year')
        # Calculate absolute or relative difference
        if diff == 'abs':
            values = ds - ds_baseline
        elif diff == 'rel':
            values = ((ds - ds_baseline) /abs(ds_baseline)) * 100
    elif mode == 'climatology':
         values = ds
    
    values = values.transpose()  # Transpose the values for plotting
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(20, 10))

    if cbar_value == 0:
        max_values = values.max()
        min_values = values.min()
        if diff == 'rel':
            max_values = abs(values).max()
            min_values = - max_values
    else:
        max_value=abs(cbar_value)

    img = ax.pcolormesh(values.year,values.month, values,
                        cmap = cmap, 
                        vmin = min_values, vmax = max_values)

    # Add colorbar
    cbar = fig.colorbar(img, ax=ax, extend='both')
    
    if mode == 'change':
        FIRST_base = baseline_period.start
        LAST_base = baseline_period.stop

    # Add ticks labels
    ax.set_yticks(np.arange(1, 13))
    ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    #set title
    name_var = get_attribute("variable", var)
    units = get_attribute("units", attrs.get("unit"))
    if units == None:
        units = attrs.get("unit")
    if diff == 'rel':
        units = "%"
    if mode == 'climatology':
        title = f'{name_var} ({units}) - {attrs.get("project")} - {mode}  - {attrs.get("scenario")}'
    else:
         title = f'{name_var} ({units})- {attrs.get("project")} - {mode} {diff}. to - ({baseline_period.start} - {baseline_period.stop}) - {attrs.get("scenario")} '
        
    ax.set_title(title)
    
    return plt  # Return the plot object
import pandas as pd
import xarray as xr
import numpy as np
import os

def select_member_GWLs(ds, GWLs, project, scenario, GWL):
    '''
    Selects GWLs data for specific model, scenario, and GWL.

    Parameters:
    -----------
    ds : xarray.Dataset
        The dataset containing the GWLs data.
    GWLs : DataFrame
        DataFrame containing GWLs data.
    project : str
        Model name, either 'CMIP6' or 'CMIP5'.
    scenario : str
        Scenario name.
    GWL : str
        Global Warming Level (GWL) to select.

    Returns:
    --------
    GWLs_members_with_period : DataFrame
        GWLs data for the specified model, scenario, and GWL with period information.
    '''

    members = np.intersect1d(ds.member_id.values, GWLs.index)
    GWLs_members = GWLs[GWL, scenario].loc[members]
    GWLs_with_period = [mem for mem in GWLs_members.index if '-' in GWLs_members.loc[mem]]
    GWLs_members_with_period = GWLs[GWL, scenario].loc[GWLs_with_period]
    
    return GWLs_members_with_period

def load_GWLs(model):
    '''
    Loads the Global Warming Levels (GWLs) data for a given model.

    Parameters:
    -----------
    model: str
        The name of the model.

    Returns:
    --------
    GWLs: DataFrame
        A DataFrame containing the Global Warming Levels data for the specified model.
    '''

    # Get current directory
    c_path = os.getcwd()
    c_path_c3s_atlas = '/'.join(c_path.split('/')[0:-1])

    root_GWLs = 'warming_levels/'
    if model in ["CMIP5", "CMIP6"]:
        GWLs = pd.read_csv(f"{c_path_c3s_atlas}/auxiliar/GWLs/{model}_WarmingLevels.csv", 
                           header=[0, 1], index_col=[0])
    elif model == "CORDEX-CORE":
        GWLs = pd.read_csv(f"{c_path_c3s_atlas}/auxiliar/GWLs/CORDEX-CORE_WarmingLevels_plusIPCC-Atlas.csv", 
                           header=[0, 1], index_col=[0])
    elif model == "CORDEX-EUR-11":
        GWLs = pd.read_csv(f"{c_path_c3s_atlas}/auxiliar/GWLs/CMIP5_WarmingLevels.csv", 
                           header=[0, 1], index_col=[0])
    # Convert all data to strings
    GWLs = GWLs.astype(str)

    return GWLs

def select_over_period(ds, mean_period):
    """
    Function to select the data from a DataArray over a given time period.
    
    Parameters:
    -----------
    ds: xarray.DataArray
        The DataArray to select from.
    mean_period: str
        The time period in format "YYYY-YYYY".
    
    Returns:
    --------
    xarray.DataArray: 
        A new DataArray containing data for the specified period.
    """
    start_date = mean_period.split('-')[0] + '-01-01'
    end_date = mean_period.split('-')[1] + '-12-31'
    return ds.sel(time=slice(start_date, end_date))

def mean_over_period(ds, mean_period):
    """
    Function to do a mean of the data from a DataArray over a given time period.
    
    Parameters:
    -----------
    ds: xarray.DataArray
        The DataArray to select from.
    mean_period:str
        The time period in format "YYYY-YYYY".
    
    Returns:
    --------
    xarray.DataArray: 
        A new DataArray containing the mean of data for the specified period.
    """
    start_date = mean_period.split('-')[0] + '-01-01'
    end_date = mean_period.split('-')[1] + '-12-31'
    return ds.sel(time=slice(start_date, end_date)).mean('time')

def GWLs_groupby_month(ds, mean_period):
    """
    Function to do a mean of the data from a DataArray over a given time period.
    
    Parameters:
    -----------
    ds:xarray.DataArray
        The DataArray to select from.
    mean_period:str
        The time period in format "YYYY-YYYY".
    
    Returns:
    --------
    xarray.DataArray: 
        A new DataArray containing the mean of data for the specified period.
    """
    dates = pd.to_datetime(ds['time'].values)
    months = np.array([date.month for date in dates])
    ds = ds.assign_coords(month=('time', months))
    start_date = mean_period.split('-')[0] + '-01-01'
    end_date = mean_period.split('-')[1] + '-12-31'
    
    return ds.sel(time=slice(start_date, end_date)).groupby('month').mean(dim='time', skipna=True)

def get_selected_data(ds, GWLs_members_with_period):
    """
    Selects data for each member based on the specified time periods.

    Parameters:
    ----------
    ds: xarray.Dataset
        The Dataset containing the data to be selected.
    GWLs_members_with_period: dict
        A dictionary where the keys are the member names and the values are tuples
        representing the time period (start_date, end_date).

    Returns:
    -------
    xarray.DataArray or xarray.Dataset
        A DataArray or Dataset with the selected data concatenated along the 'member' dimension.
    """
    #Selecting data for each member
    selected_data = None
    members_gwl=[]
    for member, mean_period in GWLs_members_with_period.items():
        members_gwl.append(member)
        #if selected_data:
        #    selected_data = xr.concat([selected_data, 
         #                              select_over_period(ds.sel(member=np.where(ds.member_id == member)[0]), mean_period)], 
        #                              dim = 'member')
        #else:
        #    selected_data= select_over_period(ds.sel(member=np.where(ds.member_id == member)[0]), mean_period)

    mem_inters_gwl = np.intersect1d(ds.member_id.values, members_gwl)
    ds_members = ds.isel(member = np.in1d(ds.member_id.values, mem_inters_gwl))
    return ds_members

def get_mean_data(ds,GWLs_members_with_period):
    """
    Gets the mean of data for each member based on the specified time periods.

    Parameters:
    ----------
    ds: xarray.Dataset
        The Dataset containing the data to be selected.
    GWLs_members_with_period: dict
        A dictionary where the keys are the member names and the values are tuples
        representing the time period (start_date, end_date).

    Returns:
    -------
    xarray.DataArray or xarray.Dataset
        A DataArray or Dataset with the selected data concatenated along the 'member' dimension.
    """
    # Applying time averaging for each member
    averaged_data = None
    for member, mean_period in GWLs_members_with_period.items():
        if averaged_data:
            averaged_data = xr.concat([averaged_data, 
                                       mean_over_period(ds.sel(member=np.where(ds.member_id == member)[0]), mean_period)], 
                                      dim = 'member')
        else:
            averaged_data= mean_over_period(ds.sel(member=np.where(ds.member_id == member)[0]), mean_period)

    mem_inters_gwl = np.intersect1d(ds.member_id.values, averaged_data.member_id.values)
    ds_members = ds.isel(member = np.in1d(ds.member_id.values, mem_inters_gwl))
    return averaged_data, ds_members

def get_mean_data_by_months(ds,GWLs_members_with_period):
    """
    Gets the mean of data for each member based on the specified time periods.

    Parameters:
    ----------
    ds: xarray.Dataset
        The Dataset containing the data to be selected.
    GWLs_members_with_period: dict
        A dictionary where the keys are the member names and the values are tuples
        representing the time period (start_date, end_date).

    Returns:
    --------
    xarray.DataArray or xarray.Dataset
        A DataArray or Dataset with the selected data concatenated along the 'member' dimension.
    """
    # Applying time averaging for each member
    averaged_data = None
    for member, mean_period in GWLs_members_with_period.items():
        if averaged_data:
            averaged_data = xr.concat([averaged_data, 
                                       GWLs_groupby_month(ds.sel(member=np.where(ds.member_id == member)[0]), mean_period)], 
                                      dim = 'member')
        else:
            averaged_data= mean_over_period(ds.sel(member=np.where(ds.member_id == member)[0]), mean_period)

    mem_inters_gwl = np.intersect1d(ds.member_id.values, averaged_data.member_id.values)
    ds_members = ds.isel(member = np.in1d(ds.member_id.values, mem_inters_gwl))
    return averaged_data, ds_members
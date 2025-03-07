![logo](./figures/LogoLine_horizon_C3S.png)


# Reproducibility of the C3S Atlas  

The [C3S Atlas Dataset](https://doi.org/10.24381/cds.h35hb680) support blablabla and has been produces using a workflow....blabla

Figure 1 shows the scheme of the workflow designed for data production of the C3S Atlas Dataset.

To calculate an index:
- Download climate data from the C3S-CDS using the CDS API.
- Download the reference datasets (only for bias adjusted indices).
- Perform data homogenization to ensure the same calendar time, coordinate names, variable units, dimension order, among other things.
- Interpolate both the projections and the reference dataset to a regular-common grid using conservative remapping (only for bias adjusted indices).
- Calculate the index.
- Perform temporal aggregation.
- Interpolate to a regular-common grid using conservative remapping (only for no bias adjusted indices)

![Overview schematic diagram of the C3S Atlas workflow designed for data production](./figures/workflow.png)

**Figure 1** shows the scheme of the workflow designed for data production

### Open Python libraries

Table 1 displays the list of Python libraries used for the implementation of the workflow for index calculation.

| Library  | Description | Used in (workflow/user-tools) |
|----------|-------------|-------------------------------|
| [xclim](https://xclim.readthedocs.io/en/stable/) | xclim is a library for climate index calculation built using xarray and can seamlessly benefit from the parallelization handling provided by dask. | workflow and user-tools 
| [ibicus](https://ibicus.readthedocs.io/en/latest/index.html) | Bias adjustment library for climate model data adjustment using observational references. | workflow and user-tools |
| [xESMF](https://xesmf.readthedocs.io/en/stable/) | Regridding library for geospatial data | workflow and user-tools (encapsulated in a wrapper) |
| [xarray](https://docs.xarray.dev/en/stable/) | Python library for managing labelled multi-dimensional arrays | workflow and user-tools |
| [dask](https://examples.dask.org/xarray.html) | Python library for parallel computing | Used for user-tools. The workflow uses an in-house chunking strategy |
| [cdsapi](https://cds.climate.copernicus.eu/api-how-to) | The Climate Data Store (CDS) Application Program Interface (API) is a service providing programmatic access to CDS data. | workflow (encapsulated in a wrapper) and user-tools |

**Table 1**. List of Python libraries used in the C3S Atlas.

### List of indices


Table 2 shows the climate variables and indices included in the C3S Atlas dataset (v2).


| Name Data | Unit Data | Description data | Implementation |
|------------------------|-----------------|---------------------------|---------------|
| Monthly mean of daily mean temperature | degC | Monthly mean of daily mean near-surface (2-metre) air temperature | <span style="color:blue">t.resample(time='MS').mean()</span> |
| Monthly mean of daily minimum temperature | degC | Monthly mean of daily minimum near-surface (2-metre) air temperature | <span style="color:blue">tn.resample(time='MS').mean()</span> |
| Monthly mean of daily maximum temperature | degC | Monthly mean of daily maximum near-surface (2-metre) air temperature | <span style="color:blue">tx.resample(time='MS').mean()</span> |
| Monthly minimum of daily minimum temperature | degC | Monthly minimum of daily minimum near-surface (2-metre) air temperature | <span style="color:blue">tn.resample(time='MS').min()</span> |
| Monthly maximum of daily maximum temperature | degC | Monthly maximum of daily maximum near-surface (2-metre) air temperature | <span style="color:blue">tx.resample(time='MS').max()</span> |
| Monthly count of days with maximum temperature above 35 degC | 1 | Monthly count of days with maximum near-surface (2-metre) air temperature above 35 degC | <span style="color:magenta">xclim.indices.tx_days_above(tx, thresh='35.0 degC', freq='MS', op='>')</span> |
| Monthly count of days with maximum temperature above 40 degC | 1 | Monthly count of days with maximum near-surface (2-metre) air temperature above 40 degC | <span style="color:magenta">xclim.indices.tx_days_above(tx, thresh='40.0 degC', freq='MS', op='>')</span> |
| Monthly count of tropical nights (days with minimum temperature above 20 degC) | 1 | Monthly count of days with minimum near-surface (2-metre) air temperature above 20 degC | <span style="color:magenta">xclim.indicators.atmos.tropical_nights(tasmin=tn, thresh='20.0 degC', freq='MS', op='>')</span> |
| Monthly mean of daily temperature range | degC | Monthly mean of daily near-surface (2-metre) air temperature range | <span style="color:magenta">xclim.indices.daily_temperature_range(tn, tx, freq='MS', op='mean')</span> |
| Monthly count of frost days | 1 | Monthly count of days with minimum near-surface (2-metre) air temperature below 0 degC | <span style="color:magenta">xclim.indicators.atmos.frost_days(tn, thresh='0 degC', freq='MS')</span> |
| Annual heating degree-days | degC day | Annual energy consumption to heat the deficit of temperature below 15.5 degC | <span style="color:green">user-tools.lib.indexes.hd(t, tx, tn, freq='YS', thresh=15.5)</span> |
| Annual cooling degree-days | degC day | Annual energy consumption to cool the excess of temperature above 22 degC | <span style="color:green">user-tools.lib.indexes.cd(t, tx, tn, freq='YS', thresh=22)</span> |
| Monthly mean of daily accumulated precipitation | mm | Monthly mean of daily accumulated precipitation of liquid water equivalent from all phases | <span style="color:blue">r.resample(time='MS').mean()</span> |
| Monthly count of days with daily accumulated precipitation above 1 mm | 1 | Monthly count of days with daily accumulated precipitation of liquid water equivalent from all phases above 1 mm | <span style="color:magenta">xclim.indices.days_over_precip_thresh(r, 0, thresh='1 mm/day', freq='MS', bootstrap=False, op='>')</span> |
| Monthly mean of daily accumulated evaporation (including sublimation and transpiration) | mm | Monthly mean of daily amount of water in the atmosphere due to conversion of both liquid and solid phases to vapor (from underlying surface and vegetation) | <span style="color:blue">evspsbl.resample(time='MS').mean()</span> |
| Monthly mean of sea surface temperature | degC | Monthly mean temperature of sea water near the surface | <span style="color:blue">sst.resample(time='MS').mean()</span> |
| Monthly average of mean sea level pressure | hPa | Monthly average air pressure at mean sea level | <span style="color:blue">psl.resample(time='MS').mean()</span> |



**Table 2**. Description of the climate variables and indices included in the second version of the C3S Atlas. The first three columns indicate the name, units, and description of the indices. The last column includes the Python command used to compute the C3S Atlas indices from daily data, either using xarray (blue), xclim (magenta) or in-house functions (green). Input variables used to compute each index are defined with its code name (e.g. t for daily mean air temperature). 

#### Bias corrected indices

For threshold-dependent indices (...) we propose to include both raw and bias adjusted information, using a simple linear scaling and a more advanced trend preserving method (ISIMIP3), as planed in D381.1.3.1 (Sec. 2.6); note that this was not possible in the first version since ISIMIP method is computationally demanding. 

| Ibiscu Method  | Function                | Parameters  | Description  |
|---------------|------------------------|-------------|-------------|
| LinearScaling | LinearScaling          | "running_window_mode": True, "running_window_length": 30, "running_window_step_length": 30 | Linear scaling method based on Douglas Maraun 2016. Reference period used for BA: 1980-2005 (CMIP5/6 using WFDE5) and 1970-2005 (CORDEX-EUR-11 using E-OBS and CORDEX-CORE using ERA5-Land) |
| ISIMIP        | ISIMIP (temperature)    | "running_window_mode": False | ISIMIP trend preserving method based on Lange 2021. Reference period used for BA: 1980-2005 (CMIP5/6 using WFDE5) and 1970-2005 (CORDEX-EUR-11 using E-OBS and CORDEX-CORE using ERA5-Land) |
| ISIMIP (pr)   | ISIMIP (pr)             | "lower_bound": 0, "lower_threshold": 0.1, "upper_bound": np.inf, "upper_threshold": np.inf, "distribution": scipy.stats.gamma, "trend_preservation_method": "mixed", "running_window_mode": False |  |

**Table 3.** Specific functions and parameters of the Python Ibicus package ([Ibicus Documentation](https://ibicus.readthedocs.io)) used in the C3S Atlas for bias-adjusted variables. The details of the different reference periods and datasets for the bias adjustment process of the different datasets are given in Table 3.


### Notebooks


This chapter include severa notebooks for reproducing the calculation of indices forming the dataset underpinning the C3S Atlas ([C3S Atlas Dataset](https://doi.org/10.24381/cds.h35hb680)). These notebooks facilitate reusability and allow to quickly develop customized products for particular applications. Note that the examples included in the notebooks correspond to particular regions and/or subsets and do not allow to directly reproduce the full dataset. This requires a optimized worflow running on an HPC infrastructure.

Table 4 include several notebooks to reproduce some of the indices of the C3S Atlas and compare the results obtained with the C3S Atlas Dataset.

| Directory | Contents |
| :-------- | :------- |
[tx35.ipynb](https://github.com/ecmwf-projects/c3s-atlas/blob/main/user-tools/tx35.ipynb) | Jupyter Notebook for calculating the “number of days with maximum temperature over 35°C” (TX35) index using xclim library.
|  [tx35bals.ipynb](https://github.com/ecmwf-projects/c3s-atlas/blob/main/user-tools/tx35bals.ipynb) | Jupyter Notebook for calculating “number of days with bias-adjusted maximum temperature over 35°C” (TX35bals) index using xclim and ibicus libraries.
|  [cd.ipynb](https://github.com/ecmwf-projects/c3s-atlas/blob/main/user-tools/cd.ipynb) | Jupyter Notebook for calculating the “Cooling Degree-Days” (CD) index using in-house index funtions.
|  [prbaisimip.ipynb](https://github.com/ecmwf-projects/c3s-atlas/blob/main/user-tools/prbaisimip.ipynb) | Jupyter Notebook for calculating the “bias-adjusted (ISIMIP) precipitation” (CD) index using xclim and ibicus funtions.

**Table 4.** Notebooks included as example to reproduce the C3S Atlas.



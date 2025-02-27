# user-tools

## Contents
The implementation of FAIR principles in the [C3S Atlas](http://atlas.climate.copernicus.eu) provides transparency and enable the reusability of the data and software used for the development of the products provided in the Atlas. The development of the “C3S Atlas User Tools” is a key milestone for this activity, providing access to the code and auxiliary information used to produce the datasets and visual products. The User Tools have been implemented favouring interoperability using a technological stack based on Jupyter Notebooks, a powerful tool for documenting and sharing workflows, experiments, and analysis.
Jupyter notebooks to reproduce the Copernicus Interactive Climate indices and visual products.

This User Tools GitLab repository has been prepared as a first package of user tools enabling reproducibility and reusability for the calculation of the indices forming the C3S Atlas Dataset and the generation of the visual products displayed in the Interactive Atlas. 

## Reproducibility of the C3S Atlas dataset 

Notebooks for reproducing the calculation of indices forming the dataset underpinning the C3S Atlas ([C3S Atlas dataset](https://doi.org/10.24381/cds.h35hb680)). These notebooks facilitate reusability and allow to quickly develop customized products for particular applications. Note that the examples included in the notebooks correspond to particular regions and/or subsets and do not allow to directly reproduce the full dataset. This requires a optimized worflow running on an HPC infrastructure.

| Directory | Contents |
| :-------- | :------- |
[tx35.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/tx35.ipynb) | Jupyter Notebook for calculating the “number of days with maximum temperature over 35°C” (TX35) index using xclim library.
|  [tx35bals.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/tx35bals.ipynb) | Jupyter Notebook for calculating “number of days with bias-adjusted maximum temperature over 35°C” (TX35bals) index using xclim and ibicus libraries.
|  [cd.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/cd.ipynb) | Jupyter Notebook for calculating the “Cooling Degree-Days” (CD) index using in-house index funtions.
|  [prbaisimip.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/prbaisimip.ipyn) | Jupyter Notebook for calculating the “bias-adjusted (ISIMIP) precipitation” (CD) index using xclim and ibicus funtions.

## Reproducibility of the C3S Atlas visual products

Notebooks to reproduce and extend parts of the figures and products provided by the Copernicus Interactive Climate Atlas (C3S Atlas, https://atlas.climate.copernicus.eu/atlas).

| Directory | Contents |
| :-------- | :------- |
|  [global_map.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/global_map.ipynb) | Jupyter Notebook for reproducing global maps of climatologies or changes, including the calculation and display of uncertainty for the latter following the IPCC AR6 methodology (advanced method).
|  [time_series.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/time_series.ipynb) | Jupyter Notebook for reproducing regional time series.
|  [climate_stripe.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/climate_stripe.ipynb) | Jupyter Notebook for reproducing regional climate stripes.
|  [seasonal_stripe.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/seasonal_stripe.ipynb) | Jupyter Notebook for reproducing regional seasonal stripes.
|  [annual_cycle.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/annual_cycle.ipynb) | Jupyter Notebook for reproducing regional annual cycles.
|  [customized_regions.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/customized_regions.ipynb) | Jupyter Auxiliary notebook with examples of how to produce results for customized regions defined in machine-readable formats (e.g. geojson).
|  [GWLs.ipynb](https://github.com/ecmwf-projects/c3s-atlas/-/blob/main/user-tools/GWLs.ipynb) | Auxiliary Jupyter Notebook for calculating the Global Warming Levels (GWLs) following the IPCC AR6 methodology. This is used by previous notebooks for calculating changes for different warming levels.



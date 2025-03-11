![logo](../book/notebooks/figures/LogoLine_horizon_C3S.png)

# c3s_atlas(in-house) python functions

This repository contains **source** functions and wrappers designed to reproduce the workflow for data production of the [C3S Atlas](https://atlas.climate.copernicus.eu/atlas). The functions in this repository facilitate various processing steps such as harmonization, aggregation, interpolation, and more.

Table 1 provides descriptions of the main files in the repository, outlining their functionality.

| **File**             | **Description**                                                                 |
|----------------------|---------------------------------------------------------------------------------|
| `aggregation.py`      | Contains functions to aggregate data across different dimensions or time periods.
| `analysis.py`         | Includes functions for data analysis, such as calculating statistical properties, trends, and performing exploratory data analysis |
| `customized_regions.py`| Provides functions to define and handle custom regions for analysis, possibly including spatial subsetting or creating specific regional masks. |
| `errors.py`           | Contains error-handling functions to manage and log errors throughout the processing pipeline. |
| `fixers.py`           | Provides utility functions to fix or clean up data from different sources |
| `indexes.py`          | Includes in-house function for calculating various climate indices |
| `interpolation.py`    | Contains functions for regridding data to different spatial resolutions based on the [xESMF](https://xesmf.readthedocs.io/en/stable/) Regridding library |
| `logger.py`           | Includes functions for logging messages, warnings, and errors during the execution of the data processing pipeline. |
| `products.py`         | Contains functions to visualice the products available in the [C3S Atlas Application](./_build/html/chapter02.html). |
| `temporal.py`         | Includes functions to handle time-based operations |
| `units.py`            | Contains utility functions for unit conversions and ensuring consistency of units across the dataset. |

Table 1. In-house functions for the [C3S Atlas](https://atlas.climate.copernicus.eu/atlas).








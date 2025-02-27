# Repository supporting the implementation of FAIR principles in the [C3S Atlas](https://atlas.climate.copernicus.eu/atlas)

## Contents

This repository provides the scripts and notebooks, as well as the required auxiliary products and datasets, supporting the reproducibility and reusability of some of the C3S Atlas products, as described in the following schema and table of contents.

<img src="user-tools/workflow.png" alt="Overview schematic diagram of the C3S Atlas workflow designed for data production" width="800"/>

**Figure 1**. Overview schematic diagram of the C3S Atlas workflow designed for data production.



| Directory | Contents |
| :-------- | :------- |
|  [auxiliar](https://github.com/ecmwf-projects/c3s-atlas/tree/main/auxiliar) | Auxiliary materials containing GeoJSONs, GWLs, masks, etc.
|  [c3s_atlas](https://github.com/ecmwf-projects/c3s-atlas/tree/main/c3s_atlas) | Python functions and wrappers to reproduce the workflow for data production of the C3S Atlas.
|  [user-tools](https://github.com/ecmwf-projects/c3s-atlas/tree/main/user-tools) | Jupyter notebooks, combining the information from several of the previous directories to perform specific analyses.

**Table 1**. Table of contents.


## Requirements

Scripts and (jupyter) notebooks are provided in [Python](https://www.python.org/) to ensure reproducibility and reusability of the results. The simplest way to meet all these requirements is by using a dedicated [conda](https://docs.conda.io) environment, which can be easily installed by issuing:

```sh
git clone git@github.com:ecmwf-projects/c3s-atlas.git
conda create -n c3s-atlas
conda activate c3s-atlas
cd c3s-atlas
conda env update --file environment.yml --prune
pip install -e .
```

Table 2 displays the list of Python libraries used for the implementation of the workflow and the user-tools repository.

| Library  | Description | Used in (workflow/user-tools) |
|----------|-------------|-------------------------------|
| [xclim](https://xclim.readthedocs.io/en/stable/) | xclim is a library for climate index calculation built using xarray and can seamlessly benefit from the parallelization handling provided by dask. | workflow and user-tools 
| [ibicus](https://ibicus.readthedocs.io/en/latest/index.html) | Bias adjustment library for climate model data adjustment using observational references. | workflow and user-tools |
| [xESMF](https://xesmf.readthedocs.io/en/stable/) | Regridding library for geospatial data | workflow and user-tools (encapsulated in a wrapper) |
| [xarray](https://docs.xarray.dev/en/stable/) | Python library for managing labelled multi-dimensional arrays | workflow and user-tools |
| [dask](https://examples.dask.org/xarray.html) | Python library for parallel computing | Used for user-tools. The workflow uses an in-house chunking strategy |
| [cdsapi](https://cds.climate.copernicus.eu/api-how-to) | The Climate Data Store (CDS) Application Program Interface (API) is a service providing programmatic access to CDS data. | workflow (encapsulated in a wrapper) and user-tools |

**Table 2**. List of Python libraries used in the C3S Atlas software, as main packages for the different components shown in Figure 1.


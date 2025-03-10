![logo](./book/figures/LogoLine_horizon_C3S.png)

# Repository supporting the implementation of FAIR principles in the [C3S Atlas](https://atlas.climate.copernicus.eu/atlas)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ecmwf-projects/c3s-atlas/tree/main/HEAD?urlpath=%2Fdoc%2Ftree%2Fhttps%3A%2F%2Fgithub.com%2Fecmwf-projects%2Fc3s-atlas%2Fblob%2Fmain%2Fbook%2Ftx35.ipynb)

The c3s-atlas GitHub repository of the [C3S Atlas](https://atlas.climate.copernicus.eu/atlas) have been developed to enhance transparency and facilitate the reusability of the software developed to produce the [C3S Atlas Dataset](https://doi.org/10.24381/cds.h35hb680) and the visual products displayed in the [C3S Atlas Application](https://atlas.climate.copernicus.eu), implementing FAIR principles (Findability, Accessibility, Interoperability, and Reusability; [Iturbide et al. 2022](https://doi.org/10.5194/essd-12-2959-2020)).

## The C3S Atlas

The [C3S Atlas](http://atlas.climate.copernicus.eu) is an application of the  Copernicus Climate Change Service (C3S) which enables an interactive exploration of the Earth's climate, from recent changes and trends to possible climate futures under different emission scenarios. It uses key datasets that are available in the C3S Climate Data Store (CDS), including observation-based datasets (E-OBS), reanalyses (ECMWF’s ERA5, ERA5-Land and ORAS5), and comprehensive global (CMIP5/6) and regional (CORDEX) climate projections. The C3S Atlas is a new resource for policy makers wishing to formulate effective climate policy and for other users who need to visualise and analyse climate change information, particularly at the regional scale. This C3S tool is an evolution of the Intergovernmental Panel on Climate Change (IPCC) Interactive Atlas (IPCC-IA), which was frozen in 2021 with the publication of the Sixth Assessment Report’s (AR6) WGI (Working Group I) section (see https://www.ipcc.ch/report/ar6/wg1).

A brief description of the C3S Atlas is available in the ECMWF Newsletter 181 ([Gutiérrez et al. 2024](https://doi.org/10.21957/ah52ufc369), [online document](https://www.ecmwf.int/en/newsletter/181/earth-system-science/copernicus-interactive-climate-atlas-tool-explore-regional)).


## The C3S Atlas GitHub repository

Table 1 shows the structure of the [c3s-atlas GitHub repository](https://github.com/ecmwf-projects/c3s-atlas).

| Directory | Contents |
| :-------- | :------- |
|  [auxiliar](https://github.com/ecmwf-projects/c3s-atlas/tree/main/auxiliar) | Auxiliary information and datasets, including GeoJSONs for pre-defined regions, spatial masks, etc.
|  [c3s_atlas](https://github.com/ecmwf-projects/c3s-atlas/tree/main/c3s_atlas) | Python functions and wrappers to reproduce the workflow for data production of the C3S Atlas.
|  [book](https://github.com/ecmwf-projects/c3s-atlas/tree/main/book) | Jupyter notebooks building on the sofware and auxiliary information to illustrate the calculation of indices of the dataset and visual products of the application.

**Table 1**. Table of contents of the  [“c3s-atlas" GitHub repository](https://github.com/ecmwf-projects/c3s-atlas).

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

A much straigtforward way to explore and interact with this repository is through binder. Binder provides an executable environment, making the code immediately reproducible. The required software is pre-installed in a cloud environment where the user can create and execute notebooks (directly) and scripts (via the available Terminal). Moreover, the environment is accessible without any further authentication by the user.

To start exploring the binder interface, just click the Launch in MyBinder badge above. You will arrive at a JupyterLab interface with access to the contents of this repository.

## License

```
Copyright 2023, European Union.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```


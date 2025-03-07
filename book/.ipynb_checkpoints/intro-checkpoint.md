![logo](LogoLine_horizon_C3S.png)


# Repository Supporting the Implementation of FAIR Principles in the [C3S Atlas](https://atlas.climate.copernicus.eu/atlas)

## Introduction

This Jupyter Book supports the implementation of FAIR principles (Findability, Accessibility, Interoperability, and Reusability; {cite:p}`Iturbide2022`) in The Copernicus Interactive Climate Atlas (https://atlas.climate.copernicus.eu, [C3S Atlas](https://atlas.climate.copernicus.eu/atlas) in short), providing transparency and enabling the reusability of the data and software used for the development of the C3S Atlas products. The development of the “c3s-atlas" GitHub repository (https://github.com/ecmwf-projects/c3s-atlas) and this associated Jupyter Book represents a key milestone in this effort, providing access to the code and auxiliary information used to produce the datasets and visual products.

This book is divided into two main chapters, where sets of notebooks are produced: 
 - [C3S Atlas dataset](./_build/html/index_rep.html): This chapter includes the documentation and software necessary to reproduce and extend the [Gridded dataset underpinning the Copernicus Interactive Climate Atlas](https://cds.climate.copernicus.eu/datasets/multi-origin-c3s-atlas?tab=overview), with some Jupyter Notebooks as examples for several of the indices included in the C3S Atlas.
 - [C3S Atlas products](./_build/html/product_rep.html): This chapter provides a short explanation of the products visualized in the C3S Atlas and contains several Jupyter Notebooks to reproduce the majority of them, such as global maps, time series, stripe plots among others.

Therefore, this Jupyter Book and the “c3s-atlas" GitHub repository serve as the initial package of user tools enabling reproducibility and reusability in the calculation of the indices forming the C3S Atlas Dataset and the generation of the visual products displayed in the Interactive Atlas.

## The C3S Atlas

The C3S Atlas evolves from the frozen IPCC Atlas (Gutiérrez et al., 2021; https://interactive-atlas.ipcc.ch/) to potentially address the needs of the IPCC’s seventh assessment cycle. Blablabla 

https://www.ecmwf.int/en/newsletter/181/earth-system-science/copernicus-interactive-climate-atlas-tool-explore-regional

### GitHub repository

The "c3s-atlas" GitHub repository (https://github.com/ecmwf-projects/c3s-atlas) has been designed to enhance interoperability by leveraging technological stack based on Jupyter Notebooks, a powerful tool for documenting and sharing workflows, experiments, and analysis.


Table 1 shows the structure of the “c3s-atlas" GitHub repository.

| Directory | Contents |
| :-------- | :------- |
|  [auxiliar](https://github.com/ecmwf-projects/c3s-atlas/tree/main/auxiliar) | Auxiliary materials including GeoJSONs, GWLs, masks, etc.
|  [c3s_atlas](https://github.com/ecmwf-projects/c3s-atlas/tree/main/c3s_atlas) | Python functions and wrappers to reproduce the workflow for data production of the C3S Atlas.
|  [book](https://github.com/ecmwf-projects/c3s-atlas/tree/main/book) | Jupyter notebooks, combining the information from several of the previous directories to perform specific analyses.

**Table 1**. Table of contents of the  [“c3s-atlas" GitHub repository](https://github.com/ecmwf-projects/c3s-atlas).

## Requirements

Scripts and (jupyter) notebooks are provided in [Python](https://www.python.org/) to ensure reproducibility and reusability of the results. The simplest way to meet these requirements is by using a dedicated [conda](https://docs.conda.io) environment, which can be installed which the following commnads:

```sh
git clone git@github.com:ecmwf-projects/c3s-atlas.git
conda create -n c3s-atlas
conda activate c3s-atlas
cd c3s-atlas
conda env update --file environment.yml --prune
pip install -e .
```

## Bibliography

```{bibliography}
:style: unsrt
```



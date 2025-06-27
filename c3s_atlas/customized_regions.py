import numpy as np
import os
import xarray as xr
import regionmask
from shapely.geometry import Polygon
import geopandas as gpd
from .utils import c_path_c3s_atlas

class Mask:
    def __init__(self, ds: xr.Dataset):
        """
        Initialize the Mask object.

        Parameters:
            ds (xr.Dataset): Dataset containing the data.
        """
        self.ds=ds
    
    def polygon(self,region: np.array = np.array([])) -> np.ndarray:
        """
        Generates a mask for the user-defined region.

        Args:
            region (np.array, optional): User-defined region. Defaults to np.array([]).

        Returns:
            np.ndarray: Mask for the user-defined region.
        """
        # Define a polygon object (region_poly) based on the provided region definition
        region_poly = Polygon(region)
        
        # Extract longitude (lon) and latitude (lat) coordinates from the dataset (self.ds)
        lon = self.ds['lon'].values
        lat = self.ds['lat'].values
        
        # Create a list containing the user-defined polygon (user_regions_poly)
        user_regions_poly = [region_poly]
        
        # Create a mask for the user-defined region using regionmask.Regions
        mask_user = regionmask.Regions(user_regions_poly).mask(lon, lat)
        
        # Return the mask for the user-defined region (mask_user)
        mask_user = ~np.isnan(mask_user)
        return mask_user


    def regions_AR6(self, AR6_regions = ['']) -> np.ndarray:
        """
        Generates a mask for the AR6 region.

        Args:
            AR6_regions (arr, optional): AR6 regions. Defaults to [''].

        Returns:
            np.ndarray: Mask for the AR6 region.
        """
        # Extract longitude (lon) and latitude (lat) coordinates from the dataset (self.ds)
        lon = self.ds['lon'].values
        lat = self.ds['lat'].values
        
        # Define the target region (assuming AR6)
        regions_ar6_land = regionmask.defined_regions.ar6.all

        # Access the 'abbrevs' attribute correctly
        region_abbrevs = regions_ar6_land.abbrevs
        
        # Filter regions based on mask_data
        filtered_regions = regions_ar6_land[[region_abbrevs.index(abbrev) for abbrev in
                                             AR6_regions]]

        # Return the mask for AR6 regions (mask_AR6)
        mask_AR6 = filtered_regions.mask(lon, lat)

        # Convert the mask to a boolean array where True indicates the region and False
        # indicates NaN
        mask_AR6 = ~np.isnan(mask_AR6)

        return mask_AR6

        
    def regions_geojson(self,file_path:str = '', acronym = 'Acronym', 
                        geojson_regions = [''])->np.array:
        """
        This function generates a mask for a specified region based on a 
        GeoJSON file and abbreviation.
        
        Args:
          file_path (str, optional): Path to the GeoJSON file containing region data. Defaults to ''.
          acronym (str, optional): The name of the column containing region abbreviations in the GeoJSON file. Defaults to 'Acronym'.
          geojson_regions (list, optional): A list of region abbreviations to include in the mask. Defaults to [''].
        
        Returns:
          np.array: A boolean NumPy array representing the mask for the specified region.
        """
        # Read the GeoJSON file
        geojson_data = gpd.read_file(file_path)        
        # Filter the GeoDataFrame to get only rows with the abbreviations
        mask_data = geojson_data[geojson_data[acronym].isin(geojson_regions)]
        
        lon = self.ds['lon'].values
        lat = self.ds['lat'].values
        
        # Create the mask using latitude and longitude coordinates
        mask_geojson = regionmask.mask_geopandas(mask_data, lon, lat)
        mask_geojson = ~np.isnan(mask_geojson)
        return mask_geojson
        
    def European_contries(self,regions = [''])->np.array:
        """
          This function creates a mask for European countries based on provided abbreviations.
        
          Args:
              regions : A list of country abbreviations to include in the mask. Defaults to [''].
        
          Returns:
              np.array: A boolean NumPy array representing the mask for European countries.
          """
        # Read the GeoJSON file
        geojson_data = gpd.read_file(f"{c_path_c3s_atlas}/auxiliar/geojsons/european-countries_areas.geojson")
        
        # Filter the GeoDataFrame to get only rows with the abbreviations
        mask_data = geojson_data[geojson_data['Acronym'].isin(regions)]        
        # Get latitude and longitude coordinates from the data
        
        lon = self.ds['lon'].values
        lat = self.ds['lat'].values
        
        # Create the mask using latitude and longitude coordinates
        mask_geojson = regionmask.mask_geopandas(mask_data, lon, lat)
        mask_geojson = ~np.isnan(mask_geojson)
        return mask_geojson
        
    def EUCRA_contries(self,regions = [''])->np.array:
        """
        This function creates a mask for EUCRA countries based on provided abbreviations.
        
        Args:
          regions (list, optional): A list of country abbreviations to include in the mask. 
          Defaults to [''] (empty list).
        
        Returns:
          np.array: A boolean NumPy array representing the mask for EUCRA countries.
        """
        # Read the GeoJSON file
        geojson_data = gpd.read_file(f"{c_path_c3s_atlas}/auxiliar/geojsons/EUCRA_areas.geojson")
        
        # Filter the GeoDataFrame to get only rows with the abbreviations
        mask_data = geojson_data[geojson_data['Acronym'].isin(regions)]        
        # Get latitude and longitude coordinates from the data
        
        lon = self.ds['lon'].values
        lat = self.ds['lat'].values
        
        # Create the mask using latitude and longitude coordinates
        mask_geojson = regionmask.mask_geopandas(mask_data, lon, lat)
        mask_geojson = ~np.isnan(mask_geojson)
        
        return mask_geojson

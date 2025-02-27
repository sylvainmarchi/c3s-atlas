import xarray as xr
import re
from c3s_atlas.software.logger import get_logger
from c3s_atlas.software.temporal import infer_freq

logger = get_logger("UNITS_TRANSFORM")

UNIT_CONVERTER = {
    "Kelvin": (1, -273.15, "Celsius"),
    "K": (1, -273.15, "Celsius"),
    "Fahrenheit": (5 / 9, -32 * 5 / 9, "Celsius"),
    "Celsius": (1, 0, "Celsius"),
    "degC": (1, 0, "Celsius"),
    "m hour**-1": (1000 * 24, 0, "mm"),
    "mm day**-1": (1, 0, "mm"),
    "mm": (1, 0, "mm"),
    "m": (1000, 0, "mm"),
    "mm s**-1": (3600 * 24, 0, "mm"),
    "m**3 m**-3": (100, 0, "kg m-2"),
    "kg m**-2 day**-1": (1, 0, "mm"),
    "kg m-2 s-1": (3600 * 24, 0, "mm"),
    "kg m**-2": (1, 0, "mm"),
    "kg m-2": (1, 0, "mm"),
    "C": (1, 0, "Celsius"),
    "(0 - 1)": (100, 0, "%"),
    "Fraction": (100, 0, "%"),
    "m of water equivalent": (1000, 0, "mm"),
    "m s**-1": (1, 0, "m s-1"),
    "m s-1": (1, 0, "m s-1"),
    "m/s": (1, 0, "m s-1"),
    "km h**-1": (10 / 36, 0, "m s-1"),
    "W/m2": (1, 0, "W m-2"),
    "hPa": (100, 0, "Pa"),
    "knots": (0.51, 0, "m s-1"),
    "kts": (0.51, 0, "m s-1"),
    "mph (nautical miles per hour)": (0.51, 0, "m s-1"),
    "%": (1, 0, "%"),
    "W m**-2": (1, 0, "W m-2"),
    "J m**-2": (1 / 3600, 0, "W m-2"),
    "dimensionless": (1, 0, "kW/kW_installed")
}

UNIT_CONVERTER_MONTHLY = {
    "J m**-2": (1 / (3600 * 24), 0, "W m-2"),
    "m": (-1000, 0, "mm"),
    "m of water equivalent": (-1000, 0, "mm"),
}
VALID_UNITS = {
    "tas": "Celsius",
    "mx2t": "Celsius",
    "tasmax": "Celsius",
    "tasmin": "Celsius",
    "tasrange": "Celsius",
    "dwp": "Celsius",
    "src": "mm",
    "hurs": "%",
    "clt": "%",
    "evspsbl": "mm",
    "pr": "mm",
    "psl": "Pa",
    "ps": "Pa",
    "stl4": "K",
    "daily_fire_weather_index": "1",
    "fwi-daily-proj": "1",
    "fwi30": "Day",
    "fwi45": "Day",
    "fwi15": "Day",
    "bio01": "Celsius",
    "bio12": "mm",
    "bio03": "1",
    "bio05": "Celsius",
    "bio02": "Celsius",
    "bio11": "Celsius",
    "bio09": "Celsius",
    "bio10": "Celsius",
    "bio08": "Celsius",
    "bio06": "Celsius",
    "bio19": "mm",
    "bio14": "mm",
    "bio17": "mm",
    "bio18": "mm",
    "bio13": "mm",
    "bio16": "mm",
    "bio15": "1",
    "dsr": "Numeric",
    "bio07": "Celsius",
    "bio04": "Celsius",
    "fwi": r"1|Numeric",
    "fwi-jjas": "1",
    "prsn": "mm",
    "siconc": "%",
    "spv": "kW/kW_installed",
    "wof": "kW/kW_installed",
    "won": "kW/kW_installed",
    "ws100": "m s-1",
    "sfcwind": "m s-1",
    "uwind": "m s**-1",
    "vwind": "m s**-1",
    "mrsos": "kg m-2",
    "mrsos2": "kg m-2",
    "mrsos3": "kg m-2",
    "mrsos4": "kg m-2",
    "mrro": "kg m-2",
    "huss": "1",
    "sst": "Celsius",
    "rlds": "W m-2",
    "rsds": "W m-2",
    "mslp": "Pa",
    "z": "m**2 s**-2",
    "tci": "1",
    "hci": "1",
    "tci-fair": "1",
    "hci-fair": "1",
    "tci-good": "1",
    "hci-good": "1",
    "tci-unfav": "1",
    "hci-unfav": "1"
}


def convert_units(ds: xr.Dataset, project: str) -> xr.Dataset:
    """
    Transform the data units.

    Performs data transformation by reading the 'units' attribute inside the metadata.
    For instance: if data is in Kelvin, the function transform it in ºC

    Parameters
    ----------
    ds: xarray.Dataset
       data stored by dimensions
    project : str
       The name of the project.

    Returns
    -------
    ds (xarray.Dataset): data with the new units
    """
    for ds_var in list(ds.data_vars):
        if re.match(f"^{VALID_UNITS[ds_var]}$", ds[ds_var].attrs["units"]):
            logger.info(
                f"The dataset {ds_var} units are already in the correct magnitude"
            )
        else:
            logger.info(
                f"The dataset {ds_var} units are not in the correct magnitude. "
                f'A conversion from {ds[ds_var].attrs["units"]} to '
                f"{VALID_UNITS[ds_var]} will be performed."
            )
            time_frequency = infer_freq(ds)
            if (time_frequency == "MS" and ds_var in ["rlds", "rsds"]) or (
                "era5" in project and ds_var in ["evspsbl"] and time_frequency == "MS"
            ):
                conversion = UNIT_CONVERTER_MONTHLY[ds[ds_var].attrs["units"]]
            else:
                conversion = UNIT_CONVERTER[ds[ds_var].attrs["units"]]
            ds[ds_var] = ds[ds_var] * conversion[0] + conversion[1]
            ds[ds_var].attrs["units"] = conversion[2]
    return ds

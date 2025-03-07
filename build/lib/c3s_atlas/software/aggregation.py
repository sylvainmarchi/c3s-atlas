from enum import Enum


class AggregationFunction(Enum):
    Min = "minimum"
    Max = "maximum"
    Mean = "mean"
    Sum = "sum"
    Percentile99 = "per99"
    Percentile95 = "per95"


def aggregate_in_time(ds: any, agg_funct: AggregationFunction, agg_res: str = "1D"):
    """
    Group data by day and by using and aggregation function.

    Parameters
    ----------
    ds (xr.Dataset): dataset to group its value by its time variable.
    agg_funct (AggregationFunction): aggregation function to use.

    Returns
    -------
    grouped_ds (xr.Dataset): dataset with variables aggregated spatially.
    """
    resampled = ds.resample(time=agg_res)
    if agg_funct == AggregationFunction.Mean:
        result = resampled.mean("time")
    elif agg_funct == AggregationFunction.Min:
        result = resampled.min("time")
    elif agg_funct == AggregationFunction.Max:
        result = resampled.max("time")
    elif agg_funct == AggregationFunction.Sum:
        result = resampled.sum("time")
    elif agg_funct == AggregationFunction.Percentile99:
        result = resampled.quantile(q=0.99, dim="time")
    elif agg_funct == AggregationFunction.Percentile95:
        result = resampled.quantile(q=0.95, dim="time")
    else:
        raise ValueError(
            "Aggregation function not implented. Please, specify "
            "one of the following: 'maximum', 'minimum', 'mean', 'sum', "
            "'per99', 'per95'."
        )
    return result

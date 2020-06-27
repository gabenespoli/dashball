"""Download statcast data in batches."""

import os
from datetime import datetime, timedelta
from functools import lru_cache

from pybaseball import statcast
from pyspark.sql import SparkSession


@lru_cache(maxsize=None)
def get_spark():
    """Get SparkSession variable, whether on Databricks or not."""
    return (
        SparkSession.builder.master("local").appName("dashball").getOrCreate()
    )


def daterange(start_dt, end_dt):
    """Get an interator for a range of dates."""
    for n in range(int((end_dt - start_dt).days + 1)):
        yield start_dt + timedelta(n)


def get_statcast(
    filename: str,
    start: str,
    end: str = None,
    fmt: str = "%Y-%m-%d",
    mode="append",
):
    """Download data to an existing parquet file."""
    filename = os.path.expanduser(filename)
    if end is None:
        end = start
    start_dt = datetime.strptime(start, fmt).date()
    end_dt = datetime.strptime(end, fmt).date()

    for dt in daterange(start_dt, end_dt):
        datestr = dt.strftime("%Y-%m-%d")
        print("Downloading data from " + datestr + "... ", end="")

        pdf = statcast(start_dt=datestr, end_dt=datestr)

        if pdf.empty:
            print("No data.")
            continue

        # fix type of string columns with NaNs
        fields = [
            x
            for x in pdf.columns
            if pdf[x].dtype == "object" and pdf[x].isna().sum() > 0
        ]

        for field in fields:
            pdf[field] = pdf[field].astype(str)

        # convert to spark and save as parquet
        print("Saving as parquet ({})... ".format(mode), end="")
        sdf = get_spark().createDataFrame(pdf)

        sdf.write.parquet(filename, mode=mode, partitionBy="pitcher")

        # overwrite on first pass, append after that
        if mode == "overwrite":
            mode = "append"

        print("Done.")


if __name__ == "__main__":
    print("Getting statcast data...")

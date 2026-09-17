import censusdis.data as ced
from censusdis.datasets import ACS5
import pandas as pd
import geopandas as gpd


def labels4acs(var: str, yr: int) -> str:
    gn = var.split("_")[0]
    vars = ced.variables.search(ACS5, yr, group_name=gn, name=var)
    label = vars.iloc[0]["LABEL"]
    label = label.split("!")
    for i in ["", "Estimate", "Total:", "Total"]:
        while i in label:
            label.remove(i)
    labstr = "_".join(label).replace(" ", "_")
    if len(labstr) == 0:
        labstr = var.split("_")[0] + "_Total_Universe"

    return labstr


def cid2desc(tab: pd.DataFrame | gpd.GeoDataFrame) -> dict[str, str]:
    renamers = {}
    for col in tab.columns:
        if "_" in col:
            renamers[col] = labels4acs(col, 2024)
    return renamers

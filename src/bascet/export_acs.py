import pandas as pd
import geopandas as gpd
from pathlib import Path


def acs2parquet(tab: pd.DataFrame | gpd.GeoDataFrame, out_path: str):
    """
    Export a pandas dataframe or geopandas geodataframe to parquet.

    Parameters
    ----------
    tab : pd.DataFrame | gpd.GeoDataFrame
    out_path : str
        Location & file name where to export.

    Returns
    -------
    None
    """
    op = Path(out_path)
    if op.suffix == "":
        out_path += ".parquet"
        op = Path(out_path)
    if op.suffix == ".parquet":
        tab.to_parquet(op)
    else:
        raise ValueError("File Path must end in '.parquet'.")


def acs2spat(tab: gpd.GeoDataFrame, out_path: str, vint: int = 2024):
    """
    Export a geopandas geodataframe to geopackage or shapefile.

    Parameters
    ----------
    tab : gpd.GeoDataFrame
    out_path : str
        Location & file name where to export.
    vint : int = 2024
        Year of data - for converting columns to 10 char for shapefiles.

    Returns
    -------
    None
    """
    if type(tab) is not gpd.GeoDataFrame:
        raise TypeError("Table must be a GeoDataFrame.")

    op = Path(out_path)
    if op.suffix == "":
        out_path += ".gpkg"
        op = Path(out_path)

    if op.suffix == ".gpkg":
        tab.to_file(op)
    elif op.suffix == ".shp":
        # deal with 10 letters
        tab = tab.rename(columns=ten_char_names(vint))
        tab.to_file(op)
    else:
        raise ValueError("File Path must end in '.shp' or '.gpkg'.")


def acs2csv(tab: pd.DataFrame | gpd.GeoDataFrame, out_path: str):
    """
    Export a pandas dataframe or geopandas geodataframe to csv. If
    the table is a geodataframe, will drop geometry before exporting.

    Parameters
    ----------
    tab : pd.DataFrame | gpd.GeoDataFrame
    out_path : str
        Location & file name where to export.

    Returns
    -------
    None
    """
    if "geometry" in tab.columns:
        tab = tab.drop(columns=["geometry"])
    op = Path(out_path)
    if op.suffix == "":
        out_path += ".csv"
        op = Path(out_path)
    if op.suffix == ".csv":
        tab.to_csv(op)
    else:
        raise ValueError("File Path must end in '.csv'.")


def ten_char_names(vintage: int = 2024) -> dict[str, str]:
    """
    Record relationship between predefined column names
    and their 10 character name counterparts that are used for shapefiles.

    Parameters
    ----------
    vintage: int = 2024
        Year of data - for translating median income string.

    Returns
    -------
    ten_char_rename : dict[str, str]

    """
    ten_char_rename = {
        "total_housing_units_universe": "hu_tot",
        "occupied_housing_units_percent": "occ_hu_per",
        "vacant_housing_units_percent": "vac_hu_per",
        "total_population_universe": "pop_tot",
        "total_households_universe": "hh_tot",
        f"median_household_income_{vintage}$": "med_inc",
        "tenure_owner_occupied_percent": "oo_hh_perc",
        "tenure_renter_occupied_percent": "ro_hh_perc",
        "tenure_total_hh": "hh_tot_ten",
        "employment_civilian_labor_force_percent": "civ_lf_per",
        "employment_civilian_labor_force_employed_percent": "civ_lf_emp",
        "employment_civilian_labor_force_unemployed_percent": "civ_lf_un",
        "employment_not_in_labor_force_percent": "not_in_lf",
        "year_struct_built_2020_later_percent": "b_2020p",
        "year_struct_built_2010_2019_percent": "b_2010_19",
        "year_struct_built_2000_2009_percent": "b_2000_09",
        "year_struct_built_1990_1999_percent": "b_1990_99",
        "year_struct_built_1980_1989_percent": "b_1980_89",
        "year_struct_built_1970_1979_percent": "b_1970_79",
        "year_struct_built_1960_1969_percent": "b_1960_69",
        "year_struct_built_1950_1959_percent": "b_1950_59",
        "year_struct_built_1940_1949_percent": "b_1940_49",
        "year_struct_built_pre_1940_percent": "b_pre_1940",
        "year_struct_built_total_struct": "struc_tot",
        "units_in_struct_occupied_housing_units": "hu_total",
        "units_in_struct_occupied_housing_units_1_detached_percent": "hu_1d_per",
        "units_in_struct_occupied_housing_units_1_attached_percent": "hu_1a_per",
        "units_in_struct_occupied_housing_units_2_percent": "hu_2_perc",
        "units_in_struct_occupied_housing_units_3_4_percent": "hu_3_4_per",
        "units_in_struct_occupied_housing_units_5_9_percent": "hu_5_9_per",
        "units_in_struct_occupied_housing_units_10_19_percent": "hu_10_19_p",
        "units_in_struct_occupied_housing_units_20_49_percent": "hu_20_49_p",
        "units_in_struct_occupied_housing_units_50_more_percent": "hu_50p_per",
        "units_in_struct_occupied_housing_units_mobile_home_percent": "hu_mh_perc",
        "units_in_struct_occupied_housing_units_boat_rv_van_etc_percent": "hu_etc_per",
        "sex_female_percent": "sex_f_perc",
        "age_under_5_percent": "u5_perc",
        "age_under_18_percent": "u18_perc",
        "age_over_64_percent": "p64_perc",
        "federal_poverty_limit_below_percent": "pl_100u",
        "federal_poverty_limit_between_100_149_percent": "pl_100_149",
        "federal_poverty_limit_above_150_percent": "pl_150p",
        "race_not_hispanic_white_alone_percent": "nh_wh_perc",
        "race_not_hispanic_black_alone_percent": "nh_bl_perc",
        "race_not_hispanic_aian_alone_percent": "nh_aian_pe",
        "race_not_hispanic_asian_alone_percent": "nh_as_perc",
        "race_not_hispanic_nhpi_alone_percent": "nh_nhpi_pe",
        "race_not_hispanic_otherrace_alone_percent": "nh_or_perc",
        "race_not_hispanic_percent": "nhisp_perc",
        "race_hispanic_percent": "hisp_perc",
        "race_personofcolor_percent": "poc_perc",
    }
    return ten_char_rename

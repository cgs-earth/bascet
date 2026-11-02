import censusdis.data as ced
from censusdis.datasets import ACS5
from censusdis.states import ALL_STATES_AND_DC
import pandas as pd
import geopandas as gpd
import os
from dotenv import find_dotenv, load_dotenv, set_key
from pathlib import Path
import numpy as np


def save_api_key(key_str: str) -> Path:
    """
    Create a saved environment variable for a Census API Key by creating or updating
    a .env file in the current working directory. The key is also set for the
    current session, so it can be used right away.

    To do manually- see .env.example: replace the string and resave as .env

    If you don't have an API Key, request one here:
        https://api.census.gov/data/key_signup.html

    Parameters
    ----------
    key_str : str
        Census API Key

    Returns
    -------
    env_loc : Path
        File path location of .env file.

    """
    env_loc = Path("./.env")
    set_key(env_loc, key_to_set="CENSUS_API_KEY", value_to_set=key_str)
    os.environ["CENSUS_API_KEY"] = key_str
    return env_loc


def get_api_key() -> str | None:
    """
    Return the Census API Key from the CENSUS_API_KEY environment variable,
    or from a .env file in the current working directory (or one of its parents).

    Parameters
    ----------
    None

    Returns
    -------
        : str | None - API Key
    """
    load_dotenv(find_dotenv(usecwd=True))
    return os.getenv("CENSUS_API_KEY")


def dwnld_acs5(
    cols: list[str],
    geo: str = "tract",
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Download data from the American Community Survey 5-Year Estimates
        with pre-set restrictions.

    Note - this function will also work for other surveys
        (namely the Decennial Census files)
        but the default variables are for the 2024 ACS 5YR EST tables.

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    cols: list[str]
        List of ACS columns to grab.
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
    """

    if api_key is None:
        api_key = get_api_key()
    if api_key is None:  # still
        raise KeyError(
            "Please run the save_api_key() function with your Census API Key \
                to create an environmental variable."
        )

    if geo == "tract":  # default
        tab = ced.download(
            dataset,
            vintage,
            cols,
            state=state,
            county=county,
            tract="*",
            with_geometry=True,
            api_key=api_key,
        )
        tab["GEOID"] = tab["STATE"] + tab["COUNTY"] + tab["TRACT"]
    elif geo == "place":
        tab = ced.download(
            dataset,
            vintage,
            cols,
            state=state,
            place="*",
            with_geometry=True,
            api_key=api_key,
        )
        tab["GEOID"] = tab["STATE"] + tab["PLACE"]
    elif geo == "county":
        tab = ced.download(
            dataset,
            vintage,
            cols,
            state=state,
            county=county,
            with_geometry=True,
            api_key=api_key,
        )
        tab["GEOID"] = tab["STATE"] + tab["COUNTY"]
    elif geo == "state":
        tab = ced.download(
            dataset,
            vintage,
            cols,
            state=state,
            with_geometry=True,
            api_key=api_key,
        )
        tab["GEOID"] = tab["STATE"]
    else:
        raise KeyError("Not one of the geography options.")
    for cid in ["COUNTY", "PLACE", "TRACT"]:
        if cid not in tab.columns:
            tab[cid] = np.nan
    return tab


def make_race_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of population
        by race & hispanic/latino.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "race_not_hispanic_white_alone_percent",
            "race_not_hispanic_black_alone_percent",
            "race_not_hispanic_aian_alone_percent",
            "race_not_hispanic_asian_alone_percent",
            "race_not_hispanic_nhpi_alone_percent",
            "race_not_hispanic_otherrace_alone_percent",
            "race_not_hispanic_percent",
            "race_hispanic_percent",
            "race_personofcolor_percent",
            "geometry",
    """
    bcn = {
        "B03002_001E": "RACE_TOT_POP",
        "B03002_003E": "RACE_NOT_HISPANIC_WHITE_ALONE_POP",
        "B03002_004E": "RACE_NOT_HISPANIC_BLACK_ALONE_POP",
        "B03002_005E": "RACE_NOT_HISPANIC_AIAN_ALONE_POP",
        "B03002_006E": "RACE_NOT_HISPANIC_ASIAN_ALONE_POP",
        "B03002_007E": "RACE_NOT_HISPANIC_NHPI_ALONE_POP",
        "B03002_008E": "RACE_NOT_HISPANIC_OTHERRACE_ALONE_POP",
        "B03002_012E": "RACE_HISPANIC_TOT_POP",
        "B03002_002E": "RACE_NOT_HISPANIC_TOT_POP",
    }
    cols = ["NAME"] + list(bcn.keys())

    rt = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    rt["race_not_hispanic_white_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_WHITE_ALONE_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_not_hispanic_black_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_BLACK_ALONE_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_not_hispanic_aian_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_AIAN_ALONE_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_not_hispanic_asian_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_ASIAN_ALONE_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_not_hispanic_nhpi_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_NHPI_ALONE_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_not_hispanic_otherrace_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_OTHERRACE_ALONE_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_not_hispanic_percent"] = round(
        rt["RACE_NOT_HISPANIC_TOT_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_hispanic_percent"] = round(
        rt["RACE_HISPANIC_TOT_POP"] / rt["RACE_TOT_POP"],
        3,
    )
    rt["race_personofcolor_percent"] = round(
        1 - rt["race_not_hispanic_white_alone_percent"],
        3,
    )
    return rt[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "race_not_hispanic_white_alone_percent",
            "race_not_hispanic_black_alone_percent",
            "race_not_hispanic_aian_alone_percent",
            "race_not_hispanic_asian_alone_percent",
            "race_not_hispanic_nhpi_alone_percent",
            "race_not_hispanic_otherrace_alone_percent",
            "race_not_hispanic_percent",
            "race_hispanic_percent",
            "race_personofcolor_percent",
            "geometry",
        ]
    ]


def make_pov_limit_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of population
        by relationship to the federal poverty threshold.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "federal_poverty_limit_below_percent",
            "federal_poverty_limit_between_100_149_percent",
            "federal_poverty_limit_above_150_percent",
            "geometry",
    """
    bcn = {
        "B06012_001E": "TOT_POP_POVERTY",
        "B06012_002E": "POP_BELOW_POVERTY_LIMIT",
        "B06012_003E": "POP_BETWEEN_100-149_POVERTY_LIMIT",
        "B06012_004E": "POP_ABOVE_150_POVERTY_LIMIT",
    }
    cols = ["NAME"] + list(bcn.keys())
    plt = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    plt["federal_poverty_limit_below_percent"] = round(
        plt["POP_BELOW_POVERTY_LIMIT"] / plt["TOT_POP_POVERTY"],
        3,
    )
    plt["federal_poverty_limit_between_100_149_percent"] = round(
        plt["POP_BETWEEN_100-149_POVERTY_LIMIT"] / plt["TOT_POP_POVERTY"],
        3,
    )
    plt["federal_poverty_limit_above_150_percent"] = round(
        plt["POP_ABOVE_150_POVERTY_LIMIT"] / plt["TOT_POP_POVERTY"],
        3,
    )
    return plt[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "federal_poverty_limit_below_percent",
            "federal_poverty_limit_between_100_149_percent",
            "federal_poverty_limit_above_150_percent",
            "geometry",
        ]
    ]


def make_age_sex_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of population
        by sex (female) and by three age groups relevant for policy
        (under 5, under 18, and 65+)

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "sex_female_percent",
            "age_under_5_percent",
            "age_under_18_percent",
            "age_over_64_percent",
            "geometry",
    """
    bcn = {
        "B01001_026E": "SEX_FEMALE_POP",
        "B01001_001E": "SEX_AGE_TOT_POP",
        "B01001_003E": "AGE_UNDER_FIVE_MALE",
        "B01001_027E": "AGE_UNDER_FIVE_FEMALE",
        "B01001_004E": "AGE_5_9_MALE",
        "B01001_028E": "AGE_5_9_FEMALE",
        "B01001_005E": "AGE_10_14_MALE",
        "B01001_029E": "AGE_10_14_FEMALE",
        "B01001_006E": "AGE_15_17_MALE",
        "B01001_030E": "AGE_15_17_FEMALE",
        "B01001_020E": "AGE_65_66_MALE",
        "B01001_044E": "AGE_65_66_FEMALE",
        "B01001_021E": "AGE_67_69_MALE",
        "B01001_045E": "AGE_67_69_FEMALE",
        "B01001_022E": "AGE_70_74_MALE",
        "B01001_046E": "AGE_70_74_FEMALE",
        "B01001_023E": "AGE_75_79_MALE",
        "B01001_047E": "AGE_75_79_FEMALE",
        "B01001_024E": "AGE_80_84_MALE",
        "B01001_048E": "AGE_80_84_FEMALE",
        "B01001_025E": "AGE_85p_MALE",
        "B01001_049E": "AGE_85p_FEMALE",
    }
    cols = ["NAME"] + list(bcn.keys())
    ast = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    ast["sex_female_percent"] = round(
        ast["SEX_FEMALE_POP"] / ast["SEX_AGE_TOT_POP"],
        3,
    )

    ast["age_under_5_percent"] = round(
        (ast["AGE_UNDER_FIVE_FEMALE"] + ast["AGE_UNDER_FIVE_MALE"])
        / ast["SEX_AGE_TOT_POP"],
        3,
    )

    ast["age_under_18_percent"] = round(
        (
            ast["AGE_UNDER_FIVE_FEMALE"]
            + ast["AGE_UNDER_FIVE_MALE"]
            + ast["AGE_5_9_FEMALE"]
            + ast["AGE_5_9_MALE"]
            + ast["AGE_10_14_FEMALE"]
            + ast["AGE_10_14_MALE"]
            + ast["AGE_15_17_FEMALE"]
            + ast["AGE_15_17_MALE"]
        )
        / ast["SEX_AGE_TOT_POP"],
        3,
    )

    ast["age_over_64_percent"] = round(
        (
            ast["AGE_65_66_FEMALE"]
            + ast["AGE_65_66_MALE"]
            + ast["AGE_67_69_FEMALE"]
            + ast["AGE_67_69_MALE"]
            + ast["AGE_70_74_FEMALE"]
            + ast["AGE_70_74_MALE"]
            + ast["AGE_75_79_FEMALE"]
            + ast["AGE_75_79_MALE"]
            + ast["AGE_80_84_FEMALE"]
            + ast["AGE_80_84_MALE"]
            + ast["AGE_85p_FEMALE"]
            + ast["AGE_85p_MALE"]
        )
        / ast["SEX_AGE_TOT_POP"],
        3,
    )

    return ast[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "sex_female_percent",
            "age_under_5_percent",
            "age_under_18_percent",
            "age_over_64_percent",
            "geometry",
        ]
    ]


def make_units_in_struct_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of occupied housing units
    by number of units.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "units_in_struct_occupied_housing_units",
            "units_in_struct_occupied_housing_units_1_detached_percent",
            "units_in_struct_occupied_housing_units_1_attached_percent",
            "units_in_struct_occupied_housing_units_2_percent",
            "units_in_struct_occupied_housing_units_3_4_percent",
            "units_in_struct_occupied_housing_units_5_9_percent",
            "units_in_struct_occupied_housing_units_10_19_percent",
            "units_in_struct_occupied_housing_units_20_49_percent",
            "units_in_struct_occupied_housing_units_50_more_percent",
            "units_in_struct_occupied_housing_units_mobile_home_percent",
            "units_in_struct_occupied_housing_units_boat_rv_van_etc_percent",
            "geometry",
    """
    bcn = {
        "B25032_002E": "TENURE_BY_U_IN_STRUCT_OO_HUS",
        "B25032_013E": "TENURE_BY_U_IN_STRUCT_RO_HUS",
        "B25032_003E": "TENURE_BY_U_IN_STRUCT_OO_HUS_1_DETACHED",
        "B25032_004E": "TENURE_BY_U_IN_STRUCT_OO_HUS_1_ATTACHED",
        "B25032_005E": "TENURE_BY_U_IN_STRUCT_OO_HUS_2",
        "B25032_006E": "TENURE_BY_U_IN_STRUCT_OO_HUS_3_4",
        "B25032_007E": "TENURE_BY_U_IN_STRUCT_OO_HUS_5_9",
        "B25032_008E": "TENURE_BY_U_IN_STRUCT_OO_HUS_10_19",
        "B25032_009E": "TENURE_BY_U_IN_STRUCT_OO_HUS_20_49",
        "B25032_010E": "TENURE_BY_U_IN_STRUCT_OO_HUS_50_MORE",
        "B25032_011E": "TENURE_BY_U_IN_STRUCT_OO_HUS_MOBILEHOME",
        "B25032_012E": "TENURE_BY_U_IN_STRUCT_OO_HUS_BOAT_RV_VAN_ETC",
        "B25032_014E": "TENURE_BY_U_IN_STRUCT_RO_HUS_1_DETACHED",
        "B25032_015E": "TENURE_BY_U_IN_STRUCT_RO_HUS_1_ATTACHED",
        "B25032_016E": "TENURE_BY_U_IN_STRUCT_RO_HUS_2",
        "B25032_017E": "TENURE_BY_U_IN_STRUCT_RO_HUS_3_4",
        "B25032_018E": "TENURE_BY_U_IN_STRUCT_RO_HUS_5_9",
        "B25032_019E": "TENURE_BY_U_IN_STRUCT_RO_HUS_10_19",
        "B25032_020E": "TENURE_BY_U_IN_STRUCT_RO_HUS_20_49",
        "B25032_021E": "TENURE_BY_U_IN_STRUCT_RO_HUS_50_MORE",
        "B25032_022E": "TENURE_BY_U_IN_STRUCT_RO_HUS_MOBILEHOME",
        "B25032_023E": "TENURE_BY_U_IN_STRUCT_RO_HUS_BOAT_RV_VAN_ETC",
    }
    cols = ["NAME"] + list(bcn.keys())
    tut = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    tut["units_in_struct_occupied_housing_units"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS"] + tut["TENURE_BY_U_IN_STRUCT_RO_HUS"],
        3,
    )

    tut["units_in_struct_occupied_housing_units_1_detached_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_1_DETACHED"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_1_DETACHED"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_1_attached_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_1_ATTACHED"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_1_ATTACHED"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_2_percent"] = round(
        (tut["TENURE_BY_U_IN_STRUCT_OO_HUS_2"] + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_2"])
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_3_4_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_3_4"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_3_4"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_5_9_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_5_9"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_5_9"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_10_19_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_10_19"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_10_19"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_20_49_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_20_49"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_20_49"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_50_more_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_50_MORE"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_50_MORE"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_mobile_home_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_MOBILEHOME"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_MOBILEHOME"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    tut["units_in_struct_occupied_housing_units_boat_rv_van_etc_percent"] = round(
        (
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_BOAT_RV_VAN_ETC"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_BOAT_RV_VAN_ETC"]
        )
        / tut["units_in_struct_occupied_housing_units"],
        3,
    )
    return tut[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "units_in_struct_occupied_housing_units",
            "units_in_struct_occupied_housing_units_1_detached_percent",
            "units_in_struct_occupied_housing_units_1_attached_percent",
            "units_in_struct_occupied_housing_units_2_percent",
            "units_in_struct_occupied_housing_units_3_4_percent",
            "units_in_struct_occupied_housing_units_5_9_percent",
            "units_in_struct_occupied_housing_units_10_19_percent",
            "units_in_struct_occupied_housing_units_20_49_percent",
            "units_in_struct_occupied_housing_units_50_more_percent",
            "units_in_struct_occupied_housing_units_mobile_home_percent",
            "units_in_struct_occupied_housing_units_boat_rv_van_etc_percent",
            "geometry",
        ]
    ]


def make_year_built_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of buildings by year built.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "year_struct_built_2020_later_percent",
            "year_struct_built_2010_2019_percent",
            "year_struct_built_2000_2009_percent",
            "year_struct_built_1990_1999_percent",
            "year_struct_built_1980_1989_percent",
            "year_struct_built_1970_1979_percent",
            "year_struct_built_1960_1969_percent",
            "year_struct_built_1950_1959_percent",
            "year_struct_built_1940_1949_percent",
            "year_struct_built_pre_1940_percent",
            "year_struct_built_total_struct",
            "geometry",
    """
    bcn = {
        "B25034_001E": "year_struct_built_total_struct",
        "B25034_002E": "year_struct_built_2020_later",
        "B25034_003E": "year_struct_built_2010_2019",
        "B25034_004E": "year_struct_built_2000_2009",
        "B25034_005E": "year_struct_built_1990_1999",
        "B25034_006E": "year_struct_built_1980_1989",
        "B25034_007E": "year_struct_built_1970_1979",
        "B25034_008E": "year_struct_built_1960_1969",
        "B25034_009E": "year_struct_built_1950_1959",
        "B25034_010E": "year_struct_built_1940_1949",
        "B25034_011E": "year_struct_built_pre_1940",
    }
    cols = ["NAME"] + list(bcn.keys())
    ybt = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    ybt["year_struct_built_2020_later_percent"] = round(
        ybt["year_struct_built_2020_later"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_2010_2019_percent"] = round(
        ybt["year_struct_built_2010_2019"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_2000_2009_percent"] = round(
        ybt["year_struct_built_2000_2009"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_1990_1999_percent"] = round(
        ybt["year_struct_built_1990_1999"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_1980_1989_percent"] = round(
        ybt["year_struct_built_1980_1989"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_1970_1979_percent"] = round(
        ybt["year_struct_built_1970_1979"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_1960_1969_percent"] = round(
        ybt["year_struct_built_1960_1969"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_1950_1959_percent"] = round(
        ybt["year_struct_built_1950_1959"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_1940_1949_percent"] = round(
        ybt["year_struct_built_1940_1949"] / ybt["year_struct_built_total_struct"],
        3,
    )
    ybt["year_struct_built_pre_1940_percent"] = round(
        ybt["year_struct_built_pre_1940"] / ybt["year_struct_built_total_struct"],
        3,
    )

    return ybt[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "year_struct_built_2020_later_percent",
            "year_struct_built_2010_2019_percent",
            "year_struct_built_2000_2009_percent",
            "year_struct_built_1990_1999_percent",
            "year_struct_built_1980_1989_percent",
            "year_struct_built_1970_1979_percent",
            "year_struct_built_1960_1969_percent",
            "year_struct_built_1950_1959_percent",
            "year_struct_built_1940_1949_percent",
            "year_struct_built_pre_1940_percent",
            "year_struct_built_total_struct",
            "geometry",
        ]
    ]


def make_civ_emp_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of buildings by year built.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "employment_civilian_labor_force_percent",
            "employment_civilian_labor_force_employed_percent",
            "employment_civilian_labor_force_unemployed_percent",
            "employment_not_in_labor_force_percent",
            "geometry",
    """
    bcn = {
        "B23025_001E": "TOT_POP_16P",
        "B23025_003E": "EMPLOYMENT_CIVILIAN_LABOR_FORCE",
        "B23025_004E": "EMPLOYMENT_CIVILIAN_LABOR_FORCE_EMPLOYED",
        "B23025_005E": "EMPLOYMENT_CIVILIAN_LABOR_FORCE_UNEMPLOYED",
        "B23025_007E": "NOT_IN_LABOR_FORCE",
    }
    cols = ["NAME"] + list(bcn.keys())
    cet = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    cet["employment_civilian_labor_force_percent"] = round(
        cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE"] / cet["TOT_POP_16P"],
        3,
    )
    cet["employment_civilian_labor_force_employed_percent"] = round(
        cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE_EMPLOYED"]
        / cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE"],
        3,
    )
    cet["employment_civilian_labor_force_unemployed_percent"] = round(
        cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE_UNEMPLOYED"]
        / cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE"],
        3,
    )
    cet["employment_not_in_labor_force_percent"] = round(
        cet["NOT_IN_LABOR_FORCE"] / cet["TOT_POP_16P"],
        3,
    )

    return cet[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "employment_civilian_labor_force_percent",
            "employment_civilian_labor_force_employed_percent",
            "employment_civilian_labor_force_unemployed_percent",
            "employment_not_in_labor_force_percent",
            "geometry",
        ]
    ]


def make_tenure_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage households living in owner-occupied
    and renter-occupied housing units.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "tenure_owner_occupied_percent",
            "tenure_renter_occupied_percent",
            "tenure_total_hh",
            "geometry",
    """
    bcn = {
        "B25003_001E": "tenure_total_hh",
        "B25003_002E": "tenure_owner_occupied",
        "B25003_003E": "tenure_renter_occupied",
    }
    cols = ["NAME"] + list(bcn.keys())
    ten = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    ten["tenure_owner_occupied_percent"] = round(
        ten["tenure_owner_occupied"] / ten["tenure_total_hh"], 3
    )
    ten["tenure_renter_occupied_percent"] = round(
        ten["tenure_renter_occupied"] / ten["tenure_total_hh"], 3
    )

    return ten[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "tenure_owner_occupied_percent",
            "tenure_renter_occupied_percent",
            "tenure_total_hh",
            "geometry",
        ]
    ]


def make_med_inc_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for median household income in vintage dollars.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "median_household_income_{vintage}$"
            "geometry",
    """
    bcn = {
        "B19013_001E": f"median_household_income_{vintage}$",
    }
    cols = ["NAME"] + list(bcn.keys())
    mit = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    return mit[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            f"median_household_income_{vintage}$",
            "geometry",
        ]
    ]


def make_basics_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for basic universe counts:
        total population, total housing units, total households.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "total_population_universe",
            "total_households_universe",
            "total_housing_units_universe",
            "geometry",
    """
    bcn = {
        "B01003_001E": "total_population_universe",
        "B08201_001E": "total_households_universe",
        "B25002_001E": "total_housing_units_universe",
    }
    cols = ["NAME"] + list(bcn.keys())
    bt = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    return bt[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "total_population_universe",
            "total_households_universe",
            "total_housing_units_universe",
            "geometry",
        ]
    ]


def make_occupancy_tables(
    dataset: str = ACS5,
    state: list[str] | str = ALL_STATES_AND_DC,
    county: list[str] | str = "*",
    geo: str = "tract",
    vintage: int = 2024,
    api_key: str | None = None,
) -> gpd.GeoDataFrame | pd.DataFrame:
    """
    Create a predefined table for percentage of housing units that
      are occupied or vacant.

    This function calls the dwnld_acs5 function so all that
    applies to that function also applies to this one (including defaults).

    Defaults:
        - Dataset: ACS 5YR Estimates
        - Vintage: 2024
        - Geography:
            - state: ALL STATES + DC
            - county: All counties in the selected states
            - geo: tract - the smallest unit of geo you can select for this function.
                Alternatively can be Place, County, or State.
        - API Key read from .env file (you can also provide as a string)

    Parameters
    ----------
    dataset: str
        String representing the dataset you are downloading.
        Defaults to "acs/acs5" - from censusdis = ACS_5
    state: list[str] | str
        List of two letter state FIPS codes that you want to download data for.
        Defaults to censusdis constant ALL_STATES_AND_DC.
    county: list[str] | str
        List of county FIPS codes that you want to download data for. Must match
        the states in the state list specified above.
        Defaults to "*" (all)
    geo: str
        The base geographic category that you want your data in.
        Defaults to "tract". Other options are ["county", "state", "place]
    vintage: int
        Year of dataset. Defaults to 2024.
    api_key: str
        Census API Key. Defaults to pulling from the environment variable.

    Returns
    -------
    tab : gpd.GeoDataFrame (with_geometry always set to TRUE)
        Columns -
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "total_housing_units_universe",
            "occupied_housing_units_percent",
            "vacant_housing_units_percent",
            "geometry",
    """
    bcn = {
        "B25002_001E": "total_housing_units_universe",
        "B25002_002E": "occupied_housing_units",
        "B25002_003E": "vacant_housing_units",
    }
    cols = ["NAME"] + list(bcn.keys())
    ot = dwnld_acs5(
        cols,
        dataset=dataset,
        state=state,
        county=county,
        geo=geo,
        vintage=vintage,
        api_key=api_key,
    ).rename(columns=bcn)

    ot["occupied_housing_units_percent"] = round(
        ot["occupied_housing_units"] / ot["total_housing_units_universe"],
        3,
    )
    ot["vacant_housing_units_percent"] = round(
        ot["vacant_housing_units"] / ot["total_housing_units_universe"],
        3,
    )

    return ot[
        [
            "GEOID",
            "STATE",
            "COUNTY",
            "PLACE",
            "TRACT",
            "NAME",
            "total_housing_units_universe",
            "occupied_housing_units_percent",
            "vacant_housing_units_percent",
            "geometry",
        ]
    ]

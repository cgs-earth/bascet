[![black](https://github.com/cgs-earth/bascet/actions/workflows/black.yml/badge.svg)](https://github.com/cgs-earth/bascet/actions/workflows/black.yml)
[![tests](https://github.com/cgs-earth/bascet/actions/workflows/test.yml/badge.svg)](https://github.com/cgs-earth/bascet/actions/workflows/test.yml)

# bascet
bascet = BASic CEnsus Tables.

A way to easily grab some pre-formatted tables from the American Community Survey.

Attending Metaphysician: Margo Atkinson (matkinson@lincolninst.edu)

Examples with the Decennial Census and CPS forthcoming.

## Install

```pip install bascet```

## Census API key
bascet downloads data from the Census Bureau API, which needs a free API key.
If you don't have one, request it here: https://api.census.gov/data/key_signup.html

Save your key once with `save_api_key()`:

```python
import bascet

bascet.save_api_key("your-census-api-key")
```

This does two things:
1. Writes `CENSUS_API_KEY="your-census-api-key"` to a `.env` file in your **current
   working directory** (creating the file if needed, or updating the key if it is
   already there).
2. Sets the `CENSUS_API_KEY` environment variable for the current Python session, so
   you can start downloading right away.

It returns the path of the `.env` file it wrote.

In later sessions you don't need to call it again: every download function looks up the key automatically (via `get_api_key()`), first from the `CENSUS_API_KEY` environment variable, then from a `.env` file in the current working directory or any of its parent folders. So run your scripts or notebooks from the folder where you saved the key (or one below it). If no key is found, you'll get a `KeyError` asking you to run `save_api_key()`.

Other ways to provide the key:
- Set the `CENSUS_API_KEY` environment variable yourself.
- Copy [.env.example](https://github.com/cgs-earth/bascet/blob/main/.env.example) to
  `.env` and replace the placeholder with your key.
- Pass it directly to any download function with `api_key="..."`.

> **Keep your key private.** Don't commit your `.env` file. Add `.env` to your
> `.gitignore` if your project is in a git repository.

## Examples
Simple:
```
from bascet.access_acs import make_age_sex_tables
from bascet.export_acs import acs2parquet
from censusdis.states import STATE_RI  # state FIPS code

age_sex = make_age_sex_tables(state=STATE_RI, geo="tract")
acs2parquet(age_sex, "bascet\out\age_sex.parquet")

```

Combination / Advanced:
See: https://github.com/cgs-earth/bascet/blob/main/notebooks/acs_access_demo.ipynb
or create your own tables with: dwnld_acs5()

## Tables
#### dwnld_acs5()
```
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
```

#### make_race_tables()
```
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
```

#### make_pov_limit_tables()
```
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
```

#### make_age_sex_tables()
```
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
```

#### make_units_in_struct_tables()
```
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
```

#### make_year_built_tables()
```
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
```

#### make_civ_emp_tables()
```
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
```

#### make_tenure_tables()
```
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
```

#### make_med_inc_tables()
```
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
```

#### make_basics_tables()
```
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
```

#### make_occupancy_tables()
```
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
```
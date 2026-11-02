[![black](https://github.com/cgs-earth/bascet/actions/workflows/black.yml/badge.svg)](https://github.com/cgs-earth/bascet/actions/workflows/black.yml)
[![tests](https://github.com/cgs-earth/bascet/actions/workflows/test.yml/badge.svg)](https://github.com/cgs-earth/bascet/actions/workflows/test.yml)

# bascet
bascet = BASic CEnsus Tables.

A way to easily grab some pre-formatted tables from the American Community Survey.

Attending Metaphysician: Margo Atkinson (matkinson@lincolninst.edu)

Examples with the Decennial Census and CPS forthcoming.

## Install

```bash
pip install bascet
```

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
```python
from bascet import make_basics_tables, acs2csv, acs2spat
from censusdis.states import STATE_RI

basics = make_basics_tables(state=STATE_RI)
acs2csv(basics, "ri_basics.csv")
acs2spat(basics, "ri_basics.gpkg")
acs2spat(basics, "ri_basics.shp")  # short column names
```

Combination / Advanced:
See the [demo notebook](https://github.com/cgs-earth/bascet/blob/main/notebooks/acs_access_demo.ipynb),
or create your own tables with `dwnld_acs5()`.

## Exporting
Every table can be saved with one of the export helpers. If `out_path` has no file
extension, the default one is added. The folder you save into must already exist.

| Function | Output | Notes |
| --- | --- | --- |
| `acs2csv(tab, out_path)` | `.csv` | Drops the `geometry` column first. |
| `acs2parquet(tab, out_path)` | `.parquet` | Keeps geometry when given a GeoDataFrame. |
| `acs2spat(tab, out_path, vint=2024)` | `.gpkg` (default) or `.shp` | Needs a GeoDataFrame. For `.shp`, columns are renamed to 10 characters (shapefile limit) using `ten_char_names()`. Set `vint` to your data's year so the median income column is renamed correctly. |
| `ten_char_names(vintage=2024)` | `dict` | The full-name → 10-character column mapping used for shapefiles. |



## Tables
Every function below returns a `geopandas.GeoDataFrame` (one row per geography, with
`geometry`). All share the same arguments (`state`, `county`, `geo`, `vintage`,
`dataset`, `api_key`), and every table also includes these ID columns:
`GEOID`, `STATE`, `COUNTY`, `PLACE`, `TRACT`, `NAME`, `geometry`.
ID columns that don't apply to the chosen `geo` are left empty (e.g. `TRACT` for
`geo="county"`).

All % return values are between 0 and 1.

| Function | What it returns | Key columns |
| --- | --- | --- |
| `dwnld_acs5(cols, ...)` | Any ACS variables you choose (build your own table). | Your requested `cols` |
| `make_basics_tables()` | Universe counts: total population, households, and housing units. | `total_population_universe`, `total_households_universe`, `total_housing_units_universe` |
| `make_age_sex_tables()` | % of population that is female and in three policy-relevant age groups. | `sex_female_percent`, `age_under_5_percent`, `age_under_18_percent`, `age_over_64_percent` |
| `make_race_tables()` | % of population by race and Hispanic/Latino origin. | `race_not_hispanic_{white,black,aian,asian,nhpi,otherrace}_alone_percent`, `race_not_hispanic_percent`, `race_hispanic_percent`, `race_personofcolor_percent` |
| `make_pov_limit_tables()` | % of population by income relative to the federal poverty threshold. | `federal_poverty_limit_below_percent`, `federal_poverty_limit_between_100_149_percent`, `federal_poverty_limit_above_150_percent` |
| `make_med_inc_tables()` | Median household income, in dollars of the `vintage` year. | `median_household_income_{vintage}$` (e.g. `median_household_income_2024$`) |
| `make_civ_emp_tables()` | % of population 16+ in/out of the civilian labor force, and % of the civilian labor force employed/unemployed. | `employment_civilian_labor_force_percent`, `employment_civilian_labor_force_employed_percent`, `employment_civilian_labor_force_unemployed_percent`, `employment_not_in_labor_force_percent` |
| `make_tenure_tables()` | % of households in owner- vs. renter-occupied housing. | `tenure_owner_occupied_percent`, `tenure_renter_occupied_percent`, `tenure_total_hh` |
| `make_occupancy_tables()` | % of housing units that are occupied vs. vacant. | `total_housing_units_universe`, `occupied_housing_units_percent`, `vacant_housing_units_percent` |
| `make_units_in_struct_tables()` | % of occupied housing units by number of units in the building. | `units_in_struct_occupied_housing_units` (total), then `units_in_struct_occupied_housing_units_{1_detached,1_attached,2,3_4,5_9,10_19,20_49,50_more,mobile_home,boat_rv_van_etc}_percent` |
| `make_year_built_tables()` | % of buildings by decade built. | `year_struct_built_{2020_later,2010_2019,2000_2009,...,1940_1949,pre_1940}_percent`, `year_struct_built_total_struct` |

For full details on any function, use `help()`, e.g. `help(bascet.make_race_tables)`.

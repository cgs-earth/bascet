"""
bascet = BASic CEnsus Tables.

Pre-formatted tables from the American Community Survey, plus helpers
to export them.
"""

from importlib.metadata import PackageNotFoundError, version

from bascet.access_acs import (
    dwnld_acs5,
    get_api_key,
    make_age_sex_tables,
    make_basics_tables,
    make_civ_emp_tables,
    make_med_inc_tables,
    make_occupancy_tables,
    make_pov_limit_tables,
    make_race_tables,
    make_tenure_tables,
    make_units_in_struct_tables,
    make_year_built_tables,
    save_api_key,
)
from bascet.export_acs import acs2csv, acs2parquet, acs2spat, ten_char_names

try:
    # Must match `name` in pyproject.toml.
    __version__ = version("bascet")
except PackageNotFoundError:  # running from a source checkout without installing
    __version__ = "unknown"

__all__ = [
    "__version__",
    "acs2csv",
    "acs2parquet",
    "acs2spat",
    "dwnld_acs5",
    "get_api_key",
    "make_age_sex_tables",
    "make_basics_tables",
    "make_civ_emp_tables",
    "make_med_inc_tables",
    "make_occupancy_tables",
    "make_pov_limit_tables",
    "make_race_tables",
    "make_tenure_tables",
    "make_units_in_struct_tables",
    "make_year_built_tables",
    "save_api_key",
    "ten_char_names",
]

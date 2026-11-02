# Changelog

All notable changes to bascet are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1]

First release.

### Added
- `dwnld_acs5()` to download ACS 5-year estimates at the tract level (with geometry) via censusdis.
- Pre-formatted table builders: `make_basics_tables()`, `make_age_sex_tables()`,
  `make_race_tables()`, `make_tenure_tables()`, `make_occupancy_tables()`,
  `make_units_in_struct_tables()`, `make_year_built_tables()`, `make_med_inc_tables()`,
  `make_pov_limit_tables()`, and `make_civ_emp_tables()`.
- Census API key helpers: `save_api_key()` and `get_api_key()`.
- Export helpers: `acs2csv()`, `acs2parquet()`, `acs2spat()`, and `ten_char_names()`.
- Unit tests and CI on Python 3.10–3.13.

[Unreleased]: https://github.com/cgs-earth/bascet/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/cgs-earth/bascet/releases/tag/v0.0.1

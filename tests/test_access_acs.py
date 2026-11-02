import inspect
from pathlib import Path

import numpy as np
import pytest

import bascet.access_acs as access_acs
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

ID_COLS = ["GEOID", "STATE", "COUNTY", "PLACE", "TRACT", "NAME"]


# ---------------------------------------------------------------------------
# API key helpers
# ---------------------------------------------------------------------------


def test_save_api_key_writes_env_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    env_loc = save_api_key("my-test-key")

    assert env_loc == Path("./.env")
    assert "CENSUS_API_KEY='my-test-key'" in (tmp_path / ".env").read_text()


def test_save_api_key_updates_existing_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("OTHER=1\nCENSUS_API_KEY='old'\n")

    save_api_key("new")

    text = (tmp_path / ".env").read_text()
    assert "CENSUS_API_KEY='new'" in text
    assert "old" not in text
    assert "OTHER=1" in text


def test_get_api_key_reads_environment(monkeypatch):
    monkeypatch.setenv("CENSUS_API_KEY", "from-env")
    assert get_api_key() == "from-env"


def test_get_api_key_returns_none_when_unset():
    assert get_api_key() is None


def test_get_api_key_reads_env_file_in_working_directory(tmp_path):
    (tmp_path / ".env").write_text("CENSUS_API_KEY='from-file'\n")
    assert get_api_key() == "from-file"


def test_get_api_key_searches_parent_directories(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("CENSUS_API_KEY='from-parent'\n")
    (tmp_path / "sub").mkdir()
    monkeypatch.chdir(tmp_path / "sub")
    assert get_api_key() == "from-parent"


def test_saved_key_is_used_in_same_session(fake_download):
    save_api_key("old")
    dwnld_acs5(["NAME"])
    save_api_key("new")
    dwnld_acs5(["NAME"])

    assert [c["api_key"] for c in fake_download.calls] == ["old", "new"]


def test_api_key_default_is_not_read_at_import():
    assert inspect.signature(dwnld_acs5).parameters["api_key"].default is None


# ---------------------------------------------------------------------------
# dwnld_acs5
# ---------------------------------------------------------------------------


def test_dwnld_acs5_raises_without_api_key(fake_download, monkeypatch):
    monkeypatch.setattr(access_acs, "get_api_key", lambda: None)

    with pytest.raises(KeyError):
        dwnld_acs5(["NAME"], api_key=None)
    assert fake_download.calls == []


def test_dwnld_acs5_falls_back_to_stored_key(fake_download, monkeypatch):
    monkeypatch.setattr(access_acs, "get_api_key", lambda: "stored")

    dwnld_acs5(["NAME"], api_key=None)

    assert fake_download.calls[0]["api_key"] == "stored"


def test_dwnld_acs5_passes_arguments_through(fake_download):
    dwnld_acs5(
        ["NAME", "B01003_001E"],
        dataset="dec/pl",
        state=["25", "44"],
        county="017",
        vintage=2020,
        api_key="k",
    )

    call = fake_download.calls[0]
    assert call["dataset"] == "dec/pl"
    assert call["vintage"] == 2020
    assert call["cols"] == ["NAME", "B01003_001E"]
    assert call["state"] == ["25", "44"]
    assert call["county"] == "017"
    assert call["with_geometry"] is True
    assert call["api_key"] == "k"


@pytest.mark.parametrize(
    "geo, geo_kwargs, missing_kwargs, expected_geoid, nan_cols",
    [
        (
            "tract",
            {"county": "*", "tract": "*"},
            ["place"],
            ["25017000100", "25025000200"],
            ["PLACE"],
        ),
        (
            "place",
            {"place": "*"},
            ["county", "tract"],
            ["2507000", "2537000"],
            ["COUNTY", "TRACT"],
        ),
        (
            "county",
            {"county": "*"},
            ["place", "tract"],
            ["25017", "25025"],
            ["PLACE", "TRACT"],
        ),
        (
            "state",
            {},
            ["county", "place", "tract"],
            ["25", "25"],
            ["COUNTY", "PLACE", "TRACT"],
        ),
    ],
)
def test_dwnld_acs5_geographies(
    fake_download, geo, geo_kwargs, missing_kwargs, expected_geoid, nan_cols
):
    tab = dwnld_acs5(["NAME"], geo=geo, api_key="k")

    call = fake_download.calls[0]
    for k, v in geo_kwargs.items():
        assert call[k] == v
    for k in missing_kwargs:
        assert k not in call

    assert tab["GEOID"].tolist() == expected_geoid
    for c in ["COUNTY", "PLACE", "TRACT"]:
        assert c in tab.columns
    for c in nan_cols:
        assert tab[c].isna().to_numpy().all()


def test_dwnld_acs5_invalid_geo(fake_download):
    with pytest.raises(KeyError, match="geography"):
        dwnld_acs5(["NAME"], geo="block", api_key="k")
    assert fake_download.calls == []


# ---------------------------------------------------------------------------
# Predefined tables: shared behavior
# ---------------------------------------------------------------------------

TABLES = [
    (
        make_race_tables,
        "B03002",
        [
            "race_not_hispanic_white_alone_percent",
            "race_not_hispanic_black_alone_percent",
            "race_not_hispanic_aian_alone_percent",
            "race_not_hispanic_asian_alone_percent",
            "race_not_hispanic_nhpi_alone_percent",
            "race_not_hispanic_otherrace_alone_percent",
            "race_not_hispanic_percent",
            "race_hispanic_percent",
            "race_personofcolor_percent",
        ],
    ),
    (
        make_pov_limit_tables,
        "B06012",
        [
            "federal_poverty_limit_below_percent",
            "federal_poverty_limit_between_100_149_percent",
            "federal_poverty_limit_above_150_percent",
        ],
    ),
    (
        make_age_sex_tables,
        "B01001",
        [
            "sex_female_percent",
            "age_under_5_percent",
            "age_under_18_percent",
            "age_over_64_percent",
        ],
    ),
    (
        make_units_in_struct_tables,
        "B25032",
        [
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
        ],
    ),
    (
        make_year_built_tables,
        "B25034",
        [
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
        ],
    ),
    (
        make_civ_emp_tables,
        "B23025",
        [
            "employment_civilian_labor_force_percent",
            "employment_civilian_labor_force_employed_percent",
            "employment_civilian_labor_force_unemployed_percent",
            "employment_not_in_labor_force_percent",
        ],
    ),
    (
        make_tenure_tables,
        "B25003",
        [
            "tenure_owner_occupied_percent",
            "tenure_renter_occupied_percent",
            "tenure_total_hh",
        ],
    ),
    (make_med_inc_tables, "B19013", ["median_household_income_2024$"]),
    (
        make_basics_tables,
        None,
        [
            "total_population_universe",
            "total_households_universe",
            "total_housing_units_universe",
        ],
    ),
    (
        make_occupancy_tables,
        "B25002",
        [
            "total_housing_units_universe",
            "occupied_housing_units_percent",
            "vacant_housing_units_percent",
        ],
    ),
]


@pytest.mark.parametrize(
    "func, table_id, value_cols", TABLES, ids=[t[0].__name__ for t in TABLES]
)
def test_table_output_columns(fake_download, func, table_id, value_cols):
    tab = func(api_key="k")
    assert tab.columns.tolist() == ID_COLS + value_cols + ["geometry"]


@pytest.mark.parametrize(
    "func, table_id, value_cols", TABLES, ids=[t[0].__name__ for t in TABLES]
)
def test_table_requests_name_and_its_table(fake_download, func, table_id, value_cols):
    func(api_key="k")

    cols = fake_download.calls[0]["cols"]
    assert cols[0] == "NAME"
    assert len(cols) == len(set(cols))
    if table_id is not None:
        assert all(c.startswith(table_id) for c in cols[1:])


@pytest.mark.parametrize(
    "func, table_id, value_cols", TABLES, ids=[t[0].__name__ for t in TABLES]
)
def test_table_forwards_download_options(fake_download, func, table_id, value_cols):
    func(
        dataset="acs/acs1",
        state="25",
        county="017",
        geo="county",
        vintage=2022,
        api_key="k",
    )

    call = fake_download.calls[0]
    assert call["dataset"] == "acs/acs1"
    assert call["state"] == "25"
    assert call["county"] == "017"
    assert call["vintage"] == 2022
    assert call["api_key"] == "k"
    assert "tract" not in call


# ---------------------------------------------------------------------------
# Predefined tables: calculations
# ---------------------------------------------------------------------------


def test_race_percentages(fake_download):
    fake_download.values.update(
        {
            "B03002_001E": [1000, 300],
            "B03002_002E": [800, 150],
            "B03002_003E": [500, 100],
            "B03002_004E": [200, 0],
            "B03002_005E": [10, 0],
            "B03002_006E": [50, 50],
            "B03002_007E": [5, 0],
            "B03002_008E": [35, 0],
            "B03002_012E": [200, 150],
        }
    )

    tab = make_race_tables(api_key="k")

    row = tab.iloc[0]
    assert row["race_not_hispanic_white_alone_percent"] == 0.5
    assert row["race_not_hispanic_black_alone_percent"] == 0.2
    assert row["race_not_hispanic_aian_alone_percent"] == 0.01
    assert row["race_not_hispanic_asian_alone_percent"] == 0.05
    assert row["race_not_hispanic_nhpi_alone_percent"] == 0.005
    assert row["race_not_hispanic_otherrace_alone_percent"] == 0.035
    assert row["race_not_hispanic_percent"] == 0.8
    assert row["race_hispanic_percent"] == 0.2
    assert row["race_personofcolor_percent"] == 0.5
    # 100 / 300 rounds to 3 decimals
    assert tab.iloc[1]["race_not_hispanic_white_alone_percent"] == 0.333
    assert tab.iloc[1]["race_personofcolor_percent"] == 0.667


def test_pov_limit_percentages(fake_download):
    fake_download.values.update(
        {
            "B06012_001E": [200, 400],
            "B06012_002E": [50, 40],
            "B06012_003E": [30, 60],
            "B06012_004E": [120, 300],
        }
    )

    tab = make_pov_limit_tables(api_key="k")

    assert tab["federal_poverty_limit_below_percent"].tolist() == [0.25, 0.1]
    assert tab["federal_poverty_limit_between_100_149_percent"].tolist() == [0.15, 0.15]
    assert tab["federal_poverty_limit_above_150_percent"].tolist() == [0.6, 0.75]


def test_age_sex_percentages(fake_download):
    # Every age bucket is 10 people; total 1000, 520 female.
    fake_download.values.update(
        {"B01001_001E": [1000, 1000], "B01001_026E": [520, 520]}
    )

    tab = make_age_sex_tables(api_key="k")

    row = tab.iloc[0]
    assert row["sex_female_percent"] == 0.52
    assert row["age_under_5_percent"] == 0.02  # 2 buckets
    assert row["age_under_18_percent"] == 0.08  # 8 buckets
    assert row["age_over_64_percent"] == 0.12  # 12 buckets


def test_units_in_struct_percent_of_all_occupied_units(fake_download):
    # Owner-occupied columns are B25032_002E..012E, renter are 013E..023E.
    for i in range(2, 24):
        fake_download.values[f"B25032_{i:03d}E"] = [0, 0]
    fake_download.values.update(
        {
            "B25032_002E": [60, 2],  # owner total
            "B25032_013E": [40, 1],  # renter total
            "B25032_003E": [30, 1],  # owner 1 detached
            "B25032_014E": [10, 0],  # renter 1 detached
            "B25032_023E": [5, 0],  # renter boat/rv/van
        }
    )

    tab = make_units_in_struct_tables(api_key="k")

    row = tab.iloc[0]
    assert row["units_in_struct_occupied_housing_units"] == 100
    assert row["units_in_struct_occupied_housing_units_1_detached_percent"] == 0.4
    assert row["units_in_struct_occupied_housing_units_boat_rv_van_etc_percent"] == 0.05
    assert row["units_in_struct_occupied_housing_units_2_percent"] == 0
    assert tab.iloc[1]["units_in_struct_occupied_housing_units"] == 3
    assert (
        tab.iloc[1]["units_in_struct_occupied_housing_units_1_detached_percent"]
        == 0.333
    )


def test_year_built_percentages(fake_download):
    fake_download.values["B25034_001E"] = [400, 3]
    for i in range(2, 12):
        fake_download.values[f"B25034_{i:03d}E"] = [40, 1]

    tab = make_year_built_tables(api_key="k")

    pct_cols = [c for c in tab.columns if c.endswith("_percent")]
    assert len(pct_cols) == 10
    assert tab[pct_cols].iloc[0].eq(0.1).all()
    assert tab[pct_cols].iloc[1].eq(0.333).all()
    assert tab["year_struct_built_total_struct"].tolist() == [400, 3]


def test_civ_emp_uses_correct_denominators(fake_download):
    fake_download.values.update(
        {
            "B23025_001E": [1000, 1000],
            "B23025_003E": [600, 600],
            "B23025_004E": [540, 540],
            "B23025_005E": [60, 60],
            "B23025_007E": [400, 400],
        }
    )

    tab = make_civ_emp_tables(api_key="k")

    row = tab.iloc[0]
    assert row["employment_civilian_labor_force_percent"] == 0.6
    # employed / unemployed are shares of the labor force, not of all 16+
    assert row["employment_civilian_labor_force_employed_percent"] == 0.9
    assert row["employment_civilian_labor_force_unemployed_percent"] == 0.1
    assert row["employment_not_in_labor_force_percent"] == 0.4


def test_tenure_percentages(fake_download):
    fake_download.values.update(
        {
            "B25003_001E": [80, 3],
            "B25003_002E": [60, 1],
            "B25003_003E": [20, 2],
        }
    )

    tab = make_tenure_tables(api_key="k")

    assert tab["tenure_owner_occupied_percent"].tolist() == [0.75, 0.333]
    assert tab["tenure_renter_occupied_percent"].tolist() == [0.25, 0.667]
    assert tab["tenure_total_hh"].tolist() == [80, 3]


def test_med_inc_column_named_for_vintage(fake_download):
    fake_download.values["B19013_001E"] = [55000, 72000]

    tab = make_med_inc_tables(vintage=2021, api_key="k")

    assert "median_household_income_2021$" in tab.columns
    assert tab["median_household_income_2021$"].tolist() == [55000, 72000]


def test_basics_renames_universe_counts(fake_download):
    fake_download.values.update(
        {
            "B01003_001E": [5000, 6000],
            "B08201_001E": [2000, 2500],
            "B25002_001E": [2200, 2600],
        }
    )

    tab = make_basics_tables(api_key="k")

    assert tab["total_population_universe"].tolist() == [5000, 6000]
    assert tab["total_households_universe"].tolist() == [2000, 2500]
    assert tab["total_housing_units_universe"].tolist() == [2200, 2600]


def test_occupancy_percentages(fake_download):
    fake_download.values.update(
        {
            "B25002_001E": [200, 0],
            "B25002_002E": [180, 0],
            "B25002_003E": [20, 0],
        }
    )

    tab = make_occupancy_tables(api_key="k")

    assert tab.iloc[0]["occupied_housing_units_percent"] == 0.9
    assert tab.iloc[0]["vacant_housing_units_percent"] == 0.1
    # zero housing units yields NaN rather than raising
    assert np.isnan(tab.iloc[1]["occupied_housing_units_percent"])

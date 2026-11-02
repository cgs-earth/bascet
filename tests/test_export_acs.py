import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

import bascet.access_acs as access_acs
from bascet.export_acs import acs2csv, acs2parquet, acs2spat, ten_char_names


@pytest.fixture
def gdf():
    return gpd.GeoDataFrame(
        {
            "GEOID": ["25017000100", "25025000200"],
            "NAME": ["Area A", "Area B"],
            "race_hispanic_percent": [0.2, 0.5],
            "median_household_income_2024$": [55000, 72000],
        },
        geometry=[Point(0, 0), Point(1, 1)],
        crs="EPSG:4326",
    )


# ---------------------------------------------------------------------------
# acs2parquet
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["out", "out.parquet"])
def test_acs2parquet_writes_parquet(tmp_path, gdf, name):
    acs2parquet(gdf, str(tmp_path / name))

    result = gpd.read_parquet(tmp_path / "out.parquet")
    assert result["GEOID"].tolist() == gdf["GEOID"].tolist()
    assert result.geometry.equals(gdf.geometry)


def test_acs2parquet_accepts_plain_dataframe(tmp_path):
    df = pd.DataFrame({"GEOID": ["25"], "x": [1.0]})

    acs2parquet(df, str(tmp_path / "out"))

    pd.testing.assert_frame_equal(pd.read_parquet(tmp_path / "out.parquet"), df)


def test_acs2parquet_rejects_other_suffix(tmp_path, gdf):
    with pytest.raises(ValueError, match=".parquet"):
        acs2parquet(gdf, str(tmp_path / "out.csv"))
    assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------------------
# acs2spat
# ---------------------------------------------------------------------------


def test_acs2spat_requires_geodataframe(tmp_path):
    df = pd.DataFrame({"GEOID": ["25"]})
    with pytest.raises(TypeError):
        acs2spat(df, str(tmp_path / "out.gpkg"))  # type: ignore


@pytest.mark.parametrize("name", ["out", "out.gpkg"])
def test_acs2spat_writes_geopackage(tmp_path, gdf, name):
    acs2spat(gdf, str(tmp_path / name))

    result = gpd.read_file(tmp_path / "out.gpkg")
    assert result["race_hispanic_percent"].tolist() == [0.2, 0.5]
    assert "median_household_income_2024$" in result.columns


def test_acs2spat_shapefile_shortens_column_names(tmp_path, gdf):
    acs2spat(gdf, str(tmp_path / "out.shp"))

    result = gpd.read_file(tmp_path / "out.shp")
    assert "hisp_perc" in result.columns
    assert "med_inc" in result.columns
    assert result["med_inc"].tolist() == [55000, 72000]
    # input is not modified in place
    assert "race_hispanic_percent" in gdf.columns


def test_acs2spat_shapefile_uses_vintage_for_income(tmp_path, gdf):
    gdf = gdf.rename(
        columns={"median_household_income_2024$": "median_household_income_2019$"}
    )

    acs2spat(gdf, str(tmp_path / "out.shp"), vint=2019)

    assert "med_inc" in gpd.read_file(tmp_path / "out.shp").columns


def test_acs2spat_rejects_other_suffix(tmp_path, gdf):
    with pytest.raises(ValueError, match=".shp"):
        acs2spat(gdf, str(tmp_path / "out.geojson"))
    assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------------------
# acs2csv
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["out", "out.csv"])
def test_acs2csv_drops_geometry(tmp_path, gdf, name):
    acs2csv(gdf, str(tmp_path / name))

    result = pd.read_csv(tmp_path / "out.csv", index_col=0, dtype={"GEOID": str})
    assert "geometry" not in result.columns
    assert result["GEOID"].tolist() == gdf["GEOID"].tolist()


def test_acs2csv_rejects_other_suffix(tmp_path, gdf):
    with pytest.raises(ValueError, match=".csv"):
        acs2csv(gdf, str(tmp_path / "out.txt"))
    assert list(tmp_path.iterdir()) == []


def test_acs2csv_accepts_dataframe_without_geometry(tmp_path):
    df = pd.DataFrame({"GEOID": ["25"], "x": [1.0]})

    acs2csv(df, str(tmp_path / "out.csv"))

    assert (tmp_path / "out.csv").exists()


# ---------------------------------------------------------------------------
# ten_char_names
# ---------------------------------------------------------------------------


def test_ten_char_names_fit_shapefile_limit():
    names = ten_char_names()
    assert all(len(v) <= 10 for v in names.values())


def test_ten_char_names_are_unique():
    names = list(ten_char_names().values())
    assert len(names) == len(set(names))


def test_ten_char_names_income_key_uses_vintage():
    assert ten_char_names(2019)["median_household_income_2019$"] == "med_inc"
    assert "median_household_income_2024$" not in ten_char_names(2019)


TABLE_FUNCS = [
    access_acs.make_race_tables,
    access_acs.make_pov_limit_tables,
    access_acs.make_age_sex_tables,
    access_acs.make_units_in_struct_tables,
    access_acs.make_year_built_tables,
    access_acs.make_civ_emp_tables,
    access_acs.make_tenure_tables,
    access_acs.make_med_inc_tables,
    access_acs.make_basics_tables,
    access_acs.make_occupancy_tables,
]


@pytest.mark.parametrize("func", TABLE_FUNCS, ids=[f.__name__ for f in TABLE_FUNCS])
def test_ten_char_names_cover_predefined_tables(fake_download, func):
    tab = func(api_key="k")
    names = ten_char_names()

    too_long = [c for c in tab.columns if len(c) > 10 and c not in names]
    assert too_long == []

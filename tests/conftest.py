from types import SimpleNamespace

import geopandas as gpd
import pytest
from shapely.geometry import Point

import basket.access_acs as access_acs


@pytest.fixture(autouse=True)
def isolated_api_key(tmp_path, monkeypatch):
    """
    Keep tests away from the developer's real .env and CENSUS_API_KEY:
    run each test in an empty directory with the variable unset
    (and restored afterwards).
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("CENSUS_API_KEY", "placeholder")
    monkeypatch.delenv("CENSUS_API_KEY")


@pytest.fixture
def fake_download(monkeypatch):
    """
    Replace censusdis' download with a stub that records each call and returns
    a two-row GeoDataFrame shaped like the real response.

    Set ``fake_download.values[<census col>] = [row1, row2]`` to control the
    numbers returned for a column; unset columns default to [10.0, 20.0].
    """
    calls = []
    values = {}

    def _download(dataset, vintage, cols, **kwargs):
        calls.append({"dataset": dataset, "vintage": vintage, "cols": cols, **kwargs})
        data = {"STATE": ["25", "25"]}
        if "county" in kwargs:
            data["COUNTY"] = ["017", "025"]
        if "tract" in kwargs:
            data["TRACT"] = ["000100", "000200"]
        if "place" in kwargs:
            data["PLACE"] = ["07000", "37000"]
        for c in cols:
            if c == "NAME":
                data[c] = values.get(c, ["Area A", "Area B"])
            else:
                data[c] = values.get(c, [10.0, 20.0])
        return gpd.GeoDataFrame(
            data, geometry=[Point(0, 0), Point(1, 1)], crs="EPSG:4326"
        )

    monkeypatch.setattr(access_acs.ced, "download", _download)
    return SimpleNamespace(calls=calls, values=values)

import bascet
from bascet import access_acs, export_acs


def test_public_functions_importable_from_package():
    for name in bascet.__all__:
        assert hasattr(bascet, name), name


def test_package_exports_match_modules():
    assert bascet.make_race_tables is access_acs.make_race_tables
    assert bascet.acs2csv is export_acs.acs2csv


def test_version_is_set():
    assert bascet.__version__ != "unknown"

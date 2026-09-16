import censusdis.data as ced
import censusdis.maps as cem  # noqa
from censusdis.datasets import ACS5
from censusdis.states import ALL_STATES_AND_DC  # noqa
import pandas as pd
import geopandas as gpd
import os
from dotenv import load_dotenv

load_dotenv()
c = os.getenv("CENSUS_API_KEY")


def labels4acs(var: str, year: int) -> str:
    vars = ced.variables.search(
        ACS5, year, group_name=var.split("_")[0], name=var
    )
    label = vars.iloc[0]["LABEL"]
    label = label.split("!")
    for i in ["", "Estimate", "Total:", "Total"]:
        while i in label:
            label.remove(i)
    labstr = "_".join(label).replace(" ", "_")
    if len(labstr) == 0:
        labstr = var.split("_")[0] + "_Total_Universe"

    return labstr


def cid2desc(tab: pd.DataFrame | gpd.GeoDataFrame) -> dict[str, str]:
    renamers = {}
    for col in tab.columns:
        if "_" in col:
            renamers[col] = labels4acs(col, 2024)
    return renamers


def dwnld_acs5(
    cols: list[str],
    geo="tract",
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    vintage=2024,
    api_key=c,
):
    print(geo)
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
    return tab


def make_race_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
    bcn = {
        "B03002_001E": "RACE_TOTAL_POPULATION",
        "B03002_003E": "RACE_NOT_HISPANIC_WHITE_ALONE_POPULATION",
        "B03002_004E": "RACE_NOT_HISPANIC_BLACK_ALONE_POPULATION",
        "B03002_005E": "RACE_NOT_HISPANIC_AIAN_ALONE_POPULATION",
        "B03002_006E": "RACE_NOT_HISPANIC_ASIAN_ALONE_POPULATION",
        "B03002_007E": "RACE_NOT_HISPANIC_NHPI_ALONE_POPULATION",
        "B03002_008E": "RACE_NOT_HISPANIC_OTHERRACE_ALONE_POPULATION",
        "B03002_012E": "RACE_HISPANIC_TOTAL_POPULATION",
        "B03002_002E": "RACE_NOT_HISPANIC_TOTAL_POPULATION",
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
        rt["RACE_NOT_HISPANIC_WHITE_ALONE_POPULATION"]
        / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_not_hispanic_black_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_BLACK_ALONE_POPULATION"]
        / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_not_hispanic_aian_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_AIAN_ALONE_POPULATION"]
        / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_not_hispanic_asian_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_ASIAN_ALONE_POPULATION"]
        / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_not_hispanic_nhpi_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_NHPI_ALONE_POPULATION"]
        / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_not_hispanic_otherrace_alone_percent"] = round(
        rt["RACE_NOT_HISPANIC_OTHERRACE_ALONE_POPULATION"]
        / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_not_hispanic_percent"] = round(
        rt["RACE_NOT_HISPANIC_TOTAL_POPULATION"] / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_hispanic_percent"] = round(
        rt["RACE_HISPANIC_TOTAL_POPULATION"] / rt["RACE_TOTAL_POPULATION"],
        3,
    )
    rt["race_personofcolor_percent"] = round(
        1 - rt["race_not_hispanic_white_alone_percent"],
        3,
    )
    return rt[
        [
            "GEOID",
            "race_not_hispanic_white_alone_percent",
            "race_not_hispanic_black_alone_percent",
            "race_not_hispanic_aian_alone_percent",
            "race_not_hispanic_asian_alone_percent",
            "race_not_hispanic_nhpi_alone_percent",
            "race_not_hispanic_otherrace_alone_percent",
            "race_not_hispanic_percent",
            "race_hispanic_percent",
            "race_personofcolor_percent",
        ]
    ]


def make_pov_limit_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
    bcn = {
        "B06012_001E": "TOTAL_POPULATION_POVERTY",
        "B06012_002E": "POPULATION_BELOW_POVERTY_LIMIT",
        "B06012_003E": "POPULATION_BETWEEN_100-149_POVERTY_LIMIT",
        "B06012_004E": "POPULATION_ABOVE_150_POVERTY_LIMIT",
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
        plt["POPULATION_BELOW_POVERTY_LIMIT"]
        / plt["TOTAL_POPULATION_POVERTY"],
        3,
    )
    plt["federal_poverty_limit_between_100_149_percent"] = round(
        plt["POPULATION_BETWEEN_100-149_POVERTY_LIMIT"]
        / plt["TOTAL_POPULATION_POVERTY"],
        3,
    )
    plt["federal_poverty_limit_above_150_percent"] = round(
        plt["POPULATION_ABOVE_150_POVERTY_LIMIT"]
        / plt["TOTAL_POPULATION_POVERTY"],
        3,
    )
    return plt[
        [
            "GEOID",
            "federal_poverty_limit_below_allraces_percent",
            "federal_poverty_limit_between_100_149_percent",
            "federal_poverty_limit_above_150_percent",
        ]
    ]


def make_age_sex_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
    bcn = {
        "B01001_026E": "SEX_FEMALE_POPULATION",
        "B01001_001E": "SEX_AGE_TOTAL_POPULATION",
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
        ast["SEX_FEMALE_POPULATION"] / ast["SEX_AGE_TOTAL_POPULATION"],
        3,
    )

    ast["age_under_5_years_percent"] = round(
        (ast["AGE_UNDER_FIVE_FEMALE"] + ast["AGE_UNDER_FIVE_MALE"])
        / ast["SEX_AGE_TOTAL_POPULATION"],
        3,
    )

    ast["age_under_18_years_percent"] = round(
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
        / ast["SEX_AGE_TOTAL_POPULATION"],
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
        / ast["SEX_AGE_TOTAL_POPULATION"],
        3,
    )

    return ast[
        [
            "GEOID",
            "sex_female_percent",
            "age_under_5_years_percent",
            "age_under_18_years_percent",
            "age_over_64_percent",
        ]
    ]


def make_tenure_by_units_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
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

    tut["tenure_by_units_in_struct_occupied_housing_units"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS"],
        3,
    )

    tut["tenure_by_units_in_struct_occupied_housing_units_1_detached"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_1_DETACHED"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_1_DETACHED"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_1_attached"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_1_ATTACHED"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_1_ATTACHED"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_2"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_2"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_2"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_3_4"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_3_4"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_3_4"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_5_9"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_5_9"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_5_9"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_10_19"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_10_19"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_10_19"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_20_49"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_20_49"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_20_49"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_50_more"] = round(
        tut["TENURE_BY_U_IN_STRUCT_OO_HUS_50_MORE"]
        + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_50_MORE"],
        3,
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_mobile_home"] = (
        round(
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_MOBILEHOME"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_MOBILEHOME"],
            3,
        )
    )
    tut["tenure_by_units_in_struct_occupied_housing_units_boat_rv_van_etc"] = (
        round(
            tut["TENURE_BY_U_IN_STRUCT_OO_HUS_BOAT_RV_VAN_ETC"]
            + tut["TENURE_BY_U_IN_STRUCT_RO_HUS_BOAT_RV_VAN_ETC"],
            3,
        )
    )
    return tut[
        [
            "GEOID",
            "tenure_by_units_in_struct_occupied_housing_units",
            "tenure_by_units_in_struct_occupied_housing_units_1_detached",
            "tenure_by_units_in_struct_occupied_housing_units_1_attached",
            "tenure_by_units_in_struct_occupied_housing_units_2"
            "tenure_by_units_in_struct_occupied_housing_units_3_4",
            "tenure_by_units_in_struct_occupied_housing_units_5_9",
            "tenure_by_units_in_struct_occupied_housing_units_10_19",
            "tenure_by_units_in_struct_occupied_housing_units_20_49",
            "tenure_by_units_in_struct_occupied_housing_units_50_more",
            "tenure_by_units_in_struct_occupied_housing_units_mobile_home",
            "tenure_by_units_in_struct_occupied_housing_units_boat_rv_van_etc",
        ]
    ]


def make_year_built_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
    bcn = {
        "B25034_001E": "year_structure_built_total_struct",
        "B25034_002E": "year_structure_built_built_2020_later",
        "B25034_003E": "year_structure_built_built_2010_2019",
        "B25034_004E": "year_structure_built_built_2000_2009",
        "B25034_005E": "year_structure_built_built_1990_1999",
        "B25034_006E": "year_structure_built_built_1980_1989",
        "B25034_007E": "year_structure_built_built_1970_1979",
        "B25034_008E": "year_structure_built_built_1960_1969",
        "B25034_009E": "year_structure_built_built_1950_1959",
        "B25034_010E": "year_structure_built_built_1940_1949",
        "B25034_011E": "year_structure_built_built_pre_1940",
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

    ybt["year_structure_built_built_2020_later_percent"] = round(
        ybt["year_structure_built_built_2020_later"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_2010_2019_percent"] = round(
        ybt["year_structure_built_built_2010_2019_later"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_2000_2009_percent"] = round(
        ybt["year_structure_built_built_2000_2009"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_1990_1999_percent"] = round(
        ybt["year_structure_built_built_1990_1999"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_1980_1989_percent"] = round(
        ybt["year_structure_built_built_1980_1989"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_1970_1979_percent"] = round(
        ybt["year_structure_built_built_1970_1979"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_1960_1969_percent"] = round(
        ybt["year_structure_built_built_1960_1969"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_1950_1959_percent"] = round(
        ybt["year_structure_built_built_1950_1959"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_1940_1949_percent"] = round(
        ybt["year_structure_built_built_1940_1949"]
        / ybt["year_structure_built_total_struct"],
        3,
    )
    ybt["year_structure_built_built_pre_1940_percent"] = round(
        ybt["year_structure_built_built_pre_1940"]
        / ybt["year_structure_built_total_struct"],
        3,
    )

    return ybt[
        [
            "GEOID",
            "year_structure_built_built_2020_later_percent",
            "year_structure_built_built_2010_2019_percent",
            "year_structure_built_built_2000_2009_percent",
            "year_structure_built_built_1990_1999_percent",
            "year_structure_built_built_1980_1989_percent"
            "year_structure_built_built_1970_1979_percent"
            "year_structure_built_built_1960_1969_percent",
            "year_structure_built_built_1950_1959_percent",
            "year_structure_built_built_1940_1949_percent",
            "year_structure_built_built_pre_1940_percent",
            "year_structure_built_total_struct",
        ]
    ]


def make_civ_emp_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
    bcn = {
        "B23025_001E": "TOTAL_POPULATION_16P",
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
        cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE"] / cet["TOTAL_POPULATION_16P"],
        3,
    )
    cet["employment_civilian_labor_force_employed_percent"] = round(
        cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE_EMPLOYED"]
        / cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE"],
        3,
    )
    cet["employment_civilian_labor_force_unemployed_percent"] = round(
        cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE_UNEMPLOYED",]
        / cet["EMPLOYMENT_CIVILIAN_LABOR_FORCE"],
        3,
    )
    cet["employment_not_in_labor_force_percent"] = round(
        cet["NOT_IN_LABOR_FORCE"] / cet["TOTAL_POPULATION_16P"],
        3,
    )

    return cet[
        [
            "GEOID",
            "employment_civilian_labor_force_percent",
            "employment_civilian_labor_force_employed_percent",
            "employment_civilian_labor_force_unemployed_percent",
            "employment_not_in_labor_force_percent",
        ]
    ]


def make_tenure_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
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
        ten["tenure_tenter_occupied"] / ten["tenure_total_hh"], 3
    )

    return ten[
        [
            "GEOID",
            "tenure_owner_occupied_percent",
            "tenure_renter_occupied_percent",
            "tenure_total_hh",
        ]
    ]


def make_med_inc_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
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

    return mit[["GEOID", f"median_household_income_{vintage}$"]]


def make_basics_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
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
            "total_population_universe",
            "total_households_universe",
            "total_housing_units_universe",
        ]
    ]


def make_occupancy_tables(
    dataset=ACS5,
    state=ALL_STATES_AND_DC,
    county="*",
    geo="tract",
    vintage=2024,
    api_key=c,
):
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
            "total_housing_units_universe",
            "occupied_housing_units_percent",
            "vacant_housing_units_percent",
        ]
    ]

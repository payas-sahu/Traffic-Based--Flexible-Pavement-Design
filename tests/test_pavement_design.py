import pandas as pd
import pytest

from pavement_design import (
    select_catalogue_traffic_level,
    calculate_subgrade_modulus,
    get_verified_catalogue_case,
    create_catalogue_section_table,
    create_iitpave_structural_input,
    create_iitpave_load_input,
)


# ============================================================
# TEST 1: CATALOGUE TRAFFIC LEVEL SELECTION
# ============================================================

@pytest.mark.parametrize(
    "design_traffic_msa, expected_level",
    [
        (2.0, 5),
        (4.9, 5),
        (5.0, 5),
        (5.1, 10),
        (10.0, 10),
        (10.1, 20),
        (20.0, 20),
        (20.1, 30),
        (30.0, 30),
        (30.1, 40),
        (40.0, 40),
        (40.1, 50),
        (50.0, 50),
    ],
)
def test_catalogue_traffic_level_selection(
    design_traffic_msa,
    expected_level
):
    result = select_catalogue_traffic_level(
        design_traffic_msa
    )

    assert result == expected_level


# ============================================================
# TEST 2: TRAFFIC BELOW 2 MSA IS REJECTED
# ============================================================

def test_catalogue_rejects_traffic_below_2_msa():

    with pytest.raises(ValueError):

        select_catalogue_traffic_level(1.99)


# ============================================================
# TEST 3: TRAFFIC ABOVE 50 MSA IS REJECTED
# ============================================================

def test_catalogue_rejects_traffic_above_50_msa():

    with pytest.raises(ValueError):

        select_catalogue_traffic_level(50.01)


# ============================================================
# TEST 4: SUBGRADE MODULUS FOR CBR <= 5
# ============================================================

@pytest.mark.parametrize(
    "effective_cbr, expected_modulus",
    [
        (1, 10),
        (2, 20),
        (3, 30),
        (4, 40),
        (5, 50),
    ],
)
def test_subgrade_modulus_for_low_cbr(
    effective_cbr,
    expected_modulus
):
    result = calculate_subgrade_modulus(
        effective_cbr
    )

    assert result == pytest.approx(
        expected_modulus
    )


# ============================================================
# TEST 5: SUBGRADE MODULUS FOR CBR > 5
# ============================================================

def test_subgrade_modulus_for_cbr_10():

    expected_modulus = 17.6 * (10 ** 0.64)

    result = calculate_subgrade_modulus(10)

    assert result == pytest.approx(
        expected_modulus
    )


# ============================================================
# TEST 6: SUBGRADE MODULUS IS CAPPED AT 100 MPA
# ============================================================

def test_subgrade_modulus_is_capped_at_100_mpa():

    result = calculate_subgrade_modulus(100)

    assert result == pytest.approx(100)


# ============================================================
# TEST 7: NON-POSITIVE CBR IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "effective_cbr",
    [0, -1, -10],
)
def test_non_positive_cbr_is_rejected(
    effective_cbr
):

    with pytest.raises(ValueError):

        calculate_subgrade_modulus(
            effective_cbr
        )


# ============================================================
# TEST 8: VERIFIED CATALOGUE CASE LOOKUP
# ============================================================

def test_verified_catalogue_case_lookup():

    result = get_verified_catalogue_case(
        alternative_number=3,
        effective_cbr=10,
        catalogue_traffic_level=50
    )

    assert result["plate"] == "Plate-22"
    assert result["figure"] == "Figure 12.22"
    assert result["annex_table"] == "Table III.3"

    assert result["total_bituminous_mm"] == 100
    assert result["ctb_mm"] == 135
    assert result["ctsb_mm"] == 200


# ============================================================
# TEST 9: UNSUPPORTED CATALOGUE CASE IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "alternative_number, effective_cbr, traffic_level",
    [
        (1, 10, 50),
        (2, 10, 50),
        (4, 10, 50),
        (3, 5, 50),
        (3, 15, 50),
        (3, 10, 60),
    ],
)
def test_unsupported_catalogue_case_is_rejected(
    alternative_number,
    effective_cbr,
    traffic_level
):

    with pytest.raises(ValueError):

        get_verified_catalogue_case(
            alternative_number=
                alternative_number,
            effective_cbr=
                effective_cbr,
            catalogue_traffic_level=
                traffic_level
        )


# ============================================================
# TEST 10: CATALOGUE SECTION TABLE
# ============================================================

def test_catalogue_section_table():

    catalogue_case = get_verified_catalogue_case(
        alternative_number=3,
        effective_cbr=10,
        catalogue_traffic_level=50
    )

    result = create_catalogue_section_table(
        catalogue_case
    )

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 5

    assert result.iloc[0]["Layer"] == (
        "Total Bituminous Layer"
    )

    assert result.iloc[0]["Thickness_mm"] == 100

    sami_row = result[
        result["Layer"] == "SAMI"
    ].iloc[0]

    assert pd.isna(
        sami_row["Thickness_mm"]
    )

    subgrade_row = result[
        result["Layer"] == "Subgrade"
    ].iloc[0]

    assert (
        subgrade_row["Thickness_mm"]
        == "Semi-Infinite"
    )


# ============================================================
# TEST 11: IITPAVE STRUCTURAL INPUT TABLE
# ============================================================

def test_iitpave_structural_input_table():

    catalogue_case = get_verified_catalogue_case(
        alternative_number=3,
        effective_cbr=10,
        catalogue_traffic_level=50
    )

    subgrade_modulus = (
        calculate_subgrade_modulus(10)
    )

    result = create_iitpave_structural_input(
        catalogue_case=catalogue_case,
        subgrade_modulus=subgrade_modulus
    )

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 4

    assert "SAMI" not in result[
        "Layer_Name"
    ].tolist()

    assert result.iloc[0][
        "Layer_Name"
    ] == "Total Bituminous Layer"

    assert result.iloc[0][
        "Thickness_mm"
    ] == 100

    assert result.iloc[1][
        "Layer_Name"
    ] == "Cement Treated Base (CTB)"

    assert result.iloc[1][
        "Thickness_mm"
    ] == 135

    assert result.iloc[2][
        "Layer_Name"
    ] == "Cement Treated Sub-base (CTSB)"

    assert result.iloc[2][
        "Thickness_mm"
    ] == 200

    assert result.iloc[3][
        "Layer_Name"
    ] == "Subgrade"

    assert result.iloc[3][
        "Elastic_or_Resilient_Modulus_MPa"
    ] == pytest.approx(
        subgrade_modulus
    )


# ============================================================
# TEST 12: IITPAVE LOAD INPUT TABLE
# ============================================================

def test_iitpave_load_input_table():

    result = create_iitpave_load_input()

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 4

    standard_axle_row = result[
        result["Input_Parameter"]
        == "Standard Axle Load"
    ].iloc[0]

    assert standard_axle_row["Value"] == 80
    assert standard_axle_row["Unit"] == "kN"

    wheels_row = result[
        result["Input_Parameter"]
        == "Number of Wheels"
    ].iloc[0]

    assert wheels_row["Value"] == 4

    load_per_wheel_row = result[
        result["Input_Parameter"]
        == "Load per Wheel"
    ].iloc[0]

    assert load_per_wheel_row["Value"] == 20

    pressure_row = result[
        result["Input_Parameter"]
        == "Tyre Contact Pressure"
    ].iloc[0]

    assert pressure_row["Value"] == pytest.approx(
        0.56
    )

    assert pressure_row["Unit"] == "MPa"
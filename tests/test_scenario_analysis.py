import pandas as pd
import pytest

from scenario_analysis import (
    validate_scenario_inputs,
    analyze_scenario,
    compare_scenarios,
    create_compact_comparison_table,
    create_scenario_summary,
)


AVERAGE_CVPD = 2355.14


BASELINE_SCENARIO = {
    "scenario_name": "Baseline",
    "growth_rate": 0.05,
    "design_period": 20,
    "years_to_completion": 0.0,
    "vdf": 3.0,
    "distribution_factor": 0.50
}


HIGHER_GROWTH_SCENARIO = {
    "scenario_name": "Higher Growth",
    "growth_rate": 0.07,
    "design_period": 20,
    "years_to_completion": 0.0,
    "vdf": 3.0,
    "distribution_factor": 0.50
}


HIGHER_VDF_SCENARIO = {
    "scenario_name": "Higher VDF",
    "growth_rate": 0.05,
    "design_period": 20,
    "years_to_completion": 0.0,
    "vdf": 4.0,
    "distribution_factor": 0.50
}


# ============================================================
# TEST 1: VALID SCENARIO INPUTS
# ============================================================

def test_valid_scenario_inputs():

    result = validate_scenario_inputs(
        scenario_name="Baseline",
        average_cvpd=AVERAGE_CVPD,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0,
        vdf=3.0,
        distribution_factor=0.50
    )

    assert result is None


# ============================================================
# TEST 2: EMPTY SCENARIO NAME IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "scenario_name",
    ["", "   "]
)
def test_empty_scenario_name_is_rejected(
    scenario_name
):

    with pytest.raises(
        ValueError,
        match="Scenario name cannot be empty"
    ):

        validate_scenario_inputs(
            scenario_name=scenario_name,
            average_cvpd=AVERAGE_CVPD,
            growth_rate=0.05,
            design_period=20,
            years_to_completion=0,
            vdf=3.0,
            distribution_factor=0.50
        )


# ============================================================
# TEST 3: NON-POSITIVE TRAFFIC IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "average_cvpd",
    [0, -1, -100]
)
def test_non_positive_average_cvpd_is_rejected(
    average_cvpd
):

    with pytest.raises(ValueError):

        validate_scenario_inputs(
            scenario_name="Test",
            average_cvpd=average_cvpd,
            growth_rate=0.05,
            design_period=20,
            years_to_completion=0,
            vdf=3.0,
            distribution_factor=0.50
        )


# ============================================================
# TEST 4: NEGATIVE GROWTH RATE IS REJECTED
# ============================================================

def test_negative_growth_rate_is_rejected():

    with pytest.raises(ValueError):

        validate_scenario_inputs(
            scenario_name="Test",
            average_cvpd=AVERAGE_CVPD,
            growth_rate=-0.01,
            design_period=20,
            years_to_completion=0,
            vdf=3.0,
            distribution_factor=0.50
        )


# ============================================================
# TEST 5: NON-POSITIVE DESIGN PERIOD IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "design_period",
    [0, -1, -20]
)
def test_non_positive_design_period_is_rejected(
    design_period
):

    with pytest.raises(ValueError):

        validate_scenario_inputs(
            scenario_name="Test",
            average_cvpd=AVERAGE_CVPD,
            growth_rate=0.05,
            design_period=design_period,
            years_to_completion=0,
            vdf=3.0,
            distribution_factor=0.50
        )


# ============================================================
# TEST 6: NEGATIVE OPENING DELAY IS REJECTED
# ============================================================

def test_negative_opening_delay_is_rejected():

    with pytest.raises(ValueError):

        validate_scenario_inputs(
            scenario_name="Test",
            average_cvpd=AVERAGE_CVPD,
            growth_rate=0.05,
            design_period=20,
            years_to_completion=-1,
            vdf=3.0,
            distribution_factor=0.50
        )


# ============================================================
# TEST 7: NON-POSITIVE VDF IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "vdf",
    [0, -1, -5]
)
def test_non_positive_vdf_is_rejected(vdf):

    with pytest.raises(ValueError):

        validate_scenario_inputs(
            scenario_name="Test",
            average_cvpd=AVERAGE_CVPD,
            growth_rate=0.05,
            design_period=20,
            years_to_completion=0,
            vdf=vdf,
            distribution_factor=0.50
        )


# ============================================================
# TEST 8: INVALID DISTRIBUTION FACTOR IS REJECTED
# ============================================================

@pytest.mark.parametrize(
    "distribution_factor",
    [0, -0.1, 1.01, 2.0]
)
def test_invalid_distribution_factor_is_rejected(
    distribution_factor
):

    with pytest.raises(ValueError):

        validate_scenario_inputs(
            scenario_name="Test",
            average_cvpd=AVERAGE_CVPD,
            growth_rate=0.05,
            design_period=20,
            years_to_completion=0,
            vdf=3.0,
            distribution_factor=distribution_factor
        )


# ============================================================
# TEST 9: ANALYZE BASELINE SCENARIO
# ============================================================

def test_analyze_baseline_scenario():

    result = analyze_scenario(
        scenario_name="  Baseline  ",
        average_cvpd=AVERAGE_CVPD,
        growth_rate=0.05,
        design_period=20,
        years_to_completion=0.0,
        vdf=3.0,
        distribution_factor=0.50
    )

    assert isinstance(result, dict)

    assert result["Scenario"] == "Baseline"

    assert result[
        "Design_Traffic_MSA"
    ] == pytest.approx(
        42.64,
        abs=0.02
    )

    assert result[
        "Catalogue_Status"
    ] == "Verified catalogue case available"

    assert result[
        "Catalogue_Traffic_Level_MSA"
    ] == 50

    assert result[
        "Effective_CBR_Percent"
    ] == 10

    assert result["Total_Bituminous_mm"] == 100
    assert result["CTB_mm"] == 135
    assert result["CTSB_mm"] == 200

    assert result["IRC_Figure"] == "Figure 12.22"
    assert result["IRC_Plate"] == "Plate-22"
    assert result["IRC_Annex_Table"] == "Table III.3"


# ============================================================
# TEST 10: UNSUPPORTED HIGH-TRAFFIC SCENARIO
# ============================================================

def test_unsupported_high_traffic_scenario():

    result = analyze_scenario(
        scenario_name="High Traffic",
        average_cvpd=AVERAGE_CVPD,
        growth_rate=0.10,
        design_period=30,
        years_to_completion=0.0,
        vdf=5.0,
        distribution_factor=0.75
    )

    assert result["Design_Traffic_MSA"] > 50

    assert (
        "exceeds 50 MSA"
        in result["Catalogue_Status"]
    )

    assert result[
        "Catalogue_Traffic_Level_MSA"
    ] is None

    assert result["Total_Bituminous_mm"] is None


# ============================================================
# TEST 11: UNSUPPORTED LOW-TRAFFIC SCENARIO
# ============================================================

def test_unsupported_low_traffic_scenario():

    result = analyze_scenario(
        scenario_name="Low Traffic",
        average_cvpd=100,
        growth_rate=0.0,
        design_period=5,
        years_to_completion=0.0,
        vdf=1.0,
        distribution_factor=0.50
    )

    assert result["Design_Traffic_MSA"] < 2

    assert (
        "below 2 MSA"
        in result["Catalogue_Status"]
    )

    assert result[
        "Catalogue_Traffic_Level_MSA"
    ] is None


# ============================================================
# TEST 12: EMPTY SCENARIO LIST IS REJECTED
# ============================================================

def test_empty_scenario_list_is_rejected():

    with pytest.raises(
        ValueError,
        match="At least one scenario is required"
    ):

        compare_scenarios(
            scenarios=[],
            average_cvpd=AVERAGE_CVPD
        )


# ============================================================
# TEST 13: DUPLICATE SCENARIO NAMES ARE REJECTED
# ============================================================

def test_duplicate_scenario_names_are_rejected():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        BASELINE_SCENARIO.copy()
    ]

    with pytest.raises(
        ValueError,
        match="Scenario names must be unique"
    ):

        compare_scenarios(
            scenarios=scenarios,
            average_cvpd=AVERAGE_CVPD
        )


# ============================================================
# TEST 14: MISSING BASELINE IS REJECTED
# ============================================================

def test_missing_baseline_scenario_is_rejected():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy()
    ]

    with pytest.raises(
        ValueError,
        match="was not found"
    ):

        compare_scenarios(
            scenarios=scenarios,
            average_cvpd=AVERAGE_CVPD,
            baseline_scenario_name="Missing Scenario"
        )


# ============================================================
# TEST 15: FIRST SCENARIO BECOMES DEFAULT BASELINE
# ============================================================

def test_first_scenario_is_default_baseline():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy()
    ]

    result = compare_scenarios(
        scenarios=scenarios,
        average_cvpd=AVERAGE_CVPD
    )

    baseline_rows = result[
        result["Is_Baseline"]
    ]

    assert len(baseline_rows) == 1

    assert baseline_rows.iloc[0][
        "Scenario"
    ] == "Baseline"


# ============================================================
# TEST 16: SCENARIO COMPARISON OUTPUT
# ============================================================

def test_compare_scenarios_output():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy(),
        HIGHER_VDF_SCENARIO.copy()
    ]

    result = compare_scenarios(
        scenarios=scenarios,
        average_cvpd=AVERAGE_CVPD,
        baseline_scenario_name="Baseline"
    )

    assert isinstance(result, pd.DataFrame)

    assert len(result) == 3

    assert result["Is_Baseline"].sum() == 1

    baseline_row = result[
        result["Is_Baseline"]
    ].iloc[0]

    assert baseline_row[
        "MSA_Change_From_Baseline"
    ] == pytest.approx(0.0)

    assert baseline_row[
        "Percent_Change_From_Baseline"
    ] == pytest.approx(0.0)

    assert baseline_row[
        "MSA_Ratio_To_Baseline"
    ] == pytest.approx(1.0)


# ============================================================
# TEST 17: HIGHER INPUTS INCREASE DESIGN TRAFFIC
# ============================================================

def test_higher_scenarios_increase_design_traffic():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy(),
        HIGHER_VDF_SCENARIO.copy()
    ]

    result = compare_scenarios(
        scenarios=scenarios,
        average_cvpd=AVERAGE_CVPD,
        baseline_scenario_name="Baseline"
    )

    baseline_msa = result.loc[
        result["Scenario"] == "Baseline",
        "Design_Traffic_MSA"
    ].iloc[0]

    higher_growth_msa = result.loc[
        result["Scenario"] == "Higher Growth",
        "Design_Traffic_MSA"
    ].iloc[0]

    higher_vdf_msa = result.loc[
        result["Scenario"] == "Higher VDF",
        "Design_Traffic_MSA"
    ].iloc[0]

    assert higher_growth_msa > baseline_msa
    assert higher_vdf_msa > baseline_msa


# ============================================================
# TEST 18: TRAFFIC RANKING
# ============================================================

def test_traffic_ranking():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy(),
        HIGHER_VDF_SCENARIO.copy()
    ]

    result = compare_scenarios(
        scenarios=scenarios,
        average_cvpd=AVERAGE_CVPD,
        baseline_scenario_name="Baseline"
    )

    highest_msa = result[
        "Design_Traffic_MSA"
    ].max()

    highest_row = result[
        result["Design_Traffic_MSA"] == highest_msa
    ].iloc[0]

    assert highest_row["Traffic_Rank"] == 1


# ============================================================
# TEST 19: COMPACT COMPARISON TABLE
# ============================================================

def test_compact_comparison_table():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy()
    ]

    comparison = compare_scenarios(
        scenarios=scenarios,
        average_cvpd=AVERAGE_CVPD,
        baseline_scenario_name="Baseline"
    )

    result = create_compact_comparison_table(
        comparison
    )

    expected_columns = [
        "Scenario",
        "Growth_Rate_Percent",
        "Design_Period_Years",
        "Years_To_Opening",
        "VDF",
        "Distribution_Factor",
        "Design_Traffic_MSA",
        "MSA_Change_From_Baseline",
        "Percent_Change_From_Baseline",
        "Catalogue_Traffic_Level_MSA",
        "Total_Bituminous_mm",
        "CTB_mm",
        "CTSB_mm",
        "Traffic_Rank",
        "Is_Baseline"
    ]

    assert isinstance(result, pd.DataFrame)

    assert result.columns.tolist() == expected_columns

    assert len(result) == len(comparison)


# ============================================================
# TEST 20: SCENARIO SUMMARY
# ============================================================

def test_scenario_summary():

    scenarios = [
        BASELINE_SCENARIO.copy(),
        HIGHER_GROWTH_SCENARIO.copy(),
        HIGHER_VDF_SCENARIO.copy()
    ]

    comparison = compare_scenarios(
        scenarios=scenarios,
        average_cvpd=AVERAGE_CVPD,
        baseline_scenario_name="Baseline"
    )

    summary = create_scenario_summary(
        comparison
    )

    assert isinstance(summary, dict)

    assert summary["number_of_scenarios"] == 3

    assert summary["baseline_scenario"] == "Baseline"

    assert summary[
        "baseline_msa"
    ] == pytest.approx(
        42.64,
        abs=0.02
    )

    assert summary[
        "highest_design_traffic_msa"
    ] >= summary[
        "lowest_design_traffic_msa"
    ]

    assert summary[
        "design_traffic_range_msa"
    ] == pytest.approx(
        summary["highest_design_traffic_msa"]
        - summary["lowest_design_traffic_msa"]
    )

    assert (
        summary["verified_catalogue_cases"]
        + summary["unsupported_catalogue_cases"]
        == summary["number_of_scenarios"]
    )
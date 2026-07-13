import pandas as pd
import pytest

from sensitivity_analysis import (
    calculate_baseline,
    create_scenario_values,
    analyze_growth_rate,
    analyze_vdf,
    analyze_design_period,
    analyze_construction_delay,
    run_sensitivity_analysis,
    calculate_parameter_influence,
)


AVERAGE_CVPD = 2355.14
GROWTH_RATE = 0.05
DESIGN_PERIOD = 20
YEARS_TO_COMPLETION = 0.0
VDF = 3.0
DISTRIBUTION_FACTOR = 0.50


# ============================================================
# TEST 1: BASELINE CALCULATION
# ============================================================

def test_calculate_baseline():

    result = calculate_baseline(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    assert isinstance(result, dict)

    assert result["design_traffic_msa"] == pytest.approx(
        42.64,
        abs=0.02
    )


# ============================================================
# TEST 2: SCENARIO VALUES INCLUDE BASELINE
# ============================================================

def test_create_scenario_values_includes_baseline():

    values = create_scenario_values(
        baseline=5.5,
        minimum=2.0,
        maximum=10.0,
        step=1.0,
        decimals=2
    )

    assert 5.5 in values

    assert values == sorted(values)

    assert len(values) == len(set(values))


# ============================================================
# TEST 3: DUPLICATE BASELINE IS NOT ADDED
# ============================================================

def test_create_scenario_values_no_duplicate_baseline():

    values = create_scenario_values(
        baseline=5.0,
        minimum=2.0,
        maximum=10.0,
        step=1.0,
        decimals=2
    )

    assert values.count(5.0) == 1


# ============================================================
# TEST 4: GROWTH RATE SENSITIVITY OUTPUT
# ============================================================

def test_growth_rate_sensitivity():

    result = analyze_growth_rate(
        average_cvpd=AVERAGE_CVPD,
        baseline_growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    assert isinstance(result, pd.DataFrame)

    assert set(result.columns) == {
        "Growth_Rate_Percent",
        "Design_Traffic_MSA",
        "Is_Baseline"
    }

    assert result["Is_Baseline"].sum() == 1

    baseline_row = result[
        result["Is_Baseline"]
    ].iloc[0]

    assert baseline_row[
        "Growth_Rate_Percent"
    ] == pytest.approx(5.0)

    assert baseline_row[
        "Design_Traffic_MSA"
    ] == pytest.approx(
        42.64,
        abs=0.02
    )


# ============================================================
# TEST 5: DESIGN TRAFFIC INCREASES WITH GROWTH RATE
# ============================================================

def test_design_traffic_increases_with_growth_rate():

    result = analyze_growth_rate(
        average_cvpd=AVERAGE_CVPD,
        baseline_growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    sorted_result = result.sort_values(
        "Growth_Rate_Percent"
    )

    msa_values = sorted_result[
        "Design_Traffic_MSA"
    ].tolist()

    assert all(
        later > earlier
        for earlier, later in zip(
            msa_values,
            msa_values[1:]
        )
    )


# ============================================================
# TEST 6: VDF SENSITIVITY OUTPUT
# ============================================================

def test_vdf_sensitivity():

    result = analyze_vdf(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        baseline_vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    assert isinstance(result, pd.DataFrame)

    assert set(result.columns) == {
        "VDF",
        "Design_Traffic_MSA",
        "Is_Baseline"
    }

    assert result["Is_Baseline"].sum() == 1

    baseline_row = result[
        result["Is_Baseline"]
    ].iloc[0]

    assert baseline_row["VDF"] == pytest.approx(3.0)

    assert baseline_row[
        "Design_Traffic_MSA"
    ] == pytest.approx(
        42.64,
        abs=0.02
    )


# ============================================================
# TEST 7: DESIGN TRAFFIC INCREASES WITH VDF
# ============================================================

def test_design_traffic_increases_with_vdf():

    result = analyze_vdf(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        baseline_vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    sorted_result = result.sort_values("VDF")

    msa_values = sorted_result[
        "Design_Traffic_MSA"
    ].tolist()

    assert all(
        later > earlier
        for earlier, later in zip(
            msa_values,
            msa_values[1:]
        )
    )


# ============================================================
# TEST 8: DESIGN PERIOD SENSITIVITY OUTPUT
# ============================================================

def test_design_period_sensitivity():

    result = analyze_design_period(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        baseline_design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    assert isinstance(result, pd.DataFrame)

    assert set(result.columns) == {
        "Design_Period_Years",
        "Design_Traffic_MSA",
        "Is_Baseline"
    }

    assert result["Is_Baseline"].sum() == 1

    baseline_row = result[
        result["Is_Baseline"]
    ].iloc[0]

    assert baseline_row[
        "Design_Period_Years"
    ] == 20

    assert baseline_row[
        "Design_Traffic_MSA"
    ] == pytest.approx(
        42.64,
        abs=0.02
    )


# ============================================================
# TEST 9: DESIGN TRAFFIC INCREASES WITH DESIGN PERIOD
# ============================================================

def test_design_traffic_increases_with_design_period():

    result = analyze_design_period(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        baseline_design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    sorted_result = result.sort_values(
        "Design_Period_Years"
    )

    msa_values = sorted_result[
        "Design_Traffic_MSA"
    ].tolist()

    assert all(
        later > earlier
        for earlier, later in zip(
            msa_values,
            msa_values[1:]
        )
    )


# ============================================================
# TEST 10: CONSTRUCTION DELAY SENSITIVITY OUTPUT
# ============================================================

def test_construction_delay_sensitivity():

    result = analyze_construction_delay(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        baseline_years_to_completion=
            YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    assert isinstance(result, pd.DataFrame)

    assert set(result.columns) == {
        "Years_To_Completion",
        "Design_Traffic_MSA",
        "Is_Baseline"
    }

    assert result["Is_Baseline"].sum() == 1

    baseline_row = result[
        result["Is_Baseline"]
    ].iloc[0]

    assert baseline_row[
        "Years_To_Completion"
    ] == pytest.approx(0.0)

    assert baseline_row[
        "Design_Traffic_MSA"
    ] == pytest.approx(
        42.64,
        abs=0.02
    )


# ============================================================
# TEST 11: DELAY INCREASES DESIGN TRAFFIC
# ============================================================

def test_design_traffic_increases_with_delay():

    result = analyze_construction_delay(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        baseline_years_to_completion=
            YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    sorted_result = result.sort_values(
        "Years_To_Completion"
    )

    msa_values = sorted_result[
        "Design_Traffic_MSA"
    ].tolist()

    assert all(
        later > earlier
        for earlier, later in zip(
            msa_values,
            msa_values[1:]
        )
    )


# ============================================================
# TEST 12: COMPLETE SENSITIVITY ANALYSIS OUTPUT
# ============================================================

def test_run_sensitivity_analysis():

    results = run_sensitivity_analysis(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    assert set(results.keys()) == {
        "baseline",
        "growth_rate",
        "vdf",
        "design_period",
        "construction_delay"
    }

    assert isinstance(
        results["baseline"],
        dict
    )

    assert isinstance(
        results["growth_rate"],
        pd.DataFrame
    )

    assert isinstance(
        results["vdf"],
        pd.DataFrame
    )

    assert isinstance(
        results["design_period"],
        pd.DataFrame
    )

    assert isinstance(
        results["construction_delay"],
        pd.DataFrame
    )


# ============================================================
# TEST 13: ALL SENSITIVITY TABLES CONTAIN ONE BASELINE
# ============================================================

def test_all_sensitivity_tables_have_one_baseline():

    results = run_sensitivity_analysis(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    sensitivity_tables = [
        results["growth_rate"],
        results["vdf"],
        results["design_period"],
        results["construction_delay"]
    ]

    for dataframe in sensitivity_tables:

        assert dataframe[
            "Is_Baseline"
        ].sum() == 1


# ============================================================
# TEST 14: PARAMETER INFLUENCE OUTPUT
# ============================================================

def test_parameter_influence_output():

    results = run_sensitivity_analysis(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    influence = calculate_parameter_influence(
        results
    )

    assert isinstance(influence, pd.DataFrame)

    assert len(influence) == 4

    assert set(influence["Parameter"]) == {
        "Growth Rate",
        "VDF",
        "Design Period",
        "Construction Delay"
    }

    assert influence[
        "Influence_Rank"
    ].tolist() == [1, 2, 3, 4]


# ============================================================
# TEST 15: INFLUENCE RANKING IS DESCENDING
# ============================================================

def test_influence_ranking_is_descending():

    results = run_sensitivity_analysis(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    influence = calculate_parameter_influence(
        results
    )

    percentage_ranges = influence[
        "Percentage_Range_of_Baseline"
    ].tolist()

    assert percentage_ranges == sorted(
        percentage_ranges,
        reverse=True
    )


# ============================================================
# TEST 16: INFLUENCE VALUES ARE CONSISTENT
# ============================================================

def test_parameter_influence_values_are_consistent():

    results = run_sensitivity_analysis(
        average_cvpd=AVERAGE_CVPD,
        growth_rate=GROWTH_RATE,
        design_period=DESIGN_PERIOD,
        years_to_completion=YEARS_TO_COMPLETION,
        vdf=VDF,
        distribution_factor=DISTRIBUTION_FACTOR
    )

    influence = calculate_parameter_influence(
        results
    )

    baseline_msa = results[
        "baseline"
    ]["design_traffic_msa"]

    for _, row in influence.iterrows():

        expected_range = (
            row["Maximum_MSA"]
            - row["Minimum_MSA"]
        )

        expected_percentage = (
            expected_range
            / baseline_msa
            * 100
        )

        assert row[
            "MSA_Range"
        ] == pytest.approx(
            expected_range
        )

        assert row[
            "Percentage_Range_of_Baseline"
        ] == pytest.approx(
            expected_percentage
        )
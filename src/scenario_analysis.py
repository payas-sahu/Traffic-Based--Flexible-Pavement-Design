import pandas as pd

from design_traffic import calculate_design_traffic

from pavement_design import (
    select_catalogue_traffic_level,
    calculate_subgrade_modulus,
    get_verified_catalogue_case
)


SUPPORTED_ALTERNATIVE_NUMBER = 3
SUPPORTED_EFFECTIVE_CBR = 10


# ============================================================
# 1. VALIDATE SCENARIO INPUTS
# ============================================================

def validate_scenario_inputs(
    scenario_name,
    average_cvpd,
    growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):

    if not str(scenario_name).strip():
        raise ValueError(
            "Scenario name cannot be empty."
        )

    if average_cvpd <= 0:
        raise ValueError(
            "Average commercial traffic must be greater than zero."
        )

    if growth_rate < 0:
        raise ValueError(
            "Traffic growth rate cannot be negative."
        )

    if design_period <= 0:
        raise ValueError(
            "Design period must be greater than zero."
        )

    if years_to_completion < 0:
        raise ValueError(
            "Years to road opening cannot be negative."
        )

    if vdf <= 0:
        raise ValueError(
            "VDF must be greater than zero."
        )

    if not 0 < distribution_factor <= 1:
        raise ValueError(
            "Distribution factor must be greater than 0 "
            "and less than or equal to 1."
        )


# ============================================================
# 2. ANALYZE ONE SCENARIO
# ============================================================

def analyze_scenario(
    scenario_name,
    average_cvpd,
    growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):
    """
    Calculate design traffic and, when applicable, perform
    verified IRC catalogue screening for one scenario.
    """

    validate_scenario_inputs(
        scenario_name=scenario_name,
        average_cvpd=average_cvpd,
        growth_rate=growth_rate,
        design_period=design_period,
        years_to_completion=years_to_completion,
        vdf=vdf,
        distribution_factor=distribution_factor
    )

    design_results = calculate_design_traffic(
        traffic_at_last_count=average_cvpd,
        growth_rate=growth_rate,
        design_period=int(design_period),
        years_to_completion=years_to_completion,
        vdf=vdf,
        distribution_factor=distribution_factor
    )

    design_traffic_msa = design_results["design_traffic_msa"]

    result = {
        "Scenario": str(scenario_name).strip(),
        "Average_CVPD": average_cvpd,
        "Growth_Rate_Percent": growth_rate * 100,
        "Design_Period_Years": int(design_period),
        "Years_To_Opening": years_to_completion,
        "VDF": vdf,
        "Distribution_Factor": distribution_factor,
        "Opening_Traffic_CVPD": design_results["opening_traffic"],
        "Growth_Factor": design_results["growth_factor"],
        "Design_Traffic_MSA": design_traffic_msa,
        "Catalogue_Status": None,
        "Catalogue_Traffic_Level_MSA": None,
        "Effective_CBR_Percent": None,
        "Subgrade_Modulus_MPa": None,
        "Total_Bituminous_mm": None,
        "CTB_mm": None,
        "CTSB_mm": None,
        "IRC_Figure": None,
        "IRC_Plate": None,
        "IRC_Annex_Table": None
    }

    # ========================================================
    # CATALOGUE SCREENING
    # ========================================================

    try:

        catalogue_traffic_level = (
            select_catalogue_traffic_level(
                design_traffic_msa
            )
        )

        catalogue_case = get_verified_catalogue_case(
            alternative_number=SUPPORTED_ALTERNATIVE_NUMBER,
            effective_cbr=SUPPORTED_EFFECTIVE_CBR,
            catalogue_traffic_level=catalogue_traffic_level
        )

        subgrade_modulus = calculate_subgrade_modulus(
            SUPPORTED_EFFECTIVE_CBR
        )

        result.update(
            {
                "Catalogue_Status":
                    "Verified catalogue case available",

                "Catalogue_Traffic_Level_MSA":
                    catalogue_traffic_level,

                "Effective_CBR_Percent":
                    SUPPORTED_EFFECTIVE_CBR,

                "Subgrade_Modulus_MPa":
                    subgrade_modulus,

                "Total_Bituminous_mm":
                    catalogue_case["total_bituminous_mm"],

                "CTB_mm":
                    catalogue_case["ctb_mm"],

                "CTSB_mm":
                    catalogue_case["ctsb_mm"],

                "IRC_Figure":
                    catalogue_case["figure"],

                "IRC_Plate":
                    catalogue_case["plate"],

                "IRC_Annex_Table":
                    catalogue_case["annex_table"]
            }
        )

    except ValueError as error:

        result["Catalogue_Status"] = str(error)

    return result


# ============================================================
# 3. COMPARE MULTIPLE SCENARIOS
# ============================================================

def compare_scenarios(
    scenarios,
    average_cvpd,
    baseline_scenario_name=None
):
    """
    Analyze multiple scenarios and return a comparison DataFrame.

    Each item in scenarios must contain:
        scenario_name
        growth_rate
        design_period
        years_to_completion
        vdf
        distribution_factor
    """

    if not scenarios:
        raise ValueError(
            "At least one scenario is required."
        )

    scenario_names = [
        str(scenario["scenario_name"]).strip()
        for scenario in scenarios
    ]

    if len(scenario_names) != len(set(scenario_names)):
        raise ValueError(
            "Scenario names must be unique."
        )

    records = []

    for scenario in scenarios:

        result = analyze_scenario(
            scenario_name=scenario["scenario_name"],
            average_cvpd=average_cvpd,
            growth_rate=scenario["growth_rate"],
            design_period=scenario["design_period"],
            years_to_completion=scenario["years_to_completion"],
            vdf=scenario["vdf"],
            distribution_factor=scenario["distribution_factor"]
        )

        records.append(result)

    comparison_df = pd.DataFrame(records)

    # ========================================================
    # BASELINE SELECTION
    # ========================================================

    if baseline_scenario_name is None:
        baseline_scenario_name = comparison_df.iloc[0]["Scenario"]

    baseline_rows = comparison_df[
        comparison_df["Scenario"] == baseline_scenario_name
    ]

    if baseline_rows.empty:
        raise ValueError(
            f"Baseline scenario '{baseline_scenario_name}' "
            "was not found."
        )

    baseline_msa = baseline_rows.iloc[0]["Design_Traffic_MSA"]

    if baseline_msa <= 0:
        raise ValueError(
            "Baseline design traffic must be greater than zero."
        )

    # ========================================================
    # COMPARISON METRICS
    # ========================================================

    comparison_df["MSA_Change_From_Baseline"] = (
        comparison_df["Design_Traffic_MSA"]
        - baseline_msa
    )

    comparison_df["Percent_Change_From_Baseline"] = (
        comparison_df["MSA_Change_From_Baseline"]
        / baseline_msa
        * 100
    )

    comparison_df["MSA_Ratio_To_Baseline"] = (
        comparison_df["Design_Traffic_MSA"]
        / baseline_msa
    )

    comparison_df["Is_Baseline"] = (
        comparison_df["Scenario"]
        == baseline_scenario_name
    )

    # ========================================================
    # RANK SCENARIOS BY DESIGN TRAFFIC
    # ========================================================

    comparison_df["Traffic_Rank"] = (
        comparison_df["Design_Traffic_MSA"]
        .rank(
            method="dense",
            ascending=False
        )
        .astype(int)
    )

    return comparison_df


# ============================================================
# 4. CREATE COMPACT COMPARISON TABLE
# ============================================================

def create_compact_comparison_table(comparison_df):
    """
    Return the most useful scenario-comparison columns for
    dashboard display.
    """

    columns = [
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

    return comparison_df[columns].copy()


# ============================================================
# 5. CREATE ENGINEERING SUMMARY
# ============================================================

def create_scenario_summary(comparison_df):
    """
    Create a summary dictionary for dashboard interpretation.
    """

    highest_traffic_row = (
        comparison_df
        .sort_values(
            "Design_Traffic_MSA",
            ascending=False
        )
        .iloc[0]
    )

    lowest_traffic_row = (
        comparison_df
        .sort_values(
            "Design_Traffic_MSA",
            ascending=True
        )
        .iloc[0]
    )

    baseline_row = (
        comparison_df[
            comparison_df["Is_Baseline"]
        ]
        .iloc[0]
    )

    verified_cases = (
        comparison_df[
            comparison_df[
                "Catalogue_Traffic_Level_MSA"
            ].notna()
        ]
    )

    return {
        "number_of_scenarios":
            len(comparison_df),

        "baseline_scenario":
            baseline_row["Scenario"],

        "baseline_msa":
            baseline_row["Design_Traffic_MSA"],

        "highest_traffic_scenario":
            highest_traffic_row["Scenario"],

        "highest_design_traffic_msa":
            highest_traffic_row["Design_Traffic_MSA"],

        "lowest_traffic_scenario":
            lowest_traffic_row["Scenario"],

        "lowest_design_traffic_msa":
            lowest_traffic_row["Design_Traffic_MSA"],

        "design_traffic_range_msa":
            (
                highest_traffic_row["Design_Traffic_MSA"]
                - lowest_traffic_row["Design_Traffic_MSA"]
            ),

        "verified_catalogue_cases":
            len(verified_cases),

        "unsupported_catalogue_cases":
            len(comparison_df) - len(verified_cases)
    }


# ============================================================
# 6. TEST MODULE
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("SCENARIO COMPARISON MODULE TEST")
    print("=" * 70)

    TEST_AVERAGE_CVPD = 2355.14

    test_scenarios = [

        {
            "scenario_name": "Baseline",
            "growth_rate": 0.05,
            "design_period": 20,
            "years_to_completion": 0.0,
            "vdf": 3.0,
            "distribution_factor": 0.50
        },

        {
            "scenario_name": "Higher Growth",
            "growth_rate": 0.07,
            "design_period": 20,
            "years_to_completion": 0.0,
            "vdf": 3.0,
            "distribution_factor": 0.50
        },

        {
            "scenario_name": "Higher VDF",
            "growth_rate": 0.05,
            "design_period": 20,
            "years_to_completion": 0.0,
            "vdf": 4.0,
            "distribution_factor": 0.50
        },

        {
            "scenario_name": "Longer Design Period",
            "growth_rate": 0.05,
            "design_period": 30,
            "years_to_completion": 0.0,
            "vdf": 3.0,
            "distribution_factor": 0.50
        }
    ]

    comparison_results = compare_scenarios(
        scenarios=test_scenarios,
        average_cvpd=TEST_AVERAGE_CVPD,
        baseline_scenario_name="Baseline"
    )

    compact_results = create_compact_comparison_table(
        comparison_results
    )

    summary = create_scenario_summary(
        comparison_results
    )

    print("\nSCENARIO COMPARISON")
    print("-" * 70)

    print(
        compact_results
        .round(2)
        .to_string(index=False)
    )

    print("\nENGINEERING SUMMARY")
    print("-" * 70)

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nSCENARIO COMPARISON MODULE EXECUTED SUCCESSFULLY")
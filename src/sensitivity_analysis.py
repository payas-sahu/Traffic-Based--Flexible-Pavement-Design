import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from design_traffic import (
    calculate_design_traffic,
    get_average_commercial_traffic
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "traffic_data.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# DEFAULT BASELINE PARAMETERS
# Used only when running this file directly.
# ============================================================

DEFAULT_GROWTH_RATE = 0.05
DEFAULT_DESIGN_PERIOD = 20
DEFAULT_YEARS_TO_COMPLETION = 0.0
DEFAULT_VDF = 3.0
DEFAULT_DISTRIBUTION_FACTOR = 0.50


# ============================================================
# 1. CALCULATE BASELINE
# ============================================================

def calculate_baseline(
    average_cvpd,
    growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):

    return calculate_design_traffic(

        traffic_at_last_count=average_cvpd,

        growth_rate=growth_rate,

        design_period=design_period,

        years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


# ============================================================
# 2. CREATE NUMERIC SCENARIO VALUES
# ============================================================

def create_scenario_values(
    baseline,
    minimum,
    maximum,
    step,
    decimals=2
):
    """
    Create sensitivity scenario values and ensure that the
    current baseline value is included.

    Floating-point values are rounded to avoid values such as
    0.30000000000000004.
    """

    values = []

    current_value = minimum

    while current_value <= maximum + 1e-12:

        values.append(
            round(current_value, decimals)
        )

        current_value += step

    values.append(
        round(baseline, decimals)
    )

    return sorted(set(values))


# ============================================================
# 3. GROWTH RATE SENSITIVITY
# ============================================================

def analyze_growth_rate(
    average_cvpd,
    baseline_growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):

    baseline_percent = baseline_growth_rate * 100

    minimum_growth = max(
        0.0,
        baseline_percent - 3.0
    )

    maximum_growth = min(
        20.0,
        baseline_percent + 5.0
    )

    growth_rates_percent = create_scenario_values(

        baseline=baseline_percent,

        minimum=minimum_growth,

        maximum=maximum_growth,

        step=1.0,

        decimals=2

    )

    records = []

    for growth_rate_percent in growth_rates_percent:

        results = calculate_design_traffic(

            traffic_at_last_count=average_cvpd,

            growth_rate=growth_rate_percent / 100,

            design_period=design_period,

            years_to_completion=years_to_completion,

            vdf=vdf,

            distribution_factor=distribution_factor

        )

        records.append({

            "Growth_Rate_Percent":
                growth_rate_percent,

            "Design_Traffic_MSA":
                results["design_traffic_msa"],

            "Is_Baseline":
                abs(
                    growth_rate_percent
                    - baseline_percent
                ) < 1e-9

        })

    return pd.DataFrame(records)


# ============================================================
# 4. VDF SENSITIVITY
# ============================================================

def analyze_vdf(
    average_cvpd,
    growth_rate,
    design_period,
    years_to_completion,
    baseline_vdf,
    distribution_factor
):

    minimum_vdf = max(
        0.1,
        baseline_vdf - 1.5
    )

    maximum_vdf = min(
        20.0,
        baseline_vdf + 2.0
    )

    vdf_values = create_scenario_values(

        baseline=baseline_vdf,

        minimum=minimum_vdf,

        maximum=maximum_vdf,

        step=0.5,

        decimals=2

    )

    records = []

    for scenario_vdf in vdf_values:

        results = calculate_design_traffic(

            traffic_at_last_count=average_cvpd,

            growth_rate=growth_rate,

            design_period=design_period,

            years_to_completion=years_to_completion,

            vdf=scenario_vdf,

            distribution_factor=distribution_factor

        )

        records.append({

            "VDF":
                scenario_vdf,

            "Design_Traffic_MSA":
                results["design_traffic_msa"],

            "Is_Baseline":
                abs(
                    scenario_vdf
                    - baseline_vdf
                ) < 1e-9

        })

    return pd.DataFrame(records)


# ============================================================
# 5. DESIGN PERIOD SENSITIVITY
# ============================================================

def analyze_design_period(
    average_cvpd,
    growth_rate,
    baseline_design_period,
    years_to_completion,
    vdf,
    distribution_factor
):

    minimum_period = max(
        1,
        baseline_design_period - 10
    )

    maximum_period = min(
        50,
        baseline_design_period + 10
    )

    design_periods = list(

        range(
            minimum_period,
            maximum_period + 1,
            5
        )

    )

    design_periods.append(
        int(baseline_design_period)
    )

    design_periods = sorted(
        set(design_periods)
    )

    records = []

    for scenario_period in design_periods:

        results = calculate_design_traffic(

            traffic_at_last_count=average_cvpd,

            growth_rate=growth_rate,

            design_period=scenario_period,

            years_to_completion=years_to_completion,

            vdf=vdf,

            distribution_factor=distribution_factor

        )

        records.append({

            "Design_Period_Years":
                scenario_period,

            "Design_Traffic_MSA":
                results["design_traffic_msa"],

            "Is_Baseline":
                scenario_period
                == baseline_design_period

        })

    return pd.DataFrame(records)


# ============================================================
# 6. CONSTRUCTION DELAY SENSITIVITY
# ============================================================

def analyze_construction_delay(
    average_cvpd,
    growth_rate,
    design_period,
    baseline_years_to_completion,
    vdf,
    distribution_factor
):

    minimum_delay = max(
        0.0,
        baseline_years_to_completion - 2.0
    )

    maximum_delay = min(
        20.0,
        baseline_years_to_completion + 5.0
    )

    delay_values = create_scenario_values(

        baseline=baseline_years_to_completion,

        minimum=minimum_delay,

        maximum=maximum_delay,

        step=1.0,

        decimals=2

    )

    records = []

    for scenario_delay in delay_values:

        results = calculate_design_traffic(

            traffic_at_last_count=average_cvpd,

            growth_rate=growth_rate,

            design_period=design_period,

            years_to_completion=scenario_delay,

            vdf=vdf,

            distribution_factor=distribution_factor

        )

        records.append({

            "Years_To_Completion":
                scenario_delay,

            "Design_Traffic_MSA":
                results["design_traffic_msa"],

            "Is_Baseline":
                abs(
                    scenario_delay
                    - baseline_years_to_completion
                ) < 1e-9

        })

    return pd.DataFrame(records)


# ============================================================
# 7. RUN COMPLETE DYNAMIC SENSITIVITY ANALYSIS
# ============================================================

def run_sensitivity_analysis(
    average_cvpd,
    growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):

    baseline_results = calculate_baseline(

        average_cvpd=average_cvpd,

        growth_rate=growth_rate,

        design_period=design_period,

        years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


    growth_results = analyze_growth_rate(

        average_cvpd=average_cvpd,

        baseline_growth_rate=growth_rate,

        design_period=design_period,

        years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


    vdf_results = analyze_vdf(

        average_cvpd=average_cvpd,

        growth_rate=growth_rate,

        design_period=design_period,

        years_to_completion=years_to_completion,

        baseline_vdf=vdf,

        distribution_factor=distribution_factor

    )


    design_period_results = analyze_design_period(

        average_cvpd=average_cvpd,

        growth_rate=growth_rate,

        baseline_design_period=design_period,

        years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


    construction_delay_results = analyze_construction_delay(

        average_cvpd=average_cvpd,

        growth_rate=growth_rate,

        design_period=design_period,

        baseline_years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


    return {

        "baseline":
            baseline_results,

        "growth_rate":
            growth_results,

        "vdf":
            vdf_results,

        "design_period":
            design_period_results,

        "construction_delay":
            construction_delay_results

    }


# ============================================================
# 8. CALCULATE PARAMETER INFLUENCE
# ============================================================

def calculate_parameter_influence(results):
    """
    Calculate a range-based scenario influence ranking.

    Percentage range is measured relative to the current
    baseline design traffic:

        (Maximum MSA - Minimum MSA) / Baseline MSA * 100

    This is not a formal global sensitivity analysis.
    """

    baseline_msa = (
        results["baseline"]["design_traffic_msa"]
    )

    parameter_data = {

        "Growth Rate":
            results["growth_rate"],

        "VDF":
            results["vdf"],

        "Design Period":
            results["design_period"],

        "Construction Delay":
            results["construction_delay"]

    }

    records = []

    for parameter, dataframe in parameter_data.items():

        minimum_msa = (
            dataframe[
                "Design_Traffic_MSA"
            ].min()
        )

        maximum_msa = (
            dataframe[
                "Design_Traffic_MSA"
            ].max()
        )

        msa_range = (
            maximum_msa
            - minimum_msa
        )

        percentage_range = (

            msa_range
            / baseline_msa
            * 100

        )

        records.append({

            "Parameter":
                parameter,

            "Minimum_MSA":
                minimum_msa,

            "Maximum_MSA":
                maximum_msa,

            "MSA_Range":
                msa_range,

            "Percentage_Range_of_Baseline":
                percentage_range

        })


    influence_df = pd.DataFrame(records)


    influence_df = influence_df.sort_values(

        by="Percentage_Range_of_Baseline",

        ascending=False

    ).reset_index(drop=True)


    influence_df.insert(

        0,

        "Influence_Rank",

        influence_df.index + 1

    )


    return influence_df


# ============================================================
# 9. CREATE SENSITIVITY CHART
# Used by standalone execution.
# Streamlit will render DataFrames directly.
# ============================================================

def create_sensitivity_chart(
    dataframe,
    x_column,
    title,
    x_label,
    output_file
):

    plt.figure(figsize=(9, 6))

    plt.plot(
        dataframe[x_column],
        dataframe["Design_Traffic_MSA"],
        marker="o"
    )

    plt.title(title)

    plt.xlabel(x_label)

    plt.ylabel("Design Traffic (MSA)")

    plt.grid()

    plt.tight_layout()

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.close()


# ============================================================
# 10. SAVE SENSITIVITY RESULTS
# ============================================================

def save_sensitivity_results(
    results,
    influence_results
):

    results["growth_rate"].to_csv(

        OUTPUT_DIR / "growth_rate_sensitivity.csv",

        index=False

    )


    results["vdf"].to_csv(

        OUTPUT_DIR / "vdf_sensitivity.csv",

        index=False

    )


    results["design_period"].to_csv(

        OUTPUT_DIR / "design_period_sensitivity.csv",

        index=False

    )


    results["construction_delay"].to_csv(

        OUTPUT_DIR / "construction_delay_sensitivity.csv",

        index=False

    )


    influence_results.to_csv(

        OUTPUT_DIR / "parameter_influence_ranking.csv",

        index=False

    )


# ============================================================
# 11. CREATE ALL CHARTS
# ============================================================

def create_all_sensitivity_charts(results):

    create_sensitivity_chart(

        results["growth_rate"],

        "Growth_Rate_Percent",

        "Sensitivity of Design Traffic to Growth Rate",

        "Annual Traffic Growth Rate (%)",

        OUTPUT_DIR / "growth_rate_sensitivity.png"

    )


    create_sensitivity_chart(

        results["vdf"],

        "VDF",

        "Sensitivity of Design Traffic to VDF",

        "Vehicle Damage Factor (VDF)",

        OUTPUT_DIR / "vdf_sensitivity.png"

    )


    create_sensitivity_chart(

        results["design_period"],

        "Design_Period_Years",

        "Sensitivity of Design Traffic to Design Period",

        "Design Period (Years)",

        OUTPUT_DIR / "design_period_sensitivity.png"

    )


    create_sensitivity_chart(

        results["construction_delay"],

        "Years_To_Completion",

        "Sensitivity of Design Traffic to Construction Delay",

        "Years Between Traffic Count and Road Opening",

        OUTPUT_DIR / "construction_delay_sensitivity.png"

    )


# ============================================================
# 12. TEST MODULE
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)

    print("DYNAMIC DESIGN TRAFFIC SENSITIVITY ANALYSIS")

    print("=" * 70)


    average_cvpd = get_average_commercial_traffic(
        DATA_FILE
    )


    results = run_sensitivity_analysis(

        average_cvpd=average_cvpd,

        growth_rate=DEFAULT_GROWTH_RATE,

        design_period=DEFAULT_DESIGN_PERIOD,

        years_to_completion=DEFAULT_YEARS_TO_COMPLETION,

        vdf=DEFAULT_VDF,

        distribution_factor=DEFAULT_DISTRIBUTION_FACTOR

    )


    influence_results = (
        calculate_parameter_influence(
            results
        )
    )


    print(

        f"\nAverage Commercial Traffic : "
        f"{average_cvpd:.2f} CVPD"

    )


    print(

        f"Baseline Design Traffic    : "
        f"{results['baseline']['design_traffic_msa']:.2f} MSA"

    )


    print("\nGROWTH RATE SENSITIVITY")

    print("-" * 70)

    print(
        results["growth_rate"].round(2)
    )


    print("\nVDF SENSITIVITY")

    print("-" * 70)

    print(
        results["vdf"].round(2)
    )


    print("\nDESIGN PERIOD SENSITIVITY")

    print("-" * 70)

    print(
        results["design_period"].round(2)
    )


    print("\nCONSTRUCTION DELAY SENSITIVITY")

    print("-" * 70)

    print(
        results["construction_delay"].round(2)
    )


    print("\nPARAMETER INFLUENCE RANKING")

    print("-" * 70)

    print(
        influence_results.round(2)
    )


    most_influential_parameter = (
        influence_results.iloc[0]["Parameter"]
    )


    print(

        "\nMOST INFLUENTIAL PARAMETER "
        "WITHIN TESTED SCENARIO RANGES"

    )

    print("-" * 70)

    print(
        most_influential_parameter
    )


    save_sensitivity_results(

        results,

        influence_results

    )


    create_all_sensitivity_charts(
        results
    )


    print(

        "\nDynamic sensitivity analysis CSV files "
        "and charts saved successfully."

    )


    print(

        "\nSENSITIVITY ANALYSIS MODULE "
        "EXECUTED SUCCESSFULLY"

    )
import pandas as pd
from pathlib import Path

from traffic_utils import (
    load_traffic_data,
    validate_traffic_data,
    add_total_traffic,
    calculate_commercial_vehicle_analysis
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "traffic_data.csv"

OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. VALIDATE DESIGN INPUTS
# ============================================================

def validate_design_inputs(
    commercial_traffic,
    growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):
    """
    Validate inputs required for design traffic calculation.

    growth_rate must be entered as a decimal.

    Example:
    5% growth rate = 0.05
    """

    errors = []


    if commercial_traffic < 0:

        errors.append(
            "Commercial traffic cannot be negative."
        )


    if growth_rate < 0:

        errors.append(
            "Growth rate cannot be negative."
        )


    if design_period <= 0:

        errors.append(
            "Design period must be greater than zero."
        )


    if years_to_completion < 0:

        errors.append(
            "Years to completion cannot be negative."
        )


    if vdf <= 0:

        errors.append(
            "Vehicle Damage Factor must be greater than zero."
        )


    if not 0 < distribution_factor <= 1:

        errors.append(
            "Distribution factor must be greater than 0 "
            "and less than or equal to 1."
        )


    return errors


# ============================================================
# 2. PROJECT TRAFFIC TO YEAR OF ROAD OPENING
# ============================================================

def project_traffic_to_opening(
    traffic_at_last_count,
    growth_rate,
    years_to_completion
):
    """
    Project commercial traffic from the year of the traffic
    count to the year of completion/opening.

    A = P(1 + r)^x

    P = commercial traffic at last count
    r = annual traffic growth rate (decimal)
    x = years between traffic count and road completion
    """

    opening_traffic = (

        traffic_at_last_count

        * (1 + growth_rate) ** years_to_completion

    )


    return opening_traffic


# ============================================================
# 3. CALCULATE CUMULATIVE GROWTH FACTOR
# ============================================================

def calculate_growth_factor(
    growth_rate,
    design_period
):
    """
    Calculate cumulative traffic growth factor.

    Growth Factor = ((1+r)^n - 1) / r

    For r = 0:

    Growth Factor = n
    """


    if growth_rate == 0:

        return float(design_period)


    growth_factor = (

        ((1 + growth_rate) ** design_period - 1)

        / growth_rate

    )


    return growth_factor


# ============================================================
# 4. CALCULATE DESIGN TRAFFIC
# ============================================================

def calculate_design_traffic(
    traffic_at_last_count,
    growth_rate,
    design_period,
    years_to_completion,
    vdf,
    distribution_factor
):
    """
    Calculate cumulative design traffic.

    N = 365 × A × D × F × Growth Factor

    Returns the complete calculation results as a dictionary.
    """


    # Validate inputs

    errors = validate_design_inputs(

        commercial_traffic=traffic_at_last_count,

        growth_rate=growth_rate,

        design_period=design_period,

        years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


    if errors:

        raise ValueError(
            " | ".join(errors)
        )


    # Traffic at road opening

    opening_traffic = project_traffic_to_opening(

        traffic_at_last_count,

        growth_rate,

        years_to_completion

    )


    # Cumulative growth factor

    growth_factor = calculate_growth_factor(

        growth_rate,

        design_period

    )


    # Cumulative standard axles

    cumulative_standard_axles = (

        365

        * opening_traffic

        * distribution_factor

        * vdf

        * growth_factor

    )


    # Convert to MSA

    design_traffic_msa = (

        cumulative_standard_axles

        / 1_000_000

    )


    return {

        "traffic_at_last_count":
            traffic_at_last_count,

        "opening_traffic":
            opening_traffic,

        "growth_rate":
            growth_rate,

        "design_period":
            design_period,

        "years_to_completion":
            years_to_completion,

        "vdf":
            vdf,

        "distribution_factor":
            distribution_factor,

        "growth_factor":
            growth_factor,

        "cumulative_standard_axles":
            cumulative_standard_axles,

        "design_traffic_msa":
            design_traffic_msa

    }


# ============================================================
# 5. GET COMMERCIAL TRAFFIC FROM MODULE 1
# ============================================================

def get_average_commercial_traffic(
    file_path
):
    """
    Load the traffic dataset and obtain average two-way
    commercial traffic per day from Module 1.
    """


    df = load_traffic_data(file_path)


    validation_results = (
        validate_traffic_data(df)
    )


    if validation_results["missing_columns"]:

        raise ValueError(

            "Required traffic columns are missing: "

            + str(
                validation_results[
                    "missing_columns"
                ]
            )

        )


    if validation_results["missing_values"] > 0:

        raise ValueError(
            "Traffic dataset contains missing values."
        )


    if validation_results["negative_counts"] > 0:

        raise ValueError(
            "Traffic dataset contains negative traffic counts."
        )


    df = add_total_traffic(df)


    commercial_results = (
        calculate_commercial_vehicle_analysis(df)
    )


    average_cvpd = (

        commercial_results[
            "average_cvpd"
        ]

    )


    return average_cvpd


# ============================================================
# 6. SAVE DESIGN TRAFFIC SUMMARY
# ============================================================

def save_design_traffic_summary(
    results,
    output_file
):
    """
    Save design traffic calculation results to CSV.
    """


    summary = pd.DataFrame({

        "Parameter": [

            "Commercial Traffic at Last Count",

            "Traffic Growth Rate",

            "Years to Completion",

            "Traffic at Road Opening",

            "Design Period",

            "Vehicle Damage Factor",

            "Lateral Distribution Factor",

            "Growth Factor",

            "Cumulative Standard Axles",

            "Design Traffic"

        ],


        "Value": [

            results[
                "traffic_at_last_count"
            ],

            results[
                "growth_rate"
            ] * 100,

            results[
                "years_to_completion"
            ],

            results[
                "opening_traffic"
            ],

            results[
                "design_period"
            ],

            results[
                "vdf"
            ],

            results[
                "distribution_factor"
            ],

            results[
                "growth_factor"
            ],

            results[
                "cumulative_standard_axles"
            ],

            results[
                "design_traffic_msa"
            ]

        ],


        "Unit": [

            "CVPD",

            "%",

            "years",

            "CVPD",

            "years",

            "-",

            "-",

            "-",

            "standard axles",

            "MSA"

        ]

    })


    summary.to_csv(
        output_file,
        index=False
    )


# ============================================================
# 7. RUN MODULE FOR TESTING
# ============================================================

if __name__ == "__main__":


    print("\n" + "=" * 60)

    print(
        "DESIGN TRAFFIC CALCULATION ENGINE"
    )

    print(
        "IRC:37-2018"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # GET AVERAGE COMMERCIAL TRAFFIC FROM MODULE 1
    # --------------------------------------------------------

    average_cvpd = (
        get_average_commercial_traffic(
            DATA_FILE
        )
    )


    print(

        "\nAverage commercial traffic "
        "from Module 1:"

    )


    print(

        f"{average_cvpd:,.2f} CVPD"

    )


    # --------------------------------------------------------
    # DESIGN INPUTS
    # --------------------------------------------------------

    print("\nDESIGN INPUT PARAMETERS")

    print("-" * 60)


    growth_rate_percent = float(

        input(
            "Enter annual traffic growth rate (%) : "
        )

    )


    design_period = int(

        input(
            "Enter pavement design period (years) : "
        )

    )


    years_to_completion = float(

        input(
            "Enter years between traffic count "
            "and road completion : "
        )

    )


    vdf = float(

        input(
            "Enter Vehicle Damage Factor (VDF) : "
        )

    )


    distribution_factor = float(

        input(
            "Enter lateral distribution factor (D) : "
        )

    )


    growth_rate = (

        growth_rate_percent / 100

    )


    # --------------------------------------------------------
    # CALCULATE DESIGN TRAFFIC
    # --------------------------------------------------------

    results = calculate_design_traffic(

        traffic_at_last_count=average_cvpd,

        growth_rate=growth_rate,

        design_period=design_period,

        years_to_completion=years_to_completion,

        vdf=vdf,

        distribution_factor=distribution_factor

    )


    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print("DESIGN TRAFFIC RESULTS")

    print("=" * 60)


    print(

        f"Traffic at last count (P)        : "

        f"{results['traffic_at_last_count']:,.2f} CVPD"

    )


    print(

        f"Traffic at road opening (A)      : "

        f"{results['opening_traffic']:,.2f} CVPD"

    )


    print(

        f"Annual traffic growth rate       : "

        f"{results['growth_rate'] * 100:.2f} %"

    )


    print(

        f"Design period                    : "

        f"{results['design_period']} years"

    )


    print(

        f"Years to completion              : "

        f"{results['years_to_completion']:.2f} years"

    )


    print(

        f"Vehicle Damage Factor            : "

        f"{results['vdf']:.2f}"

    )


    print(

        f"Lateral distribution factor      : "

        f"{results['distribution_factor']:.2f}"

    )


    print(

        f"Growth factor                    : "

        f"{results['growth_factor']:.4f}"

    )


    print("-" * 60)


    print(

        f"Cumulative standard axles        : "

        f"{results['cumulative_standard_axles']:,.0f}"

    )


    print(

        f"DESIGN TRAFFIC                   : "

        f"{results['design_traffic_msa']:.2f} MSA"

    )


    print("=" * 60)


    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    OUTPUT_FILE = (

        OUTPUT_DIR

        / "design_traffic_summary.csv"

    )


    save_design_traffic_summary(

        results,

        OUTPUT_FILE

    )


    print(

        f"\nDesign traffic summary saved to:"

        f"\n{OUTPUT_FILE}"

    )


    print(

        "\nDESIGN TRAFFIC ENGINE "

        "EXECUTED SUCCESSFULLY"

    )
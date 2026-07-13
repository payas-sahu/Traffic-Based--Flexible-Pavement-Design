import pandas as pd
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
# BASELINE DESIGN PARAMETERS
# ============================================================

BASE_GROWTH_RATE = 0.05
BASE_DESIGN_PERIOD = 20
BASE_YEARS_TO_COMPLETION = 0
BASE_VDF = 3.0
BASE_DISTRIBUTION_FACTOR = 0.50


# ============================================================
# IRC CATALOGUE TRAFFIC LEVELS
# ============================================================

CATALOGUE_TRAFFIC_LEVELS = [5, 10, 20, 30, 40, 50]


# ============================================================
# SUPPORTED CATALOGUE CASES
#
# First verified implementation:
# IRC:37-2018
# Figure 12.22 / Plate-22
# Annex III Table III.3
#
# Pavement:
# Bituminous Surface + CTSB + CTB + SAMI
#
# Effective CBR = 10%
# ============================================================

VERIFIED_CATALOGUE_CASES = {

    (3, 10, 5): {
        "plate": "Plate-22",
        "figure": "Figure 12.22",
        "annex_table": "Table III.3",
        "total_bituminous_mm": 40,
        "ctb_mm": 160,
        "ctsb_mm": 200
    },

    (3, 10, 10): {
        "plate": "Plate-22",
        "figure": "Figure 12.22",
        "annex_table": "Table III.3",
        "total_bituminous_mm": 50,
        "ctb_mm": 160,
        "ctsb_mm": 200
    },

    (3, 10, 20): {
        "plate": "Plate-22",
        "figure": "Figure 12.22",
        "annex_table": "Table III.3",
        "total_bituminous_mm": 80,
        "ctb_mm": 150,
        "ctsb_mm": 200
    },

    (3, 10, 30): {
        "plate": "Plate-22",
        "figure": "Figure 12.22",
        "annex_table": "Table III.3",
        "total_bituminous_mm": 100,
        "ctb_mm": 130,
        "ctsb_mm": 200
    },

    (3, 10, 40): {
        "plate": "Plate-22",
        "figure": "Figure 12.22",
        "annex_table": "Table III.3",
        "total_bituminous_mm": 100,
        "ctb_mm": 135,
        "ctsb_mm": 200
    },

    (3, 10, 50): {
        "plate": "Plate-22",
        "figure": "Figure 12.22",
        "annex_table": "Table III.3",
        "total_bituminous_mm": 100,
        "ctb_mm": 135,
        "ctsb_mm": 200
    }
}


# ============================================================
# IRC MATERIAL PROPERTIES
#
# Catalogue assumptions / recommended structural properties.
# ============================================================

BITUMINOUS_MODULUS_MPA = 3000
BITUMINOUS_POISSON_RATIO = 0.35

CTB_MODULUS_MPA = 5000
CTB_POISSON_RATIO = 0.25

CTSB_MODULUS_MPA = 600
CTSB_POISSON_RATIO = 0.25

SUBGRADE_POISSON_RATIO = 0.35


# ============================================================
# 1. SELECT CATALOGUE TRAFFIC LEVEL
# ============================================================

def select_catalogue_traffic_level(design_traffic_msa):

    if design_traffic_msa < 2:

        raise ValueError(
            "Design traffic is below 2 MSA. "
            "Use the applicable IRC guidelines for low-volume roads."
        )

    if design_traffic_msa > 50:

        raise ValueError(
            "Design traffic exceeds 50 MSA. "
            "IRC catalogue screening is not applicable."
        )

    for traffic_level in CATALOGUE_TRAFFIC_LEVELS:

        if design_traffic_msa <= traffic_level:

            return traffic_level

    return 50


# ============================================================
# 2. CALCULATE SUBGRADE MODULUS
# ============================================================

def calculate_subgrade_modulus(effective_cbr):

    if effective_cbr <= 0:

        raise ValueError(
            "Effective CBR must be greater than zero."
        )

    if effective_cbr <= 5:

        modulus = 10 * effective_cbr

    else:

        modulus = 17.6 * effective_cbr ** 0.64

    return min(modulus, 100)


# ============================================================
# 3. GET VERIFIED IRC CATALOGUE CASE
# ============================================================

def get_verified_catalogue_case(
    alternative_number,
    effective_cbr,
    catalogue_traffic_level
):

    key = (
        alternative_number,
        int(effective_cbr),
        catalogue_traffic_level
    )

    if key not in VERIFIED_CATALOGUE_CASES:

        raise ValueError(

            "\nThe selected combination has not yet been "
            "implemented from a verified IRC catalogue plate.\n"

            "Currently supported case:\n"

            "Alternative 3 + Effective CBR 10% + "
            "Catalogue traffic levels 5 to 50 MSA."
        )

    return VERIFIED_CATALOGUE_CASES[key]


# ============================================================
# 4. CREATE IRC CATALOGUE SECTION TABLE
# ============================================================

def create_catalogue_section_table(catalogue_case):

    records = [

        {
            "Layer":
                "Total Bituminous Layer",

            "Thickness_mm":
                catalogue_case["total_bituminous_mm"],

            "Catalogue_Status":
                "Verified IRC Catalogue Thickness"
        },

        {
            "Layer":
                "SAMI",

            "Thickness_mm":
                None,

            "Catalogue_Status":
                "Crack Relief Treatment - "
                "Not Structural IITPAVE Layer"
        },

        {
            "Layer":
                "Cement Treated Base (CTB)",

            "Thickness_mm":
                catalogue_case["ctb_mm"],

            "Catalogue_Status":
                "Verified IRC Catalogue Thickness"
        },

        {
            "Layer":
                "Cement Treated Sub-base (CTSB)",

            "Thickness_mm":
                catalogue_case["ctsb_mm"],

            "Catalogue_Status":
                "Verified IRC Catalogue Thickness"
        },

        {
            "Layer":
                "Subgrade",

            "Thickness_mm":
                "Semi-Infinite",

            "Catalogue_Status":
                "Foundation Layer"
        }
    ]

    return pd.DataFrame(records)


# ============================================================
# 5. CREATE IITPAVE STRUCTURAL INPUT TABLE
# ============================================================

def create_iitpave_structural_input(
    catalogue_case,
    subgrade_modulus
):

    records = [

        {
            "Layer_Number": 1,

            "Layer_Name":
                "Total Bituminous Layer",

            "Thickness_mm":
                catalogue_case["total_bituminous_mm"],

            "Elastic_or_Resilient_Modulus_MPa":
                BITUMINOUS_MODULUS_MPA,

            "Poisson_Ratio":
                BITUMINOUS_POISSON_RATIO
        },

        {
            "Layer_Number": 2,

            "Layer_Name":
                "Cement Treated Base (CTB)",

            "Thickness_mm":
                catalogue_case["ctb_mm"],

            "Elastic_or_Resilient_Modulus_MPa":
                CTB_MODULUS_MPA,

            "Poisson_Ratio":
                CTB_POISSON_RATIO
        },

        {
            "Layer_Number": 3,

            "Layer_Name":
                "Cement Treated Sub-base (CTSB)",

            "Thickness_mm":
                catalogue_case["ctsb_mm"],

            "Elastic_or_Resilient_Modulus_MPa":
                CTSB_MODULUS_MPA,

            "Poisson_Ratio":
                CTSB_POISSON_RATIO
        },

        {
            "Layer_Number": 4,

            "Layer_Name":
                "Subgrade",

            "Thickness_mm":
                "Semi-Infinite",

            "Elastic_or_Resilient_Modulus_MPa":
                subgrade_modulus,

            "Poisson_Ratio":
                SUBGRADE_POISSON_RATIO
        }
    ]

    return pd.DataFrame(records)


# ============================================================
# 6. CREATE IITPAVE LOAD INPUT TABLE
# ============================================================

def create_iitpave_load_input():

    records = [

        {
            "Input_Parameter":
                "Standard Axle Load",

            "Value":
                80,

            "Unit":
                "kN"
        },

        {
            "Input_Parameter":
                "Number of Wheels",

            "Value":
                4,

            "Unit":
                "-"
        },

        {
            "Input_Parameter":
                "Load per Wheel",

            "Value":
                20,

            "Unit":
                "kN"
        },

        {
            "Input_Parameter":
                "Tyre Contact Pressure",

            "Value":
                0.56,

            "Unit":
                "MPa"
        }
    ]

    return pd.DataFrame(records)


# ============================================================
# 7. CREATE SCREENING SUMMARY
# ============================================================

def create_screening_summary(
    design_traffic_msa,
    catalogue_traffic_level,
    effective_cbr,
    subgrade_modulus,
    catalogue_case
):

    summary = {

        "Calculated_Design_Traffic_MSA":
            design_traffic_msa,

        "Catalogue_Screening_Traffic_MSA":
            catalogue_traffic_level,

        "Effective_CBR_Percent":
            effective_cbr,

        "Estimated_Subgrade_Modulus_MPa":
            subgrade_modulus,

        "Pavement_Composition":
            "Bituminous Surface + CTSB + CTB + SAMI",

        "IRC_Figure":
            catalogue_case["figure"],

        "IRC_Plate":
            catalogue_case["plate"],

        "IRC_Annex_Table":
            catalogue_case["annex_table"],

        "Crack_Relief_Treatment":
            "SAMI",

        "SAMI_IITPAVE_Status":
            "Excluded from structural-layer input",

        "Verification_Status":
            "Preliminary IRC catalogue screening; "
            "site-specific mechanistic-empirical "
            "verification required"
    }

    return summary


# ============================================================
# 8. SAVE OUTPUT FILES
# ============================================================

def save_outputs(
    screening_summary,
    catalogue_section_table,
    iitpave_structural_input,
    iitpave_load_input
):

    screening_file = (
        OUTPUT_DIR
        / "pavement_catalogue_screening_summary.csv"
    )

    catalogue_file = (
        OUTPUT_DIR
        / "verified_irc_catalogue_section.csv"
    )

    structural_file = (
        OUTPUT_DIR
        / "iitpave_structural_input_summary.csv"
    )

    load_file = (
        OUTPUT_DIR
        / "iitpave_load_input_summary.csv"
    )

    pd.DataFrame(
        [screening_summary]
    ).to_csv(
        screening_file,
        index=False
    )

    catalogue_section_table.to_csv(
        catalogue_file,
        index=False
    )

    iitpave_structural_input.to_csv(
        structural_file,
        index=False
    )

    iitpave_load_input.to_csv(
        load_file,
        index=False
    )

    return (
        screening_file,
        catalogue_file,
        structural_file,
        load_file
    )


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)

    print(
        "IRC CATALOGUE SCREENING AND "
        "IITPAVE INPUT PREPARATION"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # GET TRAFFIC DATA
    # --------------------------------------------------------

    average_cvpd = (
        get_average_commercial_traffic(
            DATA_FILE
        )
    )


    # --------------------------------------------------------
    # CALCULATE DESIGN TRAFFIC
    # --------------------------------------------------------

    design_results = calculate_design_traffic(

        traffic_at_last_count=
            average_cvpd,

        growth_rate=
            BASE_GROWTH_RATE,

        design_period=
            BASE_DESIGN_PERIOD,

        years_to_completion=
            BASE_YEARS_TO_COMPLETION,

        vdf=
            BASE_VDF,

        distribution_factor=
            BASE_DISTRIBUTION_FACTOR
    )


    design_traffic_msa = (
        design_results[
            "design_traffic_msa"
        ]
    )


    # --------------------------------------------------------
    # SELECT CATALOGUE TRAFFIC LEVEL
    # --------------------------------------------------------

    catalogue_traffic_level = (
        select_catalogue_traffic_level(
            design_traffic_msa
        )
    )


    # --------------------------------------------------------
    # CURRENT VERIFIED CASE
    # --------------------------------------------------------

    effective_cbr = 10

    alternative_number = 3


    catalogue_case = (
        get_verified_catalogue_case(

            alternative_number=
                alternative_number,

            effective_cbr=
                effective_cbr,

            catalogue_traffic_level=
                catalogue_traffic_level
        )
    )


    # --------------------------------------------------------
    # SUBGRADE MODULUS
    # --------------------------------------------------------

    subgrade_modulus = (
        calculate_subgrade_modulus(
            effective_cbr
        )
    )


    # --------------------------------------------------------
    # CREATE TABLES
    # --------------------------------------------------------

    catalogue_section_table = (
        create_catalogue_section_table(
            catalogue_case
        )
    )


    iitpave_structural_input = (
        create_iitpave_structural_input(

            catalogue_case=
                catalogue_case,

            subgrade_modulus=
                subgrade_modulus
        )
    )


    iitpave_load_input = (
        create_iitpave_load_input()
    )


    screening_summary = (
        create_screening_summary(

            design_traffic_msa=
                design_traffic_msa,

            catalogue_traffic_level=
                catalogue_traffic_level,

            effective_cbr=
                effective_cbr,

            subgrade_modulus=
                subgrade_modulus,

            catalogue_case=
                catalogue_case
        )
    )


    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print(
        f"\nCalculated Design Traffic      : "
        f"{design_traffic_msa:.2f} MSA"
    )

    print(
        f"Catalogue Screening Level      : "
        f"{catalogue_traffic_level} MSA"
    )

    print(
        f"Effective CBR                  : "
        f"{effective_cbr}%"
    )

    print(
        f"Estimated Subgrade Modulus     : "
        f"{subgrade_modulus:.2f} MPa"
    )

    print(
        f"IRC Catalogue Reference        : "
        f"{catalogue_case['figure']} / "
        f"{catalogue_case['plate']}"
    )

    print(
        f"Annex Verification Reference   : "
        f"{catalogue_case['annex_table']}"
    )


    print("\n" + "=" * 70)

    print("VERIFIED IRC CATALOGUE SECTION")

    print("=" * 70)

    print(
        catalogue_section_table.to_string(
            index=False
        )
    )


    print("\n" + "=" * 70)

    print("IITPAVE STRUCTURAL INPUT SUMMARY")

    print("=" * 70)

    print(
        iitpave_structural_input.to_string(
            index=False
        )
    )


    print("\n" + "=" * 70)

    print("IITPAVE LOAD INPUT SUMMARY")

    print("=" * 70)

    print(
        iitpave_load_input.to_string(
            index=False
        )
    )


    print("\nIMPORTANT ENGINEERING NOTE")

    print("-" * 70)

    print(
        "SAMI is a crack-relief treatment and is excluded "
        "from the IITPAVE structural-layer input."
    )

    print(
        "The catalogue section is a preliminary screening "
        "case. Final pavement design requires site-specific "
        "inputs, mechanistic-empirical analysis, performance "
        "checks, and iteration where required."
    )


    # --------------------------------------------------------
    # SAVE OUTPUT FILES
    # --------------------------------------------------------

    files = save_outputs(

        screening_summary=
            screening_summary,

        catalogue_section_table=
            catalogue_section_table,

        iitpave_structural_input=
            iitpave_structural_input,

        iitpave_load_input=
            iitpave_load_input
    )


    print("\nOUTPUT FILES CREATED")

    print("-" * 70)

    for file in files:

        print(file)


    print(
        "\nPAVEMENT DESIGN SUPPORT MODULE "
        "EXECUTED SUCCESSFULLY"
    )
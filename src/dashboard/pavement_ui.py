import pandas as pd
import streamlit as st

from pavement_design import (
    select_catalogue_traffic_level,
    calculate_subgrade_modulus,
    get_verified_catalogue_case,
    create_catalogue_section_table,
    create_iitpave_structural_input,
    create_iitpave_load_input,
    create_screening_summary
)


SUPPORTED_ALTERNATIVE_NUMBER = 3
SUPPORTED_EFFECTIVE_CBR = 10


def render_pavement_design(design_inputs):
    """
    Render the currently verified IRC catalogue-screening case
    and prepare IITPAVE structural/load input tables.

    Returns the pavement-screening results when the current
    design traffic is within the supported range.

    Returns None when catalogue screening is not applicable.
    """

    st.header(
        "5. IRC Catalogue Screening and "
        "IITPAVE Input Preparation"
    )

    st.write(
        "Screen the calculated design traffic against the currently "
        "implemented verified IRC catalogue case and prepare "
        "structural and loading inputs for subsequent IITPAVE analysis."
    )

    st.caption(
        "Current verified implementation: Alternative 3, effective "
        "CBR = 10%, IRC:37-2018 Figure 12.22 / Plate-22 / "
        "Annex III Table III.3."
    )

    # ========================================================
    # GET CURRENT DESIGN TRAFFIC
    # ========================================================

    design_traffic_msa = design_inputs["design_traffic_msa"]

    # ========================================================
    # CATALOGUE APPLICABILITY CHECK
    # ========================================================

    try:

        catalogue_traffic_level = select_catalogue_traffic_level(
            design_traffic_msa
        )

    except ValueError as error:

        st.subheader("Catalogue Applicability Check")

        applicability_col1, applicability_col2, applicability_col3 = (
            st.columns(3)
        )

        applicability_col1.metric(
            "Calculated Design Traffic",
            f"{design_traffic_msa:.2f} MSA"
        )

        applicability_col2.metric(
            "Supported Effective CBR",
            f"{SUPPORTED_EFFECTIVE_CBR}%"
        )

        applicability_col3.metric(
            "Verified Pavement Alternative",
            f"Alternative {SUPPORTED_ALTERNATIVE_NUMBER}"
        )

        st.error(str(error))

        st.warning(
            "No verified IRC catalogue section is generated for "
            "the current design traffic. Modify the design inputs "
            "to obtain a design traffic within the currently "
            "supported catalogue-screening range."
        )

        st.divider()

        return None

    # ========================================================
    # GET VERIFIED CATALOGUE CASE
    # ========================================================

    try:

        catalogue_case = get_verified_catalogue_case(
            alternative_number=SUPPORTED_ALTERNATIVE_NUMBER,
            effective_cbr=SUPPORTED_EFFECTIVE_CBR,
            catalogue_traffic_level=catalogue_traffic_level
        )

    except ValueError as error:

        st.error(str(error))

        st.divider()

        return None

    # ========================================================
    # CALCULATE SUBGRADE MODULUS
    # ========================================================

    subgrade_modulus = calculate_subgrade_modulus(
        SUPPORTED_EFFECTIVE_CBR
    )

    # ========================================================
    # CREATE OUTPUT TABLES
    # ========================================================

    catalogue_section_table = create_catalogue_section_table(
        catalogue_case
    )

    iitpave_structural_input = create_iitpave_structural_input(
        catalogue_case=catalogue_case,
        subgrade_modulus=subgrade_modulus
    )

    iitpave_load_input = create_iitpave_load_input()

    screening_summary = create_screening_summary(
        design_traffic_msa=design_traffic_msa,
        catalogue_traffic_level=catalogue_traffic_level,
        effective_cbr=SUPPORTED_EFFECTIVE_CBR,
        subgrade_modulus=subgrade_modulus,
        catalogue_case=catalogue_case
    )

    screening_summary_df = pd.DataFrame(
        [screening_summary]
    )

    # ========================================================
    # APPLICABILITY STATUS
    # ========================================================

    st.subheader("Catalogue Applicability Check")

    applicability_col1, applicability_col2, applicability_col3 = (
        st.columns(3)
    )

    applicability_col1.metric(
        "Calculated Design Traffic",
        f"{design_traffic_msa:.2f} MSA"
    )

    applicability_col2.metric(
        "Supported Effective CBR",
        f"{SUPPORTED_EFFECTIVE_CBR}%"
    )

    applicability_col3.metric(
        "Verified Pavement Alternative",
        f"Alternative {SUPPORTED_ALTERNATIVE_NUMBER}"
    )

    st.success(
        "The current design traffic is within the traffic range "
        "supported by the project's verified catalogue implementation."
    )

    # ========================================================
    # SCREENING RESULTS
    # ========================================================

    st.subheader("Catalogue Screening Results")

    screening_col1, screening_col2, screening_col3, screening_col4 = (
        st.columns(4)
    )

    screening_col1.metric(
        "Calculated Traffic",
        f"{design_traffic_msa:.2f} MSA"
    )

    screening_col2.metric(
        "Catalogue Traffic Level",
        f"{catalogue_traffic_level} MSA"
    )

    screening_col3.metric(
        "Effective CBR",
        f"{SUPPORTED_EFFECTIVE_CBR}%"
    )

    screening_col4.metric(
        "Subgrade Modulus",
        f"{subgrade_modulus:.2f} MPa"
    )

    # ========================================================
    # VERIFIED IRC REFERENCE
    # ========================================================

    st.subheader("Verified IRC Catalogue Reference")

    reference_col1, reference_col2, reference_col3 = (
        st.columns(3)
    )

    reference_col1.metric(
        "IRC Figure",
        catalogue_case["figure"]
    )

    reference_col2.metric(
        "IRC Plate",
        catalogue_case["plate"]
    )

    reference_col3.metric(
        "Annex Table",
        catalogue_case["annex_table"]
    )

    # ========================================================
    # PAVEMENT COMPOSITION
    # ========================================================

    st.subheader("Screened Pavement Composition")

    st.info(
        "Bituminous Surface + Cement Treated Base (CTB) + "
        "Cement Treated Sub-base (CTSB) + SAMI + Subgrade"
    )

    st.dataframe(
        catalogue_section_table,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # THICKNESS SUMMARY
    # ========================================================

    st.subheader("Verified Structural Thickness Summary")

    thickness_col1, thickness_col2, thickness_col3 = (
        st.columns(3)
    )

    thickness_col1.metric(
        "Total Bituminous Layer",
        f"{catalogue_case['total_bituminous_mm']} mm"
    )

    thickness_col2.metric(
        "CTB Thickness",
        f"{catalogue_case['ctb_mm']} mm"
    )

    thickness_col3.metric(
        "CTSB Thickness",
        f"{catalogue_case['ctsb_mm']} mm"
    )

    # ========================================================
    # IITPAVE STRUCTURAL INPUT
    # ========================================================

    st.subheader("IITPAVE Structural Input Preparation")

    st.write(
        "The following table contains the structural-layer "
        "thicknesses, elastic/resilient moduli, and Poisson's "
        "ratios for subsequent IITPAVE analysis."
    )

    st.dataframe(
        iitpave_structural_input,
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "SAMI is a crack-relief treatment and is excluded from "
        "the IITPAVE structural-layer input."
    )

    # ========================================================
    # IITPAVE LOAD INPUT
    # ========================================================

    st.subheader("IITPAVE Standard Axle Load Input")

    st.dataframe(
        iitpave_load_input,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # SCREENING SUMMARY
    # ========================================================

    st.subheader("Pavement Screening Summary")

    st.dataframe(
        screening_summary_df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # ENGINEERING INTERPRETATION
    # ========================================================

    st.subheader("Engineering Interpretation")

    st.success(
        f"The calculated design traffic of "
        f"{design_traffic_msa:.2f} MSA is screened at the next "
        f"supported catalogue traffic level of "
        f"{catalogue_traffic_level} MSA. For Alternative "
        f"{SUPPORTED_ALTERNATIVE_NUMBER} with effective CBR = "
        f"{SUPPORTED_EFFECTIVE_CBR}%, the preliminary pavement "
        f"section consists of "
        f"{catalogue_case['total_bituminous_mm']} mm total "
        f"bituminous layer, {catalogue_case['ctb_mm']} mm CTB, "
        f"and {catalogue_case['ctsb_mm']} mm CTSB."
    )

    st.warning(
        "This result is a preliminary IRC catalogue-screening "
        "output. Site-specific material properties, "
        "mechanistic-empirical response analysis, performance "
        "checks, and iteration in IITPAVE are required."
    )

    # ========================================================
    # DOWNLOADS
    # ========================================================

    st.subheader("Download Pavement Screening Results")

    screening_csv = (
        screening_summary_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    catalogue_csv = (
        catalogue_section_table
        .to_csv(index=False)
        .encode("utf-8")
    )

    structural_csv = (
        iitpave_structural_input
        .to_csv(index=False)
        .encode("utf-8")
    )

    load_csv = (
        iitpave_load_input
        .to_csv(index=False)
        .encode("utf-8")
    )

    download_row1_col1, download_row1_col2 = st.columns(2)

    with download_row1_col1:

        st.download_button(
            label="Download Screening Summary",
            data=screening_csv,
            file_name="pavement_catalogue_screening_summary.csv",
            mime="text/csv",
            key="pavement_download_screening"
        )

    with download_row1_col2:

        st.download_button(
            label="Download IRC Catalogue Section",
            data=catalogue_csv,
            file_name="verified_irc_catalogue_section.csv",
            mime="text/csv",
            key="pavement_download_catalogue"
        )

    download_row2_col1, download_row2_col2 = st.columns(2)

    with download_row2_col1:

        st.download_button(
            label="Download IITPAVE Structural Input",
            data=structural_csv,
            file_name="iitpave_structural_input_summary.csv",
            mime="text/csv",
            key="pavement_download_structural"
        )

    with download_row2_col2:

        st.download_button(
            label="Download IITPAVE Load Input",
            data=load_csv,
            file_name="iitpave_load_input_summary.csv",
            mime="text/csv",
            key="pavement_download_load"
        )

    st.divider()

    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {
        "catalogue_traffic_level": catalogue_traffic_level,
        "subgrade_modulus": subgrade_modulus,
        "catalogue_case": catalogue_case,
        "catalogue_section_table": catalogue_section_table,
        "iitpave_structural_input": iitpave_structural_input,
        "iitpave_load_input": iitpave_load_input,
        "screening_summary": screening_summary,
        "screening_summary_df": screening_summary_df
    }
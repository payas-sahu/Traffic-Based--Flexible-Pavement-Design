import pandas as pd
import streamlit as st

from design_traffic import calculate_design_traffic


def render_design_traffic(average_cvpd):
    """
    Render interactive IRC:37 design-traffic inputs and results.

    Returns the current design inputs and calculated results so
    downstream dashboard sections can reuse them.
    """

    st.header("3. IRC:37 Design Traffic Calculation")

    st.write(
        "Estimate cumulative design traffic using the commercial "
        "traffic obtained from the classified traffic dataset."
    )

    # ========================================================
    # DESIGN INPUTS
    # ========================================================

    st.subheader("Design Parameters")

    input_col1, input_col2, input_col3 = st.columns(3)

    with input_col1:

        growth_rate_percent = st.number_input(
            "Annual Traffic Growth Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5,
            key="design_growth_rate"
        )

        design_period = st.number_input(
            "Design Period (Years)",
            min_value=1,
            max_value=50,
            value=20,
            step=1,
            key="design_period"
        )

    with input_col2:

        years_to_completion = st.number_input(
            "Years Between Traffic Count and Road Opening",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=0.5,
            key="years_to_completion"
        )

        vdf = st.number_input(
            "Vehicle Damage Factor (VDF)",
            min_value=0.1,
            max_value=20.0,
            value=3.0,
            step=0.1,
            key="design_vdf"
        )

    with input_col3:

        distribution_factor = st.number_input(
            "Lateral Distribution Factor (D)",
            min_value=0.01,
            max_value=1.0,
            value=0.50,
            step=0.05,
            key="distribution_factor"
        )

    # ========================================================
    # CALCULATE DESIGN TRAFFIC
    # ========================================================

    growth_rate = growth_rate_percent / 100

    try:

        design_results = calculate_design_traffic(
            traffic_at_last_count=average_cvpd,
            growth_rate=growth_rate,
            design_period=int(design_period),
            years_to_completion=years_to_completion,
            vdf=vdf,
            distribution_factor=distribution_factor
        )

    except Exception as error:

        st.error(
            f"Design traffic calculation failed: {error}"
        )

        st.stop()

    # ========================================================
    # EXTRACT RESULTS
    # ========================================================

    traffic_at_last_count = (
        design_results["traffic_at_last_count"]
    )

    opening_traffic = (
        design_results["opening_traffic"]
    )

    growth_factor = (
        design_results["growth_factor"]
    )

    cumulative_standard_axles = (
        design_results["cumulative_standard_axles"]
    )

    design_traffic_msa = (
        design_results["design_traffic_msa"]
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    st.subheader("Design Traffic Results")

    result_col1, result_col2, result_col3, result_col4 = (
        st.columns(4)
    )

    result_col1.metric(
        "Traffic at Last Count (P)",
        f"{traffic_at_last_count:,.2f} CVPD"
    )

    result_col2.metric(
        "Traffic at Road Opening (A)",
        f"{opening_traffic:,.2f} CVPD"
    )

    result_col3.metric(
        "Growth Factor",
        f"{growth_factor:,.4f}"
    )

    result_col4.metric(
        "Design Traffic",
        f"{design_traffic_msa:,.2f} MSA"
    )

    # ========================================================
    # CALCULATION SUMMARY
    # ========================================================

    st.subheader("Calculation Summary")

    design_summary_df = pd.DataFrame(
        {
            "Parameter": [
                "Commercial Traffic at Last Count (P)",
                "Annual Traffic Growth Rate",
                "Years to Road Opening",
                "Traffic at Road Opening (A)",
                "Design Period",
                "Vehicle Damage Factor (VDF)",
                "Lateral Distribution Factor (D)",
                "Cumulative Growth Factor",
                "Cumulative Standard Axles",
                "Design Traffic"
            ],

            "Value": [
                traffic_at_last_count,
                growth_rate_percent,
                years_to_completion,
                opening_traffic,
                int(design_period),
                vdf,
                distribution_factor,
                growth_factor,
                cumulative_standard_axles,
                design_traffic_msa
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
        }
    )

    st.dataframe(
        design_summary_df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # ENGINEERING INTERPRETATION
    # ========================================================

    st.subheader("Engineering Interpretation")

    if design_traffic_msa <= 5:

        traffic_category = "Low Design Traffic"

    elif design_traffic_msa <= 20:

        traffic_category = "Moderate Design Traffic"

    elif design_traffic_msa <= 50:

        traffic_category = "High Design Traffic"

    else:

        traffic_category = "Design Traffic Above Catalogue Range"

    st.info(
        f"The current input assumptions produce a cumulative "
        f"design traffic of **{design_traffic_msa:.2f} MSA**. "
        f"For dashboard interpretation, this is classified as "
        f"**{traffic_category}**."
    )

    if design_traffic_msa > 50:

        st.warning(
            "The calculated design traffic exceeds the range "
            "supported by the project's current verified IRC "
            "catalogue-screening implementation."
        )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    design_summary_csv = (
        design_summary_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="Download Design Traffic Summary",
        data=design_summary_csv,
        file_name="design_traffic_summary.csv",
        mime="text/csv",
        key="design_traffic_download"
    )

    st.divider()

    # ========================================================
    # RETURN RESULTS FOR STAGES 4 AND 5
    # ========================================================

    return {
        "growth_rate_percent": growth_rate_percent,
        "growth_rate": growth_rate,
        "design_period": int(design_period),
        "years_to_completion": years_to_completion,
        "vdf": vdf,
        "distribution_factor": distribution_factor,
        "design_results": design_results,
        "design_traffic_msa": design_traffic_msa,
        "design_summary_df": design_summary_df
    }
import streamlit as st

from sensitivity_analysis import (
    run_sensitivity_analysis,
    calculate_parameter_influence
)


def render_sensitivity_analysis(
    average_cvpd,
    design_inputs
):
    """
    Render dynamic sensitivity analysis using the current
    design-traffic inputs.

    Returns the sensitivity results and parameter influence ranking.
    """

    st.header("4. Interactive Sensitivity Analysis")

    st.write(
        "Evaluate how changes in growth rate, Vehicle Damage Factor "
        "(VDF), design period, and years to road opening affect "
        "cumulative design traffic."
    )

    st.caption(
        "The scenario ranges are generated around the current "
        "design inputs. The influence ranking is range-based and "
        "is not a formal global sensitivity analysis."
    )

    # ========================================================
    # EXTRACT CURRENT DESIGN INPUTS
    # ========================================================

    growth_rate = design_inputs["growth_rate"]
    design_period = design_inputs["design_period"]

    years_to_completion = (
        design_inputs["years_to_completion"]
    )

    vdf = design_inputs["vdf"]

    distribution_factor = (
        design_inputs["distribution_factor"]
    )

    # ========================================================
    # RUN SENSITIVITY ANALYSIS
    # ========================================================

    try:

        sensitivity_results = run_sensitivity_analysis(
            average_cvpd=average_cvpd,
            growth_rate=growth_rate,
            design_period=design_period,
            years_to_completion=years_to_completion,
            vdf=vdf,
            distribution_factor=distribution_factor
        )

        influence_results = calculate_parameter_influence(
            sensitivity_results
        )

    except Exception as error:

        st.error(
            f"Sensitivity analysis failed: {error}"
        )

        st.stop()

    # ========================================================
    # BASELINE RESULTS
    # ========================================================

    baseline_msa = (
        sensitivity_results["baseline"]["design_traffic_msa"]
    )

    st.subheader("Current Baseline Design Case")

    baseline_col1, baseline_col2, baseline_col3 = (
        st.columns(3)
    )

    baseline_col1.metric(
        "Baseline Design Traffic",
        f"{baseline_msa:.2f} MSA"
    )

    baseline_col2.metric(
        "Highest-Ranked Parameter",
        influence_results.iloc[0]["Parameter"]
    )

    baseline_col3.metric(
        "Influence Range",
        f"{influence_results.iloc[0]['Percentage_Range_of_Baseline']:.2f}%"
    )

    # ========================================================
    # HELPER FUNCTION
    # ========================================================

    def display_sensitivity_analysis(
        title,
        dataframe,
        x_column,
        x_label,
        download_file_name,
        download_key
    ):

        st.subheader(title)

        chart_data = (
            dataframe
            .set_index(x_column)["Design_Traffic_MSA"]
        )

        st.line_chart(
            chart_data,
            use_container_width=True
        )

        baseline_rows = dataframe[
            dataframe["Is_Baseline"]
        ]

        if not baseline_rows.empty:

            baseline_x = baseline_rows.iloc[0][x_column]

            baseline_y = (
                baseline_rows.iloc[0]["Design_Traffic_MSA"]
            )

            st.info(
                f"Current baseline: {x_label} = {baseline_x}, "
                f"Design Traffic = {baseline_y:.2f} MSA."
            )

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

        csv_data = (
            dataframe
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            label=f"Download {title} Results",
            data=csv_data,
            file_name=download_file_name,
            mime="text/csv",
            key=download_key
        )

    # ========================================================
    # GROWTH RATE SENSITIVITY
    # ========================================================

    display_sensitivity_analysis(
        title="Growth Rate Sensitivity",
        dataframe=sensitivity_results["growth_rate"],
        x_column="Growth_Rate_Percent",
        x_label="Annual Traffic Growth Rate (%)",
        download_file_name="growth_rate_sensitivity.csv",
        download_key="sensitivity_download_growth"
    )

    # ========================================================
    # VDF SENSITIVITY
    # ========================================================

    display_sensitivity_analysis(
        title="VDF Sensitivity",
        dataframe=sensitivity_results["vdf"],
        x_column="VDF",
        x_label="Vehicle Damage Factor (VDF)",
        download_file_name="vdf_sensitivity.csv",
        download_key="sensitivity_download_vdf"
    )

    # ========================================================
    # DESIGN PERIOD SENSITIVITY
    # ========================================================

    display_sensitivity_analysis(
        title="Design Period Sensitivity",
        dataframe=sensitivity_results["design_period"],
        x_column="Design_Period_Years",
        x_label="Design Period (Years)",
        download_file_name="design_period_sensitivity.csv",
        download_key="sensitivity_download_period"
    )

    # ========================================================
    # ROAD-OPENING SENSITIVITY
    # ========================================================

    display_sensitivity_analysis(
        title="Years to Road Opening Sensitivity",
        dataframe=sensitivity_results["construction_delay"],
        x_column="Years_To_Completion",
        x_label="Years Between Traffic Count and Road Opening",
        download_file_name="construction_delay_sensitivity.csv",
        download_key="sensitivity_download_delay"
    )

    # ========================================================
    # PARAMETER INFLUENCE RANKING
    # ========================================================

    st.subheader("Parameter Influence Ranking")

    st.dataframe(
        influence_results.round(2),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # ENGINEERING INTERPRETATION
    # ========================================================

    most_influential_parameter = (
        influence_results.iloc[0]["Parameter"]
    )

    highest_influence_range = (
        influence_results
        .iloc[0]["Percentage_Range_of_Baseline"]
    )

    lowest_influence_parameter = (
        influence_results.iloc[-1]["Parameter"]
    )

    st.subheader("Sensitivity Interpretation")

    st.info(
        f"Within the scenario ranges generated around the current "
        f"design inputs, **{most_influential_parameter}** produces "
        f"the largest MSA variation, equal to "
        f"**{highest_influence_range:.2f}% of the baseline MSA**. "
        f"The lowest-ranked parameter within the tested ranges is "
        f"**{lowest_influence_parameter}**."
    )

    st.warning(
        "The ranking depends on the scenario ranges used for each "
        "parameter. It should not be interpreted as proving that "
        "one parameter is universally more important than another."
    )

    # ========================================================
    # DOWNLOAD INFLUENCE RANKING
    # ========================================================

    influence_csv = (
        influence_results
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="Download Parameter Influence Ranking",
        data=influence_csv,
        file_name="parameter_influence_ranking.csv",
        mime="text/csv",
        key="sensitivity_download_influence"
    )

    st.divider()

    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {
        "sensitivity_results": sensitivity_results,
        "influence_results": influence_results,
        "baseline_msa": baseline_msa
    }
import pandas as pd
import streamlit as st

from scenario_analysis import (
    compare_scenarios,
    create_compact_comparison_table,
    create_scenario_summary
)


def render_scenario_comparison(
    average_cvpd,
    design_inputs
):
    """
    Render interactive multi-scenario comparison.

    The current Stage 3 design case is used as the baseline.
    Users can compare alternative assumptions against it.
    """

    st.header("6. Scenario Comparison")

    st.write(
        "Compare multiple traffic and pavement-design assumptions "
        "against the current Stage 3 baseline case."
    )

    st.caption(
        "Each scenario independently recalculates design traffic "
        "and performs catalogue screening when the result falls "
        "within the currently verified implementation range."
    )

    # ========================================================
    # CURRENT BASELINE
    # ========================================================

    baseline_scenario = {
        "scenario_name": "Current Baseline",
        "growth_rate": design_inputs["growth_rate"],
        "design_period": design_inputs["design_period"],
        "years_to_completion":
            design_inputs["years_to_completion"],
        "vdf": design_inputs["vdf"],
        "distribution_factor":
            design_inputs["distribution_factor"]
    }

    st.subheader("Current Baseline Scenario")

    baseline_col1, baseline_col2, baseline_col3 = st.columns(3)

    baseline_col1.metric(
        "Design Traffic",
        f"{design_inputs['design_traffic_msa']:.2f} MSA"
    )

    baseline_col2.metric(
        "Growth Rate",
        f"{design_inputs['growth_rate_percent']:.2f}%"
    )

    baseline_col3.metric(
        "Design Period",
        f"{design_inputs['design_period']} Years"
    )

    # ========================================================
    # SCENARIO CONTROLS
    # ========================================================

    st.subheader("Alternative Scenario Inputs")

    number_of_alternatives = st.number_input(
        "Number of Alternative Scenarios",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
        key="scenario_number_of_alternatives"
    )

    alternative_scenarios = []

    for index in range(int(number_of_alternatives)):

        scenario_number = index + 1

        with st.expander(
            f"Alternative Scenario {scenario_number}",
            expanded=(index == 0)
        ):

            scenario_name = st.text_input(
                "Scenario Name",
                value=f"Alternative {scenario_number}",
                key=f"scenario_name_{index}"
            )

            input_col1, input_col2, input_col3 = st.columns(3)

            with input_col1:

                growth_rate_percent = st.number_input(
                    "Annual Growth Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=min(
                        20.0,
                        float(
                            design_inputs[
                                "growth_rate_percent"
                            ]
                        ) + scenario_number
                    ),
                    step=0.5,
                    key=f"scenario_growth_rate_{index}"
                )

                design_period = st.number_input(
                    "Design Period (Years)",
                    min_value=1,
                    max_value=50,
                    value=int(
                        design_inputs["design_period"]
                    ),
                    step=1,
                    key=f"scenario_design_period_{index}"
                )

            with input_col2:

                years_to_completion = st.number_input(
                    "Years to Road Opening",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(
                        design_inputs[
                            "years_to_completion"
                        ]
                    ),
                    step=0.5,
                    key=f"scenario_opening_years_{index}"
                )

                vdf = st.number_input(
                    "Vehicle Damage Factor (VDF)",
                    min_value=0.1,
                    max_value=20.0,
                    value=float(
                        design_inputs["vdf"]
                    ),
                    step=0.1,
                    key=f"scenario_vdf_{index}"
                )

            with input_col3:

                distribution_factor = st.number_input(
                    "Lateral Distribution Factor (D)",
                    min_value=0.01,
                    max_value=1.0,
                    value=float(
                        design_inputs[
                            "distribution_factor"
                        ]
                    ),
                    step=0.05,
                    key=f"scenario_distribution_{index}"
                )

            alternative_scenarios.append(
                {
                    "scenario_name": scenario_name,
                    "growth_rate":
                        growth_rate_percent / 100,
                    "design_period":
                        int(design_period),
                    "years_to_completion":
                        years_to_completion,
                    "vdf":
                        vdf,
                    "distribution_factor":
                        distribution_factor
                }
            )

    # ========================================================
    # RUN COMPARISON
    # ========================================================

    scenarios = [
        baseline_scenario,
        *alternative_scenarios
    ]

    try:

        comparison_df = compare_scenarios(
            scenarios=scenarios,
            average_cvpd=average_cvpd,
            baseline_scenario_name="Current Baseline"
        )

        compact_comparison_df = (
            create_compact_comparison_table(
                comparison_df
            )
        )

        scenario_summary = create_scenario_summary(
            comparison_df
        )

    except Exception as error:

        st.error(
            f"Scenario comparison failed: {error}"
        )

        return None

    # ========================================================
    # COMPARISON SUMMARY
    # ========================================================

    st.subheader("Scenario Comparison Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = (
        st.columns(4)
    )

    summary_col1.metric(
        "Scenarios Compared",
        scenario_summary["number_of_scenarios"]
    )

    summary_col2.metric(
        "Baseline MSA",
        f"{scenario_summary['baseline_msa']:.2f}"
    )

    summary_col3.metric(
        "Highest Traffic Scenario",
        scenario_summary["highest_traffic_scenario"]
    )

    summary_col4.metric(
        "Traffic Range",
        f"{scenario_summary['design_traffic_range_msa']:.2f} MSA"
    )

    # ========================================================
    # DESIGN TRAFFIC COMPARISON CHART
    # ========================================================

    st.subheader("Design Traffic Comparison")

    msa_chart_data = (
        comparison_df
        .set_index("Scenario")[
            "Design_Traffic_MSA"
        ]
    )

    st.bar_chart(
        msa_chart_data,
        use_container_width=True
    )

    # ========================================================
    # PERCENT CHANGE CHART
    # ========================================================

    st.subheader("Percentage Change from Baseline")

    percentage_chart_data = (
        comparison_df
        .set_index("Scenario")[
            "Percent_Change_From_Baseline"
        ]
    )

    st.bar_chart(
        percentage_chart_data,
        use_container_width=True
    )

    # ========================================================
    # COMPACT COMPARISON TABLE
    # ========================================================

    st.subheader("Scenario Comparison Table")

    st.dataframe(
        compact_comparison_df.round(2),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # CATALOGUE SCREENING STATUS
    # ========================================================

    st.subheader("Catalogue Screening Comparison")

    catalogue_columns = [
        "Scenario",
        "Design_Traffic_MSA",
        "Catalogue_Status",
        "Catalogue_Traffic_Level_MSA",
        "Total_Bituminous_mm",
        "CTB_mm",
        "CTSB_mm"
    ]

    catalogue_comparison_df = (
        comparison_df[
            catalogue_columns
        ].copy()
    )

    st.dataframe(
        catalogue_comparison_df.round(2),
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # ENGINEERING INTERPRETATION
    # ========================================================

    st.subheader("Scenario Interpretation")

    st.info(
        f"The baseline scenario produces "
        f"**{scenario_summary['baseline_msa']:.2f} MSA**. "
        f"The highest design traffic occurs in "
        f"**{scenario_summary['highest_traffic_scenario']}** "
        f"with "
        f"**{scenario_summary['highest_design_traffic_msa']:.2f} "
        f"MSA**, while the lowest occurs in "
        f"**{scenario_summary['lowest_traffic_scenario']}** "
        f"with "
        f"**{scenario_summary['lowest_design_traffic_msa']:.2f} "
        f"MSA**."
    )

    if scenario_summary["unsupported_catalogue_cases"] > 0:

        st.warning(
            f"{scenario_summary['unsupported_catalogue_cases']} "
            f"scenario(s) fall outside the currently verified "
            f"catalogue-screening implementation. Their design "
            f"traffic is still calculated, but no verified "
            f"pavement section is assigned."
        )

    else:

        st.success(
            "All compared scenarios fall within the currently "
            "verified catalogue-screening implementation."
        )

    st.caption(
        "Scenario results are comparative decision-support outputs. "
        "They do not replace site-specific pavement design, "
        "mechanistic-empirical verification, or engineering judgment."
    )

    # ========================================================
    # DOWNLOADS
    # ========================================================

    st.subheader("Download Scenario Comparison Results")

    full_comparison_csv = (
        comparison_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    compact_comparison_csv = (
        compact_comparison_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    download_col1, download_col2 = st.columns(2)

    with download_col1:

        st.download_button(
            label="Download Full Scenario Results",
            data=full_comparison_csv,
            file_name="scenario_comparison_full.csv",
            mime="text/csv",
            key="scenario_download_full"
        )

    with download_col2:

        st.download_button(
            label="Download Compact Comparison",
            data=compact_comparison_csv,
            file_name="scenario_comparison_compact.csv",
            mime="text/csv",
            key="scenario_download_compact"
        )

    st.divider()

    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {
        "comparison_df": comparison_df,
        "compact_comparison_df": compact_comparison_df,
        "scenario_summary": scenario_summary
    }
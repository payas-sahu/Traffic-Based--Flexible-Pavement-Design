import streamlit as st

from report_generator import generate_engineering_report


def render_report_generator(
    df,
    data_source_name,
    average_cvpd,
    validation_results,
    design_inputs,
    sensitivity_outputs,
    pavement_outputs,
    scenario_outputs
):
    """
    Render the Stage 7 engineering-report interface and generate
    a PDF report from the live results produced by Stages 1–6.
    """

    st.header("7. Automatic Engineering Report Generation")

    st.write(
        "Generate a downloadable PDF engineering report containing "
        "the current traffic analysis, design-traffic calculation, "
        "sensitivity results, pavement catalogue screening, "
        "IITPAVE input preparation, scenario comparison, "
        "engineering limitations, and references."
    )

    st.caption(
        "The report uses the current live dashboard results. "
        "Change the design inputs or scenario assumptions before "
        "generating the report if you want those changes reflected "
        "in the PDF."
    )

    # ========================================================
    # REPORT CONTENT STATUS
    # ========================================================

    st.subheader("Report Content Status")

    status_col1, status_col2, status_col3, status_col4 = (
        st.columns(4)
    )

    status_col1.metric(
        "Traffic Dataset",
        "Available" if df is not None else "Unavailable"
    )

    status_col2.metric(
        "Sensitivity Results",
        "Available"
        if sensitivity_outputs is not None
        else "Unavailable"
    )

    status_col3.metric(
        "Pavement Screening",
        "Available"
        if pavement_outputs is not None
        else "Unavailable"
    )

    status_col4.metric(
        "Scenario Comparison",
        "Available"
        if scenario_outputs is not None
        else "Unavailable"
    )

    # ========================================================
    # REPORT SUMMARY
    # ========================================================

    st.subheader("Current Report Case")

    summary_col1, summary_col2, summary_col3 = (
        st.columns(3)
    )

    summary_col1.metric(
        "Average Commercial Traffic",
        f"{average_cvpd:,.2f} CVPD"
    )

    summary_col2.metric(
        "Design Traffic",
        f"{design_inputs['design_traffic_msa']:.2f} MSA"
    )

    if pavement_outputs is not None:

        catalogue_level = (
            pavement_outputs["catalogue_traffic_level"]
        )

        summary_col3.metric(
            "Catalogue Traffic Level",
            f"{catalogue_level} MSA"
        )

    else:

        summary_col3.metric(
            "Catalogue Traffic Level",
            "Not Available"
        )

    # ========================================================
    # GENERATE REPORT
    # ========================================================

    st.subheader("Generate PDF Report")

    st.info(
        "Click the button below to generate the report from the "
        "current dashboard inputs and analysis results."
    )

    if st.button(
        "Generate Engineering PDF Report",
        type="primary",
        key="report_generate_button"
    ):

        try:

            with st.spinner(
                "Generating engineering report..."
            ):

                pdf_bytes = generate_engineering_report(
                    df=df,
                    data_source_name=data_source_name,
                    average_cvpd=average_cvpd,
                    validation_results=validation_results,
                    design_inputs=design_inputs,
                    sensitivity_outputs=sensitivity_outputs,
                    pavement_outputs=pavement_outputs,
                    scenario_outputs=scenario_outputs
                )

                st.session_state[
                    "engineering_report_pdf"
                ] = pdf_bytes

            st.success(
                "Engineering PDF report generated successfully."
            )

        except Exception as error:

            st.session_state.pop(
                "engineering_report_pdf",
                None
            )

            st.error(
                f"PDF report generation failed: {error}"
            )

    # ========================================================
    # DOWNLOAD GENERATED REPORT
    # ========================================================

    if "engineering_report_pdf" in st.session_state:

        st.download_button(
            label="Download Engineering PDF Report",
            data=st.session_state[
                "engineering_report_pdf"
            ],
            file_name=(
                "traffic_based_flexible_pavement_"
                "engineering_report.pdf"
            ),
            mime="application/pdf",
            key="report_download_button"
        )

        st.caption(
            "If you change any Stage 3 or Stage 6 inputs, click "
            "'Generate Engineering PDF Report' again before "
            "downloading so the PDF contains the latest results."
        )

    # ========================================================
    # ENGINEERING NOTE
    # ========================================================

    st.subheader("Report Use and Limitations")

    st.warning(
        "The generated report is a decision-support document. "
        "Catalogue screening and IITPAVE input preparation do not "
        "constitute final pavement design approval. Project-specific "
        "investigation, material characterization, mechanistic-"
        "empirical analysis, performance verification, and "
        "engineering judgment are required."
    )

    st.divider()
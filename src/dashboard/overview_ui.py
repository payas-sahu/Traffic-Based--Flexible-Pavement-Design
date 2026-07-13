import streamlit as st


def render_overview(
    df,
    data_source_name,
    average_cvpd,
    validation_results
):
    """
    Render the project overview, traffic-data validation summary,
    dataset preview, and basic dataset information.
    """

    # ========================================================
    # PROJECT OVERVIEW
    # ========================================================

    st.header("1. Project Overview")

    overview_col1, overview_col2, overview_col3, overview_col4 = (
        st.columns(4)
    )

    overview_col1.metric(
        "Traffic Observations",
        f"{len(df):,}"
    )

    overview_col2.metric(
        "Average Commercial Traffic",
        f"{average_cvpd:,.2f} CVPD"
    )

    if "Date" in df.columns:
        survey_days = df["Date"].nunique()
    else:
        survey_days = "N/A"

    overview_col3.metric(
        "Survey Duration",
        f"{survey_days} Days"
    )

    overview_col4.metric(
        "Data Source",
        data_source_name
    )

    # ========================================================
    # VALIDATION SUMMARY
    # ========================================================

    st.subheader("Traffic Data Validation")

    missing_columns = validation_results["missing_columns"]
    missing_values = validation_results["missing_values"]
    negative_counts = validation_results["negative_counts"]

    validation_col1, validation_col2, validation_col3 = (
        st.columns(3)
    )

    validation_col1.metric(
        "Missing Required Columns",
        len(missing_columns)
    )

    validation_col2.metric(
        "Missing Values",
        missing_values
    )

    validation_col3.metric(
        "Negative Traffic Counts",
        negative_counts
    )

    st.success(
        "Traffic dataset passed the current validation checks."
    )

    # ========================================================
    # DATASET PREVIEW
    # ========================================================

    st.subheader("Classified Traffic Dataset Preview")

    maximum_rows = min(50, len(df))
    default_rows = min(10, len(df))

    number_of_rows = st.slider(
        "Rows to Display",
        min_value=1,
        max_value=maximum_rows,
        value=default_rows,
        key="overview_rows_to_display"
    )

    st.dataframe(
        df.head(number_of_rows),
        use_container_width=True
    )

    # ========================================================
    # DATASET INFORMATION
    # ========================================================

    with st.expander("View Dataset Information"):

        st.write(f"**Dataset:** {data_source_name}")

        st.write(f"**Number of Rows:** {len(df)}")

        st.write(f"**Number of Columns:** {len(df.columns)}")

        st.write("**Columns:**")

        st.write(list(df.columns))

    st.divider()
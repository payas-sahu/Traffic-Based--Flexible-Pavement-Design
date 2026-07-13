import pandas as pd
import streamlit as st


VEHICLE_COLUMNS = [
    "Two_Wheeler",
    "Car",
    "LCV",
    "Bus",
    "Two_Axle_Truck",
    "Three_Axle_Truck",
    "MAV"
]

COMMERCIAL_VEHICLE_COLUMNS = [
    "LCV",
    "Bus",
    "Two_Axle_Truck",
    "Three_Axle_Truck",
    "MAV"
]


def render_traffic_analytics(df):
    """
    Render traffic summary metrics, vehicle composition,
    hourly/daily variation, directional analysis, vehicle-class
    explorer, and CSV downloads.

    Returns a dictionary containing useful traffic-analysis results.
    """

    st.header("2. Interactive Traffic Analytics")

    # ========================================================
    # SAFETY CHECK
    # ========================================================

    missing_vehicle_columns = [
        column
        for column in VEHICLE_COLUMNS
        if column not in df.columns
    ]

    if missing_vehicle_columns:
        st.error(
            "Traffic analytics cannot continue because these "
            "vehicle columns are missing: "
            + ", ".join(missing_vehicle_columns)
        )
        st.stop()

    required_analysis_columns = ["Date", "Hour", "Direction"]

    missing_analysis_columns = [
        column
        for column in required_analysis_columns
        if column not in df.columns
    ]

    if missing_analysis_columns:
        st.error(
            "Traffic analytics cannot continue because these "
            "analysis columns are missing: "
            + ", ".join(missing_analysis_columns)
        )
        st.stop()

    # ========================================================
    # PREPARE DATA
    # ========================================================

    analysis_df = df.copy()

    analysis_df["Date"] = pd.to_datetime(
        analysis_df["Date"],
        errors="coerce"
    )

    analysis_df["Total_Commercial_Traffic"] = (
        analysis_df[COMMERCIAL_VEHICLE_COLUMNS].sum(axis=1)
    )

    if "Total_Traffic" not in analysis_df.columns:
        analysis_df["Total_Traffic"] = (
            analysis_df[VEHICLE_COLUMNS].sum(axis=1)
        )

    # ========================================================
    # SUMMARY CALCULATIONS
    # ========================================================

    total_traffic_volume = analysis_df["Total_Traffic"].sum()

    total_commercial_traffic = (
        analysis_df["Total_Commercial_Traffic"].sum()
    )

    if total_traffic_volume > 0:
        commercial_vehicle_share = (
            total_commercial_traffic
            / total_traffic_volume
            * 100
        )
    else:
        commercial_vehicle_share = 0.0

    daily_traffic = (
        analysis_df
        .groupby("Date")[
            ["Total_Traffic", "Total_Commercial_Traffic"]
        ]
        .sum()
        .sort_index()
    )

    average_daily_total_traffic = (
        daily_traffic["Total_Traffic"].mean()
    )

    hourly_analysis = (
        analysis_df
        .groupby("Hour")[
            ["Total_Traffic", "Total_Commercial_Traffic"]
        ]
        .sum()
        .sort_index()
    )

    peak_hour = hourly_analysis["Total_Traffic"].idxmax()

    peak_hour_traffic = hourly_analysis.loc[
        peak_hour,
        "Total_Traffic"
    ]

    directional_traffic = (
        analysis_df
        .groupby("Direction")["Total_Traffic"]
        .sum()
        .sort_values(ascending=False)
    )

    dominant_direction = directional_traffic.idxmax()

    dominant_direction_traffic = directional_traffic.max()

    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )

    metric_col1.metric(
        "Total Traffic Volume",
        f"{total_traffic_volume:,.0f} Vehicles"
    )

    metric_col2.metric(
        "Average Daily Traffic",
        f"{average_daily_total_traffic:,.0f} Vehicles/Day"
    )

    metric_col3.metric(
        "Commercial Vehicle Share",
        f"{commercial_vehicle_share:.2f}%"
    )

    metric_col4.metric(
        "Peak Hour",
        str(peak_hour)
    )

    # ========================================================
    # VEHICLE COMPOSITION
    # ========================================================

    st.subheader("Vehicle Composition")

    vehicle_composition = (
        analysis_df[VEHICLE_COLUMNS]
        .sum()
        .sort_values(ascending=False)
    )

    vehicle_composition_df = (
        vehicle_composition
        .rename("Traffic Volume")
        .reset_index()
        .rename(columns={"index": "Vehicle Class"})
    )

    vehicle_composition_df["Percentage Share"] = (
        vehicle_composition_df["Traffic Volume"]
        / vehicle_composition_df["Traffic Volume"].sum()
        * 100
    )

    vehicle_chart_col, vehicle_table_col = st.columns([2, 1])

    with vehicle_chart_col:
        st.bar_chart(
            vehicle_composition,
            use_container_width=True
        )

    with vehicle_table_col:
        st.dataframe(
            vehicle_composition_df,
            use_container_width=True,
            hide_index=True
        )

    # ========================================================
    # HOURLY VARIATION
    # ========================================================

    st.subheader("Hourly Traffic Variation")

    st.line_chart(
        hourly_analysis,
        use_container_width=True
    )

    st.info(
        f"Peak traffic occurs at {peak_hour}, with a cumulative "
        f"survey-period traffic volume of "
        f"{peak_hour_traffic:,.0f} vehicles for that hourly interval."
    )

    # ========================================================
    # DIRECTIONAL DISTRIBUTION
    # ========================================================

    st.subheader("Directional Traffic Distribution")

    directional_chart_col, directional_table_col = (
        st.columns([2, 1])
    )

    with directional_chart_col:
        st.bar_chart(
            directional_traffic,
            use_container_width=True
        )

    directional_df = (
        directional_traffic
        .rename("Traffic Volume")
        .reset_index()
    )

    directional_df["Percentage Share"] = (
        directional_df["Traffic Volume"]
        / directional_df["Traffic Volume"].sum()
        * 100
    )

    with directional_table_col:
        st.dataframe(
            directional_df,
            use_container_width=True,
            hide_index=True
        )

    st.info(
        f"The dominant traffic direction is "
        f"{dominant_direction}, carrying "
        f"{dominant_direction_traffic:,.0f} vehicles."
    )

    # ========================================================
    # DAILY VARIATION
    # ========================================================

    st.subheader("Daily Traffic Variation")

    st.line_chart(
        daily_traffic,
        use_container_width=True
    )

    # ========================================================
    # VEHICLE CLASS EXPLORER
    # ========================================================

    st.subheader("Vehicle Class Explorer")

    selected_vehicle = st.selectbox(
        "Select Vehicle Class",
        VEHICLE_COLUMNS,
        key="traffic_selected_vehicle"
    )

    selected_vehicle_hourly = (
        analysis_df
        .groupby("Hour")[selected_vehicle]
        .sum()
        .sort_index()
    )

    selected_vehicle_daily = (
        analysis_df
        .groupby("Date")[selected_vehicle]
        .sum()
        .sort_index()
    )

    explorer_col1, explorer_col2 = st.columns(2)

    with explorer_col1:
        st.write(f"**Hourly Variation — {selected_vehicle}**")
        st.line_chart(
            selected_vehicle_hourly,
            use_container_width=True
        )

    with explorer_col2:
        st.write(f"**Daily Variation — {selected_vehicle}**")
        st.line_chart(
            selected_vehicle_daily,
            use_container_width=True
        )

    # ========================================================
    # DIRECTION-WISE HOURLY PATTERN
    # ========================================================

    st.subheader("Direction-Wise Hourly Traffic Pattern")

    direction_hourly = (
        analysis_df
        .pivot_table(
            index="Hour",
            columns="Direction",
            values="Total_Traffic",
            aggfunc="sum"
        )
        .sort_index()
    )

    st.line_chart(
        direction_hourly,
        use_container_width=True
    )

    # ========================================================
    # DOWNLOADS
    # ========================================================

    st.subheader("Download Traffic Analysis Results")

    download_col1, download_col2, download_col3 = (
        st.columns(3)
    )

    vehicle_csv = (
        vehicle_composition_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    hourly_csv = (
        hourly_analysis
        .reset_index()
        .to_csv(index=False)
        .encode("utf-8")
    )

    directional_csv = (
        directional_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    with download_col1:
        st.download_button(
            label="Download Vehicle Composition",
            data=vehicle_csv,
            file_name="dashboard_vehicle_composition.csv",
            mime="text/csv",
            key="traffic_download_vehicle"
        )

    with download_col2:
        st.download_button(
            label="Download Hourly Traffic",
            data=hourly_csv,
            file_name="dashboard_hourly_traffic.csv",
            mime="text/csv",
            key="traffic_download_hourly"
        )

    with download_col3:
        st.download_button(
            label="Download Directional Traffic",
            data=directional_csv,
            file_name="dashboard_directional_traffic.csv",
            mime="text/csv",
            key="traffic_download_directional"
        )

    st.divider()

    return {
        "analysis_df": analysis_df,
        "total_traffic_volume": total_traffic_volume,
        "commercial_vehicle_share": commercial_vehicle_share,
        "peak_hour": peak_hour,
        "dominant_direction": dominant_direction
    }
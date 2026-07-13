import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_FILE = BASE_DIR / "data" / "traffic_data.csv"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# IMPORT PROJECT FUNCTIONS
# ============================================================

from traffic_utils import (
    load_traffic_data,
    validate_traffic_data,
    add_total_traffic,
    calculate_commercial_vehicle_analysis
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Traffic-Based Flexible Pavement Design System",
    page_icon="🛣️",
    layout="wide"
)


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("Traffic-Based Flexible Pavement Design Decision Support System")

st.caption(
    "Classified Traffic Analysis • IRC:37 Design Traffic • "
    "Sensitivity Analysis • Pavement Catalogue Screening • "
    "IITPAVE Input Preparation"
)

st.info(
    "This application is a pavement-design decision-support tool. "
    "Catalogue screening outputs are preliminary and require "
    "site-specific mechanistic-empirical verification."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Project Controls")

data_source = st.sidebar.radio(
    "Traffic Data Source",
    [
        "Use Project Dataset",
        "Upload CSV File"
    ]
)


# ============================================================
# LOAD TRAFFIC DATA
# ============================================================

df = None
data_source_name = None

try:

    if data_source == "Use Project Dataset":

        df = load_traffic_data(DATA_FILE)

        data_source_name = DATA_FILE.name

    else:

        uploaded_file = st.sidebar.file_uploader(
            "Upload Classified Traffic CSV",
            type=["csv"]
        )

        if uploaded_file is not None:

            df = pd.read_csv(uploaded_file)

            data_source_name = uploaded_file.name

except Exception as error:

    st.error(f"Unable to load traffic data: {error}")

    st.stop()


if df is None:

    st.warning(
        "Upload a classified traffic CSV file to begin the analysis."
    )

    st.stop()


# ============================================================
# VALIDATE TRAFFIC DATA
# ============================================================

try:

    validation_results = validate_traffic_data(df)

except Exception as error:

    st.error(f"Traffic-data validation failed: {error}")

    st.stop()


missing_columns = validation_results["missing_columns"]
missing_values = validation_results["missing_values"]
negative_counts = validation_results["negative_counts"]


if missing_columns:

    st.error(
        "Required traffic columns are missing: "
        + ", ".join(missing_columns)
    )

    st.stop()


if missing_values > 0:

    st.error(
        f"The traffic dataset contains {missing_values} missing values."
    )

    st.stop()


if negative_counts > 0:

    st.error(
        f"The traffic dataset contains {negative_counts} negative counts."
    )

    st.stop()


# ============================================================
# PREPARE TRAFFIC DATA
# ============================================================

try:

    df = add_total_traffic(df)

    commercial_results = calculate_commercial_vehicle_analysis(df)

    average_cvpd = commercial_results["average_cvpd"]

except Exception as error:

    st.error(f"Traffic analysis failed: {error}")

    st.stop()


# ============================================================
# PROJECT OVERVIEW
# ============================================================

st.header("1. Project Overview")

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

overview_col1.metric(
    "Traffic Observations",
    f"{len(df):,}"
)

overview_col2.metric(
    "Average Commercial Traffic",
    f"{average_cvpd:,.2f} CVPD"
)

if "Date" in df.columns:

    survey_days = pd.to_datetime(df["Date"]).nunique()

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


# ============================================================
# DATA VALIDATION SUMMARY
# ============================================================

st.subheader("Traffic Data Validation")

validation_col1, validation_col2, validation_col3 = st.columns(3)

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

st.success("Traffic dataset passed the current validation checks.")


# ============================================================
# DATASET PREVIEW
# ============================================================

st.subheader("Classified Traffic Dataset Preview")

number_of_rows = st.slider(
    "Rows to Display",
    min_value=5,
    max_value=min(50, len(df)),
    value=min(10, len(df))
)

st.dataframe(
    df.head(number_of_rows),
    use_container_width=True
)


# ============================================================
# BASIC DATASET INFORMATION
# ============================================================

with st.expander("View Dataset Information"):

    st.write(f"**Dataset:** {data_source_name}")

    st.write(f"**Number of Rows:** {len(df)}")

    st.write(f"**Number of Columns:** {len(df.columns)}")

    st.write("**Columns:**")

    st.write(list(df.columns))


# ============================================================
# STAGE 1 STATUS
# ============================================================

st.divider()

st.success(
    "Stage 1 completed: traffic data loading, validation, "
    "commercial-traffic calculation, and project overview "
    "are connected successfully."
)
# ============================================================
# STAGE 2: INTERACTIVE TRAFFIC ANALYTICS
# ============================================================

st.header("2. Interactive Traffic Analytics")


# ============================================================
# VEHICLE COLUMN DEFINITIONS
# ============================================================

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


# ============================================================
# SAFETY CHECK
# ============================================================

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


# ============================================================
# PREPARE ANALYSIS DATA
# ============================================================

analysis_df = df.copy()

analysis_df["Date"] = pd.to_datetime(
    analysis_df["Date"],
    errors="coerce"
)

analysis_df["Total_Commercial_Traffic"] = (
    analysis_df[COMMERCIAL_VEHICLE_COLUMNS]
    .sum(axis=1)
)

if "Total_Traffic" not in analysis_df.columns:

    analysis_df["Total_Traffic"] = (
        analysis_df[VEHICLE_COLUMNS]
        .sum(axis=1)
    )


# ============================================================
# TRAFFIC SUMMARY METRICS
# ============================================================

total_traffic_volume = (
    analysis_df["Total_Traffic"].sum()
)

total_commercial_traffic = (
    analysis_df["Total_Commercial_Traffic"].sum()
)

commercial_vehicle_share = (
    total_commercial_traffic
    / total_traffic_volume
    * 100
)

average_daily_total_traffic = (
    analysis_df
    .groupby("Date")["Total_Traffic"]
    .sum()
    .mean()
)


# ============================================================
# PEAK HOUR ANALYSIS
# ============================================================

hourly_total_traffic = (
    analysis_df
    .groupby("Hour")["Total_Traffic"]
    .sum()
    .sort_index()
)

peak_hour = hourly_total_traffic.idxmax()

peak_hour_traffic = hourly_total_traffic.max()


# ============================================================
# DIRECTIONAL ANALYSIS
# ============================================================

directional_traffic = (
    analysis_df
    .groupby("Direction")["Total_Traffic"]
    .sum()
    .sort_values(ascending=False)
)

dominant_direction = directional_traffic.idxmax()

dominant_direction_traffic = directional_traffic.max()


# ============================================================
# DISPLAY SUMMARY METRICS
# ============================================================

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


# ============================================================
# VEHICLE COMPOSITION ANALYSIS
# ============================================================

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
    .rename(
        columns={
            "index": "Vehicle Class"
        }
    )
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


# ============================================================
# HOURLY TRAFFIC VARIATION
# ============================================================

st.subheader("Hourly Traffic Variation")

hourly_analysis = (
    analysis_df
    .groupby("Hour")[
        [
            "Total_Traffic",
            "Total_Commercial_Traffic"
        ]
    ]
    .sum()
    .sort_index()
)

st.line_chart(
    hourly_analysis,
    use_container_width=True
)

st.info(
    f"Peak traffic occurs at {peak_hour}, with a cumulative "
    f"survey-period traffic volume of "
    f"{peak_hour_traffic:,.0f} vehicles for that hourly interval."
)


# ============================================================
# DIRECTIONAL TRAFFIC DISTRIBUTION
# ============================================================

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
    f"The dominant traffic direction in the survey dataset is "
    f"{dominant_direction}, carrying "
    f"{dominant_direction_traffic:,.0f} vehicles."
)


# ============================================================
# DAILY TRAFFIC VARIATION
# ============================================================

st.subheader("Daily Traffic Variation")

daily_traffic = (
    analysis_df
    .groupby("Date")[
        [
            "Total_Traffic",
            "Total_Commercial_Traffic"
        ]
    ]
    .sum()
    .sort_index()
)

st.line_chart(
    daily_traffic,
    use_container_width=True
)


# ============================================================
# VEHICLE CLASS EXPLORER
# ============================================================

st.subheader("Vehicle Class Explorer")

selected_vehicle = st.selectbox(
    "Select Vehicle Class",
    VEHICLE_COLUMNS
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

    st.write(
        f"**Hourly Variation — {selected_vehicle}**"
    )

    st.line_chart(
        selected_vehicle_hourly,
        use_container_width=True
    )


with explorer_col2:

    st.write(
        f"**Daily Variation — {selected_vehicle}**"
    )

    st.line_chart(
        selected_vehicle_daily,
        use_container_width=True
    )


# ============================================================
# DIRECTION-WISE HOURLY TRAFFIC
# ============================================================

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


# ============================================================
# TRAFFIC ANALYSIS DOWNLOADS
# ============================================================

st.subheader("Download Traffic Analysis Results")

download_col1, download_col2, download_col3 = (
    st.columns(3)
)


vehicle_csv = vehicle_composition_df.to_csv(
    index=False
).encode("utf-8")


hourly_csv = hourly_analysis.reset_index().to_csv(
    index=False
).encode("utf-8")


directional_csv = directional_df.to_csv(
    index=False
).encode("utf-8")


with download_col1:

    st.download_button(
        label="Download Vehicle Composition",
        data=vehicle_csv,
        file_name="dashboard_vehicle_composition.csv",
        mime="text/csv"
    )


with download_col2:

    st.download_button(
        label="Download Hourly Traffic",
        data=hourly_csv,
        file_name="dashboard_hourly_traffic.csv",
        mime="text/csv"
    )


with download_col3:

    st.download_button(
        label="Download Directional Traffic",
        data=directional_csv,
        file_name="dashboard_directional_traffic.csv",
        mime="text/csv"
    )


# ============================================================
# STAGE 2 STATUS
# ============================================================

st.divider()

st.success(
    "Stage 2 completed: vehicle composition, hourly variation, "
    "daily variation, directional distribution, peak-hour "
    "analysis, vehicle-class exploration, and downloadable "
    "traffic-analysis results are connected successfully."
)# ============================================================
# STAGE 3: INTERACTIVE DESIGN TRAFFIC CALCULATION
# ============================================================

from design_traffic import calculate_design_traffic


st.header("3. IRC:37 Design Traffic Calculation")

st.write(
    "Estimate cumulative design traffic using the commercial "
    "traffic obtained from the classified traffic dataset."
)


# ============================================================
# DESIGN INPUTS
# ============================================================

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


# ============================================================
# CALCULATE DESIGN TRAFFIC
# ============================================================

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


# ============================================================
# EXTRACT RESULTS
# ============================================================

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


# ============================================================
# DISPLAY PRIMARY RESULTS
# ============================================================

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


# ============================================================
# DISPLAY CALCULATION SUMMARY
# ============================================================

st.subheader("Calculation Summary")

design_summary_df = pd.DataFrame({

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

})


st.dataframe(
    design_summary_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ENGINEERING INTERPRETATION
# ============================================================

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

        "The calculated design traffic exceeds the traffic range "
        "supported by the project's current IRC catalogue-screening "
        "implementation. Site-specific mechanistic-empirical design "
        "and IITPAVE analysis are required."

    )


# ============================================================
# DESIGN TRAFFIC DOWNLOAD
# ============================================================

design_summary_csv = (
    design_summary_df
    .to_csv(index=False)
    .encode("utf-8")
)


st.download_button(

    label="Download Design Traffic Summary",

    data=design_summary_csv,

    file_name="design_traffic_summary.csv",

    mime="text/csv"

)


# ============================================================
# STAGE 3 STATUS
# ============================================================

st.divider()

st.success(

    "Stage 3 completed: interactive traffic-growth projection, "
    "design-period calculation, VDF and lateral-distribution "
    "inputs, cumulative standard-axle calculation, and live "
    "MSA estimation are connected successfully."

)
# ============================================================
# STAGE 4: INTERACTIVE SENSITIVITY ANALYSIS
# ============================================================

from sensitivity_analysis import (
    run_sensitivity_analysis,
    calculate_parameter_influence
)


st.header("4. Interactive Sensitivity Analysis")

st.write(
    "Evaluate how changes in growth rate, Vehicle Damage Factor "
    "(VDF), design period, and years to road opening affect "
    "cumulative design traffic."
)

st.caption(
    "The scenario ranges are generated around the current Stage 3 "
    "design inputs. The influence ranking is range-based and is not "
    "a formal global sensitivity analysis."
)


# ============================================================
# RUN DYNAMIC SENSITIVITY ANALYSIS
# ============================================================

try:

    sensitivity_results = run_sensitivity_analysis(

        average_cvpd=average_cvpd,

        growth_rate=growth_rate,

        design_period=int(design_period),

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


# ============================================================
# BASELINE RESULTS
# ============================================================

baseline_msa = (
    sensitivity_results[
        "baseline"
    ][
        "design_traffic_msa"
    ]
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

    (
        f"{influence_results.iloc[0]}"
        "['Percentage_Range_of_Baseline']:.2f}%"
    )

)


# ============================================================
# HELPER FUNCTION FOR DISPLAYING ANALYSIS
# ============================================================

def display_sensitivity_analysis(

    title,

    dataframe,

    x_column,

    x_label,

    download_file_name

):

    st.subheader(title)


    display_dataframe = dataframe.copy()


    # --------------------------------------------------------
    # CHART DATA
    # --------------------------------------------------------

    chart_data = (

        display_dataframe

        .set_index(x_column)[
            "Design_Traffic_MSA"
        ]

    )


    st.line_chart(

        chart_data,

        use_container_width=True

    )


    # --------------------------------------------------------
    # IDENTIFY BASELINE ROW
    # --------------------------------------------------------

    baseline_rows = display_dataframe[

        display_dataframe[
            "Is_Baseline"
        ]

    ]


    if not baseline_rows.empty:

        baseline_x = (

            baseline_rows
            .iloc[0][x_column]

        )

        baseline_y = (

            baseline_rows
            .iloc[0][
                "Design_Traffic_MSA"
            ]

        )


        st.info(

            f"Current baseline: "
            f"{x_label} = {baseline_x}, "
            f"Design Traffic = "
            f"{baseline_y:.2f} MSA."

        )


    # --------------------------------------------------------
    # DISPLAY TABLE
    # --------------------------------------------------------

    st.dataframe(

        display_dataframe,

        use_container_width=True,

        hide_index=True

    )


    # --------------------------------------------------------
    # DOWNLOAD CSV
    # --------------------------------------------------------

    csv_data = (

        display_dataframe

        .to_csv(index=False)

        .encode("utf-8")

    )


    st.download_button(

        label=f"Download {title} Results",

        data=csv_data,

        file_name=download_file_name,

        mime="text/csv",

        key=f"download_{download_file_name}"

    )


# ============================================================
# GROWTH RATE SENSITIVITY
# ============================================================

display_sensitivity_analysis(

    title=
        "Growth Rate Sensitivity",

    dataframe=
        sensitivity_results[
            "growth_rate"
        ],

    x_column=
        "Growth_Rate_Percent",

    x_label=
        "Annual Traffic Growth Rate (%)",

    download_file_name=
        "growth_rate_sensitivity.csv"

)


# ============================================================
# VDF SENSITIVITY
# ============================================================

display_sensitivity_analysis(

    title=
        "VDF Sensitivity",

    dataframe=
        sensitivity_results[
            "vdf"
        ],

    x_column=
        "VDF",

    x_label=
        "Vehicle Damage Factor (VDF)",

    download_file_name=
        "vdf_sensitivity.csv"

)


# ============================================================
# DESIGN PERIOD SENSITIVITY
# ============================================================

display_sensitivity_analysis(

    title=
        "Design Period Sensitivity",

    dataframe=
        sensitivity_results[
            "design_period"
        ],

    x_column=
        "Design_Period_Years",

    x_label=
        "Design Period (Years)",

    download_file_name=
        "design_period_sensitivity.csv"

)


# ============================================================
# CONSTRUCTION DELAY SENSITIVITY
# ============================================================

display_sensitivity_analysis(

    title=
        "Years to Road Opening Sensitivity",

    dataframe=
        sensitivity_results[
            "construction_delay"
        ],

    x_column=
        "Years_To_Completion",

    x_label=
        "Years Between Traffic Count and Road Opening",

    download_file_name=
        "construction_delay_sensitivity.csv"

)


# ============================================================
# PARAMETER INFLUENCE RANKING
# ============================================================

st.subheader("Parameter Influence Ranking")


st.dataframe(

    influence_results.round(2),

    use_container_width=True,

    hide_index=True

)


# ============================================================
# ENGINEERING INTERPRETATION
# ============================================================

most_influential_parameter = (

    influence_results
    .iloc[0]["Parameter"]

)


highest_influence_range = (

    influence_results
    .iloc[0][
        "Percentage_Range_of_Baseline"
    ]

)


lowest_influence_parameter = (

    influence_results
    .iloc[-1]["Parameter"]

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
    "parameter. It should not be interpreted as proving that one "
    "parameter is universally more important than another."

)


# ============================================================
# DOWNLOAD INFLUENCE RANKING
# ============================================================

influence_csv = (

    influence_results

    .to_csv(index=False)

    .encode("utf-8")

)


st.download_button(

    label="Download Parameter Influence Ranking",

    data=influence_csv,

    file_name=
        "parameter_influence_ranking.csv",

    mime="text/csv"

)


# ============================================================
# STAGE 4 STATUS
# ============================================================

st.divider()


st.success(

    "Stage 4 completed: dynamic growth-rate, VDF, design-period, "
    "and road-opening sensitivity analyses are connected to the "
    "current design inputs, together with scenario-based influence "
    "ranking, engineering interpretation, and CSV downloads."

)
# ============================================================
# STAGE 5: IRC CATALOGUE SCREENING AND IITPAVE INPUT PREPARATION
# ============================================================

from pavement_design import (
    select_catalogue_traffic_level,
    calculate_subgrade_modulus,
    get_verified_catalogue_case,
    create_catalogue_section_table,
    create_iitpave_structural_input,
    create_iitpave_load_input,
    create_screening_summary
)


st.header("5. IRC Catalogue Screening and IITPAVE Input Preparation")

st.write(
    "Screen the calculated design traffic against the currently "
    "implemented verified IRC catalogue case and prepare structural "
    "and loading inputs for subsequent IITPAVE analysis."
)

st.caption(
    "Current verified implementation: Alternative 3, effective "
    "CBR = 10%, IRC:37-2018 Figure 12.22 / Plate-22 / Annex III "
    "Table III.3."
)


# ============================================================
# CURRENT VERIFIED IMPLEMENTATION
# ============================================================

SUPPORTED_ALTERNATIVE_NUMBER = 3
SUPPORTED_EFFECTIVE_CBR = 10


# ============================================================
# CHECK CATALOGUE APPLICABILITY
# ============================================================

catalogue_applicable = True
catalogue_error_message = None


try:

    catalogue_traffic_level = (
        select_catalogue_traffic_level(
            design_traffic_msa
        )
    )


except ValueError as error:

    catalogue_applicable = False

    catalogue_error_message = str(error)


# ============================================================
# DISPLAY APPLICABILITY STATUS
# ============================================================

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


if not catalogue_applicable:

    st.error(catalogue_error_message)

    st.warning(
        "No verified IRC catalogue section is generated for the "
        "current design traffic. Modify the Stage 3 design inputs "
        "to obtain a design traffic within the currently supported "
        "catalogue-screening range."
    )


else:

    # ========================================================
    # GET VERIFIED CATALOGUE CASE
    # ========================================================

    try:

        catalogue_case = get_verified_catalogue_case(

            alternative_number=
                SUPPORTED_ALTERNATIVE_NUMBER,

            effective_cbr=
                SUPPORTED_EFFECTIVE_CBR,

            catalogue_traffic_level=
                catalogue_traffic_level

        )


    except ValueError as error:

        st.error(str(error))

        st.stop()


    # ========================================================
    # CALCULATE SUBGRADE MODULUS
    # ========================================================

    subgrade_modulus = calculate_subgrade_modulus(
        SUPPORTED_EFFECTIVE_CBR
    )


    # ========================================================
    # CREATE PAVEMENT OUTPUT TABLES
    # ========================================================

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
                SUPPORTED_EFFECTIVE_CBR,

            subgrade_modulus=
                subgrade_modulus,

            catalogue_case=
                catalogue_case

        )
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
    # IRC REFERENCE
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
    # LAYER THICKNESS SUMMARY
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
        "ratios required for subsequent IITPAVE analysis."
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


    screening_summary_df = pd.DataFrame(
        [screening_summary]
    )


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
        f"{catalogue_traffic_level} MSA. For the currently verified "
        f"Alternative 3 case with effective CBR = "
        f"{SUPPORTED_EFFECTIVE_CBR}%, the preliminary pavement "
        f"section is {catalogue_case['total_bituminous_mm']} mm "
        f"total bituminous layer, {catalogue_case['ctb_mm']} mm "
        f"CTB, and {catalogue_case['ctsb_mm']} mm CTSB."
    )


    st.warning(
        "This result is a preliminary IRC catalogue-screening "
        "output. It is not a final pavement design approval. "
        "Site-specific material properties, mechanistic-empirical "
        "response analysis, performance checks, and iteration in "
        "IITPAVE are required."
    )


    # ========================================================
    # DOWNLOAD OUTPUT FILES
    # ========================================================

    st.subheader("Download Pavement Screening Results")


    download_row1_col1, download_row1_col2 = st.columns(2)


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


    with download_row1_col1:

        st.download_button(
            label="Download Screening Summary",
            data=screening_csv,
            file_name="pavement_catalogue_screening_summary.csv",
            mime="text/csv",
            key="stage5_download_screening"
        )


    with download_row1_col2:

        st.download_button(
            label="Download IRC Catalogue Section",
            data=catalogue_csv,
            file_name="verified_irc_catalogue_section.csv",
            mime="text/csv",
            key="stage5_download_catalogue"
        )


    download_row2_col1, download_row2_col2 = st.columns(2)


    with download_row2_col1:

        st.download_button(
            label="Download IITPAVE Structural Input",
            data=structural_csv,
            file_name="iitpave_structural_input_summary.csv",
            mime="text/csv",
            key="stage5_download_structural"
        )


    with download_row2_col2:

        st.download_button(
            label="Download IITPAVE Load Input",
            data=load_csv,
            file_name="iitpave_load_input_summary.csv",
            mime="text/csv",
            key="stage5_download_load"
        )


    # ========================================================
    # STAGE 5 STATUS
    # ========================================================

    st.divider()


    st.success(
        "Stage 5 completed: live design traffic is connected to "
        "verified IRC catalogue screening, subgrade modulus "
        "estimation, pavement section preparation, and IITPAVE "
        "structural/load input generation."
    )
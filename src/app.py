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
# PROJECT IMPORTS
# ============================================================

from traffic_utils import (
    load_traffic_data,
    validate_traffic_data,
    add_total_traffic,
    calculate_commercial_vehicle_analysis
)

from dashboard.overview_ui import render_overview
from dashboard.traffic_ui import render_traffic_analytics
from dashboard.design_traffic_ui import render_design_traffic
from dashboard.sensitivity_ui import render_sensitivity_analysis
from dashboard.pavement_ui import render_pavement_design
from dashboard.scenario_ui import render_scenario_comparison
from dashboard.report_ui import render_report_generator

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

st.title(
    "Traffic-Based Flexible Pavement Design Decision Support System"
)

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
    ],
    key="main_data_source"
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
            type=["csv"],
            key="main_csv_uploader"
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
# PREPARE SHARED TRAFFIC DATA
# ============================================================

try:

    df = add_total_traffic(df)

    commercial_results = calculate_commercial_vehicle_analysis(df)

    average_cvpd = commercial_results["average_cvpd"]

except Exception as error:

    st.error(f"Traffic analysis failed: {error}")

    st.stop()


# ============================================================
# RENDER DASHBOARD SECTIONS
# ============================================================

render_overview(
    df=df,
    data_source_name=data_source_name,
    average_cvpd=average_cvpd,
    validation_results=validation_results
)


traffic_results = render_traffic_analytics(
    df=df
)


design_inputs = render_design_traffic(
    average_cvpd=average_cvpd
)


sensitivity_outputs = render_sensitivity_analysis(
    average_cvpd=average_cvpd,
    design_inputs=design_inputs
)


pavement_outputs = render_pavement_design(
    design_inputs=design_inputs
)
scenario_outputs = render_scenario_comparison(
    average_cvpd=average_cvpd,
    design_inputs=design_inputs
)
render_report_generator(
    df=df,
    data_source_name=data_source_name,
    average_cvpd=average_cvpd,
    validation_results=validation_results,
    design_inputs=design_inputs,
    sensitivity_outputs=sensitivity_outputs,
    pavement_outputs=pavement_outputs,
    scenario_outputs=scenario_outputs
)


# ============================================================
# APPLICATION STATUS
# ============================================================

st.success(
    "End-to-end workflow completed successfully: traffic analysis, "
    "design-traffic calculation, sensitivity analysis, IRC catalogue "
    "screening, IITPAVE input preparation, multi-scenario comparison, "
    "and automatic engineering PDF report generation."
)
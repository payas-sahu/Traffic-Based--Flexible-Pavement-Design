from io import BytesIO
from datetime import datetime

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ============================================================
# REPORT CONSTANTS
# ============================================================

REPORT_TITLE = (
    "Traffic-Based Flexible Pavement Design "
    "Decision Support System"
)

REPORT_SUBTITLE = (
    "Engineering Analysis Report"
)


# ============================================================
# 1. HELPER FUNCTIONS
# ============================================================

def format_value(value, decimals=2):
    """
    Format values safely for PDF display.
    """

    if value is None:
        return "N/A"

    try:

        if pd.isna(value):
            return "N/A"

    except (TypeError, ValueError):

        pass

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, int):
        return f"{value:,}"

    if isinstance(value, float):
        return f"{value:,.{decimals}f}"

    return str(value)


def dataframe_to_table_data(
    dataframe,
    columns=None,
    column_labels=None,
    decimals=2
):
    """
    Convert a DataFrame into ReportLab table data.
    """

    if dataframe is None or dataframe.empty:
        return [["No data available"]]

    display_df = dataframe.copy()

    if columns is not None:

        available_columns = [
            column
            for column in columns
            if column in display_df.columns
        ]

        display_df = display_df[available_columns]

    if column_labels is None:

        headers = [
            str(column).replace("_", " ")
            for column in display_df.columns
        ]

    else:

        headers = [
            column_labels.get(
                column,
                str(column).replace("_", " ")
            )
            for column in display_df.columns
        ]

    table_data = [headers]

    for _, row in display_df.iterrows():

        table_data.append(
            [
                format_value(value, decimals)
                for value in row.tolist()
            ]
        )

    return table_data


def add_table(
    story,
    table_data,
    available_width,
    font_size=7,
    repeat_rows=1,
    column_widths=None
):
    """
    Add a consistently styled ReportLab table.
    """

    if column_widths is None:

        number_of_columns = max(
            len(row)
            for row in table_data
        )

        column_widths = [
            available_width / number_of_columns
        ] * number_of_columns

    table = Table(
        table_data,
        colWidths=column_widths,
        repeatRows=repeat_rows,
        hAlign="LEFT"
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#D9EAF7")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.black
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    font_size
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                )
            ]
        )
    )

    story.append(table)

    story.append(Spacer(1, 5 * mm))


# ============================================================
# 2. PAGE NUMBER FUNCTION
# ============================================================

def add_page_number(canvas, document):
    """
    Add page number and footer text.
    """

    canvas.saveState()

    page_number = canvas.getPageNumber()

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.drawString(
        20 * mm,
        12 * mm,
        "Traffic-Based Flexible Pavement Design "
        "Decision Support System"
    )

    canvas.drawRightString(
        A4[0] - 20 * mm,
        12 * mm,
        f"Page {page_number}"
    )

    canvas.restoreState()


# ============================================================
# 3. GENERATE ENGINEERING PDF REPORT
# ============================================================

def generate_engineering_report(
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
    Generate the complete engineering report and return PDF bytes.
    """

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title=REPORT_TITLE,
        author="Traffic-Based Flexible Pavement Design System"
    )

    available_width = (
        A4[0]
        - document.leftMargin
        - document.rightMargin
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=25,
        spaceAfter=8 * mm
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=13,
        leading=17,
        spaceAfter=10 * mm
    )

    section_style = ParagraphStyle(
        "ReportSection",
        parent=styles["Heading1"],
        fontSize=15,
        leading=19,
        spaceBefore=5 * mm,
        spaceAfter=4 * mm
    )

    subsection_style = ParagraphStyle(
        "ReportSubsection",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=3 * mm,
        spaceAfter=3 * mm
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=3 * mm
    )

    note_style = ParagraphStyle(
        "ReportNote",
        parent=body_style,
        fontSize=8,
        leading=11,
        leftIndent=5 * mm,
        rightIndent=5 * mm
    )

    story = []

    # ========================================================
    # TITLE PAGE
    # ========================================================

    story.append(
        Spacer(1, 20 * mm)
    )

    story.append(
        Paragraph(
            REPORT_TITLE,
            title_style
        )
    )

    story.append(
        Paragraph(
            REPORT_SUBTITLE,
            subtitle_style
        )
    )

    report_date = datetime.now().strftime(
        "%d %B %Y, %H:%M"
    )

    title_information = [

        ["Report Generated", report_date],

        [
            "Traffic Dataset",
            format_value(data_source_name)
        ],

        [
            "Traffic Observations",
            format_value(len(df))
        ],

        [
            "Average Commercial Traffic",
            f"{average_cvpd:,.2f} CVPD"
        ],

        [
            "Calculated Design Traffic",
            (
                f"{design_inputs['design_traffic_msa']:.2f} "
                "MSA"
            )
        ]

    ]

    add_table(
        story=story,
        table_data=[
            ["Report Parameter", "Value"],
            *title_information
        ],
        available_width=available_width,
        font_size=9,
        column_widths=[
            available_width * 0.40,
            available_width * 0.60
        ]
    )

    story.append(
        Spacer(1, 10 * mm)
    )

    story.append(
        Paragraph(
            "Purpose of Report",
            subsection_style
        )
    )

    story.append(
        Paragraph(
            "This report summarizes classified traffic analysis, "
            "cumulative design-traffic estimation, sensitivity "
            "analysis, preliminary IRC catalogue screening, "
            "IITPAVE input preparation, and multi-scenario "
            "comparison generated by the decision-support "
            "application.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "<b>Important:</b> Catalogue-screening results are "
            "preliminary decision-support outputs and do not "
            "replace site-specific pavement investigation, "
            "material characterization, mechanistic-empirical "
            "analysis, performance verification, or engineering "
            "judgment.",
            note_style
        )
    )

    story.append(PageBreak())

    # ========================================================
    # 1. TRAFFIC DATA SUMMARY
    # ========================================================

    story.append(
        Paragraph(
            "1. Traffic Data Summary",
            section_style
        )
    )

    survey_days = (
        df["Date"].nunique()
        if "Date" in df.columns
        else "N/A"
    )

    traffic_summary_data = [

        ["Parameter", "Value"],

        [
            "Dataset",
            format_value(data_source_name)
        ],

        [
            "Number of Observations",
            format_value(len(df))
        ],

        [
            "Survey Duration",
            f"{survey_days} Days"
        ],

        [
            "Average Commercial Traffic",
            f"{average_cvpd:,.2f} CVPD"
        ],

        [
            "Missing Required Columns",
            format_value(
                len(
                    validation_results[
                        "missing_columns"
                    ]
                )
            )
        ],

        [
            "Missing Values",
            format_value(
                validation_results[
                    "missing_values"
                ]
            )
        ],

        [
            "Negative Traffic Counts",
            format_value(
                validation_results[
                    "negative_counts"
                ]
            )
        ]

    ]

    add_table(
        story,
        traffic_summary_data,
        available_width,
        font_size=8,
        column_widths=[
            available_width * 0.50,
            available_width * 0.50
        ]
    )

    story.append(
        Paragraph(
            "Traffic Dataset Preview",
            subsection_style
        )
    )

    preview_df = df.head(10).copy()

    preview_columns = [
        column
        for column in [
            "Date",
            "Hour",
            "Direction",
            "Two_Wheeler",
            "Car",
            "LCV",
            "Bus",
            "Two_Axle_Truck",
            "Three_Axle_Truck",
            "MAV",
            "Total_Traffic"
        ]
        if column in preview_df.columns
    ]

    preview_table_data = dataframe_to_table_data(
        preview_df,
        columns=preview_columns
    )

    add_table(
        story,
        preview_table_data,
        available_width,
        font_size=5.5
    )

    # ========================================================
    # 2. DESIGN TRAFFIC CALCULATION
    # ========================================================

    story.append(
        Paragraph(
            "2. Design Traffic Calculation",
            section_style
        )
    )

    design_summary_df = design_inputs[
        "design_summary_df"
    ]

    design_table_data = dataframe_to_table_data(
        design_summary_df,
        columns=[
            "Parameter",
            "Value",
            "Unit"
        ]
    )

    add_table(
        story,
        design_table_data,
        available_width,
        font_size=8,
        column_widths=[
            available_width * 0.52,
            available_width * 0.28,
            available_width * 0.20
        ]
    )

    story.append(
        Paragraph(
            (
                "The current baseline assumptions produce a "
                f"cumulative design traffic of "
                f"<b>{design_inputs['design_traffic_msa']:.2f} "
                "MSA</b>."
            ),
            body_style
        )
    )

    # ========================================================
    # 3. SENSITIVITY ANALYSIS
    # ========================================================

    story.append(
        Paragraph(
            "3. Sensitivity Analysis",
            section_style
        )
    )

    if sensitivity_outputs is None:

        story.append(
            Paragraph(
                "Sensitivity-analysis results were not available.",
                body_style
            )
        )

    else:

        influence_results = sensitivity_outputs[
            "influence_results"
        ]

        influence_table_data = dataframe_to_table_data(
            influence_results,
            columns=[
                "Influence_Rank",
                "Parameter",
                "Minimum_MSA",
                "Maximum_MSA",
                "MSA_Range",
                "Percentage_Range_of_Baseline"
            ],
            column_labels={
                "Influence_Rank": "Rank",
                "Minimum_MSA": "Minimum MSA",
                "Maximum_MSA": "Maximum MSA",
                "MSA_Range": "MSA Range",
                "Percentage_Range_of_Baseline":
                    "% Range of Baseline"
            }
        )

        add_table(
            story,
            influence_table_data,
            available_width,
            font_size=6.5
        )

        most_influential_parameter = (
            influence_results
            .iloc[0]["Parameter"]
        )

        story.append(
            Paragraph(
                (
                    "Within the scenario ranges tested, the "
                    f"highest-ranked parameter is "
                    f"<b>{most_influential_parameter}</b>. "
                    "The ranking is range-dependent and should "
                    "not be interpreted as a formal global "
                    "sensitivity analysis."
                ),
                body_style
            )
        )

    # ========================================================
    # 4. PAVEMENT CATALOGUE SCREENING
    # ========================================================

    story.append(
        Paragraph(
            "4. IRC Catalogue Screening",
            section_style
        )
    )

    if pavement_outputs is None:

        story.append(
            Paragraph(
                "No verified catalogue section was generated for "
                "the current design case because the calculated "
                "design traffic is outside the currently supported "
                "catalogue-screening implementation.",
                body_style
            )
        )

    else:

        screening_summary_df = pavement_outputs[
            "screening_summary_df"
        ]

        screening_table_data = dataframe_to_table_data(
            screening_summary_df
        )

        add_table(
            story,
            screening_table_data,
            available_width,
            font_size=5.5
        )

        story.append(
            Paragraph(
                "Verified Pavement Section",
                subsection_style
            )
        )

        catalogue_section_table = pavement_outputs[
            "catalogue_section_table"
        ]

        catalogue_table_data = dataframe_to_table_data(
            catalogue_section_table
        )

        add_table(
            story,
            catalogue_table_data,
            available_width,
            font_size=7
        )

        catalogue_case = pavement_outputs[
            "catalogue_case"
        ]

        story.append(
            Paragraph(
                (
                    "The preliminary screened pavement section "
                    f"contains "
                    f"<b>{catalogue_case['total_bituminous_mm']} mm</b> "
                    "total bituminous layer, "
                    f"<b>{catalogue_case['ctb_mm']} mm</b> CTB, and "
                    f"<b>{catalogue_case['ctsb_mm']} mm</b> CTSB."
                ),
                body_style
            )
        )

    # ========================================================
    # 5. IITPAVE INPUT PREPARATION
    # ========================================================

    story.append(
        Paragraph(
            "5. IITPAVE Input Preparation",
            section_style
        )
    )

    if pavement_outputs is None:

        story.append(
            Paragraph(
                "IITPAVE structural input preparation was not "
                "available because no verified catalogue section "
                "was generated.",
                body_style
            )
        )

    else:

        story.append(
            Paragraph(
                "Structural Layer Input",
                subsection_style
            )
        )

        structural_table_data = dataframe_to_table_data(
            pavement_outputs[
                "iitpave_structural_input"
            ]
        )

        add_table(
            story,
            structural_table_data,
            available_width,
            font_size=6.5
        )

        story.append(
            Paragraph(
                "Standard Axle Load Input",
                subsection_style
            )
        )

        load_table_data = dataframe_to_table_data(
            pavement_outputs[
                "iitpave_load_input"
            ]
        )

        add_table(
            story,
            load_table_data,
            available_width,
            font_size=7
        )

        story.append(
            Paragraph(
                "SAMI is treated as a crack-relief treatment and "
                "is excluded from the IITPAVE structural-layer "
                "input table.",
                note_style
            )
        )

    # ========================================================
    # 6. SCENARIO COMPARISON
    # ========================================================

    story.append(
        Paragraph(
            "6. Multi-Scenario Comparison",
            section_style
        )
    )

    if scenario_outputs is None:

        story.append(
            Paragraph(
                "Scenario-comparison results were not available.",
                body_style
            )
        )

    else:

        scenario_summary = scenario_outputs[
            "scenario_summary"
        ]

        scenario_summary_data = [

            ["Parameter", "Value"],

            [
                "Scenarios Compared",
                format_value(
                    scenario_summary[
                        "number_of_scenarios"
                    ]
                )
            ],

            [
                "Baseline Scenario",
                format_value(
                    scenario_summary[
                        "baseline_scenario"
                    ]
                )
            ],

            [
                "Baseline Design Traffic",
                (
                    f"{scenario_summary['baseline_msa']:.2f} "
                    "MSA"
                )
            ],

            [
                "Highest Traffic Scenario",
                format_value(
                    scenario_summary[
                        "highest_traffic_scenario"
                    ]
                )
            ],

            [
                "Highest Design Traffic",
                (
                    f"{scenario_summary['highest_design_traffic_msa']:.2f} "
                    "MSA"
                )
            ],

            [
                "Lowest Traffic Scenario",
                format_value(
                    scenario_summary[
                        "lowest_traffic_scenario"
                    ]
                )
            ],

            [
                "Lowest Design Traffic",
                (
                    f"{scenario_summary['lowest_design_traffic_msa']:.2f} "
                    "MSA"
                )
            ],

            [
                "Verified Catalogue Cases",
                format_value(
                    scenario_summary[
                        "verified_catalogue_cases"
                    ]
                )
            ],

            [
                "Unsupported Catalogue Cases",
                format_value(
                    scenario_summary[
                        "unsupported_catalogue_cases"
                    ]
                )
            ]

        ]

        add_table(
            story,
            scenario_summary_data,
            available_width,
            font_size=8,
            column_widths=[
                available_width * 0.55,
                available_width * 0.45
            ]
        )

        compact_comparison_df = scenario_outputs[
            "compact_comparison_df"
        ]

        scenario_columns = [
            "Scenario",
            "Growth_Rate_Percent",
            "Design_Period_Years",
            "VDF",
            "Distribution_Factor",
            "Design_Traffic_MSA",
            "Percent_Change_From_Baseline",
            "Catalogue_Traffic_Level_MSA",
            "Traffic_Rank"
        ]

        scenario_table_data = dataframe_to_table_data(
            compact_comparison_df,
            columns=scenario_columns,
            column_labels={
                "Growth_Rate_Percent": "Growth %",
                "Design_Period_Years": "Period",
                "Distribution_Factor": "D",
                "Design_Traffic_MSA": "MSA",
                "Percent_Change_From_Baseline":
                    "% Change",
                "Catalogue_Traffic_Level_MSA":
                    "Catalogue MSA",
                "Traffic_Rank": "Rank"
            }
        )

        add_table(
            story,
            scenario_table_data,
            available_width,
            font_size=5.5
        )

    # ========================================================
    # 7. ENGINEERING LIMITATIONS
    # ========================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "7. Engineering Limitations and Required Verification",
            section_style
        )
    )

    limitations = [

        "The classified traffic dataset must be representative "
        "of the project road and survey conditions.",

        "Traffic growth rate, design period, Vehicle Damage "
        "Factor, lane distribution factor, and road-opening "
        "assumptions must be selected using project-specific "
        "investigations and applicable standards.",

        "The current verified catalogue implementation supports "
        "only Alternative 3 with effective CBR equal to 10% and "
        "supported catalogue traffic levels from 5 to 50 MSA.",

        "The catalogue section is a preliminary screening output "
        "and is not a substitute for mechanistic-empirical "
        "analysis.",

        "Material moduli, Poisson's ratios, axle loading, tyre "
        "pressure, interface conditions, and other IITPAVE inputs "
        "must be verified for the actual project.",

        "Scenario comparison and sensitivity rankings are "
        "decision-support outputs and depend on the tested input "
        "ranges and assumptions.",

        "Final pavement design requires engineering judgment, "
        "applicable IRC requirements, site investigation, "
        "laboratory testing, performance checks, and design "
        "iteration where required."

    ]

    for limitation in limitations:

        story.append(
            Paragraph(
                f"• {limitation}",
                body_style
            )
        )

    # ========================================================
    # 8. REFERENCES
    # ========================================================

    story.append(
        Paragraph(
            "8. References",
            section_style
        )
    )

    references = [

        "IRC:37-2018, Guidelines for the Design of Flexible Pavements.",

        "IITPAVE layered elastic analysis software and associated "
        "input requirements.",

        "Project classified traffic dataset and engineering "
        "assumptions used in the application."

    ]

    for reference in references:

        story.append(
            Paragraph(
                f"• {reference}",
                body_style
            )
        )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    pdf_bytes = pdf_buffer.getvalue()

    pdf_buffer.close()

    return pdf_bytes
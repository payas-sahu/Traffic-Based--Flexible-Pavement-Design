import pandas as pd


# ==================================================
# VEHICLE CATEGORY DEFINITIONS
# ==================================================

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


# ==================================================
# 1. LOAD TRAFFIC DATA
# ==================================================

def load_traffic_data(file_path):
    """
    Load classified traffic volume data from a CSV file.
    """

    df = pd.read_csv(file_path)

    return df


# ==================================================
# 2. VALIDATE TRAFFIC DATA
# ==================================================

def validate_traffic_data(df):
    """
    Check the traffic dataset for:

    1. Missing columns
    2. Missing values
    3. Duplicate rows
    4. Invalid directions
    5. Negative traffic counts
    """

    required_columns = [
        "Date",
        "Hour",
        "Direction"
    ] + VEHICLE_COLUMNS


    validation_results = {}


    # --------------------------------------------------
    # CHECK MISSING COLUMNS
    # --------------------------------------------------

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    validation_results["missing_columns"] = missing_columns


    # Stop remaining validation if required columns are missing

    if missing_columns:

        validation_results["missing_values"] = None

        validation_results["duplicate_rows"] = None

        validation_results["invalid_directions"] = None

        validation_results["negative_counts"] = None

        return validation_results


    # --------------------------------------------------
    # CHECK MISSING VALUES
    # --------------------------------------------------

    missing_values = (
        df[required_columns]
        .isnull()
        .sum()
        .sum()
    )

    validation_results["missing_values"] = missing_values


    # --------------------------------------------------
    # CHECK DUPLICATE ROWS
    # --------------------------------------------------

    duplicate_rows = df.duplicated().sum()

    validation_results["duplicate_rows"] = duplicate_rows


    # --------------------------------------------------
    # CHECK INVALID DIRECTIONS
    # --------------------------------------------------

    valid_directions = [
        "UP",
        "DOWN"
    ]


    invalid_directions = (
        df.loc[
            ~df["Direction"].isin(valid_directions),
            "Direction"
        ]
        .unique()
        .tolist()
    )


    validation_results["invalid_directions"] = (
        invalid_directions
    )


    # --------------------------------------------------
    # CHECK NEGATIVE TRAFFIC COUNTS
    # --------------------------------------------------

    negative_counts = (
        df[VEHICLE_COLUMNS] < 0
    ).sum().sum()


    validation_results["negative_counts"] = negative_counts


    return validation_results


# ==================================================
# 3. ADD TOTAL TRAFFIC COLUMN
# ==================================================

def add_total_traffic(df):
    """
    Calculate total traffic volume for every
    Date × Hour × Direction observation.
    """

    df = df.copy()


    df["Total_Traffic"] = (
        df[VEHICLE_COLUMNS]
        .sum(axis=1)
    )


    return df


# ==================================================
# 4. VEHICLE COMPOSITION ANALYSIS
# ==================================================

def calculate_vehicle_composition(df):
    """
    Calculate:

    1. Total vehicles by category
    2. Total survey traffic
    3. Vehicle composition percentage
    """


    vehicle_totals = (
        df[VEHICLE_COLUMNS]
        .sum()
    )


    total_traffic = vehicle_totals.sum()


    vehicle_composition = (
        vehicle_totals
        / total_traffic
    ) * 100


    return (
        vehicle_totals,
        total_traffic,
        vehicle_composition
    )


# ==================================================
# 5. DAILY TRAFFIC AND ADT ANALYSIS
# ==================================================

def calculate_daily_traffic_and_adt(df):
    """
    Calculate:

    1. Two-way daily traffic volume
    2. Average Daily Traffic (ADT)
    """


    daily_traffic = (
        df.groupby("Date")["Total_Traffic"]
        .sum()
    )


    adt = daily_traffic.mean()


    return daily_traffic, adt


# ==================================================
# 6. HOURLY TRAFFIC ANALYSIS
# ==================================================

def calculate_hourly_traffic(df):
    """
    Calculate:

    1. Two-way hourly traffic for each survey day
    2. Average hourly traffic across survey days
    3. Peak hour
    4. Peak-hour traffic volume
    5. Lowest traffic hour
    """


    # Two-way traffic for each Date × Hour

    daily_hourly_traffic = (
        df.groupby(
            [
                "Date",
                "Hour"
            ]
        )["Total_Traffic"]
        .sum()
        .reset_index()
    )


    # Average traffic for each hour across survey days

    average_hourly_traffic = (
        daily_hourly_traffic
        .groupby("Hour")["Total_Traffic"]
        .mean()
    )


    # Peak hour

    peak_hour = (
        average_hourly_traffic
        .idxmax()
    )


    peak_hour_volume = (
        average_hourly_traffic
        .max()
    )


    # Lowest traffic hour

    lowest_hour = (
        average_hourly_traffic
        .idxmin()
    )


    lowest_hour_volume = (
        average_hourly_traffic
        .min()
    )


    return {

        "daily_hourly_traffic":
            daily_hourly_traffic,

        "average_hourly_traffic":
            average_hourly_traffic,

        "peak_hour":
            peak_hour,

        "peak_hour_volume":
            peak_hour_volume,

        "lowest_hour":
            lowest_hour,

        "lowest_hour_volume":
            lowest_hour_volume
    }


# ==================================================
# 7. DIRECTIONAL DISTRIBUTION ANALYSIS
# ==================================================

def calculate_directional_distribution(df):
    """
    Calculate:

    1. Total traffic by direction
    2. Directional distribution percentage
    3. Average hourly traffic by direction
    """


    # Total traffic by direction

    direction_totals = (
        df.groupby("Direction")["Total_Traffic"]
        .sum()
    )


    # Directional distribution percentage

    direction_percentage = (
        direction_totals
        / direction_totals.sum()
    ) * 100


    # Traffic for every Date × Hour × Direction

    daily_hourly_direction = (
        df.groupby(
            [
                "Date",
                "Hour",
                "Direction"
            ]
        )["Total_Traffic"]
        .sum()
        .reset_index()
    )


    # Average hourly directional traffic

    average_hourly_direction = (
        daily_hourly_direction
        .groupby(
            [
                "Hour",
                "Direction"
            ]
        )["Total_Traffic"]
        .mean()
        .unstack()
    )


    return {

        "direction_totals":
            direction_totals,

        "direction_percentage":
            direction_percentage,

        "daily_hourly_direction":
            daily_hourly_direction,

        "average_hourly_direction":
            average_hourly_direction
    }


# ==================================================
# 8. COMMERCIAL VEHICLE ANALYSIS
# ==================================================

def calculate_commercial_vehicle_analysis(df):
    """
    Calculate:

    1. Commercial vehicles per observation
    2. Daily commercial vehicle traffic
    3. Average commercial vehicles per day
    4. Total commercial vehicles
    5. Commercial vehicle percentage
    6. Commercial vehicle directional distribution
    """


    df = df.copy()


    # Commercial vehicles in each observation

    df["Commercial_Vehicles"] = (
        df[COMMERCIAL_VEHICLE_COLUMNS]
        .sum(axis=1)
    )


    # Daily commercial vehicle traffic

    daily_commercial_traffic = (
        df.groupby("Date")[
            "Commercial_Vehicles"
        ]
        .sum()
    )


    # Average commercial vehicles per day

    average_cvpd = (
        daily_commercial_traffic
        .mean()
    )


    # Total commercial vehicles

    total_commercial_vehicles = (
        df["Commercial_Vehicles"]
        .sum()
    )


    # Total traffic

    total_traffic = (
        df["Total_Traffic"]
        .sum()
    )


    # Commercial vehicle percentage

    commercial_vehicle_percentage = (

        total_commercial_vehicles
        / total_traffic

    ) * 100


    # Commercial vehicle traffic by direction

    commercial_traffic_by_direction = (
        df.groupby("Direction")[
            "Commercial_Vehicles"
        ]
        .sum()
    )


    # Commercial vehicle directional distribution

    commercial_direction_percentage = (

        commercial_traffic_by_direction
        / commercial_traffic_by_direction.sum()

    ) * 100


    return {

        "data":
            df,

        "daily_commercial_traffic":
            daily_commercial_traffic,

        "average_cvpd":
            average_cvpd,

        "total_commercial_vehicles":
            total_commercial_vehicles,

        "commercial_vehicle_percentage":
            commercial_vehicle_percentage,

        "commercial_traffic_by_direction":
            commercial_traffic_by_direction,

        "commercial_direction_percentage":
            commercial_direction_percentage
    }


# ==================================================
# TEST THE TRAFFIC ANALYSIS FUNCTIONS
# ==================================================

if __name__ == "__main__":


    print("=" * 60)

    print("TRAFFIC ANALYSIS CALCULATION ENGINE")

    print("=" * 60)


    # --------------------------------------------------
    # LOAD DATASET
    # --------------------------------------------------

    df = load_traffic_data(
        "data/traffic_data.csv"
    )


    print("\nDATASET SHAPE")

    print(df.shape)


    # --------------------------------------------------
    # VALIDATE DATASET
    # --------------------------------------------------

    validation_results = (
        validate_traffic_data(df)
    )


    print("\nVALIDATION RESULTS")


    for check, result in validation_results.items():

        print(
            check,
            ":",
            result
        )


    # Stop analysis if columns are missing

    if validation_results["missing_columns"]:

        raise ValueError(
            "Required columns are missing."
        )


    # --------------------------------------------------
    # ADD TOTAL TRAFFIC
    # --------------------------------------------------

    df = add_total_traffic(df)


    # --------------------------------------------------
    # VEHICLE COMPOSITION
    # --------------------------------------------------

    (
        vehicle_totals,
        total_traffic,
        vehicle_composition

    ) = calculate_vehicle_composition(df)


    print("\nTOTAL TRAFFIC BY VEHICLE CATEGORY")

    print(vehicle_totals)


    print("\nTOTAL SURVEY TRAFFIC")

    print(total_traffic)


    print("\nVEHICLE COMPOSITION (%)")

    print(
        vehicle_composition.round(2)
    )


    # --------------------------------------------------
    # DAILY TRAFFIC AND ADT
    # --------------------------------------------------

    daily_traffic, adt = (
        calculate_daily_traffic_and_adt(df)
    )


    print("\nDAILY TRAFFIC TOTALS")

    print(daily_traffic)


    print("\nAVERAGE DAILY TRAFFIC (ADT)")

    print(round(adt, 2))


    # --------------------------------------------------
    # HOURLY TRAFFIC ANALYSIS
    # --------------------------------------------------

    hourly_results = (
        calculate_hourly_traffic(df)
    )


    print("\nPEAK HOUR")

    print(
        hourly_results[
            "peak_hour"
        ]
    )


    print("\nAVERAGE PEAK HOUR VOLUME")

    print(
        round(
            hourly_results[
                "peak_hour_volume"
            ],
            2
        )
    )


    print("\nLOWEST TRAFFIC HOUR")

    print(
        hourly_results[
            "lowest_hour"
        ]
    )


    print("\nAVERAGE LOWEST HOUR VOLUME")

    print(
        round(
            hourly_results[
                "lowest_hour_volume"
            ],
            2
        )
    )


    # --------------------------------------------------
    # DIRECTIONAL DISTRIBUTION
    # --------------------------------------------------

    directional_results = (
        calculate_directional_distribution(df)
    )


    print("\nTOTAL TRAFFIC BY DIRECTION")

    print(
        directional_results[
            "direction_totals"
        ]
    )


    print("\nDIRECTIONAL DISTRIBUTION (%)")

    print(
        directional_results[
            "direction_percentage"
        ].round(2)
    )


    # --------------------------------------------------
    # COMMERCIAL VEHICLE ANALYSIS
    # --------------------------------------------------

    commercial_results = (
        calculate_commercial_vehicle_analysis(df)
    )


    print("\nDAILY COMMERCIAL VEHICLE TRAFFIC")

    print(
        commercial_results[
            "daily_commercial_traffic"
        ]
    )


    print("\nAVERAGE COMMERCIAL VEHICLES PER DAY")

    print(
        round(
            commercial_results[
                "average_cvpd"
            ],
            2
        )
    )


    print("\nTOTAL COMMERCIAL VEHICLES")

    print(
        commercial_results[
            "total_commercial_vehicles"
        ]
    )


    print("\nCOMMERCIAL VEHICLE PERCENTAGE")

    print(
        round(
            commercial_results[
                "commercial_vehicle_percentage"
            ],
            2
        )
    )


    print(
        "\nCOMMERCIAL VEHICLE TRAFFIC BY DIRECTION"
    )

    print(
        commercial_results[
            "commercial_traffic_by_direction"
        ]
    )


    print(
        "\nCOMMERCIAL VEHICLE "
        "DIRECTIONAL DISTRIBUTION (%)"
    )

    print(
        commercial_results[
            "commercial_direction_percentage"
        ].round(2)
    )


    print("\n" + "=" * 60)

    print(
        "TRAFFIC ANALYSIS ENGINE "
        "EXECUTED SUCCESSFULLY"
    )

    print("=" * 60)
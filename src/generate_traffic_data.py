import pandas as pd
import numpy as np

print("PROGRAM STARTED")

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

# Makes the random data reproducible
np.random.seed(42)

dates = pd.date_range(
    start="2026-07-01",
    periods=7,
    freq="D"
)

directions = ["UP", "DOWN"]

# Approximate average traffic volume during a normal hour.
# These are assumptions for generating synthetic test data.
base_vehicle_counts = {
    "Two_Wheeler": 110,
    "Car": 90,
    "LCV": 18,
    "Bus": 12,
    "Two_Axle_Truck": 24,
    "Three_Axle_Truck": 8,
    "MAV": 5
}

traffic_records = []


# --------------------------------------------------
# HOURLY TRAFFIC VARIATION
# --------------------------------------------------

def get_hourly_factor(hour):

    if 0 <= hour < 5:
        return 0.20

    elif 5 <= hour < 7:
        return 0.50

    elif 7 <= hour < 10:
        return 1.20

    elif 10 <= hour < 16:
        return 0.85

    elif 16 <= hour < 20:
        return 1.30

    elif 20 <= hour < 23:
        return 0.70

    else:
        return 0.35


# --------------------------------------------------
# WEEKDAY / WEEKEND VARIATION
# --------------------------------------------------

def get_day_factor(date):

    # Monday = 0
    # Saturday = 5
    # Sunday = 6

    weekday = date.weekday()

    if weekday < 5:
        return 1.00

    elif weekday == 5:
        return 0.90

    else:
        return 0.80


# --------------------------------------------------
# DIRECTIONAL VARIATION
# --------------------------------------------------

def get_direction_factor(direction, hour):

    # Morning peak:
    # Higher traffic in UP direction

    if 7 <= hour < 10:

        if direction == "UP":
            return 1.15

        else:
            return 0.85


    # Evening peak:
    # Higher traffic in DOWN direction

    elif 16 <= hour < 20:

        if direction == "DOWN":
            return 1.15

        else:
            return 0.85


    # Other periods

    else:
        return 1.00


# --------------------------------------------------
# GENERATE TRAFFIC DATA
# --------------------------------------------------

for date in dates:

    day_factor = get_day_factor(date)

    for hour in range(24):

        hourly_factor = get_hourly_factor(hour)

        for direction in directions:

            direction_factor = get_direction_factor(
                direction,
                hour
            )

            record = {
                "Date": date.strftime("%Y-%m-%d"),
                "Hour": f"{hour:02d}:00",
                "Direction": direction
            }


            # Generate traffic counts for each vehicle category

            for vehicle, base_count in base_vehicle_counts.items():

                expected_count = (
                    base_count
                    * hourly_factor
                    * day_factor
                    * direction_factor
                )


                # Add random variation

                random_factor = np.random.normal(
                    loc=1.0,
                    scale=0.08
                )


                generated_count = round(
                    expected_count * random_factor
                )


                # Traffic counts cannot be negative

                generated_count = max(
                    generated_count,
                    0
                )


                record[vehicle] = generated_count


            traffic_records.append(record)


# --------------------------------------------------
# CREATE DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(traffic_records)


# --------------------------------------------------
# DISPLAY DATASET INFORMATION
# --------------------------------------------------

print("\nFIRST 10 ROWS")

print(df.head(10))


print("\nDATASET SHAPE")

print(df.shape)


print("\nCOLUMN NAMES")

print(df.columns.tolist())


print("\nTOTAL TRAFFIC BY VEHICLE CATEGORY")

vehicle_columns = list(
    base_vehicle_counts.keys()
)

print(
    df[vehicle_columns].sum()
)


# --------------------------------------------------
# CHECK GENERATED DATA
# --------------------------------------------------

print("\nMISSING VALUES")

print(
    df.isnull().sum()
)


print("\nDUPLICATE ROWS")

print(
    df.duplicated().sum()
)


print("\nNEGATIVE TRAFFIC COUNTS")

print(
    (df[vehicle_columns] < 0).sum()
)


# --------------------------------------------------
# SAVE DATASET
# --------------------------------------------------

df.to_csv(
    "data/traffic_data.csv",
    index=False
)


print(
    "\nDATASET SAVED SUCCESSFULLY:"
    " data/traffic_data.csv"
)


print("\nPROGRAM FINISHED")
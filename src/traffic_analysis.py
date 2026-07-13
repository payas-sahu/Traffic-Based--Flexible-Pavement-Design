import pandas as pd
import matplotlib.pyplot as plt

# Load the classified traffic volume data
df = pd.read_csv("data/traffic_data.csv")

# Display first 5 rows
print("FIRST 5 ROWS OF THE DATASET")
print(df.head())

# Display dataset dimensions
print("\nDATASET SHAPE")
print(df.shape)

# Display column names
print("\nCOLUMN NAMES")
print(df.columns.tolist())

# Display data types
print("\nDATA TYPES")
print(df.dtypes)

# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

print("\nMISSING VALUES")
print(df.isnull().sum())

print("\nNUMBER OF DUPLICATE ROWS")
print(df.duplicated().sum())

print("\nUNIQUE DIRECTIONS")
print(df["Direction"].unique())

vehicle_columns = [
    "Two_Wheeler",
    "Car",
    "LCV",
    "Bus",
    "Two_Axle_Truck",
    "Three_Axle_Truck",
    "MAV"
]

print("\nNEGATIVE TRAFFIC COUNT CHECK")

negative_counts = (df[vehicle_columns] < 0).sum()

print(negative_counts)

# --------------------------------------------------
# TRAFFIC VOLUME ANALYSIS
# --------------------------------------------------

# Calculate total vehicles in each observation
df["Total_Traffic"] = df[vehicle_columns].sum(axis=1)

print("\nDATASET WITH TOTAL TRAFFIC")
print(df[["Date", "Hour", "Direction", "Total_Traffic"]])

# Calculate total traffic volume by vehicle category
vehicle_totals = df[vehicle_columns].sum()

print("\nTOTAL TRAFFIC BY VEHICLE CATEGORY")
print(vehicle_totals)

# Calculate total traffic volume of all vehicles
total_traffic = vehicle_totals.sum()

print("\nTOTAL TRAFFIC VOLUME")
print(total_traffic)
# --------------------------------------------------
# VEHICLE COMPOSITION ANALYSIS
# --------------------------------------------------

# Calculate percentage composition of each vehicle category
vehicle_composition = (vehicle_totals / total_traffic) * 100

print("\nVEHICLE COMPOSITION PERCENTAGE")
print(vehicle_composition.round(2))
print("\nSUM OF VEHICLE COMPOSITION PERCENTAGES")
print(vehicle_composition.sum())
# --------------------------------------------------
# VEHICLE COMPOSITION BAR CHART
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    vehicle_composition.index,
    vehicle_composition.values
)

plt.title("Vehicle Composition of Observed Traffic")
plt.xlabel("Vehicle Category")
plt.ylabel("Percentage of Total Traffic (%)")

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.savefig(
    "outputs/vehicle_composition.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# DAILY TRAFFIC ANALYSIS
# --------------------------------------------------

# Calculate total traffic for each date
daily_traffic = df.groupby("Date")["Total_Traffic"].sum()

print("\nDAILY TRAFFIC TOTALS")
print(daily_traffic)


# Calculate Average Daily Traffic (ADT)
adt = daily_traffic.mean()

print("\nAVERAGE DAILY TRAFFIC (ADT)")
print(round(adt, 2))


# Identify highest traffic day
highest_traffic_day = daily_traffic.idxmax()

highest_traffic_volume = daily_traffic.max()

print("\nHIGHEST TRAFFIC DAY")
print(highest_traffic_day)

print("\nHIGHEST DAILY TRAFFIC VOLUME")
print(highest_traffic_volume)


# Identify lowest traffic day
lowest_traffic_day = daily_traffic.idxmin()

lowest_traffic_volume = daily_traffic.min()

print("\nLOWEST TRAFFIC DAY")
print(lowest_traffic_day)

print("\nLOWEST DAILY TRAFFIC VOLUME")
print(lowest_traffic_volume)
print("\nADT VALIDATION")

adt_check = total_traffic / df["Date"].nunique()

print("ADT from daily totals:", round(adt, 2))

print("ADT from total traffic / number of days:",
      round(adt_check, 2))

if round(adt, 2) == round(adt_check, 2):
    print("PASS: ADT calculation is consistent.")

else:
    print("FAIL: ADT calculation is inconsistent.")
# --------------------------------------------------
# HOURLY TRAFFIC VARIATION ANALYSIS
# --------------------------------------------------

# Calculate two-way traffic volume for each Date and Hour
daily_hourly_traffic = (
    df.groupby(["Date", "Hour"])["Total_Traffic"]
    .sum()
    .reset_index()
)

print("\nFIRST 10 DAILY-HOURLY TRAFFIC RECORDS")
print(daily_hourly_traffic.head(10))


# Calculate average hourly traffic volume across 7 days
average_hourly_traffic = (
    daily_hourly_traffic
    .groupby("Hour")["Total_Traffic"]
    .mean()
)

print("\nAVERAGE HOURLY TRAFFIC VOLUME")
print(average_hourly_traffic.round(2))


# Identify peak hour
peak_hour = average_hourly_traffic.idxmax()

peak_hour_volume = average_hourly_traffic.max()

print("\nPEAK HOUR")
print(peak_hour)

print("\nAVERAGE PEAK HOUR VOLUME")
print(round(peak_hour_volume, 2))


# Identify lowest traffic hour
lowest_hour = average_hourly_traffic.idxmin()

lowest_hour_volume = average_hourly_traffic.min()

print("\nLOWEST TRAFFIC HOUR")
print(lowest_hour)

print("\nAVERAGE LOWEST HOUR VOLUME")
print(round(lowest_hour_volume, 2))
# --------------------------------------------------
# HOURLY TRAFFIC VARIATION CHART
# --------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    average_hourly_traffic.index,
    average_hourly_traffic.values,
    marker="o"
)

plt.title("Average Hourly Traffic Variation")
plt.xlabel("Hour of Day")
plt.ylabel("Average Two-Way Traffic Volume (vehicles/hour)")

plt.xticks(rotation=45)

plt.grid()

plt.tight_layout()

plt.savefig(
    "outputs/hourly_traffic_variation.png",
    dpi=300
)

plt.close()
# --------------------------------------------------
# DIRECTIONAL DISTRIBUTION ANALYSIS
# --------------------------------------------------

# Total traffic volume by direction
direction_totals = (
    df.groupby("Direction")["Total_Traffic"]
    .sum()
)

print("\nTOTAL TRAFFIC BY DIRECTION")
print(direction_totals)


# Percentage distribution by direction
direction_percentage = (
    direction_totals / direction_totals.sum()
) * 100

print("\nOVERALL DIRECTIONAL DISTRIBUTION (%)")
print(direction_percentage.round(2))


# --------------------------------------------------
# HOURLY TRAFFIC BY DIRECTION
# --------------------------------------------------

# Total traffic for each Date × Hour × Direction
daily_hourly_direction = (
    df.groupby(["Date", "Hour", "Direction"])["Total_Traffic"]
    .sum()
    .reset_index()
)

# Average traffic volume by Hour × Direction
average_hourly_direction = (
    daily_hourly_direction
    .groupby(["Hour", "Direction"])["Total_Traffic"]
    .mean()
    .unstack()
)

print("\nAVERAGE HOURLY TRAFFIC BY DIRECTION")
print(average_hourly_direction.round(2))


# --------------------------------------------------
# MORNING PEAK DIRECTIONAL DISTRIBUTION
# --------------------------------------------------

morning_hours = ["07:00", "08:00", "09:00"]

morning_direction_traffic = (
    daily_hourly_direction[
        daily_hourly_direction["Hour"].isin(morning_hours)
    ]
    .groupby("Direction")["Total_Traffic"]
    .sum()
)

morning_direction_percentage = (
    morning_direction_traffic
    / morning_direction_traffic.sum()
) * 100

print("\nMORNING PEAK DIRECTIONAL DISTRIBUTION (%)")
print(morning_direction_percentage.round(2))


# --------------------------------------------------
# EVENING PEAK DIRECTIONAL DISTRIBUTION
# --------------------------------------------------

evening_hours = ["16:00", "17:00", "18:00", "19:00"]

evening_direction_traffic = (
    daily_hourly_direction[
        daily_hourly_direction["Hour"].isin(evening_hours)
    ]
    .groupby("Direction")["Total_Traffic"]
    .sum()
)

evening_direction_percentage = (
    evening_direction_traffic
    / evening_direction_traffic.sum()
) * 100

print("\nEVENING PEAK DIRECTIONAL DISTRIBUTION (%)")
print(evening_direction_percentage.round(2))


# --------------------------------------------------
# DIRECTIONAL TRAFFIC VARIATION CHART
# --------------------------------------------------

plt.figure(figsize=(12, 6))

for direction in average_hourly_direction.columns:

    plt.plot(
        average_hourly_direction.index,
        average_hourly_direction[direction],
        marker="o",
        label=direction
    )

plt.title("Average Hourly Traffic Variation by Direction")

plt.xlabel("Hour of Day")

plt.ylabel("Average Traffic Volume (vehicles/hour/direction)")

plt.xticks(rotation=45)

plt.legend()

plt.grid()

plt.tight_layout()

plt.savefig(
    "outputs/directional_traffic_variation.png",
    dpi=300
)

plt.close()
# --------------------------------------------------
# COMMERCIAL VEHICLE TRAFFIC ANALYSIS
# --------------------------------------------------

commercial_vehicle_columns = [
    "LCV",
    "Bus",
    "Two_Axle_Truck",
    "Three_Axle_Truck",
    "MAV"
]

# Total commercial vehicles in each observation
df["Commercial_Vehicles"] = df[
    commercial_vehicle_columns
].sum(axis=1)


# Daily two-way commercial vehicle traffic
daily_commercial_traffic = (
    df.groupby("Date")["Commercial_Vehicles"]
    .sum()
)

print("\nDAILY COMMERCIAL VEHICLE TRAFFIC")
print(daily_commercial_traffic)


# Average commercial vehicles per day
average_cvpd = daily_commercial_traffic.mean()

print("\nAVERAGE COMMERCIAL VEHICLES PER DAY")
print(round(average_cvpd, 2))


# Total commercial vehicles during survey period
total_commercial_vehicles = (
    df["Commercial_Vehicles"].sum()
)

print("\nTOTAL COMMERCIAL VEHICLES")
print(total_commercial_vehicles)


# Commercial vehicles as percentage of total traffic
commercial_vehicle_percentage = (
    total_commercial_vehicles / total_traffic
) * 100

print("\nCOMMERCIAL VEHICLE PERCENTAGE")
print(round(commercial_vehicle_percentage, 2))


# --------------------------------------------------
# COMMERCIAL VEHICLE TRAFFIC BY DIRECTION
# --------------------------------------------------

commercial_traffic_by_direction = (
    df.groupby("Direction")["Commercial_Vehicles"]
    .sum()
)

print("\nCOMMERCIAL VEHICLE TRAFFIC BY DIRECTION")
print(commercial_traffic_by_direction)


commercial_direction_percentage = (
    commercial_traffic_by_direction
    / commercial_traffic_by_direction.sum()
) * 100

print("\nCOMMERCIAL VEHICLE DIRECTIONAL DISTRIBUTION (%)")
print(commercial_direction_percentage.round(2))


# --------------------------------------------------
# DAILY COMMERCIAL TRAFFIC CHART
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(
    daily_commercial_traffic.index,
    daily_commercial_traffic.values
)

plt.title("Daily Commercial Vehicle Traffic")

plt.xlabel("Date")

plt.ylabel("Two-Way Commercial Vehicle Traffic (vehicles/day)")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "outputs/daily_commercial_traffic.png",
    dpi=300
)

plt.close()
# --------------------------------------------------
# SAVE ANALYSIS RESULTS
# --------------------------------------------------

# Save daily traffic totals
daily_traffic.to_csv(
    "outputs/daily_traffic_totals.csv",
    header=["Total_Traffic"]
)

# Save vehicle composition results
vehicle_composition.to_csv(
    "outputs/vehicle_composition.csv",
    header=["Percentage"]
)

# Save average hourly traffic
average_hourly_traffic.to_csv(
    "outputs/average_hourly_traffic.csv",
    header=["Average_Traffic"]
)

# Save hourly directional traffic
average_hourly_direction.to_csv(
    "outputs/average_hourly_direction.csv"
)

# Save daily commercial vehicle traffic
daily_commercial_traffic.to_csv(
    "outputs/daily_commercial_traffic.csv",
    header=["Commercial_Vehicles"]
)


# Create overall traffic analysis summary
summary_results = pd.DataFrame({
    "Metric": [
        "Total Survey Traffic",
        "7-Day Average Daily Traffic (ADT)",
        "Peak Hour",
        "Average Peak Hour Volume",
        "Lowest Traffic Hour",
        "Average Lowest Hour Volume",
        "Average Commercial Vehicles Per Day",
        "Commercial Vehicle Percentage"
    ],

    "Value": [
        total_traffic,
        round(adt, 2),
        peak_hour,
        round(peak_hour_volume, 2),
        lowest_hour,
        round(lowest_hour_volume, 2),
        round(average_cvpd, 2),
        round(commercial_vehicle_percentage, 2)
    ]
})


summary_results.to_csv(
    "outputs/traffic_analysis_summary.csv",
    index=False
)


print("\nANALYSIS RESULTS SAVED SUCCESSFULLY")
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import binomtest
from scipy.stats import ttest_ind


# Load your HTML content
with open("trimet_stopevents_2022-12-07.html", "r") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")
data = []

# Loop through all headers that match the PDX_TRIP pattern
for header in soup.find_all("h2"):
    if "Stop events for PDX_TRIP" in header.text:
        trip_id = header.text.split("PDX_TRIP")[-1].strip()
        table = header.find_next_sibling("table")

        if not table:
            continue

        # Get header to know column positions
        header_row = table.find("tr")
        col_names = [th.text.strip().lower() for th in header_row.find_all("th")]

        # Get indices for required columns
        try:
            idx_vehicle = col_names.index("vehicle_number")
            idx_location = col_names.index("location_id")
            idx_arrive = col_names.index("arrive_time")
            idx_ons = col_names.index("ons")
            idx_offs = col_names.index("offs")
        except ValueError:
            continue  # Skip table if any column not found

        # Process data rows
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < max(idx_vehicle, idx_location, idx_arrive, idx_ons, idx_offs) + 1:
                continue

            try:
                vehicle_number = cols[idx_vehicle].text.strip()
                location_id = cols[idx_location].text.strip()
                arrive_time = int(cols[idx_arrive].text.strip())
                ons = int(cols[idx_ons].text.strip())
                offs = int(cols[idx_offs].text.strip())
                tstamp = (datetime.min + timedelta(seconds=arrive_time)).time().isoformat()

                data.append({
                    "trip_id": trip_id,
                    "vehicle_number": vehicle_number,
                    "tstamp": tstamp,
                    "location_id": location_id,
                    "ons": ons,
                    "offs": offs
                })
            except ValueError:
                continue

# Final DataFrame
stops_df = pd.DataFrame(data)
print(stops_df)

################################################################################
## START SLIDE 2 (TRANSFORM)
################################################################################

print(f"SLIDE TWO RESULTS: \n")
# How many unique vehicles?
num_vehicles = stops_df['vehicle_number'].nunique()
print(f"Number of unique vehicles: {num_vehicles}")

# How many unique stop locations?
num_locations = stops_df['location_id'].nunique()
print(f"Number of unique stop locations: {num_locations}")

# Min and Max values of tstamp
stops_df['tstamp_dt'] = pd.to_datetime(stops_df['tstamp'], format='%H:%M:%S')
min_tstamp = stops_df['tstamp_dt'].min().time()
max_tstamp = stops_df['tstamp_dt'].max().time()
print(f"Earliest stop time: {min_tstamp}")
print(f"Latest stop time: {max_tstamp}")

# How many stop events where at least one passenger boarded?
events_with_boarding = stops_df[stops_df['ons'] >= 1]
num_events_with_boarding = len(events_with_boarding)
print(f"Stop events with at least one passenger boarding: {num_events_with_boarding}")

# Percentage of stop events with at least one boarding
total_events = len(stops_df)
boarding_percentage = (num_events_with_boarding / total_events) * 100 if total_events > 0 else 0
print(f"Percentage of stop events with at least one boarding: {boarding_percentage:.2f}%")

# Ensure timestamps are parsed if not already
stops_df['tstamp_dt'] = pd.to_datetime(stops_df['tstamp'], format='%H:%M:%S')

################################################################################
## START SLIDE 3 (VALIDATE)
################################################################################

print(f"SLIDE THREE RESULTS: \n")

# For location 6913
loc_id = "6913"
loc_df = stops_df[stops_df['location_id'] == loc_id]

# How many stops at this location?
num_stops_at_loc = len(loc_df)
print(f"Number of stops at location {loc_id}: {num_stops_at_loc}")

# How many different vehicles stopped at this location?
num_vehicles_at_loc = loc_df['vehicle_number'].nunique()
print(f"Number of different vehicles that stopped at location {loc_id}: {num_vehicles_at_loc}")

# Percentage of stops at this location where at least one passenger boarded
num_boarding_at_loc = (loc_df['ons'] >= 1).sum()
boarding_pct_loc = (num_boarding_at_loc / num_stops_at_loc) * 100 if num_stops_at_loc > 0 else 0
print(f"Percentage of stops at location {loc_id} with at least one boarding: {boarding_pct_loc:.2f}%")

# For vehicle 4062
veh_id = "4062"
veh_df = stops_df[stops_df['vehicle_number'] == veh_id]

# How many stops made by this vehicle?
num_stops_by_vehicle = len(veh_df)
print(f"Number of stops made by vehicle {veh_id}: {num_stops_by_vehicle}")

# Total passengers boarded this vehicle
total_boarded_by_vehicle = veh_df['ons'].sum()
print(f"Total passengers boarded vehicle {veh_id}: {total_boarded_by_vehicle}")

# Total passengers deboarded this vehicle
total_offs_by_vehicle = veh_df['offs'].sum()
print(f"Total passengers deboarded vehicle {veh_id}: {total_offs_by_vehicle}")

# Percentage of stops where at least one person boarded
num_boarding_stops_veh = (veh_df['ons'] >= 1).sum()
boarding_pct_vehicle = (num_boarding_stops_veh / num_stops_by_vehicle) * 100 if num_stops_by_vehicle > 0 else 0
print(f"Percentage of vehicle {veh_id} stop events with at least one boarding: {boarding_pct_vehicle:.2f}%")


################################################################################
## START SLIDE 4 (BIASED BOARDING DATA)
################################################################################

print(f"SLIDE FOUR RESULTS: \n")

stops_df['ons'] = pd.to_numeric(stops_df['ons'], errors='coerce').fillna(0)

total_stops = len(stops_df)
total_boarding_stops = (stops_df['ons'] >= 1).sum()
overall_boarding_rate = total_boarding_stops / total_stops
print(f"Overall system-wide boarding rate: {overall_boarding_rate:.4f} ({total_boarding_stops}/{total_stops})")

results = []

for vehicle_id, group in stops_df.groupby('vehicle_number'):
    n = len(group)  # total stop events for this vehicle
    k = (group['ons'] >= 1).sum()  # number of events where someone boarded

    result = binomtest(k, n, p=overall_boarding_rate, alternative='two-sided')
    p_value = result.pvalue

    results.append({
        'vehicle_id': vehicle_id,
        'num_stops': n,
        'num_boarding_stops': k,
        'boarding_rate': k / n if n > 0 else 0,
        'p_value': p_value
    })

vehicle_df = pd.DataFrame(results)

biased_vehicles_df = vehicle_df[vehicle_df['p_value'] < 0.05].sort_values('p_value')

print("Vehicles with potentially biased boarding data (p < 0.05):\n")
print(biased_vehicles_df[['vehicle_id', 'num_stops', 'boarding_rate', 'p_value']])

################################################################################
## START SLIDE 5 (BIASED GPS DATA)
################################################################################
print(f"SLIDE FIVE RESULTS: \n\n")

relpos_df = pd.read_csv("trimet_relpos_2022-12-07.csv")

relpos_df.columns = [col.strip().lower() for col in relpos_df.columns]

# Drop any rows with missing RELPOS or VEHICLE_NUMBER
relpos_df.dropna(subset=["relpos", "vehicle_number"], inplace=True)

# Ensure correct types
relpos_df["relpos"] = pd.to_numeric(relpos_df["relpos"], errors="coerce")
relpos_df["vehicle_number"] = relpos_df["vehicle_number"].astype(str)

relpos_df = relpos_df.dropna(subset=["relpos"])

print("Loaded RELPOS data:")
print(relpos_df.head())

all_relpos = relpos_df['relpos'].dropna().values  # array of all relpos

results = []

for vehicle_id, group in relpos_df.groupby('vehicle_number'):
    vehicle_relpos = group['relpos'].dropna().values

    t_stat, p_value = ttest_ind(vehicle_relpos, all_relpos, equal_var=False)

    results.append({
        'vehicle_id': vehicle_id,
        'num_points': len(vehicle_relpos),
        'mean_relpos': vehicle_relpos.mean(),
        'p_value': p_value
    })

vehicle_bias_df = pd.DataFrame(results)

# 4. Filter vehicles with p < 0.005 (very strong evidence of bias)
biased_vehicles = vehicle_bias_df[vehicle_bias_df['p_value'] < 0.005].sort_values('p_value')

print("Vehicles with statistically significant RELPOS bias (p < 0.005):")
print(biased_vehicles[['vehicle_id', 'num_points', 'mean_relpos', 'p_value']])
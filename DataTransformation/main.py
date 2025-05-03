import pandas as pd
from datetime import datetime, timedelta

# Read data and drop unwanted columns
data = pd.read_csv("bc_trip259172515_230215.csv")
data = data.drop(columns=["EVENT_NO_STOP", "GPS_SATELLITES", "GPS_HDOP"])

#data = pd.read_csv("bc_trip259172515_230215.csv", usecols=[
#    "EVENT_NO_STOP", "GPS_SATELLITES", "GPS_HDOP", "OPD_DATE", "ACT_TIME"
#])

# Compute timestamp from ODP_DATE and ACT_TIME
def compute_timestamp(row):
    base_date = datetime.strptime(row["OPD_DATE"], "%d%b%Y:%H:%M:%S")
    time_offset = timedelta(seconds=int(row["ACT_TIME"]))
    return base_date + time_offset

data["TIMESTAMP"] = data.apply(compute_timestamp, axis=1)
data = data.drop(columns=["OPD_DATE", "ACT_TIME"])

# Compute differences
data["dMETERS"] = data["METERS"].diff()
data["dTIMESTAMP"] = data["TIMESTAMP"].diff().dt.total_seconds()  # Convert timedelta to seconds

# Compute SPEED
data["SPEED"] = data.apply(lambda row: row["dMETERS"] / row["dTIMESTAMP"] if pd.notnull(row["dMETERS"]) and row["dTIMESTAMP"] > 0 else 0, axis=1)

# Drop dMETERS and dTIMESTAMP columns
data = data.drop(columns=["dMETERS", "dTIMESTAMP"])

min = data["SPEED"].min()
max = data["SPEED"].max()
avg = data["SPEED"].mean()

# Print total breadcrumb records & data
print(data)
print(f"Number of breadcrumb records: {len(data)}")

# Print min, max, & avg speeds
print(f"Minimum Speed: {min} m/s")
print(f"Maximum Speed: {max} m/s")
print(f"Average Speed: {avg} m/s")

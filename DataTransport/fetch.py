import urllib.request
import urllib.parse
import json

def fetchData(vehicleID):
    url = f"https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id={urllib.parse.quote(str(vehicleID))}"
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        return json.loads(data)  
    except urllib.error.HTTPError as err:
        print(f"HTTPError for vehicle {vehicleID}: {err.code} - {err.reason}")
    except urllib.error.URLError as err:
        print(f"URLError for vehicle {vehicleID}: {err.reason}")
    except Exception as err:
        print(f"Unexpected error for vehicle {vehicleID}: {err}")
    return []  

vehicle_ids = [2907, 3055]
combined_data = []

for vid in vehicle_ids:
    vehicle_data = fetchData(vid)
    combined_data.extend(vehicle_data)  

with open("bcsample.json", 'w') as file:
    json.dump(combined_data, file, indent=2)

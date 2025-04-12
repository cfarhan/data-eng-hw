import requests

def check_if_currently_raining():
    url = "https://api.openweathermap.org/data/2.5/weather"
    city = 'Portland'
    params = {
        "q": city,
        "appid": '9ecd04a093d3315421511ab21f380c83',
        "units": 'imperial'       
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    weather_conditions = [w['main'] for w in data['weather']]
    if "Rain" in weather_conditions:
        print(f"Yes, it's currently raining in {city}.")
    else:
        print(f"No, it's not raining in {city}.")

def will_it_rain():

    url = "https://api.openweathermap.org/data/2.5/forecast"
    city = 'Portland'
    params = {
        "q": city,
        "appid": '9ecd04a093d3315421511ab21f380c83',
        "units": "imperial"
    }

    response = requests.get(url, params=params)
    data = response.json()

    for item in data["list"]:
        weather_conditions = [w["main"] for w in item["weather"]]
        if "Rain" in weather_conditions:
            time = item["dt_txt"]
            description = item["weather"][0]["description"]
            print(f"Rain expected at {time}")


def main():
    check_if_currently_raining()
    will_it_rain()


if __name__ == "__main__":
    main()
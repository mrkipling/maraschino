from flask import Flask, jsonify, render_template
from pywapi.pywapi import get_weather_from_google
import re

from Maraschino import app
from settings import *
from maraschino.tools import *

@app.route('/xhr/weather')
@requires_auth
def xhr_weather():

    location = get_setting_value('weather_location')
    use_metric = get_setting_value('weather_use_metric') == '1'
    weather = get_weather_from_google(location)

    current_conditions = weather['current_conditions']
    forcast_info = weather['forecast_information']

    wind = current_conditions['wind_condition']
    windspeed_mph = re.findall("\d+", wind)
    windspeed_mph = int(windspeed_mph[0])

    day1 = weather['forecasts'][0]
    day2 = weather['forecasts'][1]
    day3 = weather['forecasts'][2]
    day4 = weather['forecasts'][3]

    imagepath = "/static/images/weather/"

    if current_conditions['condition'] == "Chance of Rain":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Light rain":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Thunderstorm":
        current_conditions['icon'] = "Thunderstorm"
    elif current_conditions['condition'] == "Clear":
        current_conditions['icon'] = "Sunny"
    elif current_conditions['condition'] == "Sunny":
        current_conditions['icon'] = "Sunny"
    elif current_conditions['condition'] == "Freezing Drizzle":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Light Snow":
        current_conditions['icon'] = "Snow"
    elif current_conditions['condition'] == "Overcast":
        current_conditions['icon'] = "Overcast"
    elif current_conditions['condition'] == "Rain and Snow":
        current_conditions['icon'] = "Rain and Snow"
    elif current_conditions['condition'] == "Scattered Showers":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Showers":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Scattered Thunderstorms":
        current_conditions['icon'] = "Thunderstorm"
    elif current_conditions['condition'] == "Mostly Sunny":
        current_conditions['icon'] = "Sunny"
    elif current_conditions['condition'] == "Partly Cloudy":
        current_conditions['icon'] = "Partly Sunny"
    elif current_conditions['condition'] == "Partly Sunny":
        current_conditions['icon'] = "Partly Sunny"
    elif current_conditions['condition'] == "Mostly Cloudy":
        current_conditions['icon'] = "Overcast"
    elif current_conditions['condition'] == "Chance of Storm":
        current_conditions['icon'] = "Storm"
    elif current_conditions['condition'] == "Rain":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Chance of Snow":
        current_conditions['icon'] = "Snow"
    elif current_conditions['condition'] == "Cloudy":
        current_conditions['icon'] = "Overcast"
    elif current_conditions['condition'] == "Mist":
        current_conditions['icon'] = "Fog"
    elif current_conditions['condition'] == "Storm":
        current_conditions['icon'] = "Storm"
    elif current_conditions['condition'] == "Chance of TStorm":
        current_conditions['icon'] = "Thunderstorm"
    elif current_conditions['condition'] == "Sleet":
        current_conditions['icon'] = "Rain and Snow"
    elif current_conditions['condition'] == "Snow":
        current_conditions['icon'] = "Snow"
    elif current_conditions['condition'] == "Icy":
        current_conditions['icon'] = "Snow"
    elif current_conditions['condition'] == "Dust":
        current_conditions['icon'] = "Snow"
    elif current_conditions['condition'] == "Fog":
        current_conditions['icon'] = "Fog"
    elif current_conditions['condition'] == "Smoke":
        current_conditions['icon'] = "Fog"
    elif current_conditions['condition'] == "Haze":
        current_conditions['icon'] = "Fog"
    elif current_conditions['condition'] == "Flurries":
        current_conditions['icon'] = "Snow"
    elif current_conditions['condition'] == "Light Rain":
        current_conditions['icon'] = "Rain"
    elif current_conditions['condition'] == "Snow Showers":
        current_conditions['icon'] = "Rain and Snow"
    elif current_conditions['condition'] == "Hail":
        current_conditions['icon'] = "Storm"

    for day in weather['forecasts']:
        if day['condition'] == "Chance of Rain":
            day['icon'] = "Rain"
        elif day['condition'] == "Light rain":
            day['icon'] = "Rain"
        elif day['condition'] == "Thunderstorm":
            day['icon'] = "Thunderstorm"
        elif day['condition'] == "Clear":
            day['icon'] = "Sunny"
        elif day['condition'] == "Sunny":
            day['icon'] = "Sunny"
        elif day['condition'] == "Freezing Drizzle":
            day['icon'] = "Rain"
        elif day['condition'] == "Light Snow":
            day['icon'] = "Snow"
        elif day['condition'] == "Overcast":
            day['icon'] = "Overcast"
        elif day['condition'] == "Rain and Snow":
            day['icon'] = "Rain and Snow"
        elif day['condition'] == "Scattered Showers":
            day['icon'] = "Rain"
        elif day['condition'] == "Showers":
            day['icon'] = "Rain"
        elif day['condition'] == "Scattered Thunderstorms":
            day['icon'] = "Thunderstorm"
        elif day['condition'] == "Mostly Sunny":
            day['icon'] = "Sunny"
        elif day['condition'] == "Partly Cloudy":
            day['icon'] = "Partly Sunny"
        elif day['condition'] == "Partly Sunny":
            day['icon'] = "Partly Sunny"
        elif day['condition'] == "Mostly Cloudy":
            day['icon'] = "Overcast"
        elif day['condition'] == "Chance of Storm":
            day['icon'] = "Storm"
        elif day['condition'] == "Rain":
            day['icon'] = "Rain"
        elif day['condition'] == "Chance of Snow":
            day['icon'] = "Snow"
        elif day['condition'] == "Cloudy":
            day['icon'] = "Overcast"
        elif day['condition'] == "Mist":
            day['icon'] = "Fog"
        elif day['condition'] == "Storm":
            day['icon'] = "Storm"
        elif day['condition'] == "Chance of TStorm":
            day['icon'] = "Thunderstorm"
        elif day['condition'] == "Sleet":
            day['icon'] = "Rain and Snow"
        elif day['condition'] == "Snow":
            day['icon'] = "Snow"
        elif day['condition'] == "Icy":
            day['icon'] = "Snow"
        elif day['condition'] == "Dust":
            day['icon'] = "Snow"
        elif day['condition'] == "Fog":
            day['icon'] = "Fog"
        elif day['condition'] == "Smoke":
            day['icon'] = "Fog"
        elif day['condition'] == "Haze":
            day['icon'] = "Fog"
        elif day['condition'] == "Flurries":
            day['icon'] = "Snow"
        elif day['condition'] == "Light Rain":
            day['icon'] = "Rain"
        elif day['condition'] == "Snow Showers":
            day['icon'] = "Rain and Snow"
        elif day['condition'] == "Hail":
            day['icon'] = "Storm"

    currentimage = imagepath + current_conditions['icon'] + ".png"
    day1image = imagepath + day1['icon'] + ".png"
    day2image = imagepath + day2['icon'] + ".png"
    day3image = imagepath + day3['icon'] + ".png"
    day4image = imagepath + day4['icon'] + ".png"

    title = forcast_info['city']

    if use_metric:
        current_temp = current_conditions['temp_c'] + " c"
        windspeed_kph = windspeed_mph * 1.609
        windspeed_kph = int(windspeed_kph)
        windspeed_mph = str(windspeed_mph)
        windspeed_kph = str(windspeed_kph)
        wind = wind.replace(windspeed_mph, windspeed_kph)
        wind = wind.replace("mph", "kph")

        for temp in weather['forecasts']:
            temp['low'] = int(temp['low']) - 32
            temp['low'] = int(temp['low']) * 5
            temp['low'] = int(temp['low']) / 9
            temp['low'] = str(temp['low']) + " c"
            temp['high'] = int(temp['high']) - 32
            temp['high'] = int(temp['high']) * 5
            temp['high'] = int(temp['high']) / 9
            temp['high'] = str(temp['high']) + " c"

    else:
        current_temp = current_conditions['temp_f'] + " f"
        for temp in weather['forecasts']:
            temp['low'] = temp['low'] + " f"
            temp['high'] = temp['high'] + " f"

    return render_template('weather.html',
        current_conditions = current_conditions,
        current_temp = current_temp,
        currentimage = currentimage,
        day1image = day1image,
        day2image = day2image,
        day3image = day3image,
        day4image = day4image,
        title = title,
        wind = wind,
        day1 = day1,
        day2 = day2,
        day3 = day3,
        day4 = day4,
    )

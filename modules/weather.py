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

    title = forcast_info['city']

    if use_metric:
        current_temp = current_conditions['temp_c']
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
            temp['high'] = int(temp['high']) - 32
            temp['high'] = int(temp['high']) * 5
            temp['high'] = int(temp['high']) / 9

    else:
        current_temp = current_conditions['temp_f']

    return render_template('weather.html',
        title = title,
        current_conditions = current_conditions,
        current_temp = current_temp,
        wind = wind,
        day1 = day1,
        day2 = day2,
        day3 = day3,
        day4 = day4,
    )

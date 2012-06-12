from flask import Flask, jsonify, render_template
from pywapi.pywapi import get_weather_from_google
import re

from Maraschino import app
from maraschino.tools import *

@app.route('/xhr/weather')
@requires_auth
def xhr_weather():

    location = get_setting_value('weather_location')
    use_celcius = get_setting_value('weather_use_celcius') == '1'
    use_kilometers = get_setting_value('weather_use_kilometers') == '1'
    compact_view = get_setting_value('weather_compact') == '1'
    weather = get_weather_from_google(location)

    current_conditions = weather['current_conditions']
    forcast_info = weather['forecast_information']

    wind = current_conditions['wind_condition']
    windspeed_mph = re.findall("\d+", wind)
    windspeed_mph = int(windspeed_mph[0])

    imagepath = "/static/images/weather/"

    if ": N" in wind:
        wind_image = imagepath + "N.png"
    elif ": E" in wind:
        wind_image = imagepath + "E.png"
    elif ": S" in wind:
        wind_image = imagepath + "S.png"
    elif ": W" in wind:
        wind_image = imagepath + "W.png"
    elif ": NE" in wind:
        wind_image = imagepath + "NE.png"
    elif ": SE" in wind:
        wind_image = imagepath + "SE.png"
    elif ": SW" in wind:
        wind_image = imagepath + "SW.png"
    elif ": NW" in wind:
        wind_image = imagepath + "NW.png"

    conditions = (
        {
            'image': 'Rain',
            'conditions':[

                'Chance of Rain',
                'Chance of Showers',
                'Light rain',
                'Freezing Drizzle',
                'Drizzle',
                'Scattered Showers',
                'Showers',
                'Rain Showers',
                'Rain'
            ]
        },
        {
            'image': 'Thunderstorm',
            'conditions': [

                'Thunderstorm',
                'Scattered Thunderstorms',
                'Chance of TStorm'
            ]
        },
        {
            'image': 'Sunny',
            'conditions': [

                'Clear',
                'Sunny',
                'Mostly Sunny'
            ]
        },
        {
            'image': 'Overcast',
            'conditions': [

                'Overcast',
                'Mostly Cloudy',
                'Cloudy'
            ]
        },
        {
            'image': 'Snow',
            'conditions': [

                'Light Snow',
                'Chance of Snow',
                'Snow',
                'Icy',
                'Dust',
                'Flurries'
            ]
        },
        {
            'image': 'Partly Sunny',
            'conditions': [

                'Partly Cloudy',
                'Partly Sunny'
            ]
        },
        {
            'image': 'Overcast',
            'conditions': [

                'Overcast',
                'Mostly Cloudy',
                'Cloudy'
            ]
        },
        {
            'image': 'Rain and Snow',
            'conditions': [

                'Rain and Snow',
                'Sleet',
                'Snow Showers'
            ]
        },
        {
            'image': 'Storm',
            'conditions': [

                'Chance of Storm',
                'Storm',
                'Hail'
            ]
        },
        {
            'image': 'Fog',
            'conditions': [

                'Mist',
                'Fog',
                'Smoke',
                'Haze'
            ]
        },
    )

    for condition in conditions:
        if current_conditions['condition'] in condition['conditions']:
            current_conditions['icon'] = condition['image']

        for day in weather['forecasts']:
            if day['condition'] in condition['conditions']:
                day['icon'] = condition['image']

    day1 = weather['forecasts'][0]
    day2 = weather['forecasts'][1]
    day3 = weather['forecasts'][2]
    day4 = weather['forecasts'][3]

    currentimage = imagepath + current_conditions['icon'] + ".png"
    day1image = imagepath + day1['icon'] + ".png"
    day2image = imagepath + day2['icon'] + ".png"
    day3image = imagepath + day3['icon'] + ".png"
    day4image = imagepath + day4['icon'] + ".png"

    title = forcast_info['city']
    degrees = unichr(176)

    if use_celcius:
        current_temp = current_conditions['temp_c'] + degrees + "C"

        for temp in weather['forecasts']:
            temp['low'] = int(temp['low']) - 32
            temp['low'] = int(temp['low']) * 5
            temp['low'] = int(temp['low']) / 9
            temp['low'] = str(temp['low']) + degrees + "C"
            temp['high'] = int(temp['high']) - 32
            temp['high'] = int(temp['high']) * 5
            temp['high'] = int(temp['high']) / 9
            temp['high'] = str(temp['high']) + degrees + "C"

    else:
        current_temp = current_conditions['temp_f'] + degrees + "F"
        for temp in weather['forecasts']:
            temp['low'] = temp['low'] + degrees + "F"
            temp['high'] = temp['high'] + degrees + "F"

    if use_kilometers:
        windspeed_kph = windspeed_mph * 1.609
        windspeed_kph = int(windspeed_kph)
        windspeed_mph = str(windspeed_mph)
        windspeed_kph = str(windspeed_kph)
        wind = wind.replace(windspeed_mph, windspeed_kph)
        wind = wind.replace("mph", "kph")

    return render_template('weather.html',
        current_conditions = current_conditions,
        compact_view = compact_view,
        current_temp = current_temp,
        currentimage = currentimage,
		wind_image = wind_image,
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

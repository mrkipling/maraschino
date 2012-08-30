from flask import render_template
from maraschino import app, WEBROOT
from maraschino.tools import requires_auth, get_setting_value
from weatherfeed.weatherfeed import Weather
from jinja2.filters import FILTERS
import datetime


def meridian():
    meridian = get_setting_value('weather_time') == '0'
    return meridian


def get_time():
    now = datetime.datetime.now()
    if meridian():
        return now.strftime('%I:%M')
    else:
        return now.strftime('%H:%M')


def get_date():
    now = datetime.datetime.now()
    return now.strftime('%A %d %B')


def weather_temp(temp):
    if not temp.isdigit():
        return temp

    temp = int(temp)
    degrees = unichr(176)

    if get_setting_value('weather_use_celcius') == '1':
        temp = temp - 32
        temp = temp * 5
        temp = temp / 9
        return str(int(temp)) + degrees + 'C'
    else:
        return str(int(temp)) + degrees + 'F'

FILTERS['weather_temp'] = weather_temp


def weather_speed(speed):
    if not speed.isdigit():
        return speed

    speed = int(speed)

    if get_setting_value('weather_use_kilometers') == '1':
        speed = speed * 1.609
        return str(int(speed)) + 'kph'
    else:
        return str(int(speed)) + 'mph'

FILTERS['weather_speed'] = weather_speed


@app.route('/xhr/weather/')
@requires_auth
def xhr_weather():
    
    location = get_setting_value('weather_location')
    use_kilometers = get_setting_value('weather_use_kilometers') == '1'
    compact_view = get_setting_value('weather_compact') == '1'

    w = Weather(location, metric=False)

    weather = {
        'current': w.currentConditions,
        'forecast': w.forecast
    }

    wind = int(weather['current']['wind']['degrees'])

    if wind in range(0, 22) or wind in range(338, 360):
        img = 'N'
    elif wind in range(68, 112):
        img = 'E'
    elif wind in range(158, 202):
        img = 'S'
    elif wind in range(248, 292):
        img = 'W'
    elif wind in range(22, 68):
        img = 'NE'
    elif wind in range(112, 158):
        img = 'SE'
    elif wind in range(202, 248):
        img = 'SW'
    elif wind in range(292, 338):
        img = 'NW'

    wind_image = '%s/static/images/weather/%s.png' % (WEBROOT, img)

    conditions = [
        {
            'image': 'Rain', 
            'conditions': ['rain', 'shower', 'drizzle']
        },
        {
            'image': 'Thunderstorm',
            'conditions': ['thunder']
        },
        {
            'image': 'Sunny',
            'conditions': ['sunny', 'clear']
        },
        {
            'image': 'Overcast',
            'conditions': ['overcast', 'cloudy']
        },
        {
            'image': 'Snow',
            'conditions': ['snow']
        },
        {
            'image': 'Storm',
            'conditions': ['storm', 'hail']
        },
        {
            'image': 'Fog',
            'conditions': ['mist', 'fog', 'smoke', 'haze']
        }
    ]

    for a in conditions:
        for cond in a['conditions']:
            if cond in weather['current']['type'].lower():
                weather['current']['image'] = '%s/static/images/weather/%s.png' % (WEBROOT, a['image'])

            for day in weather['forecast']:
                if day:
                    if cond in day['day']['type'].lower():
                        day['image'] = '%s/static/images/weather/%s.png' % (WEBROOT, a['image'])

    return render_template('weather.html',
        compact_view=compact_view,
        weather=weather,
        wind_image=wind_image,
        time = get_time(),
        date = get_date(),
        meridian = meridian()
    )

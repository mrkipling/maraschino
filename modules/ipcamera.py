import urllib2
from flask import jsonify, render_template, request
import base64

from Maraschino import app
from maraschino.tools import *
from maraschino import logger

foscammjeg_settings = {
    #uses base control
    'control_base': '/decoder_control.cgi?command=',
    'down': '0',
    'down_stop': '1',
    'up': '2',
    'up_stop': '3',
    'left': '4',
    'left_stop': '5',
    'right': '6',
    'right_stop': '7',
    'center': '25',
    'vertical_patrol': '26',
    'stop_vertical_patrol': '27',
    'horizontal_patrol': '28',
    'stop_horizontal_patrol': '29',
    'preset_1': '31',
    'preset_2': '33',
    'preset_3': '35',
    'preset_4': '37',
    'set_preset_1': '30',
    'set_preset_2': '32',
    'set_preset_3': '34',
    'set_preset_4': '36',
    'ir_off': '95',
    'ir_on': '94',
    # uses camera settigns
    'camera_settings': '/camera_control.cgi?param=',
    'oi_output_high': '94',
    'oi_output_low': '95',
    'resolution': '0',
    'resolution_qvga': '0&value=8',
    'resolution_vga': '0&value=32',
    'brightness': '1',
    'contrast': '2',
    'mode': '3',
    'fifty': '3&value=0',
    'sixty': '3&value=1',
    'outdoor': '3&value=2',
    'flippandmirror': '5',
    'default': '5&value=3',
    'flip': '5&value=1',
    'mirror': '5&value=2',
    'fam': '5&value=0',
    # uses set_alarm
    'set_alarm': '/set_alarm.cgi?',
    'motion_armed_on': '&motion_armed=1',
    'motion_armed_off': '&motion_armed=0',
    'motion_sensitivity_high': '&motion_sensitivity=0',
    'motion_sensitivity_medium': '&motion_sensitivity=1',
    'motion_sensitivity_low': '&motion_sensitivity=2',
    'motion_sensitivity_ultralow': '&motion_sensitivity=3',
    'input_armed_yes': '&input_armed=0',
    'input_armed_no': '&input_armed=1',
    # uses set_misc
    'set_misc': '/set_misc.cgi?',
    'led_mode_always_off': '&led_mode=2',
    'led_mode_blink' :'&led_mode=1' ,
    'led_mode_blink_once': '&led_mode=0',
    # stream urls
    'videostream': '/videostream.cgi'
    }

def camera_url(login=True):
    credentials = ''
    ip = get_setting_value('ipcamera_ip')
    port = get_setting_value('ipcamera_port')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')

    if login and username and password:
        credentials = '%s:%s@' % (username, password)

    return 'http://%s%s:%s' % (credentials, ip, port)


def send_camera_request(cat, arg):
    type = get_setting_value('ipcamera_type')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')
    url = camera_url(login=False)
    if type == 'foscammjeg':
        url += foscammjeg_settings[cat] + foscammjeg_settings[arg]
    elif type == 'foscammp4':
        url += foscammjeg_settings['control_base'] + foscammjeg_settings[arg]
    else:
        logger.log('IPCamera Error :: Missing camera type', 'INFO')

    try:
        r = urllib2.Request(url)
        if username and password:
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            r.add_header('Authorization', 'Basic %s' % base64string)
        data = urllib2.urlopen(r).read()
        logger.log('IPCamera :: Webcam is to turn %s' % (arg), 'INFO')
    except Exception as e:
        data = False
        logger.log('IPCamera Error :: Error on %s -> %s call :: %s' % (cat, arg, e), 'DEBUG')

    return jsonify({'status': data})


@app.route('/xhr/ipcamera/')
@requires_auth
def rend_page():
    type = get_setting_value('ipcamera_type')
    stream_url = '%s/videostream.cgi' % (camera_url())
    if type == 'foscammjeg':
        return render_template('ipcamera/foscammjeg.html', stream_url=stream_url)
    elif type == 'foscammp4':
        return render_template('ipcamera/foscammp4.html', stream_url=stream_url)


@app.route('/xhr/ipcamera/<cat>/<arg>/')
@requires_auth
def camera(cat, arg):
    return send_camera_request(cat, arg)

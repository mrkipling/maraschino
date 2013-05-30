#--coding: utf-8--

import urllib2
from flask import Flask, render_template, make_response, request, Response
import maraschino
from maraschino import *
from maraschino import app
from maraschino.tools import *
import base64

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

@app.route('/xhr/ipcamera')
@requires_auth
def rend_page():
    ip = get_setting_value('ipcamera_ip')
    port = get_setting_value('ipcamera_port')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')
    type = get_setting_value('ipcamera_type')
    stream_url = 'http://%s:%s@%s:%s/videostream.cgi' % (username, password, ip, port)
    if type == 'foscammjeg':
        return render_template('ipcamera/foscammjeg.html', stream_url = stream_url)  #  Rends the template
    elif type == 'test':
        return render_template('ipcamera/template.html', stream_url = stream_url)
    elif type == 'foscammp4':
        return render_template('ipcamera/foscammp4.html', stream_url = stream_url)

@app.route('/xhr/ipcamera/control/<arg>/')
@requires_auth
def control(arg):
    ip = get_setting_value('ipcamera_ip')
    port = get_setting_value('ipcamera_port')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')
    type = get_setting_value('ipcamera_type')
    url = 'http://%s:%s' % (ip, port)
    if type == 'foscammjeg':
        f_url = url + foscammjeg_settings['control_base'] + foscammjeg_settings[arg]
    elif type == 'test':
        pass #f_url = url + your_settings[''] + your_settings[arg]
    elif type == 'foscammp4':
        f_url = url + foscammjeg_settings['control_base'] + foscammjeg_settings[arg]
    else:
        logger.log('Missing camera type', 'INFO')

    try:
        request = urllib2.Request(f_url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        response = urllib2.urlopen(request).read()
        logger.log('Webcam is to turn %s :: Camera responded %s' % (arg, response), 'INFO')
    except:
        logger.log('Webcam is trying to turn %s :: Camera responed %s' % (arg, response), 'DEBUG')


@app.route('/xhr/ipcamera/camera_settings/<arg>/')
@requires_auth
def camera_settings(arg):
    ip = get_setting_value('ipcamera_ip')
    port = get_setting_value('ipcamera_port')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')
    type = get_setting_value('ipcamera_type')
    url = 'http://%s:%s' % (ip, port)
    if type == 'foscammjeg':
        f_url = url + foscammjeg_settings['camera_settings'] + foscammjeg_settings[arg] 
    elif type == 'test':
        pass # f_url = url + your_settings[''] + your_settings[arg]
    elif type == 'foscammp4':
        f_url = url + foscammjeg_settings['control_base'] + foscammjeg_settings[arg]
    else:
        logger.log('Camera type is missing %s,' % type, 'INFO')
    try:
        request = urllib2.Request(f_url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        response = urllib2.urlopen(request).read()
        logger.log('Webcam is to turn %s :: Camera responded %s' % (arg, response), 'INFO')
    except:
        logger.log('Webcam is trying to turn %s :: Camera responed %s' % (arg, response), 'DEBUG')

@app.route('/xhr/ipcamera/set_misc/<arg>/')
@requires_auth
def set_misc(arg):
    ip = get_setting_value('ipcamera_ip')
    port = get_setting_value('ipcamera_port')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')
    type = get_setting_value('ipcamera_type')
    url = 'http://%s:%s' % (ip, port)
    if type == 'foscammjeg':
        camera_type = foscammjeg_settings
        f_url = url + foscammjeg_settings['set_misc'] + foscammjeg_settings[arg] #change this before release.
    elif type == 'test':
        pass #f_url =url + your_settings[''] + your_settings[arg]
    elif type == 'foscammp4':
        f_url = url + foscammjeg_settings['control_base'] + foscammjeg_settings[arg]
    try:
        request = urllib2.Request(f_url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        response = urllib2.urlopen(request).read()
        logger.log('Webcam is to turn %s :: Camera responded %s' % (arg, response), 'INFO')
    except:
        logger.log('Webcam is trying to turn %s :: Camera responed %s' % (arg, response), 'DEBUG')

@app.route('/xhr/ipcamera/set_alarm/<arg>/')
@requires_auth
def set_alarm(arg):
    ip = get_setting_value('ipcamera_ip')
    port = get_setting_value('ipcamera_port')
    username = get_setting_value('ipcamera_username')
    password = get_setting_value('ipcamera_password')
    type = get_setting_value('ipcamera_type')
    url = 'http://%s:%s' % (ip, port)
    if type == 'foscammjeg':
        f_url = url + foscammjeg_settings['set_alarm'] + foscammjeg_settings[arg] 
    elif type == 'test':
        pass #f_url = url + your_settings[''] + your_settings[arg]
    elif type == 'foscammp4':
        f_url = url + foscammjeg_settings['control_base'] + foscammjeg_settings[arg]
    try:
        request = urllib2.Request(f_url)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        response = urllib2.urlopen(request).read()
        logger.log('Webcam is to turn %s :: Camera responded %s' % (arg, response), 'INFO')
    except:
        logger.log('Webcam is trying to turn %s :: Camera responed %s' % (arg, response), 'DEBUG')
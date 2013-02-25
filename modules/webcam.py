#--coding: utf-8--

import urllib2
from flask import Flask, render_template, make_response, request, Response
import maraschino
from maraschino import *
from maraschino import app
from maraschino.tools import *

# With foscam or clones this module should be plug and play. But commands like left, right, up and down might be reversed.
# Based on Foscam sdk 

# Im sure there are better ways to make a module then this one, but was the best i could do with my google fu.
# Thanks to N3MIS15 and gugahoi for all the help.
#
# I have written some comments on code that felt needed explaination. 
#
#

### Control settings ###
# uses control_base()
down = "0"
down_stop = "1"
up = "2"
up_stop = "3"
left = "4"
left_stop = "5"
right = "6"
right_stop = "7"
center= "25"
vertical_patrol = "26"
stop_vertical_patrol = "27"
horizontal_patrol = "28"
stop_horizontal_patrol = "29"
preset_1 = "31"
preset_2 = "33"
preset_3 = "35"
preset_4 = "37"
set_preset_1 = "30"
set_preset_2 = "32"
set_preset_3 = "34"
set_preset_4 = "36"
ir_off = "95"#
ir_on = "94"#
# decoder_control command 94 if turn off led/ 95 is turn on.
# uses camera_settings
io_output_high = "94"
io_output_low = "95"
resolution = "0" 
resolution_qvga = "&value=8"
resolution_vga = "&value=32" 
brightness = "1" 
contrast = "2"
mode = "3"
fifty = "&value=0"
sixty = "&value=1"
outdoor = "&value=2" 
flippandmirror = "5" 
default = "&value=3"
flip = "&value=1"
mirror = "&value=2"
fam = "&value=0"
# uses set_alarm
motion_armed_on = "&motion_armed=1"
motion_armed_off = "&motion_armed=0"
motion_sensitivity_high = "&motion_sensitivity=0"
motion_sensitivity_medium = "&motion_sensitivity=1"
motion_sensitivity_low = "&motion_sensitivity=2"
motion_sensitivity_ultralow = "&motion_sensitivity=3"
input_armed_yes = "&input_armed=0"
input_armed_no = "&input_armed=1"
# uses snap, not finished
count = "1"
# uses set_misc
led_mode_always_off = "&led_mode=2"
led_mode_blink = "&led_mode=1" 
led_mode_blink_once = "&led_mode=0" 
### End of control settings ##

### Url for http api webcam ###
# Used for basic controls like up, down mirror etc

def control_base():
    # Reading the ip address from the db.
    ip = get_setting_value('webcam_ip')
    port = get_setting_value('webcam_port') 
    username = get_setting_value('webcam_username')
    password = get_setting_value('webcam_password')
    # Returning the url below and ip on the first %s, port on the %s etc etc.
    return "http://%s:%s/decoder_control.cgi?user=%s&pwd=%s&command=" % (ip, port, username, password)

def camera_settings():
    ip = get_setting_value('webcam_ip')
    port = get_setting_value('webcam_port')
    username = get_setting_value('webcam_username')
    password = get_setting_value('webcam_password')
    return "http://%s:%s/camera_control.cgi?user=%s&pwd=%s&param=" % (ip, port, username, password)

# Not in use atm
def snap():
    ip = get_setting_value('webcam_ip')
    port = get_setting_value('webcam_port')
    username = get_setting_value('webcam_username')
    password = get_setting_value('webcam_password')
    return "http://%s:%s/snapshot.cgi?%s&user=%s&pwd=%s" % (ip, port, count, username, password)

def set_alarm():
    ip = get_setting_value('webcam_ip')
    port = get_setting_value('webcam_port')
    username = get_setting_value('webcam_username')
    password = get_setting_value('webcam_password')
    return "http://%s:%s/set_alarm.cgi?user=%s&pwd=%s" % (ip, port, username, password)

def set_misc():
    ip = get_setting_value('webcam_ip')
    port = get_setting_value('webcam_port')
    username = get_setting_value('webcam_username')
    password = get_setting_value('webcam_password')
    return "http://%s:%s/set_misc.cgi?user=%s&pwd=%s" % (ip, port, username, password)

#Renders the webcam.html and the stream. 
@app.route('/xhr/webcam')
@requires_auth
def rend():
    ip = get_setting_value('webcam_ip')
    port = get_setting_value('webcam_port')
    username = get_setting_value('webcam_username')
    password = get_setting_value('webcam_password')
    stream_url = "http://%s:%s@%s:%s/videostream.cgi" % (username, password, ip, port)
    return render_template('webcam.html', stream_url = stream_url)

### Movement controls, settings etc ###

@app.route('/xhr/webcam/turn_left') # The route Maraschino uses to run the function (Maraschino load '/xhr/ModuleName' as the modules default location)
@requires_auth # Use Maraschino's basic Authentication, else someone could have used: http://maraschinoip:port/xhr/Modulname/Function and executed the code without being authorized
def turn_left():
    try: # try to do something is it failes skip to the exception
        r = urllib2.urlopen(control_base() + left) # Opens the complete url
        x = r.read() # Reads the response of the webcam
        logger.log('Webcam is turning left, server responed %s' % x, 'INFO') # Logging what it tried, and inserts the response we got from 
    except:
        logger.log('Webcam is trying to turn left using function turn_left :: camera responed %s' % x, 'DEBUG')
    

@app.route('/xhr/webcam/turn_left_stop')
@requires_auth
def turn_left_stop():
    try:
        r = urllib2.urlopen(control_base() + left_stop)
        x = r.read()
        logger.log('Webcam is stopping turn left, :: Camera responded %s' % x, 'INFO')
    except:
        logger.log('Webcam is trying to stop turning left using function :: turn_left_stop :: Camera responed %s' % x, 'DEBUG')


@app.route('/xhr/webcam/turn_right')
@requires_auth
def turn_right():
    try:
        r = urllib2.urlopen(control_base() + right)
        x = r.read()
        logger.log('Webcam is to turn right, :: Camera responded %s' % x, 'INFO')
    except:
        logger.log('Webcam is trying to turn right using function :: turn_right :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_right_stop')
@requires_auth
def turn_right_stop():
    try:
        r = urllib2.urlopen(control_base() + right_stop)
        x = r.read()
        logger.log('Webcam is stopping turning RIGHT', 'INFO')
    except:
        logger.log('Webcam is trying to stop RIGHT using function :: turn_right_stop :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_up')
@requires_auth
def turn_up():
    try:
        r = urllib2.urlopen(control_base() + up)
        x = r.read()
        logger.log('Webcam is turning UP', 'INFO')
    except: 
        logger.log('Webcam is trying to stop move UP using function :: turn_ip :: Camera responed %s , DEBUG') % (up, x)
    

@app.route('/xhr/webcam/turn_up_stop')
@requires_auth
def turn_up_stop():
    try:
        r = urllib2.urlopen(control_base() + up_stop)
        x = r.read()
        logger.log('Webcam is stopping turning UP', 'INFO')
    except: 
        logger.log('Webcam is trying to stop move UP using function :: turn_up_stop :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/turn_down')
@requires_auth
def turn_down():
    try:
        r = urllib2.urlopen(control_base() + down)
        x = r.read()
        logger.log('Webcam is turning DOWN', 'INFO')
    except:
        logger.log('Webcam is trying to move DOWN using function :: turn_down :: Camera responded %s' % x, 'DEBUG')
    

@app.route('/xhr/webcam/turn_down_stop')
@requires_auth
def turn_down_stop():
    try:
        r = urllib2.urlopen(control_base() + down_stop)
        x = r.read()
        logger.log('Webcam is stopping turning DOWN', 'INFO')
    except:
        logger.log('Webcam is trying to stop move DOWN using function :: turn_down_stop :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/turn_center')
@requires_auth
def turn_center():
    try:
        r = urllib2.urlopen(control_base() + center)
        x = r.read()
        logger.log('Webcam is turning CENTER', 'INFO')
    except:
        logger.log('Webcam is trying to move CENTER using function :: turn_center :: Camera responded %s' % x, 'DEBUG')


@app.route('/xhr/webcam/turn_vertical_patrol')
@requires_auth
def turn_vertical_patrol():
    try:
        r = urllib2.urlopen(control_base() + vertical_patrol)
        x = r.read()
        logger.log('Webcam is turning in a VERTICAL PATROL', 'INFO')
    except:
        logger.log('Webcam is trying to move in a VERTICAL PATROL using function :: turn_vertical_patrol :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/turn_stop_vertical_patrol')
@requires_auth
def turn_stop_vertical_patrol():
    try:
        r = urllib2.urlopen(control_base() + stop_vertical_patrol)
        x = r.read()
        logger.log('Webcam is stopping VERTICAL PATROL', 'INFO')
    except:
        logger.log('Webcam is trying to stop VERTICAL PATROL using function :: turn_stop_vertical_patrol :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_horizontal_patrol')
@requires_auth
def turn_horizontal_patrol():
    try:
        r = urllib2.urlopen(control_base() + horizontal_patrol)
        x = r.read()
        logger.log('Webcam is turning in a HORIZONTAL PATROL', 'INFO')
    except:
        logger.log('Webcam is trying to move in a HORIZONTAL PATROL using function :: turn_horizontal_patrol :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_stop_horizontal_patrol')
@requires_auth
def turn_stop_horizontal_patrol():
    try:
        r = urllib2.urlopen(control_base() + stop_horizontal_patrol)
        x = r.read()
        logger.log('Webcam is trying to stop HORIZONTAL PATROL', 'INFO')
    except:
        logger.log('Webcam is trying stop HORIZONTAL PATROL using function :: turn_stop_horizontal_patrol :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_preset_1')
@requires_auth
def turn_preset_1():
    try:
        r = urllib2.urlopen(control_base() + preset_1)
        x = r.read()
        logger.log('Webcam is trying move to PRESET POSISION 1', 'INFO')
    except:
        logger.log('Webcam is trying move to PRESET POSISION 1 using function :: turn_preset_1 :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/turn_preset_2')
@requires_auth
def turn_preset_2():
    try:
        r = urllib2.urlopen(control_base() + preset_2)
        x = r.read()
        logger.log('Webcam is trying move to PRESET POSISION 2', 'INFO')
    except:
        logger.log('Webcam is trying move to PRESET POSISION 2 using function :: turn_preset_2 :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/turn_preset_3')
@requires_auth
def turn_preset_3():
    try:
        r = urllib2.urlopen(control_base() + preset_3)
        x = r.read()
        logger.log('Webcam is trying move to PRESET POSISION 3', 'INFO')
    except:
        logger.log('Webcam is trying move to PRESET POSISION 3 using function :: turn_preset_3 :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_preset_4')
@requires_auth
def turn_preset_4():
    try:
        r = urllib2.urlopen(control_base() + preset_4)
        x = r.read()
        logger.log('Webcam is trying move to PRESET POSISION 4', 'INFO')
    except:
        logger.log('Webcam is trying move to PRESET POSISION 4 using function :: turn_preset_4 :: Camera responded %s' % x, 'DEBUG')

    
@app.route('/xhr/webcam/set_set_preset_1')
@requires_auth
def set_set_preset_1():
    try:
        r = urllib2.urlopen(control_base() + set_preset_1)
        x = r.read()
        logger.log('Webcam is setting current posision to SET PRESET 1', 'INFO')
    except:
        logger.log('Webcam is setting current posision to SET PRESET 1 using function :: set_set_preset_1 :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/set_set_preset_2')
@requires_auth
def set_set_preset_2():
    try:
        r = urllib2.urlopen(control_base() + set_preset_2)
        x = r.read()
        logger.log('Webcam is setting current posision to SET PRESET 2', 'INFO')
    except:
        logger.log('Webcam is setting current posision to SET PRESET 2 using function :: set_set_preset_2 :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_set_preset_3')
@requires_auth
def set_set_preset_3():
    try:
        r = urllib2.urlopen(control_base() + set_preset_3)
        x = r.read()
        logger.log('Webcam is setting current posision to SET PRESET 3', 'INFO')
    except:
        logger.log('Webcam is setting current posision to SET PRESET 3 using function :: set_set_preset_3 :: Camera responded %s' % x, 'DEBUG')

    
@app.route('/xhr/webcam/set_set_preset_4')
@requires_auth
def set_set_preset_4():
    try:
        r = urllib2.urlopen(control_base() + set_preset_4)
        x = r.read()
        logger.log('Webcam is setting current posision to SET PRESET 4', 'INFO')
    except:
        logger.log('Webcam is setting current posision to SET PRESET 4 using function :: set_set_preset_4 :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_ir_off')
@requires_auth
def turn_ir_off():
    try:
        r = urllib2.urlopen(control_base() + ir_off)
        x = r.read()
        logger.log('IR off', 'INFO')
    except:
        logger.log('Webcam ir setting ir off using funtion :: turn_ir_off :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/turn_ir_on')
@requires_auth
def turn_ir_on():
    try:
        r = urllib2.urlopen(control_base() + ir_on)
        x = r.read()
        logger.log('IR on', 'INFO')
    except:
        logger.log('Webcam ir setting ir off using funtion :: turn_ir_on :: Camera responded %s' % x, 'DEBUG')

### Camera control

@app.route('/xhr/webcam/resolution_resolution_qvga')
@requires_auth
def resolution_resolution_qvga():
    try:
        r = urllib2.urlopen(camera_settings() + resolution +  resolution_qvga)
        x = r.read()
        logger.log('Webcam is setting feed to QVGA', 'INFO')
    except:
        logger.log('Webcam is setting feed to QVGA using  function :: resolution_resolution_qvga :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/resolution_resolution_vga')
@requires_auth
def resolution_resolution_vga():
    try:
        r = urllib2.urlopen(camera_settings() + resolution +  resolution_vga)
        x = r.read()
        logger.log('Webcam is setting feed to VGA', 'INFO')
    except:
        logger.log('Webcam is setting feed to VGA using  function :: resolution_resolution_vga :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/mode_fifty')
@requires_auth
def mode_fifty():
    try:
        r = urllib2.urlopen(camera_settings() + mode + fifty)
        x = r.read()
        logger.log('Webcam is setting camera to 50 HZ', 'INFO')
    except:
        logger.log('Webcam is setting camera to 50 HZ using function :: mode_fifty :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/mode_sixty')
@requires_auth
def mode_sixty():
    try:
        r = urllib2.urlopen(camera_settings() + mode + sixty)
        x = r.read()
        logger.log('Webcam is setting camera to 60 HZ', 'INFO')
    except:
        logger.log('Webcam is setting camera to 60 HZ using function :: mode_fifty :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/mode_outdoor')
@requires_auth
def mode_outdoor():
    try:
        r = urllib2.urlopen(camera_settings() + mode + outdoor)
        x = r.read()
        logger.log('Webcam is setting camera to outdoor mode', 'INFO')
    except:
        logger.log('Webcam failed setting camera to outdoor mode using function :: mode_outdoor :: Camera responded %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/flippandmirror_default')
@requires_auth
def flippandmirror_default():
    try:
        r = urllib2.urlopen(camera_settings() + flippandmirror + default)
        x = r.read()
        logger.log('Webcam is trying reset camera position', 'INFO')
    except:
        logger.log('Webcam failed trying reset camera position using function :: flippandmirror_default :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/flippandmirror_flip')
@requires_auth
def flippandmirror_flip():
    try:
        r = urllib2.urlopen(camera_settings() + flippandmirror + flip)
        x = r.read()
        logger.log('Webcam flipping feed upside down', 'INFO')
    except:
        logger.log('Webcam failed flipping camera feed using function :: flippandmirror_flip :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/flippandmirror_mirror')
@requires_auth
def flippandmirror_mirror():
    try:
        r = urllib2.urlopen(camera_settings() + flippandmirror + mirror)
        x = r.read()
        logger.log('Webcam feed is mirrored', 'INFO')
    except:
        logger.log('Webcam failed mirroring the feed using function :: flippandmirror_mirror :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/flippandmirror_fam')
@requires_auth
def flippandmirror_fam():
    try:
        r = urllib2.urlopen(camera_settings() + flippandmirror + fam)
        x = r.read()
        logger.log('Zhe camera is upside down and your looking in a damn mirror', 'INFO')
    except:
        logger.log('Webcam failed mirroring and flipping the feed using function :: flippandmirror_fam :: Camera responded %s' % x, 'DEBUG')

@app.route('/xhr/webcam/motion_armed_yes')
@requires_auth
def motion_armed_yes():
    try:
        r = urllib2.urlopen(set_alarm() + motion_armed_on)
        x = r.read()
        logger.log('Webcam motion detection turned ON', 'INFO')
    except:
        logger.log('Webcam failed activatin motion detection using function :: motion_armed_yes :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/motion_armed_no')
@requires_auth
def motion_armed_no():
    try:
        r = urllib2.urlopen(set_alarm() + motion_armed_off)
        x = r.read()
        logger.log('Webcam motion detection turned OFF', 'INFO')
    except:
        logger.log('Webcam failed disabling motion detection using function :: motion_armed_no :: Camera responed %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/set_motion_sensitivity_high')
@requires_auth
def set_motion_sensitivity_high():
    try:
        r = urllib2.urlopen(set_alarm() + motion_sensitivity_high)
        x = r.read()
        logger.log('Webcam MOTION DETECTION is set to HIGH', 'INFO')
    except:
        logger.log('Webcam failed setting MOTION DETECTION HIGH using function :: set_motion_sensitivity_high :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_motion_sensitivity_medium')
@requires_auth
def set_motion_sensitivity_medium():
    try:
        r = urllib2.urlopen(set_alarm() + motion_sensitivity_medium)
        x = r.read()
        logger.log('Webcam MOTION DETECTION is set to MEDIUM', 'INFO')
    except:
        logger.log('Webcam failed setting MOTION DETECTION MEDIUM using function :: set_motion_sensitivity_medium :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_motion_sensitivity_low')
@requires_auth
def set_motion_sensitivity_low():
    try:
        r = urllib2.urlopen(set_alarm() + motion_sensitivity_low)
        x = r.read()
        logger.log('Webcam MOTION DETECTION is set to LOW', 'INFO')
    except:
        logger.log('Webcam failed setting MOTION DETECTION LOW using function :: set_motion_sensitivity_low :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_motion_sensitivity_ultralow')
@requires_auth
def set_motion_sensitivity_ultralow():
    try:
        r = urllib2.urlopen(set_alarm() + motion_sensitivity_ultralow)
        x = r.read()
        logger.log('Webcam MOTION DETECTION is set to ULTRALOW', 'INFO')
    except:
        logger.log('Webcam failed setting MOTION DETECTION ULTRALOW using function :: set_motion_sensitivity_ultralow :: Camera responed %s' % x, 'DEBUG')
    
@app.route('/xhr/webcam/set_input_armed_yes')
@requires_auth
def set_input_armed_yes():
    try:
        r = urllib2.urlopen(set_alarm() + input_armed_yes)
        x = r.read()
        logger.log('Webcam INPUT is ARMED', 'INFO')
    except:
        logger.log('Webcam failed setting INPUT to ARMED using function :: input_armed_yes :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_input_armed_no')
@requires_auth
def set_input_armed_no():
    try:
        r = urllib2.urlopen(set_alarm() + input_armed_no)
        x = r.read()
        logger.log('Webcam INPUT is DISARMED', 'INFO')
    except:
        logger.log('Webcam failed setting INPUT to DISARMED using function :: input_armed_no :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_ir_mode_always_off')
@requires_auth
def set_led_mode_always_off():
    try:
        r = urllib2.urlopen(set_misc() + led_mode_always_off)
        x = r.read()
        logger.log('Leds are turned off', 'INFO')
    except:
        logger.log('Ip Camera failed to turn off led using function :: set_led_mode_always_off :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_ir_mode_blink')
@requires_auth
def set_led_mode_blink():
    try:
        r = urllib2.urlopen(set_misc() + led_mode_blink)
        x = r.read()
        logger.log('Leds are on', 'INFO')
    except:
        logger.log('Ip Camera failed to turn on led blink using function :: set_led_mode_mode_blink :: Camera responed %s' % x, 'DEBUG')

@app.route('/xhr/webcam/set_ir_mode_blink_once')
@requires_auth
def set_led_mode_blink_once():
    try:
        r = urllib2.urlopen(set_misc() + led_mode_blink_once)
        x = r.read()
        logger.log('Leds blinked once', 'INFO')
    except:
        logger.log('Ip Camera failed to turn on led blink once using function :: set_led_mode_blink_once :: Camera responed %s' % x, 'DEBUG')

#--coding: utf-8--

import urllib2
import urllib
from flask import *
from Maraschino import app
from maraschino.tools import *
from maraschino import *


@app.route('/xhr/telenor_sms/send/', methods=['post', 'get'])
def sms_send():
    username = get_setting_value('telenor_sms_username')
    pwd = get_setting_value('telenor_sms_password')
    input = request.form
    recipient = input['res']
    msg = input['mmsg']
    msg = msg.encode("ISO-8859-1") #  in case רזו
    msg = urllib.quote_plus(msg)
    sms_url = 'https://telenormobil.no/smapi/3/sms?sender=%s&password=%s&recipients=%s&sId=1000000000&content=%s' % (username, pwd, recipient, msg)
    status = 'processed=\"OK\"'
    
    try:
        response = urllib2.urlopen(sms_url).read()
        if status in response:
            logger.log('Your sms was sendt to the server','INFO')
            result = 'SENDT'
        else:
            logger.log('Your sms was not sendt to the server :: server responed %s' % response, 'DEBUG')
            result = "NOT SENDT! check log"

    except:
        result = "EVERYTHING failed"
    
    return render_template('telenor_sms.html', 
        result = result,
        status = status)
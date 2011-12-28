from flask import Flask, jsonify, render_template, send_file
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from lib.tools import *

def spotweb_url():
    url = '%s/api?apikey=%s' % (get_setting_value('spotweb_url'), get_setting_value('spotweb_api'))
    
#    if using_auth():
#        return 'http://%s%s' % (login_string(), url)
        
    return 'http://%s' % (url)
    
def spotweb_url_no_api():
    url = '%s/' % get_setting_value('spotweb_url')

#    if using_auth():
#        return 'http://%s%s' % (login_string(), url)

    return 'http://%s' % (url)

@app.route('/xhr/spotweb')
@requires_auth
def xhr_spotweb():
    try:
        url = '%s&t=tvsearch&cat=5000,2000&o=json&limit=%s' % (spotweb_url(), get_setting_value('spotweb_items'))
        result = urllib.urlopen(url).read()
        spotweb = json.JSONDecoder().decode(result)
    except:
        print 'Failed'
        raise Exception
    
    #if spotweb.rfind('ID') < 0:
    #    spotweb = ''

    # spot info @ ?page=getspot&messageid=
    #
    return render_template('spotweb.html', url = spotweb_url_no_api(), spotweb = spotweb,)
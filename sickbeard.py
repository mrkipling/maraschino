from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from tools import *

SICKBEARD_IP = get_setting_value('sickbeard_ip')
SICKBEARD_PORT = get_setting_value('sickbeard_port')
SICKBEARD_API = get_setting_value('sickbeard_api')
try:
	SICKEBARD_USER = get_setting_value('sickbeard_user')
	SICKBEARD_PW = get_setting_value('sickbeard_pw')
	LOGIN = '%s:%s@' % (SICKEBARD_USER, SICKBEARD_PW)
except:
	LOGIN = ''
	
SICKBEARD_URL = 'http://%s%s:%s/api/%s' % (LOGIN, SICKBEARD_IP, SICKBEARD_PORT, SICKBEARD_API)

@app.route('/xhr/sickbeard')
def xhr_sickbeard():
	try:
		url = '%s/?cmd=future&sort=date' % (SICKBEARD_URL)
		result = urllib.urlopen(url).read()
 		sickbeard = json.JSONDecoder().decode(result)
	except:
		raise Exception
		
	if sickbeard['result'].rfind('success') >= 0:
		sickbeard = sickbeard['data']
	else:
		sickbeard = ''
		
	return render_template('sickbeard.html',
		url = '%s:%s' %(SICKBEARD_IP, SICKBEARD_PORT) ,
		sickbeard = sickbeard,
		missed = sickbeard['missed'],
		today = sickbeard['today'],
		soon = sickbeard['soon']
	)
	
@app.route('/sickbeard/search_ep/<tvdbid>/<season>/<episode>')
@requires_auth
def search_ep(tvdbid, season, episode):
	try:
		url = '%s/?cmd=episode.search&tvdbid=%s&season=%s&episode=%s' %(SICKBEARD_URL, tvdbid, season, episode)
		result = urllib.urlopen(url).read()
 		sickbeard = json.JSONDecoder().decode(result)
	except:
		raise Exception
		
	if sickbeard['result'].rfind('success') >= 0:
		return sickbeard
		
	return ''
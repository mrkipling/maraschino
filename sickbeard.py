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
URL = 'http://%s%s:%s/' % (LOGIN, SICKBEARD_IP, SICKBEARD_PORT)

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
		soon = sickbeard['soon'],
		later = sickbeard['later'],
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
	
@app.route('/sickbeard/get_plot/<tvdbid>/<season>/<episode>')
def get_plot(tvdbid, season, episode):
	try:
		url = '%s/home/plotDetails?show=%s&episode=%s&season=%s' %(URL, tvdbid, episode, season)
		plot = urllib.urlopen(url).read()
	except:
		raise Exception
		
	if plot:
		return plot
		
	return ''

@app.route('/sickbeard/get_all')
def get_all():
	try:
		url = '%s/?cmd=shows&sort=name' %(SICKBEARD_URL)
		result = urllib.urlopen(url).read()
 		sickbeard = json.JSONDecoder().decode(result)
	except:
		raise Exception
		
	if sickbeard['result'].rfind('success') >=0:
		sickbeard = sickbeard['data']
		for show in sickbeard:
			sickbeard[show]['url'] = get_pic(sickbeard[show]['tvdbid'], 'banner')
	
	return render_template('sickbeard-all.html',
		sickbeard = sickbeard,
	)

@app.route('/sickbeard/get_show_info/<tvdbid>')
def show_info(tvdbid):
	try:
		url = '%s/?cmd=show&tvdbid=%s' %(SICKBEARD_URL, tvdbid)
		result = urllib.urlopen(url).read()
 		sickbeard = json.JSONDecoder().decode(result)
	except:
		raise Exception
		
	if sickbeard['result'].rfind('success') >= 0:
		sickbeard = sickbeard['data']
		sickbeard['url'] = get_pic(tvdbid, 'banner')
		sickbeard['tvdb'] = tvdbid
	
	return render_template('sickbeard-show.html',
		sickbeard = sickbeard,
	)

@app.route('/sickbeard/get_season/<tvdbid>/<season>')
def get_season(tvdbid, season):
	try:
		url = '%s/?cmd=show.seasons&tvdbid=%s&season=%s' %(SICKBEARD_URL, tvdbid, season)
		result = urllib.urlopen(url).read()
 		sickbeard = json.JSONDecoder().decode(result)
	except:
		raise Exception
		
	if sickbeard['result'].rfind('success') >= 0:
		sickbeard = sickbeard['data']
	
	return render_template('sickbeard-season.html',
		sickbeard = sickbeard,
	)

@app.route('/sickbeard/history/<limit>')
def history(limit):
	try:
		url = '%s/?cmd=history&limit=%s' %(SICKBEARD_URL, limit)
		result = urllib.urlopen(url).read()
 		sickbeard = json.JSONDecoder().decode(result)
	except:
		raise Exception
		
	if sickbeard['result'].rfind('success') >= 0:
		sickbeard = sickbeard['data']
		for show in sickbeard:
			show['image'] = get_pic(show['tvdbid'])
	
	return render_template('sickbeard-history.html',
		history = sickbeard,
	)
	
def get_pic(tvdb, style='banner'):
	url = '%s:%s' %(SICKBEARD_IP, SICKBEARD_PORT)
	return 'http://%s/showPoster/?show=%s&which=%s' %(url, tvdb, style)

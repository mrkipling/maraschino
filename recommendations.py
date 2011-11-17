from flask import Flask, jsonify, render_template, request
import hashlib, json, jsonrpclib, urllib, random
from pprint import pprint

from maraschino import app
from settings import *
from noneditable import *
from tools import *

TRAKT_API_KEY = get_setting_value('trakt_api_key')
TRAKT_USERNAME = get_setting_value('trakt_username')
TRAKT_PASSWORD = get_setting_value('trakt_password')

@app.route('/xhr/recommendations')
def xhr_recommendations():
	rand = random.randint(0,10)
	# setting up username and password to pass to POST request
	try:
		params = {
	  	'username': TRAKT_USERNAME,
	  	'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest()
		}
	except:
		params = {}
	
	# Movie show recommendation request
	url = 'http://api.trakt.tv/recommendations/movies/%s' % (TRAKT_API_KEY)
	params = urllib.urlencode(params)
	result = urllib.urlopen(url, params).read()
	result = json.JSONDecoder().decode(result)
	#if result is empty, set mov object as empty
	if not result:
		mov = {}
	else:
		movie = result[rand]
		
		# checking if imdb id is present, otherwise, use tvdb id as per trakt instructions
		if movie['imdb_id'] != '':
			movie_id = movie['imdb_id']
		else:
			movie_id = movie['tmdb_id']
			
		# creating movie object to pass to template	
		mov = {}
		mov['url'] = movie['url']
		mov['title'] = movie['title']
		mov['image'] = movie['images']['poster']
		mov['overview'] = movie['overview']
		mov['year'] = movie['year']
		mov['liked'] = movie['ratings']['percentage']
		mov['id'] = movie_id
		mov['watchlist'] = movie['in_watchlist']
	
	# making TV Show Recommendation request
	url = 'http://api.trakt.tv/recommendations/shows/%s' % (TRAKT_API_KEY)
	result = urllib.urlopen(url, params).read()
	result = json.JSONDecoder().decode(result)
	#if result is empty, set tv object as empty
	if not result:
		tv = {}
	else:
		tv_result = result[rand]
		
		# checking if imdb id is present, otherwise, use tvdb id as per trakt instructions
		if tv_result['imdb_id'] != '':
			tv_id = tv_result['imdb_id']
		else:
			tv_id = tv_result['tmdb_id']
			
		# creating movie object to pass to template	
		tv = {}
		tv['url'] = tv_result['url']
		tv['title'] = tv_result['title']
		tv['image'] = tv_result['images']['poster']
		tv['overview'] = tv_result['overview']
		tv['year'] = tv_result['year']
		tv['liked'] = tv_result['ratings']['percentage']
		tv['id'] = tv_id
		tv['watchlist'] = tv_result['in_watchlist']

	
	return render_template('recommendations.html',
		movie = mov,
		tv = tv,
	  )
	  
@app.route('/trakt/add_to_watchlist/<movieid>/<title>/<year>/')
@requires_auth
def add_to_watchlist(movieid, title, year):
		try:
			params = {
		  	'username': TRAKT_USERNAME,
		  	'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest(),
				'movies': {	'imdb_id': movieid, 
										'title': title, 
										'year': year
									}
			}
		except:
			raise Exception
			
		try:
			url = 'http://api.trakt.tv/movie/watchlist/%s' % (TRAKT_API_KEY)
			params = urllib.urlencode(params)
			result = urllib.urlopen(url, params).read()
			result = json.JSONDecoder().decode(result)
			
			if result['status'] == 'success':
				return 'Item successfully added to Watchlist'
			else:
				return 'I\'m sorry, an error ocurred: %s' % (result)
		
		except:
			return ''

@app.route('/trakt/dismiss_rec/<movieid>/<title>/<year>/')
@requires_auth
def dimiss_reccomendation(movieid, title, year):
		try:
			params = {
		  	'username': TRAKT_USERNAME,
		  	'password': hashlib.sha1(TRAKT_PASSWORD).hexdigest(),
				'imdb_id': movieid, 
				'title': title, 
				'year': year
			}
		except:
			raise Exception
			
		try:
			url = 'http://api.trakt.tv/recommendations/movies/dismiss/%s' % (TRAKT_API_KEY)
			params = urllib.urlencode(params)
			result = urllib.urlopen(url, params).read()
			result = json.JSONDecoder().decode(result)
			
			if result['status'] == 'success':
				return '%s: %s' % (result['status'], result['message'])
			else:
				return 'I\'m sorry, an error ocurred: %s' % (result)
		
		except:
			return ''

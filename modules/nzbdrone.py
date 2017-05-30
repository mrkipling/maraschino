from flask import jsonify, render_template, request, send_file
import urllib2
import base64
import StringIO
import json
import datetime

from maraschino import app
from maraschino.tools import *
import maraschino
import requests

def nzbdrone_http():
    if get_setting_value('nzbdrone_https') == '1':
        return 'https://'
    else:
        return 'http://'

def nzbdrone_external_url():
    url_base = get_setting_value('nzbdrone_ip')
    webroot = get_setting_value('nzbdrone_webroot')
    
    if url_base:
        return url_base
    if webroot:
        return webroot


def nzbdrone_url(params = None):
    port = get_setting_value('nzbdrone_port')
    url_base = get_setting_value('nzbdrone_ip')
    webroot = get_setting_value('nzbdrone_webroot')
    
    if port:
        url_base = '%s:%s' % (url_base, port)
        
    if webroot:
        url_base = '%s/%s' % (url_base, webroot)
        
    url = url_base
    
    return nzbdrone_http() + url
    
def nzbdrone_api(params = None):
    api = get_setting_value('nzbdrone_api')
    url = nzbdrone_url() + params
    headers = {'X-Api-Key': api}
    return requests.get(url, headers=headers)
    
def log_exception(e):
    logger.log('NZBDrone :: EXCEPTION -- %s' % e, 'DEBUG') 

def get_episode_overview(params = None):
    params = '/api/episode/' + str(params)
    episodeoverview = nzbdrone_api(params=params).json()
    return episodeoverview['overview']
    
    
def search_episode(params = None):
    url = '/api/command/'
    api = get_setting_value('nzbdrone_api')
    url = nzbdrone_url() + url
    headers = {'X-Api-Key': api}
    ids = str(params)
    if str(requests.post(url, headers=headers, data=json.dumps({'name':'episodesearch', 'episodeIds':[ids]}))) == '<Response [201]>':
        return True
    else:
        return False

@requires_auth
@app.route('/xhr/nzbdrone/')
def xhr_nzbdrone_getshows():
    print get_setting_value('nzbdrone_external_server')
    url = nzbdrone_api(params='/api/series')
    json_string = url.json()   #opens previous json
    series = {}            #creates a list
    var1 = 0            #sets var1 up to be incremented
    for increment in json_string:   #just here to drop us down a level in the json
        try:            #catches the final error
            series.update({json_string[var1]['title']:[json_string[var1]['id'], json_string[var1]['titleSlug'], json_string[var1]['tvdbId']]}) #sets a variable to a dict of the id/titleslug
            var1 += 1           #increments var1 so we can move to the next entry in the json
        except:                 #error catching
            break               #breaks the loop when it hits an error
    
    images = series
    return render_template('nzbdrone.html',
        external_server = get_setting_value('nzbdrone_external_server'),
        port = get_setting_value('nzbdrone_port'),
        url = nzbdrone_external_url(),
        images = images
        
    ) #renders the result to maraschino
    
@requires_auth   
@app.route('/xhr/nzbdrone/search')
def nzbdrone_search(message=None, params = None):
    nzbdrone = {}
    
    logger.log('NZBDrone :: params is %s' % (params), 'DEBUG')
    try:
        query = request.args['name']
        params = '/api/Series/lookup/?term=' + query
    except:
        pass
        
    logger.log('NZBDrone :: params is %s' % (params), 'DEBUG')
    try:
        nzbdrone = nzbdrone_api(params=params)
        amount = len(nzbdrone.json())
        nzbdrone = nzbdrone.json()
        logger.log('NZBDrone :: found %i series matching %s' % (amount, query), 'INFO')
        if amount != 0:
            try:
                var = 0
                series_list = []
                for increment in nzbdrone:
                    try:
                        titles = []
                        series_title = nzbdrone[var]['title']
                        series_tvdbid = nzbdrone[var]['tvdbId']
                        series_titleslug = nzbdrone[var]['titleSlug']
                        series_seasons = nzbdrone[var]['seasons']
                        poster = nzbdrone[var]['remotePoster']
                        overview = nzbdrone[var]['overview']
                        overview = (overview[:500] + '..') if len(overview) > 500 else overview
                        overview = (overview) if len(overview) != 0 else 'No description available for this show.'
                        titles.append(series_title)
                        titles.append(series_tvdbid)
                        titles.append(series_titleslug)
                        titles.append(series_seasons)
                        titles.append(poster)
                        titles.append(overview)
                        series_list.append(titles)
                        var += 1
                    except:
                        break
               
                params = '/api/profile'    
                profile_list = nzbdrone_api(params=params)
                var = 0
                profiles = {}
                profile_list = profile_list.json()
                for incrementing in profile_list:
                    try:
                        profiles.update({profile_list[var]['id']:profile_list[var]['name']})
                        var += 1
                        logger.log('NZBDrone :: %s' % (profiles), 'DEBUG')
                    except:
                        break
                        
                params = '/api/Rootfolder'
                folders = {}
                folder_list = nzbdrone_api(params=params)
                folder_list = folder_list.json()
                var = 0
                for incrementing in folder_list:
                    try:
                        folders.update({folder_list[var]['path']:(round(float(folder_list[var]['freeSpace']) / (1000000000)))})
                        var += 1
                        logger.log('NZBDrone :: %s' % (folders), 'DEBUG')
                    except:
                        break
            except:
                log_exception(e)
        else:
            return render_template('nzbdrone/search.html', error='No series with "%s" were found' % (query), nzbdrone='results')
               
    except Exception as e:
        log_exception(e)
        nzbdrone = None
                
    else:
        logger.log('NZBDrone :: Loading search template', 'DEBUG')
        nzbdrone = None
       
    return render_template('nzbdrone/search.html',
        titles = series_list,
        profiles = profiles,
        folders = folders,
        url = nzbdrone_external_url(),
        port = get_setting_value('nzbdrone_port'),
        external_server = get_setting_value('nzbdrone_external_server'),
        error = message
    )

@app.route('/xhr/nzbdrone/add_show/<tvdbid>/<title>/<qualityprofile>/<seriestype>/<path>/<titleslug>/<monitoredseasons>')
def add_series(tvdbid, title, qualityprofile, seriestype, path, titleslug):
    params = '/api/Series/lookup/?term=tvdbid:'+tvdbid
    season = nzbdrone_api(params=params)
    season = season.json()[0]['seasons']
    
    try:
        logger.log('NZBDrone :: Adding %s to library' % (title), 'INFO')
        title = str(title)
        tvdbId = str(tvdbid)
        qualityprofile = str(qualityprofile)
        seriestype = str(seriestype)
        path = str((urllib2.unquote(path)))
        titleslug = str(titleslug)
        monitored = str(True)
        seasonFolder = str(True)
        var = len(season)
        var -= 1
        s = {}
        seasons = []
        print seasons
        
        '''very kludgey, if you return the seasons starting at 0 it fails. So we have to go backwards from the last season 
        You also can't have double quotes which is why we build another dict to remove them from the json
        and lastly, we have to roll it all into a list'''
        for increment in xrange (var, 0, -1):
            try:
                s = {'seasonNumber': var, 'monitored': True}
                seasons.append(s)
                print seasons
                var -= 1
            except:
                break
                
        payload = {"title": title, "seasons": seasons, "rootFolderPath": path, "seasonFolder": seasonFolder, "monitored": monitored, "tvdbId": tvdbId, "seriestype": seriestype, "titleSlug": titleslug, "qualityProfileId": qualityprofile}
        params = '/api/Series/'
        titletemp = payload['titleSlug']
        nzbdrone = nzbdrone_api(params=params).json()
        title = []
        var = 0
        for increment in nzbdrone:
            title.append(nzbdrone[var]['titleSlug'])
            var += 1
        
        var = 0
        for increment in title:
            print str.find(str(title[var]), str(titletemp))
            if str.find(str(title[var]), str(titletemp)) != -1:
                return jsonify({'duplicate': True})
            var += 1
            
        api = get_setting_value('nzbdrone_api')
        url = nzbdrone_url() + '/api/Series/'     
        headers = {'X-Api-Key': api}
        logger.log('NZBDrone :: 188', 'INFO')
        payload = json.dumps(payload)
        result = requests.post(url, headers=headers, data=payload)
        logger.log('NZBDrone :: 191 %s' % (result.json()), 'INFO')
        return jsonify({'success': True})
    except Exception as e:
        log_exception(e)
        
    
    return jsonify({'success': False})
    
@app.route('/xhr/nzbdrone/get_history/')
def get_history():
    params = '/api/history?pageSize=25&page=1&sortKey=date&sortDir=desc'
    history = nzbdrone_api(params=params)
    history = history.json()
    properties = []
    for overview in history['records']:
        try:
            temp = []
            eventtypes = False
            overviews = overview['series']['overview']
            titles = overview['series']['title']
            episodetitle = overview['episode']['title']
            episode = overview['episode']['episodeNumber']
            season = overview['episode']['seasonNumber']
            try:
                path = overview['data']['importedPath']
                eventtypes = True
            except:
                pass
            date = overview['date'][:10]
            seriesid = overview['seriesId']
            temp.append(overviews)
            temp.append(titles)
            temp.append(episodetitle)
            temp.append(episode)
            temp.append(season)
            temp.append(path)
            temp.append(date)
            temp.append(seriesid)
            temp.append(eventtypes)
            properties.append(temp)
        except Exception as e:
            log_exception(e)

    return render_template('nzbdrone/history.html',
        url = nzbdrone_external_url(),
        port = get_setting_value('nzbdrone_port'),
        properties = properties,
        external_server = get_setting_value('nzbdrone_external_server')
    )
    
@app.route('/xhr/nzbdrone/calendar')
def calendar():
    current_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.strptime(current_date, '%Y-%m-%d') - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.strptime(current_date, '%Y-%m-%d') + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    params = '/api/calendar?start=' + start_date + '&end=' + end_date
    calendar = nzbdrone_api(params=params)
    calendar = calendar.json()
    missed = {}
    today = {}
    tomorrow = {}
    later = {}
    for increment in calendar:
        banner = increment['seriesId']
        episodetitle = increment['title']
        airdateutc = increment['airDateUtc']
        airdate = datetime.datetime.strptime( airdateutc, "%Y-%m-%dT%H:%M:%SZ" )
        airdatestr = airdate.strftime("%m/%d/%Y %H:%M:%S UTC")
        season = increment['seasonNumber']
        episode = increment['episodeNumber']
        episodeid = increment['id']
        episodetvdbid = increment['series']['tvdbId']
        episodeoverview = get_episode_overview(episodeid)
        if episodeoverview != '':
            overview = episodeoverview
        else:
            overview = increment['series']['overview']
    
        episodeid = increment['id']
        title = increment['series']['title']
        if airdate < datetime.datetime.utcnow():
            if str(increment['hasFile']) == 'False':
                missed.update({banner:[episodetitle, airdatestr, season, episode, overview, title, banner, episodeid, episodetvdbid]})
        elif  datetime.datetime.utcnow().date() == airdate.date():
            if datetime.datetime.utcnow() < airdate:
                today.update({banner:[episodetitle, airdatestr, season, episode, overview, title, banner, episodeid, episodetvdbid]})
        elif datetime.datetime.utcnow() < airdate:
            if airdate.date() == (datetime.datetime.utcnow().date() + datetime.timedelta(days=1)):
                tomorrow.update({banner:[episodetitle, airdatestr, season, episode, overview, title, banner, episodeid, episodetvdbid]})
            elif airdate.date() > (datetime.datetime.utcnow().date() + datetime.timedelta(days=1)):
                later.update({banner:[episodetitle, airdatestr, season, episode, overview, title, banner, episodeid, episodetvdbid]})
    return render_template('nzbdrone/calendar.html',
        url = nzbdrone_external_url(),
        port = get_setting_value('nzbdrone_port'),
        missed = missed,
        today = today,
        tomorrow = tomorrow,
        later = later
    )
    
    
@app.route('/xhr/nzbdrone/search_ep/<id>/')
def search_episodes(id):
    if search_episode(params=id) == True:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
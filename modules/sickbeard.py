from flask import Flask, jsonify, render_template, request, send_file, json
import urllib

from maraschino import app
from maraschino.tools import *
import maraschino

def sickbeard_http():
    if get_setting_value('sickbeard_https') == '1':
        return 'https://'
    else:
        return 'http://'

def login_string():
    try:
        login = '%s:%s@' % (get_setting('sickbeard_user').value, get_setting('sickbeard_password').value)

    except:
        login = ''

    return login

def sickbeard_url():
    port = get_setting_value('sickbeard_port')
    url_base = get_setting_value('sickbeard_ip')

    if port:
        url_base = '%s:%s' % (url_base, port)

    url = '%s/api/%s' % (url_base, get_setting_value('sickbeard_api'))

    if using_auth():
        return sickbeard_http() + login_string() + url

    return sickbeard_http() + url

def sickbeard_url_no_api():
    port = get_setting_value('sickbeard_port')
    url_base = get_setting_value('sickbeard_ip')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if using_auth():
        return sickbeard_http() + login_string() + url_base

    return sickbeard_http() + url_base

@app.route('/xhr/sickbeard')
def xhr_sickbeard():
    try:
        url = '%s/?cmd=future&sort=date' % (sickbeard_url())
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

        compact_view = get_setting_value('sickbeard_compact') == '1'
        show_airdate = get_setting_value('sickbeard_airdate') == '1'

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']
            for time in sickbeard:
                for episode in sickbeard[time]:
                    episode['image'] = get_pic(episode['tvdbid'], 'banner')
    except:
        return render_template('sickbeard.html',
            sickbeard = '',
        )

    return render_template('sickbeard.html',
        url = sickbeard_url_no_api(),
        sickbeard = sickbeard,
        missed = sickbeard['missed'],
        today = sickbeard['today'],
        soon = sickbeard['soon'],
        later = sickbeard['later'],
        compact_view = compact_view,
        show_airdate = show_airdate,
    )

@app.route('/sickbeard/search_ep/<tvdbid>/<season>/<episode>')
@requires_auth
def search_ep(tvdbid, season, episode):
    try:
        url = '%s/?cmd=episode.search&tvdbid=%s&season=%s&episode=%s' %(sickbeard_url(), tvdbid, season, episode)
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
        url = '%s/home/plotDetails?show=%s&episode=%s&season=%s' %(sickbeard_url_no_api(), tvdbid, episode, season)
        plot = urllib.urlopen(url).read()

    except:
        raise Exception

    if plot:
        return plot

    return ''

@app.route('/sickbeard/get_all')
def get_all():
    try:
        url = '%s/?cmd=shows&sort=name' %(sickbeard_url())
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
        url = '%s/?cmd=show&tvdbid=%s' %(sickbeard_url(), tvdbid)
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
        url = '%s/?cmd=show.seasons&tvdbid=%s&season=%s' %(sickbeard_url(), tvdbid, season)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

    return render_template('sickbeard-season.html',
       sickbeard = sickbeard,
        id = tvdbid,
        season = season,
    )

@app.route('/sickbeard/history/<limit>')
def history(limit):
    try:
        url = '%s/?cmd=history&limit=%s' %(sickbeard_url(), limit)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

        for show in sickbeard:
            show['image'] = get_pic(show['tvdbid'])

    return render_template('sickbeard-history.html',
        sickbeard = sickbeard,
    )

# returns a link with the path to the required image from SB
def get_pic(tvdb, style='banner'):
    return '%s/sickbeard/get_%s/%s' % (maraschino.WEBROOT, style, tvdb)

@app.route('/sickbeard/get_ep_info/<tvdbid>/<season>/<ep>')
def get_episode_info(tvdbid, season, ep):
    try:
        url = '%s/?cmd=episode&tvdbid=%s&season=%s&episode=%s&full_path=1' %(sickbeard_url(), tvdbid, season, ep)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

    return render_template('sickbeard-episode.html',
        sickbeard = sickbeard,
        id = tvdbid,
        season = season,
        ep = ep,
    )

@app.route('/sickbeard/set_ep_status/<tvdbid>/<season>/<ep>/<st>')
def set_episode_status(tvdbid, season, ep, st):
    try:
        url = '%s/?cmd=episode.setstatus&tvdbid=%s&season=%s&episode=%s&status=%s' %(sickbeard_url(), tvdbid, season, ep, st)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    status = 'error'

    if sickbeard['result'] == 'success':
        status = 'success'

    return jsonify({ 'status': status })

@app.route('/sickbeard/shutdown')
def shutdown():
    try:
        url = '%s/?cmd=sb.shutdown' %(sickbeard_url())
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    return sickbeard['message']

@app.route('/sickbeard/restart')
def restart():
    try:
        url = '%s/?cmd=sb.restart' %(sickbeard_url())
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    return sickbeard['message']

@app.route('/sickbeard/search/')
def search():
    sickbeard = {}
    params = ''

    try:
        params = '&name=%s' % (request.args['name'])
    except:
        pass

    try:
        params = '&tvdbid=%s' % (request.args['tvdbid'])
    except:
        pass

    try:
        params = '&lang=%s' % (request.args['lang'])
    except:
        pass

    if params is not '':
        try:
            url = '%s/?cmd=sb.searchtvdb%s' %(sickbeard_url(), params)
            result = urllib.urlopen(url).read()
            sickbeard = json.JSONDecoder().decode(result)
            sickbeard = sickbeard['data']['results']

        except:
            sickbeard = None

    else:
        sickbeard = None

    return render_template('sickbeard-search.html',
        data = sickbeard,
        sickbeard = 'results',
    )

@app.route('/sickbeard/add_show/<tvdbid>')
def add_show(tvdbid):
    try:
        url = '%s/?cmd=show.addnew&tvdbid=%s' %(sickbeard_url(), tvdbid)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    return sickbeard['message']

@app.route('/sickbeard/get_banner/<tvdbid>')
def get_banner(tvdbid):
    import StringIO
    url = '%s/?cmd=show.getbanner&tvdbid=%s' %(sickbeard_url(), tvdbid)
    img = StringIO.StringIO(urllib.urlopen(url).read())
    return send_file(img, mimetype='image/jpeg')

@app.route('/sickbeard/get_poster/<tvdbid>')
def get_poster(tvdbid):
    import StringIO
    url = '%s/?cmd=show.getposter&tvdbid=%s' %(sickbeard_url(), tvdbid)
    img = StringIO.StringIO(urllib.urlopen(url).read())
    return send_file(img, mimetype='image/jpeg')
    
@app.route('/sickbeard/log/<level>')
def log(level):
    try:
        url = '%s/?cmd=logs&min_level=%s' %(sickbeard_url(), level)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)
        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']
    except:
        sickbeard = None

    return render_template('sickbeard-log.html',
        sickbeard = sickbeard,
        level = level,
    )
    
@app.route('/sickbeard/delete_show/<tvdbid>')
def delete_show(tvdbid):
    try:
        url = '%s/?cmd=show.delete&tvdbid=%s' %(sickbeard_url(), tvdbid)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    return sickbeard['message']

@app.route('/sickbeard/refresh_show/<tvdbid>')
def refresh_show(tvdbid):
    try:
        url = '%s/?cmd=show.refresh&tvdbid=%s' %(sickbeard_url(), tvdbid)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    return sickbeard['message']

@app.route('/sickbeard/update_show/<tvdbid>')
def update_show(tvdbid):
    try:
        url = '%s/?cmd=show.update&tvdbid=%s' %(sickbeard_url(), tvdbid)
        result = urllib.urlopen(url).read()
        sickbeard = json.JSONDecoder().decode(result)

    except:
        raise Exception

    return sickbeard['message']

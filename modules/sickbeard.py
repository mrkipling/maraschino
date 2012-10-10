from flask import jsonify, render_template, request, send_file, json
import urllib2
import base64
import StringIO

from maraschino import app
from maraschino.tools import *
import maraschino


def sickbeard_http():
    if get_setting_value('sickbeard_https') == '1':
        return 'https://'
    else:
        return 'http://'


def sickbeard_url():
    port = get_setting_value('sickbeard_port')
    url_base = get_setting_value('sickbeard_ip')
    webroot = get_setting_value('sickbeard_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    url = '%s/api/%s' % (url_base, get_setting_value('sickbeard_api'))

    return sickbeard_http() + url


def sickbeard_url_no_api():
    port = get_setting_value('sickbeard_port')
    url_base = get_setting_value('sickbeard_ip')
    webroot = get_setting_value('sickbeard_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    return sickbeard_http() + url_base


def sickbeard_api(params=None, use_json=True, dev=False):
    username = get_setting_value('sickbeard_user')
    password = get_setting_value('sickbeard_password')

    url = sickbeard_url() + params
    r = urllib2.Request(url)

    if username and password:
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        r.add_header("Authorization", "Basic %s" % base64string)

    data = urllib2.urlopen(r).read()
    if dev:
        print url
        print data
    if use_json:
        data = json.JSONDecoder().decode(data)
    return data


@app.route('/xhr/sickbeard/')
def xhr_sickbeard():
    params = '/?cmd=future&sort=date'

    try:
        sickbeard = sickbeard_api(params)

        compact_view = get_setting_value('sickbeard_compact') == '1'
        show_airdate = get_setting_value('sickbeard_airdate') == '1'

        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']
            for time in sickbeard:
                for episode in sickbeard[time]:
                    episode['image'] = get_pic(episode['tvdbid'], 'banner')
    except:
        return render_template('sickbeard.html',
            sickbeard='',
        )

    return render_template('sickbeard.html',
        url=sickbeard_url_no_api(),
        sickbeard=sickbeard,
        missed=sickbeard['missed'],
        today=sickbeard['today'],
        soon=sickbeard['soon'],
        later=sickbeard['later'],
        compact_view=compact_view,
        show_airdate=show_airdate,
    )


@app.route('/sickbeard/search_ep/<tvdbid>/<season>/<episode>/')
@requires_auth
def search_ep(tvdbid, season, episode):
    params = '/?cmd=episode.search&tvdbid=%s&season=%s&episode=%s' % (tvdbid, season, episode)

    try:
        sickbeard = sickbeard_api(params)
        return jsonify(sickbeard)
    except:
        return jsonify({'result': False})


@app.route('/sickbeard/get_plot/<tvdbid>/<season>/<episode>/')
def get_plot(tvdbid, season, episode):
    params = '/?cmd=episode&tvdbid=%s&season=%s&episode=%s' % (tvdbid, season, episode)

    try:
        sickbeard = sickbeard_api(params)
        return sickbeard['data']['description']
    except:
        return ''


@app.route('/sickbeard/get_all/')
def get_all():
    params = '/?cmd=shows&sort=name'

    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

        for show in sickbeard:
            sickbeard[show]['url'] = get_pic(sickbeard[show]['tvdbid'], 'banner')

    return render_template('sickbeard-all.html',
        sickbeard=sickbeard,
    )


@app.route('/sickbeard/get_show_info/<tvdbid>/')
def show_info(tvdbid):
    params = '/?cmd=show&tvdbid=%s' % tvdbid

    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']
        sickbeard['url'] = get_pic(tvdbid, 'banner')
        sickbeard['tvdb'] = tvdbid

    return render_template('sickbeard-show.html',
        sickbeard=sickbeard,
    )


@app.route('/sickbeard/get_season/<tvdbid>/<season>/')
def get_season(tvdbid, season):
    params = '/?cmd=show.seasons&tvdbid=%s&season=%s' % (tvdbid, season)

    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

    return render_template('sickbeard-season.html',
        sickbeard=sickbeard,
        id=tvdbid,
        season=season,
    )


@app.route('/sickbeard/history/<limit>/')
def history(limit):
    params = '/?cmd=history&limit=%s' % limit
    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

        for show in sickbeard:
            show['image'] = get_pic(show['tvdbid'])

    return render_template('sickbeard-history.html',
        sickbeard=sickbeard,
    )


# returns a link with the path to the required image from SB
def get_pic(tvdb, style='banner'):
    return '%s/sickbeard/get_%s/%s' % (maraschino.WEBROOT, style, tvdb)


@app.route('/sickbeard/get_ep_info/<tvdbid>/<season>/<ep>/')
def get_episode_info(tvdbid, season, ep):
    params = '/?cmd=episode&tvdbid=%s&season=%s&episode=%s&full_path=1' % (tvdbid, season, ep)

    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    if sickbeard['result'].rfind('success') >= 0:
        sickbeard = sickbeard['data']

    return render_template('sickbeard-episode.html',
        sickbeard=sickbeard,
        id=tvdbid,
        season=season,
        ep=ep,
    )


@app.route('/sickbeard/set_ep_status/<tvdbid>/<season>/<ep>/<st>/')
def set_episode_status(tvdbid, season, ep, st):
    params = '/?cmd=episode.setstatus&tvdbid=%s&season=%s&episode=%s&status=%s' % (tvdbid, season, ep, st)

    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    status = 'error'

    if sickbeard['result'] == 'success':
        status = 'success'

    return jsonify({'status': status})


@app.route('/sickbeard/shutdown/')
def shutdown():
    params = '/?cmd=sb.shutdown'

    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    return sickbeard['message']


@app.route('/sickbeard/restart/')
def restart():
    params = '/?cmd=sb.restart'
    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    return sickbeard['message']


@app.route('/sickbeard/search/')
def sb_search():
    sickbeard = {}
    params = ''

    try:
        params = '&name=%s' % (urllib2.quote(request.args['name']))
    except:
        pass

    try:
        params = '&tvdbid=%s' % (urllib2.quote(request.args['tvdbid']))
    except:
        pass

    try:
        params = '&lang=%s' % (urllib2.quote(request.args['lang']))
    except:
        pass

    if params is not '':
        params = '/?cmd=sb.searchtvdb%s' % params

        try:
            sickbeard = sickbeard_api(params)
            sickbeard = sickbeard['data']['results']
        except:
            sickbeard = None

    else:
        sickbeard = None

    return render_template('sickbeard-search.html',
        data=sickbeard,
        sickbeard='results',
    )


@app.route('/sickbeard/add_show/<tvdbid>/')
def add_show(tvdbid):
    params = '/?cmd=show.addnew&tvdbid=%s' % tvdbid
    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    return sickbeard['message']


@app.route('/sickbeard/get_banner/<tvdbid>/')
def get_banner(tvdbid):
    params = '/?cmd=show.getbanner&tvdbid=%s' % tvdbid
    img = StringIO.StringIO(sickbeard_api(params, use_json=False))
    return send_file(img, mimetype='image/jpeg')


@app.route('/sickbeard/get_poster/<tvdbid>/')
def get_poster(tvdbid):
    params = '/?cmd=show.getposter&tvdbid=%s' % tvdbid
    img = StringIO.StringIO(sickbeard_api(params, use_json=False))
    return send_file(img, mimetype='image/jpeg')


@app.route('/sickbeard/log/<level>/')
def log(level):
    params = '/?cmd=logs&min_level=%s' % level
    try:
        sickbeard = sickbeard_api(params)
        if sickbeard['result'].rfind('success') >= 0:
            sickbeard = sickbeard['data']

    except:
        sickbeard = None

    return render_template('sickbeard-log.html',
        sickbeard=sickbeard,
        level=level,
    )


@app.route('/sickbeard/delete_show/<tvdbid>/')
def delete_show(tvdbid):
    params = '/?cmd=show.delete&tvdbid=%s' % tvdbid
    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    return sickbeard['message']


@app.route('/sickbeard/refresh_show/<tvdbid>/')
def refresh_show(tvdbid):
    params = '/?cmd=show.refresh&tvdbid=%s' % tvdbid
    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    return sickbeard['message']


@app.route('/sickbeard/update_show/<tvdbid>/')
def update_show(tvdbid):
    params = '/?cmd=show.update&tvdbid=%s' % tvdbid
    try:
        sickbeard = sickbeard_api(params)
    except:
        raise Exception

    return sickbeard['message']

from flask import render_template, json
import urllib2

from maraschino import app
from maraschino.tools import *
import datetime as DT


def nzbdrone_http():
    if get_setting_value('nzbdrone_https') == '1':
        return 'https://'
    else:
        return 'http://'


def nzbdrone_url():
    port = get_setting_value('nzbdrone_port')
    url_base = get_setting_value('nzbdrone_ip')
    webroot = get_setting_value('nzbdrone_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    url = '%s/api/' % (url_base)

    return nzbdrone_http() + url


def nzbdrone_url_no_api():
    port = get_setting_value('nzbdrone_port')
    url_base = get_setting_value('nzbdrone_ip')
    webroot = get_setting_value('nzbdrone_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    return nzbdrone_http() + url_base


def nzbdrone_api(params=None, use_json=True, dev=True):
    url = nzbdrone_url() + params
    r = urllib2.Request(url)
    r.add_header("X-Api-Key ", get_setting_value('nzbdrone_api'))

    data = urllib2.urlopen(r).read()
    if dev:
        print url
        print data
    if use_json:
        data = json.JSONDecoder().decode(data)
    return data


@app.route('/xhr/nzbdrone/')
def xhr_nzbdrone():
    params = 'Calendar?end=%s' %(DT.date.today() + DT.timedelta(days=7))

    try:
        nzbdrone = nzbdrone_api(params)

    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone.html',
        nzbdrone=nzbdrone,
    )


@app.route('/xhr/nzbdrone/series/')
def series():
    params = '/Series'

    try:
        nzbdrone = nzbdrone_api(params)
    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone/series.html',
        nzbdrone=nzbdrone,
    )


@app.route('/xhr/nzbdrone/history/')
def nzbdrone_history():
    params = '/History?page=1&pageSize=50&sortKey=date&sortDir=desc'

    try:
        nzbdrone = nzbdrone_api(params)
    except:
        return render_template('nzbdrone.html',
            nzbdrone='Error',
        )

    return render_template('nzbdrone/history.html',
        nzbdrone=nzbdrone['records'],
    )


# @app.route('/xhr/nzbdrone/search_ep/<tvdbid>/<season>/<episode>/')
# @requires_auth
# def search_ep(tvdbid, season, episode):
#     params = '/?cmd=episode.search&tvdbid=%s&season=%s&episode=%s' % (tvdbid, season, episode)

#     try:
#         nzbdrone = nzbdrone_api(params)
#         return jsonify(nzbdrone)
#     except:
#         return jsonify({'result': False})


# @app.route('/xhr/nzbdrone/get_plot/<tvdbid>/<season>/<episode>/')
# def get_plot(tvdbid, season, episode):
#     params = '/?cmd=episode&tvdbid=%s&season=%s&episode=%s' % (tvdbid, season, episode)

#     try:
#         nzbdrone = nzbdrone_api(params)
#         return nzbdrone['data']['description']
#     except:
#         return ''


# @app.route('/xhr/nzbdrone/get_show_info/<tvdbid>/')
# def show_info(tvdbid):
#     params = '/?cmd=show&tvdbid=%s' % tvdbid

#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     if nzbdrone['result'].rfind('success') >= 0:
#         nzbdrone = nzbdrone['data']
#         nzbdrone['url'] = get_pic(tvdbid, 'banner')
#         nzbdrone['tvdb'] = tvdbid

#     return render_template('nzbdrone/show.html',
#         nzbdrone=nzbdrone,
#     )


# @app.route('/xhr/nzbdrone/get_season/<tvdbid>/<season>/')
# def get_season(tvdbid, season):
#     params = '/?cmd=show.seasons&tvdbid=%s&season=%s' % (tvdbid, season)

#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     if nzbdrone['result'].rfind('success') >= 0:
#         nzbdrone = nzbdrone['data']

#     return render_template('nzbdrone/season.html',
#         nzbdrone=nzbdrone,
#         id=tvdbid,
#         season=season,
#     )


# @app.route('/xhr/nzbdrone/history/<limit>/')
# def history(limit):
#     params = '/?cmd=history&limit=%s' % limit
#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     if nzbdrone['result'].rfind('success') >= 0:
#         nzbdrone = nzbdrone['data']

#         for show in nzbdrone:
#             show['image'] = get_pic(show['tvdbid'])

#     return render_template('nzbdrone/history.html',
#         nzbdrone=nzbdrone,
#     )


# # returns a link with the path to the required image from SB
# def get_pic(tvdb, style='banner'):
#     return '%s/xhr/nzbdrone/get_%s/%s' % (maraschino.WEBROOT, style, tvdb)


# @app.route('/xhr/nzbdrone/get_ep_info/<tvdbid>/<season>/<ep>/')
# def get_episode_info(tvdbid, season, ep):
#     params = '/?cmd=episode&tvdbid=%s&season=%s&episode=%s&full_path=1' % (tvdbid, season, ep)

#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     if nzbdrone['result'].rfind('success') >= 0:
#         nzbdrone = nzbdrone['data']

#     return render_template('nzbdrone/episode.html',
#         nzbdrone=nzbdrone,
#         id=tvdbid,
#         season=season,
#         ep=ep,
#     )


# @app.route('/xhr/nzbdrone/set_ep_status/<tvdbid>/<season>/<ep>/<st>/')
# def set_episode_status(tvdbid, season, ep, st):
#     params = '/?cmd=episode.setstatus&tvdbid=%s&season=%s&episode=%s&status=%s' % (tvdbid, season, ep, st)

#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     status = 'error'

#     if nzbdrone['result'] == 'success':
#         status = 'success'

#     return jsonify({'status': status})


# @app.route('/xhr/nzbdrone/shutdown/')
# def shutdown():
#     params = '/?cmd=sb.shutdown'

#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     return nzbdrone['message']


# @app.route('/xhr/nzbdrone/restart/')
# def restart():
#     params = '/?cmd=sb.restart'
#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     return nzbdrone['message']


# @app.route('/xhr/nzbdrone/search/')
# def sb_search():
#     nzbdrone = {}
#     params = ''

#     try:
#         params = '&name=%s' % (urllib2.quote(request.args['name']))
#     except:
#         pass

#     try:
#         params = '&tvdbid=%s' % (urllib2.quote(request.args['tvdbid']))
#     except:
#         pass

#     try:
#         params = '&lang=%s' % (urllib2.quote(request.args['lang']))
#     except:
#         pass

#     if params is not '':
#         params = '/?cmd=sb.searchtvdb%s' % params

#         try:
#             nzbdrone = nzbdrone_api(params)
#             nzbdrone = nzbdrone['data']['results']
#         except:
#             nzbdrone = None

#     else:
#         nzbdrone = None

#     return render_template('nzbdrone/search.html',
#         data=nzbdrone,
#         nzbdrone='results',
#     )


# @app.route('/xhr/nzbdrone/add_show/<tvdbid>/')
# def add_show(tvdbid):
#     params = '/?cmd=show.addnew&tvdbid=%s' % tvdbid
#     try:
#         status = urllib2.quote(request.args['status'])
#         lang = urllib2.quote(request.args['lang'])
#         initial = urllib2.quote(request.args['initial'])
#         if status:
#             params += '&status=%s' % status

#         if lang:
#             params += '&lang=%s' % lang

#         if initial:
#             params += '&initial=%s' % initial
#     except:
#         pass

#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     return nzbdrone['message']


# @app.route('/xhr/nzbdrone/get_banner/<tvdbid>/')
# def get_banner(tvdbid):
#     params = '/?cmd=show.getbanner&tvdbid=%s' % tvdbid
#     img = StringIO.StringIO(nzbdrone_api(params, use_json=False))
#     return send_file(img, mimetype='image/jpeg')


# @app.route('/xhr/nzbdrone/get_poster/<tvdbid>/')
# def get_poster(tvdbid):
#     params = '/?cmd=show.getposter&tvdbid=%s' % tvdbid
#     img = StringIO.StringIO(nzbdrone_api(params, use_json=False))
#     return send_file(img, mimetype='image/jpeg')


# @app.route('/xhr/nzbdrone/log/<level>/')
# def log(level):
#     params = '/?cmd=logs&min_level=%s' % level
#     try:
#         nzbdrone = nzbdrone_api(params)
#         if nzbdrone['result'].rfind('success') >= 0:
#             nzbdrone = nzbdrone['data']
#             if not nzbdrone:
#                 nzbdrone = ['The %s log is empty' % level]

#     except:
#         nzbdrone = None

#     return render_template('nzbdrone/log.html',
#         nzbdrone=nzbdrone,
#         level=level,
#     )


# @app.route('/xhr/nzbdrone/delete_show/<tvdbid>/')
# def delete_show(tvdbid):
#     params = '/?cmd=show.delete&tvdbid=%s' % tvdbid
#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     return nzbdrone['message']


# @app.route('/xhr/nzbdrone/refresh_show/<tvdbid>/')
# def refresh_show(tvdbid):
#     params = '/?cmd=show.refresh&tvdbid=%s' % tvdbid
#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     return nzbdrone['message']


# @app.route('/xhr/nzbdrone/update_show/<tvdbid>/')
# def update_show(tvdbid):
#     params = '/?cmd=show.update&tvdbid=%s' % tvdbid
#     try:
#         nzbdrone = nzbdrone_api(params)
#     except:
#         raise Exception

#     return nzbdrone['message']

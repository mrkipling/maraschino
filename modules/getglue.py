from flask import render_template
import jsonrpclib, re

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

@app.route('/xhr/getglue')
@requires_auth
def xhr_getglue():
    getglue = {}

    try:
        xbmc = jsonrpclib.Server(server_api_address())
    except:
        return render_template('getglue.html',
            getglue = getglue
        )

    try:
        currently_playing = xbmc.Player.GetItem(playerid = 1, properties = ['tvshowid', 'showtitle', 'season', 'imdbnumber', 'title'])['item']
        getglue['itemid'] = currently_playing['imdbnumber']

        # if watching a TV show
        if currently_playing['tvshowid'] != -1:
            show = xbmc.VideoLibrary.GetTVShowDetails(tvshowid = currently_playing['tvshowid'], properties = ['imdbnumber'])['tvshowdetails']
            getglue['itemid'] = show['imdbnumber']

    except:
        currently_playing = None

    if currently_playing:
        getglue['title'] = currently_playing['title']
        getglue['watching'] = currently_playing['label']

        if currently_playing['tvshowid'] != -1:
            getglue['path'] = "tv_shows/" + prep_for_url(currently_playing['showtitle'])
        else:
            getglue['path'] = "movies/" + prep_for_url(currently_playing['title'])
    else:
        getglue = None

    return render_template('getglue.html',
        getglue = getglue
    )


def prep_for_url(title):
    #clean and remove utf8
    title = title.encode('ascii', 'ignore').lower().replace(" ", "_").replace("__", "_").replace("the", "").replace("and", "").replace("&", "").replace(" a ", "").replace("-", "").replace(":", "")
    #remove leading _
    title = re.sub('^_', "", title)
    #remove ending _
    title = re.sub('_$', "", title)
    return title

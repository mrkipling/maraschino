from flask import jsonify, render_template, json, send_file
from maraschino import app, logger, WEBROOT, RUNDIR
from maraschino.tools import requires_auth, get_setting_value
from threading import Thread
import StringIO
import urllib
import urllib2
import base64

def headphones_http():
    if get_setting_value('headphones_https') == '1':
        return 'https://'
    else:
        return 'http://'

def headphones_url():
    port = get_setting_value('headphones_port')
    url_base = get_setting_value('headphones_host')
    webroot = get_setting_value('headphones_webroot')

    if port:
        url_base = '%s:%s' % (url_base, port)

    if webroot:
        url_base = '%s/%s' % (url_base, webroot)

    return headphones_http() + url_base

def headphones_api(command, use_json=True, dev=False):
    username = get_setting_value('headphones_user')
    password = get_setting_value('headphones_password')
    apikey =  get_setting_value('headphones_api')

    url = '%s/api?apikey=%s&cmd=%s' % (headphones_url(), apikey, command)
    
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    data = urllib2.urlopen(request).read()

    if use_json:
        data = json.JSONDecoder().decode(data)

    if dev:
        print 'DEVELOPER :: %s' % url
        print 'DEVELOPER :: %s' % data

    return data


def convert_track_duration(milliseconds):
    if milliseconds is None:
        return "00:00"
    seconds = milliseconds / 1000
    hours = seconds / 3600
    seconds -= 3600 * hours
    minutes = seconds / 60
    seconds -= 60 * minutes
    if hours == 0:
        return "%02d:%02d" % (minutes, seconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


def hp_compact():
    return get_setting_value('headphones_compact') == '1'

def headphones_exception(e):
    logger.log('HEADPHONES :: EXCEPTION -- %s' % e, 'DEBUG')
    return render_template('headphones-base.html', headphones=True, message=e)


def hp_artistart(id):
    return '%s/xhr/headphones/img/artist/%s' % (WEBROOT, id)


def hp_albumart(id):
    return '%s/xhr/headphones/img/album/%s' % (WEBROOT, id)

@app.route('/xhr/headphones/img/<type>/<id>/')
@requires_auth
def xhr_headphones_image(type, id):
    if type == 'artist':
        cache_url = headphones_api('getArtistThumb&id=' + id, use_json=False)
    else:
        cache_url = headphones_api('getAlbumThumb&id=' + id, use_json=False)

    if cache_url:
        url = '%s/%s' % (headphones_url(), cache_url)
    else:
        img = RUNDIR + '/static/images/applications/HeadPhones.png'
        return send_file(img, mimetype='image/jpeg')

    username = get_setting_value('headphones_user')
    password = get_setting_value('headphones_password')

    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)

    img = StringIO.StringIO(urllib2.urlopen(request).read())
    return send_file(img, mimetype='image/jpeg')


@app.route('/xhr/headphones/')
@requires_auth
def xhr_headphones():
    return xhr_headphones_upcoming()


@app.route('/xhr/headphones/artists/')
@requires_auth
def xhr_headphones_artists(mobile=False):
    logger.log('HEADPHONES :: Fetching artists list', 'INFO')
    artists = []

    try:
        headphones = headphones_api('getIndex')
        updates = headphones_api('getVersion')
    except Exception as e:
        if mobile:
            headphones_exception(e)
            return artists
        return headphones_exception(e)


    for artist in headphones:
        if not 'Fetch failed' in artist['ArtistName']:
            try:
                artist['Percent'] = int(100 * float(artist['HaveTracks']) / float(artist['TotalTracks']))
            except:
                artist['Percent'] = 0

            if not hp_compact() and not mobile:
                try:
                    artist['ThumbURL'] = hp_artistart(artist['ArtistID'])
                except:
                    pass
            artists.append(artist)

    if mobile:
        return artists

    return render_template('headphones-artists.html',
        headphones=True,
        artists=artists,
        updates=updates,
        compact=hp_compact(),
    )


@app.route('/xhr/headphones/artist/<artistid>/')
@requires_auth
def xhr_headphones_artist(artistid, mobile=False):
    logger.log('HEADPHONES :: Fetching artist', 'INFO')

    try:
        albums = headphones_api('getArtist&id=%s' % artistid)
    except Exception as e:
        return headphones_exception(e)

    if not hp_compact() and not mobile:
        for album in albums['albums']:
            try:
                album['ThumbURL'] = hp_albumart(album['AlbumID'])
            except:
                pass

    if mobile:
        return albums

    return render_template('headphones-artist.html',
        albums=albums,
        headphones=True,
        compact=hp_compact(),
    )


@app.route('/xhr/headphones/album/<albumid>/')
@requires_auth
def xhr_headphones_album(albumid, mobile=False):
    logger.log('HEADPHONES :: Fetching album', 'INFO')

    try:
        headphones = headphones_api('getAlbum&id=%s' % albumid)
    except Exception as e:
        return headphones_exception(e)

    album = headphones['album'][0]

    try:
        album['ThumbURL'] = hp_albumart(album['AlbumID'])
    except:
        pass

    album['TotalDuration'] = 0

    for track in headphones['tracks']:
        if track['TrackDuration'] == None:
            track['TrackDuration'] = 0
        album['TotalDuration'] = album['TotalDuration'] + int(track['TrackDuration'])
        track['TrackDuration'] = convert_track_duration(track['TrackDuration'])

    album['TotalDuration'] = convert_track_duration(album['TotalDuration'])
    album['Tracks'] = len(headphones['tracks'])

    if mobile:
        return headphones
    return render_template('headphones-album.html',
        album=headphones,
        headphones=True,
        compact=hp_compact(),
    )


@app.route('/xhr/headphones/upcoming/')
@requires_auth
def xhr_headphones_upcoming(mobile=False):
    logger.log('HEADPHONES :: Fetching upcoming albums', 'INFO')

    try:
        upcoming = headphones_api('getUpcoming')
    except Exception as e:
        return headphones_exception(e)

    if upcoming == []:
        upcoming = 'empty'

    if not mobile:
        for album in upcoming:
            try:
                album['ThumbURL'] = hp_albumart(album['AlbumID'])
            except:
                pass

    try:
        wanted = headphones_api('getWanted')
    except Exception as e:
        return headphones_exception(e)

    if wanted == []:
        wanted = 'empty'

    if not mobile:
        for album in wanted:
            try:
                album['ThumbURL'] = hp_albumart(album['AlbumID'])
            except:
                pass

    if mobile:
        return [upcoming, wanted]

    return render_template('headphones.html',
        upcoming=upcoming,
        wanted=wanted,
        headphones=True,
        compact=hp_compact(),
    )


@app.route('/xhr/headphones/similar/')
@requires_auth
def xhr_headphones_similar():
    logger.log('HEADPHONES :: Fetching similar artists', 'INFO')

    try:
        headphones = headphones_api('getSimilar')
    except Exception as e:
        return headphones_exception(e)

    return render_template('headphones-similar.html',
        similar=headphones,
        headphones=True,
    )


@app.route('/xhr/headphones/history/')
@requires_auth
def xhr_headphones_history(mobile=False):
    logger.log('HEADPHONES :: Fetching history', 'INFO')

    try:
        headphones = headphones_api('getHistory')
    except Exception as e:
        return headphones_exception(e)

    if mobile:
        return headphones

    return render_template('headphones-history.html',
        history=headphones,
        headphones=True,
    )


@app.route('/xhr/headphones/search/<type>/<query>/')
@requires_auth
def xhr_headphones_search(type, query, mobile=False):
    if type == 'artist':
        logger.log('HEADPHONES :: Searching for artist', 'INFO')
        command = 'findArtist&name=%s' % urllib.quote(query)
    else:
        logger.log('HEADPHONES :: Searching for album', 'INFO')
        command = 'findAlbum&name=%s' % urllib.quote(query)

    try:
        headphones = headphones_api(command)
    except Exception as e:
        return headphones_exception(e)

    for artist in headphones:
        artist['url'].replace('\/', '/')

        if mobile:
            return headphones

    return render_template('headphones-search_dialog.html',
        headphones=True,
        search=headphones,
        query=query
    )


@app.route('/xhr/headphones/artist/<artistid>/<action>/')
@requires_auth
def xhr_headphones_artist_action(artistid, action, mobile=False):
    if action == 'pause':
        logger.log('HEADPHONES :: Pausing artist', 'INFO')
        command = 'pauseArtist&id=%s' % artistid
    elif action == 'resume':
        logger.log('HEADPHONES :: Resuming artist', 'INFO')
        command = 'resumeArtist&id=%s' % artistid
    elif action == 'refresh':
        logger.log('HEADPHONES :: Refreshing artist', 'INFO')
        command = 'refreshArtist&id=%s' % artistid
    elif action == 'remove':
        logger.log('HEADPHONES :: Removing artist', 'INFO')
        command = 'delArtist&id=%s' % artistid
    elif action == 'add':
        logger.log('HEADPHONES :: Adding artist', 'INFO')
        command = 'addArtist&id=%s' % artistid

    try:
        if command == 'remove':
            headphones_api(command, False)
        elif command == 'pause':
            headphones_api(command, False)
        elif command == 'resume':
            headphones_api(command, False)
        else:
            Thread(target=headphones_api, args=(command, False)).start()
    except Exception as e:
        if mobile:
            headphones_exception(e)
            return jsonify(error='failed')

        return headphones_exception(e)

    return jsonify(status='successful')


@app.route('/xhr/headphones/album/<albumid>/<status>/')
@requires_auth
def xhr_headphones_album_status(albumid, status, mobile=False):
    if status == 'wanted':
        logger.log('HEADPHONES :: Marking album as wanted', 'INFO')
        command = 'queueAlbum&id=%s' % albumid
    if status == 'wanted_new':
        logger.log('HEADPHONES :: Marking album as wanted (new)', 'INFO')
        command = 'queueAlbum&new=True&id=%s' % albumid
    if status == 'skipped':
        logger.log('HEADPHONES :: Marking album as skipped', 'INFO')
        command = 'unqueueAlbum&id=%s' % albumid

    try:
        Thread(target=headphones_api, args=(command, False)).start()
    except Exception as e:
        if mobile:
            headphones_exception(e)
            return jsonify(error='failed')

        return headphones_exception(e)

    return jsonify(status='successful')


@app.route('/xhr/headphones/control/<command>/')
@requires_auth
def xhr_headphones_control(command):
    if command == 'shutdown':
        logger.log('HEADPHONES :: Shutting down', 'INFO')

    elif command == 'restart':
        logger.log('HEADPHONES :: Restarting', 'INFO')

    elif command == 'update':
        logger.log('HEADPHONES :: Updating', 'INFO')

    elif command == 'force_search':
        logger.log('HEADPHONES :: Forcing wanted album search', 'INFO')
        command = 'forceSearch'

    elif command == 'force_process':
        logger.log('HEADPHONES :: Forcing post process', 'INFO')
        command = 'forceProcess'

    try:
        Thread(target=headphones_api, args=(command, False)).start()
    except Exception as e:
        return headphones_exception(e)

    return jsonify(status='successful')

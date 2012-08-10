from flask import jsonify
import jsonrpclib
import socket
import struct
import urllib

from Maraschino import app
from maraschino.noneditable import *
from maraschino.tools import *
from maraschino import logger

xbmc_error = 'There was a problem connecting to the XBMC server'

@app.route('/xhr/play/<file_type>/<media_type>/<int:media_id>')
@requires_auth
def xhr_play_media(file_type, media_type, media_id):
    logger.log('CONTROLS :: Playing %s' % media_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    if file_type == 'video':
        id = 1
    else:
        id = 0

    try:
        xhr_clear_playlist(id)
    except:
        logger.log('CONTROLS :: Failed to clear %s playlist' % file_type, 'DEBUG')
        return jsonify({ 'failed': True })

    if file_type == 'video':

        if media_type == 'tvshow':
            try:
                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, sort={ 'method': 'episode' })['episodes']
                for episode in tvshow_episodes:
                    episodeid = episode['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            except:
                logger.log('CONTROLS :: Failed to retrieve episodes', 'DEBUG')
                return jsonify({ 'failed': True })

        elif 'season' in media_type:
            media_type = media_type.split('_')
            season = int(media_type[1])

            try:
                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, season=season, sort={ 'method': 'episode' })['episodes']
                for episode in tvshow_episodes:
                    episodeid = episode['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            except:
                logger.log('CONTROLS :: Failed to retrieve episodes', 'DEBUG')
                return jsonify({ 'failed': True })

        else:
            try:
                item = { media_type + 'id': media_id }
                xbmc.Playlist.Add(playlistid=1, item=item)
            except:
                logger.log('CONTROLS :: Failed to add %s to playlist' % media_type, 'DEBUG')
                return jsonify({ 'failed': True })

        playlistid = 1

    else:
        try:
            item = { media_type + 'id': media_id }
            xbmc.Playlist.Add(playlistid=0, item=item)
        except:
            logger.log('CONTROLS :: Failed to add %s to playlist' % media_type, 'DEBUG')
            return jsonify({ 'failed': True })

        playlistid = 0

    try:
        item = { 'playlistid': playlistid }
        xbmc.Player.Open(item)
    except:
        logger.log('CONTROLS :: Failed to open %s playlist' % file_type, 'DEBUG')
        return jsonify({ 'failed': True })

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue/<file_type>/<media_type>/<int:media_id>')
@requires_auth
def xhr_enqueue_media(file_type, media_type, media_id):
    logger.log('CONTROLS :: Queueing %s' % media_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    if file_type == 'video':

        if media_type == 'tvshow':
            try:
                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, sort={ 'method': 'episode' })['episodes']
                for episode in tvshow_episodes:
                    episodeid = episode['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            except:
                logger.log('CONTROLS :: Failed to retrieve episodes', 'DEBUG')
                return jsonify({ 'failed': True })

        elif 'season' in media_type:
            media_type = media_type.split('_')
            season = int(media_type[1])

            try:
                tvshow_episodes = xbmc.VideoLibrary.GetEpisodes(tvshowid=media_id, season=season, sort={ 'method': 'episode' })['episodes']
                for episode in tvshow_episodes:
                    episodeid = episode['episodeid']
                    item = { 'episodeid': episodeid }
                    xbmc.Playlist.Add(playlistid=1, item=item)

            except:
                logger.log('CONTROLS :: Failed to retrieve episodes', 'DEBUG')
                return jsonify({ 'failed': True })

        else:
            try:
                item = { media_type + 'id': media_id }
                xbmc.Playlist.Add(playlistid=1, item=item)
            except:
                logger.log('CONTROLS :: Failed to add %s to playlist' % media_type, 'DEBUG')
                return jsonify({ 'failed': True })

    else:
        try:
            item = { media_type + 'id': media_id }
            xbmc.Playlist.Add(playlistid=0, item=item)
        except:
            logger.log('CONTROLS :: Failed to add %s to playlist' % media_type, 'DEBUG')
            return jsonify({ 'failed': True })

    return jsonify({ 'success': True })

@app.route('/xhr/resume/video/<video_type>/<int:video_id>')
@requires_auth
def xhr_resume_video(video_type, video_id):
    logger.log('CONTROLS :: Resuming %s' % video_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xhr_clear_playlist(1)
    except:
        logger.log('CONTROLS :: Failed to clear video playlist', 'DEBUG')
        return jsonify({ 'failed': True })

    try:
        if video_type == 'episode':
            video = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=video_id, properties=['resume'])['episodedetails']
        else:
            video = xbmc.VideoLibrary.GetMovieDetails(movieid=video_id, properties=['resume'])['moviedetails']
    except:
        logger.log('CONTROLS :: Failed to retrieve reume position', 'DEBUG')
        return jsonify({ 'failed': True })

    seconds = int(video['resume']['position'])

    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes

    position = { 'hours': hours, 'minutes': minutes, 'seconds': seconds }

    try:
        item = { video_type + 'id': video_id }
        xbmc.Playlist.Add(playlistid=1, item=item)
    except:
        logger.log('CONTROLS :: Failed to add %s to playlist' % video_type, 'DEBUG')
        return jsonify({ 'failed': True })

    item = { 'playlistid': 1 }

    try:
        xbmc.Player.Open(item)
        xbmc.Player.Seek(playerid=1, value=position)
    except:
        logger.log('CONTROLS :: Failed to open %s at %s' % (video_type, position), 'DEBUG')
        return jsonify({ 'failed': True })

    return jsonify({ 'success': True })

@app.route('/xhr/play/trailer/<int:movieid>')
@app.route('/xhr/play/trailer/url/<path:trailer>')
@requires_auth
def xhr_play_trailer(movieid=None, trailer=None):
    logger.log('CONTROLS :: Playing trailer', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xhr_clear_playlist(1)
    except:
        logger.log('CONTROLS :: Failed to clear video playlist', 'DEBUG')
        return jsonify({ 'failed': True })

    if not trailer:
        try:
            trailer = xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties= ['trailer'])['moviedetails']['trailer']
        except:
            logger.log('CONTROLS :: Failed to retrieve trailer url', 'DEBUG')
            return jsonify({ 'failed': True })
    else:
        trailer = youtube_to_xbmc(trailer)

    item = { 'file': trailer }

    try:
        xbmc.Playlist.Add(playlistid=1, item=item)
        item = { 'playlistid': 1 }
        xbmc.Player.Open(item)
    except:
        logger.log('CONTROLS :: Failed to open trailer', 'DEBUG')
        return jsonify({ 'failed': True })

    return jsonify({ 'success': True })

@app.route('/xhr/play_file/<file_type>/', methods=['POST'])
@requires_auth
def xhr_play_file(file_type):
    logger.log('CONTROLS :: Playing %s file' % file_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    if file_type == "music":
        file_type = "audio"
        id = 0
    else:
        id = 1

    try:
        xhr_clear_playlist(id)
    except:
        logger.log('CONTROLS :: Failed to clear %s playlist' % file_type, 'DEBUG')
        return jsonify({ 'failed': True })

    file = request.form['file']
    file = urllib.unquote(file.encode('ascii')).decode('utf-8')

    if file_type == "video":
        player = 1
    else:
        player = 0

    try:
        item = { 'file': file }
        xbmc.Playlist.Add(playlistid=player, item=item)
    except:
        logger.log('CONTROLS :: Failed to add %s to playlist' % file_type, 'DEBUG')
        return jsonify({ 'failed': True })

    try:
        item = { 'playlistid': player }
        xbmc.Player.Open(item)
    except:
        logger.log('CONTROLS :: Failed to open %s' % file_type, 'DEBUG')
        return jsonify({ 'failed': True })

    return jsonify({ 'success': True })

@app.route('/xhr/enqueue_file/<file_type>/', methods=['POST'])
@requires_auth
def xhr_enqueue_file(file_type):
    logger.log('CONTROLS :: Queueing %s file' % file_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    file = request.form['file']
    file = urllib.unquote(file.encode('ascii')).decode('utf-8')

    if file_type == "video":
        player = 1
    else:
        player = 0

    try:
        item = { 'file': file }
        xbmc.Playlist.Add(playlistid=player, item=item)
    except:
        logger.log('CONTROLS :: Failed to add %s to playlist' % file_type, 'DEBUG')
        return jsonify({ 'failed': True })

    return jsonify({ 'success': True })

@app.route('/xhr/playlist/<int:playerid>/play/<int:position>')
@requires_auth
def xhr_playlist_play(playerid, position):
    logger.log('CONTROLS :: playing playlist position %i' % position, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xbmc.Player.GoTo(playerid=playerid, position=position)
        return jsonify({'success': True})

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({'failed': True})

@app.route('/xhr/playlist/<int:playlistid>/clear')
@requires_auth
def xhr_clear_playlist(playlistid):
    logger.log('CONTROLS :: Clearing playlist', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xbmc.Playlist.Clear(playlistid=playlistid)
        return jsonify({'success': True})

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({'failed': True})

@app.route('/xhr/playlist/<int:playlistid>/move_item/<int:position1>/<direction>')
@requires_auth
def xhr_move_playlist_item(playlistid, position1, direction):
    logger.log('CONTROLS :: Moving playlist item %s' % direction, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    if direction == 'up':
        if position1 != 0:
            position2 = position1 - 1
        else:
            logger.log('CONTROLS :: Playlist item is already at first position', 'INFO')
            return jsonify({'success': True})
    else:
        position2 = position1 + 1

    try:
        xbmc.Playlist.Swap(playlistid=playlistid, position1=position1, position2=position2)
        return jsonify({'success': True})

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({'failed': True})

@app.route('/xhr/playlist/<int:playlistid>/remove_item/<int:position>')
@requires_auth
def xhr_remove_playlist_item(playlistid, position):
    logger.log('CONTROLS :: Removing playlist item %s' % position, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        xbmc.Playlist.Remove(playlistid=playlistid, position=position)
        return jsonify({'success': True})

    except:
        logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
        return jsonify({'failed': True})

@app.route('/xhr/controls/<command>')
@requires_auth
def xhr_controls(command):
    serversettings = server_settings()
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        active_player = xbmc.Player.GetActivePlayers()
        if active_player[0]['type'] == 'video':
            playerid = 1
        elif active_player[0]['type'] == 'audio':
            playerid = 0
    except:
        active_player = None

    if command == 'play_pause':
        logger.log('CONTROLS :: Play/Pause', 'INFO')
        try:
            xbmc.Player.PlayPause(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'stop':
        logger.log('CONTROLS :: Stop', 'INFO')
        try:
            xbmc.Player.Stop(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif 'volume' in command:
        logger.log('CONTROLS :: Volume', 'INFO')
        try:
            volume = command.split('_')
            volume = int(volume[1])
            xbmc.Application.SetVolume(volume=volume)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'next':
        logger.log('CONTROLS :: Next', 'INFO')
        try:
            xbmc.Player.GoNext(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'previous':
        logger.log('CONTROLS :: Previous', 'INFO')
        try:
            xbmc.Player.GoPrevious(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'fast_forward':
        logger.log('CONTROLS :: Fast forward', 'INFO')
        try:
            xbmc.Player.SetSpeed(playerid=playerid, speed='increment')
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'rewind':
        logger.log('CONTROLS :: Rewind', 'INFO')
        try:
            xbmc.Player.SetSpeed(playerid=playerid, speed='decrement')
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif 'seek' in command:
        logger.log('CONTROLS :: Seek', 'INFO')
        try:
            percentage = command.split('_')
            percentage = int(percentage[1])
            xbmc.Player.Seek(playerid=playerid, value=percentage)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'shuffle':
        logger.log('CONTROLS :: Shuffle', 'INFO')
        try:
            shuffled = xbmc.Player.GetProperties(playerid=playerid, properties=['shuffled'])['shuffled']
            if shuffled == True:
                xbmc.Player.UnShuffle(playerid=playerid)
            else:
                xbmc.Player.Shuffle(playerid=playerid)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'repeat':
        logger.log('CONTROLS :: Repeat', 'INFO')
        try:
            states = ['off', 'one', 'all']
            repeat = xbmc.Player.GetProperties(playerid=playerid, properties=['repeat'])['repeat']
            state = states.index(repeat)
            if state <= 1:
                state = state + 1
            else:
                state = 0

            state = states[state]
            xbmc.Player.Repeat(playerid=playerid, state=state)
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'update_video':
        logger.log('CONTROLS :: Updating video library', 'INFO')
        try:
            xbmc.VideoLibrary.Scan()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'clean_video':
        logger.log('CONTROLS :: Cleaning video library', 'INFO')
        try:
            xbmc.VideoLibrary.Clean()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'update_audio':
        logger.log('CONTROLS :: Updating audio library', 'INFO')
        try:
            xbmc.AudioLibrary.Scan()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'clean_audio':
        logger.log('CONTROLS :: Cleaning audio library', 'INFO')
        try:
            xbmc.AudioLibrary.Clean()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'poweroff':
        logger.log('CONTROLS :: Shutting down XBMC machine', 'INFO')
        try:
            xbmc.System.Shutdown()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'suspend':
        logger.log('CONTROLS :: Suspending XBMC machine', 'INFO')
        try:
            xbmc.System.Suspend()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'reboot':
        logger.log('CONTROLS :: Rebooting XBMC machine', 'INFO')
        try:
            xbmc.System.Reboot()
            return_response = 'success'
        except:
            logger.log('CONTROLS :: %s' % xbmc_error, 'ERROR')
            return_response = 'failed'

    elif command == 'poweron':
        logger.log('CONTROLS :: Powering on XBMC machine', 'INFO')
        server_macaddress = serversettings['mac_address']

        if not server_macaddress:
            logger.log('CONTROLS :: No XBMC machine MAC address defined', 'ERROR')
            return jsonify({ 'failed': True })

        else:
            try:
                addr_byte = server_macaddress.split(':')
                hw_addr = struct.pack('BBBBBB',
                int(addr_byte[0], 16),
                int(addr_byte[1], 16),
                int(addr_byte[2], 16),
                int(addr_byte[3], 16),
                int(addr_byte[4], 16),
                int(addr_byte[5], 16))

                msg = '\xff' * 6 + hw_addr * 16
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.sendto(msg, ("255.255.255.255", 9))
                return_response = 'success'

            except:
                logger.log('CONTROLS :: Failed to send WOL packet', 'ERROR')
                return_response = 'failed'

    if return_response == 'success':
        return jsonify({ 'success': True })
    else:
        return jsonify({ 'failed': True })

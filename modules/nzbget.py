from flask import render_template, jsonify, request
from jsonrpclib import jsonrpc
import base64
import urllib

from maraschino import app, logger
from maraschino.tools import *


def nzbget_http():
    if get_setting_value('nzbget_https') == '1':
        return 'https://'
    else:
        return 'http://'


def nzbget_auth():
    return 'nzbget:%s@' % (get_setting_value('nzbget_password'))


def nzbget_url():
    return '%s%s%s:%s' % (nzbget_http(), \
        nzbget_auth(), \
        get_setting_value('nzbget_host'), \
        get_setting_value('nzbget_port'))


def nzbget_exception(e):
    logger.log('NZBGet :: EXCEPTION -- %s' % e, 'DEBUG')


@app.route('/xhr/nzbget/')
@requires_auth
def xhr_nzbget():
    downloads = status = nzbget = None
    logger.log('NZBGet :: Getting download list', 'INFO')
    try:
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % nzbget_url())
        status = nzbget.status()
        downloads = nzbget.listgroups()
    except Exception as e:
        nzbget_exception(e)

    logger.log('NZBGet :: Getting download list (DONE)', 'INFO')
    return render_template('nzbget-queue.html',
        nzbget=status,
        downloads=downloads,
    )


@app.route('/xhr/nzbget/queue/<action>/')
@requires_auth
def queue_action_nzbget(action):
    status = False
    logger.log('NZBGet :: Queue action: %s' % action, 'INFO')
    try:
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % nzbget_url())
        if 'resume' in action:
            status = nzbget.resume()
        elif 'pause' in action:
            status = nzbget.pause()

    except Exception as e:
        nzbget_exception(e)

    return jsonify({'success': status})


@app.route('/xhr/nzbget/queue/add/', methods=['POST'])
@requires_auth
def queue_add_nzbget():
    status = False
    if len(nzb):
        try:
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % nzbget_url())
            nzb = request.form['url']
            nzb = urllib.urlopen(nzb).read()
            status = nzbget.append('test', '', False, base64.encode(nzb))
        except Exception as e:
            nzbget_exception(e)

    return jsonify({'success': status})


@app.route('/xhr/nzbget/individual/<int:id>/<action>/')
@requires_auth
def individual_action_nzbget(id, action):
    status = False
    logger.log('NZBGet :: Item %s action: %s' % (id, action), 'INFO')
    if 'resume' in action:
        action = 'GroupResume'
    elif 'pause' in action:
        action = 'GroupPause'
    elif 'delete' in action:
        action = 'GroupDelete'

    try:
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % nzbget_url())
        status = nzbget.editqueue(action, 0, '', id)

    except Exception as e:
        nzbget_exception(e)

    return jsonify({'success': status, 'id': id, 'action': action})


@app.route('/xhr/nzbget/set_speed/<int:speed>/')
@requires_auth
def set_speed_nzbget(speed):
    logger.log('NZBGet :: Setting speed limit: %s' % speed, 'INFO')
    try:
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % nzbget_url())
        status = nzbget.rate(speed)
    except Exception as e:
        nzbget_exception(e)

    return jsonify({'success': status})

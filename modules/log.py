from flask import render_template
from maraschino import app, LOG_FILE
from maraschino.noneditable import *
from maraschino import logger
from pastebin.pastebin import PastebinAPI
from maraschino.tools import requires_auth


@app.route('/xhr/log')
@requires_auth
def xhr_log():
    file = open(LOG_FILE)
    log = []

    for line in reversed(file.readlines()):
        log.append(line.rstrip())

    file.close()

    return render_template('log_dialog.html',
        log=log,
    )


@app.route('/xhr/log/pastebin')
@requires_auth
def xhr_log_pastebin():
    file = open(LOG_FILE)
    log = []
    log_str = ''

    for line in reversed(file.readlines()):
        log.append(line.rstrip())
        log_str += line.rstrip()
        log_str += '\n'

    file.close()
    x = PastebinAPI()
    try:
        url = x.paste('feed610f82c2c948f430b43cc0048258', log_str)
        logger.log('LOG :: Log successfully uploaded to %s' % url, 'INFO')
    except Exception as e:
        logger.log('LOG :: Log failed to upload - %s' % e, 'INFO')

    return render_template('log_dialog.html',
        log=log,
        url=url,
    )

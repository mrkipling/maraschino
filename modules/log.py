from flask import Flask, render_template
from maraschino import app, LOG_FILE
from maraschino.noneditable import *
from pastebin.pastebin import submit
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
        log = log,
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

    url = submit(log_str)

    return render_template('log_dialog.html',
        log = log,
        url = url,
    )

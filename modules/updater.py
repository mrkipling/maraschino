from flask import jsonify, render_template
from maraschino import app, logger, COMMITS_BEHIND, COMMITS_COMPARE_URL
from maraschino.updater import checkGithub, Update
from maraschino.tools import requires_auth
import maraschino

@app.route('/xhr/update_bar')
@requires_auth
def xhr_update_bar():
    if maraschino.COMMITS_BEHIND != 0:
        return render_template('includes/update_bar.html',
            commits = maraschino.COMMITS_BEHIND,
            compare_url = maraschino.COMMITS_COMPARE_URL,
        )
    else:
        return jsonify(up_to_date=True)

@app.route('/xhr/updater/check')
@requires_auth
def xhr_update_check():
    check = checkGithub()
    return jsonify(update=check)

@app.route('/xhr/updater/update')
@requires_auth
def xhr_update():
    updated = Update()
    if updated:
        logger.log('UPDATER :: Update complete', 'INFO')
    else:
        logger.log('UPDATER :: Update failed', 'ERROR')

    return jsonify(updated=updated)

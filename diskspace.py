from flask import Flask, render_template
import jsonrpclib, os

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/diskspace')
@requires_auth
def xhr_diskspace():
    return render_template('diskspace.html')

def disk_usage(path):
    st = os.statvfs(path)

    free = float(st.f_bavail * st.f_frsize) / 1073741824
    total = float(st.f_blocks * st.f_frsize) / 1073741824
    used = float((st.f_blocks - st.f_bfree) * st.f_frsize) / 1073741824

    return {
        'total': total,
        'used': used,
        'free': free,
    }

from flask import Flask, render_template
import jsonrpclib, os

from maraschino import app
from settings import *
from noneditable import *
from tools import *

@app.route('/xhr/diskspace')
@requires_auth
def xhr_diskspace():
    disks = [disk_usage('/')]
    print disks

    return render_template('diskspace.html',
        disks = disks,
    )

def disk_usage(path):
    st = os.statvfs(path)

    free = float(st.f_bavail * st.f_frsize) / 1073741824
    total = float(st.f_blocks * st.f_frsize) / 1073741824
    used = float((st.f_blocks - st.f_bfree) * st.f_frsize) / 1073741824

    return {
        'path': path,
        'total': "%.2f" % total,
        'used': "%.2f" % used,
        'free': "%.2f" % free,
        'percentage_used': int(used/total * 100),
    }

from flask import Flask, render_template
import jsonrpclib, os

from maraschino import app
from settings import *
from noneditable import *
from tools import *

from models import Disk

@app.route('/xhr/diskspace')
@requires_auth
def xhr_diskspace():
    disks = []
    disks_db = Disk.query.order_by(Disk.position)

    if disks_db.count() > 0:
        disks.append(disk_usage(disks_db.path))

    return render_template('diskspace.html',
        disks = disks,
    )

@app.route('/xhr/add_disk_dialog')
@requires_auth
def add_disk_dialog():
    return add_edit_disk_dialog()

@app.route('/xhr/edit_disk_dialog/<disk_id>')
@requires_auth
def edit_disk_dialog(disk_id):
    return add_edit_disk_dialog(disk_id)

def add_edit_disk_dialog(disk_id=None):
    disk = None

    if disk_id:
        try:
            disk = Disk.query.filter(Disk.id == disk_id).first()

        except:
            pass

    return render_template('add_edit_disk_dialog.html',
        disk = disk,
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

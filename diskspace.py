from flask import Flask, jsonify, render_template
import jsonrpclib, os, platform, ctypes

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
        for disk_db in disks_db:
            disk = disk_usage(disk_db.path)
            disk['path'] = disk_db.path
            disk['id'] = disk_db.id
            disks.append(disk)

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

@app.route('/xhr/add_edit_disk', methods=['POST'])
@requires_auth
def add_edit_disk():
    path = request.form['path']
    position = request.form['position']

    if path == '':
        return jsonify({ 'status': 'error' })

    if position == '':
        position = None

    if 'disk_id' in request.form:
        disk = Disk.query.filter(Disk.id == request.form['disk_id']).first()
        disk.path = path
        disk.position = position

    else:
        disk = Disk(
            path,
            position,
        )

    try:
        disk_usage(disk.path)
        db_session.add(disk)
        db_session.commit()

    except:
        return jsonify({ 'status': 'error' })

    return xhr_diskspace()

@app.route('/xhr/delete_disk/<disk_id>', methods=['POST'])
@requires_auth
def delete_disk(disk_id):
    try:
        disk = Disk.query.filter(Disk.id == disk_id).first()
        db_session.delete(disk)
        db_session.commit()

    except:
        return jsonify({ 'status': 'error' })

    return xhr_diskspace()

def disk_usage(path):
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        print free_bytes
    else:
        st = os.statvfs(path)
    
        free = float(st.f_bavail * st.f_frsize) / 1073741824
        total = float(st.f_blocks * st.f_frsize) / 1073741824
        used = float((st.f_blocks - st.f_bfree) * st.f_frsize) / 1073741824
    
        return {
            'total': "%.2f" % total,
            'used': "%.2f" % used,
            'free': "%.2f" % free,
            'percentage_used': int(used/total * 100),
        }

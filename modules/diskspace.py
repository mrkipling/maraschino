from flask import Flask, jsonify, render_template, request
import os, platform, ctypes

from maraschino import app
from maraschino.noneditable import *
from maraschino.tools import *
from maraschino.database import db_session

from maraschino.models import Disk, Disk2

@app.route('/xhr/diskspace')
@requires_auth
def xhr_diskspace():
    disks_db_old = Disk.query.order_by(Disk.position)
    if disks_db_old.count() > 0:
        disk_legacy_check()

    disks = []
    disks_db = Disk2.query.order_by(Disk2.position)

    if disks_db.count() > 0:
        for disk_db in disks_db:
            disk = disk_usage(disk_db.path)
            disk['path'] = disk_db.path
            disk['name'] = disk_db.name
            disk['id'] = disk_db.id
            disks.append(disk)

    return render_template('diskspace.html',
        disks=disks,
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
            disk = Disk2.query.filter(Disk2.id == disk_id).first()

        except:
            pass

    return render_template('add_edit_disk_dialog.html',
        disk=disk,
    )

@app.route('/xhr/add_edit_disk', methods=['POST'])
@requires_auth
def add_edit_disk():
    path = request.form['path']
    name = request.form['name']
    position = request.form['position']

    if path == '':
        return jsonify({'status': 'error'})

    if position == '':
        position = None

    if 'disk_id' in request.form:
        disk = Disk2.query.filter(Disk2.id == request.form['disk_id']).first()
        disk.path = path
        disk.name = name
        disk.position = position

    else:
        disk = Disk2(
            path,
            name,
            position,
        )

    try:
        disk_usage(disk.path)
        db_session.add(disk)
        db_session.commit()

    except:
        return jsonify({'status': 'error'})

    return xhr_diskspace()

@app.route('/xhr/delete_disk/<disk_id>', methods=['POST'])
@requires_auth
def delete_disk(disk_id):
    try:
        disk = Disk.query.filter(Disk.id == disk_id).first()
        db_session.delete(disk)
        db_session.commit()

    except:
        return jsonify({'status': 'error'})

    return xhr_diskspace()

def disk_usage(path):
    if platform.system() == 'Windows':
        freeuser = ctypes.c_int64()
        total = ctypes.c_int64()
        free = ctypes.c_int64()
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), ctypes.byref(freeuser), ctypes.byref(total), ctypes.byref(free))
        used = (total.value - free.value)
        total = total.value
        free = free.value

    else:
        st = os.statvfs(path)

        free = float(st.f_bavail * st.f_frsize)
        total = float(st.f_blocks * st.f_frsize)
        used = float((st.f_blocks - st.f_bfree) * st.f_frsize)

    return {
        'total': format_number(total),
        'used': format_number(used),
        'free': format_number(free),
        'percentage_used': int((float(used)/float(total))*100),
    }

def disk_legacy_check():
    disks_db_old = Disk.query.order_by(Disk.position)
    for disk_old in disks_db_old:

        disk = Disk2(
            disk_old.path,
            disk_old.path,
            disk_old.position,
        )

        try:
            disk_usage(disk_old.path)
            db_session.add(disk)
            db_session.delete(disk_old)
            db_session.commit()

        except:
            return jsonify({'status': 'error'})

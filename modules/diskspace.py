from flask import Flask, jsonify, render_template, request
import os, platform, ctypes

from maraschino import app, logger
from maraschino.tools import requires_auth, format_number, get_setting_value
from maraschino.database import db_session

from maraschino.models import Disk, HardDisk

@app.route('/xhr/diskspace/')
@requires_auth
def xhr_diskspace():
    # Legacy check
    disks_db_old = Disk.query.order_by(Disk.position)
    if disks_db_old.count() > 0:
        legacy_disk_migrate()

    disks = {'groups':[], 'disks':[]}

    # Get list of disks from database
    disks_db = HardDisk.query.order_by(HardDisk.position)

    if disks_db.count() > 0:
        for disk_db in disks_db:
            disk = disk_usage(disk_db.data['path'])
            disk['path'] = disk_db.data['path']
            disk['name'] = disk_db.data['name']
            disk['group'] = disk_db.data['group']
            disk['id'] = disk_db.id

            if disk['group'] and disk['group'] not in [g['name'] for g in disks['groups']]:
                disks['groups'].append(
                    {
                        'name': disk['group'],
                        'total': 0,
                        'used': 0,
                        'free': 0
                    }
                )
            disks['disks'].append(disk)

        # Add all disk values in group to get total group values
        for disk in disks['disks']:
            if disk['group']:
                for group in disks['groups']:
                    if disk['group'] == group['name']:
                        group['total'] = group['total'] + int(float(disk['total']))
                        group['used'] = group['used'] + int(float(disk['used']))
                        group['free'] = group['free'] + int(float(disk['free']))

        # Make the group values readable data
        if disks['groups']:
            for group in disks['groups']:
                group['percentage_used'] = int((float(group['used'])/float(group['total']))*100)
                group['total'] = format_number(group['total'])
                group['used'] = format_number(group['used'])
                group['free'] = format_number(group['free'])

        # make the disk values readable data
        for disk in disks['disks']:
            disk['total'] = format_number(disk['total'])
            disk['used'] = format_number(disk['used'])
            disk['free'] = format_number(disk['free'])

    return render_template('diskspace.html',
        disks=disks,
        show_grouped_disks=get_setting_value('show_grouped_disks') == '1'
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
            disk = HardDisk.query.filter(HardDisk.id == disk_id).first()

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
    group = request.form['group']
    position = request.form['position']

    if path == '':
        return jsonify({'status': 'error'})

    if position == '':
        position = None

    if 'disk_id' in request.form:
        disk = HardDisk.query.filter(HardDisk.id == request.form['disk_id']).first()
        disk.data = {'path': path, 'name': name, 'group': group}
        disk.position = position

    else:
        disk = HardDisk(
            data={'path': path, 'name': name, 'group': group},
            position=position,
        )

    try:
        db_session.add(disk)
        db_session.commit()

    except:
        return jsonify({'status': 'error'})

    return xhr_diskspace()

@app.route('/xhr/delete_disk/<disk_id>', methods=['POST'])
@requires_auth
def delete_disk(disk_id):
    try:
        disk = HardDisk.query.filter(HardDisk.id == disk_id).first()
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
        'total': total,
        'used': used,
        'free': free,
        'percentage_used': int((float(used)/float(total))*100),
    }

def legacy_disk_migrate():
    logger.log('DISKSPACE :: Migrating legacy disks', 'INFO')

    disks_db_old = Disk.query.order_by(Disk.position)
    for disk_old in disks_db_old:

        disk = HardDisk(
            data={
                'path': disk_old.path,
                'name': disk_old.path,
                'group': '',
            },
            position=disk_old.position
        )

        try:
            db_session.add(disk)
            db_session.delete(disk_old)
            db_session.commit()

        except:
            return jsonify({'status': 'error'})

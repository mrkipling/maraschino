#Author: Guido S. Nickels <gsn@kernel-oops.de>
#Based on the utorrent maraschino module

from flask import Flask, jsonify, render_template
from datetime import timedelta
from maraschino import app, logger
from maraschino.tools import *
from rtorrent import RTorrent

def log_error(ex):
    logger.log('RTORRENTDL :: EXCEPTION - %s' % ex, 'DEBUG')

@app.route('/xhr/rtorrentdl/')
@requires_auth

def xhr_rtorrentdl():
	# initialize empty list, which will be later populated with listing
	# of active torrents
	torrentlist = list()

	# connection flag
	connected = False

	try:
		if get_setting_value('rtorrent_url') is not None:
			client = RTorrent(
				get_setting_value('rtorrent_url'),
				get_setting_value('rtorrent_user'),
				get_setting_value('rtorrent_password'),
				True
			)

			if client is not None:
				connected = True

			# loop through each job, add any active (downloading) torrents to torrentlist()
			# torrent: { info_hash: <HASH>, name: <NAME> }
			for torrent in client.get_torrents():
				# friendly status
				if torrent.complete:
					if torrent.active:
						status = 'seeding'
					else:
						status = 'done'
				else:
					if torrent.active:
						status = 'busy'
					else:
						status = 'inactive'

				# get torrent file list
				torrent_filelist = []
				for file_current in torrent.get_files():
					torrent_filelist.append(os.path.join(torrent.directory,file_current.path))

				# what's left?
				percent_done = float(100.0 / torrent.size_bytes * (torrent.size_bytes-torrent.left_bytes))
				time_left = str(timedelta(seconds = float(torrent.left_bytes) / torrent.down_rate)) if torrent.down_rate > 0 else -1

				# append to list
				torrentlist.append({
					'name': torrent.name,
					'id': torrent.info_hash,
					'status': status,
					'torrent_state': torrent.state,
					'progress': percent_done,
					'sec_left': time_left,
					'seed_ratio': torrent.ratio,
					'folder': torrent.directory,
					'files': '|'.join(torrent_filelist)
				})

			# no torrents -> empty list
			if not torrentlist.__len__():
				torrentlist = None

	except Exception as ex:
		log_error(ex)
		torrentlist = None

	return render_template('rtorrentdl.html',
		torrents = torrentlist
	)

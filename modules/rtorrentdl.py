#Author: Guido S. Nickels <gsn@kernel-oops.de>
#Based on the utorrent maraschino module

from flask import render_template
from datetime import timedelta
from maraschino import app, logger
from maraschino.tools import *
from rtorrent import RTorrent

def log_error(ex):
	logger.log('RTORRENTDL :: EXCEPTION - %s' % ex, 'DEBUG')

@app.route('/xhr/rtorrentdl/')
@requires_auth

def xhr_rtorrentdl():

	# url qualification
	def url_qualify(url_proto,url_host,url_port):

		url_host_part=str(url_host).partition('/')

		# validate host (kinda... just make sure it's not empty)
		if url_host_part[0]:

			# validate port
			if not url_port:

				# for http and https we can assume default service ports
				if url_proto == 'http':
					url_port = 80
				elif url_proto == 'https':
					url_port = 443
				else:
					raise Exception('port must be defined for protocol %s' % (url_proto))

			else:
				try:
					url_port=int(url_port)
				except ValueError:
					raise Exception('port must be a numeric value')

			url_qualified='%s://%s:%i%s%s' % (
				url_proto,
				url_host_part[0],
				url_port,
				url_host_part[1],
				url_host_part[2]
			)

			return url_qualified

		else:
			raise Exception('invalid host: %s' % (url_host[0]))

	# initialize empty list, which will be later populated with listing
	# of active torrents
	torrentlist = list()

	# connection flag
	connected = False

	# global rates
	down_rate = 0.0
	up_rate = 0.0

	rtorrent_url = None
	rtorrent_user = None
	rtorrent_password = None

	try:
		if get_setting_value('rtorrent_host') is not None:
			rtorrent_url = url_qualify(
				get_setting_value('rtorrent_proto'),
				get_setting_value('rtorrent_host'),
				get_setting_value('rtorrent_port')
			)
	except Exception as ex:
		log_error(ex)

	try:
		if rtorrent_url:
			# user/password login is not implemented for scgi
			if get_setting_value('rtorrent_proto') != 'scgi':
				rtorrent_user = get_setting_value('rtorrent_user')
				rtorrent_password = get_setting_value('rtorrent_password')

			client = RTorrent(rtorrent_url,rtorrent_user,rtorrent_password,True)

			if client is not None:
				connected = True
				down_rate = client.get_down_rate()
				up_rate = client.get_up_rate()

			# loop through each job and add all torrents to torrentlist()
			for torrent in client.get_torrents():
				# friendly status and time left
				time_left = -1
				if torrent.complete:
					if torrent.active:
						status = 'seeding'
					else:
						status = 'done'
				else:
					if torrent.active:
						if torrent.down_rate > 0:
							time_left = str(timedelta(seconds = round(float(torrent.left_bytes) / torrent.down_rate)))
							status = 'leeching'
						else:
							status = 'waiting'
					else:
						status = 'inactive'

				# get torrent file list
				# FIXME takes too much time and is not used anyway for now
				#torrent_filelist = []
				#for file_current in torrent.get_files():
				#	torrent_filelist.append(os.path.join(torrent.directory,file_current.path))

				# what's left?
				progress = float(100.0 / torrent.size_bytes * (torrent.size_bytes-torrent.left_bytes))

				# append to list
				torrentlist.append({
					'name': torrent.name,
					'info_hash': torrent.info_hash,
					'status': status,
					'state': torrent.state,
					'progress': progress,
					'time_left': time_left,
					'down_rate': torrent.down_rate,
					'up_rate': torrent.up_rate,
					'ratio': torrent.ratio
				#	'folder': torrent.directory,
				#	'files': '|'.join(torrent_filelist)
				})

			# no torrents -> empty list
			if not torrentlist.__len__():
				torrentlist = None

	except Exception as ex:
		log_error(ex)
		torrentlist = None

	return render_template('rtorrentdl.html',
		connected = connected,
		torrentlist_scroll = get_setting_value('rtorrent_list_scroll'),
		torrentlist = torrentlist,
		down_rate = down_rate,
		up_rate = up_rate
	)

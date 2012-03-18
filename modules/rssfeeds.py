from flask import Flask, render_template

from Maraschino import app
from maraschino.tools import *
from feedparser import feedparser
import re

cat_newznab = [
            {'id': '', 'name': 'Select Category'},
        { 'label' : 'Movies' , 'value' : [
            {'id': 2000, 'name': ': All'},
            {'id': 2010, 'name': ': Foreign'},
            {'id': 2040, 'name': ': HD'},
            {'id': 2020, 'name': ': Other'},
            {'id': 2030, 'name': ': SD'},
          ]
        },
        { 'label' : 'TV' , 'value' : [
            {'id': 5000, 'name': ': All'},
            {'id': 5020, 'name': ': Foreign'},
            {'id': 5040, 'name': ': HD'},
            {'id': 5050, 'name': ': Other'},
            {'id': 5030, 'name': ': SD'},
            {'id': 5060, 'name': ': Sport'},
          ]
        },
        { 'label' : 'Audio' , 'value' : [
            {'id': 3000, 'name': ': All'},
            {'id': 3030, 'name': ': Audiobook'},
            {'id': 3040, 'name': ': Lossless'},
            {'id': 3010, 'name': ': MP3'},
            {'id': 3020, 'name': ': Video'},
          ]
        },
        { 'label' : 'Consoles' , 'value' : [
            {'id': 1000, 'name': ': All'},
            {'id': 1010, 'name': ': NDS'},
            {'id': 1080, 'name': ': PS3'},
            {'id': 1020, 'name': ': PSP'},
            {'id': 1030, 'name': ': Wii'},
            {'id': 1060, 'name': ': WiiWare/VC'},
            {'id': 1070, 'name': ': XBOX 360 DLC'},
            {'id': 1040, 'name': ': Xbox'},
            {'id': 1050, 'name': ': Xbox 360'},
          ]
        },
        { 'label' : 'PC' , 'value' : [
            {'id': 4000, 'name': ': All'},
            {'id': 4010, 'name': ': 0day'},
            {'id': 4050, 'name': ': Games'},
            {'id': 4020, 'name': ': ISO'},
            {'id': 4030, 'name': ': Mac'},
            {'id': 4040, 'name': ': Phone'},
          ]
        },
        { 'label' : 'XXX' , 'value' : [
            {'id': 6000, 'name': ': All'},
            {'id': 6010, 'name': ': DVD'},
            {'id': 6020, 'name': ': WMV'},
            {'id': 6030, 'name': ': XviD'},
            {'id': 6040, 'name': ': x264'},
          ]
        },
        { 'label' : 'Other' , 'value' : [
            {'id': 7000, 'name': ': All'},
            {'id': 7030, 'name': ': Comics'},
            {'id': 7020, 'name': ': Ebook'},
            {'id': 7010, 'name': ': Misc'} 
          ]
        },
    ]

cat_nzbmatrix = [
            { 'id': 0 , 'name': 'Select Category...' },
        { 'label' : 'Movies' , 'value' : [
            { 'id': 1,  'name': ': DVD' },
            { 'id': 2,  'name': ': Divx/Xvid' },
            { 'id': 54, 'name': ': BRRip' },
            { 'id': 42, 'name': ': HD (x264)' },
            { 'id': 50, 'name': ': HD (Image)' },
            { 'id': 48, 'name': ': WMV-HD' },
            { 'id': 3,  'name': ': SVCD/VCD' },
            { 'id': 4,  'name': ': Other' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 5,  'name': ': DVD' },
            { 'id': 6,  'name': ': Divx/Xvid' },
            { 'id': 41, 'name': ': HD' },
            { 'id': 7,  'name': ': Sport/Ent' },
            { 'id': 8,  'name': ': Other' },
          ]
        },
        { 'label' : 'Documentaries' , 'value' : [
            { 'id': 9,  'name': ': STD' },
            { 'id': 53, 'name': ': HD' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 10, 'name': ': PC' },
            { 'id': 11, 'name': ': PS2' },
            { 'id': 43, 'name': ': PS3' },
            { 'id': 12, 'name': ': PSP' },
            { 'id': 13, 'name': ': Xbox' },
            { 'id': 14, 'name': ': Xbox360' },
            { 'id': 56, 'name': ': Xbox360 (Other)' },
            { 'id': 15, 'name': ': PS1' },
            { 'id': 16, 'name': ': Dreamcast' },
            { 'id': 44, 'name': ': Wii' },
            { 'id': 51, 'name': ': Wii VC' },
            { 'id': 45, 'name': ': DS' },
            { 'id': 46, 'name': ': GameCube' },
            { 'id': 17, 'name': ': Other' },
          ]
        },
        { 'label' : 'Apps' , 'value' : [
            { 'id': 18, 'name': ': PC' },
            { 'id': 19, 'name': ': Mac' },
            { 'id': 52, 'name': ': Portable' },
            { 'id': 20, 'name': ': Linux' },
            { 'id': 55, 'name': ': Phone' },
            { 'id': 21, 'name': ': Other' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 22, 'name': ': MP3 Albums' },
            { 'id': 47, 'name': ': MP3 Singles' },
            { 'id': 23, 'name': ': Lossless' },
            { 'id': 24, 'name': ': DVD' },
            { 'id': 25, 'name': ': Video' },
            { 'id': 27, 'name': ': Other' },
          ]
        },
        { 'label' : 'Anime' , 'value' : [
            { 'id': 28, 'name': ': ALL' },
          ]
        },
        { 'label' : 'Other' , 'value' : [
            { 'id': 49, 'name': ': Audio Books' },
            { 'id': 33, 'name': ': Emulation' },
            { 'id': 34, 'name': ': PPC/PDA' },
            { 'id': 26, 'name': ': Radio' },
            { 'id': 36, 'name': ': E-Books' },
            { 'id': 37, 'name': ': Images' },
            { 'id': 38, 'name': ': Mobile Phone' },
            { 'id': 39, 'name': ': Extra Pars/Fills' },
            { 'id': 40, 'name': ': Other' },
          ]
        },
    ]

cat_piratebay = [
            {'id': '' , 'name': 'Select Category...' },
            {'id': 0, 'name': 'Everything'},
        { 'label' : 'Audio' , 'value' : [
            {'id': 100, 'name': ': All'},
            {'id': 101, 'name': ': Music'},
            {'id': 102, 'name': ': Audio books'},
            {'id': 103, 'name': ': Sound clips'},
            {'id': 104, 'name': ': FLAC'},
            {'id': 199, 'name': ': Other'},
          ]
        },
        { 'label' : 'Video' , 'value' : [
            {'id': 200, 'name': ': All'},
            {'id': 201, 'name': ': Movies'},
            {'id': 202, 'name': ': Movies DVDR'},
            {'id': 203, 'name': ': Music videos'},
            {'id': 204, 'name': ': Movie clips'},
            {'id': 205, 'name': ': TV Shows'},
            {'id': 206, 'name': ': Handheld'},
            {'id': 207, 'name': ': Highres - Movies'},
            {'id': 208, 'name': ': Highres - TV Shows'},
            {'id': 209, 'name': ': 3D'},
            {'id': 299, 'name': ': Other'},
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            {'id': 300, 'name': ': All'},
            {'id': 301, 'name': ': Windows'},
            {'id': 302, 'name': ': Mac'},
            {'id': 303, 'name': ': UNIX'},
            {'id': 304, 'name': ': Handheld'},
            {'id': 305, 'name': ': IOS (iPad/iPhone)'},
            {'id': 306, 'name': ': Android'},
            {'id': 399, 'name': ': Other OS'},
          ]
        },
        { 'label' : 'Games' , 'value' : [
            {'id': 400, 'name': ': All'},
            {'id': 401, 'name': ': PC'},
            {'id': 402, 'name': ': MAC'},
            {'id': 403, 'name': ': PSX'},
            {'id': 404, 'name': ': XBOX360'},
            {'id': 405, 'name': ': WII'},
            {'id': 406, 'name': ': Handheld'},
            {'id': 407, 'name': ': IOS (iPad/iPhone)'},
            {'id': 408, 'name': ': Android'},
            {'id': 499, 'name': ': Other'},
          ]
        },
        { 'label' : 'Other' , 'value' : [
            {'id': 600, 'name': ': All'},
            {'id': 600, 'name': ': E-books'},
            {'id': 600, 'name': ': Comics'},
            {'id': 600, 'name': ': Pictures'},
            {'id': 600, 'name': ': Covers'},
            {'id': 600, 'name': ': Physibles'},
            {'id': 600, 'name': ': Other'},
          ]
        },
      ]
    
cat_rlslog = [
           { 'id': 0, 'name': 'Select Category...' },
        { 'label' : 'Movies', 'value' : [
            { 'id': 101, 'path': 'movies/bdrip' ,      'name': ': BDRip' },
            { 'id': 102, 'path': 'movies/cam',         'name': ': Cam' },
            { 'id': 103, 'path': 'movies/dvdrip',      'name': ': DVDRip' },
            { 'id': 104, 'path': 'movies/dvdrip-old',  'name': ': DVDRip Old' },
            { 'id': 105, 'path': 'movies/dvdscr',      'name': ': DVDSCR' },
            { 'id': 106, 'path': 'movies/hdrip',       'name': ': HDRip' },
            { 'id': 107, 'path': 'movies/r5',          'name': ': R5' },
            { 'id': 108, 'path': 'movies/scr',         'name': ': SCR' },
            { 'id': 109, 'path': 'movies/staff-picks', 'name': ': Staff Picks' },
            { 'id': 110, 'path': 'movies/telecine',    'name': ': Telecine' },
            { 'id': 111, 'path': 'movies/telesync',    'name': ': Telesync' },
            { 'id': 112, 'path': 'movies/workprint',   'name': ': Workprint' },
          ]
        },
        { 'label' : 'TV', 'value' : [
            { 'id': 201, 'path': 'tv-shows',           'name': ': TV Shows' },
            { 'id': 202, 'path': 'tv-shows/tv-packs',  'name': ': TV Packs' },
          ]
        },
        { 'label' : 'Music', 'value' : [
            { 'id': 301, 'path': 'music/albums',       'name': ': Albums' },
            { 'id': 302, 'path': 'music/itunes',       'name': ': iTunes' },
            { 'id': 304, 'path': 'music/mvid',         'name': ': MViD' },
            { 'id': 305, 'path': 'movies/singles',     'name': ': Singles/EPs' },
            { 'id': 306, 'path': 'movies/musicpicks',  'name': ': Staff Picks' },
          ]
        },
        { 'label' : 'Games', 'value' : [
            { 'id': 401, 'path': 'games/pc',           'name': ': PC' },
            { 'id': 402, 'path': 'games/ps3-games',    'name': ': PS3' },
            { 'id': 403, 'path': 'games/psp',          'name': ': PSP' },
            { 'id': 404, 'path': 'games/wii',          'name': ': Wii' },
            { 'id': 405, 'path': 'games/xbox360',      'name': ': XBOX360' },
          ]
        },
        { 'label' : 'Applications', 'value' : [
            { 'id': 501, 'path': 'applications/android',      'name': ': Android' },
            { 'id': 502, 'path': 'applications/ios',          'name': ': iOS' },
            { 'id': 503, 'path': 'applications/mac',          'name': ': MAC' },
            { 'id': 504, 'path': 'applications/windows',      'name': ': Windows' },
          ]
        },
    ]

cat_scnsrc = [
            { 'id': 0,                          'name': 'Select Category...' },
        { 'label' : 'Movies', 'value' : [
            { 'id': '/films/feed/',              'name': ': All' },
            { 'id': '/films/bdrip/feed/',        'name': ': BDRip' },
            { 'id': '/films/bdscr/feed/',        'name': ': BDSCR' },
            { 'id': '/films/bluray/feed/',       'name': ': BluRay' },
            { 'id': '/films/cam/feed/',          'name': ': Cam' },
            { 'id': '/films/dvdrip/feed/',       'name': ': DVDRip' },
            { 'id': '/films/dvdscr/feed/',       'name': ': DVDSCR' },
            { 'id': '/films/hd/feed/',           'name': ': HD' },
            { 'id': '/films/r5/feed/',           'name': ': R5' },
            { 'id': '/films/scr/feed/',          'name': ': SCR' },
            { 'id': '/films/telecine/feed/',     'name': ': Telecine' },
            { 'id': '/films/telesync/feed/',     'name': ': Telesync' },
            { 'id': '/films/workprint/feed/',    'name': ': Workprint' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': '/tv/feed/',                 'name': ': All' },        
            { 'id': '/tv/dvd/feed/',             'name': ': DVD' },
            { 'id': '/tv/miniseries/feed/',      'name': ': Mini Series' },
            { 'id': '/tv/ppv/feed/',             'name': ': PPV' },
            { 'id': '/tv/preair/feed/',          'name': ': PREAiR' },
            { 'id': '/tv/sports/feed/',          'name': ': Sports' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': '/new-music/feed/',                'name': ': All' },
            { 'id': '/new-music/concert/feed/',        'name': ': Concert' },
            { 'id': '/new-music-video-releases/feed/', 'name': ': MViD' },
            { 'id': '/new-music/flac/feed/',           'name': ': FLAC' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': '/games/feed/',             'name': ': All' },
            { 'id': '/games/clone/feed/',       'name': ': Clone' },
            { 'id': '/games/iso/feed/',         'name': ': ISO' },
            { 'id': '/games/ps3/feed/',         'name': ': PS3' },
            { 'id': '/games/xbox360/feed/',     'name': ': XBOX360' },
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            { 'id': '/applications/iphone/feed/',  'name': ': iPhone' },
            { 'id': '/applications/macosx/feed/',  'name': ': MAC' },
            { 'id': '/applications/windows/feed/', 'name': ': Windows' },
          ]
        },
    ]

@app.route('/xhr/rssfeeds')
@app.route('/xhr/rssfeeds/<site>')
@requires_auth
def xhr_rssfeeds_site(site = None):

    if site == 'nzbmatrix':
        categories = cat_nzbmatrix
    elif site == 'newznab':
        categories = cat_newznab
    elif site == 'piratebay':
        categories = cat_piratebay
    elif site == 'rlslog':
        categories = cat_rlslog
    elif site == 'scnsrc':
        categories = cat_scnsrc
    elif site == 'oneddl':
        categories = cat_oneddl
    elif site == 'sceper':
        categories = cat_sceper
    elif site == 'vcdq':
        categories = cat_vcdq

    else:
       categories = None

    return render_template('rssfeeds.html',
        site = site,
        categories = categories,
    )

@app.route('/xhr/rssfeeds/<site>/<category>')
@requires_auth
def xhr_rssfeeds_category(site = None, category = None):

    if site == "nzbmatrix":
        categories = cat_nzbmatrix

        username = get_setting_value('nzb_matrix_user')
        apikey = get_setting_value('nzb_matrix_API')

        if username and apikey:
            feed = 'http://rss.nzbmatrix.com/rss.php?page=download&username=' + username + '&apikey=' + apikey + '&subcat=' + category
        else:
            feed = 'http://rss.nzbmatrix.com/rss.php?&subcat=' + category

        feed = feedparser.parse(feed)

        for entry in feed['entries']:
            r = re.compile('Size:</b> (.*?)<br />')
            result = r.search(entry['description'])
            if result:
                size = result.group(1)
            else:
                size = ""

            r = re.compile('Added:</b> (.*?)<br />')
            result = r.search(entry['description'])
            if result:
                added = result.group(1)
            else:
                added = ""

            r = re.compile('Group:</b> (.*?)<br />')
            result = r.search(entry['description'])
            if result:
                group = result.group(1)
            else:
                group = ""

            r = re.compile('NFO:</b> <a href="(.*?)">View NFO</a>')
            result = r.search(entry['description'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            r = re.compile('IMDB Link:</b> <a href="(.*?)">Go To IMDB</a>')
            result = r.search(entry['description'])
            if result:
                imdblink = result.group(1)
            else:
                imdblink = ""

            if username and apikey:
                r = re.compile('View NZB:</b> <a href="(.*?)">View</a>')
                result = r.search(entry['description'])
                if result:
                    nzblink = result.group(1)
                    entry['link'] = nzblink
                    nzblink = nzblink[7:]
                else:
                    nzblink = ""
            else:
                nzblink = entry['link'][7:]

            description = { 'size': size, 'added': added, 'group': group, 'nfolink': nfolink, 'imdblink': imdblink, 'nzblink': nzblink }
            entry['description'] = description

    elif site == "piratebay":
        categories = cat_piratebay
        feed = 'http://rss.thepiratebay.se/' + category
        feed = feedparser.parse(feed)

    elif site == "scnsrc":
        categories = cat_scnsrc
        feed = 'http://www.scnsrc.me/category' + category
        feed = feedparser.parse(feed)

    elif site == "newznab":
        categories = cat_newznab
        feed = 'http://nzb.su/rss?t=' + category
        feed = feedparser.parse(feed)

    elif site == "rlslog":
        categories = cat_rlslog

        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']

        feed = 'http://www.rlslog.net/category/' + path + '/feed/'
        feed = feedparser.parse(feed)


        for entry in feed['entries']:
            r = re.compile('<strong>Size:</strong> (.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            else:
                size = ""

            r = re.compile('<strong>IMDB Rating</strong>: (.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdbrating = result.group(1)
            else:
                imdbrating = ""

            r = re.compile('<a href="(.*?)">iMDB</a>')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdblink = result.group(1)
            else:
                imdblink = ""

            r = re.compile('<strong>NFO:</strong> <a href="(.*?)">')
            result = r.search(entry['content'][0]['value'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            r = re.compile('<strong>NFO:</strong> <a href="(.*?)">')
            result = r.search(entry['content'][0]['value'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            description = { 'size': size, 'imdbrating': imdbrating, 'imdblink': imdblink, 'nfolink': nfolink }
            entry['description'] = description

    elif site == "oneddl":
        categories = cat_oneddl
        feed = 'http://www.oneddl.eu/category' + category
        feed = feedparser.parse(feed)

    elif site == "sceper":
        categories = cat_sceper
        feed = 'http://www.sceper.eu/category' + category
        feed = feedparser.parse(feed)

    elif site == "vcdq":
        categories = cat_vcdq
        feed = 'http://www.vcdq.com' + category
        feed = feedparser.parse(feed)
        
    else:
        feed = None

    return render_template('rssfeeds.html',
        site = site,
        category = int(category),
        categories = categories,
        feed = feed,
    )

from flask import Flask, render_template

from Maraschino import app
from maraschino.tools import *
from feedparser import feedparser
import re

cat_newznab = [
        {'id': '', 'name': 'Select Category'},
        {'id': 1000, 'name': 'Console'},
        {'id': 1010, 'name': 'Console: NDS'},
        {'id': 1080, 'name': 'Console: PS3'},
        {'id': 1020, 'name': 'Console: PSP'},
        {'id': 1030, 'name': 'Console: Wii'},
        {'id': 1060, 'name': 'Console: WiiWare/VC'},
        {'id': 1070, 'name': 'Console: XBOX 360 DLC'},
        {'id': 1040, 'name': 'Console: Xbox'},
        {'id': 1050, 'name': 'Console: Xbox 360'},
        {'id': 2000, 'name': 'Movies'},
        {'id': 2010, 'name': 'Movies: Foreign'},
        {'id': 2040, 'name': 'Movies: HD'},
        {'id': 2020, 'name': 'Movies: Other'},
        {'id': 2030, 'name': 'Movies: SD'},
        {'id': 3000, 'name': 'Audio'},
        {'id': 3030, 'name': 'Audio: Audiobook'},
        {'id': 3040, 'name': 'Audio: Lossless'},
        {'id': 3010, 'name': 'Audio: MP3'},
        {'id': 3020, 'name': 'Audio: Video'},
        {'id': 4000, 'name': 'PC'},
        {'id': 4010, 'name': 'PC: 0day'},
        {'id': 4050, 'name': 'PC: Games'},
        {'id': 4020, 'name': 'PC: ISO'},
        {'id': 4030, 'name': 'PC: Mac'},
        {'id': 4040, 'name': 'PC: Phone'},
        {'id': 5000, 'name': 'TV'},
        {'id': 5020, 'name': 'TV: Foreign'},
        {'id': 5040, 'name': 'TV: HD'},
        {'id': 5050, 'name': 'TV: Other'},
        {'id': 5030, 'name': 'TV: SD'},
        {'id': 5060, 'name': 'TV: Sport'},
        {'id': 6000, 'name': 'XXX'},
        {'id': 6010, 'name': 'XXX: DVD'},
        {'id': 6020, 'name': 'XXX: WMV'},
        {'id': 6030, 'name': 'XXX: XviD'},
        {'id': 6040, 'name': 'XXX: x264'},
        {'id': 7000, 'name': 'Other'},
        {'id': 7030, 'name': 'Other: Comics'},
        {'id': 7020, 'name': 'Other: Ebook'},
        {'id': 7010, 'name': 'Other: Misc'} 
      ]

cat_nzbmatrix = [
        { 'id': 0 , 'name': 'Select Category...' },
        { 'label' : 'Movies' , 'value' : [
            { 'id': 1, 'name': ': DVD' },
            { 'id': 2, 'name': ': Divx/Xvid' },
            { 'id': 54, 'name': ': BRRip' },
            { 'id': 42, 'name': ': HD (x264)' },
            { 'id': 50, 'name': ': HD (Image)' },
            { 'id': 48, 'name': ': WMV-HD' },
            { 'id': 3, 'name': ': SVCD/VCD' },
            { 'id': 4, 'name': ': Other' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 5, 'name': ': DVD' },
            { 'id': 6, 'name': ': Divx/Xvid' },
            { 'id': 41, 'name': ': HD' },
            { 'id': 7, 'name': ': Sport/Ent' },
            { 'id': 8, 'name': ': Other' },
          ]
        },
        { 'label' : 'Documentaries' , 'value' : [
            { 'id': 9, 'name': ': STD' },
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
    
cat_rlslog = [
        { 'id': 0 , 'name': 'Select Category...' },
        { 'label' : 'Movies' , 'value' : [
            { 'id': 'movies/bdrip/feed/' , 'name': ': BDRip' },
            { 'id': 'movies/cam/feed/' , 'name': ': Cam' },
            { 'id': 'movies/dvdrip/feed/' , 'name': ': DVDRip)' },
            { 'id': 'movies/dvdrip-old/feed/' , 'name': ': DVDRip Old' },
            { 'id': 'movies/dvdscr/feed/' , 'name': ': DVDSCR' },
            { 'id': 'movies/hdrip/feed/' , 'name': ': HDRip' },
            { 'id': 'movies/r5/feed/' , 'name': ': R5' },
            { 'id': 'movies/scr/feed/' , 'name': ': SCR' },
            { 'id': 'movies/staff-picks/feed/' , 'name': ': Staff Picks' },
            { 'id': 'movies/telecine/feed/' , 'name': ': Telecine' },
            { 'id': 'movies/telesync/feed/' , 'name': ': Telesync' },
            { 'id': 'movies/workprint/feed/' , 'name': ': Workprint' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 'tv-shows/feed/' , 'name': ': TV Shows' },
            { 'id': 'tv-shows/tv-packs/feed/' , 'name': ': TV Packs' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 'music/albums/feed/' , 'name': ': Albums' },
            { 'id': 'music/itunes/feed/' , 'name': ': iTunes' },
            { 'id': 'music/mvid/feed/' , 'name': ': MViD' },
            { 'id': 'movies/singles/feed/' , 'name': ': Singles/EPs' },
            { 'id': 'movies/musicpicks/feed/' , 'name': ': Staff Picks' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 'games/pc/feed/' , 'name': ': PC' },
            { 'id': 'games/ps3-games/feed/' , 'name': ': PS3' },
            { 'id': 'games/psp/feed/' , 'name': ': PSP' },
            { 'id': 'games/wii/feed/' , 'name': ': Wii' },
            { 'id': 'games/xbox360/feed/' , 'name': ': XBOX360' },
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            { 'id': 'games/android/feed/' , 'name': ': Android' },
            { 'id': 'games/ios/feed/' , 'name': ': iOS' },
            { 'id': 'games/mac/feed/' , 'name': ': MAC' },
            { 'id': 'games/windows/feed/' , 'name': ': Windows' },
          ]
        },
    ]

cat_scnsrc = [
        { 'id': 0 , 'name': 'Select Category...' },
        { 'label' : 'Movies' , 'value' : [
            { 'id': 'films/feed/' , 'name': ': All' },
            { 'id': 'films/bdrip/feed/' , 'name': ': BDRip' },
            { 'id': 'films/bdscr/feed/' , 'name': ': BDSCR' },
            { 'id': 'films/bluray/feed/' , 'name': ': BluRay' },
            { 'id': 'films/cam/feed/' , 'name': ': Cam' },
            { 'id': 'films/dvdrip/feed/' , 'name': ': DVDRip' },
            { 'id': 'films/dvdscr/feed/' , 'name': ': DVDSCR' },
            { 'id': 'films/hd/feed/' , 'name': ': HD' },
            { 'id': 'films/r5/feed/' , 'name': ': R5' },
            { 'id': 'films/scr/feed/' , 'name': ': SCR' },
            { 'id': 'films/telecine/feed/' , 'name': ': Telecine' },
            { 'id': 'films/telesync/feed/' , 'name': ': Telesync' },
            { 'id': 'films/workprint/feed/' , 'name': ': Workprint' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 'tv/feed/' , 'name': ': All' },        
            { 'id': 'tv/dvd/feed/' , 'name': ': DVD' },
            { 'id': 'tv/miniseries/feed/' , 'name': ': Mini Series' },
            { 'id': 'tv/ppv/feed/' , 'name': ': PPV' },
            { 'id': 'tv/preair/feed/' , 'name': ': PREAiR' },
            { 'id': 'tv/sports/feed/' , 'name': ': Sports' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 'new-music/feed/' , 'name': ': All' },
            { 'id': 'new-music/concert/feed/' , 'name': ': Concert' },
            { 'id': 'new-music-video-releases/feed/' , 'name': ': MViD' },
            { 'id': 'new-music/flac/feed/' , 'name': ': FLAC' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 'games/feed/' , 'name': ': All' },
            { 'id': 'games/clone/feed/' , 'name': ': Clone' },
            { 'id': 'games/iso/feed/' , 'name': ': ISO' },
            { 'id': 'games/ps3/feed/' , 'name': ': PS3' },
            { 'id': 'games/xbox360/feed/' , 'name': ': XBOX360' },
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            { 'id': 'applications/iphone/feed/' , 'name': ': iPhone' },
            { 'id': 'applications/macosx/feed/' , 'name': ': MAC' },
            { 'id': 'applications/windows/feed/' , 'name': ': Windows' },
          ]
        },
    ]

@app.route('/xhr/rssfeeds')
@app.route('/xhr/rssfeeds/<site>')
@requires_auth
def xhr_rssfeeds_site(site = None):

    if site == 'nzbmatrix':
        catagories = cat_nzbmatrix
    elif site == 'newznab':
        catagories = cat_newznab
    elif site == 'rlslog':
        catagories = cat_rlslog
    elif site == 'scnsrc':
        catagories = cat_scnsrc

    else:
       catagories = None

    return render_template('rssfeeds.html',
        site = site,
        catagories = catagories,
    )

@app.route('/xhr/rssfeeds/<site>/<catagory>')
@requires_auth
def xhr_rssfeeds_catagory(site = None, catagory = None):

    if site == "nzbmatrix":
        catagories = cat_nzbmatrix

        username = get_setting_value('nzb_matrix_user')
        apikey = get_setting_value('nzb_matrix_API')

        if username and apikey:
            feed = 'http://rss.nzbmatrix.com/rss.php?page=download&username=' + username + '&apikey=' + apikey + '&subcat=' + catagory
        else:
            feed = 'http://rss.nzbmatrix.com/rss.php?&subcat=' + catagory

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

    elif site == "newznab":
        catagories = cat_newznab
        feed = 'http://nzb.su/rss?t=' + catagory
        feed = feedparser.parse(feed)

    elif site == "rlslog":
        catagories = cat_rlslog
        feed = 'http://www.rlslos.net/category' + catagory
        feed = feedparser.parse(feed)

    elif site == "scnsrc":
        catagories = cat_scnsrc
        feed = 'http://www.scnsrc.me/category' + catagory
        feed = feedparser.parse(feed)

    else:
        feed = None

    return render_template('rssfeeds.html',
        site = site,
        catagory = int(catagory),
        catagories = catagories,
        feed = feed,
    )

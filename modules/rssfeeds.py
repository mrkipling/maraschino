from flask import Flask, render_template

from Maraschino import app
from maraschino.tools import *
from feedparser import feedparser
import re

cat_newznab = [
            {'id': '', 'name': 'Select Category'},
        { 'label' : 'Movies' , 'value' : [
            {'id': 2000, 'name': 'All'},
            {'id': 2010, 'name': 'Foreign'},
            {'id': 2040, 'name': 'HD'},
            {'id': 2020, 'name': 'Other'},
            {'id': 2030, 'name': 'SD'},
          ]
        },
        { 'label' : 'TV' , 'value' : [
            {'id': 5000, 'name': 'All'},
            {'id': 5020, 'name': 'Foreign'},
            {'id': 5040, 'name': 'HD'},
            {'id': 5050, 'name': 'Other'},
            {'id': 5030, 'name': 'SD'},
            {'id': 5060, 'name': 'Sport'},
          ]
        },
        { 'label' : 'Audio' , 'value' : [
            {'id': 3000, 'name': 'All'},
            {'id': 3030, 'name': 'Audiobook'},
            {'id': 3040, 'name': 'Lossless'},
            {'id': 3010, 'name': 'MP3'},
            {'id': 3020, 'name': 'Video'},
          ]
        },
        { 'label' : 'Consoles' , 'value' : [
            {'id': 1000, 'name': 'All'},
            {'id': 1010, 'name': 'NDS'},
            {'id': 1080, 'name': 'PS3'},
            {'id': 1020, 'name': 'PSP'},
            {'id': 1030, 'name': 'Wii'},
            {'id': 1060, 'name': 'WiiWare/VC'},
            {'id': 1070, 'name': 'XBOX 360 DLC'},
            {'id': 1040, 'name': 'Xbox'},
            {'id': 1050, 'name': 'Xbox 360'},
          ]
        },
        { 'label' : 'PC' , 'value' : [
            {'id': 4000, 'name': 'All'},
            {'id': 4010, 'name': '0day'},
            {'id': 4050, 'name': 'Games'},
            {'id': 4020, 'name': 'ISO'},
            {'id': 4030, 'name': 'Mac'},
            {'id': 4040, 'name': 'Phone'},
          ]
        },
        { 'label' : 'XXX' , 'value' : [
            {'id': 6000, 'name': 'All'},
            {'id': 6010, 'name': 'DVD'},
            {'id': 6020, 'name': 'WMV'},
            {'id': 6030, 'name': 'XviD'},
            {'id': 6040, 'name': 'x264'},
          ]
        },
        { 'label' : 'Other' , 'value' : [
            {'id': 7000, 'name': 'All'},
            {'id': 7030, 'name': 'Comics'},
            {'id': 7020, 'name': 'Ebook'},
            {'id': 7010, 'name': 'Misc'} 
          ]
        },
    ]

cat_nzbmatrix = [
            { 'id': 0 , 'name': 'Select Category...' },
        { 'label' : 'Movies' , 'value' : [
            { 'id': 1,  'name': 'DVD' },
            { 'id': 2,  'name': 'Divx/Xvid' },
            { 'id': 54, 'name': 'BRRip' },
            { 'id': 42, 'name': 'HD (x264)' },
            { 'id': 50, 'name': 'HD (Image)' },
            { 'id': 48, 'name': 'WMV-HD' },
            { 'id': 3,  'name': 'SVCD/VCD' },
            { 'id': 4,  'name': 'Other' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 5,  'name': 'DVD' },
            { 'id': 6,  'name': 'Divx/Xvid' },
            { 'id': 41, 'name': 'HD' },
            { 'id': 7,  'name': 'Sport/Ent' },
            { 'id': 8,  'name': 'Other' },
          ]
        },
        { 'label' : 'Documentaries' , 'value' : [
            { 'id': 9,  'name': 'STD' },
            { 'id': 53, 'name': 'HD' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 10, 'name': 'PC' },
            { 'id': 11, 'name': 'PS2' },
            { 'id': 43, 'name': 'PS3' },
            { 'id': 12, 'name': 'PSP' },
            { 'id': 13, 'name': 'Xbox' },
            { 'id': 14, 'name': 'Xbox360' },
            { 'id': 56, 'name': 'Xbox360 (Other)' },
            { 'id': 15, 'name': 'PS1' },
            { 'id': 16, 'name': 'Dreamcast' },
            { 'id': 44, 'name': 'Wii' },
            { 'id': 51, 'name': 'Wii VC' },
            { 'id': 45, 'name': 'DS' },
            { 'id': 46, 'name': 'GameCube' },
            { 'id': 17, 'name': 'Other' },
          ]
        },
        { 'label' : 'Apps' , 'value' : [
            { 'id': 18, 'name': 'PC' },
            { 'id': 19, 'name': 'Mac' },
            { 'id': 52, 'name': 'Portable' },
            { 'id': 20, 'name': 'Linux' },
            { 'id': 55, 'name': 'Phone' },
            { 'id': 21, 'name': 'Other' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 22, 'name': 'MP3 Albums' },
            { 'id': 47, 'name': 'MP3 Singles' },
            { 'id': 23, 'name': 'Lossless' },
            { 'id': 24, 'name': 'DVD' },
            { 'id': 25, 'name': 'Video' },
            { 'id': 27, 'name': 'Other' },
          ]
        },
        { 'label' : 'Anime' , 'value' : [
            { 'id': 28, 'name': 'ALL' },
          ]
        },
        { 'label' : 'Other' , 'value' : [
            { 'id': 49, 'name': 'Audio Books' },
            { 'id': 33, 'name': 'Emulation' },
            { 'id': 34, 'name': 'PPC/PDA' },
            { 'id': 26, 'name': 'Radio' },
            { 'id': 36, 'name': 'E-Books' },
            { 'id': 37, 'name': 'Images' },
            { 'id': 38, 'name': 'Mobile Phone' },
            { 'id': 39, 'name': 'Extra Pars/Fills' },
            { 'id': 40, 'name': 'Other' },
          ]
        },
    ]

cat_piratebay = [
            {'id': '' , 'name': 'Select Category...' },
            {'id': 0, 'name': 'Everything'},
        { 'label' : 'Audio' , 'value' : [
            {'id': 100, 'name': 'All'},
            {'id': 101, 'name': 'Music'},
            {'id': 102, 'name': 'Audio books'},
            {'id': 103, 'name': 'Sound clips'},
            {'id': 104, 'name': 'FLAC'},
            {'id': 199, 'name': 'Other'},
          ]
        },
        { 'label' : 'Video' , 'value' : [
            {'id': 200, 'name': 'All'},
            {'id': 201, 'name': 'Movies'},
            {'id': 202, 'name': 'Movies DVDR'},
            {'id': 203, 'name': 'Music videos'},
            {'id': 204, 'name': 'Movie clips'},
            {'id': 205, 'name': 'TV Shows'},
            {'id': 206, 'name': 'Handheld'},
            {'id': 207, 'name': 'Highres - Movies'},
            {'id': 208, 'name': 'Highres - TV Shows'},
            {'id': 209, 'name': '3D'},
            {'id': 299, 'name': 'Other'},
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            {'id': 300, 'name': 'All'},
            {'id': 301, 'name': 'Windows'},
            {'id': 302, 'name': 'Mac'},
            {'id': 303, 'name': 'UNIX'},
            {'id': 304, 'name': 'Handheld'},
            {'id': 305, 'name': 'IOS (iPad/iPhone)'},
            {'id': 306, 'name': 'Android'},
            {'id': 399, 'name': 'Other OS'},
          ]
        },
        { 'label' : 'Games' , 'value' : [
            {'id': 400, 'name': 'All'},
            {'id': 401, 'name': 'PC'},
            {'id': 402, 'name': 'MAC'},
            {'id': 403, 'name': 'PSX'},
            {'id': 404, 'name': 'XBOX360'},
            {'id': 405, 'name': 'WII'},
            {'id': 406, 'name': 'Handheld'},
            {'id': 407, 'name': 'IOS (iPad/iPhone)'},
            {'id': 408, 'name': 'Android'},
            {'id': 499, 'name': 'Other'},
          ] 
        },
        { 'label' : 'Other' , 'value' : [
            {'id': 600, 'name': 'All'},
            {'id': 600, 'name': 'E-books'},
            {'id': 600, 'name': 'Comics'},
            {'id': 600, 'name': 'Pictures'},
            {'id': 600, 'name': 'Covers'},
            {'id': 600, 'name': 'Physibles'},
            {'id': 600, 'name': 'Other'},
          ]
        },
      ]
    
cat_rlslog = [
           { 'id': 0, 'name': 'Select Category...' },
        { 'label' : 'Movies', 'value' : [
            { 'id': 101, 'path': 'movies/bdrip',       'name': 'BDRip' },
            { 'id': 102, 'path': 'movies/cam',         'name': 'Cam' },
            { 'id': 103, 'path': 'movies/dvdrip',      'name': 'DVDRip' },
            { 'id': 104, 'path': 'movies/dvdrip-old',  'name': 'DVDRip Old' },
            { 'id': 105, 'path': 'movies/dvdscr',      'name': 'DVDSCR' },
            { 'id': 106, 'path': 'movies/hdrip',       'name': 'HDRip' },
            { 'id': 107, 'path': 'movies/r5',          'name': 'R5' },
            { 'id': 108, 'path': 'movies/scr',         'name': 'SCR' },
            { 'id': 109, 'path': 'movies/staff-picks', 'name': 'Staff Picks' },
            { 'id': 110, 'path': 'movies/telecine',    'name': 'Telecine' },
            { 'id': 111, 'path': 'movies/telesync',    'name': 'Telesync' },
            { 'id': 112, 'path': 'movies/workprint',   'name': 'Workprint' },
          ]
        },
        { 'label' : 'TV', 'value' : [
            { 'id': 201, 'path': 'tv-shows',           'name': 'TV Shows' },
            { 'id': 202, 'path': 'tv-shows/tv-packs',  'name': 'TV Packs' },
          ]
        },
        { 'label' : 'Music', 'value' : [
            { 'id': 301, 'path': 'music/albums',       'name': 'Albums' },
            { 'id': 302, 'path': 'music/itunes',       'name': 'iTunes' },
            { 'id': 304, 'path': 'music/mvid',         'name': 'MViD' },
            { 'id': 305, 'path': 'movies/singles',     'name': 'Singles/EPs' },
            { 'id': 306, 'path': 'movies/musicpicks',  'name': 'Staff Picks' },
          ]
        },
        { 'label' : 'Games', 'value' : [
            { 'id': 401, 'path': 'games/pc',           'name': 'PC' },
            { 'id': 402, 'path': 'games/ps3-games',    'name': 'PS3' },
            { 'id': 403, 'path': 'games/psp',          'name': 'PSP' },
            { 'id': 404, 'path': 'games/wii',          'name': 'Wii' },
            { 'id': 405, 'path': 'games/xbox360',      'name': 'XBOX360' },
          ]
        },
        { 'label' : 'Applications', 'value' : [
            { 'id': 501, 'path': 'applications/android',      'name': 'Android' },
            { 'id': 502, 'path': 'applications/ios',          'name': 'iOS' },
            { 'id': 503, 'path': 'applications/mac',          'name': 'MAC' },
            { 'id': 504, 'path': 'applications/windows',      'name': 'Windows' },
          ]
        },
    ]

cat_scnsrc = [
            { 'id': 0,                          'name': 'Select Category...' },
        { 'label' : 'Movies', 'value' : [
            { 'id': 101, 'path': 'films',              'name': 'All' },
            { 'id': 102, 'path': 'films/bdrip',        'name': 'BDRip' },
            { 'id': 103, 'path': 'films/bdscr',        'name': 'BDSCR' },
            { 'id': 104, 'path': 'films/bluray',       'name': 'BluRay' },
            { 'id': 105, 'path': 'films/cam',          'name': 'Cam' },
            { 'id': 106, 'path': 'films/dvdrip',       'name': 'DVDRip' },
            { 'id': 107, 'path': 'films/dvdscr',       'name': 'DVDSCR' },
            { 'id': 108, 'path': 'films/hd',           'name': 'HD' },
            { 'id': 109, 'path': 'films/r5',           'name': 'R5' },
            { 'id': 110, 'path': 'films/scr',          'name': 'SCR' },
            { 'id': 111, 'path': 'films/telecine',     'name': 'Telecine' },
            { 'id': 112, 'path': 'films/telesync',     'name': 'Telesync' },
            { 'id': 113, 'path': 'films/workprint',    'name': 'Workprint' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 201, 'path': 'tv',                 'name': 'All' },        
            { 'id': 202, 'path': 'tv/dvd',             'name': 'DVD' },
            { 'id': 203, 'path': 'tv/miniseries',      'name': 'Mini Series' },
            { 'id': 204, 'path': 'tv/ppv',             'name': 'PPV' },
            { 'id': 205, 'path': 'tv/preair',          'name': 'PREAiR' },
            { 'id': 206, 'path': 'tv/sports',          'name': 'Sports' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 301, 'path': 'new-music',                'name': 'All' },
            { 'id': 302, 'path': 'new-music/concert',        'name': 'Concert' },
            { 'id': 303, 'path': 'new-music-video-releases', 'name': 'MViD' },
            { 'id': 304, 'path': 'new-music/flac',           'name': 'FLAC' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 401, 'path': 'games',             'name': 'All' },
            { 'id': 402, 'path': 'games/clone',       'name': 'Clone' },
            { 'id': 403, 'path': 'games/iso',         'name': 'ISO' },
            { 'id': 404, 'path': 'games/ps3',         'name': 'PS3' },
            { 'id': 405, 'path': 'games/xbox360',     'name': 'XBOX360' },
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            { 'id': 501, 'path': 'applications/iphone',  'name': 'iPhone' },
            { 'id': 502, 'path': 'applications/macosx',  'name': 'MAC' },
            { 'id': 503, 'path': 'applications/windows', 'name': 'Windows' },
          ]
        },
    ]

cat_oneddl = [
            { 'id': 0,                           'name': 'Select Category...' },
        { 'label' : 'Movies', 'value' : [
            { 'id': 101, 'path': 'movies',                'name': 'All' },
            { 'id': 102, 'path': 'movies/1080p',          'name': '1080p' },
            { 'id': 103, 'path': 'movies/720p',           'name': '720p' },
            { 'id': 104, 'path': 'movies/bdrip',          'name': 'BDRip' },
            { 'id': 105, 'path': 'movies/bdscr-movies',   'name': 'BDScr' },
            { 'id': 106, 'path': 'movies/brrip',          'name': 'BRRip' },
            { 'id': 107, 'path': 'movies/cam',            'name': 'Cam' },
            { 'id': 108, 'path': 'movies/complete-bluray','name': 'Complete Bluray' },
            { 'id': 109, 'path': 'movies/dvdr',           'name': 'DVDR' },
            { 'id': 110, 'path': 'movies/dvdrip',         'name': 'DVDRip' },
            { 'id': 111, 'path': 'movies/dvdscr',         'name': 'DVDScr' },
            { 'id': 112, 'path': 'movies/hdrip',          'name': 'HDRip' },
            { 'id': 113, 'path': 'movies/r5',             'name': 'R5' },
            { 'id': 114, 'path': 'movies/rc',             'name': 'RC' },
            { 'id': 115, 'path': 'movies/scr',            'name': 'Scr' },
            { 'id': 116, 'path': 'movies/telecine',       'name': 'Telecine' },
            { 'id': 117, 'path': 'movies/telesync',       'name': 'TeleSync' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 201, 'path': 'tv-shows',              'name': 'All' },        
            { 'id': 202, 'path': 'tv-shows/hd-720p',      'name': 'HD 720p' },
            { 'id': 203, 'path': 'tv-shows/ppv',          'name': 'PPV' },
            { 'id': 204, 'path': 'tv-shows/sports',       'name': 'Sports' },
            { 'id': 205, 'path': 'tv-shows/tv-dvdrip',    'name': 'TV DVDRip' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 301, 'path': 'music',                'name': 'All' },
            { 'id': 302, 'path': 'music/flac',           'name': 'FLAC' },
            { 'id': 303, 'path': 'music/mp3',            'name': 'MP3' },
            { 'id': 304, 'path': 'music/mvid',           'name': 'MViD' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 401, 'path': 'games',             'name': 'All' },
            { 'id': 402, 'path': 'games/pc',          'name': 'PC' },
            { 'id': 403, 'path': 'games/ps3',         'name': 'PS3' },
            { 'id': 404, 'path': 'games/psp',         'name': 'PSP' },
            { 'id': 405, 'path': 'games/wii',         'name': 'Wii' },
            { 'id': 406, 'path': 'games/xbox360',     'name': 'XBOX360' },
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            { 'id': 501, 'path': 'apps',              'name': 'All' },
            { 'id': 502, 'path': 'apps/mac-apps',     'name': 'MAC' },
            { 'id': 503, 'path': 'apps/windows',      'name': 'Windows' },
          ]
        },
    ]

cat_irfree = [
            { 'id': 0, 'name': 'Select Category...' },
        { 'label' : 'Movies' , 'value' : [
            { 'id': 101, 'path': 'movies/',                 'name': 'All' },
            { 'id': 102, 'path': 'movies/anime/',           'name': 'Anime' },
            { 'id': 103, 'path': 'movies/bdripbbrip/',      'name': 'BDRip/BBRip' },
            { 'id': 104, 'path': 'movies/cam/',             'name': 'CAM' },
            { 'id': 105, 'path': 'movies/dvd-r/',           'name': 'DVD-R' },
            { 'id': 106, 'path': 'movies/dvdrip/',          'name': 'DVDRip' },
            { 'id': 107, 'path': 'movies/dvdscr/',          'name': 'DVDScr' },
            { 'id': 108, 'path': 'movies/moviesx264/',      'name': 'Movies x264' },
            { 'id': 109, 'path': 'movies/r5/',              'name': 'R5' },
            { 'id': 110, 'path': 'movies/telesyncts/',      'name': 'Telesyncts' },
          ]
        },
        { 'label' : 'TV Shows' , 'value' : [
            { 'id': 201, 'path': 'tv-shows/',                'name': 'All' },        
            { 'id': 202, 'path': 'tv-shows/tv-showx264/',    'name': 'TV Shows x264' },
            { 'id': 203, 'path': 'tv-shows/tv-showsboxsets/','name': 'TV Show Boxsets' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 301, 'path': 'music/',                  'name': 'Music' },
            { 'id': 302, 'path': 'music/mvid/',             'name': 'Music Videos' },
          ]
        },
        { 'label' : 'Applications', 'value' : [
            { 'id': 401, 'path': 'applications/',           'name': 'All' },
            { 'id': 402, 'path': 'applications/android/',   'name': 'Android' },
            { 'id': 403, 'path': 'applications/iphone/',    'name': 'IPhone' },
            { 'id': 404, 'path': 'applications/mac/',       'name': 'MAC' },
            { 'id': 405, 'path': 'applications/windows/',   'name': 'Windows' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 501, 'path': 'games/',                  'name': 'All' },
            { 'id': 502, 'path': 'games/ps3/',              'name': 'PS3' },
            { 'id': 503, 'path': 'games/psp/',              'name': 'PSP' },
            { 'id': 504, 'path': 'games/wii/',              'name': 'Wii' },
            { 'id': 505, 'path': 'games/xbox360/',          'name': 'Xbox360' },
          ]
        },
        { 'label' : 'EBooks' , 'value' : [
            { 'id': 601, 'path': 'ebooks/',                 'name': 'All' },
            { 'id': 602, 'path': 'ebooks/magazines/',       'name': 'Magazines' },
          ]
        },
    ]

cat_sceper = [
            { 'id': 0,                           'name': 'Select Category...' },
        { 'label' : 'Movies', 'value' : [
            { 'id': 101, 'path': 'movies',                      'name': 'All' },
            { 'id': 102, 'path': 'movies/cartoons',             'name': 'Cartoons' },
            { 'id': 103, 'path': 'movies/movie-packs',          'name': 'Movie-Packs' },
            { 'id': 104, 'path': 'movies/movies-3d',            'name': 'Movies-3D' },
            { 'id': 105, 'path': 'movies/movies-bluray-rip',    'name': 'BluRay Rip' },
            { 'id': 106, 'path': 'movies/movies-cam',           'name': 'Cam' },
            { 'id': 107, 'path': 'movies/movies-ddc',           'name': 'DDC' },
            { 'id': 108, 'path': 'movies/movies-dvdrip',        'name': 'DVDRip' },
            { 'id': 109, 'path': 'movies/movies-dvdr',          'name': 'DVDR' },
            { 'id': 110, 'path': 'movies/movies-foreign/',      'name': 'Foreign' },
            { 'id': 111, 'path': 'movies/movies-full-bd',       'name': 'Full BD' },
            { 'id': 112, 'path': 'movies/movies-hddvd-rip',     'name': 'HDDVD Rip' },
            { 'id': 113, 'path': 'movies/movies-hdtv',          'name': 'HDTV Movies' },
            { 'id': 114, 'path': 'movies/movies-hdtv-720p',     'name': 'HDTV 720p Movies' },
            { 'id': 115, 'path': 'movies/movies-ppv-rip',       'name': 'HDTV PPV Movies' },
            { 'id': 116, 'path': 'movies/movies-r3',            'name': 'R3' },
            { 'id': 117, 'path': 'movies/movies-r5',            'name': 'R5' },
            { 'id': 118, 'path': 'movies/movies-screener',      'name': 'Screener' },
            { 'id': 119, 'path': 'movies/movies-telecine',      'name': 'Telecine' },
            { 'id': 120, 'path': 'movies/movies-telesync',      'name': 'Telesync' },
            { 'id': 121, 'path': 'movies/movies-workprint',     'name': 'Workprint' },
            { 'id': 122, 'path': 'movies/movies-mini',          'name': 'Movies Mini(<551MB)' },
          ]
        },
        { 'label' : 'TV' , 'value' : [
            { 'id': 201, 'path': 'tv-shows',                    'name': 'All' },        
            { 'id': 202, 'path': 'tv-shows/animes',             'name': 'Animes/Cartoons' },
            { 'id': 203, 'path': 'tv-shows/documentaries',      'name': 'Documentaries' },
            { 'id': 204, 'path': 'tv-shows/mini-series',        'name': 'Mini Series' },
            { 'id': 205, 'path': 'tv-shows/tv-packs',           'name': 'TV Packs' },
            { 'id': 205, 'path': 'tv-shows/tv-shows-x264',      'name': 'TV Shows x264' },
          ]
        },
        { 'label' : 'Music' , 'value' : [
            { 'id': 301, 'path': 'music',                   'name': 'All' },
            { 'id': 302, 'path': 'music/itunes-singles',    'name': 'FLAC' },
            { 'id': 303, 'path': 'music/music-mdvdr',       'name': 'Music DVDR' },
            { 'id': 304, 'path': 'music/music-video',       'name': 'Music Video' },
          ]
        },
        { 'label' : 'Games' , 'value' : [
            { 'id': 401, 'path': 'games',                   'name': 'All' },
            { 'id': 402, 'path': 'games/console-games',     'name': 'Console' },
            { 'id': 403, 'path': 'games/games-pack',        'name': 'Games Packs' },
            { 'id': 404, 'path': 'games/mini-games',        'name': 'Mini Games' },
            { 'id': 405, 'path': 'games/mobile-phone-games','name': 'Mobile Phone Games' },
            { 'id': 406, 'path': 'games/pc-games',          'name': 'PC Games' },
          ]
        },
        { 'label' : 'Applications' , 'value' : [
            { 'id': 501, 'path': '/applications',             'name': 'All' },
            { 'id': 502, 'path': '/applications/pda',         'name': 'PDA' },
          ]
        },
    ]

cat_vcdq = [
            { 'id': 0,                                              'name': 'Select Category...' },
        { 'label' : 'VCDq', 'value' : [
            { 'id': 101, 'path': '0/0/0/0/0/0/0',                   'name': 'Everthing' },
          ]
        },
        { 'label' : 'Movies', 'value' : [
            { 'id': 201, 'path': '1/0/0/0/0/0/0',                   'name': 'All' },
            { 'id': 202, 'path': '1/2_1/0/3_2/0/0/0',               'name': 'HD' },
            { 'id': 203, 'path': '1/2_1/0/4_9_10_11_12_21_22/0/0/0','name': 'SD' },
          ]
        },
        { 'label' : 'TV Shows', 'value' : [
            { 'id': 301, 'path': '3/0/0/0/0/0/0',                   'name': 'All' },
            { 'id': 302, 'path': '3/2_1/0/3_2/0/0/0',               'name': 'HD' },
            { 'id': 303, 'path': '3/2_1/0/4_9_10_11_12_21_22/0/0/0','name': 'SD' },
          ]
        },
        { 'label' : 'Games', 'value' : [
            { 'id': 401, 'path': '2/0/0/0/0/0/0/0/0/0/1',           'name': 'PC' },
            { 'id': 402, 'path': '6/0/0/0/0/0/0',                   'name': 'PS3' },
            { 'id': 403, 'path': '5/0/0/0/0/0/0',                   'name': 'XBox360' },
            { 'id': 404, 'path': '4/0/0/0/0/0/0',                   'name': 'Wii' },
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
    elif site == 'irfree':
        categories = cat_irfree
    else:
       categories = None

    return render_template('rssfeeds.html',
        site = site,
        categories = categories,
    )

@app.route('/xhr/rssfeeds/<site>/<category>')
@requires_auth
def xhr_rssfeeds_category(site = None, category = None):

# NZBMatrix Start #

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

            r = re.compile('IMDB Link:</b> <a href="(.*?)/">Go To IMDB</a>')
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

# RlsLog Start

    elif site == "rlslog":
        categories = cat_rlslog

        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']

        feed = 'http://www.rlslog.net/category/' + path + '/feed/'
        feed = feedparser.parse(feed)

        for entry in feed['entries']:
            r = re.compile('src="(.*?)"')
            result = r.search(entry['content'][0]['value'])
            if result:
                img = result.group(1)
            else:
                img = ""

            r = re.compile('<strong>Genre:</strong> (.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                genre = result.group(1)
            else:
                genre = ""

            r = re.compile('<a href="(.*?)">Homepage</a>')
            result = r.search(entry['content'][0]['value'])
            if result:
                homepage = result.group(1)
            else:
                homepage = ""

            r = re.compile('<strong>Size:</strong> (.*?)<br />')
            s = re.compile('<strong>Size</strong>: (.*?)<br />')
            t = re.compile('<strong>Size: </strong>(.*?)<br />')
            u = re.compile('<strong>Size:</strong>(.*?)</p>')
            v = re.compile('|(.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            if not result:
                result = s.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            if not result:
                result = t.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            if not result:
                result = u.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            if not result:
                result = v.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            else:
                size = ""

            r = re.compile('<strong>IMDB Rating</strong>:(.*?)<br />')
            s = re.compile('<strong>IMDB Rating:</strong>(.*?)<br />')
            t = re.compile('<strong>IMDB rating:</strong>(.*?)<br />')
            u = re.compile('<strong>IMDB rating</strong>:(.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdbrating = result.group(1)
            if not result:
                result = s.search(entry['content'][0]['value'])
            if result:
                imdbrating = result.group(1)
            if not result:
                result = t.search(entry['content'][0]['value'])
            if result:
                imdbrating = result.group(1)
            if not result:
                result = u.search(entry['content'][0]['value'])
            if result:
                imdbrating = result.group(1)
                if "-/10" in imdbrating:
                    imdbrating = "No Rating"
            else:
                imdbrating = ""

            r = re.compile('<a href="(.*?)">iMDB')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdblink = result.group(1)
                x = imdblink.find('http://www.imdb.com')
                imdblink = imdblink[x:]
            else:
                imdblink = ""

            r = re.compile('http://nfo.rlslog.net/view/(.*?)">')
            result = r.search(entry['content'][0]['value'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            description = { 'size': size, 'imdbrating': imdbrating, 'imdblink': imdblink, 'nfolink': nfolink, 'img': img, 'genre':genre, 'homepage':homepage, }
            entry['description'] = description
            entry.description['genre'] = entry.description['genre'].replace("&amp;", "&")

# The Pirate Bay
    elif site == "piratebay":
        categories = cat_piratebay
        feed = 'http://rss.thepiratebay.se/' + category
        feed = feedparser.parse(feed)

# SCNSRC
    elif site == "scnsrc":
        categories = cat_scnsrc

        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']

        feed = 'http://www.scnsrc.me/category/' + path + '/feed/'
        feed = feedparser.parse(feed)

        for entry in feed['entries']:
            r = re.compile('src="(.*?.(?:jpg|png))"')
            result = r.search(entry['content'][0]['value'])
            if result:
                img = result.group(1)
            else:
                img = ""

            r = re.compile('<strong>Genre:</strong>(.*?)<br />')
            s = re.compile('<b>Genre:</b>(.*?)<')
            result = r.search(entry['content'][0]['value'])
            if result:
                genre = result.group(1)
            if not result:
                result = s.search(entry['content'][0]['value'])
            if result:
                genre = result.group(1)
            else:
                genre = ""

            r = re.compile('&#124;.*?&#124;(.*?)&#124;')
            result = r.search(entry['description'])
            if result:
                size = result.group(1)
            else:
                size = ""

            r = re.compile('IMDB:(.*?)&#124;')
            s = re.compile('IMDB:(.*?)<')
            result = r.search(entry['description'])
            if result:
                imdbrating = result.group(1)
            if not result:
                result = s.search(entry['description'])
            if result:
                imdbrating = result.group(1)
            else:
                imdbrating = ""

            r = re.compile('imdb.com/title/(.*?)/')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdblink = result.group(1)
            else:
                imdblink = ""

            r = re.compile('http://nfomation.net/info/(.*?)"')
            result = r.search(entry['content'][0]['value'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            description = { 'size': size, 'imdbrating': imdbrating, 'imdblink': imdblink, 'nfolink': nfolink, 'img': img, 'genre':genre, }
            entry['description'] = description
            entry.description['genre'] = entry.description['genre'].replace("&amp;", "&")

# OneDDL
    elif site == "oneddl":
        categories = cat_oneddl
        
        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']
                    
        feed = 'http://www.oneddl.eu/category/' + path + '/feed/'
        feed = feedparser.parse(feed)

        for entry in feed['entries']:
            r = re.compile('images.oneddl.eu/images/(.*?)"')
            result = r.search(entry['content'][0]['value'])
            if result:
                img = result.group(1)
            else:
                img = ""

            r = re.compile('imdb.com/title/(.*?)/')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdblink = result.group(1)
            else:
                imdblink = ""

            r = re.compile('http://nfomation.net/info/(.*?)"')
            result = r.search(entry['content'][0]['value'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            description = { 'img': img, 'nfolink': nfolink, 'imdblink' : imdblink, }
            entry['description'] = description

# Sceper
    elif site == "sceper":
        categories = cat_sceper
        
        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']
                    
        feed = 'http://sceper.eu/category/' + path + '/feed/'
        feed = feedparser.parse(feed)

        for entry in feed['entries']:
            r = re.compile('http://img.sceper.eu/images/(.*?)"')
            result = r.search(entry['content'][0]['value'])
            if result:
                img = result.group(1)
            else:
                img = ""

            r = re.compile('Size:</span>(.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                size = result.group(1)
            else:
                size = ""

            r = re.compile('Genre:</span>(.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                genre = result.group(1)
            else:
                genre = ""

            r = re.compile('imdb.com/title/(.*?)/')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdblink = result.group(1)
            else:
                imdblink = ""

            r = re.compile('http://nfo.sceper.eu/nfo/(.*?)"')
            result = r.search(entry['content'][0]['value'])
            if result:
                nfolink = result.group(1)
            else:
                nfolink = ""

            r = re.compile('IMDB Rating:</span>(.*?)<br />')
            result = r.search(entry['content'][0]['value'])
            if result:
                imdbrating = result.group(1)
            else:
                imdbrating = ""

            description = { 'img': img, 'nfolink': nfolink, 'imdblink': imdblink, 'size':size, 'genre': genre, 'imdbrating': imdbrating, }
            entry['description'] = description

#VCDq
    elif site == "vcdq":
        categories = cat_vcdq
        
        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']
                    
        feed = 'http://www.vcdq.com/browse/rss/' + path
        feed = feedparser.parse(feed)

# NewzNab
    elif site == "newznab":
        categories = cat_newznab
        feed = 'http://nzb.su/rss?t=' + category
        feed = feedparser.parse(feed)

# IRFree
    elif site == "irfree":
        categories = cat_irfree
        
        for cat in categories[1:]:
            for subcat in cat['value']:
                if int(category) == subcat['id']:
                    path = subcat['path']
                    
        feed = 'http://www.irfree.com/' + path + 'rss.xml'
        feed = feedparser.parse(feed)

        for entry in feed['entries']:
            r = re.compile('src="(.*?)"')
            result = r.search(entry['summary'])
            if result:
                img = result.group(1)
            else:
                img = ""

            r = re.compile('<strong>Genre:</strong>(.*?)(<br />|</p>)')
            s = re.compile('\[GENRE\]:(.*?)<br />')
            t = re.compile('Genre -(.*?)<br />')
            u = re.compile('Genre(s): <em>(.*?)</em>') 
            v = re.compile('Genre:(.*?)</em>')
            result = r.search(entry['summary'])
            if result:
                genre = result.group(1)
            if not result:
                result = s.search(entry['summary'])
            if not result:
                result = t.search(entry['summary'])
            if not result:
                result = u.search(entry['summary'])
            if not result:
                result = v.search(entry['summary'])
            if result:
                genre = result.group(1)
            else:
                genre = ""

            r = re.compile('Size</strong>:(.*?)<br />')
            s = re.compile('Size:</strong>(.*?)<br />')
            t = re.compile('SIZE\]:(.*?)<br />')
            u = re.compile('Size.*- (.*?)<br />')
            v = re.compile('Size :</strong>(.*?)<br />')
            result = r.search(entry['summary'])
            if result:
                size = result.group(1)
            if not result:
                result = s.search(entry['summary'])
            if not result:
                result = t.search(entry['summary'])
            if not result:
                result = u.search(entry['summary'])
            if not result:
                result = v.search(entry['summary'])
            if result:
                size = result.group(1)
            else:
                size = ""

            r = re.compile('IMDB:</strong>(.*?)<br />')
            s = re.compile('Rating:</strong>(.*?)<br />')
            t = re.compile('Rating</strong>:(.*?)<br />')
            u = re.compile('Rating:(.*?)<')
            result = r.search(entry['summary'])
            if result:
                imdbrating = result.group(1)
            if not result:
                result = s.search(entry['summary'])
            if not result:
                result = t.search(entry['summary'])
            if not result:
                result = u.search(entry['summary'])
            if result:
                imdbrating = result.group(1)
            else:
                imdbrating = "Click Here"

            r = re.compile('imdb.com/title/(.*?)"')
            result = r.search(entry['summary'])
            if result:
                imdblink = result.group(1)
            else:
                imdblink = ""

            description = { 'img': img, 'genre': genre, 'size': size, 'imdbrating': imdbrating, 'imdblink': imdblink, }
            entry['description'] = description
            entry.description['genre'] = entry.description['genre'].replace("&amp;", "&")
            entry.description['genre'] = entry.description['genre'].replace("&nbsp;", "")
            entry.description['genre'] = entry.description['genre'].replace(" | ", ", ")
            entry.description['size'] = entry.description['size'].replace("&nbsp;", "")
            entry.description['imdbrating'] = entry.description['imdbrating'].replace("&nbsp;", "")
            
    else:
        feed = None
    if feed:
        for entry in feed['entries']:
            entry['title'] = entry['title'].replace(".", " ")

    return render_template('rssfeeds.html',
        site = site,
        category = int(category),
        categories = categories,
        feed = feed,
    )

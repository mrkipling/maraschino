from flask import render_template, jsonify

from Maraschino import app
from maraschino.tools import *
from maraschino import logger
from sites.nzbmatrix import *
from sites.nzbsu import *
import urllib

# Newznab Category List:
cat_newznab = [
        {'id': '', 'name': 'Everything'},
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

# NZBMatrix Category List:
cat_nzbmatrix = [
        {'id': 0, 'name': 'Everything'},
        {'label': 'Movies', 'value':[
            {'id': 1, 'name': 'Movies: DVD'},
            {'id': 2, 'name': 'Movies: Divx/Xvid'},
            {'id': 54, 'name': 'Movies: BRRip'},
            {'id': 42, 'name': 'Movies: HD (x264)'},
            {'id': 50, 'name': 'Movies: HD (Image)'},
            {'id': 48, 'name': 'Movies: WMV-HD'},
            {'id': 3, 'name': 'Movies: SVCD/VCD'},
            {'id': 4, 'name': 'Movies: Other'},
          ]
        },
        {'label': 'TV', 'value': [
            {'id': 5, 'name': 'TV: DVD'},
            {'id': 6, 'name': 'TV: Divx/Xvid'},
            {'id': 41, 'name': 'TV: HD'},
            {'id': 7, 'name': 'TV: Sport/Ent'},
            {'id': 8, 'name': 'TV: Other'},
          ]
        },
        {'label': 'Documentaries', 'value': [
            {'id': 9, 'name': 'Documentaries: STD'},
            {'id': 53, 'name': 'Documentaries: HD'},
          ]
        },
        {'label': 'Games', 'value': [
            {'id': 10, 'name': 'Games: PC'},
            {'id': 11, 'name': 'Games: PS2'},
            {'id': 43, 'name': 'Games: PS3'},
            {'id': 12, 'name': 'Games: PSP'},
            {'id': 13, 'name': 'Games: Xbox'},
            {'id': 14, 'name': 'Games: Xbox360'},
            {'id': 56, 'name': 'Games: Xbox360 (Other)'},
            {'id': 15, 'name': 'Games: PS1'},
            {'id': 16, 'name': 'Games: Dreamcast'},
            {'id': 44, 'name': 'Games: Wii'},
            {'id': 51, 'name': 'Games: Wii VC'},
            {'id': 45, 'name': 'Games: DS'},
            {'id': 46, 'name': 'Games: GameCube'},
            {'id': 17, 'name': 'Games: Other'},
          ]
        },
        {'label': 'Apps', 'value': [
            {'id': 18, 'name': 'Apps: PC'},
            {'id': 19, 'name': 'Apps: Mac'},
            {'id': 52, 'name': 'Apps: Portable'},
            {'id': 20, 'name': 'Apps: Linux'},
            {'id': 55, 'name': 'Apps: Phone'},
            {'id': 21, 'name': 'Apps: Other'},
          ]
        },
        {'label': 'Music', 'value': [
            {'id': 22, 'name': 'Music: MP3 Albums'},
            {'id': 47, 'name': 'Music: MP3 Singles'},
            {'id': 23, 'name': 'Music: Lossless'},
            {'id': 24, 'name': 'Music: DVD'},
            {'id': 25, 'name': 'Music: Video'},
            {'id': 27, 'name': 'Music: Other'},
          ]
        },
        {'label': 'Anime', 'value': [
            {'id': 28, 'name': 'Anime: ALL'},
          ]
        },
        {'label': 'Other', 'value': [
            {'id': 49, 'name': 'Other: Audio Books'},
            {'id': 33, 'name': 'Other: Emulation'},
            {'id': 34, 'name': 'Other: PPC/PDA'},
            {'id': 26, 'name': 'Other: Radio'},
            {'id': 36, 'name': 'Other: E-Books'},
            {'id': 37, 'name': 'Other: Images'},
            {'id': 38, 'name': 'Other: Mobile Phone'},
            {'id': 39, 'name': 'Other: Extra Pars/Fills'},
            {'id': 40, 'name': 'Other: Other'},
          ]
        },
    ]


@app.route('/xhr/search/')
@app.route('/xhr/search/<site>')
def xhr_search(site=None):
    if get_setting_value('search') == '0':
        logger.log('SEARCH :: Search fature not enabled, please enable it on the top right corner menu', 'INFO')
        return ''

    if site == 'nzbmatrix':
        categories = cat_nzbmatrix
    elif site == 'nzb.su':
        categories = cat_newznab
    else:
        # defaulting to nzbmatrix for now
        site = 'nzbmatrix'
        categories = cat_nzbmatrix

    return render_template('search.html',
        site=site,
        categories=categories,
    )


@app.route('/search/nzbmatrix/<item>/')
@app.route('/search/nzbmatrix/<item>/<cat>/')
def nzb_matrix(item, cat=None, mobile=False):
    API = get_setting_value('nzb_matrix_API')
    USERNAME = get_setting_value('nzb_matrix_user')

    if not API or not USERNAME:
        logger.log('SEARCH :: NZBMatrix API or USERNAME missing', 'DEBUG')
        return jsonify({'error': "Missing NZBMatrix details"})

    nzb = Matrix(username=USERNAME, apiKey=API)

    if item is not '':
        if cat:
            logger.log('SEARCH :: NZBMatrix :: Searching for "%s" in category: %s' % (item, cat), 'INFO')
            result = nzb.Search(query=item, catId=cat)
        else:
            logger.log('SEARCH :: NZBMatrix :: Searching for "%s" in all categories' % (item), 'INFO')
            result = nzb.Search(item)

    if result.get('error'):
        result = None

    if mobile:
        return result

    return render_template('search-nzbmatrix.html',
        site='nzbmatrix',
        results=result,
        item=item,
        categories=cat_nzbmatrix,
    )


@app.route('/search/nzb.su/<item>/')
@app.route('/search/nzb.su/<item>/<cat>/')
def nzb_su(item, cat=None, mobile=False):
    API = get_setting_value('nzb_su_API')

    if not API:
        logger.log('SEARCH :: NZB.su API missing', 'DEBUG')
        return jsonify({'error': "Missing NZB.su API"})

    nzb = nzbsu(apiKey=API)

    if item is not '':
        if cat:
            logger.log('SEARCH :: NZB.su :: Searching for "%s" in category: %s' % (item, cat), 'INFO')
            result = nzb.Search(query=item, catId=cat)
        else:
            logger.log('SEARCH :: NZB.su :: Searching for "%s" in all categories' % (item), 'INFO')
            result = nzb.Search(item)

        for x in result['channel']['item']:
            x['link'] = urllib.quote(x['link'])

        logger.log('SEARCH :: NZB.su :: Found %i results for %s' % (len(result['channel']['item']), item), 'INFO')

    else:
        result = ''

    if mobile:
        return result

    return render_template('search-nzbsu.html',
        site='nzb.su',
        results=result['channel']['item'],
        item=item,
        categories=cat_newznab,
    )

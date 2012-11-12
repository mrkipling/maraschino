from flask import render_template, jsonify, json, request

from maraschino.tools import requires_auth, get_setting_value, convert_bytes
from maraschino import app, logger
from feedparser import feedparser
from maraschino.models import NewznabSite
from maraschino.database import db_session
import urllib, re

# NZBMatrix Category List:
cat_nzbmatrix = [
        {'id': 0, 'name': 'Everything'},
        {'label': 'Movies', 'id': 'movies', 'value':[
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
        {'label': 'TV', 'id': 'tv', 'value': [
            {'id': 5, 'name': 'TV: DVD'},
            {'id': 6, 'name': 'TV: Divx/Xvid'},
            {'id': 41, 'name': 'TV: HD'},
            {'id': 7, 'name': 'TV: Sport/Ent'},
            {'id': 8, 'name': 'TV: Other'},
          ]
        },
        {'label': 'Documentaries', 'id': 'doco', 'value': [
            {'id': 9, 'name': 'Documentaries: STD'},
            {'id': 53, 'name': 'Documentaries: HD'},
          ]
        },
        {'label': 'Games', 'id': 'games', 'value': [
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
        {'label': 'Apps', 'id': 'apps', 'value': [
            {'id': 18, 'name': 'Apps: PC'},
            {'id': 19, 'name': 'Apps: Mac'},
            {'id': 52, 'name': 'Apps: Portable'},
            {'id': 20, 'name': 'Apps: Linux'},
            {'id': 55, 'name': 'Apps: Phone'},
            {'id': 21, 'name': 'Apps: Other'},
          ]
        },
        {'label': 'Music', 'id': 'music', 'value': [
            {'id': 22, 'name': 'Music: MP3 Albums'},
            {'id': 47, 'name': 'Music: MP3 Singles'},
            {'id': 23, 'name': 'Music: Lossless'},
            {'id': 24, 'name': 'Music: DVD'},
            {'id': 25, 'name': 'Music: Video'},
            {'id': 27, 'name': 'Music: Other'},
          ]
        },
        {'label': 'Anime', 'id': 'anime', 'value': [
            {'id': 28, 'name': 'Anime: ALL'},
          ]
        },
        {'label': 'Other', 'id': 'other', 'value': [
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


# Newznab Category List:
def cat_newznab(url):
    categories = [{'id': '0', 'name': 'Everything'}]
    try:
        result = json.loads(urllib.urlopen(url + '/api?t=caps&o=json').read())
    except:
        return []

    for cat in result['categories']['category']:
        category = {'label': cat['@attributes']['name'], 'id': cat['@attributes']['id']}
        category['value'] = [x['@attributes'] for x in cat['subcat']]

        for subcat in category['value']:
            subcat['name'] = '%s: %s' % (category['label'], subcat['name'])
        categories.append(category)

    return categories


def get_newznab_sites():
    try:
        newznab_sites = NewznabSite.query.order_by(NewznabSite.id)
    except Exception as e:
        newznab_sites = []
        logger.log('SEARCH :: Failed to get newznab sites')
        logger.log(e, 'DEBUG')

    return newznab_sites


@app.route('/xhr/search/')
@app.route('/xhr/search/<site>')
@requires_auth
def xhr_search(site='nzbmatrix'):
    if get_setting_value('search') == '0':
        logger.log('SEARCH :: Search fature not enabled, please enable it on the top right corner menu', 'INFO')
        return ''

    if site == 'nzbmatrix':
        categories = cat_nzbmatrix
    else:
        site = int(site)
        newznab = NewznabSite.query.filter(NewznabSite.id == site).first()
        categories = cat_newznab(newznab.url)

    return render_template('search.html',
        site=site,
        newznab_sites=get_newznab_sites(),
        categories=categories,
        category=0,
        maxage=0
    )


@app.route('/search/<site>/<category>/<maxage>/')
@app.route('/search/<site>/<category>/<maxage>/<term>/')
@requires_auth
def get_search_results(site, category='0', maxage='0', term=''):
    if site == 'nzbmatrix':
        return nzb_matrix(category=category, maxage=maxage, term=term)
    else:
        return newznab(site=site, category=category, maxage=maxage, term=term)


def nzb_matrix(category, maxage, term, mobile=False):
    catid = category
    apikey = get_setting_value('nzb_matrix_API')
    username = get_setting_value('nzb_matrix_user')

    english = get_setting_value('search_english')
    ssl = get_setting_value('search_ssl')
    retention = get_setting_value('search_retention')

    if not category.isdigit(): #Category group
        for i in range(len(cat_nzbmatrix)):
            if 'label' in cat_nzbmatrix[i] and cat_nzbmatrix[i]['id'] == category:
                cats = [str(x['id']) for x in cat_nzbmatrix[i]['value']]
                category = ','.join(cats)
                break

    url = 'http://rss.nzbmatrix.com/rss.php?scenename=1&searchin=name&subcat=%s&term=%s&maxage=%s' % (category, term, maxage)

    if username and apikey:
        url += '&page=download&username=%s&apikey=%s' % (username, apikey)
    else:
        logger.log('SEARCH :: NZBMatrix apikey or username missing', 'WARNING')

    if english:
        url += '&english=%s' % english
    if ssl:
        url += '&ssl=%s' % ssl
    if retention:
        if retention.isdigit():
            url += '&age=%s' % retention
        else:
            logger.log('SEARCH :: Retention must be a number.', 'ERROR')

    logger.log('SEARCH :: NZBMatrix :: Searching for "%s" in category: %s' % (term, category), 'INFO')

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        logger.log('SEARCH :: NZBMatrix :: Failed  to parse feed', 'ERROR')
        logger.log(e, 'DEBUG')
        return jsonify(error='Failed to parse feed')

    result = feed['entries']
    results = []
    for item in result:
        print item
        a = {
            'nzblink': item['link'],
            'title': item['title'].decode('utf-8'),
            'category': item['category'],
        }

        try:
            a['size'] = re.compile('<b>Size:</b> (.*?)<').search(item['summary']).group(1)
        except:
            a['size'] = 'Unknown'

        try:
            a['details'] = re.compile('View NZB:</b> <a href="(.*?)"').search(item['summary']).group(1)
        except:
            a['details'] = item['link']

        results.append(a)

    if mobile:
        return results

    return render_template('search-results.html',
        site='nzbmatrix',
        results=results,
        term=term,
        categories=cat_nzbmatrix,
        category=catid,
        maxage=int(maxage),
        newznab_sites=get_newznab_sites()
    )


def newznab(site, category, maxage, term, mobile=False):
    site = int(site)
    newznab = NewznabSite.query.filter(NewznabSite.id == site).first()

    url = newznab.url
    apikey = newznab.apikey
    categories = cat_newznab(url)

    try:
        url += '/api?t=search&o=json&apikey=%s&maxage=%s' % (apikey, maxage)
        if category != '0':
            url += '&cat=%s' % category
        if term:
            url += '&q=%s' % urllib.quote(term)

        logger.log('SEARCH :: %s :: Searching for "%s" in category: %s' % (site, term, category), 'INFO')
        result = json.loads(urllib.urlopen(url).read())['channel']

        if 'item' in result:
            result = result['item']
        else:
            result = []
            logger.log('SEARCH :: No results found', 'INFO')

    except Exception as e:
        logger.log(e, 'DEBUG')
        result = []

    def parse_item(item):
        if isinstance(item, dict):
            for attr in item['attr']:
                if attr['@attributes']['name'] == 'size':
                    size = convert_bytes(attr['@attributes']['value'])

            a = {
                'nzblink': item['link'],
                'details': item['guid'],
                'title': item['title'].decode('utf-8'),
                'category': item['category'],
                'size': size
            }

        return a

    if isinstance(result, dict):
        results = [parse_item(result)]
    else:
        results = [parse_item(x) for x in result]

    if mobile:
        return results

    return render_template('search-results.html',
        site=site,
        results=results,
        term=term,
        categories=categories,
        category=category,
        maxage=int(maxage),
        newznab_sites=get_newznab_sites()
    )

@app.route('/search/newznab_dialog/')
@app.route('/search/newznab_dialog/<newznab_id>')
@requires_auth
def newznab_dialog(newznab_id=None, newznab=None):
    if newznab_id:
        try:
            newznab = NewznabSite.query.filter(NewznabSite.id == newznab_id).first()
        except Exception as e:
            logger.log('SEARCH :: Could not find Newznab site id: %s' % newznab_id, 'ERROR')
            logger.log(e, 'DEBUG')

    return render_template('add_edit_newznab_dialog.html',
        newznab=newznab,
    )


@app.route('/search/add_edit_newznab/', methods=['POST'])
@requires_auth
def add_edit_newznab():
    name = request.form['name']
    url = request.form['url']
    apikey = request.form['apikey']

    if url.endswith('/'):
        url = url[:-1]

    if not name:
        return jsonify(error=True)
    if not apikey:
        return jsonify(error=True)
    if not url:
        return jsonify(error=True)

    if 'newznab_id' in request.form:
        logger.log('SEARCH :: Editing Newznab site %s' % request.form['newznab_id'], 'INFO')
        newznab = NewznabSite.query.filter(NewznabSite.id == request.form['newznab_id']).first()
        newznab.name = name
        newznab.url = url
        newznab.apikey = apikey


    else:
        logger.log('SEARCH :: Adding new Newznab site', 'INFO')
        newznab = NewznabSite(
            name=name,
            url=url,
            apikey=apikey
        )

    try:
        db_session.add(newznab)
        db_session.commit()

    except Exception as e:
        logger.log(e, 'DEBUG')
        return jsonify(error=True)

    return xhr_search()


@app.route('/search/delete_newznab/<newznab_id>/')
@requires_auth
def delete_newznab(newznab_id):
    try:
        newznab = NewznabSite.query.filter(NewznabSite.id == newznab_id).first()
        db_session.delete(newznab)
        db_session.commit()

    except:
        return jsonify(error=True)

    return xhr_search()



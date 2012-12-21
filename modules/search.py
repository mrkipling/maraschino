from flask import render_template, jsonify, request

from maraschino.tools import requires_auth, get_setting_value, convert_bytes
from maraschino import app, logger
from feedparser import feedparser
from maraschino.models import NewznabSite
from maraschino.database import db_session
from xmltodict import xmltodict
import urllib
import re


# Newznab Category List:
def cat_newznab(url):
    categories = [{'id': '0', 'name': 'Everything'}]
    try:
        result = xmltodict.parse(urllib.urlopen(url + '/api?t=caps&o=xml').read())
    except:
        return []

    for cat in result['caps']['categories']['category']:
        category = {'label': cat['@name'], 'id': cat['@id']}
        category['value'] = [{'name': x['@name'], 'id': x['@id']} for x in cat['subcat']]

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
def xhr_search(site=1):
    if get_setting_value('search') == '0':
        logger.log('SEARCH :: Search fature not enabled, please enable it on the top right corner menu', 'INFO')
        return ''

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
        return newznab(site=site, category=category, maxage=maxage, term=term)


def newznab(site, category, maxage, term, mobile=False):
    site = int(site)
    newznab = NewznabSite.query.filter(NewznabSite.id == site).first()

    url = newznab.url
    apikey = newznab.apikey
    categories = cat_newznab(url)

    try:
        url += '/api?t=search&o=xml&apikey=%s&maxage=%s' % (apikey, maxage)
        if category != '0':
            url += '&cat=%s' % category
        if term:
            url += '&q=%s' % urllib.quote(term)

        logger.log('SEARCH :: %s :: Searching for "%s" in category: %s' % (site, term, category), 'INFO')
        result = xmltodict.parse(urllib.urlopen(url).read())['rss']['channel']

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
            for attr in item['newznab:attr']:
                if attr['@name'] == 'size':
                    size = convert_bytes(attr['@value'])

            a = {
                'nzblink': item['link'],
                'details': item['guid']['#text'],
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

    return render_template('dialogs/add_edit_newznab_dialog.html',
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

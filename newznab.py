# Author: J. van Emden
#
# ToDo:
# - implement search function:
#   - Select catergory to search in (currently cat=2000 is used)
#   - Disable enter in form
# - ability to handle multiple newznab accounts
#
from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from maraschino import app
from settings import *
from tools import *

def newznab_url():
    url = '%s/api?apikey=%s' % (get_setting_value('newznab_url'), get_setting_value('newznab_api'))
    
#    if using_auth():
#        return 'http://%s%s' % (login_string(), url)
        
    return 'http://%s' % (url)
    
def newznab_url_no_api():
    url = '%s/' % get_setting_value('newznab_url')

#    if using_auth():
#        return 'http://%s%s' % (login_string(), url)

    return 'http://%s' % (url)

@app.route('/xhr/newznab')
@requires_auth
def xhr_newznab():
    try:
        url = '%s&t=tvsearch&cat=5000,2000&o=json&limit=%s' % (newznab_url(), get_setting_value('newznab_items'))
        result = urllib.urlopen(url).read()
        newznab = json.JSONDecoder().decode(result)
    except:
        raise Exception
    
    #if newznab.rfind('ID') < 0:
    #    newznab = ''

    # spot info @ ?page=getspot&messageid=
    # nzb.su info @ /details/<guid>
    #
    return render_template('newznab.html', url = newznab_url_no_api(), newznab = newznab,)
    
@app.route('/newznab/series')
@requires_auth
def newznab_series():
    try:
        url = '%s&t=tvsearch&cat=5000&o=json&limit=%s' % (newznab_url(), get_setting_value('newznab_items'))
        result = urllib.urlopen(url).read()
        newznab = json.JSONDecoder().decode(result)
    except:
        raise Exception

    #  if newznab[].rfind('ID') >= 0:
    return render_template('newznab.html', url = newznab_url_no_api(), newznab = newznab,)
    #  return ''
  
@app.route('/newznab/movies')
@requires_auth
def newznab_movies():
    try:
        url = '%s&t=tvsearch&cat=2000&o=json&limit=%s' % (newznab_url(), get_setting_value('newznab_items'))
        result = urllib.urlopen(url).read()
        newznab = json.JSONDecoder().decode(result)
    except:
        raise Exception

#    if newznab[].rfind('ID') >= 0:
    return render_template('newznab.html', url = newznab_url_no_api(), newznab = newznab,)
#    return ''

@app.route('/newznab/search')
@requires_auth
def newznab_search():
    # Loads the search page
    return render_template('newznab-search.html', newznab = 'search',)
  
@app.route('/newznab/query', methods=['POST'])
@requires_auth
def newznab_query():
    # Fetch the query from the post results
    try:
        newz_query = request.form['query']
        newz_cat = request.form['cat']
        
    except:
        return jsonify({ 'status': 'error' })
    
    if newz_query == '':
        # Empty query
        return render_template('newznab-search.html', newznab = 'Search error', message = 'Empty query submitted!', )
    
    if newz_cat == '':
        newz_cat = '2000,5000'
        
    else:
        # Query the results
        try:
            url = '%s&t=tvsearch&o=json&limit=%s&q=%s&cat=%s' % (newznab_url(), get_setting_value('newznab_items'), newz_query, newz_cat)
            result = urllib.urlopen(url).read()
            newznab = json.JSONDecoder().decode(result)

        except:
            raise Exception
        
        message = 'Results for \'%s\':' % (newz_query)
        
        if result == '[]':
            # Empty results
            return render_template('newznab-search.html', newznab = 'Search error', message = message, error = 'No results found',)
            
        else:
            # Results found
            return render_template('newznab-search.html', url = newznab_url_no_api(), newznab = 'Search results', message = message, data = newznab,)

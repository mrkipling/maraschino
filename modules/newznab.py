# Author: J. van Emden
#
# ToDo:
# - implement search function:
#   - Handle multiple categories in python
#   - Disable enter in form
# - ability to handle multiple newznab accounts
#
from flask import Flask, jsonify, render_template
import json, jsonrpclib, urllib

from Maraschino import app
from settings import *
from maraschino.tools import *

def newznab_url():
    url = '%s/api?apikey=%s' % (get_setting_value('newznab_url'), get_setting_value('newznab_api'))
    
    # Check if url contains http otherwise add it
    if not ('http' in url):
        url = 'http://%s' % url
    
#    if using_auth():
#        return 'http://%s%s' % (login_string(), url)
        
    return url
    
def newznab_url_no_api():
    url = '%s/' % get_setting_value('newznab_url')
    
    # Check if url contains http otherwise add it
    if not ('http' in url):
        url = 'http://%s' % url

#    if using_auth():
#        return 'http://%s%s' % (login_string(), url)

    return url
    
def sabnzbd_url():
    url = ''
    
    try:
        sab_host = get_setting_value('sabnzbd_host')
        
    except:
        return url
    
    try:
        sab_port = get_setting_value('sabnzbd_port')
        
    except:
        pass
        
    try:
        sab_api = get_setting_value('sabnzbd_api')
        
    except:
        pass
    
    if sab_port != None:
        url = 'http://%s:%i/api?apikey=%s' % ( sab_host, sab_port, sab_api )
    else:
        url = 'http://%s/api?apikey=%s' % ( sab_host, sab_api )
    
    return url

@app.route('/xhr/newznab')
@requires_auth
def xhr_newznab():
    try:
        url = '%s&t=tvsearch&cat=5000,2000&o=json&limit=%s' % (newznab_url(), get_setting_value('newznab_items'))
        result = urllib.urlopen(url).read()
        newznab = json.JSONDecoder().decode(result)
    
    except:
        raise Exception
    
    if result == '[]':
        # Empty results
        newznab = ''
        
    for item in newznab:
        if (int(item['size']) / 1024 ) > 1024:
            if (int(item['size']) / pow(1024,2) ) > 1024:
                if (int(item['size']) / pow(1024,3) ) > 1024:
                    item['size'] = '%.2f TBytes' % float( int(item['size']) / pow(1024.,4) )
                else:
                    item['size'] = '%.2f GBytes' % float( int(item['size']) / pow(1024.,3) )
                
            else:
                item['size'] = '%.2f MBytes' % float( int(item['size']) / pow(1024.,2) )
            
        else:
            item['size'] = '%.2f KBytes' % float( int(item['size']) / 1024. )
    
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
    
    if result == '[]':
        # Empty results
        newznab = ''
    
    for item in newznab:
        if (int(item['size']) / 1024 ) > 1024:
            if (int(item['size']) / pow(1024,2) ) > 1024:
                if (int(item['size']) / pow(1024,3) ) > 1024:
                    item['size'] = '%.2f TBytes' % float( int(item['size']) / pow(1024.,4) )
                else:
                    item['size'] = '%.2f GBytes' % float( int(item['size']) / pow(1024.,3) )
                
            else:
                item['size'] = '%.2f MBytes' % float( int(item['size']) / pow(1024.,2) )
            
        else:
            item['size'] = '%.2f KBytes' % float( int(item['size']) / 1024. )
    
    return render_template('newznab.html', url = newznab_url_no_api(), newznab = newznab,)
  
@app.route('/newznab/movies')
@requires_auth
def newznab_movies():
    try:
        url = '%s&t=tvsearch&cat=2000&o=json&limit=%s' % (newznab_url(), get_setting_value('newznab_items'))
        result = urllib.urlopen(url).read()
        newznab = json.JSONDecoder().decode(result)
    except:
        raise Exception
    
    if result == '[]':
        # Empty results
        newznab = ''
    
    for item in newznab:
        if (int(item['size']) / 1024 ) > 1024:
            if (int(item['size']) / pow(1024,2) ) > 1024:
                if (int(item['size']) / pow(1024,3) ) > 1024:
                    item['size'] = '%.2f TBytes' % float( int(item['size']) / pow(1024.,4) )
                else:
                    item['size'] = '%.2f GBytes' % float( int(item['size']) / pow(1024.,3) )
                
            else:
                item['size'] = '%.2f MBytes' % float( int(item['size']) / pow(1024.,2) )
            
        else:
            item['size'] = '%.2f KBytes' % float( int(item['size']) / 1024. )
    
    return render_template('newznab.html', url = newznab_url_no_api(), newznab = newznab,)

@app.route('/newznab/search')
@requires_auth
def newznab_search():
    # Category list:
    categories = [ {'id': 2000, 'name': 'Movies'},
                   {'id': 2010, 'name': 'Movies - Foreign'},
                   {'id': 2020, 'name': 'Movies - Other'},
                   {'id': 2030, 'name': 'Movies - SD'},
                   {'id': 2040, 'name': 'Movies - HD'},
                   {'id': 2060, 'name': 'Movies - Sports'},
                   {'id': 5000, 'name': 'TV'},
                   {'id': 5010, 'name': 'TV - Foreign'},
                   {'id': 5030, 'name': 'TV - SD'},
                   {'id': 5040, 'name': 'TV - HD'},
                   {'id': 5050, 'name': 'TV - Other'},
                   {'id': 5060, 'name': 'TV - Sports'},
                   {'id': 5070, 'name': 'TV - Anime'}]

    # Loads the search page
    return render_template('newznab-search.html', newznab = 'search', categories = categories,)

@app.route('/newznab/search', methods=['POST'])
@requires_auth
def newznab_query():
    categories = [ {'id': 2000, 'name': 'Movies'},
                   {'id': 2010, 'name': 'Movies - Foreign'},
                   {'id': 2020, 'name': 'Movies - Other'},
                   {'id': 2030, 'name': 'Movies - SD'},
                   {'id': 2040, 'name': 'Movies - HD'},
                   {'id': 2060, 'name': 'Movies - Sports'},
                   {'id': 5000, 'name': 'TV'},
                   {'id': 5010, 'name': 'TV - Foreign'},
                   {'id': 5030, 'name': 'TV - SD'},
                   {'id': 5040, 'name': 'TV - HD'},
                   {'id': 5050, 'name': 'TV - Other'},
                   {'id': 5060, 'name': 'TV - Sports'},
                   {'id': 5070, 'name': 'TV - Anime'}]

    # Fetch the query from the post results
    # print request.form
    # ImmutableMultiDict([('query', u'Chuck'), ('cat', u'2010'), ('cat', u'5050'), ('cat', u'5060')])
    
    #test = request.form
    #print test
    
    try:
        newz_query = request.form['query']
        
    except:
        pass
        
    try:
        newz_cats = [int(request.form['cat'])]
        
    except:
        newz_cats = [2000]
    
    if newz_query == '':
        # Empty query
        return render_template('newznab-search.html', newznab = 'Search error', message = 'Empty query submitted!', categories = categories,)
        
    else:
        newz_name = ''
        newz_cats2 = ''
        i = 0
        
        sab_cat = ''
        
        for newz_cat in newz_cats:
            if newz_cat >= 2000 and newz_cat < 3000 and sab_cat == '':
                sab_cat = 'movies'
            
            elif newz_cat >= 5000 and newz_cat < 6000 and sab_cat == '':
                sab_cat = 'tv'
            
            newz_cats2 = '%s%s,' % ( newz_cats2, newz_cat )
            i += 1
            
            for cat in categories:
                if cat['id'] == newz_cat:
                    if i > 1 and i == len(newz_cats):
                        newz_name = '%s and %s' % ( newz_name, cat['name'] )
                        
                    elif i > 1 and i <= len(newz_cats):
                        newz_name = '%s, %s' % ( newz_name, cat['name'] )
                        
                    else:
                        newz_name = cat['name']
        
        # Query the results
        try:
            url = '%s&t=tvsearch&o=json&limit=%s&q=%s&cat=%s' % (newznab_url(), get_setting_value('newznab_items'), newz_query, newz_cats2)
            result = urllib.urlopen(url).read()
            newznab = json.JSONDecoder().decode(result)

        except:
            raise Exception
        
        message = 'Results for \'%s\' from \'%s\':' % (newz_query, newz_name.lstrip())
        
        if result == '[]':
            # Empty results
            return render_template('newznab-search.html', newznab = 'Search error', message = message, error = 'No results found', categories = categories,)
            
        else:
            for item in newznab:
                if (int(item['size']) / 1024 ) > 1024:
                    if (int(item['size']) / pow(1024,2) ) > 1024:
                        if (int(item['size']) / pow(1024,3) ) > 1024:
                            item['size'] = '%.2f TBytes' % float( int(item['size']) / pow(1024.,4) )
                        else:
                            item['size'] = '%.2f GBytes' % float( int(item['size']) / pow(1024.,3) )
                        
                    else:
                        item['size'] = '%.2f MBytes' % float( int(item['size']) / pow(1024.,2) )
                    
                else:
                    item['size'] = '%.2f KBytes' % float( int(item['size']) / 1024. )
                
                saburl = sabnzbd_url()
                if saburl != '':
                    nzb_url = '%s&t=get&id=%s' % ( newznab_url(), item['guid'] )
                    item['addToSab'] = '%s&mode=addurl&%s&cat=%s&output=json' % ( saburl, urllib.urlencode( { 'name': nzb_url } ), sab_cat )
                    #print item['addToSab']
            
            # Results found
            return render_template('newznab-search.html', url = newznab_url_no_api(), newznab = 'Search results', message = message, data = newznab, categories = categories,)

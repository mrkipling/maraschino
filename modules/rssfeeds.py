from flask import Flask, jsonify, render_template

from Maraschino import app
from settings import *
from maraschino.tools import *
import feedparser.feedparser

@app.route('/xhr/rssfeeds')
@requires_auth
def xhr_rssfeeds():

    feed = feedparser.parse('http://rss.nzbmatrix.com/rss.php?subcat=42')
    for entry in feed['entries']:
        print "Catagory: %s" % (entry['tags'][0]['term'])
        print "NZB name: %s" % (entry['title'])
        print "Link: %s" % (entry['links'][0]['href'])
        print "-----------------------------------------------------"
    
        return render_template('rssfeeds.html',
            feed = feed,
    )
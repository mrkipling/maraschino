from flask import Flask, jsonify, render_template

from Maraschino import app
from settings import *
from maraschino.tools import *
import feedparser.feedparser

@app.route('/xhr/rssfeeds')
@requires_auth
def xhr_rssfeeds():

    feed = feedparser.parse('http://rss.nzbmatrix.com/rss.php?subcat=42')
    return render_template('rssfeeds.html',
        feed = feed,
    )
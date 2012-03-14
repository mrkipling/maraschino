from flask import Flask, render_template

from Maraschino import app
from maraschino.tools import *
from feedparser import feedparser

@app.route('/xhr/rssfeeds')
@requires_auth
def xhr_rssfeeds():

    feed = feedparser.parse('http://rss.nzbmatrix.com/rss.php?subcat=54')

    return render_template('rssfeeds.html',
        feed = feed,
    )
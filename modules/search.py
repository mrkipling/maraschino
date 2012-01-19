from flask import Flask, jsonify, render_template

from Maraschino import app
from settings import *
from maraschino.tools import *
from nzbmatrix.pyMatrix import * 

@app.route('/xhr/search/')
def xhr_search():

    return render_template('search.html',
        results = nzb_matrix(item),
    )

@app.route('/xhr/nzbmatrix/<item>')
def nzb_matrix(item):
    API = get_setting_value('nzb_matrix_API')
    USERNAME = get_setting_value('nzb_matrix_user')
    
    nzb = Matrix(username=USERNAME, apiKey=API)

    if item is not '':
        return nzb.Search(item)

    #matrix = Matrix(username="MyUsername", apiKey="f70e1394d05be493069537a7d430297c")
    #print matrix.Bookmarks("566252", BOOKMARK_ACTION_REMOVE)
    #print matrix.Download("566252", "C:\\test")
    #print matrix.Details("659980")
    #print matrix.Search("book of eli")

    #for value in matrix.Search(query="34ferf34").values():
    #    print value
    
@app.route('/xhr/search/<item>')
def xhr_search(item):
    return render_template('search.html',
        results = nzb_matrix(item),
    )

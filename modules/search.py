from flask import Flask, jsonify, render_template

from Maraschino import app
from settings import *
from maraschino.tools import *
from nzbmatrix.pyMatrix import * 

# Newznab Category List:
cat_newznab = [ {'id': 2000, 'name': 'Movies'},
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
                {'id': 5070, 'name': 'TV - Anime'} ]

# NZBMatrix Category List:
cat_nzbmatrix = [
        { 'id': 0 , 'name': 'Everything' },
        { 'label' : 'Movies' , 'value' : [          
            { 'id': 1 , 'name': 'Movies: DVD' },
            { 'id': 2 , 'name': 'Movies: Divx/Xvid' },
            { 'id': 54 , 'name': 'Movies: BRRip' },
            { 'id': 42 , 'name': 'Movies: HD (x264)' },
            { 'id': 50 , 'name': 'Movies: HD (Image)' },
            { 'id': 48 , 'name': 'Movies: WMV-HD' },
            { 'id': 3 , 'name': 'Movies: SVCD/VCD' },
            { 'id': 4 , 'name': 'Movies: Other' },
          ] 
        },
        { 'label' : 'TV' , 'value' : [          
            { 'id': 5 , 'name': 'TV: DVD' },
            { 'id': 6 , 'name': 'TV: Divx/Xvid' },
            { 'id': 41 , 'name': 'TV: HD' },
            { 'id': 7 , 'name': 'TV: Sport/Ent' },
            { 'id': 8 , 'name': 'TV: Other' },
          ] 
        },
        { 'label' : 'Documentaries' , 'value' : [          
            { 'id': 9 , 'name': 'Documentaries: STD' },
            { 'id': 53 , 'name': 'Documentaries: HD' },
          ] 
        },
        { 'label' : 'Games' , 'value' : [          
            { 'id': 10 , 'name': 'Games: PC' },
            { 'id': 11 , 'name': 'Games: PS2' },
            { 'id': 43 , 'name': 'Games: PS3' },
            { 'id': 12 , 'name': 'Games: PSP' },
            { 'id': 13 , 'name': 'Games: Xbox' },
            { 'id': 14 , 'name': 'Games: Xbox360' },
            { 'id': 56 , 'name': 'Games: Xbox360 (Other)' },
            { 'id': 15 , 'name': 'Games: PS1' },
            { 'id': 16 , 'name': 'Games: Dreamcast' },
            { 'id': 44 , 'name': 'Games: Wii' },
            { 'id': 51 , 'name': 'Games: Wii VC' },
            { 'id': 45 , 'name': 'Games: DS' },
            { 'id': 46 , 'name': 'Games: GameCube' },
            { 'id': 17 , 'name': 'Games: Other' },
          ] 
        },
        { 'label' : 'Apps' , 'value' : [          
            { 'id': 18 , 'name': 'Apps: PC' },
            { 'id': 19 , 'name': 'Apps: Mac' },
            { 'id': 52 , 'name': 'Apps: Portable' },
            { 'id': 20 , 'name': 'Apps: Linux' },
            { 'id': 55 , 'name': 'Apps: Phone' },
            { 'id': 21 , 'name': 'Apps: Other' },
          ] 
        },
        { 'label' : 'Music' , 'value' : [        
            { 'id': 22 , 'name': 'Music: MP3 Albums' },
            { 'id': 47 , 'name': 'Music: MP3 Singles' },
            { 'id': 23 , 'name': 'Music: Lossless' },
            { 'id': 24 , 'name': 'Music: DVD' },
            { 'id': 25 , 'name': 'Music: Video' },
            { 'id': 27 , 'name': 'Music: Other' },
          ] 
        },
        { 'label' : 'Anime' , 'value' : [          
            { 'id': 28 , 'name': 'Anime: ALL' },
          ] 
        },
        { 'label' : 'Other' , 'value' : [          
            { 'id': 49 , 'name': 'Other: Audio Books' },
            { 'id': 33 , 'name': 'Other: Emulation' },
            { 'id': 34 , 'name': 'Other: PPC/PDA' },
            { 'id': 26 , 'name': 'Other: Radio' },
            { 'id': 36 , 'name': 'Other: E-Books' },
            { 'id': 37 , 'name': 'Other: Images' },
            { 'id': 38 , 'name': 'Other: Mobile Phone' },
            { 'id': 39 , 'name': 'Other: Extra Pars/Fills' },
            { 'id': 40 , 'name': 'Other: Other' },
          ] 
        },
    ]
    
@app.route('/xhr/search/')
@app.route('/xhr/search/<site>')
def xhr_search(site = None):
    if site == 'nzbmatrix':
        categories = cat_nzbmatrix
    elif site == 'nzb.su':
        categories = cat_newznab
    else:
        categories = ''
    
    return render_template('search.html',
        categories = categories,
    )

@app.route('/xhr/nzbmatrix/<item>')
@app.route('/xhr/nzbmatrix/<item>/<cat>')
def nzb_matrix(item, cat = None):
    API = get_setting_value('nzb_matrix_API')
    USERNAME = get_setting_value('nzb_matrix_user')
    
    nzb = Matrix(username=USERNAME, apiKey=API)
    
    if item is not '':
        if cat:
            result = nzb.Search(query = item, catId = cat)
        else:
            result = nzb.Search(item)

    return render_template('search.html',
        results = result,
        item = item,
        categories = cat_nzbmatrix,
    )
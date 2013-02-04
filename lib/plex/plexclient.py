'''
Created on Jun 23, 2012

@author: Anne Jan Elsinga
'''
__version__="0.1.2"
import urllib
import urllib2
import time
import xml.etree.ElementTree as ElementTree
    
def str2int (string):
    ''' 
    converts a string to an int
    input: string to convert
    output: integer
    '''
    try:
        i = int(string)
    except (ValueError,TypeError):
        i = 0
    return i

def getHTMLbody(urltoget):
    url=urllib2.urlopen(urltoget)
    currently_playing_page=url.read()
    url.close()
    result=[]
    toprocess=currently_playing_page.replace("<html>","")
    toprocess=toprocess.replace("</html>","")
    line=toprocess.split('<li>')
    return line
        
class PLEXLibrary(object):
    '''
    Connects to a Plex Media Server for various tasks
    '''
    
    def __init__(self, server="127.0.0.1:32400", MovieLibID="1", TVLibID="2", MusicLibID="3"):
        '''
        Constructor
        input: server including port 
        output: none
        '''
        self.server=server
        self.TVLibrary=TVLibID
        self.MovieLibrary=MovieLibID
        self.MusicLibrary=MusicLibID
    
    '''
    Shared functions that don't really have anything to do with Movies, TV Shows or Music
    '''
    def getXML (self, location):
        '''
        getXML returns the root for an XML for Plex
        '''
        try:
            formedurl=self.server+location
            tree = ElementTree.parse(urllib2.urlopen(formedurl))
            root=tree.getroot()
            return root
        except:
            return None
    
    def getClients(self):
        root=self.getXML("/clients")
        Clients=[]
        for node in root:
            Clients.append({'name': node.get('name'),'host':node.get('host'),'address':node.get('address'),'port':node.get('port'),
                    'version':node.get('version'),'uniqueid':node.get('machineIdentifier')})
        return Clients

    def playFile (self,filetoplay,player):
        key='/library/metadata/'+filetoplay
        url=self.server+key
        
        f={'path': url, 'key': key}
        url=self.server+"/system/players/"+player+"/application/playMedia?"+urllib.urlencode(f)
        result=getHTMLbody(url)
        print url
        return True
    
    def currentlyPlaying(self):
        # read all clients, create array with currently playing
        currentplay=[]
        playerinfo=[]
        for connectedclient in self.getClients():
            client=PLEXClient(connectedclient['host'],connectedclient['port'])
            curplay,playinfo=client.currentlyPlaying()
            curplay['host']=connectedclient['host']
            currentplay.append(curplay)
            playinfo['volume']=str2int(client.getVolume())
            playerinfo.append(playinfo)
        return currentplay,playerinfo
    
    def activePlayers(self):
        # returns active player
        activeply=[]
        current,player=self.currentlyPlaying()
        for active in current:
            if active['playstatus'] !='Stopped':
                active={'host': active['host']}
                activeply.append(active)
        return activeply
    
    def doAction (self,client, action):
        formedurl=self.server+"/system/players/"+client+"/"+action
        try:
            urllib2.urlopen(formedurl)
            return True
        except:
            return None
    
    '''
    TV Show Functions
    '''
    def getTVShows (self):
        '''
        getTVShows returns the TV shows from the library
        '''
        TVItems=[]
        url="/library/sections/"+self.TVLibrary+"/all"
        root = self.getXML(url)
        
        for node in root:
            watched = '0'
            if node.get('leafCount') == node.get('viewedLeafCount'):
                watched = '1'

            TVItems.append({'studio':node.get('studio'),'title':node.get('title'),'thumbnail':node.get('thumb'),'art':{'banner':node.get('banner')}, 
                            'label':node.get('title'),'premiered':node.get('originallyAvailableAt'),'tvshowid':node.get('ratingKey'),
                            'playcount':watched})
        return TVItems

    def getTVShowInfo (self, ratingKey):
        '''
        getMovieInfo returns the tv show info from the library
        '''
        url="/library/metadata/"+str(ratingKey)
        root = self.getXML(url)
        
        for node in root:
            return {'tvshowid':ratingKey,'label':node.get('title'),'year':node.get('year'),'thumbnail':node.get('thumb'),'genre':-1,'plot':node.get('summary'),
                    'playcount':0, 'rating': -1,'premiered':node.get('originallyAvailableAt'),'studio':node.get('studio')}
       
        return {}

    def getTVSeasons (self, tvshowid):
        '''
        getTVSeasons returns the TV seasons from the library
        '''
        #Grab top level show info
        url="/library/metadata/"+str(tvshowid)
        root = self.getXML(url)

        showtitle = ""

        for node in root:
            showtitle = node.get('title')

        TVItems=[]
        url="/library/metadata/"+str(tvshowid)+"/children"
        root = self.getXML(url)
        
        for node in root:
            watched = '0'
            if node.get('leafCount') == node.get('viewedLeafCount'):
                watched = '1'

            TVItems.append({'tvshowid':tvshowid,'season':node.get('ratingKey'),'label':node.get('title'),'showtitle':showtitle,'thumbnail':node.get('thumb'),'episode':node.get('leafCount'),
                            'unwatched':str(int(node.get('leafCount')) - int(node.get('viewedLeafCount'))),'watched':watched})
        return TVItems

    def getTVEpisodes (self, tvshowid, season):
        '''
        getTVEpisodes returns the TV episodes from the library
        '''
        #Grab top level show info
        url="/library/metadata/"+str(tvshowid)
        root = self.getXML(url)

        showtitle = ""

        for node in root:
            showtitle = node.get('title')

        TVItems=[]
        url="/library/metadata/"+str(season)+"/children"
        root = self.getXML(url)
        
        for node in root:
            TVItems.append({'tvshowid':tvshowid,'season':season,'episodeid':node.get('ratingKey'),'label':node.get('title'),'showtitle':showtitle,'thumbnail':node.get('thumb'),'episode':node.get('leafCount'),
                            'playcount':node.get('viewCount'),'firstaired':node.get('originallyAvailableAt')})
        return TVItems

    def getTVEpisodeInfo (self, episodeid):
        '''
        getTVEpisodeInfo returns the tv episode info from the library
        '''
        url="/library/metadata/"+str(episodeid)
        root = self.getXML(url)
        
        for node in root:
            return {'episodeid':episodeid,'label':node.get('title'),'thumbnail':node.get('thumb'),'plot':node.get('summary'),
                    'rating': -1,'firstaired':node.get('originallyAvailableAt')}
       
        return {}

    def getRecentlyAddedEpisodes (self):
        '''
        getRecentlyAddedEpisodes returns the recently added TV episodes from the library
        '''
        TVItems=[]
        url="/library/sections/"+self.TVLibrary+"/recentlyAdded"
        root = self.getXML(url)
        
        for node in root:
            TVItems.append({'title':node.get('title'),'season':node.get('parentIndex'),'episode': node.get('index'),
                            'showtitle':node.get('grandparentTitle'),'playcount':node.get('viewCount'),
                            'thumbnail':node.get('thumb'), 'episodeid':node.get('ratingKey')}) 
        return TVItems

    '''
    Movie Functions
    '''
    def getMovies (self):
        '''
        getMovies returns the movies from the library
        '''
        Movies=[]
        url="/library/sections/"+self.MovieLibrary+"/all"
        root = self.getXML(url)
        
        for node in root:
            Movies.append({'movieid':node.get('ratingKey'),'label':node.get('title'),'year':node.get('year'),'thumbnail':node.get('thumb')})
        return Movies

    def getMovieInfo (self, ratingKey):
        '''
        getMovieInfo returns the movie info from the library
        '''
        url="/library/metadata/"+str(ratingKey)
        root = self.getXML(url)
        
        for node in root:
            genre = ''
            director = ''
            for subnode in node:
                if subnode.tag == 'Genre':
                    if genre == '':
                        genre = subnode.get('tag')
                    else:
                        genre += ', ' + subnode.get('tag')
                elif subnode.tag == 'Director':
                    if director == '':
                        director = subnode.get('tag')
                    else:
                        director += ', ' + subnode.get('tag')
           
            return {'movieid':ratingKey,'label':node.get('title'),'year':node.get('year'),'thumbnail':node.get('thumb'),'genre':genre,'plot':node.get('summary'),
                    'director':director,'playcount':0, 'rating': -1}
       
        return {}

    def getRecentlyAddedMovies (self):
        '''
        getRecentlyAddedMovies returns the recently added movies from the library
        '''
        MovieItems=[]
        root = self.getXML("/library/sections/"+self.MovieLibrary+"/recentlyAdded")
        for node in root:
            MovieItems.append({'title':node.get('title'),'year':node.get('year'),'rating':node.get('rating'),
                              'playcount':node.get('viewCount'),'thumbnail':node.get('thumb'),'movieid':node.get('ratingKey')}) 
        return MovieItems

    '''
    Music Functions
    '''
    def getArtists (self):
        '''
        getArtists returns the artist info from the library
        '''
        Artists=[]
        url="/library/sections/" + self.MusicLibrary + "/all"
        root = self.getXML(url)

        for node in root:
            genre = ''
            for subnode in node:
                if subnode.tag == 'Genre':
                    if genre == '':
                        genre = subnode.get('tag')
                    else:
                        genre += ', ' + subnode.get('tag')

            Artists.append({'artistid':node.get('ratingKey'),'label':node.get('title'),'thumbnail':node.get('thumb'),'yearsactive':-1,'genre':genre})

        return Artists

    def getAlbums (self, artistid):
        '''
        getAlbums returns the albums info from the library
        '''
        #Grab top level artist info
        url="/library/metadata/"+str(artistid)
        root = self.getXML(url)

        artistName = ""

        for node in root:
            artistName = node.get('title')

        Albums=[]
        url="/library/metadata/" + str(artistid) + "/children"
        root = self.getXML(url)

        for node in root:
            Albums.append({'artistid':artistid,'artist':artistName,'albumid':node.get('ratingKey'),'label':node.get('title'),'thumbnail':node.get('thumb'),'year':node.get('year')})

        return Albums

    def getSongs (self, artistid, albumid):
        '''
        getSongs returns the songs info from the library
        '''
        #Grab top level artist info
        url="/library/metadata/"+str(artistid)
        root = self.getXML(url)

        artistName = ""

        for node in root:
            artistName = node.get('title')

        #Grab top level album info
        url="/library/metadata/"+str(albumid)
        root = self.getXML(url)

        albumName = ''
        albumYear = ''

        for node in root:
            albumName = node.get('title')
            albumYear = node.get('year')

        Albums=[]
        url="/library/metadata/" + str(albumid) + "/children"
        root = self.getXML(url)

        for node in root:
            index = 0
            if node.get('index') != None:
                track = int(node.get('index'))
            Albums.append({'artistid':artistid,'albumid':albumid,'album':albumName,'artist':artistName,'year':albumYear,'title':node.get('title'),'thumbnail':node.get('thumb'),'track':index})

        return Albums

    def getRecentlyAddedAlbums (self):
        '''
        getRecentlyAddedAlbums returns the recently added music from the library
        '''
        MusicItems=[]
        root = self.getXML("/library/sections/"+self.MusicLibrary+"/recentlyAdded")
        for node in root:
            MusicItems.append({'title':node.get('title'),'year':node.get('year'),'rating':node.get('rating'),
                               'artist':node.get('artist'),'thumbnail':node.get('thumb'),
                               'albumid':node.get('ratingKey')})
        return MusicItems
        
class PLEXClient(object):
    '''
    connects to a Plex client (aka the Plex Client) for various tasks 
    '''
    def sendmessage (self, message):
        try: 
            urllib2.urlopen(self.commandurl+"ExecBuiltIn(Notification("+urllib2.quote(message)+"))")
            return True
        except:
            return None

    def __init__(self, server="127.0.0.1", port="3000"):
        '''
        Keyword arguments:
        name -- Name of the client
        icon_file -- location of an icon file, if any (png, jpg or gif)
        '''
        self.server=server
        self.port=port
        self.commandurl="http://"+self.server+":"+self.port+"/xbmcCmds/XbmcHttp?command="

    def currently_playing(self):
        toprocess=getHTMLbody(self.commandurl+"GetCurrentlyPlaying")
        curplay={}
        curplay['tvshowid']=0
        playerinfo={}
        playerinfo['shuffled']='Unknown'
        playerinfo['repeat']='Unknown'        
        for line in toprocess:
            if line.startswith("PlayStatus"):
                playStatus=line[11:].strip()
                curplay ['playstatus']=playStatus
            elif line.startswith('Track'):
                curplay['track']=line[6:].strip()
            elif line.startswith('Artist'):
                curplay['albumartist']=''
                curplay['artistid']=0
                curplay['artist']=line[7:].strip().decode('utf-8','ignore')
            elif line.startswith('Album'):
                curplay['albumid']=0
                curplay['album']=line[6:].strip().decode('utf-8','ignore')
                
            elif line.startswith('Lyrics'):
                curplay['lyrics']=line[7:].strip()
            elif line.startswith('URL'):
                curplay['url']=line[4:].strip()
            elif line.startswith('Samplerate'):
                curplay['samplerate']=line[11:].strip()
            elif line.startswith('SongNo'):
                curplay['songno']=line[7:].strip()
            elif line.startswith("Filename"):
                curplay['filename']=line[9:].strip()
                if curplay['filename']=='[Nothing Playing]':
                    curplay['playstatus']='Stopped'
            elif line.startswith("VideoNo"):
                curplay['videono']=line[8:].strip()
            elif line.startswith("Type"):
                curplay['type']=line[5:].strip().lower()
            elif line.startswith("Show Title"):
                curplay['showtitle']=line[11:].strip()
            elif line.startswith("Title"):
                curplay['title']=line[6:].strip().decode('utf-8','ignore')
            elif line.startswith("Plotoutline"):
                curplay['plotoutline']=line[12:].strip().decode('utf-8','ignore')
            elif line.startswith("Plot"):
                curplay['plot']=line[5:].strip().decode('utf-8','ignore')
            elif line.startswith("Year"):
                curplay['year']=line[5:].strip()
            elif line.startswith("Season"):
                curplay['season']=line[7:].strip()
            elif line.startswith("Episode"):
                curplay['episode']=line[8:].strip()
            elif line.startswith("Thumb"):
                thumb=line[6:].strip()
                #curplay['thumbnail']='http://'+self.server+":"+self.port+"/vfs/"+thumb
                curplay['thumbnail']=thumb
                curplay['fanart']='http://'+self.server+":"+self.port+"/vfs/"+thumb[:-4]
            elif line.startswith("Time"):
                time=line[5:].strip()
                time=time.split(':')
                if len(time)==1:
                    playerinfo['time']={'hours':0,'minutes':0,'seconds':str2int(time)}
                elif len(time)==2:
                    playerinfo['time']={'hours':0, 'minutes':str2int(time[0]),'seconds':str2int(time[1])}
                elif len(time)==3:
                    playerinfo['time']={'hours':str2int(time[0]), 'minutes': str2int(time[1]),'seconds':str2int(time[2])}
            elif line.startswith("Duration"):
                duration=line[9:].strip()
                time=duration.split(':')
                if len(time)==1:
                    playerinfo['totaltime']={'hours':0,'minutes':0,'seconds':str2int(time)}
                elif len(time)==2:
                    playerinfo['totaltime']={'hours':0, 'minutes':str2int(time[0]),'seconds':str2int(time[1])}
                elif len(time)==3:
                    playerinfo['totaltime']={'hours':str2int(time[0]), 'minutes': str2int(time[1]),'seconds':str2int(time[2])}
            elif line.startswith("Percentage"):
                playerinfo['percentage']=line[11:].strip()
            elif line.startswith("File size"):
                curplay['filesize']=line[10:].strip()
            elif line.startswith("Changed"):
                curplay['changed']=line[8:].strip()
            if 'year' not in curplay:
                curplay['year']=0
        return curplay,playerinfo

    def setVolume(self,volume):
        if isinstance(volume,(int,long)):
            volume=str(volume)
        toprocess=getHTMLbody(self.commandurl+"SetVolume("+volume+")")
        if toprocess[1].strip()=="OK":
            return True
        else:
            return False
        
    def seekPercentage (self, percentage):
        if isinstance(percentage,(int,long)):
            percentage=str(percentage)
        execute=getHTMLbody(self.commandurl+'SeekPercentage('+percentage+")")
        if execute[1].strip()=="OK":
            return True
        else:
            return False
        
    def getVolume(self):
        toprocess=getHTMLbody(self.commandurl+"GetVolume()")
        return toprocess[1].strip()
        
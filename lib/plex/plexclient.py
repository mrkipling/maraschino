'''
Created on Jun 23, 2012

@author: Anne Jan Elsinga
'''
__version__="0.1.1"

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
    
    def plexgetxml (self, location):
        '''
        plexgetxml returns the root for an XML for Plex
        '''
        try:
            formedurl=self.server+location
            tree = ElementTree.parse(urllib2.urlopen(formedurl))
            root=tree.getroot()
            return root
        except:
            return None
    
    def getclients(self):
        root=self.plexgetxml("/clients")
        Clients=[]
        for node in root:
            Clients.append({'name': node.get('name'),'host':node.get('host'),'address':node.get('address'),'port':node.get('port'),
                    'version':node.get('version'),'uniqueid':node.get('machineIdentifier')})
        return Clients
    
    def getrecentlyaddedepisodes (self):
        '''
        getrecentlyaddedepisodes returns the recently added TV episodes from the library
        '''
        TVItems=[]
        root = self.plexgetxml("/library/sections/"+self.TVLibrary+"/recentlyAdded")
        
        for node in root:
            TVItems.append({'title':node.get('title'),'season':node.get('parentIndex'),'episode': node.get('index'),
                            'showtitle':node.get('grandparentTitle'),'playcount':node.get('viewCount'),
                            'thumbnail':node.get('thumb')}) 
        return TVItems
        
    
    def getrecentlyaddedmovies (self):
        '''
        getrecentlyaddedmovies returns the recently added movies from the library
        '''
        MovieItems=[]
        root = self.plexgetxml("/library/sections/"+self.MovieLibrary+"/recentlyAdded")
        for node in root:
            MovieItems.append({'title':node.get('title'),'year':node.get('year'),'rating':node.get('rating'),
                              'playcount':node.get('viewCount'),'thumbnail':node.get('thumb')}) 
        return MovieItems
    
    def getrecentlyaddedalbums (self):
        '''
        getrecentlyaddedalbums returns the recently added music from the library
        '''
        MusicItems=[]
        root = self.plexgetxml("/library/sections/"+self.MusicLibrary+"/recentlyAdded")
        for node in root:
            MusicItems.append({'title':node.get('title'),'year':node.get('year'),'rating':node.get('rating'),
                               'artist':node.get('artist'),'thumbnail':node.get('thumb')})
        return MusicItems
    
    def currently_playing(self):
        # read all clients, create array with currently playing
        currentplay=[]
        playerinfo=[]
        for connectedclient in self.getclients():
            client=PLEXClient(connectedclient['host'],connectedclient['port'])
            curplay,playinfo=client.currently_playing()
            curplay['host']=connectedclient['host']
            currentplay.append(curplay)
            playerinfo.append(playinfo)
        return currentplay,playerinfo
    
    def active_players(self):
        # returns active player
        activeply=[]
        current,player=self.currently_playing()
        for active in current:
            if active['playstatus'] !='Stopped':
                active={'host': active['host']}
                activeply.append(active)
        return activeply
    
    def do_action (self,client, action):
        formedurl=self.server+"/system/players/"+client+"/"+action
        try:
            urllib2.urlopen(formedurl)
            return True
        except:
            return None
        
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
        url=urllib2.urlopen(self.commandurl+"GetCurrentlyPlaying")
        currently_playing_page=url.read()
        url.close()
        toprocess=currently_playing_page.replace("<html>","")
        toprocess=toprocess.replace("</html>","")
        toprocess = toprocess.split('<li>')
        
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
                if (curplay['filename']=='[Nothing Playing]'):
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
                curplay['thumbnail']='http://'+self.server+":"+self.port+"/vfs/"+thumb
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
            if ('year' not in curplay):
                curplay['year']=0
        return curplay,playerinfo

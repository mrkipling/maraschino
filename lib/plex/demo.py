import os
from plexclient import PLEXClient, PLEXLibrary
'''
@author: Anne Jan Elsinga
This scripts serves as a demo for what the plex client library can do.
'''

PlexServer=""
PlexPort=""
TVSection=""
MovieSection=""
AlbumSection=""
NumOfItems=3
mediaplayer=object
    
def clear_screen():
    os.system( [ 'clear', 'cls' ][ os.name == 'nt' ] )
    
def print_menu():
    clear_screen()
    print "PLEXLibrary Demo"
    print "================="
    print
    print
    print_current_config()
    print
    print "1. Set connection info"
    
    if hasattr(mediaplayer,'server'):
        print "2. Show recently added movies"
        print "3. Show recently added episodes"
        print "4. Show recently added albums"
        print "5. Show currently playing (info)"
        print "6. show connected clients"
        print "7. Send message to all connected clients"
        print "8. Play default client"
        print "9. Show currently playing clients"
    print 
    print "q. quit"
    print 
 
def print_current_config():
    print "Current config:"
    print " - Plex server: ", PlexServer
    print " - Plex Port: ", PlexPort
    print " - Movies Library ID: ", MovieSection
    print " - Series Library ID: ", TVSection  
    print " - Albums Library ID: ", AlbumSection
    print " - show num of items: ", NumOfItems
    
    
def get_connection_info():
    global PlexServer
    global PlexPort
    global TVSection
    global MovieSection
    global AlbumSection
    global actions
    global NumOfItems
    
    print 
    print "Enter configuration info"
    print "========================"
    PlexServer=raw_input("Enter Plex Server (name or IP address):")
    PlexPort=raw_input("enter port: ")
    MovieSection=raw_input ("Enter the library ID for your movies: ")
    TVSection=raw_input ("Enter the library ID for your series: ")
    AlbumSection=raw_input ("Enter the library ID for your albums: ")
    NumOfItems=str2num(raw_input("Enter number of items to show: "))
    create_connection_object()
    
    
def str2num (string):
    try:
        i = int(string)
    except ValueError:
        i = 0
    return i
    
def create_connection_object():
    global mediaplayer
    
    plexconnectionstring="http://"+PlexServer+":"+PlexPort
    mediaplayer = PLEXLibrary(plexconnectionstring,MovieLibID=MovieSection, TVLibID=TVSection, MusicLibID=AlbumSection)

def no_such_action():
    print "Chosen option invalid. Please try again"

def wait_for_enter():
    raw_input("Press Enter to continue...")
    
def maxnum (item,itemstoshow):
    if len(item)<itemstoshow:
        x=len(item)
    else:
        x=NumOfItems
    return x

def showrecentlyaddedmovies():
    AllMovies=mediaplayer.getrecentlyaddedmovies()
    for x in range (0,maxnum(AllMovies,NumOfItems)):
        showmovie(AllMovies[x])
    wait_for_enter()

def showrecentlyaddedseries():
    AllSeries=mediaplayer.getrecentlyaddedepisodes()
    for x in range (0,maxnum(AllSeries,NumOfItems)):
        showseries(AllSeries[x])
    wait_for_enter() 

def showrecentlyaddedalbums():
    AllAlbums=mediaplayer.getrecentlyaddedalbums()
    for x in range (0,maxnum(AllAlbums,NumOfItems)):
        showalbums(AllAlbums[x])
    wait_for_enter() 
    
def showrecentlyairedseries():
    AllSeries=mediaplayer.recentlyAiredTV()
    for x in range (0,maxnum(AllSeries,NumOfItems)):
        showseries(AllSeries[x])
    wait_for_enter() 
    
def doe_wat():
    mediaplayer.do_action ('192.168.1.102', 'playback/pause')
    #possible commands under playback: play, pause, stop, rewind, fastForward, stepForward
    #bigStepForward, stepBack, bigStepBack, skipNext, skipPrevious
    wait_for_enter()
    
def showcurrentlyplaying():
    allPlaying,playerinfo=mediaplayer.currently_playing()
    print allPlaying,playerinfo
    wait_for_enter()
    
def showplayingclients():
    print mediaplayer.active_players()
    wait_for_enter()
    
def showconnectedclients():
    for client in mediaplayer.getclients():
        print "address: "+ client['address']
        print "unique ID: "+client['uniqueid']
        print "version: " + client['version']
        print "client name: " +client['name']
        print "client hostname: " +client['host']
    wait_for_enter()        

def sendmessagetoallclients():
    MessageTitle=raw_input("Enter a title for the message:")
    MessageText=raw_input("Enter a message:")
    for connectedclient in mediaplayer.getclients():
        client=PLEXClient(connectedclient['host'],connectedclient['port'])
        client.sendmessage(MessageTitle+","+MessageText)
    wait_for_enter()
    
def buildmenu():
    global actions
    while True:
        print_menu()
        selection = raw_input("Your selection: ")
        if "q" == selection:
            return
        toDo = actions.get(selection, no_such_action)
        toDo()
        
def asciiprint (item):
    print item.encode('ascii','ignore')
            
def showmovie(movie):
    asciiprint ("Movie title: " + movie.title)
    print ('-' * 80)

def showseries(series):
    asciiprint ("Series title: " + series.showtitle)
    asciiprint ("episode: " + str(series.season) + "x" + str(series.episode) + " " +series.title)
    asciiprint ("playcount" + str(series.playcount))
    print ('-' * 80)

def showalbums(album):
    asciiprint ("Album title: " + album.title)
    print ('-' * 80)
    

if __name__ == '__main__':
    actions = {"1": get_connection_info, "2": showrecentlyaddedmovies, "3": showrecentlyaddedseries,"4": showrecentlyaddedalbums, 
               "5": showcurrentlyplaying, "6": showconnectedclients, "7": sendmessagetoallclients, "8": doe_wat, '9':showplayingclients}
    buildmenu()   

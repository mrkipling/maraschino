#Maraschino

* **Author**: [Bradley Abrahams](https://github.com/mrkipling)

* **Main collaborator**: [Gustavo Hoirisch](https://github.com/gugahoi)

##What is Maraschino?

I wanted a simple web interface to act as a nice overview/front page for my XBMC HTPC. I couldn't find anything that suited my requirements so I created something myself.

You can find more information and setup instructions on the [project homepage](http://www.maraschinoproject.com/ "Maraschino Project homepage").

There is now also an [official forum](http://forums.maraschinoproject.com/) which is your best bet for support, feature requests and bug reports.

In addition, there's also a thread on the [XBMC forums](http://forum.xbmc.org/showthread.php?t=113136 "XBMC forums").

##Screenshots
<img src="http://www.maraschinoproject.com/static/images/screenshot1.jpg" width="400">&nbsp;&nbsp;<img src="http://www.maraschinoproject.com/static/images/screenshot2.jpg" width="400">

##What features does it have?

* Customisable applications module providing quick access to your web interfaces (e.g. SABnzb+, SickBeard, or whatever else you want to link to).

* Recently added episodes/movies/albums modules - click an episode or movie to play it in XBMC.

* Media library browser - browse your entire movie and TV library, and click to play in XBMC. Queue items to play after.

* Control multiple XBMC servers - do you have an XBMC server in both the living room and bedroom? Switch between the two instantaly and control them using Maraschino!

* SABnzbd+ module which appears when something is downloading and hides again when finished - shows you what is currently downloading, speed, time/MB remaining, and a progress bar. Control (pause, resume, speed limit) your downloads.

* Usenet search module - search Usenet and add files directly to SABnzbd+ with the click of a button!

* Currently playing bar with play/pause/stop/volume controls, and a fully featured seek bar.

* trakt.tv shouts module which shows you what people are saying about the episode or movie that you're watching, and allows you to add your own shouts (requires a free trakt.tv account)

* trakt.tv plus module - see what your friends are watching, and view personalised TV and movie recommendations based on your viewing history.

* Sickbeard module which allows you to browse upcoming episodes and manage Sickbeard directly from Maraschino (add new shows, search for episodes, etc.).

* Disk space module showing you used/remaining space on your various drives.

* Weather module, because why the hell not!

* uTorrent and Transmission modules for the torren users among you.

* Full-screen background image changes to the fanart of what you're currently watching (optional, can be turned off)

* Customisable from within the application itself - choose how many columns you want, add new modules, rearrange them using drag-and-drop, and modify their settings without touching any settings files!

Uses Flask and some other awesome technologies (SQL-Alchemy, LESS CSS). Just set up Maraschino.py to be served using Apache and mod_wsgi or however your prefer to do it.

This is an early-stage work-in-progress - if you run into any problems then let me know, perhaps I or somebody else can help (at the very least, bug reports are always welcome!)

##Why is it called Maraschino?

If your HTPC is an ice cream sundae then Maraschino is the cherry on top.
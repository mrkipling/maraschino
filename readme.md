#Maraschino

##What is Maraschino?

I wanted a simple web interface to act as a nice overview/front page for my XBMC HTPC. I couldn't find anything that suited my requirements so I created something myself.

You can find more information and setup instructions on the [project homepage](http://www.maraschinoproject.com/ "Maraschino Project").

There's also a thread on the XBMC forums [XBMC forums](http://forum.xbmc.org/showthread.php?t=113136 "XBMC forums").

##Screenshots
<img src="http://www.maraschinoproject.com/static/images/screenshot1.jpg" width="400" style="margin-right: 20px;"><img src="http://www.maraschinoproject.com/static/images/screenshot2.jpg" width="400">

##What features does it have?

* Customisable applications widget providing quick access to your web interfaces (e.g. SABnzb+, SickBeard, or whatever else you want to link to)

* Recently added episodes widget - click an episode to play it in XBMC

* Media library browser - browse your movies and TV shows, and click to play in XBMC

* SABnzbd+ widget which appears when something is downloading and hides again when finished - shows you what is currently downloading, speed, time/MB remaining, and a progress bar

* Currently playing bar with play/pause/stop controls

* trakt.tv widget which shows you what people are saying about the episode or movie that you're watching (requires a free trakt.tv account)

* Disk space widget showing you used/remaining space on your various drives

* Full-screen background image changes to the fanart of what you're currently watching (optional, can be turned off)

* Customisable from within the application itself - no need to mess around with settings files

Uses Flask and some other awesome technologies (SQL-Alchemy, LESS CSS). Just set up maraschino.py to be served using Apache and mod_wsgi or however your prefer to do it.

This is an early-stage work-in-progress - if you run into any problems then let me know, perhaps I or somebody else can help (at the very least, bug reports are always welcome!)

##Why is it called Maraschino?

If your HTPC is an ice cream sundae then Maraschino is the cherry on top.
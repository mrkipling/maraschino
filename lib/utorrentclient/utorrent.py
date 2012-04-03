import urllib, urllib2,cookielib, sys, os, re, time
#based on the uTorrent XBMC addon by Taxigps

class HttpClient(object):
    def __init__(self, address='localhost', port='8080', user=None, password=None):
        base_url = 'http://' + address + ':' + port
        self.url = base_url + '/gui/'
        if user:
            password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_manager.add_password(realm=None, uri=self.url, user=user, passwd=password)
            self.MyCookies = cookielib.LWPCookieJar()
         
            opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(self.MyCookies)
                , urllib2.HTTPBasicAuthHandler(password_manager)
                )
            opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) chromeframe/4.0')]
            urllib2.install_opener(opener)

    def HttpCmd(self, urldta, postdta=None, content=None):
        ## Standard code
        req = urllib2.Request(urldta,postdta)

        ## Process only if Upload..
        if content != None   :
                req.add_header('Content-Type',content)
                req.add_header('Content-Length',str(len(postdta)))

        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

class Torrent(object):

    def __init__(self,torrent):
        self.hash = torrent[0]
        self.status = torrent[1]
        self.name = torrent[2]
        self.progress = torrent[3]
        self.size = torrent[4]
        self.up_rate = torrent[5]
        self.down_rate = torrent[6]
        self.eta = torrent[7]

class uTorrent(object):
    
    def __init__(self,address,port,user,password):
        self.baseurl = 'http://' + address + ":" + port + "/gui/"
        self.myClient = HttpClient(address,port,user,password)
        
    def getToken(self):
        tokenUrl = self.baseurl + 'token.html'

        try:
            data = self.myClient.HttpCmd(tokenUrl)
        except:
            sys.exit(1)
        

        match = re.compile("<div id='token' style='display:none;'>(.+?)</div>").findall(data)
        token = match[0]

        return token

    def listTorrents(self):
        token = self.getToken()
        url = self.baseurl + "?token=" + token + '&list=1'
        data = self.myClient.HttpCmd(url)
        data = data.split('\n')
        torrentList = []
        for line in data:
            if '\"rssfeeds\"' in line:
                break
            if len(line) > 80:
                tor = re.findall('\"[^\"]*\"|[0-9\-]+', line)
                hashnum = tor[0][1:-1]
                status = tor[1]
                torname = tor[2].replace("\"","")
                complete = tor[4]
                complete = int(complete)
                complete = complete / 10.0
                size = int(tor[3]) / (1024*1024)
                if (size >= 1024.00):
                   size_str = str(round(size / 1024.00,2)) +"Gb"
                else:
                    size_str = str(size) + "Mb"
                up_rate = round(float(tor[8]) / (1024),2)
                down_rate = round(float(tor[9]) / (1024),2)
                remain = int(tor[10]) / 60
                if (remain >=60):
                    remain_str = str(remain//60) + "h " + str(remain%60) + "m"
                elif(remain == -1):
                    remain_str = '?'
                else:
                    remain_str = str(remain) + "m"
                tup = (hashnum, status, torname, complete, size_str, up_rate, down_rate,remain_str)
                print(torname + str(status))
                torrentList.append(Torrent(tup))
        return torrentList


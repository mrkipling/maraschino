from maraschino.noneditable import *

try:
    import json
except ImportError:
    import simplejson as json
import urllib2, base64

api_address = xbmc_api_address()
username = xbmc_username()
password = xbmc_password()

class XBMCJSON:

    def __init__(self, server):
        self.server = server
        self.version = '2.0'

    def __call__(self, **kwargs):
        method = '.'.join(map(str, self.n))
        self.n = []
        return XBMCJSON.__dict__['Request'](self, method, kwargs)
 
    def __getattr__(self,name):
        if not self.__dict__.has_key('n'):
            self.n=[]
        self.n.append(name)
        return self

    def Request(self, method, kwargs):
        data = [{}]
        data[0]['method'] = method
        data[0]['params'] = kwargs
        data[0]['jsonrpc'] = self.version
        data[0]['id'] = 1

        data = json.JSONEncoder().encode(data)
        content_length = len(data)

        content = {
            'Content-Type': 'application/json',
            'Content-Length': content_length,
        }
   
        request = urllib2.Request(self.server, data, content)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        f = urllib2.urlopen(request)
        response = f.read()
        f.close()
        response = json.JSONDecoder().decode(response)

        try:
            return response[0]['result']
        except:
            return response[0]['error']


xbmc = XBMCJSON(api_address)

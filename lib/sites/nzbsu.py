import htmlentitydefs, os, re, urllib, urllib2, json, jsonrpclib

ERROR_INVALID_LOGIN           = "error:invalid_login"
ERROR_INVALID_API             = "error:invalid_api"
ERROR_INVALID_NZBID           = "error:invalid_nzbid"
ERROR_VIP_ONLY                = "error:vip_only"
ERROR_DISABLED_ACCOUNT        = "error:disabled_account"
ERROR_NO_NZB_FOUND            = "error:no_nzb_found"
ERROR_NO_USER                 = "error:no_user"
ERROR_NO_SEARCH               = "error:no_search"
ERROR_PEASE_WAIT_X            = "error:please_wait_x"
ERROR_NOTHING_FOUND           = "error:nothing_found"
ERROR_X_DAILY_LIMIT           = "error:x_daily_limit"
ERROR_ALL_TYPES               = [ERROR_INVALID_LOGIN, ERROR_INVALID_API, ERROR_INVALID_NZBID, ERROR_VIP_ONLY, ERROR_DISABLED_ACCOUNT, ERROR_NO_USER, ERROR_NO_NZB_FOUND, ERROR_NO_SEARCH, ERROR_PEASE_WAIT_X, ERROR_NOTHING_FOUND, ERROR_X_DAILY_LIMIT]

class nzbsu:
    def __init__(self, apiKey):
        self._apiKey   = apiKey

    def Search(self, query, catId="", group=""):
        extra = ""
        if not query:
            return False
        if group != "":
            extra = "&group="+group
        if catId != "":
            extra = extra+"&cat="+catId
             
        url    = "http://nzb.su/api?t=search&q=%s%s&apikey=%s&o=json" %(query, extra, self._apiKey)
        cache  = urllib.urlopen(url)
        source = cache.read()
        cache.close()

        result = json.JSONDecoder().decode(source)
        
        return result

######################################################################################################################################

#nzb = nzbsu(apiKey="f70e1394d05be493069537a7d430297c")
#  print matrix.Search("book of eli")


import htmlentitydefs, os, re, urllib, urllib2

BOOKMARK_ACTION_ADD           = "add"
BOOKMARK_ACTION_REMOVE        = "remove"
BOOKMARK_RESULT_ADDED         = "bookmark_added"
BOOKMARK_RESULT_ADDED_ALREADY = "bookmark_added_already"
BOOKMARK_RESULT_NOT_FOUND     = "bookmark_not_found"
BOOKMARK_RESULT_REMOVED       = "bookmark_removed"

DOWNLOAD_DONT_USE_SCENENAME   = "0"
DOWNLOAD_USE_SCENENAME        = "1"

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

REGION_CODING_UNKNOWN         = '0'
REGION_CODING_PAL             = '1'
REGION_CODING_NTSC            = '2'
REGION_CODING_FREE            = '3'

class Matrix:
    def __init__(self, username, apiKey):
        self._username = username
        self._apiKey   = apiKey

    def Details(self, nzbId):
        if not nzbId:
            return False
        data   = {}
        url    = "http://api.nzbmatrix.com/v1.1/details.php?id=%s&username=%s&apikey=%s" % (nzbId, self._username, self._apiKey)
        cache  = urllib.urlopen(url)
        source = cache.read()
        cache.close()
        if "error:" in source:
            source += ";\n"
        for item in re.findall("(.*?):(.*?);\n", source):
            data[item[0]] = item[1]
        return data

    def Search(self, query, num="50", catId="", age="", region="", group="", larger="", smaller="", minHits="", maxHits="", maxAge="", englishOnly="1", searchIn=""):
        if not query:
            return False
        data   = {}
        url    = "http://api.nzbmatrix.com/v1.1/search.php?search=%s&num=%s&catid=%s&age=%s&region=%s&group=%s&larger=%s" \
                 "&smaller=%s&minhits=%s&maxhits=%s&maxage=%s&englishonly=%s&searchin=%s" \
                 "&username=%s&apikey=%s" % \
                 (query, num, catId, age, region, group, larger, smaller, minHits, maxHits, maxAge, englishOnly, searchIn, self._username, self._apiKey)
        cache  = urllib.urlopen(url)
        source = cache.read()
        cache.close()
        if "error:" in source:
            for item in re.findall("(.*?):(.*)", source):
                data[item[0]] = item[1].strip()
            return data
        source = source.split("\n|\n")
        for index, part in enumerate(source[:-1]):
            data[index] = {}
            foundItems  = re.findall("(.*?):(.*?);", part)
            for item in foundItems:
                data[index][item[0]] = item[1]
        return data

    def Download(self, nzbId, dest, sceneName="0"):
        if not nzbId:
            return False
        url   = "http://api.nzbmatrix.com/v1.1/download.php?id=%s&username=%s&apikey=%s&scenename=%s" % (nzbId, self._username, self._apiKey, sceneName)
        cache = urllib.urlopen(url)
        print cache.headers
        try:    filename = re.findall('filename="(.*?)"', cache.headers["content-disposition"])[0]
        except: filename = "temp.nzb"
        print filename
        source = cache.read()
        cache.close()
        if not dest.endswith("\\"):
            dest += "\\"
        f = file("%s%s" % (dest, filename), "wb")
        f.write(source)
        f.close()
        return source

    def Account(self):
        data   = {}
        url    = "http://api.nzbmatrix.com/v1.1/account.php?username=%s&apikey=%s" % (self._username, self._apiKey)
        cache  = urllib.urlopen(url)
        source = cache.read()
        cache.close()
        if "error:" in source:
            source += ";\n"
        for item in re.findall("(.*?):(.*?);\n", source):
            data[item[0]] = item[1]
        return data

    def Bookmarks(self, nzbId, action=BOOKMARK_ACTION_ADD):
        data   = {}
        url    = "http://api.nzbmatrix.com/v1.1/bookmarks.php?id=%s&username=%s&apikey=%s&action=%s" % (nzbId, self._username, self._apiKey, action.lower())
        cache  = urllib.urlopen(url)
        source = cache.read()
        cache.close()
        if "error:" in source:
            source += ";\n"
        for item in re.findall("(.*?):(.*?);\n", source):
            data[item[0]] = item[1]
        return data

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)

def SortFiles(nzb, others=False):
    rars, pars, other  = [], [], []
    cache  = file(nzb, "r")
    source = cache.read()
    cache.close()
    start = re.findall("(<\?xml.*?xmlns.*?>)", source, re.IGNORECASE | re.DOTALL)
    parts = list(re.findall("(<file.*?</file>)", source, re.IGNORECASE | re.DOTALL))
    parts.sort()
    for part in parts:
        subj = str(re.findall('subject=".*?(".*?").*?"', unescape(part))[0])
        if re.search(".nfo|.sfv|.jpg|.png|subs.rar|subtitle|sample|other", subj, re.IGNORECASE):
            other.append(part)
        elif re.search(".par2", subj, re.IGNORECASE):
            pars.append(part)
        elif re.search(".part\d\d*.rar", subj, re.IGNORECASE):
            rars.append(part)
        elif re.search(".rar", subj, re.IGNORECASE):
            rars.insert(0, part)
        elif re.search(".r\d\d*", subj, re.IGNORECASE):
            rars.append(part)
        else:
            other.append(part)
    parts = start + rars + pars
    if others:
        parts += other
    f = file(nzb, "wb")
    f.write("\n".join(parts) + "\n</nzb>")
    f.close()

######################################################################################################################################

#matrix = Matrix(username="MyUsername", apiKey="f70e1394d05be493069537a7d430297c")
#print matrix.Bookmarks("566252", BOOKMARK_ACTION_REMOVE)
#print matrix.Download("566252", "C:\\test")
#print matrix.Details("659980")
#  print matrix.Search("book of eli")

#for value in matrix.Search(query="34ferf34").values():
#    print value



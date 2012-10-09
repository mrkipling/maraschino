#you will need these
import datetime, getopt, sys, urllib, urllib2

#you can remove this one in your own script
import time

def main(argv):
    try:                                
        opts, args = getopt.getopt(argv, "ipsw:", ["ip=", "port=", "script_id=", "webroot="])
    except getopt.GetoptError:          
        sys.exit(2)  
        
    ip = None
    port = None
    script_id = None
    webroot = None
    for opt, arg in opts:
        if opt in ("-i", "--ip"):
            ip = arg              
        elif opt in ("-p", "--port"):
            port = arg               
        elif opt in ("-s", "--script_id"):
            script_id = arg          
        elif opt in ("-w", "--webroot"):
            webroot = arg
    
    wait_time = 15
    
    #this is just for testing so 
    update_status('Started Execution', ip, port, webroot, script_id)
    
    #wait for a while
    time.sleep(wait_time)
    update_status('Next part of Script', ip, port, webroot, script_id)
    
    #wait for a while
    time.sleep(wait_time)
    update_status('Doing more work', ip, port, webroot, script_id)
    
    #wait for a while
    time.sleep(wait_time)
    update_status('Going to smoke', ip, port, webroot, script_id)
    
    #wait for a while
    time.sleep(wait_time)
    update_status('Next part of Script', ip, port, webroot, script_id)
    
    #wait for a while
    time.sleep(wait_time)
    finished(ip, port, webroot, script_id)

    
def finished(ip=None, port=None, webroot=None, script_id=None):
    now = datetime.datetime.now()
    update_status("Last Ran: %s" % now.strftime("%m-%d-%Y %H:%M"), ip, port, webroot, script_id)

def update_status(status, ip=None, port=None, webroot=None, script_id=None):
    if script_id == None or ip == None or port == None:
        return 
    path='http://%s:%s%s/xhr/script_launcher/script_status/%s' % (ip, port, webroot, script_id)

    data = [('status', status)]
    data=urllib.urlencode(data)

    req=urllib2.Request(path, data)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    open=urllib2.urlopen(req)
    page = open.read()

if __name__ == '__main__':
    main(sys.argv[1:])
# Author: Mikie
# URL: https://github.com/Mikie-Ghost/

import logging
import logging.handlers
import sys
import os 
from settings import *
try:
	# Path for APACHE
    from Maraschino import rundir
    LOG_DIR = os.path.join(rundir, "logs/")
except:
	# Path for dev webserver
    LOG_DIR = './logs/'
    
# Level     When it is used

# DEBUG     Detailed information, typically of interest only when diagnosing problems.
# INFO      Confirmation that things are working as expected.
# WARNING   An indication that something unexpected happened. The software is still working as expected.
# ERROR     Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL  A serious error, indicating that the program itself may be unable to continue running.

# To use
#
# import logger
# logger.log('debug message', 'level')
#

# create the directory for the logs if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    
LOG_FILE = LOG_DIR + 'maraschino.log'


# set up formatting for console and the two log files
confor = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s', '%H:%M:%S')
warfor = logging.Formatter('%(asctime)s :: %(levelname)-8s :: %(message)s', '%b-%d %H:%M:%S')


# set up logging to STDOUT for all levels DEBUG and higher
con = logging.StreamHandler(sys.stdout)
con.setLevel(logging.DEBUG)
con.setFormatter(confor)

# set up logging to a file for all levels DEBUG and higher
war = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10000000, backupCount=3)
war.setLevel(logging.DEBUG)
war.setFormatter(warfor)

# create Logger object
mylogger = logging.getLogger('MAIN')
mylogger.setLevel(logging.DEBUG)
mylogger.addHandler(con)
mylogger.addHandler(war)

def log(toLog, logLevel):
    try:
        if logLevel == 'DEBUG':
            mylogger.debug(toLog)
        elif logLevel == 'INFO':
            mylogger.info(toLog)
        elif logLevel == 'WARNING':
            mylogger.warning(toLog)
        elif logLevel == 'ERROR':
            mylogger.error(toLog)
        elif logLevel == 'CRITICAL':
            mylogger.critical(toLog)
    except ValueError:
        pass 

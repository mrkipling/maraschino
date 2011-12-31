import sys, getopt

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import *

# check if database is given @ commandline
if sys.argv[1:]:
    opts, args = getopt.getopt(sys.argv[1:], "qp::", ['quiet', 'port=', 'database='])

    for o, a in opts:
        # check for development or cherrypy server
        if o in ('--database'):
            DATABASE = a

engine = create_engine('sqlite:///%s' % (DATABASE), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

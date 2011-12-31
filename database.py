try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
except ImportError:
    print 'flask-sqlalchemy is not installed (hint: easy_install flask-sqlalchemy)'
    quit()

from settings import *

engine = create_engine('sqlite:///%s' % (DATABASE), convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    static = Column(Boolean)
    column = Column(Integer)
    poll = Column(Integer)
    delay = Column(Integer)

    def __init__(self, name=None, static=0, column=None, poll=None, delay=None):
        self.name = name
        self.static = static
        self.column = column
        self.poll = poll
        self.delay = delay

    def __repr__(self):
        return '<Module %r>' % (self.name)

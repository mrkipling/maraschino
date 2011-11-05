from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    column = Column(Integer)
    position = Column(Integer)
    poll = Column(Integer)
    delay = Column(Integer)

    def __init__(self, name=None, static=0, column=None, position=None, poll=None, delay=None):
        self.name = name
        self.static = static
        self.column = column
        self.position = position
        self.poll = poll
        self.delay = delay

    def __repr__(self):
        return '<Module %r>' % (self.name)

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True)
    value = Column(String(500))

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<Setting %r>' % (self.key)

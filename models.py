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

    def __init__(self, name, column, position=None, poll=None, delay=None):
        self.name = name
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

    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    def __repr__(self):
        return '<Setting %r>' % (self.key)

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    url = Column(String(1000))
    description = Column(String(100))
    image = Column(String(100))
    position = Column(Integer)

    def __init__(self, name, url, description=None, image=None, position=None):
        self.name = name
        self.url = url
        self.description = description
        self.image = image

        if position == None:
            highest_position = 0
            applications = Application.query.all()

            for application in applications:
                if application.position > highest_position:
                    highest_position = application.position

            position = highest_position + 1

        self.position = position

    def __repr__(self):
        return '<Application %r>' % (self.name)

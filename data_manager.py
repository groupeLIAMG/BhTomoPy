from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from borehole import Borehole
from model import Model
from mog import Mog, AirShots

engine = create_engine("sqlite:///Database.db")

Base = declarative_base(bind=engine)

class boreholes(Base):
    
    __tablename__ = "boreholes"
    id = Column(Integer, primary_key=True)
    item = Column(Borehole)
    
class models(Base):
     
    __tablename__ = "models"
    id = Column(Integer, primary_key=True)
    item = Column(Model)
     
class MOGs(Base):
     
    __tablename__ = "MOGs"
    id = Column(Integer, primary_key=True)
    item = Column(Mog)
     
class air(Base):
     
    __tablename__ = "air"
    id = Column(Integer, primary_key=True)
    item = Column(AirShots)

Base.metadata.create_all(engine)


def get(item, file, Id=None):
    
    if file.find('.db') != -1:
        
        engine.url = "sqlite:///{}".format(file[0])
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        
        for i in [boreholes, models, MOGs, air]:
            
            if item == i.__tablename__:
                item = i
        
        if item is str:
            raise ValueError
        
        if Id == None:    
            return session.query(item).all()
        
        if Id is int:
            return session.query(item).filter(item.id == Id)
        
        if Id is list:
            return list(map(lambda x: session.query(item).filter(item.id == x), Id))
        
        else:
            raise TypeError
    
    else:
        raise FileNotFoundError

def save(itemss, file=None, overwrite=True):
    
    # receives a single list of objects or list of lists and saves it
    
    if file != None:
        if file.find('.db') != -1:
            
            engine.url = ("sqlite:///{}".format(file[0]))
        
        else:
            raise FileNotFoundError
    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    
    for items in itemss:
        
        try:
            
            for item in items:
                
                if overwrite:
                
                    session.delete(session.query(type(item)).filter(type(item).id == item.id))       
            
                session.add(item)
        
        except IndexError:
            #TODO: Is the overwriting necessary?
            if overwrite:
                
                session.delete(session.query(type(items)).filter(type(items).id == items.id))       
            
            session.add(items)
    
    session.commit()

def delete_all(file):
    
    #TODO: confirm box
    for i in [boreholes, models, MOGs, air]:
        
        if session.query(i).first(): # verifies that the table has contents
            
            for j in session.query(i).all():
                
                session.delete(j)
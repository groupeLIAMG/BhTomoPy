from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:")
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def get(item, Id=None):

    # item as class
    
    if Id == None:    
        return session.query(item).all()
    
    if Id is int:
        return session.query(item).filter(item.name == Id)
    
    if Id is list:
        return [session.query(item).filter(item.name == i) for i in Id]
    
    else:
        raise TypeError

def save(items):
    
    # receives a single list of objects or a list of lists and saves it
    
    if type(items[0]) is list:
    
        for item in items:
                
            session.bulk_save_objects(item)
    
    else:
                        
        session.bulk_save_objects(items)
            
    session.commit()
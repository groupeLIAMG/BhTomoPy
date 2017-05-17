from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from borehole import Borehole
from mog import Mog, AirShots
from model import Model
from utils import Base

def create_data_management(module):
    
    module.engine = create_engine("sqlite:///:memory:")
    module.Session = sessionmaker(bind=module.engine)
    module.session = module.Session()
    Base.metadata.create_all(module.engine)

def load(module, file):
    
    try:
        module.session.close()
        module.engine.dispose()
        
        module.engine  = create_engine("sqlite:///" + file)
        module.Session = sessionmaker(bind=module.engine)
        module.session = module.Session()
        Base.metadata.create_all(module.engine)
        
        get_many(module) # initiate the session's objects
        
    except AttributeError:
        create_data_management(module)
        load(module, file)
   
def save_as(module, file):
    
    try:
        items = get_many(module)
        
        module.session.close()
        module.engine.dispose()
        
        module.engine = create_engine("sqlite:///" + file)
        Base.metadata.create_all(module.engine)
        module.Session.configure(bind=module.engine)
        module.session = module.Session()
        
        for item in get_many(module):
            module.session.delete(item)
           
        items = [module.session.merge(item) for item in items]
        module.session.add_all(items)
         
        module.session.commit()
                
    except AttributeError:
        create_data_management(module)
        save_as(module, file)

def get(module, item, Id=None):

    # item as class
    
    if Id == None:
        return module.session.query(item).all()
    
    if Id is int:
        return module.session.query(item).filter(item.name == Id)
    
    if Id is list:
        return [module.session.query(item).filter(item.name == i) for i in Id]
    
    else:
        raise TypeError

def get_many(module, *classes):
    
    # also loads items into current session
    
    items = []
    
    if not classes:
        classes = (Borehole, Mog, AirShots, Model)
    
    for i in classes:
        
        items += get(module, i)
    
    return items

# import sys
# current_module = sys.modules[__name__]

# def save(items):
#     
#     # receives a single list of objects or a list of lists and saves it
#     
#     if type(items[0]) is list:
#     
#         for item in items:
#                 
#             session.bulk_save_objects(item)
#     
#     else:
#                         
#         session.bulk_save_objects(items)
#             
#     session.commit()

# Tests bank
#                     from sqlalchemy import inspect
#                     from sqlalchemy.engine import reflection
#                     from sqlalchemy.orm.session import sessionmaker
#                     print(reflection.Inspector.from_engine(data_manager.engine).get_table_names())
#                     print(items)
#                     print([i.__tablename__ for i in items])
#                     print(reflection.Inspector.from_engine(data_manager.session.get_bind()).get_table_names())
#                     print([sessionmaker.object_session(i) for i in items])
#                     print(data_manager.session)
#                     print([sessionmaker.object_session(i) for i in items])
#                     print(reflection.Inspector.from_engine(data_manager.session.get_bind()).get_table_names())
#                     print([i.__tablename__ for i in items])
#                     print(data_manager.session.get_bind().url)
#                     print([inspect(my_object) for my_object in items])
#                     data_manager.session.commit()
#                     print([inspect(my_object).persistent for my_object in items])
#                     print([i.__tablename__ for i in data_manager.session])
#                     print(data_manager.session.query(Borehole).all())
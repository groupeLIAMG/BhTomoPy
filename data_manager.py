from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:")
Base = declarative_base()
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

def get_many(*classes):
    
    # also loads items into current session
    
    items = []
    
    for i in classes:
        
        items += get(i)
    
    return items

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
# import sys
# import database
# import borehole
#  
# current_module = sys.modules[__name__]
# database.create_data_management(current_module)
#  
# current_module.session.add(borehole.Borehole())
# current_module.session.commit()
# print([item.name + '.bh' for item in current_module.session.query(borehole.Borehole).all()])
#  
# print([item.name + '.bh' for item in current_module.session])
#  
#  
# def change():
#     current_module.session.query(borehole.Borehole).first().X = 0
#     current_module.session.query(borehole.Borehole).first().X = 1
#     print(current_module.session.query(borehole.Borehole).first().X)
#  
#  
# change()
# print(current_module.session.query(borehole.Borehole).first().X)

if '':
    print('ok')

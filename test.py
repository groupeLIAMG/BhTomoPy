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
#
#
# import utils_ui
#
# test = ['a', 'b', 'b 1', 'b 2', 'b 4']
# print(utils_ui.duplicate_new_name('a', test))
# print(utils_ui.duplicate_new_name('b', test))
#
# print([for item in test])


# import inspect, dis
#
#
# def expecting():
#     """Return how many values the caller is expecting"""
#     f = inspect.currentframe()
#     f = f.f_back.f_back
#     c = f.f_code
#     i = f.f_lasti
#     bytecode = c.co_code
#     instruction = bytecode[i + 3]
#     if instruction == dis.opmap['UNPACK_SEQUENCE']:
#         howmany = bytecode[i + 4]
#         return howmany
#     elif instruction == dis.opmap['POP_TOP']:
#         return 0
#     return 1
#
#
# def cleverfunc():
#     howmany = expecting()
#     print(howmany)
#     if howmany == 0:
#         print("return value discarded")
#     if howmany == 2:
#         return 1, 2
#     elif howmany == 3:
#         return 1, 2, 3
#     return 1
#
#
# def test():
#     cleverfunc()
#     x = cleverfunc()
#     print(x)
#     x, y = cleverfunc()
#     print(x, y)
#     x, y, z = cleverfunc()
#     print(x, y, z)
#
#
# test()


import sys
import dis


def expecting():
    f = sys._getframe().f_back.f_back
    i = f.f_lasti + 3
    bytecode = f.f_code.co_code
    instruction = ord(str(bytecode[i]))
    while True:
        if instruction == dis.opmap['DUP_TOP']:
            if ord(bytecode[i + 1]) == dis.opmap['UNPACK_SEQUENCE']:
                return ord(bytecode[i + 2])
            i += 4
            instruction = ord(bytecode[i])
            continue
        if instruction == dis.opmap['STORE_NAME']:
            return 1
        if instruction == dis.opmap['UNPACK_SEQUENCE']:
            return ord(bytecode[i + 1])
        return 0


def test():
    def f():
        r = expecting()
        print(r)
        if r == 0:
            return None
        if r == 1:
            return 0
        return range(r)

    f()
    a = f()
    a, b = f()
    a, b = c = f()
    a, b = c = d = f()
    a = b = f()
    a = b, c = f()
    a = b = c, d = f()
    a = b, c = d = f()
    a, b = c, d = f()


test()

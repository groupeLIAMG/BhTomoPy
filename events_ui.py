'''
Created on august 31st, 2016

@author: giroux
'''

from PyQt5.QtCore import QEvent


# Boreholes
class BoreholeAdded(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(BoreholeAdded, self).__init__(BoreholeAdded._type)


class BoreholeDeleted(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(BoreholeDeleted, self).__init__(BoreholeDeleted._type)


class BoreholeEdited(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(BoreholeEdited, self).__init__(BoreholeEdited._type)


# Covariance
class CovarianceEdited(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(CovarianceEdited, self).__init__(CovarianceEdited._type)


# Grid
class GridEdited(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(GridEdited, self).__init__(GridEdited._type)


# Models
class ModelAdded(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(ModelAdded, self).__init__(ModelAdded._type)


class ModelDeleted(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(ModelDeleted, self).__init__(ModelDeleted._type)


class ModelEdited(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(ModelEdited, self).__init__(ModelEdited._type)


# Mogs
class MogAdded(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(MogAdded, self).__init__(MogAdded._type)


class MogDeleted(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(MogDeleted, self).__init__(MogDeleted._type)


class MogEdited(QEvent):
    _type = QEvent.registerEventType()

    def __init__(self):
        super(MogEdited, self).__init__(MogEdited._type)


if __name__ == '__main__':

    e = MogAdded()
    print(e.type())

    print(MogAdded._type == e.type())

    e = BoreholeAdded()
    print(e.type())

    print(BoreholeAdded._type == e.type())
    print(MogAdded._type == e.type())

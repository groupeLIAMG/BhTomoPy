import sys
from PyQt4 import QtGui, QtCore
from BoreholeUI2 import BoreholeUI
from ModelUI import ModelUI
from MogUI import MOGUI
from InfoUI import InfoUI


class DatabaseUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DatabaseUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Database")
        self.bh = BoreholeUI()
        self.bh.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Sunken)
        self.bh.setLineWidth(2)
        self.model = ModelUI()
        self.model.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Sunken)
        self.model.setLineWidth(2)
        self.mog = MOGUI()
        self.mog.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Sunken)
        self.mog.setLineWidth(2)
        self.info = InfoUI()
        self.info.setFrameStyle(QtGui.QFrame.Box|QtGui.QFrame.Sunken)
        self.info.setLineWidth(2)
        self.initUI()



    def initUI(self):
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(self.bh, 0, 0)
        master_grid.addWidget(self.mog, 0, 1)
        master_grid.addWidget(self.model, 1, 0)
        master_grid.addWidget(self.info, 1, 1)
        self.setLayout(master_grid)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Database_ui = DatabaseUI()
    Database_ui.show()

    sys.exit(app.exec_())
import sys
from PyQt4 import QtGui, QtCore


class InfoUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(InfoUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Info")
        self.initUI()

    def initUI(self):
        #--- Widget ---#
        info = QtGui.QTextEdit("Database")
        info.setReadOnly(True)
        #--- GroupBox ---#

        #--- Grid ---#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(info , 0, 0)
        self.setLayout(master_grid)




        print("coucou")
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Info_ui = InfoUI()
    Info_ui.show()

    sys.exit(app.exec_())
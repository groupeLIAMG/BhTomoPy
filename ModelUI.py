import sys
from PyQt4 import QtGui, QtCore


class MOGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MOGUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/MOGs")
        self.initUI()

    def initUI(self):

        #------- Widgets Creation -------#
        #--- Buttons Set ---#
        btn_Add_Model                 = QtGui.QPushButton("Add Model")
        btn_Remove_Model                 = QtGui.QPushButton("Remove Model")
        btn_Create                 = QtGui.QPushButton("Create")
        btn_Edit                = QtGui.QPushButton("Edit")
        btn_Add_MOG                 = QtGui.QPushButton("Add MOG")
        btn_Remove_MOG                 = QtGui.QPushButton("Remove MOG")
        #--- Lists ---#
        MOG_list   = QtGui.QListWidget()
        Model_list = QtGui.QListWidget()

        #--- Sub Widgets ---#
        #--- Models Sub Widget ---#
        Models_Sub_Widget =  QtGui.QWidget()
        Models_Sub_Grid   = QtGui.QGridLayout()
        Models_Sub_Grid.addWidget(btn_Add_Model, 0, 0, 1, 2)
        Models_Sub_Grid.addWidget(btn_Remove_Model, 0, 2, 1, 2)
        Models_Sub_Grid.addWidget(Model_list, 1, 0, 1, 4)
        Models_Sub_Widget.setLayout(Models_Sub_Grid)

        #--- Grid Sub Widget ---#
        Grid_Sub_Widget =  QtGui.QWidget()
        Grid_Sub_Grid   = QtGui.QGridLayout()
        Grid_Sub_Grid.addWidget(btn_Create, 0, 0)
        Grid_Sub_Grid.addWidget(btn_Edit, 0, 1)
        Grid_Sub_Widget.setLayout(Grid_Sub_Grid)

        #--- MOGS Sub Widget ---#
        MOGS_Sub_Widget =  QtGui.QWidget()
        MOGS_Sub_Grid   = QtGui.QGridLayout()
        MOGS_Sub_Grid.addWidget(btn_Add_MOG, 0, 0, 1, 2)
        MOGS_Sub_Grid.addWidget(btn_Remove_MOG, 0, 2, 1, 2)
        MOGS_Sub_Grid.addWidget(MOG_list, 1, 0, 1, 4)
        MOGS_Sub_Widget.setLayout(MOGS_Sub_Grid)



        #------- Grid Disposition -------#
        master_grid     = QtGui.QGridLayout()
        #--- Sub Widgets Disposition ---#
        master_grid.addWidget(Models_Sub_Widget, 0, 0)
        master_grid.addWidget(Grid_Sub_Widget, 1, 0)
        master_grid.addWidget(MOGS_Sub_Widget, 0, 1)


        self.setLayout(master_grid)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    MOGUI_ui = MOGUI()
    MOGUI_ui.show()

    sys.exit(app.exec_())

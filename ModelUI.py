import sys
from PyQt4 import QtGui, QtCore


class ModelUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(ModelUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Models")
        self.initUI()

    def initUI(self):

        #------- Widgets Creation -------#
        #--- Widget Link ---#
        self.model_Creation = Model_Creation()
        self.model_Removal  = Model_Removal()
        #--- Buttons Set ---#
        btn_Add_Model                 = QtGui.QPushButton("Add Model")
        btn_Remove_Model                 = QtGui.QPushButton("Remove Model")
        btn_Create_Grid                 = QtGui.QPushButton("Create Grid")
        btn_Edit_Grid                = QtGui.QPushButton("Edit Grid")
        btn_Add_MOG                 = QtGui.QPushButton("Add MOG")
        btn_Remove_MOG                 = QtGui.QPushButton("Remove MOG")
        #--- Buttons Actions ---#
        btn_Add_Model.clicked.connect(self.model_Creation.show)
        btn_Remove_Model.clicked.connect(self.model_Removal.show)
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
        Grid_Sub_Grid.addWidget(btn_Create_Grid, 0, 0)
        Grid_Sub_Grid.addWidget(btn_Edit_Grid, 0, 1)
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

class Model_Creation(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Model_Creation, self).__init__()
        self.setWindowTitle("Model Creation")
        self.setWindowFlags(QtCore.Qt.Window)
        self.initUI()

    #------- Widget Creation -------#
    def initUI(self):
        model_label             = QtGui.QLabel("Model Name")
        model_edit               = QtGui.QLineEdit()
        btn_ok                = QtGui.QPushButton("Ok")
        #------- Grid Creation -------#

        creation_grid = QtGui.QGridLayout()
        creation_grid.addWidget(model_label,0, 0 )
        creation_grid.addWidget(model_edit, 1, 0)
        creation_grid.addWidget(btn_ok, 1, 1)
        self.setLayout(creation_grid)

class Model_Removal(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Model_Removal, self).__init__()
        self.setWindowTitle("Model Removal")
        self.setWindowFlags(QtCore.Qt.Window)
        self.initUI()

    #------- Widget Creation -------#
    def initUI(self):
        model_label             = QtGui.QLabel("Model Name")
        model_edit               = QtGui.QLineEdit()
        btn_ok                = QtGui.QPushButton("Ok")
        #------- Grid Creation -------#

        creation_grid = QtGui.QGridLayout()
        creation_grid.addWidget(model_label,0, 0 )
        creation_grid.addWidget(model_edit, 1, 0)
        creation_grid.addWidget(btn_ok, 1, 1)
        self.setLayout(creation_grid)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = ModelUI()
    Model_ui.show()

    sys.exit(app.exec_())

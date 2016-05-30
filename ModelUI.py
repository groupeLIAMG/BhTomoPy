import sys
from PyQt4 import QtGui, QtCore


class ModelUI(QtGui.QWidget):
    #------- Signals Emitted -------#
    modelInfoSignal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(ModelUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Models")
        self.models = []
        self.initUI()

    def add_model(self):
        name, ok = QtGui.QInputDialog.getText(self, "Model creation", 'Model name')
        if ok :
            self.models.append(name)
        self.update_model_list()

    def del_model(self):
        ind = self.model_list.selectedIndexes()
        for i in ind:
            del self.models[int(i.row())]
        self.update_model_list()


    def update_model_list(self):
        self.model_list.clear()
        for model in self.models:
            self.model_list.addItem(model)
        self.modelInfoSignal.emit(len(self.model_list)) # we send the information to DatabaseUI

    def initUI(self):

        #------- Widgets Creation -------#

        #--- Buttons Set ---#
        btn_Add_Model                    = QtGui.QPushButton("Add Model")
        btn_Remove_Model                 = QtGui.QPushButton("Remove Model")
        btn_Create_Grid                  = QtGui.QPushButton("Create Grid")
        btn_Edit_Grid                    = QtGui.QPushButton("Edit Grid")
        btn_Add_MOG                      = QtGui.QPushButton("Add MOG")
        btn_Remove_MOG                   = QtGui.QPushButton("Remove MOG")
        #--- Buttons Actions ---#
        btn_Add_Model.clicked.connect(self.add_model)
        btn_Remove_Model.clicked.connect(self.del_model)

        #--- Lists ---#
        MOG_list                         = QtGui.QListWidget()
        self.model_list                       = QtGui.QListWidget()

        #--- Sub Widgets ---#
        #--- Models Sub Widget ---#
        Models_Sub_Widget                = QtGui.QWidget()
        Models_Sub_Grid                  = QtGui.QGridLayout()
        Models_Sub_Grid.addWidget(btn_Add_Model, 0, 0, 1, 2)
        Models_Sub_Grid.addWidget(btn_Remove_Model, 0, 2, 1, 2)
        Models_Sub_Grid.addWidget(self.model_list, 1, 0, 1, 4)
        Models_Sub_Widget.setLayout(Models_Sub_Grid)

        #--- Grid Sub Widget ---#
        Grid_GroupBox                    = QtGui.QGroupBox("Grid")
        Grid_Sub_Grid                    = QtGui.QGridLayout()
        Grid_Sub_Grid.addWidget(btn_Create_Grid, 0, 0)
        Grid_Sub_Grid.addWidget(btn_Edit_Grid, 0, 1)
        Grid_GroupBox.setLayout(Grid_Sub_Grid)

        #--- MOGS Sub Widget ---#
        MOGS_Groupbox                    = QtGui.QGroupBox("MOGs")
        MOGS_Sub_Grid                    = QtGui.QGridLayout()
        MOGS_Sub_Grid.addWidget(btn_Add_MOG, 0, 0, 1, 2)
        MOGS_Sub_Grid.addWidget(btn_Remove_MOG, 0, 2, 1, 2)
        MOGS_Sub_Grid.addWidget(MOG_list, 1, 0, 1, 4)
        MOGS_Groupbox.setLayout(MOGS_Sub_Grid)



        #------- Grid Disposition -------#
        master_grid                      = QtGui.QGridLayout()
        #--- Sub Widgets Disposition ---#
        master_grid.addWidget(Models_Sub_Widget, 0, 0)
        master_grid.addWidget(Grid_GroupBox, 1, 0)
        master_grid.addWidget(MOGS_Groupbox, 0, 1, 2, 1)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = ModelUI()
    Model_ui.show()

    sys.exit(app.exec_())

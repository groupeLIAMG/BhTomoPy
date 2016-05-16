import sys
from PyQt4 import QtGui, QtCore
from BoreholeUI import BoreholeUI
from ModelUI import ModelUI
from MogUI import MOGUI
from InfoUI import InfoUI


class DatabaseUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DatabaseUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Database")
        #--- Other Modules Instance ---#
        self.bh = BoreholeUI()
        self.model = ModelUI()
        self.mog = MOGUI()
        self.info = InfoUI()
        self.initUI()



    def initUI(self):
        #--- MenuBar ---#

        #--- GroupBoxes ---#

        #- Boreholes GroupBox -#
        bh_GroupBox =  QtGui.QGroupBox("Boreholes")
        bh_Sub_Grid   = QtGui.QGridLayout()
        bh_Sub_Grid.addWidget(self.bh)
        bh_GroupBox.setLayout(bh_Sub_Grid)

        #- MOGs GroupBox -#
        MOGs_GroupBox =  QtGui.QGroupBox("MOGs")
        MOGs_Sub_Grid   = QtGui.QGridLayout()
        MOGs_Sub_Grid.addWidget(self.mog)
        MOGs_GroupBox.setLayout(MOGs_Sub_Grid)

        #- Models GroupBox -#
        Models_GroupBox =  QtGui.QGroupBox("Models")
        Models_Sub_Grid   = QtGui.QGridLayout()
        Models_Sub_Grid.addWidget(self.model)
        Models_GroupBox.setLayout(Models_Sub_Grid)

        #- Info GroupBox -#
        Info_GroupBox =  QtGui.QGroupBox("Infos")
        Info_Sub_Grid   = QtGui.QGridLayout()
        Info_Sub_Grid.addWidget(self.info)
        Info_GroupBox.setLayout(Info_Sub_Grid)

        #--- Grid ---#
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(bh_GroupBox, 0, 0)
        master_grid.addWidget(MOGs_GroupBox, 0, 1)
        master_grid.addWidget(Models_GroupBox, 1, 0)
        master_grid.addWidget(Info_GroupBox, 1, 1)
        self.setLayout(master_grid)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Database_ui = DatabaseUI()
    Database_ui.show()

    sys.exit(app.exec_())
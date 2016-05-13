import sys
from PyQt4 import QtGui, QtCore
from DatabaseUI import DatabaseUI


class Bh_ThomoPyUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(Bh_ThomoPyUI, self).__init__()
        self.setWindowTitle("bh_thomoPy")
        self.initUI()

    def initUI(self):
        self.database_pop = Database_Pop()
        #--- Widgets ---#
        btn_Database = QtGui.QPushButton("Database")
        btn_Automatic_Traveltime_Picking = QtGui.QPushButton("Manual Traveltime Picking")
        btn_Semi_Automatic_Traveltime_Picking = QtGui.QPushButton("Semi-Automatic Traveltime Picking (x-corr)")
        btn_Manual_Traveltime_Picking = QtGui.QPushButton("Manual Traveltime Picking")
        btn_Manual_Amplitude_Picking = QtGui.QPushButton("Manual Traveltime Picking")
        btn_Cov_Mod = QtGui.QPushButton("Covariance Model")
        btn_Inversion = QtGui.QPushButton("Inversion")
        btn_Interpretation = QtGui.QPushButton("Interpretation (GPR)")
        btn_Time_Lapse_Inversion = QtGui.QPushButton("Time-Lapse Inversion")
        btn_Time_Lapse_Visualisation = QtGui.QPushButton("Time-Lapse Visualisation")
        btn_Nano_Fluid = QtGui.QPushButton("Magnetic Nano Fluid Saturation")


        btn_Database.clicked.connect(self.database_pop.show)
        #--- GroupBox ---#
        bh_tomo_GroupBox = QtGui.QGroupBox("BH THOMO")
        bh_tomo_Sub_Grid   = QtGui.QGridLayout()
        bh_tomo_Sub_Grid.addWidget(btn_Database, 0, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Automatic_Traveltime_Picking, 1, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Semi_Automatic_Traveltime_Picking, 2, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Manual_Traveltime_Picking, 3, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Manual_Amplitude_Picking, 4, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Cov_Mod, 5, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Inversion, 6, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Interpretation, 7, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Time_Lapse_Inversion, 8, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Time_Lapse_Visualisation, 9, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Nano_Fluid, 10, 0, 1, 4)
        bh_tomo_GroupBox.setLayout(bh_tomo_Sub_Grid)
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(bh_tomo_GroupBox, 0, 0)
        self.setLayout(master_grid)


class Database_Pop(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Database_Pop, self).__init__()
        self.setWindowTitle("Bh_thomoPy/Database")
        self.setWindowFlags(QtCore.Qt.Window)
        self.initUI()

        #------- Widget Creation -------#
    def initUI(self):
        self.database = DatabaseUI()
        #------- Grid Creation -------#

        creation_grid = QtGui.QGridLayout()
        creation_grid.addWidget(self.database)
        self.setLayout(creation_grid)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Bh_ThomoPy_ui = Bh_ThomoPyUI()
    Bh_ThomoPy_ui.show()

    sys.exit(app.exec_())

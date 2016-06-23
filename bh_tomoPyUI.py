import sys
from PyQt4 import QtGui, QtCore
from DatabaseUI import DatabaseUI
from manual_ttUI import ManualttUI
from covarUI import CovarUI
from inversionUI import InversionUI
from interpUI import InterpretationUI
from semi_auto_ttUI import SemiAutottUI

class Bh_ThomoPyUI(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Bh_ThomoPyUI, self).__init__()
        self.setWindowTitle("bh_thomoPy")
        self.initUI()

    def initUI(self):
        self.database = DatabaseUI()
        self.manual_tt = ManualttUI()
        self.semi_tt = SemiAutottUI()
        self.covar = CovarUI()
        self.inv = InversionUI()
        self.interp = InterpretationUI()
        #------- Widgets -------#
        #--- Buttons ---#
        btn_Database = QtGui.QPushButton("Database")
        btn_Automatic_Traveltime_Picking = QtGui.QPushButton("Automatic Traveltime Picking (AIC-CWT)")
        btn_Semi_Automatic_Traveltime_Picking = QtGui.QPushButton("Semi-Automatic Traveltime Picking (x-corr)")
        btn_Manual_Traveltime_Picking = QtGui.QPushButton("Manual Traveltime Picking")
        btn_Manual_Amplitude_Picking = QtGui.QPushButton("Manual Amplitude Picking")
        btn_Cov_Mod = QtGui.QPushButton("Covariance Model")
        btn_Inversion = QtGui.QPushButton("Inversion")
        btn_Interpretation = QtGui.QPushButton("Interpretation (GPR)")
        btn_Time_Lapse_Inversion = QtGui.QPushButton("Time-Lapse Inversion")
        btn_Time_Lapse_Visualisation = QtGui.QPushButton("Time-Lapse Visualisation")
        btn_Nano_Fluid = QtGui.QPushButton("Magnetic Nano Fluid Saturation")

        #--- Label ---#
        Title = QtGui.QLabel('BH TOMO \n Borehole Radar/Seismic Data Processing Center')
        Title.setAlignment(QtCore.Qt.AlignHCenter)
        Title.setContentsMargins(10, 10, 10, 30)
        Title.setStyleSheet('color: Darkcyan')
        serifFont = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        Title.setFont(serifFont)


        btn_Database.clicked.connect(self.database.show)
        btn_Manual_Traveltime_Picking.clicked.connect(self.manual_tt.showMaximized)
        btn_Semi_Automatic_Traveltime_Picking.clicked.connect(self.semi_tt.showMaximized)
        btn_Cov_Mod.clicked.connect(self.covar.show)
        btn_Inversion.clicked.connect(self.inv.show)
        btn_Interpretation.clicked.connect(self.interp.show)


        btn_Automatic_Traveltime_Picking.setDisabled(True)
        btn_Manual_Amplitude_Picking.setDisabled(True)
        btn_Time_Lapse_Inversion.setDisabled(True)
        btn_Time_Lapse_Visualisation.setDisabled(True)
        btn_Nano_Fluid.setDisabled(True)
        #--- Main Widget---#
        bh_tomo = QtGui.QWidget()
        bh_tomo_Sub_Grid   = QtGui.QGridLayout()
        bh_tomo_Sub_Grid.addWidget(Title, 0, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Database, 2, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Automatic_Traveltime_Picking, 3, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Semi_Automatic_Traveltime_Picking, 4, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Manual_Traveltime_Picking, 5, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Manual_Amplitude_Picking, 6, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Cov_Mod, 7, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Inversion, 8, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Interpretation, 9, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Time_Lapse_Inversion, 10, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Time_Lapse_Visualisation, 11, 0, 1, 4)
        bh_tomo_Sub_Grid.addWidget(btn_Nano_Fluid, 12, 0, 1, 4)
        bh_tomo.setLayout(bh_tomo_Sub_Grid)
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(bh_tomo, 0, 0)
        self.setLayout(master_grid)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Bh_ThomoPy_ui = Bh_ThomoPyUI()
    Bh_ThomoPy_ui.show()

    sys.exit(app.exec_())

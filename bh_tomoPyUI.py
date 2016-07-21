import sys
from PyQt4 import QtGui, QtCore
from DatabaseUI import DatabaseUI
from manual_ttUI import ManualttUI
from covarUI import CovarUI
from inversionUI import InversionUI
from interpUI import InterpretationUI
from semi_auto_ttUI import SemiAutottUI
import os

class Bh_ThomoPyUI(QtGui.QWidget):

    def __init__(self, parent=None):
        super(Bh_ThomoPyUI, self).__init__()
        self.setWindowTitle("bh_thomoPy")
        self.database = DatabaseUI()
        self.manual_tt = ManualttUI()
        self.semi_tt = SemiAutottUI()
        self.covar = CovarUI()
        self.inv = InversionUI()
        self.interp = InterpretationUI()
        self.initUI()

    def choosedb(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Choose Database')

        self.laoddb(filename)

    def laoddb(self, filename):
        # We create a load db methods to be able to load databases in the main
        rname = filename.split('/')
        rname = rname[-1]
        if '.p' in rname:
            rname = rname[:-2]
        if '.pkl' in rname:
            rname = rname[:-4]
        if '.pickle' in rname:
            rname = rname[:-7]

        self.current_db.setText(str(rname))
        self.database.load_file(filename)

    def show(self):
        super(Bh_ThomoPyUI, self).show()

        # Get initial geometry of the widget:
        qr = self.frameGeometry()

        # Show it at the center of the screen
        cp = QtGui.QDesktopWidget().availableGeometry().center()

        # Move the window's center at the center of the screen
        qr.moveCenter(cp)

        # Then move it at the top left
        translation = qr.topLeft()

        self.move(translation)

    def initUI(self):

        #------- Widgets -------#
        # --- Actions ---#
        ChooseDbAction = QtGui.QAction('Choose Database', self)
        ChooseDbAction.setShortcut('Ctrl+O')
        ChooseDbAction.triggered.connect(self.choosedb)

        ConvertDbAction = QtGui.QAction('Convert Database', self)
        ConvertDbAction.setShortcut('Ctrl+C')

        #--- Menubar ---#
        self.menu = QtGui.QMenuBar()
        filemenu = self.menu.addMenu('&File')
        editmenu = self.menu.addMenu('&Edit')
        filemenu.addAction(ChooseDbAction)
        editmenu.addAction(ConvertDbAction)


        #--- Buttons ---#
        btn_Database                            = QtGui.QPushButton("Database")
        btn_Automatic_Traveltime_Picking        = QtGui.QPushButton("Automatic Traveltime Picking (AIC-CWT)")
        btn_Semi_Automatic_Traveltime_Picking   = QtGui.QPushButton("Semi-Automatic Traveltime Picking (x-corr)")
        btn_Manual_Traveltime_Picking           = QtGui.QPushButton("Manual Traveltime Picking")
        btn_Manual_Amplitude_Picking            = QtGui.QPushButton("Manual Amplitude Picking")
        btn_Cov_Mod                             = QtGui.QPushButton("Covariance Model")
        btn_Inversion                           = QtGui.QPushButton("Inversion")
        btn_Interpretation                      = QtGui.QPushButton("Interpretation (GPR)")
        btn_Time_Lapse_Inversion                = QtGui.QPushButton("Time-Lapse Inversion")
        btn_Time_Lapse_Visualisation            = QtGui.QPushButton("Time-Lapse Visualisation")
        btn_Nano_Fluid                          = QtGui.QPushButton("Magnetic Nano Fluid Saturation")

        #- Buttons Disposition -#
        btn_Automatic_Traveltime_Picking.setDisabled(True)
        btn_Manual_Amplitude_Picking.setDisabled(True)
        btn_Time_Lapse_Inversion.setDisabled(True)
        btn_Time_Lapse_Visualisation.setDisabled(True)
        btn_Nano_Fluid.setDisabled(True)

        #- Buttons Actions -#
        btn_Database.clicked.connect(self.database.show)
        btn_Manual_Traveltime_Picking.clicked.connect(self.manual_tt.showMaximized)
        btn_Semi_Automatic_Traveltime_Picking.clicked.connect(self.semi_tt.showMaximized)
        btn_Cov_Mod.clicked.connect(self.covar.show)
        btn_Inversion.clicked.connect(self.inv.show)
        btn_Interpretation.clicked.connect(self.interp.show)

        #--- Image ---#
        pic = QtGui.QPixmap(os.getcwd() + "/BH TOMO2.png")
        image_label = QtGui.QLabel()
        image_label.setPixmap(pic.scaled(250, 250, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.FastTransformation))
        image_label.setAlignment(QtCore.Qt.AlignCenter)

        #--- Title(if logo isnt ok) ---#
        Title = QtGui.QLabel('BH TOMO \n Borehole Radar/Seismic Data Processing Center')
        Title.setAlignment(QtCore.Qt.AlignHCenter)
        Title.setContentsMargins(10, 10, 10, 30)
        Title.setStyleSheet('color: Darkcyan')
        serifFont = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
        Title.setFont(serifFont)

        #--- Edit ---#
        # Edit to hold the chosen database's name
        self.current_db = QtGui.QLineEdit()

        #- Edit Disposition -#
        self.current_db.setReadOnly(True)
        self.current_db.setAlignment(QtCore.Qt.AlignHCenter)

        #--- Image SubWidget ---#
        sub_image_widget = QtGui.QWidget()
        sub_image_grid = QtGui.QGridLayout()
        sub_image_grid.addWidget(image_label, 0, 0)
        sub_image_grid.setContentsMargins(50, 0, 50, 0)
        sub_image_widget.setLayout(sub_image_grid)
        #--- Buttons SubWidget ---#
        Sub_button_widget = QtGui.QGroupBox()
        sub_button_grid = QtGui.QGridLayout()
        sub_button_grid.addWidget(btn_Database, 0, 0)
        sub_button_grid.addWidget(btn_Automatic_Traveltime_Picking, 1, 0)
        sub_button_grid.addWidget(btn_Semi_Automatic_Traveltime_Picking, 2, 0)
        sub_button_grid.addWidget(btn_Manual_Traveltime_Picking, 3, 0)
        sub_button_grid.addWidget(btn_Manual_Amplitude_Picking, 4, 0)
        sub_button_grid.addWidget(btn_Cov_Mod, 5, 0)
        sub_button_grid.addWidget(btn_Inversion, 6, 0)
        sub_button_grid.addWidget(btn_Interpretation, 7, 0)
        sub_button_grid.addWidget(btn_Time_Lapse_Inversion, 8, 0)
        sub_button_grid.addWidget(btn_Time_Lapse_Visualisation, 9, 0)
        sub_button_grid.addWidget(btn_Nano_Fluid, 10, 0)
        Sub_button_widget.setLayout(sub_button_grid)

        #--- Main Widget---#
        bh_tomo = QtGui.QWidget()
        master_grid   = QtGui.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0, 1, 4)
        master_grid.addWidget(sub_image_widget, 2, 0, 1, 4)
        master_grid.addWidget(self.current_db, 3, 1, 1, 2)
        master_grid.addWidget(Sub_button_widget, 4, 0, 1, 4)
        master_grid.setContentsMargins(0, 0, 0, 0)
        master_grid.setVerticalSpacing(3)


        self.setLayout(master_grid)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Bh_ThomoPy_ui = Bh_ThomoPyUI()
    Bh_ThomoPy_ui.show()

    sys.exit(app.exec_())

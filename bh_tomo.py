# -*- coding: utf-8 -*-

"""
Copyright 2016 Bernard Giroux, Elie Dumas-Lefebvre
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it /will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from PyQt4 import QtGui, QtCore
from database_ui import DatabaseUI
from manual_tt_ui import ManualttUI
from covar_ui import CovarUI
from inversion_ui import InversionUI
from interp_ui import InterpretationUI
from semi_auto_tt_ui import SemiAutottUI
from manual_amp_ui import ManualAmpUI
import os


class BhTomoPy(QtGui.QWidget):

    def __init__(self, parent=None):
        super(BhTomoPy, self).__init__()
        self.setWindowTitle("BhTomoPy")

        self.database = DatabaseUI()
        self.manual_tt = ManualttUI()
        self.semi_tt = SemiAutottUI()
        self.covar = CovarUI()
        self.inv = InversionUI()
        self.interp = InterpretationUI()
        self.manual_amp = ManualAmpUI()
        self.initUI()

        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Minimum)

    def choosedb(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Choose Database')
        if filename is not '':
            if '.db' in filename:
                filename = filename[:-3]
            self.loaddb(filename)

    def loaddb(self, filename):
        # We create a load db methods to be able to load databases in the main
        rname = os.path.basename(filename)
        self.current_db.setText(rname)

        self.database.filename = filename
        self.manual_tt.filename = filename
        self.manual_amp.filename = filename
        self.inv.filename = filename

    def show(self):
        super(BhTomoPy, self).show()

        # Get initial geometry of the widget:
        qr = self.frameGeometry()

        # Show it at the center of the screen
        cp = QtGui.QDesktopWidget().availableGeometry().center()

        # Move the window's center at the center of the screen
        qr.moveCenter(cp)

        # Then move it at the top left
        translation = qr.topLeft()

        self.move(translation)

        self.setFixedSize(self.size())
        self.__h1 = self.size().height()
        self.__h2 = self.tt_tool.size().height() + self.tl_tool.size().height()

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
        btn_Automatic_Traveltime_Picking        = QtGui.QPushButton("Automatic (AIC-CWT)")
        btn_Semi_Automatic_Traveltime_Picking   = QtGui.QPushButton("Semi-Automatic (x-corr)")
        btn_Manual_Traveltime_Picking           = QtGui.QPushButton("Manual")
        btn_Manual_Amplitude_Picking            = QtGui.QPushButton("Manual Amplitude Picking")
        btn_Cov_Mod                             = QtGui.QPushButton("Covariance Model")
        btn_Inversion                           = QtGui.QPushButton("Inversion")
        btn_Interpretation                      = QtGui.QPushButton("Interpretation (GPR)")
        btn_Time_Lapse_Inversion                = QtGui.QPushButton("Inversion")
        btn_Time_Lapse_Visualisation            = QtGui.QPushButton("Visualisation")
        btn_Nano_Fluid                          = QtGui.QPushButton("Magnetic Nano Fluid Saturation")

        #- Buttons Disposition -#
        btn_Automatic_Traveltime_Picking.setDisabled(True)
        btn_Time_Lapse_Inversion.setDisabled(True)
        btn_Time_Lapse_Visualisation.setDisabled(True)
        #btn_Nano_Fluid.setDisabled(True)

        #- Buttons Actions -#
        btn_Database.clicked.connect(self.database.show)
        btn_Manual_Traveltime_Picking.clicked.connect(self.manual_tt.showMaximized)
        btn_Semi_Automatic_Traveltime_Picking.clicked.connect(self.semi_tt.showMaximized)
        btn_Cov_Mod.clicked.connect(self.covar.show)
        btn_Inversion.clicked.connect(self.inv.show)
        btn_Interpretation.clicked.connect(self.interp.show)
        btn_Manual_Amplitude_Picking.clicked.connect(self.manual_amp.showMaximized)

        #--- Image ---#
        pic = QtGui.QPixmap(os.getcwd() + "/BH TOMO2.png")
        image_label = QtGui.QLabel()
        image_label.setPixmap(pic.scaled(250, 250,
                                         QtCore.Qt.IgnoreAspectRatio,
                                         QtCore.Qt.FastTransformation))
        image_label.setAlignment(QtCore.Qt.AlignCenter)

        #--- Title(if logo isnt ok) ---#
        Title = QtGui.QLabel(
            'BH TOMO \n Borehole Radar/Seismic Data Processing Center')
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
        #--- Traveltime ToolBox ---#
        travel_time_tool = QtGui.QWidget()
        travel_time_grid = QtGui.QGridLayout()
        travel_time_grid.addWidget(btn_Manual_Traveltime_Picking, 0, 0)
        travel_time_grid.addWidget(btn_Semi_Automatic_Traveltime_Picking, 1, 0)
        travel_time_grid.addWidget(btn_Automatic_Traveltime_Picking, 2, 0)
        travel_time_tool.setLayout(travel_time_grid)

        #--- Time Lapse Tool ---#
        time_lapse_tool = QtGui.QWidget()
        time_lapse_grid = QtGui.QGridLayout()
        time_lapse_grid.addWidget(btn_Time_Lapse_Inversion)
        time_lapse_grid.addWidget(btn_Time_Lapse_Visualisation)
        time_lapse_tool.setLayout(time_lapse_grid)

        #--- Traveltime ToolBox ---#
        tt_tool = MyQToolBox()
        tt_tool.setIcons(QtGui.QIcon('Icons/triangle_right.png'),
                              QtGui.QIcon('Icons/triangle_down.png'))
        tt_tool.addItem(travel_time_tool, 'Travel Time Picking')
        tt_tool.sizeChanged.connect(self.fitHeight)
        self.tt_tool = tt_tool

        #--- Time Lapse ToolBox ---#
        tl_tool = MyQToolBox()
        tl_tool.setIcons(QtGui.QIcon('Icons/triangle_right.png'),
                              QtGui.QIcon('Icons/triangle_down.png'))
        tl_tool.addItem(time_lapse_tool, 'Time Lapse')
        tl_tool.sizeChanged.connect(self.fitHeight)
        self.tl_tool = tl_tool

        #--- Buttons SubWidget ---#
        Sub_button_widget = QtGui.QGroupBox()
        sub_button_grid = QtGui.QGridLayout()
        sub_button_grid.addWidget(btn_Database, 0, 0)
        sub_button_grid.addWidget(tt_tool, 1, 0)
        sub_button_grid.addWidget(btn_Manual_Amplitude_Picking, 2, 0)
        sub_button_grid.addWidget(btn_Cov_Mod, 3, 0)
        sub_button_grid.addWidget(btn_Inversion, 4, 0)
        sub_button_grid.addWidget(tl_tool, 5, 0)
        sub_button_grid.addWidget(btn_Interpretation, 6, 0)
        sub_button_grid.addWidget(btn_Nano_Fluid, 7, 0)
        sub_button_grid.setRowStretch(8, 100)
        Sub_button_widget.setLayout(sub_button_grid)

        #--- Main Widget---#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0, 1, 4)
        master_grid.addWidget(sub_image_widget, 2, 0, 1, 4)
        master_grid.addWidget(self.current_db, 3, 1, 1, 2)
        master_grid.addWidget(Sub_button_widget, 4, 0, 1, 4)
        master_grid.setContentsMargins(0, 0, 0, 0)
        master_grid.setVerticalSpacing(3)

        self.setLayout(master_grid)

    def fitHeight(self, x):
        # shrink or expand height to fit the toolbox
        h = self.__h1 + x - self.__h2
        self.setFixedHeight(h)


class MyQToolBox(QtGui.QWidget):

    """
    A custom widget that mimicks the behavior of the "Tools" sidepanel in
    Adobe Acrobat. It is derived from a QToolBox with the following variants:

    1. Only one tool can be displayed at a time.
    2. Unlike the stock QToolBox widget, it is possible to hide all the tools.
    3. It is also possible to hide the current displayed tool by clicking on
       its header.
    4. The tools that are hidden are marked by a right-arrow icon, while the
       tool that is currently displayed is marked with a down-arrow icon.
    5. Closed and Expanded arrows can be set from custom icons.
    """
# =============================================================================

    sizeChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super(MyQToolBox, self).__init__(parent)

        self.__iclosed = QtGui.QWidget().style().standardIcon(
            QtGui.QStyle.SP_ToolBarHorizontalExtensionButton)
        self.__iexpand = QtGui.QWidget().style().standardIcon(
            QtGui.QStyle.SP_ToolBarVerticalExtensionButton)

        self.setLayout(QtGui.QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.__currentIndex = -1

    def setIcons(self, ar_right, ar_down):  # =================================
        self.__iclosed = ar_right
        self.__iexpand = ar_down

    def addItem(self, tool, text):  # =========================================

        N = self.layout().rowCount()

        #---- Add Header ----

        head = QtGui.QPushButton(text)
        head.setIcon(self.__iclosed)
        head.clicked.connect(self.__isClicked__)
        head.setStyleSheet("QPushButton {text-align:left;}")

        self.layout().addWidget(head, N-1, 0)

        #---- Add Item in a ScrollArea ----

        scrollarea = QtGui.QScrollArea()
        scrollarea.setFrameStyle(0)
        scrollarea.hide()
        scrollarea.setStyleSheet("QScrollArea {background-color:transparent;}")
        scrollarea.setWidgetResizable(True)

        tool.setObjectName("myViewport")
        tool.setStyleSheet("#myViewport {background-color:transparent;}")
        scrollarea.setWidget(tool)

        self.layout().addWidget(scrollarea, N, 0)
        self.layout().setRowStretch(N+1, 100)

    def __isClicked__(self):  # ===============================================

        for row in range(0, self.layout().rowCount()-1, 2):

            head = self.layout().itemAtPosition(row, 0).widget()
            tool = self.layout().itemAtPosition(row+1, 0).widget()

            if head == self.sender():
                if self.__currentIndex == row:
                    # if clicked tool is open, close it
                    head.setIcon(self.__iclosed)
                    tool.hide()
                    self.__currentIndex = -1

                else:
                    # if clicked tool is closed, expand it
                    head.setIcon(self.__iexpand)
                    tool.show()
                    self.__currentIndex = row

            else:
                # close all the other tools so that only one tool can be
                # expanded at a time.
                head.setIcon(self.__iclosed)
                tool.hide()

        self.sizeChanged.emit(self.sizeHint().height())


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    bh_tomo = BhTomoPy()
    bh_tomo.show()

    sys.exit(app.exec_())

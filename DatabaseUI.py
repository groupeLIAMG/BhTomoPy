# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from BoreholeUI import BoreholeUI
from ModelUI import ModelUI
from MogUI import MOGUI, MergeMog
from InfoUI import InfoUI
from MogData import MogData
import time

class DatabaseUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DatabaseUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Database")
        #--- Other Modules Instance ---#
        self.actual_time = time.asctime()[11:16]
        self.bh = BoreholeUI()
        self.mog = MOGUI(self.bh)
        self.model = ModelUI(borehole=self.bh, mog=self.mog)
        self.info = InfoUI()
        self.mogdata = MogData()
        self.mergemog = MergeMog(self.mog.MOGs)
        self.initUI()
        self.action_list = []

        # DatabaseUI receives the signals, which were emitted by different modules, and transmits the signal to the other
        # modules in order to update them

        self.bh.bhUpdateSignal.connect(self.update_MogUI)
        self.bh.bhInfoSignal.connect(self.update_borehole_info)
        self.mog.mogInfoSignal.connect(self.update_mog_info)
        self.mog.ntraceSignal.connect(self.update_trace_info)
        self.mog.databaseSignal.connect(self.update_database_info)
        self.model.modelInfoSignal.connect(self.update_model_info)
        self.bh.bhlogSignal.connect(self.update_log)
        self.mog.moglogSignal.connect(self.update_log)
        self.model.modellogSignal.connect(self.update_log)
        self.mergemog.mergemoglogSignal.connect(self.update_log)

    def update_spectra(self, Tx_list):
        self.mog.update_spectra_Tx_num_combo(Tx_list)
        self.mog.update_spectra_Tx_elev_value_label(Tx_list)


    def update_MogUI(self, list_bh):
        self.mog.update_Tx_and_Rx_Widget(list_bh)


    def update_database_info(self, name):
        self.info.update_database(name)

    def update_borehole_info(self, num):
        self.info.update_borehole(num)

    def update_mog_info(self, num):
        self.info.update_mog(num)

    def update_model_info(self, num):
        self.info.update_model(num)

    def update_trace_info(self, num):
        self.info.update_trace(num)

    def update_log(self, action):
        # Clear the log to make sure any action is not written more than once
        self.log.clear()

        # Append the time and the action that was done
        self.action_list.append("[{}] {} " .format(self.actual_time, action))

        # Put the Error messages in red and the others in black
        for item in self.action_list:

            if "Error: " in item:
                self.log.setTextColor(QtGui.QColor(QtCore.Qt.red))
                self.log.append(item)

            else:
                self.log.setTextColor(QtGui.QColor(QtCore.Qt.black))
                self.log.append(item)


    def show(self):
        super(DatabaseUI, self).show()

        # Get initial geometry of the widget:
        qr = self.frameGeometry()

        # Show it at the center of the screen
        cp = QtGui.QDesktopWidget().availableGeometry().center()

        # Move the window's center at the center of the screen
        qr.moveCenter(cp)

        # Then move it at the top left
        translation = qr.topLeft()

        self.move(translation)

    def openfile(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Database')

    def saveasfile(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Database as ...')

    def save(self):
        # TODO
        pass

    def initUI(self):

        #--- Log Widget ---#
        self.log = QtGui.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(0)

        #--- Actions ---#
        openAction = QtGui.QAction('Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openfile)

        saveAction = QtGui.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')

        saveasAction = QtGui.QAction('Save as', self)
        saveasAction.setShortcut('Ctrl+A')
        saveasAction.triggered.connect(self.saveasfile)


        #--- Menubar ---#
        self.menu = QtGui.QMenuBar()
        filemenu = self.menu.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(saveasAction)


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
        master_grid.addWidget(self.menu, 0, 0, 1, 3)
        master_grid.addWidget(bh_GroupBox, 1, 0)
        master_grid.addWidget(MOGs_GroupBox, 1, 1, 1, 2)
        master_grid.addWidget(Models_GroupBox, 2, 0, 1, 2)
        master_grid.addWidget(Info_GroupBox, 2, 2)
        master_grid.addWidget(self.log, 3, 0, 2, 3)
        master_grid.setVerticalSpacing(3)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)

class MyLogWidget(QtGui.QTextEdit):
    def __init__(self, parent =None):
        super(MyLogWidget, self).__init__(parent)

    def append(self, txt):
        super(MyLogWidget, self).append(txt)

        bottom = self.verticalScrollBar().maximum()
        self.verticalScrollBar().setValue(bottom)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Database_ui = DatabaseUI()
    Database_ui.action_list.append("[{}] Welcome to BH_TOMO Py " .format(Database_ui.actual_time))
    Database_ui.bh.load_bh('testData/testConstraints/F3.xyz')
    Database_ui.bh.load_bh('testData/testConstraints/F2.xyz')
    Database_ui.mog.load_file_MOG('testData/formats/ramac/t0302.rad')

    Database_ui.show()


    sys.exit(app.exec_())
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
from BoreholeUI import BoreholeUI
from ModelUI import ModelUI, gridEditor
from MogUI import MOGUI, MergeMog
from InfoUI import InfoUI
from MogData import MogData
import time
import matplotlib.image as mpimg
import pickle

class DatabaseUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DatabaseUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Database")
        #--- Other Modules Instance ---#
        self.actual_time = time.asctime()[11:16]
        self.bh = BoreholeUI()
        self.mog = MOGUI(self.bh)
        self.model = ModelUI(borehole=self.bh, mog=self.mog)
        self.grid = gridEditor(self.model)
        self.info = InfoUI()
        self.mergemog = MergeMog(self.mog.MOGs)
        self.initUI()
        self.action_list = []
        self.filename = ''
        self.name = ''
        self.models = self.model.models
        self.boreholes = self.bh.boreholes
        self.mogs = self.mog.MOGs
        self.air = self.mog.air

        # DatabaseUI receives the signals, which were emitted by different modules, and transmits the signal to the other
        # modules in order to update them

        self.bh.bhUpdateSignal.connect(self.update_MogUI)
        self.bh.bhInfoSignal.connect(self.update_borehole_info)
        self.mog.mogInfoSignal.connect(self.update_mog_info)
        self.mog.ntraceSignal.connect(self.update_trace_info)
        self.model.modelInfoSignal.connect(self.update_model_info)
        self.mergemog.mergemoglogSignal.connect(self.update_log)
        self.bh.bhlogSignal.connect(self.update_log)
        self.mog.moglogSignal.connect(self.update_log)
        self.model.modellogSignal.connect(self.update_log)


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


        self.load_file(filename)


    def load_file(self, filename):
        self.filename = filename
        try:
            if '\\' in filename:
                rname = filename.split('\\')
            elif '/' in filename:
                rname = filename.split('/')

            rname = rname[-1]
            if '.p' in rname:
                rname = rname[:-2]
            if '.pkl' in rname:
                rname = rname[:-4]
            if '.pickle' in rname:
                rname = rname[:-7]
            file = open(filename, 'rb')

            self.boreholes, self.mogs, self.air, self.models = pickle.load(file)
            self.update_database_info(rname)
            self.update_log("Database '{}' was loaded successfully".format(rname))

            self.bh.boreholes = self.boreholes
            self.mog.MOGs = self.mogs
            self.model.models = self.models
            self.grid.model = self.model


            self.mog.air = self.air

            self.bh.update_List_Widget()
            self.bh.bh_list.setCurrentRow(0)
            self.bh.update_List_Edits()

            self.mog.update_List_Widget()
            self.mog.update_edits()
            self.mog.MOG_list.setCurrentRow(0)
            self.mog.update_spectra_Tx_num_list()
            self.mog.update_spectra_Tx_elev_value_label()
            self.mog.update_edits()
            self.mog.update_prune_edits_info()
            self.mog.update_prune_info()

            self.model.update_model_list()
            self.model.update_model_mog_list()

        except:
            self.update_log('Error: Database file must be of pickle type')

    def savefile(self):
        try:

            save_file = open(self.filename, 'wb')
            pickle.dump((self.boreholes, self.mogs, self.air, self.models), save_file)
            dialog = QtGui.QMessageBox.information(self, 'Success', "Database was saved successfully"
                                                    ,buttons=QtGui.QMessageBox.Ok)

            self.update_log("Database was saved successfully")
        except:
            dialog = QtGui.QMessageBox.warning(self, 'Warning', "Database could not be saved"
                                                    , buttons=QtGui.QMessageBox.Ok)
            self.update_log('Error: Database could not be saved')

    def saveasfile(self):
        try:
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save Database as ...', self.name, filter= 'pickle (*.p *.pkl *.pickle)', )
            print(filename)
            save_file = open(filename, 'wb')
            pickle.dump((self.boreholes, self.mogs, self.air, self.models), save_file)
            dialog = QtGui.QMessageBox.information(self, 'Success', "Database was saved successfully"
                                                    ,buttons=QtGui.QMessageBox.Ok)

            self.update_log("Database was saved successfully")
        except:
            dialog = QtGui.QMessageBox.warning(self, 'Warning', "Database could not be saved"
                                                    , buttons=QtGui.QMessageBox.Ok)

            self.update_log('Error: Database could not be saved')

    def editname(self):
        new_name, ok = QtGui.QInputDialog.getText(self, "Change Name", 'Enter new name for database')

        self.name = new_name

        if new_name == '':
            return

        self.info.live_database_label.setText(str(new_name))


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
        saveAction.triggered.connect(self.savefile)

        saveasAction = QtGui.QAction('Save as', self)
        saveasAction.setShortcut('Ctrl+A')
        saveasAction.triggered.connect(self.saveasfile)

        editnameAction = QtGui.QAction('Edit database name', self)
        editnameAction.triggered.connect(self.editname)


        #--- Menubar ---#
        self.menu = QtGui.QMenuBar()
        filemenu = self.menu.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(saveasAction)

        editmenu = self.menu.addMenu('&Edit')
        editmenu.addAction(editnameAction)


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

        #- Big SubWidget -#
        sub_big_widget = QtGui.QWidget()
        sub_big_grid = QtGui.QGridLayout()
        sub_big_grid.addWidget(bh_GroupBox, 1, 0)
        sub_big_grid.addWidget(MOGs_GroupBox, 1, 1, 1, 2)
        sub_big_grid.addWidget(Models_GroupBox, 2, 0, 1, 2)
        sub_big_grid.addWidget(Info_GroupBox, 2, 2)
        sub_big_widget.setLayout(sub_big_grid)

        #--- Grid ---#
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0, 1, 3)
        master_grid.addWidget(sub_big_widget, 1, 0, 1, 3)
        master_grid.addWidget(self.log, 2, 0, 2, 3)
        master_grid.setContentsMargins(0, 0, 0, 0)
        master_grid.setVerticalSpacing(5)

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
    Database_ui.update_log("Welcome to BH TOMO Python Edition's Database")
    Database_ui.load_file('C:\\Users\\Utilisateur\\PycharmProjects\\BhTomoPy\\save test.p')
    #Database_ui.bh.load_bh('testData/testConstraints/F3.xyz')
    #Database_ui.bh.load_bh('testData/testConstraints/F2.xyz')
    #Database_ui.mog.load_file_MOG('testData/formats/ramac/t0302.rad')
    #Database_ui.mog.load_file_MOG('testData/formats/ramac/t0102.rad')
    #Database_ui.model.load_model("t0302's model")
    #Database_ui.mog.plot_spectra()
    #Database_ui.mog.plot_zop()


    Database_ui.show()



    sys.exit(app.exec_())
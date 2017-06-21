# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jerome Simon
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from borehole_ui import BoreholeUI
from model_ui import ModelUI
from mog_ui import MOGUI, MergeMog
from info_ui import InfoUI
import time
import os
import database
import utils_ui


class DatabaseUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DatabaseUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Database")
        # --- Other Modules Instance --- #
        self.bh = BoreholeUI()
        self.mog = MOGUI()
        self.model = ModelUI()
        self.info = InfoUI()
        self.mergemog = MergeMog(self.mog)
        self.initUI()
        self.action_list = []

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
        # Clears the log to make sure any action is not written more than once
        self.log.clear()

        # Appends the time and the action that was done
        self.action_list.append("[{}] {} ".format(time.asctime()[11:16], action))

        # Shows the Error messages in red and the others in black
        for item in self.action_list:

            if "Error:" in item:
                self.log.setTextColor(QtGui.QColor(QtCore.Qt.red))
                self.log.append(item)

            else:
                self.log.setTextColor(QtGui.QColor(QtCore.Qt.black))
                self.log.append(item)

    def update_widgets(self):

            self.bh.update_List_Widget()
            self.bh.bh_list.setCurrentRow(0)
            self.bh.update_List_Edits()

            self.mog.update_List_Widget()
            self.mog.update_edits()
            self.mog.MOG_list.setCurrentRow(0)
            self.mog.update_spectra_and_coverage_Tx_num_list()
            self.mog.update_spectra_and_coverage_Tx_elev_value_label()
            self.mog.update_edits()
            self.mog.update_prune_edits_info()
            self.mog.update_prune_info()

            self.model.update_model_list()
            self.model.update_model_mog_list()

            if str(database.engine.url) != 'sqlite:///:memory:':
                self.update_database_info(database.short_url(database))

    def show(self):
        super(DatabaseUI, self).show()

        # Gets initial geometry of the widget:
        qr = self.frameGeometry()

        # Shows it at the center of the screen
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()

        # Moves the window's center at the center of the screen
        qr.moveCenter(cp)

        # Then moves it at the top left
        translation = qr.topLeft()

        self.move(translation)

        self.update_widgets()

    def openfile(self):  # TODO: On Windows, access to folders containing special characters fails. May be due to the fact that Windows doesn't use Unicode.

        if utils_ui.save_warning(database):
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Database')[0]

            if filename:
                if filename[-3:] != '.db':
                    QtWidgets.QMessageBox.warning(self, 'Warning', "Database has wrong extension.", buttons=QtWidgets.QMessageBox.Ok)
                else:
                    database.load(database, filename)
                    self.update_database_info(os.path.basename(filename))
                    self.update_widgets()
                    self.update_log("Database '{}' was loaded successfully".format(os.path.basename(filename)))

    def savefile(self):

        try:
            if str(database.engine.url) == 'sqlite:///:memory:':
                self.saveasfile()
                return

            database.session.commit()
            database.modified = False

            try:
                self.model.gridui.update_model_grid()
            except:
                print("Warning : 'update_model_grid' skipped [database_ui 1]")

            self.update_log("Database was saved successfully")
            QtWidgets.QMessageBox.information(self, 'Success', "Database was saved successfully",
                                              buttons=QtWidgets.QMessageBox.Ok)

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Database could not be saved : " + str(e),
                                          buttons=QtWidgets.QMessageBox.Ok)

    def saveasfile(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Database as ...',
                                                         filter='Database (*.db)', )[0]

        if filename:
            if filename != database.long_url(database):
                database.save_as(database, filename)

                self.update_database_info(os.path.basename(filename))
                self.update_log("Database '{}' was saved successfully".format(os.path.basename(filename)))

            else:
                database.session.commit()
                database.modified = False

    def initUI(self):

        # --- Log Widget --- #
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(0)

        # --- Actions --- #
        openAction = QtWidgets.QAction('Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openfile)

        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.savefile)

        saveasAction = QtWidgets.QAction('Save as', self)
        saveasAction.setShortcut('Ctrl+A')
        saveasAction.triggered.connect(self.saveasfile)

        # --- Menubar --- #
        self.menu = QtWidgets.QMenuBar()
        filemenu = self.menu.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(saveasAction)

        # --- GroupBoxes --- #
        # - Boreholes GroupBox - #
        bh_GroupBox = QtWidgets.QGroupBox("Boreholes")
        bh_Sub_Grid = QtWidgets.QGridLayout()
        bh_Sub_Grid.addWidget(self.bh)
        bh_GroupBox.setLayout(bh_Sub_Grid)

        # - MOGs GroupBox - #
        MOGs_GroupBox = QtWidgets.QGroupBox("MOGs")
        MOGs_Sub_Grid = QtWidgets.QGridLayout()
        MOGs_Sub_Grid.addWidget(self.mog)
        MOGs_GroupBox.setLayout(MOGs_Sub_Grid)

        # - Models GroupBox - #
        Models_GroupBox = QtWidgets.QGroupBox("Models")
        Models_Sub_Grid = QtWidgets.QGridLayout()
        Models_Sub_Grid.addWidget(self.model)
        Models_GroupBox.setLayout(Models_Sub_Grid)

        # - Info GroupBox - #
        Info_GroupBox = QtWidgets.QGroupBox("Infos")
        Info_Sub_Grid = QtWidgets.QGridLayout()
        Info_Sub_Grid.addWidget(self.info)
        Info_GroupBox.setLayout(Info_Sub_Grid)

        # - Big SubWidget - #
        sub_big_widget = QtWidgets.QWidget()
        sub_big_grid = QtWidgets.QGridLayout()
        sub_big_grid.addWidget(bh_GroupBox, 0, 0, 1, 1)
        sub_big_grid.addWidget(MOGs_GroupBox, 0, 1, 1, 3)
        sub_big_grid.addWidget(Models_GroupBox, 1, 0, 2, 2)
        sub_big_grid.addWidget(Info_GroupBox, 1, 2, 2, 3)
        sub_big_grid.setColumnStretch(0, 1)
        sub_big_grid.setColumnStretch(1, 1)
        sub_big_grid.setColumnStretch(2, 1)
        sub_big_widget.setLayout(sub_big_grid)

        # - Scroll bar - #

        scrollbar = utils_ui.auto_create_scrollbar(sub_big_widget)

        # --- Grid --- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0, 1, 3)
        master_grid.addWidget(scrollbar, 1, 0, 1, 3)
        master_grid.addWidget(self.log, 2, 0, 2, 3)
        master_grid.setContentsMargins(0, 0, 0, 0)
        master_grid.setVerticalSpacing(5)

        self.setLayout(master_grid)


class MyLogWidget(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(MyLogWidget, self).__init__(parent)

    def append(self, txt):
        super(MyLogWidget, self).append(txt)

        bottom = self.verticalScrollBar().maximum()
        self.verticalScrollBar().setValue(bottom)


if __name__ == '__main__':

    database.create_data_management(database)

    app = QtWidgets.QApplication(sys.argv)

    Database_ui = DatabaseUI()
    Database_ui.show()

    Database_ui.update_log("Welcome to BH TOMO Python Edition's Database")
#     Database_ui.bh.load_bh('testData/testConstraints/F3.xyz')
#     Database_ui.bh.load_bh('testData/testConstraints/F2.xyz')
#     Database_ui.mog.load_file_MOG('testData/formats/ramac/t0302.rad')
#     Database_ui.mog.load_file_MOG('testData/formats/ramac/t0102.rad')
#     Database_ui.model.load_model("t0302's model")
#     Database_ui.model.load_model("test")
#     Database_ui.model.load_model("test2")
#     Database_ui.mog.plot_spectra()
#     Database_ui.mog.plot_zop()

#     Database_ui.saveasfile()

    sys.exit(app.exec_())

# -*- coding: utf-8 -*-
"""

Copyright 2016 Bernard Giroux, Elie Dumas-Lefebvre

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
from PyQt5 import QtWidgets, QtCore


class InfoUI(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(InfoUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Info")
        self.initUI()

    #------- Updating the information -------#
    def update_database(self, name):
        self.live_database_label.setText(name)

    def update_borehole(self, value):
        self.num_boreholes_label.setText(str(value))

    def update_mog(self, value):
        self.num_mogs_label.setText(str(value))

    def update_model(self, value):
        self.num_models_label.setText(str(value))

    def update_trace(self, value):
        self.num_traces_label.setText(str(value))


    def initUI(self):

        #--- Widget ---#
        self.database_label = QtWidgets.QLabel("Database : ")
        self.live_database_label = MyQLabel('',ha='left')
        self.boreholes_label = QtWidgets.QLabel(" Borehole(s)")
        self.num_boreholes_label = MyQLabel('0',ha='right')
        self.mogs_label = QtWidgets.QLabel(" MOG(s)")
        self.num_mogs_label = MyQLabel('0',ha='right')
        self.models_label = QtWidgets.QLabel(" Model(s)")
        self.num_models_label = MyQLabel('0',ha='right')
        self.traces_label = QtWidgets.QLabel(" Traces")
        self.num_traces_label = MyQLabel('0',ha='right')

        #--- Grid ---#
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.database_label, 0, 0)
        master_grid.addWidget(self.live_database_label, 0, 1)
        master_grid.addWidget(self.num_boreholes_label, 2, 0)
        master_grid.addWidget(self.boreholes_label, 2, 1)
        master_grid.addWidget(self.num_mogs_label, 3, 0)
        master_grid.addWidget(self.mogs_label, 3, 1)
        master_grid.addWidget(self.num_models_label, 4, 0)
        master_grid.addWidget(self.models_label, 4, 1)
        master_grid.addWidget(self.num_traces_label, 6, 0)
        master_grid.addWidget(self.traces_label, 6, 1)
        master_grid.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(master_grid)
        self.setStyleSheet("background: white")


class MyQLabel(QtWidgets.QLabel):
    def __init__(self, label, ha='left', parent=None):
        super(MyQLabel, self).__init__(label, parent)
        if ha == 'center':
            self.setAlignment(QtCore.Qt.AlignCenter)
        elif ha == 'right':
            self.setAlignment(QtCore.Qt.AlignRight)
        else:
            self.setAlignment(QtCore.Qt.AlignLeft)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    Info_ui = InfoUI()
    Info_ui.show()

    sys.exit(app.exec_())
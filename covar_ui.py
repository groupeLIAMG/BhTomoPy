# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jérome Simon
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
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import covar
import data_manager
import database


class CovarUI(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(CovarUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Covariance")
        self.initUI()

    def show(self):
        super(CovarUI, self).show()

        # Gets initial geometry of the widget:
        qr = self.frameGeometry()

        # Shows it at the center of the screen
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()

        # Moves the window's center at the center of the screen
        qr.moveCenter(cp)

        # Then moves it at the top left
        translation = qr.topLeft()

        self.move(translation)

#         self.update_widgets()

    def openfile(self):

        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Database')[0]

        if filename:
            if filename[-3:] != '.db':
                QtWidgets.QMessageBox.warning(self, 'Warning', "Database has wrong extension.", buttons=QtWidgets.QMessageBox.Ok)
            else:
                try:
                    data_manager.load(database, filename)
#                     self.update_widgets()

                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, 'Warning', "Database could not be opened : '" + str(e)[:42] + "...' File may be empty or corrupted.",
                                                  buttons=QtWidgets.QMessageBox.Ok)

    def savefile(self):

        try:
            if str(database.engine.url) == 'sqlite:///:memory:':
                self.saveasfile()
                return

            database.session.commit()

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
            if filename != str(database.engine.url).replace('sqlite:///', ''):
                data_manager.save_as(database, filename)

                self.update_database_info(os.path.basename(filename))
                self.update_log("Database '{}' was saved successfully".format(os.path.basename(filename)))

            else:
                database.session.commit()

    def initUI(self):
        # --- Color for the labels --- #
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)

        # --- Class For Alignment --- #
        class MyQLabel(QtWidgets.QLabel):
            def __init__(self, label, ha='left', parent=None):
                super(MyQLabel, self).__init__(label, parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)

        # ------- Widgets Creation ------- #

        # --- Menu Actions --- #
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

        # --- Buttons Set --- #
        btn_Show_Stats = QtWidgets.QPushButton("Show Stats")
        btn_Add_Struct = QtWidgets.QPushButton("Add Structure")
        btn_Rem_Struct = QtWidgets.QPushButton("Remove Structure")
        btn_compute    = QtWidgets.QPushButton("Compute")
        btn_GO         = QtWidgets.QPushButton("GO")

        # --- Label --- #
        cells_Label      = MyQLabel("Cells", ha='center')
        cells_Labeli     = MyQLabel("Cells", ha='center')
        rays_label       = MyQLabel("Rays", ha='center')

        curv_rays_label  = MyQLabel("Curved Rays", ha='right')
        X_label          = MyQLabel("X", ha='center')
        Y_label          = MyQLabel("Y", ha='center')
        Z_label          = MyQLabel("Y", ha='center')
        Xi_label         = MyQLabel("X", ha='center')
        Yi_label         = MyQLabel("Y", ha='center')
        Zi_label         = MyQLabel("Z", ha='center')
        self.X_min_label = MyQLabel("0", ha='center')
        self.Y_min_label = MyQLabel("0", ha='center')
        self.Z_min_label = MyQLabel("0", ha='center')
        self.X_max_label = MyQLabel("0", ha='center')
        self.Y_max_label = MyQLabel("0", ha='center')
        self.Z_max_label = MyQLabel("0", ha='center')

        Min_label        = MyQLabel("Min", ha='right')
        Max_label        = MyQLabel("Max", ha='right')
        step_label       = MyQLabel("Step :", ha='center')
        slowness_label   = MyQLabel("Slowness", ha='right')
        traveltime_label = MyQLabel("Traveltime", ha='right')
        separ_label      = MyQLabel("|", ha='center')
        bin_label        = MyQLabel("Bin Length", ha='right')
        bin_frac_label   = MyQLabel("Fraction of Bins", ha='right')
        Iter_label       = MyQLabel("Number of Iterations", ha='right')

        self.X_min_label.setPalette(palette)
        self.Y_min_label.setPalette(palette)
        self.Z_min_label.setPalette(palette)
        self.X_max_label.setPalette(palette)
        self.Y_max_label.setPalette(palette)
        self.Z_max_label.setPalette(palette)
        cells_Label     .setPalette(palette)
        cells_Labeli    .setPalette(palette)
        rays_label      .setPalette(palette)

        # --- Edits --- #
        velocity_Edit  = QtWidgets.QLineEdit()
        step_X_Edit = QtWidgets.QLineEdit()
        step_X_Edit.setFixedWidth(50)
        step_Y_Edit = QtWidgets.QLineEdit()
        step_Y_Edit.setFixedWidth(50)
        step_Z_Edit = QtWidgets.QLineEdit()
        step_Z_Edit.setFixedWidth(50)
        slowness_Edit   = QtWidgets.QLineEdit('0')
        traveltime_Edit = QtWidgets.QLineEdit('0')
        bin_Edit        = QtWidgets.QLineEdit('50')
        bin_frac_Edit   = QtWidgets.QLineEdit('0.25')
        Iter_Edit       = QtWidgets.QLineEdit('5')

        # --- Checkboxes --- #
        Upper_limit_checkbox        = QtWidgets.QCheckBox("Upper Limit - Apparent Velocity")
        ellip_veloc_checkbox        = QtWidgets.QCheckBox("Elliptical Velocity Anisotropy")
        tilted_ellip_veloc_checkbox = QtWidgets.QCheckBox("Tilted Elliptical Velocity Anisotropy")
        include_checkbox            = QtWidgets.QCheckBox("Include Experimental Variance")
        slowness_checkbox           = QtWidgets.QCheckBox()
        traveltime_checkbox         = QtWidgets.QCheckBox()
        auto_update_checkbox        = QtWidgets.QCheckBox("Auto Update")

        # --- Text Edits --- #
        futur_Graph1 = QtWidgets.QTextEdit()
        futur_Graph1.setReadOnly(True)
        futur_Graph2 = QtWidgets.QTextEdit()
        futur_Graph2.setReadOnly(True)

        # --- Comboboxes --- #
        T_and_A_combo      = QtWidgets.QComboBox()
        T_and_A_combo.addItem("Traveltime")
        T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        T_and_A_combo.addItem("Amplitude - Centroid Frequency")
        curv_rays_combo    = QtWidgets.QComboBox()
        covar_struct_combo = QtWidgets.QComboBox()
        covar_struct_combo.addItem("Structure no 1")

        # --- List --- #
        self.models_list = QtWidgets.QListWidget()

        # ------- Actions ------- #

        # --- Buttons --- #

        btn_Show_Stats.clicked.connect(covar._)
        btn_Add_Struct.clicked.connect(covar._)
        btn_Rem_Struct.clicked.connect(covar._)
        btn_compute   .clicked.connect(covar._)
        btn_GO        .clicked.connect(covar._)

        # --- Edits --- #

        velocity_Edit  .editingFinished.connect(covar._)
        step_X_Edit    .editingFinished.connect(covar._)
        step_Y_Edit    .editingFinished.connect(covar._)
        step_Z_Edit    .editingFinished.connect(covar._)
        slowness_Edit  .editingFinished.connect(covar._)
        traveltime_Edit.editingFinished.connect(covar._)
        bin_Edit       .editingFinished.connect(covar._)
        bin_frac_Edit  .editingFinished.connect(covar._)
        Iter_Edit      .editingFinished.connect(covar._)

        # --- Checkboxes --- #

        Upper_limit_checkbox       .stateChanged.connect(covar._)
        ellip_veloc_checkbox       .stateChanged.connect(covar._)
        tilted_ellip_veloc_checkbox.stateChanged.connect(covar._)
        include_checkbox           .stateChanged.connect(covar._)
        slowness_checkbox          .stateChanged.connect(covar._)
        traveltime_checkbox        .stateChanged.connect(covar._)
        auto_update_checkbox       .stateChanged.connect(covar._)

        # --- Comboboxes --- #

        T_and_A_combo     .currentIndexChanged.connect(covar._)
        curv_rays_combo   .currentIndexChanged.connect(covar._)
        covar_struct_combo.currentIndexChanged.connect(covar._)

        # ------- SubWidgets ------- #
        # --- Curved Rays SubWidget --- #
        Sub_Curved_Rays_Widget = QtWidgets.QWidget()
        Sub_Curved_Rays_Grid = QtWidgets.QGridLayout()
        Sub_Curved_Rays_Grid.addWidget(curv_rays_label, 0, 0)
        Sub_Curved_Rays_Grid.addWidget(curv_rays_combo, 0, 1)
        Sub_Curved_Rays_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_Curved_Rays_Widget.setLayout(Sub_Curved_Rays_Grid)

        # --- Grid Coordinates SubWidget --- #
        Sub_Grid_Coord_Widget = QtWidgets.QWidget()
        Sub_Grid_Coord_grid = QtWidgets.QGridLayout()
        Sub_Grid_Coord_grid.addWidget(X_label, 0, 1)
        Sub_Grid_Coord_grid.addWidget(Y_label, 0, 2)
        Sub_Grid_Coord_grid.addWidget(Z_label, 0, 3)
        Sub_Grid_Coord_grid.addWidget(Min_label, 1, 0)
        Sub_Grid_Coord_grid.addWidget(Max_label, 2, 0)
        Sub_Grid_Coord_grid.addWidget(self.X_min_label, 1, 1)
        Sub_Grid_Coord_grid.addWidget(self.Y_min_label, 1, 2)
        Sub_Grid_Coord_grid.addWidget(self.Z_min_label, 1, 3)
        Sub_Grid_Coord_grid.addWidget(self.X_max_label, 2, 1)
        Sub_Grid_Coord_grid.addWidget(self.Y_max_label, 2, 2)
        Sub_Grid_Coord_grid.addWidget(self.Z_max_label, 2, 3)
        Sub_Grid_Coord_grid.setHorizontalSpacing(55)
        Sub_Grid_Coord_Widget.setLayout(Sub_Grid_Coord_grid)

        # --- Step SubWidget --- #
        Sub_Step_Widget = QtWidgets.QWidget()
        Sub_Step_Grid = QtWidgets.QGridLayout()
        Sub_Step_Grid.addWidget(step_label, 1, 0)
        Sub_Step_Grid.addWidget(step_X_Edit, 1, 1)
        Sub_Step_Grid.addWidget(step_Y_Edit, 1, 2)
        Sub_Step_Grid.addWidget(step_Z_Edit, 1, 3)
        Sub_Step_Grid.addWidget(Xi_label, 0, 1)
        Sub_Step_Grid.addWidget(Yi_label, 0, 2)
        Sub_Step_Grid.addWidget(Zi_label, 0, 3)
        Sub_Step_Grid.addWidget(cells_Labeli, 2, 2)
        Sub_Step_Grid.setHorizontalSpacing(0)
        Sub_Step_Widget.setLayout(Sub_Step_Grid)

        # ------- SubGroupboxes ------- #
        # --- Data Groupbox --- #
        data_groupbox = QtWidgets.QGroupBox("Data")
        data_grid = QtWidgets.QGridLayout()
        data_grid.addWidget(cells_Label, 0, 0)
        data_grid.addWidget(rays_label, 1, 0)
        data_grid.addWidget(self.models_list, 2, 0, 3, 1)
        data_grid.addWidget(Upper_limit_checkbox, 0, 1)
        data_grid.addWidget(velocity_Edit, 0, 2)
        data_grid.addWidget(ellip_veloc_checkbox, 1, 1)
        data_grid.addWidget(tilted_ellip_veloc_checkbox, 2, 1)
        data_grid.addWidget(include_checkbox, 3, 1)
        data_grid.addWidget(T_and_A_combo, 4, 1)
        data_grid.addWidget(btn_Show_Stats, 4, 2)
        data_grid.addWidget(Sub_Curved_Rays_Widget, 5, 1)
        data_groupbox.setLayout(data_grid)

        # --- Grid Groupbox --- #
        Grid_groupbox = QtWidgets.QGroupBox("Grid")
        Grid_grid = QtWidgets.QGridLayout()
        Grid_grid.addWidget(Sub_Grid_Coord_Widget, 0, 0)
        Grid_grid.addWidget(Sub_Step_Widget, 0, 1)
        Grid_groupbox.setLayout(Grid_grid)

        # --- Parameters Groupbox --- #
        Param_groupbox = QtWidgets.QGroupBox("Parameters")
        Param_grid = QtWidgets.QGridLayout()
        Param_groupbox.setLayout(Param_grid)

        # --- Nugget Effect Groupbox --- #
        Nug_groupbox = QtWidgets.QGroupBox("Nugget Effect")
        Nug_grid = QtWidgets.QGridLayout()
        Nug_grid.addWidget(slowness_label, 0, 0)
        Nug_grid.addWidget(slowness_Edit, 0, 1)
        Nug_grid.addWidget(slowness_checkbox, 0, 2)
        Nug_grid.addWidget(separ_label, 0, 3)
        Nug_grid.addWidget(traveltime_label, 0, 4)
        Nug_grid.addWidget(traveltime_Edit, 0, 5)
        Nug_grid.addWidget(traveltime_checkbox, 0, 6)
        Nug_groupbox.setLayout(Nug_grid)

        # --- Covariance Model Groupbox --- #
        covar_groupbox = QtWidgets.QGroupBox("Covariance Model")
        covar_grid = QtWidgets.QGridLayout()
        covar_grid.addWidget(covar_struct_combo, 0, 0)
        covar_grid.addWidget(btn_Add_Struct, 0, 1)
        covar_grid.addWidget(btn_Rem_Struct, 0, 2)
        covar_grid.addWidget(Param_groupbox, 1, 0, 1, 3)
        covar_grid.addWidget(Nug_groupbox, 2, 0, 1, 3)
        covar_grid.addWidget(auto_update_checkbox, 3, 0)
        covar_grid.addWidget(btn_compute, 3, 1)
        covar_groupbox.setLayout(covar_grid)

        # --- Adjust Model Groupbox --- #
        Adjust_Model_groupbox = QtWidgets.QGroupBox("Adjust Model (Simplex Method)")
        Adjust_Model_grid = QtWidgets.QGridLayout()
        Adjust_Model_grid.addWidget(bin_label, 0, 0)
        Adjust_Model_grid.addWidget(bin_Edit, 0, 1)
        Adjust_Model_grid.addWidget(bin_frac_label, 1, 0)
        Adjust_Model_grid.addWidget(bin_frac_Edit, 1, 1)
        Adjust_Model_grid.addWidget(Iter_label, 2, 0)
        Adjust_Model_grid.addWidget(Iter_Edit, 2, 1)
        Adjust_Model_grid.addWidget(btn_GO, 0, 3, 3, 1)
        Adjust_Model_grid.setColumnStretch(4, 100)
        Adjust_Model_groupbox.setLayout(Adjust_Model_grid)

        # ------- Master Grid Disposition ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(futur_Graph1, 0, 0, 2, 3)
        master_grid.addWidget(futur_Graph2, 2, 0, 2, 3)
        master_grid.addWidget(data_groupbox, 0, 3)
        master_grid.addWidget(Grid_groupbox, 1, 3)
        master_grid.addWidget(covar_groupbox, 2, 3)
        master_grid.addWidget(Adjust_Model_groupbox, 3, 3)
        master_grid.setColumnStretch(0, 100)
        master_grid.setColumnStretch(3, 100)

        self.setLayout(master_grid)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    Model_ui = CovarUI()
    Model_ui.show()

    sys.exit(app.exec_())

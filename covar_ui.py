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
from PyQt5 import QtGui, QtWidgets, QtCore
from model import Model
import covar
import database

import unicodedata
xi    = unicodedata.lookup("GREEK SMALL LETTER XI")
theta = unicodedata.lookup("GREEK SMALL LETTER THETA")


class CovarUI(QtWidgets.QFrame):

    model = None  # current model

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

        self.update_data()
        self.set_current_model()
        self.update_model()
        self.update_adjust()
        self.parameters_displayed_update()

    def openfile(self):

        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Database')[0]

        if filename:
            if filename[-3:] != '.db':
                QtWidgets.QMessageBox.warning(self, 'Warning', "Database has wrong extension.", buttons=QtWidgets.QMessageBox.Ok)
            else:
                try:
                    database.load(database, filename)
                    self.update_data()
                    self.update_model()
                    self.update_parameters()

                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, 'Warning', "Database could not be opened : '" + str(e)[:42] +
                                                  "...' File may be empty or corrupted.", buttons=QtWidgets.QMessageBox.Ok)

    def savefile(self):

        try:
            if str(database.engine.url) == 'sqlite:///:memory:':
                self.saveasfile()
                return

            database.session.commit()
            QtWidgets.QMessageBox.information(self, 'Success', "Database was saved successfully",
                                              buttons=QtWidgets.QMessageBox.Ok)
            return 'ok'

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Database could not be saved : " + str(e),
                                          buttons=QtWidgets.QMessageBox.Ok)

    def saveasfile(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Database as ...',
                                                         filter='Database (*.db)', )[0]

        if filename:
            if 'sqlite:///' + filename != str(database.engine.url):
                database.save_as(database, filename)
                return 'ok'

            else:
                database.session.commit()
                return 'ok'

    updateHandler = False  # selected model may seldom modified twice. 'updateHandler' prevents functions from firing more than once.

    def set_current_model(self):  # substitutes SQLAlchemy weak referencing for a strong referencing
        if self.updateHandler:
            return

        print('Trying...')
        self.updateHandler = True
        if self.model is not None:
            print(self.model.name)
            ok = save_warning()
            if ok == 1:
                ok = self.savefile()
            elif ok == 2:
                ok = self.saveasfile()
            if ok:
                self.model = self.current_model()
                self.updateHandler = False
            else:
                for i in range(self.models_list.count()):
                    print(self.models_list.item(i).text(), self.model.name)
                    if self.models_list.item(i).text() == self.model.name:
                        self.models_list.setCurrentRow(i)
                        self.updateHandler = False
                        break
        else:
            self.model = self.current_model()
            self.updateHandler = False

    def current_model(self):

        if self.models_list.currentItem():
            return database.session.query(Model).filter(Model.name == self.models_list.currentItem().text()).first()

    def parameters_displayed_update(self):
        if self.updateHandler:
            return

        self.updateHandler = True

        self.Sub_widget.setDisabled(True)

        self.labels_2D_widget.setHidden(True)
        self.slowness_widget.setHidden(True)
        self.xi_widget.setHidden(True)
        self.tilt_widget.setHidden(True)
        self.slowness_3D_widget.setHidden(True)
        self.ellip_veloc_checkbox.setDisabled(True)
        self.tilted_ellip_veloc_checkbox.setDisabled(True)

        self.covar_struct_combo.setDisabled(True)
        self.btn_Add_Struct.setDisabled(True)
        self.btn_Rem_Struct.setDisabled(True)
        self.btn_Ren_Struct.setDisabled(True)

        self.xi_label.setHidden(True)
        self.xi_Edit.setHidden(True)
        self.xi_checkbox.setHidden(True)

        self.tilt_label.setHidden(True)
        self.tilt_Edit.setHidden(True)
        self.tilt_checkbox.setHidden(True)

        if database.session.query(Model).first() is not None:

            self.Sub_widget.setDisabled(False)

            if self.model:

                self.covar_struct_combo.setDisabled(False)
                self.btn_Add_Struct.setDisabled(False)

                if self.model.tt_covar:
                    self.btn_Rem_Struct.setDisabled(False)
                    self.btn_Ren_Struct.setDisabled(False)
                    if True:  # self.model.is3D:
                        self.labels_2D_widget.setHidden(False)
                        self.slowness_widget.setHidden(False)
                        self.ellip_veloc_checkbox.setDisabled(False)

                        if self.ellip_veloc_checkbox.checkState():
                            self.xi_widget.setHidden(False)
                            self.tilted_ellip_veloc_checkbox.setDisabled(False)

                            self.xi_label.setHidden(False)
                            self.xi_Edit.setHidden(False)
                            self.xi_checkbox.setHidden(False)

                            if self.tilted_ellip_veloc_checkbox.checkState():
                                self.tilt_widget.setHidden(False)

                                self.tilt_label.setHidden(False)
                                self.tilt_Edit.setHidden(False)
                                self.tilt_checkbox.setHidden(False)

                        else:
                            self.tilted_ellip_veloc_checkbox.setCheckState(False)

                    else:
                        self.slowness_3D_widget.setHidden(False)

            self.update_parameters()

        else:
            self.ellip_veloc_checkbox.setCheckState(False)
            self.tilted_ellip_veloc_checkbox.setCheckState(False)

        self.updateHandler = False

    def auto_update(self):
        if self.auto_update_checkbox.checkState():
            pass
            # compute

    def update_data(self):
        self.model = None
        self.models_list.clear()
        self.models_list.addItems([item.name for item in database.session.query(Model).all()])

    def update_model(self):
        self.btn_Rem_Struct.setDisabled(True)
        self.btn_Ren_Struct.setDisabled(True)
        self.covar_struct_combo.clear()
        if self.models_list.currentItem():
            self.set_current_model()
            current_list = self.model.tt_covar
            if current_list:
                self.covar_struct_combo.addItems([item.name for item in current_list])
                self.covar_struct_combo.setCurrentIndex(0)
                current_struct = current_list[0]
                self.update_parameters(current_struct)
                self.update_nugget(current_struct)
                self.btn_Rem_Struct.setDisabled(False)
                self.btn_Ren_Struct.setDisabled(False)

    def update_parameters(self, structure=None):
        pass

    def update_nugget(self, structure):
        pass

    def update_adjust(self):
        pass

    def compute(self):  # TODO progress bar
        pass

    def show_stats(self):
        pass

    def add_struct(self):
        r = [0, 0]
        a = [0]
        s = 0
        new = covar.Covariance(self.duplicate_verif(), r, a, s)
        self.model.tt_covar.append(new)
        count = self.covar_struct_combo.count()
        self.covar_struct_combo.addItem(new.name)
        self.covar_struct_combo.setCurrentIndex(count)
        self.parameters_displayed_update()
#         self.update_parameters(new)

    def del_struct(self):
        index = self.covar_struct_combo.currentIndex()
        self.covar_struct_combo.removeItem(index)
        del self.model.tt_covar[index]
        count = self.covar_struct_combo.count()
        if count != 0:
            if index == count:
                self.covar_struct_combo.setCurrentIndex(index - 1)
            else:
                self.covar_struct_combo.setCurrentIndex(index)
        self.parameters_displayed_update()
#         self.update_parameters(self.model.tt_covar[self.covar_struct_combo.currentIndex()])

    def ren_struct(self):
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename", 'New structure name :')
        if ok:
            if self.duplicate_verif(new_name) != new_name:
                QtWidgets.QMessageBox.warning(self, "Warning", "Could not rename structure: a structure already has this name.")
                return
            self.model.tt_covar[self.covar_struct_combo.currentIndex()].name = new_name
        self.update_model()

    def duplicate_verif(self, string=None, recursion=1):

        if not string:
            string = "New model"

        for i in range(self.covar_struct_combo.count()):
            if self.covar_struct_combo.itemText(i) == string:
                if recursion > 1:
                    string = string[:-2]
                string = self.duplicate_verif(string + ' ' + str(recursion), recursion + 1)
                return string

        return string

    def adjust(self):
        pass

    def test(self):
        self.models_list.setCurrentRow(0)

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

        # --- Buttons Sets --- #
        self.btn_Show_Stats = QtWidgets.QPushButton("Show Stats")
        self.btn_Add_Struct = QtWidgets.QPushButton("Add Structure")
        self.btn_Rem_Struct = QtWidgets.QPushButton("Remove Structure")
        self.btn_Ren_Struct = QtWidgets.QPushButton("Rename Structure")
        self.btn_compute    = QtWidgets.QPushButton("Compute")
        self.btn_GO         = QtWidgets.QPushButton("GO")

        # --- Labels --- #
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

        Min_label             = MyQLabel("Min", ha='right')
        Max_label             = MyQLabel("Max", ha='right')
        step_label            = MyQLabel("Step :", ha='center')
        self.slowness_label   = MyQLabel("Slowness", ha='right')
        self.traveltime_label = MyQLabel("Traveltime", ha='right')
        self.xi_label         = MyQLabel(xi, ha='right')
        self.tilt_label       = MyQLabel("Tilt Angle", ha='right')
        bin_label             = MyQLabel("Bin Length", ha='right')
        bin_frac_label        = MyQLabel("Fraction of Bins", ha='right')
        Iter_label            = MyQLabel("Number of Iterations", ha='right')

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
        velocity_Edit = MyLineEdit()
        step_X_Edit = MyLineEdit()
        step_X_Edit.setFixedWidth(50)
        step_Y_Edit = MyLineEdit()
        step_Y_Edit.setFixedWidth(50)
        step_Z_Edit = MyLineEdit()
        step_Z_Edit.setFixedWidth(50)
        self.slowness_Edit   = MyLineEdit('0')
        self.traveltime_Edit = MyLineEdit('0')
        self.xi_Edit         = MyLineEdit('0')
        self.tilt_Edit       = MyLineEdit('0')
        bin_Edit             = MyLineEdit('50')
        bin_frac_Edit        = MyLineEdit('0.25')
        Iter_Edit            = MyLineEdit('5')

        # --- Checkboxes --- #
        self.Upper_limit_checkbox        = QtWidgets.QCheckBox("Upper Limit - Apparent Velocity")
        self.ellip_veloc_checkbox        = QtWidgets.QCheckBox("Elliptical Velocity Anisotropy")
        self.tilted_ellip_veloc_checkbox = QtWidgets.QCheckBox("Tilted Elliptical Velocity Anisotropy")
        self.include_checkbox            = QtWidgets.QCheckBox("Include Experimental Variance")
        self.slowness_checkbox           = QtWidgets.QCheckBox()
        self.traveltime_checkbox         = QtWidgets.QCheckBox()
        self.xi_checkbox                 = QtWidgets.QCheckBox()
        self.tilt_checkbox               = QtWidgets.QCheckBox()
        self.auto_update_checkbox        = QtWidgets.QCheckBox("Auto Update")

        # --- Text Edits --- #
        futur_Graph1 = QtWidgets.QTextEdit()
        futur_Graph1.setReadOnly(True)
        futur_Graph2 = QtWidgets.QTextEdit()
        futur_Graph2.setReadOnly(True)

        # --- Comboboxes --- #
        self.T_and_A_combo      = QtWidgets.QComboBox()
        self.T_and_A_combo.addItem("Traveltime")
        self.T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        self.T_and_A_combo.addItem("Amplitude - Centroid Frequency")
        self.curv_rays_combo    = QtWidgets.QComboBox()
        self.covar_struct_combo = QtWidgets.QComboBox()

        # --- List --- #
        self.models_list = QtWidgets.QListWidget()

        # ------- Actions ------- #
        # --- Buttons --- #
        self.btn_Show_Stats.clicked.connect(self.show_stats)
        self.btn_Add_Struct.clicked.connect(self.add_struct)
        self.btn_Rem_Struct.clicked.connect(self.del_struct)
        self.btn_Ren_Struct.clicked.connect(self.ren_struct)
        self.btn_compute   .clicked.connect(self.compute)
        self.btn_GO        .clicked.connect(self.adjust)

        # --- Edits --- #
        velocity_Edit       .textModified.connect(self.auto_update)
        step_X_Edit         .textModified.connect(self.auto_update)
        step_Y_Edit         .textModified.connect(self.auto_update)
        step_Z_Edit         .textModified.connect(self.auto_update)
        self.slowness_Edit  .textModified.connect(self.auto_update)
        self.traveltime_Edit.textModified.connect(self.auto_update)
        self.xi_Edit        .textModified.connect(self.auto_update)
        self.tilt_Edit      .textModified.connect(self.auto_update)
        bin_Edit            .textModified.connect(self.auto_update)
        bin_frac_Edit       .textModified.connect(self.auto_update)
        Iter_Edit           .textModified.connect(self.auto_update)

        # --- Checkboxes --- #
        self.Upper_limit_checkbox       .stateChanged.connect(self.auto_update)
        self.ellip_veloc_checkbox       .stateChanged.connect(self.parameters_displayed_update)
        self.tilted_ellip_veloc_checkbox.stateChanged.connect(self.parameters_displayed_update)
        self.include_checkbox           .stateChanged.connect(self.auto_update)
#         self.slowness_checkbox          .stateChanged.connect(self.auto_update)
#         self.traveltime_checkbox        .stateChanged.connect(self.auto_update)
#         self.xi_checkbox                .stateChanged.connect(self.auto_update)
#         self.tilt_checkbox              .stateChanged.connect(self.auto_update)

        # --- Comboboxes --- #
        self.T_and_A_combo     .currentIndexChanged.connect(self.auto_update)
        self.curv_rays_combo   .currentIndexChanged.connect(self.auto_update)
        self.covar_struct_combo.currentIndexChanged.connect(self.parameters_displayed_update)

        # --- List --- #
        self.models_list.itemSelectionChanged.connect(self.update_model)
        self.models_list.itemSelectionChanged.connect(self.parameters_displayed_update)

        # ------- SubWidgets ------- #
        # --- Curved Rays SubWidget --- #
        Sub_Curved_Rays_Widget = QtWidgets.QWidget()
        Sub_Curved_Rays_Grid = QtWidgets.QGridLayout()
        Sub_Curved_Rays_Grid.addWidget(curv_rays_label, 0, 0)
        Sub_Curved_Rays_Grid.addWidget(self.curv_rays_combo, 0, 1)
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
        data_grid.addWidget(self.Upper_limit_checkbox, 0, 1)
        data_grid.addWidget(velocity_Edit, 0, 2)
        data_grid.addWidget(self.ellip_veloc_checkbox, 1, 1)
        data_grid.addWidget(self.tilted_ellip_veloc_checkbox, 2, 1)
        data_grid.addWidget(self.include_checkbox, 3, 1)
        data_grid.addWidget(self.T_and_A_combo, 4, 1)
        data_grid.addWidget(self.btn_Show_Stats, 4, 2)
        data_grid.addWidget(Sub_Curved_Rays_Widget, 5, 1)
        data_groupbox.setLayout(data_grid)

        # --- Grid Groupbox --- #
        Grid_groupbox = QtWidgets.QGroupBox("Grid")
        Grid_grid = QtWidgets.QGridLayout()
        Grid_grid.addWidget(Sub_Grid_Coord_Widget, 0, 0)
        Grid_grid.addWidget(Sub_Step_Widget, 0, 1)
        Grid_groupbox.setLayout(Grid_grid)

        # --- Parameters Groupboxes --- #
        # - Parameters items - #
        types = ('Cubic', 'Spherical', 'Gaussian', 'Exponential', 'Thin_Plate',
                 'Gravimetric', 'Magnetic', 'Hole Effect Sine', 'Hole Effect Cosine')

        range_X_label = MyQLabel("Range X", ha='right')
        range_Z_label = MyQLabel("Range Z", ha='right')
        theta_X_label = MyQLabel("{} X".format(theta), ha='right')
        sill_label    = MyQLabel("Sill", ha='right')

        self.labels_2D_widget = QtWidgets.QWidget()
        labels_2D_grid        = QtWidgets.QGridLayout()
        labels_2D_grid.addWidget(range_X_label, 3, 0)
        labels_2D_grid.addWidget(range_Z_label, 4, 0)
        labels_2D_grid.addWidget(theta_X_label, 5, 0)
        labels_2D_grid.addWidget(sill_label, 6, 0)
        labels_2D_grid.setContentsMargins(0, 0, 0, 0)
        self.labels_2D_widget.setLayout(labels_2D_grid)

        slowness_param_edit       = QtWidgets.QLineEdit('Slowness')
        slowness_type_combo       = QtWidgets.QComboBox()
        slowness_type_combo.addItems(types)
        slowness_value_label      = MyQLabel("Value", ha='center')
        slowness_fix_label        = MyQLabel("Fix", ha='center')
        slowness_range_X_edit     = MyLineEdit('0.0')
        slowness_range_Z_edit     = MyLineEdit('0.0')
        slowness_theta_X_edit     = MyLineEdit('0.0')
        slowness_sill_edit        = MyLineEdit('0.0')
        slowness_range_X_checkbox = QtWidgets.QCheckBox()
        slowness_range_Z_checkbox = QtWidgets.QCheckBox()
        slowness_theta_X_checkbox = QtWidgets.QCheckBox()
        slowness_sill_checkbox    = QtWidgets.QCheckBox()

        self.slowness_widget      = QtWidgets.QWidget()
        slowness_grid             = QtWidgets.QGridLayout()
        slowness_grid.addWidget(slowness_param_edit, 0, 0, 1, 2)
        slowness_grid.addWidget(slowness_type_combo, 1, 0, 1, 2)
        slowness_grid.addWidget(slowness_value_label, 2, 0)
        slowness_grid.addWidget(slowness_fix_label, 2, 1)
        slowness_grid.addWidget(slowness_range_X_edit, 3, 0)
        slowness_grid.addWidget(slowness_range_Z_edit, 4, 0)
        slowness_grid.addWidget(slowness_theta_X_edit, 5, 0)
        slowness_grid.addWidget(slowness_sill_edit, 6, 0)
        slowness_grid.addWidget(slowness_range_X_checkbox, 3, 1)
        slowness_grid.addWidget(slowness_range_Z_checkbox, 4, 1)
        slowness_grid.addWidget(slowness_theta_X_checkbox, 5, 1)
        slowness_grid.addWidget(slowness_sill_checkbox, 6, 1)
        slowness_grid.setContentsMargins(0, 0, 0, 0)
        self.slowness_widget.setLayout(slowness_grid)

        xi_param_edit       = QtWidgets.QLineEdit(xi)
        xi_type_combo       = QtWidgets.QComboBox()
        xi_type_combo.addItems(types)
        xi_value_label      = MyQLabel("Value", ha='center')
        xi_fix_label        = MyQLabel("Fix", ha='center')
        xi_range_X_edit     = MyLineEdit('0.0')
        xi_range_Z_edit     = MyLineEdit('0.0')
        xi_theta_X_edit     = MyLineEdit('0.0')
        xi_sill_edit        = MyLineEdit('0.0')
        xi_range_X_checkbox = QtWidgets.QCheckBox()
        xi_range_Z_checkbox = QtWidgets.QCheckBox()
        xi_theta_X_checkbox = QtWidgets.QCheckBox()
        xi_sill_checkbox    = QtWidgets.QCheckBox()

        self.xi_widget      = QtWidgets.QWidget()
        xi_grid             = QtWidgets.QGridLayout()
        xi_grid.addWidget(xi_param_edit, 0, 0, 1, 2)
        xi_grid.addWidget(xi_type_combo, 1, 0, 1, 2)
        xi_grid.addWidget(xi_value_label, 2, 0)
        xi_grid.addWidget(xi_fix_label, 2, 1)
        xi_grid.addWidget(xi_range_X_edit, 3, 0)
        xi_grid.addWidget(xi_range_Z_edit, 4, 0)
        xi_grid.addWidget(xi_theta_X_edit, 5, 0)
        xi_grid.addWidget(xi_sill_edit, 6, 0)
        xi_grid.addWidget(xi_range_X_checkbox, 3, 1)
        xi_grid.addWidget(xi_range_Z_checkbox, 4, 1)
        xi_grid.addWidget(xi_theta_X_checkbox, 5, 1)
        xi_grid.addWidget(xi_sill_checkbox, 6, 1)
        xi_grid.setContentsMargins(0, 0, 0, 0)
        self.xi_widget.setLayout(xi_grid)

        tilt_param_edit       = QtWidgets.QLineEdit('Tilt Angle')
        tilt_type_combo       = QtWidgets.QComboBox()
        tilt_type_combo.addItems(types)
        tilt_value_label      = MyQLabel("Value", ha='center')
        tilt_fix_label        = MyQLabel("Fix", ha='center')
        tilt_range_X_edit     = MyLineEdit('0.0')
        tilt_range_Z_edit     = MyLineEdit('0.0')
        tilt_theta_X_edit     = MyLineEdit('0.0')
        tilt_sill_edit        = MyLineEdit('0.0')
        tilt_range_X_checkbox = QtWidgets.QCheckBox()
        tilt_range_Z_checkbox = QtWidgets.QCheckBox()
        tilt_theta_X_checkbox = QtWidgets.QCheckBox()
        tilt_sill_checkbox    = QtWidgets.QCheckBox()

        self.tilt_widget      = QtWidgets.QWidget()
        tilt_grid             = QtWidgets.QGridLayout()
        tilt_grid.addWidget(tilt_param_edit, 0, 0, 1, 2)
        tilt_grid.addWidget(tilt_type_combo, 1, 0, 1, 2)
        tilt_grid.addWidget(tilt_value_label, 2, 0)
        tilt_grid.addWidget(tilt_fix_label, 2, 1)
        tilt_grid.addWidget(tilt_range_X_edit, 3, 0)
        tilt_grid.addWidget(tilt_range_Z_edit, 4, 0)
        tilt_grid.addWidget(tilt_theta_X_edit, 5, 0)
        tilt_grid.addWidget(tilt_sill_edit, 6, 0)
        tilt_grid.addWidget(tilt_range_X_checkbox, 3, 1)
        tilt_grid.addWidget(tilt_range_Z_checkbox, 4, 1)
        tilt_grid.addWidget(tilt_theta_X_checkbox, 5, 1)
        tilt_grid.addWidget(tilt_sill_checkbox, 6, 1)
        tilt_grid.setContentsMargins(0, 0, 0, 0)
        self.tilt_widget.setLayout(tilt_grid)

        range_X_3D_label = MyQLabel("Range X", ha='right')
        range_Y_3D_label = MyQLabel("Range Y", ha='right')
        range_Z_3D_label = MyQLabel("Range Z", ha='right')
        theta_X_3D_label = MyQLabel("{} X".format(theta), ha='right')
        theta_Y_3D_label = MyQLabel("{} Y".format(theta), ha='right')
        theta_Z_3D_label = MyQLabel("{} Z".format(theta), ha='right')
        sill_3D_label    = MyQLabel("Sill", ha='right')

        slowness_3D_param_edit       = QtWidgets.QLineEdit('Slowness')
        slowness_3D_type_combo       = QtWidgets.QComboBox()
        slowness_3D_type_combo.addItems(types)
        slowness_3D_value_label      = MyQLabel("Value", ha='center')
        slowness_3D_fix_label        = MyQLabel("Fix", ha='center')
        slowness_3D_range_X_edit     = MyLineEdit('0.0')
        slowness_3D_range_Y_edit     = MyLineEdit('0.0')
        slowness_3D_range_Z_edit     = MyLineEdit('0.0')
        slowness_3D_theta_X_edit     = MyLineEdit('0.0')
        slowness_3D_theta_Y_edit     = MyLineEdit('0.0')
        slowness_3D_theta_Z_edit     = MyLineEdit('0.0')
        slowness_3D_sill_edit        = MyLineEdit('0.0')
        slowness_3D_range_X_checkbox = QtWidgets.QCheckBox()
        slowness_3D_range_Y_checkbox = QtWidgets.QCheckBox()
        slowness_3D_range_Z_checkbox = QtWidgets.QCheckBox()
        slowness_3D_theta_X_checkbox = QtWidgets.QCheckBox()
        slowness_3D_theta_Y_checkbox = QtWidgets.QCheckBox()
        slowness_3D_theta_Z_checkbox = QtWidgets.QCheckBox()
        slowness_3D_sill_checkbox    = QtWidgets.QCheckBox()

        self.slowness_3D_widget      = QtWidgets.QWidget()
        slowness_3D_grid             = QtWidgets.QGridLayout()
        slowness_3D_grid.addWidget(slowness_3D_param_edit, 0, 1, 2, 1)
        slowness_3D_grid.addWidget(slowness_3D_type_combo, 1, 1, 2, 1)
        slowness_3D_grid.addWidget(slowness_3D_value_label, 2, 1)
        slowness_3D_grid.addWidget(slowness_3D_fix_label, 2, 2)
        slowness_3D_grid.addWidget(range_X_3D_label, 3, 0)
        slowness_3D_grid.addWidget(range_Y_3D_label, 4, 0)
        slowness_3D_grid.addWidget(range_Z_3D_label, 5, 0)
        slowness_3D_grid.addWidget(theta_X_3D_label, 6, 0)
        slowness_3D_grid.addWidget(theta_Y_3D_label, 7, 0)
        slowness_3D_grid.addWidget(theta_Z_3D_label, 8, 0)
        slowness_3D_grid.addWidget(sill_3D_label, 9, 0)
        slowness_3D_grid.addWidget(slowness_3D_range_X_edit, 3, 1)
        slowness_3D_grid.addWidget(slowness_3D_range_Y_edit, 4, 1)
        slowness_3D_grid.addWidget(slowness_3D_range_Z_edit, 5, 1)
        slowness_3D_grid.addWidget(slowness_3D_theta_X_edit, 6, 1)
        slowness_3D_grid.addWidget(slowness_3D_theta_Y_edit, 7, 1)
        slowness_3D_grid.addWidget(slowness_3D_theta_Z_edit, 8, 1)
        slowness_3D_grid.addWidget(slowness_3D_sill_edit, 9, 1)
        slowness_3D_grid.addWidget(slowness_3D_range_X_checkbox, 3, 2)
        slowness_3D_grid.addWidget(slowness_3D_range_Y_checkbox, 4, 2)
        slowness_3D_grid.addWidget(slowness_3D_range_Z_checkbox, 5, 2)
        slowness_3D_grid.addWidget(slowness_3D_theta_X_checkbox, 6, 2)
        slowness_3D_grid.addWidget(slowness_3D_theta_Y_checkbox, 7, 2)
        slowness_3D_grid.addWidget(slowness_3D_theta_Z_checkbox, 8, 2)
        slowness_3D_grid.addWidget(slowness_3D_sill_checkbox, 9, 2)
        slowness_3D_grid.setContentsMargins(0, 0, 0, 0)
        self.slowness_3D_widget.setLayout(slowness_3D_grid)

        # - Groupbox - #
        Param_groupbox = QtWidgets.QGroupBox("Parameters")
        Param_grid = QtWidgets.QGridLayout()
        Param_grid.addWidget(self.labels_2D_widget, 0, 1, 7, 1)
        Param_grid.addWidget(self.slowness_widget, 0, 2, 7, 1)
        Param_grid.addWidget(self.xi_widget, 0, 3, 7, 1)
        Param_grid.addWidget(self.tilt_widget, 0, 4, 7, 1)
        Param_grid.addWidget(self.slowness_3D_widget, 0, 5)
        Param_grid.setColumnStretch(0, 1)
        Param_grid.setColumnStretch(1, 0)
        Param_grid.setColumnStretch(2, 0)
        Param_grid.setColumnStretch(3, 0)
        Param_grid.setColumnStretch(4, 0)
        Param_grid.setColumnStretch(5, 0)
        Param_grid.setColumnStretch(6, 1)
        Param_groupbox.setLayout(Param_grid)

        # --- Nugget Effect Groupbox --- #
        Nug_groupbox = QtWidgets.QGroupBox("Nugget Effect")
        Nug_grid = QtWidgets.QGridLayout()
        Nug_grid.addWidget(self.slowness_label, 0, 0)
        Nug_grid.addWidget(self.slowness_Edit, 0, 1)
        Nug_grid.addWidget(self.slowness_checkbox, 0, 2)
        Nug_grid.addWidget(self.traveltime_label, 0, 3)
        Nug_grid.addWidget(self.traveltime_Edit, 0, 4)
        Nug_grid.addWidget(self.traveltime_checkbox, 0, 5)
        Nug_grid.addWidget(self.xi_label, 1, 0)
        Nug_grid.addWidget(self.xi_Edit, 1, 1)
        Nug_grid.addWidget(self.xi_checkbox, 1, 2)
        Nug_grid.addWidget(self.tilt_label, 1, 3)
        Nug_grid.addWidget(self.tilt_Edit, 1, 4)
        Nug_grid.addWidget(self.tilt_checkbox, 1, 5)
        Nug_groupbox.setLayout(Nug_grid)

        # --- Covariance Model Groupbox --- #
        covar_groupbox = QtWidgets.QGroupBox("Covariance Model")
        covar_grid = QtWidgets.QGridLayout()
        covar_grid.addWidget(self.covar_struct_combo, 0, 0)
        covar_grid.addWidget(self.btn_Add_Struct, 0, 1)
        covar_grid.addWidget(self.btn_Rem_Struct, 0, 2)
        covar_grid.addWidget(self.btn_Ren_Struct, 0, 3)
        covar_grid.addWidget(Param_groupbox, 1, 0, 1, 4)
        covar_grid.addWidget(Nug_groupbox, 2, 0, 1, 4)
        covar_grid.addWidget(self.auto_update_checkbox, 3, 0, 1, 2)
        covar_grid.addWidget(self.btn_compute, 3, 2, 1, 2)
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
        Adjust_Model_grid.addWidget(self.btn_GO, 0, 3, 3, 1)
#         Adjust_Model_grid.setColumnStretch(4, 100)
        Adjust_Model_groupbox.setLayout(Adjust_Model_grid)

        # --- Subgrid --- #

        self.Sub_widget = QtWidgets.QWidget()
        Sub_grid        = QtWidgets.QGridLayout()
        Sub_grid.addWidget(data_groupbox, 0, 0)
        Sub_grid.addWidget(Grid_groupbox, 1, 0)
        Sub_grid.addWidget(covar_groupbox, 2, 0)
        Sub_grid.addWidget(Adjust_Model_groupbox, 3, 0)
        Sub_grid.setContentsMargins(0, 0, 0, 0)
        self.Sub_widget.setLayout(Sub_grid)

        # --- Scroll bar --- #

        self.scrollbar_widget = QtWidgets.QWidget()
        self.scrollbar_grid   = QtWidgets.QGridLayout()
        self.scrollbar_grid.addWidget(futur_Graph1, 0, 0, 2, 3)
        self.scrollbar_grid.addWidget(futur_Graph2, 2, 0, 2, 3)
        self.scrollbar_grid.addWidget(self.Sub_widget, 0, 3, 4, 1)
        self.scrollbar_grid.setContentsMargins(0, 0, 0, 0)
        self.scrollbar_grid.setColumnStretch(1, 1)
        self.scrollbar_grid.setColumnStretch(3, 0)
        self.scrollbar_grid.setColumnMinimumWidth(0, 600)
        self.scrollbar_widget.setLayout(self.scrollbar_grid)

        self.scrollbar = QtWidgets.QScrollArea()
        self.scrollbar.setWidget(self.scrollbar_widget)
        self.scrollbar.setWidgetResizable(True)

        # ------- Master Grid Disposition ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0)
        master_grid.addWidget(self.scrollbar, 1, 0)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)

        # ------- Actions ------- #

        for item in (slowness_range_X_edit, slowness_range_Z_edit, slowness_theta_X_edit, slowness_sill_edit,
                     xi_range_X_edit, xi_range_Z_edit, xi_theta_X_edit, xi_sill_edit,
                     tilt_range_X_edit, tilt_range_Z_edit, tilt_theta_X_edit, tilt_sill_edit,
                     slowness_3D_range_X_edit, slowness_3D_range_Y_edit, slowness_3D_range_Z_edit,
                     slowness_3D_theta_X_edit, slowness_3D_theta_Y_edit, slowness_3D_theta_Z_edit, slowness_3D_sill_edit):
            item.textModified.connect(self.auto_update)

        # ------- Sizes ------- #
        self.menu            .setFixedHeight(self.menu.sizeHint().height())
        data_groupbox        .setFixedHeight(data_groupbox.sizeHint().height())
        Grid_groupbox        .setFixedHeight(Grid_groupbox.sizeHint().height())
        Param_groupbox       .setFixedHeight(Param_groupbox.sizeHint().height())
        Nug_groupbox         .setFixedHeight(Nug_groupbox.sizeHint().height())
        Adjust_Model_groupbox.setFixedHeight(Adjust_Model_groupbox.sizeHint().height())
        self.Sub_widget      .setFixedWidth(500)

        screen_resolution = QtWidgets.QApplication.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()

        desired_min_height = (data_groupbox.sizeHint().height() + Grid_groupbox.sizeHint().height() +
                              Param_groupbox.sizeHint().height() + Nug_groupbox.sizeHint().height() +
                              Nug_groupbox.sizeHint().height())
        desired_min_width  = 500 * 2.5

        if desired_min_height > 4 / 5 * height:
            desired_min_height = 4 / 5 * height

        if desired_min_width > 4 / 5 * width:
            desired_min_width = 4 / 5 * width

        self.scrollbar.setMinimumWidth(desired_min_width)
        self.scrollbar.setMinimumHeight(desired_min_height)

        for item in (labels_2D_grid, slowness_grid, xi_grid, tilt_grid):
            for i in range(0, 7):
                item.setRowMinimumHeight(i, 25)
            item.setVerticalSpacing(0)

        labels_2D_grid.setRowMinimumHeight(0, 25 * 3 - 10)

        # Peut-être que c'est à cause du stretch?

        for item in (slowness_value_label, xi_value_label, tilt_value_label, slowness_3D_value_label,
                     slowness_fix_label, xi_fix_label, tilt_fix_label, slowness_3D_fix_label,
                     range_X_label, range_Z_label, theta_X_label, sill_label):
            item.setFixedHeight(25)

#         for item in (slowness_param_edit, slowness_type_combo, xi_param_edit,
#                      xi_type_combo, tilt_param_edit, tilt_type_combo,
#                      slowness_3D_param_edit, slowness_3D_type_combo):
#             item.setFixedWidth(110)
#
#         for item in (range_X_label, range_Z_label, theta_X_label, sill_label,
#                      range_X_3D_label, range_Y_3D_label, range_Z_3D_label,
#                      theta_X_3D_label, theta_Y_3D_label, theta_Z_3D_label, sill_3D_label):
#             item.setFixedWidth(50)

#         for item in (slowness_value_label, slowness_range_X_edit, slowness_range_Z_edit, slowness_theta_X_edit, slowness_sill_edit,
#                      xi_value_label, xi_range_X_edit, xi_range_Z_edit, xi_theta_X_edit, xi_sill_edit,
#                      tilt_value_label, tilt_range_X_edit, tilt_range_Z_edit, tilt_theta_X_edit, tilt_sill_edit,
#                      slowness_3D_value_label, slowness_3D_range_X_edit, slowness_3D_range_Y_edit, slowness_3D_range_Z_edit,
#                      slowness_3D_theta_X_edit, slowness_3D_theta_Y_edit, slowness_3D_theta_Z_edit, slowness_3D_sill_edit):
#             item.setFixedWidth(110 - slowness_fix_label.sizeHint().width())

#         for item in (slowness_fix_label, slowness_range_X_checkbox, slowness_range_Z_checkbox,
#                      slowness_theta_X_checkbox, slowness_sill_checkbox,
#                      xi_fix_label, xi_range_X_checkbox, xi_range_Z_checkbox,
#                      xi_theta_X_checkbox, xi_sill_checkbox,
#                      tilt_fix_label, tilt_range_X_checkbox, tilt_range_Z_checkbox,
#                      tilt_theta_X_checkbox, tilt_sill_checkbox,
#                      slowness_3D_fix_label, slowness_3D_range_X_checkbox, slowness_3D_range_Y_checkbox,
#                      slowness_3D_range_Z_checkbox, slowness_3D_theta_X_checkbox, slowness_3D_theta_Y_checkbox,
#                      slowness_3D_theta_Z_checkbox, slowness_3D_sill_checkbox):
#             item.setFixedWidth(slowness_fix_label.sizeHint().width())


def save_warning():
    d = QtWidgets.QDialog()

    l0 = QtWidgets.QLabel(parent=d)
    l0.setAlignment(QtCore.Qt.AlignCenter)
    l0.setStyleSheet('background-color: white')

    b0 = QtWidgets.QPushButton("Save", d)
    b1 = QtWidgets.QPushButton("Save as", d)
    b2 = QtWidgets.QPushButton("Discard changes", d)
    b3 = QtWidgets.QPushButton("Cancel", d)

    l0.move(10, 10)
    b0.setMinimumWidth(b0.width())
    b1.setMinimumWidth(b0.width())
    b2.setMinimumWidth(b0.width())
    b3.setMinimumWidth(b0.width())
    b0.move(15, 40)
    b1.move(15 + b0.minimumWidth(), 40)
    b2.move(15 + 2 * b0.minimumWidth(), 40)
    b3.move(15 + 3 * b0.minimumWidth(), 40)
    l0.setMinimumWidth(10 + 4 * b1.minimumWidth())
    d.setMaximumWidth(10 * 3 + b0.width() * 4)
    d.setMaximumHeight(10 * 2 + b0.height() * 2)
    d.setMinimumWidth(10 * 3 + b0.width() * 4)
    d.setMinimumHeight(10 * 2 + b0.height() * 2)

    l0.setText("You must save your database before proceeding.")

    d.setWindowTitle("Warning")
    d.setWindowModality(QtCore.Qt.ApplicationModal)

    def save():
        nonlocal d
        d.done(1)

    def save_as():
        nonlocal d
        d.done(2)

    def no_save():
        nonlocal d
        d.done(3)

    def cancel():
        nonlocal d
        d.done(0)

    b0.clicked.connect(save)
    b1.clicked.connect(save_as)
    b2.clicked.connect(no_save)
    b3.clicked.connect(cancel)

    return d.exec_()


class MyLineEdit(QtWidgets.QLineEdit):  # allows veryfying if an edit's text has been modified
    textModified = QtCore.pyqtSignal(str, str)  # (before, after)

    def __init__(self, contents='', parent=None):
        super(MyLineEdit, self).__init__(contents, parent)
        self.editingFinished.connect(self.checkText)
        self.textChanged.connect(lambda: self.checkText())
        self.returnPressed.connect(lambda: self.checkText(True))
        self._before = contents

    def checkText(self, _return=False):
        if (not self.hasFocus() or _return) and self._before != self.text():
            self._before = self.text()
            self.textModified.emit(self._before, self.text())


if __name__ == '__main__':

    database.create_data_management(database)
#     database.load(database, 'database.db')
    database.load(database, 'db.db')

    app = QtWidgets.QApplication(sys.argv)

    Covar_ui = CovarUI()
    Covar_ui.show()

    sys.exit(app.exec_())

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
from model import Model
import covar
import database
import utils_ui
import grid
from sqlalchemy.orm.attributes import flag_modified

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mpl_toolkits.axes_grid1 import make_axes_locatable
# from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


class CovarUI(QtWidgets.QFrame):

    model = None  # current model
    temp_grid = None
    updateHandler = False  # selected model may seldom be modified twice. 'updateHandler' prevents functions from firing more than once. TODO: use a QValidator instead.

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

        self.reset_data()
        self.update_model()
        self.parameters_displayed_update()
        self.update_velocity_display()

    def openfile(self):

        if utils_ui.save_warning(database):
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Database')[0]

            if filename:
                    if filename[-3:] != '.db':
                        QtWidgets.QMessageBox.warning(self, 'Warning', "Database has wrong extension.", buttons=QtWidgets.QMessageBox.Ok)
                    else:
                        try:
                            database.load(database, filename)
                            self.reset_data()
                            self.update_model()
                            self.parameters_displayed_update()

                        except Exception as e:
                            QtWidgets.QMessageBox.warning(self, 'Warning', "Database could not be opened : '" + str(e)[:42] +
                                                          "...' File may be empty or corrupted.", buttons=QtWidgets.QMessageBox.Ok)

    def savefile(self):
        return utils_ui.savefile(database)

    def saveasfile(self):
        return utils_ui.saveasfile(database)

    def set_current_model(self):  # substitutes SQLAlchemy weak referencing for a strong referencing
        if self.updateHandler:
            return

        self.updateHandler = True
        if self.model is not None:
            if utils_ui.save_warning(database):
                self.model = self.current_model()
                self.updateHandler = False
            else:
                for i in range(self.models_list.count()):
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

    def current_covar(self):

        if self.model is not None:

            if self.T_and_A_combo.currentIndex() == 0:
                covariance = self.model.tt_covar
            else:
                covariance = self.model.amp_covar

            return covariance

    def current_struct(self):

        ind = self.covar_struct_combo.currentIndex()

        if ind != -1:
            return self.current_covar()[ind]

    def flag_modified_covar(self):

        if self.model is not None:

            if self.T_and_A_combo.currentIndex() == 0:
                flag_modified(self.model, 'tt_covar')
            else:
                flag_modified(self.model, 'amp_covar')

    def parameters_displayed_update(self):

        if self.updateHandler:
            return

        self.updateHandler = True

        self.Sub_widget.setDisabled(True)

        self.labels_2D_widget           .setHidden(True)
        self.slowness_widget            .setHidden(True)
        self.xi_widget                  .setHidden(True)
        self.tilt_widget                .setHidden(True)
        self.slowness_3D_widget         .setHidden(True)
        self.ellip_veloc_checkbox       .setDisabled(True)
        self.tilted_ellip_veloc_checkbox.setDisabled(True)

        self.covar_struct_combo.setDisabled(True)
        self.btn_Add_Struct    .setDisabled(True)
        self.btn_Rem_Struct    .setDisabled(True)

        self.xi_label   .setHidden(True)
        self.xi_edit    .setHidden(True)
        self.xi_checkbox.setHidden(True)

        self.tilt_label   .setHidden(True)
        self.tilt_edit    .setHidden(True)
        self.tilt_checkbox.setHidden(True)

        self.Nug_groupbox        .setDisabled(True)
        self.auto_update_checkbox.setDisabled(True)
        self.btn_compute         .setDisabled(True)

        self.Grid_groupbox.setDisabled(True)

        self.Adjust_Model_groupbox.setDisabled(True)

        if database.session.query(Model).first() is not None:

            self.Sub_widget.setDisabled(False)

            if self.model:

                if self.model.grid is not None:
                    self.covar_struct_combo.setDisabled(False)
                    self.btn_Add_Struct    .setDisabled(False)
                    self.Grid_groupbox     .setDisabled(False)

                    if self.current_covar():
                        self.btn_Rem_Struct       .setDisabled(False)
                        self.Nug_groupbox         .setDisabled(False)
                        self.auto_update_checkbox .setDisabled(False)
                        self.btn_compute          .setDisabled(False)
                        self.Adjust_Model_groupbox.setDisabled(False)

                        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                            self.labels_2D_widget    .setHidden(False)
                            self.slowness_widget     .setHidden(False)
                            self.ellip_veloc_checkbox.setDisabled(False)

                            if self.ellip_veloc_checkbox.checkState():
                                self.xi_widget                  .setHidden(False)
                                self.tilted_ellip_veloc_checkbox.setDisabled(False)

                                self.xi_label   .setHidden(False)
                                self.xi_edit    .setHidden(False)
                                self.xi_checkbox.setHidden(False)

                                if self.tilted_ellip_veloc_checkbox.checkState():
                                    self.tilt_widget.setHidden(False)

                                    self.tilt_label   .setHidden(False)
                                    self.tilt_edit    .setHidden(False)
                                    self.tilt_checkbox.setHidden(False)

                            else:
                                self.tilted_ellip_veloc_checkbox.setCheckState(False)

                        elif self.model.grid.type == '3D':
                            self.slowness_3D_widget.setHidden(False)

                    else:
                        self.ellip_veloc_checkbox       .setCheckState(False)
                        self.tilted_ellip_veloc_checkbox.setCheckState(False)

                else:
                    QtWidgets.QMessageBox.warning(self, "Warning", "This model has no grid.")
            else:
                self.ellip_veloc_checkbox       .setCheckState(False)
                self.tilted_ellip_veloc_checkbox.setCheckState(False)

            self.update_parameters()

        else:
            self.ellip_veloc_checkbox       .setCheckState(False)
            self.tilted_ellip_veloc_checkbox.setCheckState(False)

        self.updateHandler = False

    def auto_update(self):
        if self.auto_update_checkbox.checkState():
            self.compute()

    def reset_data(self):
        self.updateHandler = True
        self.model = None
        self.models_list.clear()
        self.models_list.addItems([item.name for item in database.session.query(Model).all()])
        self.updateHandler = False
        self.reset_grid()

    def update_model(self):
        self.btn_Rem_Struct.setDisabled(True)
        self.covar_struct_combo.clear()
        if self.models_list.currentItem():
            self.set_current_model()
            if self.model is not None:
                if self.model.grid is not None:
                    self.update_structures()
                    if self.temp_grid is None:
                        self.cells_no_label.setText(str(self.model.grid.getNumberOfCells()))
                        self.rays_no_label.setText('0')  # TODO
                        self.reset_grid()
                else:
                    self.cells_no_label.setText('0')
                    self.rays_no_label.setText('0')
                    self.reset_grid()
            else:
                self.reset_grid()
        else:
            self.reset_grid()

    def update_structures(self):
        self.covar_struct_combo.clear()
        current_list = self.current_covar()
        if current_list:
            self.covar_struct_combo.addItems(["Structure no " + str(i + 1) for i in range(len(current_list))])
            self.covar_struct_combo.setCurrentIndex(0)
            self.update_parameters()
            self.btn_Rem_Struct.setDisabled(False)

    def new_grid(self):
        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
            self.temp_grid = grid.Grid2D()
        elif self.model.grid.type == '3D':
            self.temp_grid = grid.Grid3D()  # TODO
        else:
            self.temp_grid = None

    def reset_grid(self):
        if self.model is None or self.model.grid is None:
            self.X_min_label.setText('0')
            self.Y_min_label.setText('0')
            self.Z_min_label.setText('0')
            self.X_max_label.setText('0')
            self.Y_max_label.setText('0')
            self.Z_max_label.setText('0')
            self.step_X_edit.setText('')
            self.step_Y_edit.setText('')
            self.step_Z_edit.setText('')
            self.temp_grid = None
        else:
            self.new_grid()
#             self.X_min_label.setText('0')  # the grid's TODO
#             self.Y_min_label.setText('0')
#             self.Z_min_label.setText('0')
#             self.X_max_label.setText('0')
#             self.Y_max_label.setText('0')
#             self.Z_max_label.setText('0')
#             self.step_X_edit.setText('')
#             self.step_Y_edit.setText('')
#             self.step_Z_edit.setText('')

    def update_grid(self):
        pass

    def update_parameters(self):

        struct = self.current_struct()

        if struct is not None:

            if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                self.slowness_type_combo  .setCurrentIndex(struct.slowness.type)
                self.slowness_range_X_edit.setText(str(struct.slowness.range[0]))
                self.slowness_range_Z_edit.setText(str(struct.slowness.range[1]))
                self.slowness_theta_X_edit.setText(str(struct.slowness.angle[0]))
                self.slowness_sill_edit   .setText(str(struct.slowness.sill))
                self.slowness_edit        .setText(str(struct.nugget_slowness))
                self.traveltime_edit      .setText(str(struct.nugget_traveltime))

                if self.ellip_veloc_checkbox.checkState():
                    if struct.xi is None:
                        struct.xi = covar.CovarianceModels.detDefault2D()
                    self.xi_type_combo  .setCurrentIndex(struct.xi.type)
                    self.xi_range_X_edit.setText(str(struct.xi.range[0]))
                    self.xi_range_Z_edit.setText(str(struct.xi.range[1]))
                    self.xi_theta_X_edit.setText(str(struct.xi.angle[0]))
                    self.xi_sill_edit   .setText(str(struct.xi.sill))
                    self.xi_edit        .setText(str(struct.nugget_xi))

                    if self.tilted_ellip_veloc_checkbox.checkState():
                        if struct.tilt is None:
                            struct.tilt = covar.CovarianceModels.detDefault2D()
                        self.tilt_type_combo  .setCurrentIndex(struct.tilt.type)
                        self.tilt_range_X_edit.setText(str(struct.tilt.range[0]))
                        self.tilt_range_Z_edit.setText(str(struct.tilt.range[1]))
                        self.tilt_theta_X_edit.setText(str(struct.tilt.angle[0]))
                        self.tilt_sill_edit   .setText(str(struct.tilt.sill))
                        self.tilt_edit        .setText(str(struct.nugget_tilt))

            elif self.model.grid.type == '3D':
                self.slowness_3D_type_combo  .setCurrentIndex(struct.slowness.type)
                self.slowness_3D_range_X_edit.setText(str(struct.slowness.range[0]))
                self.slowness_3D_range_Y_edit.setText(str(struct.slowness.range[1]))
                self.slowness_3D_range_Z_edit.setText(str(struct.slowness.range[2]))
                self.slowness_3D_theta_X_edit.setText(str(struct.slowness.angle[0]))
                self.slowness_3D_theta_Y_edit.setText(str(struct.slowness.angle[1]))
                self.slowness_3D_theta_Z_edit.setText(str(struct.slowness.angle[2]))
                self.slowness_3D_sill_edit   .setText(str(struct.slowness.sill))
                self.slowness_edit           .setText(str(struct.nugget_slowness))
                self.traveltime_edit         .setText(str(struct.nugget_traveltime))

    def apply_parameters_changes(self):

        struct = self.current_struct()

        if struct is not None:

            if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                struct.slowness.range[0] = self.slowness_range_X_edit.text()
                struct.slowness.range[1] = self.slowness_range_Z_edit.text()
                struct.slowness.angle[0] = self.slowness_theta_X_edit.text()
                struct.slowness.sill     = self.slowness_sill_edit   .text()
                struct.nugget_slowness   = self.slowness_edit        .text()
                struct.nugget_traveltime = self.traveltime_edit      .text()

                if self.ellip_veloc_checkbox.checkState():
                    if struct.xi is None:
                        struct.xi = covar.CovarianceModels.detDefault2D()
                    struct.xi.range[0] = self.xi_range_X_edit.text()
                    struct.xi.range[1] = self.xi_range_Z_edit.text()
                    struct.xi.angle[0] = self.xi_theta_X_edit.text()
                    struct.xi.sill     = self.xi_sill_edit   .text()
                    struct.nugget_xi   = self.xi_edit        .text()

                    if self.tilted_ellip_veloc_checkbox.checkState():
                        if struct.tilt is None:
                            struct.tilt = covar.CovarianceModels.detDefault2D()
                        struct.tilt.range[0] = self.tilt_range_X_edit.text()
                        struct.tilt.range[1] = self.tilt_range_Z_edit.text()
                        struct.tilt.angle[0] = self.tilt_theta_X_edit.text()
                        struct.tilt.sill     = self.tilt_sill_edit   .text()
                        struct.nugget_tilt   = self.tilt_edit        .text()

            elif self.model.grid.type == '3D':
                struct.slowness.range[0] = self.slowness_3D_range_X_edit.text()
                struct.slowness.range[1] = self.slowness_3D_range_Y_edit.text()
                struct.slowness.range[2] = self.slowness_3D_range_Z_edit.text()
                struct.slowness.angle[0] = self.slowness_3D_theta_X_edit.text()
                struct.slowness.angle[1] = self.slowness_3D_theta_Y_edit.text()
                struct.slowness.angle[2] = self.slowness_3D_theta_Z_edit.text()
                struct.slowness.sill     = self.slowness_3D_sill_edit   .text()
                struct.nugget_slowness   = self.slowness_edit           .text()
                struct.nugget_traveltime = self.traveltime_edit         .text()
        self.flag_modified_covar()
        database.modified = True

    def change_covar_type_slowness(self, ctype):
        covar.CovarianceModels.change_type(self.current_struct().slowness, ctype)
        self.flag_modified_covar()
        database.modified = True

    def change_covar_type_xi(self, ctype):
        covar.CovarianceModels.change_type(self.current_struct().xi, ctype)
        self.flag_modified_covar()
        database.modified = True

    def change_covar_type_tilt(self, ctype):
        covar.CovarianceModels.change_type(self.current_struct().tilt, ctype)
        self.flag_modified_covar()
        database.modified = True

    def change_covar_type_slowness_3D(self, ctype):
        covar.CovarianceModels.change_type(self.current_struct().slowness, ctype)
        self.flag_modified_covar()
        database.modified = True

    def compute(self):  # TODO progress bar
        pass
        # compute

    def show_stats(self):
        if self.model is not None:
            self.statistics_form.show()

    def add_struct(self):
        new = covar.Structure(self.model.grid.type)
        self.current_covar().append(new)
        count = self.covar_struct_combo.count()
        self.covar_struct_combo.addItem('Structure no ' + str(count + 1))
        self.covar_struct_combo.setCurrentIndex(count)
        self.parameters_displayed_update()
        self.update_parameters()
        self.flag_modified_covar()
        database.modified = True

    def del_struct(self):
        index = self.covar_struct_combo.currentIndex()
        del self.current_covar()[index]
        self.covar_struct_combo.clear()
        self.covar_struct_combo.addItems(["Structure no " + str(i + 1) for i in range(len(self.current_covar()))])
        count = self.covar_struct_combo.count()
        if count != 0:
            if index == count:
                self.covar_struct_combo.setCurrentIndex(index - 1)
            else:
                self.covar_struct_combo.setCurrentIndex(index)
        self.parameters_displayed_update()
        self.update_parameters()
        self.flag_modified_covar()
        database.modified = True

    def adjust(self):
        pass

    def fix_verif(self):
        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
            items = [self.slowness_range_X_checkbox, self.slowness_range_Z_checkbox,
                     self.slowness_theta_X_checkbox, self.slowness_sill_checkbox,
                     self.slowness_checkbox, self.traveltime_checkbox]
            if self.ellip_veloc_checkbox.checkState():
                items += [self.xi_range_X_checkbox, self.xi_range_Z_checkbox,
                          self.xi_theta_X_checkbox, self.xi_sill_checkbox,
                          self.xi_checkbox]
                if self.tilted_ellip_veloc_checkbox.checkState():
                    items += [self.tilt_range_X_checkbox, self.tilt_range_Z_checkbox,
                              self.tilt_theta_X_checkbox, self.tilt_sill_checkbox,
                              self.tilt_checkbox]

        elif self.model.grid.type == '3D':
            items = [self.slowness_3D_range_X_checkbox, self.slowness_3D_range_Y_checkbox, self.slowness_3D_range_Z_checkbox,
                     self.slowness_3D_theta_X_checkbox, self.slowness_3D_theta_Y_checkbox, self.slowness_3D_theta_Z_checkbox,
                     self.slowness_3D_sill_checkbox]

        if False in [item.checkState() for item in items]:
            self.btn_GO.setEnabled(True)

        else:
            self.btn_GO.setEnabled(False)
            QtWidgets.QMessageBox.warning(self, "Warning",
                                          "In order to adjust the model, at least one 'Fix' checkbox must be left unchecked.")

    def update_velocity_display(self):

        flag = self.Upper_limit_checkbox.checkState()
        self.velocity_edit.setEnabled(flag)
        if flag:
            self.velocity_edit.setText('0.15')  # TODO model's value instead of default
        else:
            self.velocity_edit.setText('')

    def initUI(self):

        import unicodedata
        xi    = unicodedata.lookup("GREEK SMALL LETTER XI")
        theta = unicodedata.lookup("GREEK SMALL LETTER THETA")

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
        self.btn_compute    = QtWidgets.QPushButton("Compute")
        self.btn_GO         = QtWidgets.QPushButton("GO")

        # --- Labels --- #
        cells_Label          = MyQLabel("Cells", ha='left')
        cells_Labeli         = MyQLabel("Cells", ha='left')
        rays_label           = MyQLabel("Rays", ha='left')
        self.cells_no_label  = MyQLabel("0", ha='right')
        self.cells_no_labeli = MyQLabel("0", ha='right')
        self.rays_no_label   = MyQLabel("0", ha='right')

        curv_rays_label  = MyQLabel("Curved Rays", ha='right')
        X_label          = MyQLabel("X", ha='center')
        Y_label          = MyQLabel("Y", ha='center')
        Z_label          = MyQLabel("Z", ha='center')
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

        self.X_min_label    .setPalette(palette)
        self.Y_min_label    .setPalette(palette)
        self.Z_min_label    .setPalette(palette)
        self.X_max_label    .setPalette(palette)
        self.Y_max_label    .setPalette(palette)
        self.Z_max_label    .setPalette(palette)
        self.cells_no_label .setPalette(palette)
        cells_Label         .setPalette(palette)
        self.cells_no_labeli.setPalette(palette)
        cells_Labeli        .setPalette(palette)
        self.rays_no_label  .setPalette(palette)
        rays_label          .setPalette(palette)

        # --- Edits --- #
        self.velocity_edit = MyLineEdit()
        self.step_X_edit = MyLineEdit()
        self.step_X_edit.setFixedWidth(50)
        self.step_Y_edit = MyLineEdit()
        self.step_Y_edit.setFixedWidth(50)
        self.step_Z_edit = MyLineEdit()
        self.step_Z_edit.setFixedWidth(50)
        self.slowness_edit   = MyLineEdit('0.0')
        self.traveltime_edit = MyLineEdit('0.0')
        self.xi_edit         = MyLineEdit('0.0')
        self.tilt_edit       = MyLineEdit('0.0')
        self.bin_edit        = MyLineEdit('50')
        self.bin_frac_edit   = MyLineEdit('0.25')
        self.Iter_edit       = MyLineEdit('5')

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
        self.covariance_fig = CovarianceFig(self)
        self.comparison_fig = ComparisonFig(self)

        # --- Comboboxes --- #
        self.T_and_A_combo      = QtWidgets.QComboBox()
        self.T_and_A_combo.addItem("Traveltime")
        self.T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        self.T_and_A_combo.addItem("Amplitude - Centroid Frequency")
        self.curv_rays_combo    = QtWidgets.QComboBox()
        self.covar_struct_combo = QtWidgets.QComboBox()

        # --- List --- #
        self.models_list = QtWidgets.QListWidget()

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
        cells_no_widget = QtWidgets.QWidget()
        cells_no_grid   = QtWidgets.QGridLayout()
        cells_no_grid.addWidget(self.cells_no_labeli, 0, 0)
        cells_no_grid.addWidget(cells_Labeli, 0, 1)
        cells_no_widget.setLayout(cells_no_grid)

        Sub_Step_Widget = QtWidgets.QWidget()
        Sub_Step_Grid = QtWidgets.QGridLayout()
        Sub_Step_Grid.addWidget(step_label, 1, 0)
        Sub_Step_Grid.addWidget(self.step_X_edit, 1, 1)
        Sub_Step_Grid.addWidget(self.step_Y_edit, 1, 2)
        Sub_Step_Grid.addWidget(self.step_Z_edit, 1, 3)
        Sub_Step_Grid.addWidget(Xi_label, 0, 1)
        Sub_Step_Grid.addWidget(Yi_label, 0, 2)
        Sub_Step_Grid.addWidget(Zi_label, 0, 3)
        Sub_Step_Grid.addWidget(cells_no_widget, 2, 1, 1, 3)
        Sub_Step_Grid.setHorizontalSpacing(0)
        Sub_Step_Widget.setLayout(Sub_Step_Grid)

        # ------- SubGroupboxes ------- #
        # --- Data Groupbox --- #
        data_groupbox = QtWidgets.QGroupBox("Data")
        data_grid = QtWidgets.QGridLayout()
        data_grid.addWidget(self.cells_no_label, 0, 0)
        data_grid.addWidget(cells_Label, 0, 1)
        data_grid.addWidget(self.rays_no_label, 1, 0)
        data_grid.addWidget(rays_label, 1, 1)
        data_grid.addWidget(self.models_list, 2, 0, 3, 2)
        data_grid.addWidget(self.Upper_limit_checkbox, 0, 2)
        data_grid.addWidget(self.velocity_edit, 0, 3)
        data_grid.addWidget(self.ellip_veloc_checkbox, 1, 2)
        data_grid.addWidget(self.tilted_ellip_veloc_checkbox, 2, 2)
        data_grid.addWidget(self.include_checkbox, 3, 2)
        data_grid.addWidget(self.T_and_A_combo, 4, 2)
        data_grid.addWidget(self.btn_Show_Stats, 4, 3)
        data_grid.addWidget(Sub_Curved_Rays_Widget, 5, 2)
        data_groupbox.setLayout(data_grid)

        # --- Grid Groupbox --- #
        self.Grid_groupbox = QtWidgets.QGroupBox("Grid")
        Grid_grid = QtWidgets.QGridLayout()
        Grid_grid.addWidget(Sub_Grid_Coord_Widget, 0, 0)
        Grid_grid.addWidget(Sub_Step_Widget, 0, 1)
        self.Grid_groupbox.setLayout(Grid_grid)

        # --- Parameters Groupboxes --- #
        # - Parameters items - #
        types = ('Cubic', 'Spherical', 'Gaussian', 'Exponential', 'Linear', 'Thin_Plate',
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
        slowness_param_edit.setReadOnly(True)
        slowness_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.slowness_type_combo       = QtWidgets.QComboBox()
        self.slowness_type_combo.addItems(types)
        slowness_value_label      = MyQLabel("Value", ha='center')
        slowness_fix_label        = MyQLabel("Fix", ha='center')
        self.slowness_range_X_edit     = MyLineEdit('4.0')
        self.slowness_range_Z_edit     = MyLineEdit('4.0')
        self.slowness_theta_X_edit     = MyLineEdit('0.0')
        self.slowness_sill_edit        = MyLineEdit('1.0')
        self.slowness_range_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_range_Z_checkbox = QtWidgets.QCheckBox()
        self.slowness_theta_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_sill_checkbox    = QtWidgets.QCheckBox()

        self.slowness_widget      = QtWidgets.QWidget()
        slowness_grid             = QtWidgets.QGridLayout()
        slowness_grid.addWidget(slowness_param_edit, 0, 0, 1, 2)
        slowness_grid.addWidget(self.slowness_type_combo, 1, 0, 1, 2)
        slowness_grid.addWidget(slowness_value_label, 2, 0)
        slowness_grid.addWidget(slowness_fix_label, 2, 1)
        slowness_grid.addWidget(self.slowness_range_X_edit, 3, 0)
        slowness_grid.addWidget(self.slowness_range_Z_edit, 4, 0)
        slowness_grid.addWidget(self.slowness_theta_X_edit, 5, 0)
        slowness_grid.addWidget(self.slowness_sill_edit, 6, 0)
        slowness_grid.addWidget(self.slowness_range_X_checkbox, 3, 1)
        slowness_grid.addWidget(self.slowness_range_Z_checkbox, 4, 1)
        slowness_grid.addWidget(self.slowness_theta_X_checkbox, 5, 1)
        slowness_grid.addWidget(self.slowness_sill_checkbox, 6, 1)
        slowness_grid.setContentsMargins(0, 0, 0, 0)
        self.slowness_widget.setLayout(slowness_grid)

        xi_param_edit       = QtWidgets.QLineEdit(xi)
        xi_param_edit.setReadOnly(True)
        xi_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.xi_type_combo       = QtWidgets.QComboBox()
        self.xi_type_combo.addItems(types)
        xi_value_label      = MyQLabel("Value", ha='center')
        xi_fix_label        = MyQLabel("Fix", ha='center')
        self.xi_range_X_edit     = MyLineEdit('4.0')
        self.xi_range_Z_edit     = MyLineEdit('4.0')
        self.xi_theta_X_edit     = MyLineEdit('0.0')
        self.xi_sill_edit        = MyLineEdit('1.0')
        self.xi_range_X_checkbox = QtWidgets.QCheckBox()
        self.xi_range_Z_checkbox = QtWidgets.QCheckBox()
        self.xi_theta_X_checkbox = QtWidgets.QCheckBox()
        self.xi_sill_checkbox    = QtWidgets.QCheckBox()

        self.xi_widget      = QtWidgets.QWidget()
        xi_grid             = QtWidgets.QGridLayout()
        xi_grid.addWidget(xi_param_edit, 0, 0, 1, 2)
        xi_grid.addWidget(self.xi_type_combo, 1, 0, 1, 2)
        xi_grid.addWidget(xi_value_label, 2, 0)
        xi_grid.addWidget(xi_fix_label, 2, 1)
        xi_grid.addWidget(self.xi_range_X_edit, 3, 0)
        xi_grid.addWidget(self.xi_range_Z_edit, 4, 0)
        xi_grid.addWidget(self.xi_theta_X_edit, 5, 0)
        xi_grid.addWidget(self.xi_sill_edit, 6, 0)
        xi_grid.addWidget(self.xi_range_X_checkbox, 3, 1)
        xi_grid.addWidget(self.xi_range_Z_checkbox, 4, 1)
        xi_grid.addWidget(self.xi_theta_X_checkbox, 5, 1)
        xi_grid.addWidget(self.xi_sill_checkbox, 6, 1)
        xi_grid.setContentsMargins(0, 0, 0, 0)
        self.xi_widget.setLayout(xi_grid)

        tilt_param_edit       = QtWidgets.QLineEdit('Tilt Angle')
        tilt_param_edit.setReadOnly(True)
        tilt_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.tilt_type_combo       = QtWidgets.QComboBox()
        self.tilt_type_combo.addItems(types)
        tilt_value_label      = MyQLabel("Value", ha='center')
        tilt_fix_label        = MyQLabel("Fix", ha='center')
        self.tilt_range_X_edit     = MyLineEdit('4.0')
        self.tilt_range_Z_edit     = MyLineEdit('4.0')
        self.tilt_theta_X_edit     = MyLineEdit('0.0')
        self.tilt_sill_edit        = MyLineEdit('1.0')
        self.tilt_range_X_checkbox = QtWidgets.QCheckBox()
        self.tilt_range_Z_checkbox = QtWidgets.QCheckBox()
        self.tilt_theta_X_checkbox = QtWidgets.QCheckBox()
        self.tilt_sill_checkbox    = QtWidgets.QCheckBox()

        self.tilt_widget      = QtWidgets.QWidget()
        tilt_grid             = QtWidgets.QGridLayout()
        tilt_grid.addWidget(tilt_param_edit, 0, 0, 1, 2)
        tilt_grid.addWidget(self.tilt_type_combo, 1, 0, 1, 2)
        tilt_grid.addWidget(tilt_value_label, 2, 0)
        tilt_grid.addWidget(tilt_fix_label, 2, 1)
        tilt_grid.addWidget(self.tilt_range_X_edit, 3, 0)
        tilt_grid.addWidget(self.tilt_range_Z_edit, 4, 0)
        tilt_grid.addWidget(self.tilt_theta_X_edit, 5, 0)
        tilt_grid.addWidget(self.tilt_sill_edit, 6, 0)
        tilt_grid.addWidget(self.tilt_range_X_checkbox, 3, 1)
        tilt_grid.addWidget(self.tilt_range_Z_checkbox, 4, 1)
        tilt_grid.addWidget(self.tilt_theta_X_checkbox, 5, 1)
        tilt_grid.addWidget(self.tilt_sill_checkbox, 6, 1)
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
        slowness_3D_param_edit.setReadOnly(True)
        slowness_3D_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.slowness_3D_type_combo       = QtWidgets.QComboBox()
        self.slowness_3D_type_combo.addItems(types)
        slowness_3D_value_label      = MyQLabel("Value", ha='center')
        slowness_3D_fix_label        = MyQLabel("Fix", ha='center')
        self.slowness_3D_range_X_edit     = MyLineEdit('4.0')
        self.slowness_3D_range_Y_edit     = MyLineEdit('4.0')
        self.slowness_3D_range_Z_edit     = MyLineEdit('4.0')
        self.slowness_3D_theta_X_edit     = MyLineEdit('0.0')
        self.slowness_3D_theta_Y_edit     = MyLineEdit('0.0')
        self.slowness_3D_theta_Z_edit     = MyLineEdit('0.0')
        self.slowness_3D_sill_edit        = MyLineEdit('1.0')
        self.slowness_3D_range_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_range_Y_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_range_Z_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_theta_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_theta_Y_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_theta_Z_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_sill_checkbox    = QtWidgets.QCheckBox()

        self.slowness_3D_widget      = QtWidgets.QWidget()
        slowness_3D_grid             = QtWidgets.QGridLayout()
        slowness_3D_grid.addWidget(slowness_3D_param_edit, 0, 1, 2, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_type_combo, 1, 1, 2, 1)
        slowness_3D_grid.addWidget(slowness_3D_value_label, 2, 1)
        slowness_3D_grid.addWidget(slowness_3D_fix_label, 2, 2)
        slowness_3D_grid.addWidget(range_X_3D_label, 3, 0)
        slowness_3D_grid.addWidget(range_Y_3D_label, 4, 0)
        slowness_3D_grid.addWidget(range_Z_3D_label, 5, 0)
        slowness_3D_grid.addWidget(theta_X_3D_label, 6, 0)
        slowness_3D_grid.addWidget(theta_Y_3D_label, 7, 0)
        slowness_3D_grid.addWidget(theta_Z_3D_label, 8, 0)
        slowness_3D_grid.addWidget(sill_3D_label, 9, 0)
        slowness_3D_grid.addWidget(self.slowness_3D_range_X_edit, 3, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_range_Y_edit, 4, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_range_Z_edit, 5, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_theta_X_edit, 6, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_theta_Y_edit, 7, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_theta_Z_edit, 8, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_sill_edit, 9, 1)
        slowness_3D_grid.addWidget(self.slowness_3D_range_X_checkbox, 3, 2)
        slowness_3D_grid.addWidget(self.slowness_3D_range_Y_checkbox, 4, 2)
        slowness_3D_grid.addWidget(self.slowness_3D_range_Z_checkbox, 5, 2)
        slowness_3D_grid.addWidget(self.slowness_3D_theta_X_checkbox, 6, 2)
        slowness_3D_grid.addWidget(self.slowness_3D_theta_Y_checkbox, 7, 2)
        slowness_3D_grid.addWidget(self.slowness_3D_theta_Z_checkbox, 8, 2)
        slowness_3D_grid.addWidget(self.slowness_3D_sill_checkbox, 9, 2)
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
        self.Nug_groupbox = QtWidgets.QGroupBox("Nugget Effect")
        Nug_grid = QtWidgets.QGridLayout()
        Nug_grid.addWidget(self.slowness_label, 0, 0)
        Nug_grid.addWidget(self.slowness_edit, 0, 1)
        Nug_grid.addWidget(self.slowness_checkbox, 0, 2)
        Nug_grid.addWidget(self.traveltime_label, 0, 3)
        Nug_grid.addWidget(self.traveltime_edit, 0, 4)
        Nug_grid.addWidget(self.traveltime_checkbox, 0, 5)
        Nug_grid.addWidget(self.xi_label, 1, 0)
        Nug_grid.addWidget(self.xi_edit, 1, 1)
        Nug_grid.addWidget(self.xi_checkbox, 1, 2)
        Nug_grid.addWidget(self.tilt_label, 1, 3)
        Nug_grid.addWidget(self.tilt_edit, 1, 4)
        Nug_grid.addWidget(self.tilt_checkbox, 1, 5)
        self.Nug_groupbox.setLayout(Nug_grid)

        # --- Covariance Model Groupbox --- #
        covar_groupbox = QtWidgets.QGroupBox("Covariance Model")
        covar_grid = QtWidgets.QGridLayout()
        covar_grid.addWidget(self.covar_struct_combo, 0, 0)
        covar_grid.addWidget(self.btn_Add_Struct, 0, 1)
        covar_grid.addWidget(self.btn_Rem_Struct, 0, 2)
        covar_grid.addWidget(Param_groupbox, 1, 0, 1, 3)
        covar_grid.addWidget(self.Nug_groupbox, 2, 0, 1, 3)
        covar_grid.addWidget(self.auto_update_checkbox, 3, 0, 1, 2)
        covar_grid.addWidget(self.btn_compute, 3, 2, 1, 1)
        covar_groupbox.setLayout(covar_grid)

        # --- Adjust Model Groupbox --- #
        self.Adjust_Model_groupbox = QtWidgets.QGroupBox("Adjust Model (Simplex Method)")
        Adjust_Model_grid = QtWidgets.QGridLayout()
        Adjust_Model_grid.addWidget(bin_label, 0, 0)
        Adjust_Model_grid.addWidget(self.bin_edit, 0, 1)
        Adjust_Model_grid.addWidget(bin_frac_label, 1, 0)
        Adjust_Model_grid.addWidget(self.bin_frac_edit, 1, 1)
        Adjust_Model_grid.addWidget(Iter_label, 2, 0)
        Adjust_Model_grid.addWidget(self.Iter_edit, 2, 1)
        Adjust_Model_grid.addWidget(self.btn_GO, 0, 3, 3, 1)
#         Adjust_Model_grid.setColumnStretch(4, 100)
        self.Adjust_Model_groupbox.setLayout(Adjust_Model_grid)

        # --- Subgrid --- #
        self.Sub_widget = QtWidgets.QWidget()
        Sub_grid        = QtWidgets.QGridLayout()
        Sub_grid.addWidget(data_groupbox, 0, 0)
        Sub_grid.addWidget(self.Grid_groupbox, 1, 0)
        Sub_grid.addWidget(covar_groupbox, 2, 0)
        Sub_grid.addWidget(self.Adjust_Model_groupbox, 3, 0)
        Sub_grid.setContentsMargins(0, 0, 0, 0)
        self.Sub_widget.setLayout(Sub_grid)

        # --- Scroll bar --- #

        self.scrollbar_widget = QtWidgets.QWidget()
        self.scrollbar_grid   = QtWidgets.QGridLayout()
        self.scrollbar_grid.addWidget(self.covariance_fig, 0, 0, 2, 3)
        self.scrollbar_grid.addWidget(self.comparison_fig, 2, 0, 2, 3)
        self.scrollbar_grid.addWidget(self.Sub_widget, 0, 3, 4, 1)
        self.scrollbar_grid.setContentsMargins(0, 0, 0, 0)
        self.scrollbar_grid.setColumnStretch(1, 1)
        self.scrollbar_grid.setColumnStretch(3, 0)
        self.scrollbar_grid.setColumnMinimumWidth(0, 600)
        self.scrollbar_widget.setLayout(self.scrollbar_grid)

        self.scrollbar = utils_ui.auto_create_scrollbar(self.scrollbar_widget)

        # ------- Master Grid Disposition ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0)
        master_grid.addWidget(self.scrollbar, 1, 0)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)

        # ------- Actions ------- #
        self.btn_Show_Stats.clicked.connect(self.show_stats)
        self.btn_Add_Struct.clicked.connect(self.add_struct)
        self.btn_Rem_Struct.clicked.connect(self.del_struct)
        self.btn_compute   .clicked.connect(self.compute)
        self.btn_GO        .clicked.connect(self.adjust)

        self.Upper_limit_checkbox       .stateChanged.connect(self.auto_update)
        self.Upper_limit_checkbox       .stateChanged.connect(self.update_velocity_display)
        self.ellip_veloc_checkbox       .stateChanged.connect(self.parameters_displayed_update)
        self.tilted_ellip_veloc_checkbox.stateChanged.connect(self.parameters_displayed_update)
        self.ellip_veloc_checkbox       .stateChanged.connect(self.auto_update)
        self.tilted_ellip_veloc_checkbox.stateChanged.connect(self.auto_update)
        self.include_checkbox           .stateChanged.connect(self.auto_update)

        self.T_and_A_combo     .currentIndexChanged.connect(self.update_structures)
        self.covar_struct_combo.currentIndexChanged.connect(self.parameters_displayed_update)

        self.slowness_type_combo   .currentIndexChanged.connect(self.change_covar_type_slowness)
        self.xi_type_combo         .currentIndexChanged.connect(self.change_covar_type_xi)
        self.tilt_type_combo       .currentIndexChanged.connect(self.change_covar_type_tilt)
        self.slowness_3D_type_combo.currentIndexChanged.connect(self.change_covar_type_slowness_3D)

        self.models_list.itemSelectionChanged.connect(self.update_model)
        self.models_list.itemSelectionChanged.connect(self.parameters_displayed_update)

        self.step_X_edit.textModified.connect(self.update_grid)
        self.step_Y_edit.textModified.connect(self.update_grid)
        self.step_Z_edit.textModified.connect(self.update_grid)

        for item in (self.slowness_range_X_checkbox, self.slowness_range_Z_checkbox,
                     self.slowness_theta_X_checkbox, self.slowness_sill_checkbox,
                     self.xi_range_X_checkbox, self.xi_range_Z_checkbox,
                     self.xi_theta_X_checkbox, self.xi_sill_checkbox,
                     self.tilt_range_X_checkbox, self.tilt_range_Z_checkbox,
                     self.tilt_theta_X_checkbox, self.tilt_sill_checkbox,
                     self.slowness_3D_range_X_checkbox, self.slowness_3D_range_Y_checkbox, self.slowness_3D_range_Z_checkbox,
                     self.slowness_3D_theta_X_checkbox, self.slowness_3D_theta_Y_checkbox, self.slowness_3D_theta_Z_checkbox,
                     self.slowness_3D_sill_checkbox,
                     self.slowness_checkbox, self.traveltime_checkbox, self.xi_checkbox, self.tilt_checkbox):
            item.clicked.connect(self.fix_verif)

        for item in (self.slowness_range_X_edit, self.slowness_range_Z_edit,
                     self.slowness_theta_X_edit, self.slowness_sill_edit,
                     self.xi_range_X_edit, self.xi_range_Z_edit,
                     self.xi_theta_X_edit, self.xi_sill_edit,
                     self.tilt_range_X_edit, self.tilt_range_Z_edit,
                     self.tilt_theta_X_edit, self.tilt_sill_edit,
                     self.slowness_3D_range_X_edit, self.slowness_3D_range_Y_edit, self.slowness_3D_range_Z_edit,
                     self.slowness_3D_theta_X_edit, self.slowness_3D_theta_Y_edit, self.slowness_3D_theta_Z_edit,
                     self.slowness_3D_sill_edit,
                     self.slowness_edit, self.traveltime_edit, self.xi_edit, self.tilt_edit):
            item.textModified.connect(self.apply_parameters_changes)

        for item in (self.velocity_edit, self.step_X_edit, self.step_Y_edit, self.step_Z_edit,
                     self.slowness_edit, self.traveltime_edit, self.xi_edit, self.tilt_edit,
                     self.bin_edit, self.bin_frac_edit, self.Iter_edit):
            item.textModified.connect(self.auto_update)

        for item in (self.slowness_range_X_edit, self.slowness_range_Z_edit, self.slowness_theta_X_edit, self.slowness_sill_edit,
                     self.xi_range_X_edit, self.xi_range_Z_edit, self.xi_theta_X_edit, self.xi_sill_edit,
                     self.tilt_range_X_edit, self.tilt_range_Z_edit, self.tilt_theta_X_edit, self.tilt_sill_edit,
                     self.slowness_3D_range_X_edit, self.slowness_3D_range_Y_edit, self.slowness_3D_range_Z_edit,
                     self.slowness_3D_theta_X_edit, self.slowness_3D_theta_Y_edit, self.slowness_3D_theta_Z_edit,
                     self.slowness_3D_sill_edit):
            item.textModified.connect(self.auto_update)

        for item in (self.T_and_A_combo, self.curv_rays_combo, self.curv_rays_combo):
            item.currentIndexChanged.connect(self.auto_update)

        self.models_list.itemSelectionChanged.connect(self.auto_update)

        # ------- Sizes ------- #
        self.menu                 .setFixedHeight(self.menu.sizeHint().height())
        data_groupbox             .setFixedHeight(data_groupbox.sizeHint().height())
        self.Grid_groupbox        .setFixedHeight(self.Grid_groupbox.sizeHint().height())
        Param_groupbox            .setFixedHeight(Param_groupbox.sizeHint().height())
        self.Nug_groupbox         .setFixedHeight(self.Nug_groupbox.sizeHint().height())
        self.Adjust_Model_groupbox.setFixedHeight(self.Adjust_Model_groupbox.sizeHint().height())
        self.Sub_widget           .setFixedWidth(500)

        for item in (labels_2D_grid, slowness_grid, xi_grid, tilt_grid):
            for i in range(0, 7):
                item.setRowMinimumHeight(i, slowness_param_edit.sizeHint().height())
            item.setVerticalSpacing(0)

        for i in range(0, 3):
            labels_2D_grid.setRowMinimumHeight(i, slowness_param_edit.sizeHint().height() + 19)

        for item in (slowness_value_label, xi_value_label, tilt_value_label, slowness_3D_value_label,
                     slowness_fix_label, xi_fix_label, tilt_fix_label, slowness_3D_fix_label,
                     range_X_label, range_Z_label, theta_X_label, sill_label):
            item.setFixedHeight(25)

        # --- Statistics Form --- #

        self.statistics_fig = StatisticsFig(self)
        self.statistics_form = QtWidgets.QWidget()
        statistics_grid = QtWidgets.QGridLayout()
        statistics_grid.addWidget(self.statistics_fig)
        self.statistics_form.setLayout(statistics_grid)
        self.statistics_form.setMinimumSize(1.2 * self.statistics_form.sizeHint().height(),
                                            1.2 * self.statistics_form.sizeHint().width())


class StatisticsFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure()
        super(StatisticsFig, self).__init__(fig)
        self.initFig()
        self.plot(1, None)

    def initFig(self):
        self.ax1 = self.figure.add_axes([0.1, 0.7, 0.85, 0.2])
        self.ax2 = self.figure.add_axes([0.1, 0.4, 0.85, 0.2])
        self.ax3 = self.figure.add_axes([0.1, 0.1, 0.85, 0.2])
        mpl.axes.Axes.set_xlabel(self.ax2, "Straight Ray Length")
        mpl.axes.Axes.set_xlabel(self.ax3, "Straight Ray Angle")

        plt.hist(self.ax1)

    def plot(self, data_type, model):
        s = data(:,1) / np.sum(L, 2)
        if data_type == 0:
            s = 1 / s
            data_name = "App. Velocity"
        else:
            data_name = "App. Attenuation"
        s0 = np.mean(s)
        vs = np.var(s)
        Tx = model.grid.Tx(idata, :)
        Rx = model.grid.Rx(idata, :)
        hyp = np.sqrt(np.sum((Tx - Rx)**2, 2))
        dz = Tx - Rx
        theta = 180 / np.pi * np.arcsin(dz / hyp)
        self.ax1  # hist(s, 30)
        self.ax2  # plot(hyp, s, '+')
        self.ax3  # plot(theta, s, '+')
        mpl.axes.Axes.set_title(self.ax1, "{}: {} $\pm$ {}".format(data_name, str(s0)[:3], str(vs)[:3]))
        mpl.axes.Axes.set_ylabel(self.ax2, data_name)
        mpl.axes.Axes.set_ylabel(self.ax3, data_name)


class CovarianceFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(CovarianceFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.1, 0.15, 0.85, 0.8])
        mpl.axes.Axes.set_ylabel(self.ax, "Covariance")
        mpl.axes.Axes.set_xlabel(self.ax, "Bin Number")

    def plot(self, item):
        pass


class ComparisonFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(ComparisonFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.1, 0.15, 0.85, 0.8])
        mpl.axes.Axes.set_ylabel(self.ax, "Model Covariance")
        mpl.axes.Axes.set_xlabel(self.ax, "Experimental Covariance")

    def plot(self, item):
        pass


if __name__ == '__main__':

    database.create_data_management(database)
    database.load(database, 'database.db')

    app = QtWidgets.QApplication(sys.argv)

    Covar_ui = CovarUI()
    Covar_ui.show()

    sys.exit(app.exec_())

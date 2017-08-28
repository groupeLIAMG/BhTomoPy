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
from mog import Mog
import covar
import database
import utils_ui
from utils_ui import lay, inv_lay
from utils import ComputeThread
from sqlalchemy.orm.attributes import flag_modified
from copy import deepcopy
from math import ceil
from scipy.optimize import fmin

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from mpl_toolkits.mplot3d import axes3d
import matplotlib as mpl
import numpy as np

import unicodedata
xi = unicodedata.lookup("GREEK SMALL LETTER XI")
theta = unicodedata.lookup("GREEK SMALL LETTER THETA")
tau = unicodedata.lookup("GREEK SMALL LETTER TAU")

class CovarUI(QtWidgets.QFrame):
    
    model = None           # current model
    temp_grid = None       # the grid modified from covar_ui actually is only a temporary one.  The
                           # original grid must not be modified.
    updateHandler = False  # selected model may seldom be modified twice.  'updateHandler' prevents
                           # functions from firing more than once.  TODO: use a QValidator instead.

    updateHandlerParameters = False
    data = None            # holds the model's data so that it does not need to be computed
                           # more than once
    idata = None           # idem.
    L = None               # ray matrix
    Cd = None              # experimental covariance
    xc = None              # grid's centers

    triggerFctAdjustCov = QtCore.pyqtSignal()
    FuncCounter = 0

    def __init__(self, parent=None):
        super(CovarUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Covariance")
        self.triggerFctAdjustCov.connect(self.handleAdjustCov) # Signal for computing popup, to follow the progress
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

        self.update_model()
        self.parameters_displayed_update()
        self.update_velocity_display()

    def openfile(self):

        new_model = utils_ui.chooseModel(database)
        if new_model is not None:
            self.set_current_model(new_model)
            self.mogs_list.clear()
            self.mogs_list.addItems([item.name for item in self.model.mogs])
            self.mogs_list.setCurrentRow(0)
            self.update_model()
            self.update_booleans()
            self.parameters_displayed_update()
            self.update_data()

    def savefile(self):
        self.apply_booleans()
        return utils_ui.savefile(database)

    def saveasfile(self):
        self.apply_booleans()
        return utils_ui.saveasfile(database)

    def apply_booleans(self):
        self.current_covar().use_xi = self.ellip_veloc_checkbox       .checkState()
        self.current_covar().use_tilt = self.tilted_ellip_veloc_checkbox.checkState()
        self.current_covar().use_c0 = self.include_checkbox           .checkState()
        self.flag_modified_covar()

    def update_booleans(self):
        covar_ = self.current_covar()
        if covar_ is not None:
            self.ellip_veloc_checkbox       .setCheckState(covar_.use_xi)
            self.tilted_ellip_veloc_checkbox.setCheckState(covar_.use_tilt)
            self.include_checkbox           .setCheckState(covar_.use_c0)

    def set_current_model(self, model):
        if self.updateHandler:  # TODO unnecessary?
            return

        self.updateHandler = True
        if self.model is not None:
            if utils_ui.save_warning(database):
                self.model = model
                self.clear_figures()
                if model.grid is not None:
                    self.update_temp_grid()
        else:
            self.model = model
            self.clear_figures()
            if model.grid is not None:
                self.update_temp_grid()
        self.updateHandler = False

    def current_covar(self):

        if self.model is not None and self.model.grid is not None:

            if self.T_and_A_combo.currentIndex() == 0:
                if self.model.tt_covar is None:
                    self.model.tt_covar = covar.CovarianceModel(self.model.grid.type)
                covariance = self.model.tt_covar
            else:
                if self.model.amp_covar is None:
                    self.model.amp_covar = covar.CovarianceModel(self.model.grid.type)
                covariance = self.model.amp_covar

            return covariance

    def current_mog(self):

        if self.model is not None:

            if self.mogs_list.currentIndex() != -1:

                return database.session.query(Mog).filter(Mog.name == self.mogs_list.currentItem().text()).first()

    def flag_modified_covar(self):  # refer to database's 'save_as' function

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

        for item in (*self.slowness_widget, *self.xi_widget, *self.tilt_widget):
            item.setHidden(True)

        self.slowness_3D_widget         .setHidden(True)
        self.ellip_veloc_checkbox       .setDisabled(True)
        self.tilted_ellip_veloc_checkbox.setDisabled(True)

        self.step_Y_edit.setDisabled(True)

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

        if self.model is not None:

            self.Sub_widget.setDisabled(False)

            if self.model.grid is not None:
                self.covar_struct_combo.setDisabled(False)
                self.btn_Add_Struct    .setDisabled(False)
                self.Grid_groupbox     .setDisabled(False)

                if self.current_covar().covar:

                    self.btn_Rem_Struct       .setDisabled(False)
                    self.Nug_groupbox         .setDisabled(False)
                    self.auto_update_checkbox .setDisabled(False)
                    self.btn_compute          .setDisabled(False)
                    self.Adjust_Model_groupbox.setDisabled(False)

                    if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                        for item in (*self.slowness_widget,):
                            item.setHidden(False)
                        self.ellip_veloc_checkbox.setDisabled(False)

                        if self.ellip_veloc_checkbox.checkState():
                            for item in (*self.xi_widget,):
                                item.setHidden(False)
                            self.tilted_ellip_veloc_checkbox.setDisabled(False)

                            self.xi_label   .setHidden(False)
                            self.xi_edit    .setHidden(False)
                            self.xi_checkbox.setHidden(False)

                            if self.tilted_ellip_veloc_checkbox.checkState():
                                for item in (*self.tilt_widget,):
                                    item.setHidden(False)

                                self.tilt_label   .setHidden(False)
                                self.tilt_edit    .setHidden(False)
                                self.tilt_checkbox.setHidden(False)

                            else:
                                self.tilted_ellip_veloc_checkbox.setCheckState(False)

                        else:
                            self.tilted_ellip_veloc_checkbox.setCheckState(False)
                            self.ellip_veloc_checkbox.setCheckState(False)

                    elif self.model.grid.type == '3D':
                        self.slowness_3D_widget.setHidden(False)
                        self.step_Y_edit       .setDisabled(False)

                else:
                    self.ellip_veloc_checkbox       .setCheckState(False)
                    self.tilted_ellip_veloc_checkbox.setCheckState(False)

            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "This model has no grid.")

            self.update_parameters()

        else:
            self.ellip_veloc_checkbox       .setCheckState(False)
            self.tilted_ellip_veloc_checkbox.setCheckState(False)

        if self.T_and_A_combo.currentIndex() == 0:
            self.slowness_param_edit   .setText("Slowness")
            self.slowness_3D_param_edit.setText("Slowness")
            self.slowness_label        .setText("Slowness")
            self.tt_label              .setText("Traveltime")
        else:
            self.slowness_param_edit   .setText("Attenuation")
            self.slowness_3D_param_edit.setText("Attenuation")
            self.slowness_label        .setText("Attenuation")
            self.tt_label              .setText(tau)

        self.updateHandler = False

    def auto_update(self):
        if self.auto_update_checkbox.checkState():
            self.compute()

    def update_model(self):
        self.btn_Rem_Struct.setDisabled(True)

        self.updateHandler = True
        self.covar_struct_combo.clear()
        self.updateHandler = False

        if self.model is not None:
            self.model_label.setText("Model : " + self.model.name)
            if self.model.grid is not None:
                self.update_structures()

                if self.temp_grid is None:
                    ntraces = 0
                    for mog_ in database.session.query(Mog).all():
                        ntraces += mog_.data.ntrace

                    self.mogs_list.setCurrentRow(0)

                    self.cells_no_label.setText(str(self.model.grid.getNumberOfCells()))
                    self.reset_grid()
                    self.update_data()
            else:
                self.cells_no_label.setText('0')
                self.rays_no_label.setText('0')
                self.reset_grid()
        else:
            self.reset_grid()

    def update_structures(self):
        self.covar_struct_combo.clear()
        current_list = self.current_covar().covar
        if current_list is not None:
            if not current_list:
                self.add_struct()
            self.covar_struct_combo.addItems(["Structure no " + str(i + 1) for i in range(len(current_list))])
            self.covar_struct_combo.setCurrentIndex(0)
            self.update_parameters()
            self.btn_Rem_Struct.setDisabled(False)

    def new_grid(self):
        self.temp_grid = deepcopy(self.model.grid)

    def reset_grid(self):
        if self.model is None or self.model.grid is None:
            self.X_min_label.setText('0')
            self.X_max_label.setText('0')
            self.Y_min_label.setText('0')
            self.Y_max_label.setText('0')
            self.Z_min_label.setText('0')
            self.Z_max_label.setText('0')
            self.step_X_edit.setText('0')
            self.step_Y_edit.setText('0')
            self.step_Z_edit.setText('0')
            self.temp_grid = None
        else:
            self.new_grid()

            self.X_min_label.setText(str(self.temp_grid.grx[0])[:7])
            self.X_max_label.setText(str(self.temp_grid.grx[-1])[:7])
            if self.temp_grid.gry:  # TODO verify
                self.Y_min_label.setText(str(self.temp_grid.gry[0])[:7])
                self.Y_max_label.setText(str(self.temp_grid.gry[-1])[:7])
            else:
                self.Y_min_label.setText('0')
                self.Y_max_label.setText('0')
            self.Z_min_label.setText(str(self.temp_grid.grz[0])[:7])
            self.Z_max_label.setText(str(self.temp_grid.grz[-1])[:7])

            self.step_X_edit.setText(str(2 * self.temp_grid.dx))  # by default, the step should be twice the size of the original
            self.step_Y_edit.setText(str(2 * self.temp_grid.dy))  # grid in order to make the computing less resources-expensive
            self.step_Z_edit.setText(str(2 * self.temp_grid.dz))

            self.update_temp_grid()

    def update_temp_grid(self):
        if self.temp_grid is not None and self.model.grid is not None:

            if np.abs(self.temp_grid.dx - float(self.step_X_edit.text())) > 0.00001:
                dx = float(self.step_X_edit.text())
                nb_elements = ceil((self.model.grid.grx[-1] - self.model.grid.grx[0]) / dx)
                self.temp_grid.grx = self.model.grid.grx[0] + dx * np.arange(0, nb_elements + 1)

            elif np.abs(self.temp_grid.dy - float(self.step_Y_edit.text())) > 0.00001:
                dy = float(self.step_Y_edit.text())
                nb_elements = ceil((self.model.grid.gry[-1] - self.model.grid.gry[0]) / dy)
                self.temp_grid.gry = self.model.grid.gry[0] + dy * np.arange(0, nb_elements + 1)

            elif np.abs(self.temp_grid.dz - float(self.step_Z_edit.text())) > 0.00001:
                dz = float(self.step_Z_edit.text())
                nb_elements = ceil((self.model.grid.grz[-1] - self.model.grid.grz[0]) / dz)
                self.temp_grid.grz = self.model.grid.grz[0] + dz * np.arange(0, nb_elements + 1)

            self.cells_no_labeli.setText(str(self.temp_grid.getNumberOfCells()))
            self.update_data()

    def update_parameters(self):

        self.updateHandlerParameters = True

        covar_ = self.current_covar()
        ind = self.covar_struct_combo.currentIndex()

        if ind != -1:
            if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                self.slowness_type_combo  .setCurrentIndex(covar_.covar[ind].type)
                self.slowness_range_X_edit.setText(str(covar_.covar[ind].range[0]))
                self.slowness_range_Z_edit.setText(str(covar_.covar[ind].range[1]))
                self.slowness_theta_X_edit.setText(str(covar_.covar[ind].angle[0]))
                self.slowness_sill_edit   .setText(str(covar_.covar[ind].sill))
                self.slowness_edit        .setText(str(covar_.nugget_model))
                self.tt_edit              .setText(str(covar_.nugget_data))

                if self.ellip_veloc_checkbox.checkState():
                    if covar_.covar_xi[ind] is None:
                        covar_.covar_xi[ind] = covar.CovarianceFactory.detDefault2D()
                    self.xi_type_combo  .setCurrentIndex(covar_.covar_xi[ind].type)
                    self.xi_range_X_edit.setText(str(covar_.covar_xi[ind].range[0]))
                    self.xi_range_Z_edit.setText(str(covar_.covar_xi[ind].range[1]))
                    self.xi_theta_X_edit.setText(str(covar_.covar_xi[ind].angle[0]))
                    self.xi_sill_edit   .setText(str(covar_.covar_xi[ind].sill))
                    self.xi_edit        .setText(str(covar_.nugget_xi))

                    if self.tilted_ellip_veloc_checkbox.checkState():
                        if covar_.covar_tilt[ind] is None:
                            covar_.covar_tilt[ind] = covar.CovarianceFactory.detDefault2D()
                        self.tilt_type_combo  .setCurrentIndex(covar_.covar_tilt[ind].type)
                        self.tilt_range_X_edit.setText(str(covar_.covar_tilt[ind].range[0]))
                        self.tilt_range_Z_edit.setText(str(covar_.covar_tilt[ind].range[1]))
                        self.tilt_theta_X_edit.setText(str(covar_.covar_tilt[ind].angle[0]))
                        self.tilt_sill_edit   .setText(str(covar_.covar_tilt[ind].sill))
                        self.tilt_edit        .setText(str(covar_.nugget_tilt))

            elif self.model.grid.type == '3D':
                self.slowness_3D_type_combo  .setCurrentIndex(covar_.covar[ind].type)
                self.slowness_3D_range_X_edit.setText(str(covar_.covar[ind].range[0]))
                self.slowness_3D_range_Y_edit.setText(str(covar_.covar[ind].range[1]))
                self.slowness_3D_range_Z_edit.setText(str(covar_.covar[ind].range[2]))
                self.slowness_3D_theta_X_edit.setText(str(covar_.covar[ind].angle[0]))
                self.slowness_3D_theta_Y_edit.setText(str(covar_.covar[ind].angle[1]))
                self.slowness_3D_theta_Z_edit.setText(str(covar_.covar[ind].angle[2]))
                self.slowness_3D_sill_edit   .setText(str(covar_.covar[ind].sill))
                self.slowness_edit           .setText(str(covar_.nugget_model))
                self.tt_edit                 .setText(str(covar_.nugget_data))

        self.updateHandlerParameters = False

    def apply_parameters_changes(self):

        if self.updateHandlerParameters:
            return

        covar_ = self.current_covar()
        ind = self.covar_struct_combo.currentIndex()

        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
            covar_.covar[ind].range[0] = float(self.slowness_range_X_edit.text())
            covar_.covar[ind].range[1] = float(self.slowness_range_Z_edit.text())
            covar_.covar[ind].angle[0] = float(self.slowness_theta_X_edit.text())
            covar_.covar[ind].sill = float(self.slowness_sill_edit   .text())
            covar_.nugget_model = float(self.slowness_edit        .text())
            covar_.nugget_data = float(self.tt_edit              .text())

            if self.ellip_veloc_checkbox.checkState():

                self.loadRays()
                self.computeCd()

                if covar_.covar_xi[ind] is None:
                    covar_.covar_xi[ind] = covar.CovarianceFactory.detDefault2D()
                covar_.covar_xi[ind].range[0] = float(self.xi_range_X_edit.text())
                covar_.covar_xi[ind].range[1] = float(self.xi_range_Z_edit.text())
                covar_.covar_xi[ind].angle[0] = float(self.xi_theta_X_edit.text())
                covar_.covar_xi[ind].sill = float(self.xi_sill_edit   .text())
                covar_.nugget_xi = float(self.xi_edit        .text())

                if self.tilted_ellip_veloc_checkbox.checkState():
                    if covar_.covar_tilt[ind] is None:
                        covar_.covar_tilt[ind] = covar.CovarianceFactory.detDefault2D()
                    covar_.covar_tilt[ind].range[0] = float(self.tilt_range_X_edit.text())
                    covar_.covar_tilt[ind].range[1] = float(self.tilt_range_Z_edit.text())
                    covar_.covar_tilt[ind].angle[0] = float(self.tilt_theta_X_edit.text())
                    covar_.covar_tilt[ind].sill = float(self.tilt_sill_edit   .text())
                    covar_.nugget_tilt = float(self.tilt_edit        .text())

        elif self.model.grid.type == '3D':
            covar_.covar[ind].range[0] = float(self.slowness_3D_range_X_edit.text())
            covar_.covar[ind].range[1] = float(self.slowness_3D_range_Y_edit.text())
            covar_.covar[ind].range[2] = float(self.slowness_3D_range_Z_edit.text())
            covar_.covar[ind].angle[0] = float(self.slowness_3D_theta_X_edit.text())
            covar_.covar[ind].angle[1] = float(self.slowness_3D_theta_Y_edit.text())
            covar_.covar[ind].angle[2] = float(self.slowness_3D_theta_Z_edit.text())
            covar_.covar[ind].sill = float(self.slowness_3D_sill_edit   .text())
            covar_.nugget_model = float(self.slowness_edit           .text())
            covar_.nugget_data = float(self.tt_edit                 .text())

        self.flag_modified_covar()
        database.modified = True

    def change_covar_type_slowness(self, ctype):
        if not self.updateHandler:
            ind = self.covar_struct_combo.currentIndex()
            cov = self.current_covar().covar[ind]
            self.current_covar().covar[ind] = covar.CovarianceFactory.buildCov(ctype, cov.range, cov.angle, cov.sill)
            self.flag_modified_covar()
            database.modified = True

    def change_covar_type_xi(self, ctype):
        if not self.updateHandler:
            ind = self.covar_struct_combo.currentIndex()
            cov = self.current_covar().covar_xi[ind]
            self.current_covar().covar_xi[ind] = covar.CovarianceFactory.buildCov(ctype, cov.range, cov.angle, cov.sill)
            self.flag_modified_covar()
            database.modified = True

    def change_covar_type_tilt(self, ctype):
        if not self.updateHandler:
            ind = self.covar_struct_combo.currentIndex()
            cov = self.current_covar().covar_tilt[ind]
            self.current_covar().covar_tilt[ind] = covar.CovarianceFactory.buildCov(ctype, cov.range, cov.angle, cov.sill)
            self.flag_modified_covar()
            database.modified = True

    def add_struct(self):
        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
            new = covar.CovarianceFactory.detDefault2D()
        elif self.model.grid.type == '3D':
            new = covar.CovarianceFactory.detDefault3D()
        self.current_covar().covar     .append(new)
        self.current_covar().covar_xi  .append(None)
        self.current_covar().covar_tilt.append(None)
        count = self.covar_struct_combo.count()
        self.covar_struct_combo.addItem('Structure no ' + str(count + 1))
        self.covar_struct_combo.setCurrentIndex(count)
        self.parameters_displayed_update()
        self.update_parameters()
        self.flag_modified_covar()
        database.modified = True

    def del_struct(self):
        index = self.covar_struct_combo.currentIndex()
        del self.current_covar().covar[index]
        del self.current_covar().covar_xi[index]
        del self.current_covar().covar_tilt[index]
        self.covar_struct_combo.clear()
        self.covar_struct_combo.addItems(["Structure no " + str(i + 1) for i in range(len(self.current_covar().covar))])
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

    def handleAdjustCov(self):
        self.FuncCounter += 1
        self.progress_lbl.setText("Computing Iteration " + str(self.FuncCounter) + ".\nPlease wait...")

    def adjustInThread(self):
        try:
            self.FuncCounter = 0
            self.progress_lbl.setText("Computing Iteration " + "0" + ".\nPlease wait...")
            self.computing_form.show()
            self.compute_thread = ComputeThread(self.adjust)
            self.compute_thread.finished.connect(self.computing_form.hide)
            self.compute_thread.start()
        except Exception as ex:
            print(type(ex))
            print(ex.args)
            print(ex)

    def adjust(self):
        cm = self.current_covar()
        global ix
        global x0
        ix = 0
        x0 = np.zeros(100)
        ns = len(cm.covar)
        def ifNotChekedAddToXi(checkbox,valueToAdd):
            """
            Function to simplify the code below.
            If the checkbox 'Fix' for the specify value isn't checked, add the value to the array.
            """
            global ix
            global x0
            if not checkbox.isChecked():
                    x0[ix] = valueToAdd
                    ix += 1
        for n in range(0,ns):
            _covar = cm.covar[n]
            if len(_covar.range) == 2: 
                ifNotChekedAddToXi(self.slowness_range_X_checkbox,_covar.range[0]) # Add Range X
                ifNotChekedAddToXi(self.slowness_range_Z_checkbox,_covar.range[1]) # Add Range Z
                ifNotChekedAddToXi(self.slowness_theta_X_checkbox,_covar.angle[0]) # Add Angle Theta X
                ifNotChekedAddToXi(self.slowness_sill_checkbox,_covar.sill) # Add Sill
            elif len(_covar.range) == 3: 
                ifNotChekedAddToXi(self.slowness_3D_range_X_checkbox,_covar.range[0]) # Add 3D Range X
                ifNotChekedAddToXi(self.slowness_3D_range_Y_checkbox,_covar.range[1]) # Add 3D Range Y
                ifNotChekedAddToXi(self.slowness_3D_range_Z_checkbox,_covar.range[2]) # Add 3D Range Z
                ifNotChekedAddToXi(self.slowness_3D_theta_X_checkbox,_covar.angle[0]) # Add Angle Theta X
                ifNotChekedAddToXi(self.slowness_3D_theta_Y_checkbox,_covar.angle[1]) # Add Angle Theta Y
                ifNotChekedAddToXi(self.slowness_3D_theta_Z_checkbox,_covar.angle[2]) # Add Angle Theta Z
                ifNotChekedAddToXi(self.slowness_3D_sill_checkbox,_covar.sill) # Add Sill

            if self.ellip_veloc_checkbox.isChecked():
                # TODO : add 3D support
                _covar_xi = cm.covar_xi[n]
                if len(_covar.range) == 2: 
                    ifNotChekedAddToXi(self.xi_range_X_checkbox,_covar_xi.range[0]) # Add xi Range X
                    ifNotChekedAddToXi(self.xi_range_Z_checkbox,_covar_xi.range[1]) # Add xi Range Z
                    ifNotChekedAddToXi(self.xi_theta_X_checkbox,_covar_xi.angle[0]) # Add xi Angle Theta X
                    ifNotChekedAddToXi(self.xi_sill_checkbox,_covar_xi.sill) # Add xi Sill
                if self.tilted_ellip_veloc_checkbox.isChecked():
                    _covar_tilt = cm.covar_tilt[n]
                if len(_covar.range) == 2: 
                    ifNotChekedAddToXi(self.tilt_range_X_checkbox,_covar_tilt.range[0]) # Add tilt Range X
                    ifNotChekedAddToXi(self.tilt_range_Z_checkbox,_covar_tilt.range[1]) # Add tilt Range Z
                    ifNotChekedAddToXi(self.tilt_theta_X_checkbox,_covar_tilt.angle[0]) # Add tilt Angle Theta X
                    ifNotChekedAddToXi(self.tilt_sill_checkbox,_covar_tilt.sill) # Add tilt Sill
        # Adding nugget effect
        ifNotChekedAddToXi(self.slowness_checkbox,cm.nugget_model) # Add slowness for the slowness covariance / amplitude for the amplitude covariance
        ifNotChekedAddToXi(self.tt_checkbox,cm.nugget_data) # Add traveltime for the slowness covariance / tau for the amplitude covariance
        if self.ellip_veloc_checkbox.isChecked():
            ifNotChekedAddToXi(self.xi_checkbox,cm.nugget_xi) # Add nugget xi
        if self.tilted_ellip_veloc_checkbox.isChecked():
            ifNotChekedAddToXi(self.tilt_checkbox,calculate,cm.nugget_tilt) # Add nugget tilt

        x0 = x0[:ix]
        fmin(func=self.adjustCov,x0 = x0,xtol = 1e-12,ftol = 1e-12,maxfun = int(self.Iter_edit.text()),disp = 0)

        self.update_parameters()

        g, gt = self.calculate()
        n1 = range(0, len(gt))
        n2 = range(0, len(g))
        self.covariance_fig.plot(n2, g, n1, gt)

        gmin = np.min(np.concatenate([g, gt]))
        gmax = np.max(np.concatenate([g, gt]))
        self.comparison_fig.plot(g, gt, gmin, gmax)

        self.flag_modified_covar()
        database.modified = True
 
    def adjustCov(self, x0):
        cm = self.current_covar()
        global ix
        ix = -1
        ns = len(cm.covar)
        def ifNotChekedChangeVariable(checkbox,VariableToChange):
            """
            Function to simplify the code below.
            If the checkbox 'Fix' for the specify value isn't checked, return the modified value.
            """
            global ix
            if not checkbox.isChecked():
                    ix += 1
                    return x0[ix]
            else:
                    return VariableToChange
        for n in range(0,ns):
            _covar = cm.covar[n]
            if len(_covar.range) == 2: 
                _covar.range[0] = ifNotChekedChangeVariable(self.slowness_range_X_checkbox,_covar.range[0]) # Add Range X
                _covar.range[1] = ifNotChekedChangeVariable(self.slowness_range_X_checkbox,_covar.range[1]) # Add Range Z
                _covar.angle[0] = ifNotChekedChangeVariable(self.slowness_theta_X_checkbox,_covar.angle[0]) # Add Angle Theta X
                _covar.sill = ifNotChekedChangeVariable(self.slowness_sill_checkbox,_covar.sill) # Add Sill
            elif len(_covar.range) == 3: 
                _covar.range[0] = ifNotChekedChangeVariable(self.slowness_3D_range_X_checkbox,_covar.range[0]) # Add 3D Range X
                _covar.range[1] = ifNotChekedChangeVariable(self.slowness_3D_range_Y_checkbox,_covar.range[1]) # Add 3D Range Y
                _covar.range[2] = ifNotChekedChangeVariable(self.slowness_3D_range_Z_checkbox,_covar.range[2]) # Add 3D Range Z
                _covar.angle[0] = ifNotChekedChangeVariable(self.slowness_3D_theta_X_checkbox,_covar.angle[0]) # Add Angle Theta X
                _covar.angle[1] = ifNotChekedChangeVariable(self.slowness_3D_theta_Y_checkbox,_covar.angle[1]) # Add Angle Theta Y
                _covar.angle[2] = ifNotChekedChangeVariable(self.slowness_3D_theta_Z_checkbox,_covar.angle[2]) # Add Angle Theta Z
                _covar.sill = ifNotChekedChangeVariable(self.slowness_3D_sill_checkbox,_covar.sill) # Add Sill

            if self.ellip_veloc_checkbox.isChecked():
                # TODO : add 3D support
                _covar_xi = cm.covar_xi[n]
                if len(_covar.range) == 2: 
                    _covar_xi.range[0] = ifNotChekedChangeVariable(self.xi_range_X_checkbox,_covar_xi.range[0]) # Add xi Range X
                    _covar_xi.range[1] = ifNotChekedChangeVariable(self.xi_range_Z_checkbox,_covar_xi.range[1]) # Add xi Range Z
                    _covar_xi.angle[0] = ifNotChekedChangeVariable(self.xi_theta_X_checkbox,_covar_xi.angle[0]) # Add xi Angle Theta X
                    _covar_xi.sill = ifNotChekedChangeVariable(self.xi_sill_checkbox,_covar_xi.sill) # Add xi Sill
                if self.tilted_ellip_veloc_checkbox.isChecked():
                    _covar_tilt = cm.covar_tilt[n]
                    if len(_covar.range) == 2: 
                        _covar_tilt.range[0] = ifNotChekedChangeVariable(self.tilt_range_X_checkbox,_covar_tilt.range[0]) # Add tilt Range X
                        _covar_tilt.range[1] = ifNotChekedChangeVariable(self.tilt_range_Z_checkbox,_covar_tilt.range[1]) # Add tilt Range Z
                        _covar_tilt.angle[0] = ifNotChekedChangeVariable(self.tilt_theta_X_checkbox,_covar_tilt.angle[0]) # Add tilt Angle Theta X
                        _covar_tilt.sill = ifNotChekedChangeVariable(self.tilt_sill_checkbox,_covar_tilt.sill) # Add tilt Sill

        # Adding nugget effect
        cm.nugget_model = ifNotChekedChangeVariable(self.slowness_checkbox,cm.nugget_model) # Add slowness for the slowness covariance / amplitude for the amplitude covariance
        cm.nugget_data = ifNotChekedChangeVariable(self.tt_checkbox,cm.nugget_data) # Add traveltime for the slowness covariance / tau for the amplitude covariance
        if self.ellip_veloc_checkbox.isChecked():
            cm.nugget_xi = ifNotChekedChangeVariable(self.xi_checkbox,cm.nugget_xi) # Add nugget xi
        if self.tilted_ellip_veloc_checkbox.isChecked():
            cm.nugget_tilt = ifNotChekedChangeVariable(self.tilt_checkbox,calculate,cm.nugget_tilt) # Add nugget tilt

        g, gt = self.calculate()

        _q = np.flip(np.arange(1,len(g) + 1) ** 2,axis = 0)
        _q = (_q / (np.max(_q))) + 1
        g = g[:len(_q)]
        gt = gt[:len(_q)]
        
        self.triggerFctAdjustCov.emit()

        return sum(((gt-g)*_q)**2)

    def fix_verif(self):
        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
            items = [*self.slowness_checkboxes,*self.nugget_checkboxes]
            if self.ellip_veloc_checkbox.checkState():
                items += [*self.xi_checkboxes,self.xi_checkbox]
                if self.tilted_ellip_veloc_checkbox.checkState():
                    items += [self.tilt_checkboxes,self.tilt_checkbox]

        elif self.model.grid.type == '3D':
            items = [*self.slowness_3D_checkboxes]

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
            self.velocity_edit.setText('0.15')
        else:
            self.velocity_edit.setText('')

    def update_data(self):
        selectedMogs = [i.row() for i in self.mogs_list.selectedIndexes()]
        if self.include_checkbox.checkState() and self.T_and_A_combo.currentIndex() == 0:
            vlim = float(self.velocity_edit.text())
        else:
            vlim = 0.0

        type_dict = {0: 'tt', 1: 'amp', 2: 'fce'}
        type_ = type_dict[self.T_and_A_combo.currentIndex()]

        if self.mogs_list.currentRow() != -1:
            self.data, self.idata = Model.getModelData(self.model, selectedMogs, type_, vlim = vlim)
            self.rays_no_label.setText(str(self.data.shape[0]))
            self.loadRays()
            self.computeCd()

    def loadRays(self):
        aniso = self.ellip_veloc_checkbox.checkState()
        if self.curv_rays_combo.count() > 1:  # TODO implement curved rays
            # curved rays

            # check if grid compatible
            if self.model.grid.checkCenter(self.model.inv_res[self.curv_rays_combo.currentIndex() - 1].tomo.x,  # TODO -1's?
                                           self.model.inv_res[self.curv_rays_combo.currentIndex() - 1].tomo.y,
                                           self.model.inv_res[self.curv_rays_combo.currentIndex() - 1].tomo.z) == 0:
                print('Grid Not Compatible With Ray Matrix. Using Straight Rays.')
                self.curv_rays_combo.setCurrentIndex(0)
                self.loadRays()
                return
            ndata = 0
            ind = np.zeros(self.data.shape[0], 1)
            for n in range(0, self.data.shape[0]):
                ii = np.where(self.model.inv_res[self.curv_rays_combo.currentIndex() - 1].tomo.no_trace == self.data[n, 2])
                if np.all(ii == 0):
                    print('Ray No', str(self.data[n, 3]), 'Missing From Ray Matrix. Using Straight Rays.')
                    self.curv_rays_combo.setCurrentIndex(0)
                    self.loadRays()
                    return
                else:
                    ndata += 1
                    ind[ndata] = ii
            ind = ind[0:ndata]
            self.L = self.model.inv_res[self.curv_rays_combo.currentIndex() - 1].tomo.L[ind, :]
        else:
            # straight rays
            self.L = self.temp_grid.getForwardStraightRays(self.idata, aniso=aniso)

    def computeCd(self):
        # Computes experimental covariance
        nt = self.L.shape[0]

        if not self.ellip_veloc_checkbox.checkState():
            s0 = np.mean(self.data[:, 0] / np.sum(self.L.toarray(), 1))
            mta = s0 * np.sum(self.L, 1).getA()  # mean traveltime
        else:
            np_ = self.L.shape[1] / 2
            l = np.sqrt(self.L[:, 0:np_] ** 2 + self.L[:, np_:] ** 2)
            s0 = np.mean(self.data[:, 0] / np.sum(l, 1))
            mta = s0 * np.sum(l, 1)

        dt = self.data[:, 0].reshape((-1, 1)) - mta

        self.Cd = dt.dot(dt.T)
        self.Cd = self.Cd.reshape((nt ** 2, 1), order='F')

    def compute(self):
        self.progress_lbl.setText("Computing.\nPlease wait...")
        self.computing_form.show()
        self.compute_thread = ComputeThread(self.calculateAndShow)
        self.compute_thread.finished.connect(self.computing_form.hide)
        self.compute_thread.start()

    def calculateAndShow(self):
        g, gt = self.calculate()
        n1 = range(0, len(gt))
        n2 = range(0, len(g))
        self.covariance_fig.plot(n2, g, n1, gt)

        gmin = np.min(np.concatenate([g, gt]))
        gmax = np.max(np.concatenate([g, gt]))
        self.comparison_fig.plot(g, gt, gmin, gmax)

    def calculate(self):
        self.apply_booleans()
        if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
            xc = self.temp_grid.getCellCenter()
            cm = self.current_covar()
            Cm = cm.compute(xc, xc)

            s = (self.data[:, 0].reshape(-1) / np.sum(self.L, 1).reshape(-1)).T
            s0 = np.mean(s)

            if cm.use_xi:
                if cm.use_tilt:
                    np_ = self.L.shape[1] / 2
                    l = np.sqrt(self.L[:, 0:np_] ** 2 + self.L[:, (np_):] ** 2)
                    s0 = np.mean(self.data[:, 0] / sum(l, 1)) + np.zeros([np_, 1])
                    xi0 = np.ones([np_, 1]) + 0.001       # add 1/1000 so that J_th != 0
                    theta0 = np.zeros([np_, 1]) + 0.0044  # add a quarter of a degree so that J_th != 0
                    J = covar.computeJ2(self.L, np.concatenate([s0, xi0, theta0]))
                    Cm = J.dot(np.dot(Cm, J.T.toarray()))
                else:
                    np_ = self.L.shape[1] / 2
                    l = np.sqrt(self.L[:, 0:np_] ** 2 + self.L[:, (np_):] ** 2)
                    s0 = np.mean(self.data[:, 0] / sum(l, 1)) + np.zeros([np_, 1])
                    xi0 = np.ones([np_, 1])
                    J = covar.computeJ(self.L, np.concatenate([s0, xi0]))
                    Cm = J.dot(np.dot(Cm, J.T.toarray()))
            else:
                Cm = self.L.dot(Cm.dot(self.L.T.toarray()))

            if cm.use_c0:
                # use exp variance
                c0 = self.data[:, 1] ** 2
                Cm += cm.nugget_data * np.diag(c0)
            else:
                Cm += cm.nugget_data * np.eye(self.L.shape[0])

            Cm = Cm.flatten()
            ind = np.argsort(Cm)
            ind = ind[::-1]
            Cm = Cm[ind]
            lclas = int(self.bin_edit.text())
            afi = float(self.bin_frac_edit.text())

            gt = covar.moy_bloc(Cm, lclas)
            ind0 = np.where(gt < np.inf)
            gt = gt[ind0].T

            g = self.Cd[ind]
            g = covar.moy_bloc(g, lclas)
            g = g[ind0].T

            N = int(np.round(len(g) * afi))
            g = g[0:N]
            gt = gt[0:N]

            return g,gt
    def show_stats(self):
        if self.model is not None:
            if self.mogs_list.selectedIndexes() != []:

                L = self.temp_grid.getForwardStraightRays(ind=self.idata)
                s = (self.data[:, 0].reshape(-1) / np.sum(L, 1).reshape(-1)).T

                if self.T_and_A_combo.currentIndex() == 0:
                    s = 1 / s
                    data_type = 'tt'
                else:
                    data_type = 'amp'

                s0 = np.mean(s)
                vs = np.var(s)
                Tx = self.temp_grid.Tx[self.idata, :]
                Rx = self.temp_grid.Rx[self.idata, :]
                hyp = np.sqrt(np.sum((Tx - Rx) ** 2, 1))
                dz = Tx[:, 2] - Rx[:, 2]
                theta = 180 / np.pi * np.arcsin(dz / hyp)

                self.statistics_fig.plot(data_type, s, hyp, theta, s0, vs)
                self.statistics_form.show()

            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', "No MOG selected.")

    def clear_figures(self):
        self.covariance_fig.clear_()
        self.comparison_fig.clear_()
        self.statistics_fig.clear_()

    def initUI(self):

        # --- Color for the labels --- #
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)

        class MyQLabel(QtWidgets.QLabel):  # allows a custom alignment
            def __init__(self, label, ha='left', parent=None):
                super(MyQLabel, self).__init__(label, parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        class MyLineEdit(QtWidgets.QLineEdit):  # allows verifying if an edit's text has been modified
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
        self.btn_compute = QtWidgets.QPushButton("Compute")
        self.btn_GO = QtWidgets.QPushButton("GO")

        # --- Labels --- #
        self.model_label = MyQLabel("Model :", ha='left')
        cells_label = MyQLabel("Cells", ha='left')
        cells_labeli = MyQLabel("Cells", ha='left')
        rays_label = MyQLabel("Rays", ha='left')
        self.cells_no_label = MyQLabel("0", ha='right')
        self.cells_no_labeli = MyQLabel("0", ha='right')
        self.rays_no_label = MyQLabel("0", ha='right')

        curv_rays_label = MyQLabel("Curved Rays", ha='right')
        X_label = MyQLabel("X", ha='center')
        Y_label = MyQLabel("Y", ha='center')
        Z_label = MyQLabel("Z", ha='center')
        Xi_label = MyQLabel("X", ha='center')
        Yi_label = MyQLabel("Y", ha='center')
        Zi_label = MyQLabel("Z", ha='center')
        self.X_min_label = MyQLabel("0", ha='center')
        self.Y_min_label = MyQLabel("0", ha='center')
        self.Z_min_label = MyQLabel("0", ha='center')
        self.X_max_label = MyQLabel("0", ha='center')
        self.Y_max_label = MyQLabel("0", ha='center')
        self.Z_max_label = MyQLabel("0", ha='center')

        Min_label = MyQLabel("Min", ha='left')
        Max_label = MyQLabel("Max", ha='left')
        step_label = MyQLabel("Step :", ha='center')
        self.slowness_label = MyQLabel("Slowness", ha='right')
        self.tt_label = MyQLabel("Traveltime", ha='right')
        self.xi_label = MyQLabel(xi, ha='right')
        self.tilt_label = MyQLabel("Tilt Angle", ha='right')
        bin_label = MyQLabel("Bin Length", ha='right')
        bin_frac_label = MyQLabel("Fraction of Bins", ha='right')
        Iter_label = MyQLabel("Number of Iterations", ha='right')

        for item in (self.X_min_label, self.Y_min_label, self.Z_min_label,
                     self.X_max_label, self.Y_max_label, self.Z_max_label,
                     self.cells_no_label, self.cells_no_labeli, self.rays_no_label,
                     cells_label, cells_labeli, rays_label):
            item.setPalette(palette)

        # --- Edits --- #
        self.velocity_edit = MyLineEdit()
        self.step_X_edit = MyLineEdit()
        self.step_X_edit.setFixedWidth(50)
        self.step_Y_edit = MyLineEdit()
        self.step_Y_edit.setFixedWidth(50)
        self.step_Z_edit = MyLineEdit()
        self.step_Z_edit.setFixedWidth(50)
        self.slowness_edit = MyLineEdit('0.0')
        self.tt_edit = MyLineEdit('0.0')
        self.xi_edit = MyLineEdit('0.0')
        self.tilt_edit = MyLineEdit('0.0')
        self.bin_edit = MyLineEdit('50')
        self.bin_frac_edit = MyLineEdit('0.25')
        self.Iter_edit = MyLineEdit('5')

        # --- Checkboxes --- #
        self.Upper_limit_checkbox = QtWidgets.QCheckBox("Upper Limit - Apparent Velocity")
        self.ellip_veloc_checkbox = QtWidgets.QCheckBox("Elliptical Velocity Anisotropy")
        self.tilted_ellip_veloc_checkbox = QtWidgets.QCheckBox("Tilted Elliptical Velocity Anisotropy")
        self.include_checkbox = QtWidgets.QCheckBox("Include Experimental Variance")
        self.slowness_checkbox = QtWidgets.QCheckBox()
        self.tt_checkbox = QtWidgets.QCheckBox()
        self.xi_checkbox = QtWidgets.QCheckBox()
        self.tilt_checkbox = QtWidgets.QCheckBox()
        self.auto_update_checkbox = QtWidgets.QCheckBox("Auto Update")

        # --- Figures --- #
        self.covariance_fig = CovarianceFig(self)
        self.comparison_fig = ComparisonFig(self)

        # --- Comboboxes --- #
        self.T_and_A_combo = QtWidgets.QComboBox()
        self.T_and_A_combo.addItem("Traveltime")
        self.T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        self.T_and_A_combo.addItem("Amplitude - Centroid Frequency")
        self.curv_rays_combo = QtWidgets.QComboBox()
        self.covar_struct_combo = QtWidgets.QComboBox()

        # --- List --- #
        self.mogs_list = QtWidgets.QListWidget()
        types = ('Cubic', 'Spherical', 'Gaussian', 'Exponential', 'Linear', 'Thin_Plate',
                 'Gravimetric', 'Magnetic', 'Hole Effect Sine', 'Hole Effect Cosine')

        # --- Parameters --- #
        range_X_label = MyQLabel("Range X", ha='right')
        range_Z_label = MyQLabel("Range Z", ha='right')
        theta_X_label = MyQLabel("{} X".format(theta), ha='right')
        sill_label = MyQLabel("Sill", ha='right')

        self.slowness_param_edit = QtWidgets.QLineEdit('Slowness')
        self.slowness_param_edit.setReadOnly(True)
        self.slowness_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.slowness_type_combo = QtWidgets.QComboBox()
        self.slowness_type_combo.addItems(types)
        slowness_value_label = MyQLabel("Value", ha='center')
        slowness_fix_label = MyQLabel("Fix", ha='center')
        self.slowness_range_X_edit = MyLineEdit('4.0')
        self.slowness_range_Z_edit = MyLineEdit('4.0')
        self.slowness_theta_X_edit = MyLineEdit('0.0')
        self.slowness_sill_edit = MyLineEdit('1.0')
        self.slowness_range_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_range_Z_checkbox = QtWidgets.QCheckBox()
        self.slowness_theta_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_sill_checkbox = QtWidgets.QCheckBox()

        xi_param_edit = QtWidgets.QLineEdit(xi)
        xi_param_edit.setReadOnly(True)
        xi_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.xi_type_combo = QtWidgets.QComboBox()
        self.xi_type_combo.addItems(types)
        xi_value_label = MyQLabel("Value", ha='center')
        xi_fix_label = MyQLabel("Fix", ha='center')
        self.xi_range_X_edit = MyLineEdit('4.0')
        self.xi_range_Z_edit = MyLineEdit('4.0')
        self.xi_theta_X_edit = MyLineEdit('0.0')
        self.xi_sill_edit = MyLineEdit('1.0')
        self.xi_range_X_checkbox = QtWidgets.QCheckBox()
        self.xi_range_Z_checkbox = QtWidgets.QCheckBox()
        self.xi_theta_X_checkbox = QtWidgets.QCheckBox()
        self.xi_sill_checkbox = QtWidgets.QCheckBox()

        tilt_param_edit = QtWidgets.QLineEdit('Tilt Angle')
        tilt_param_edit.setReadOnly(True)
        tilt_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.tilt_type_combo = QtWidgets.QComboBox()
        self.tilt_type_combo.addItems(types)
        tilt_value_label = MyQLabel("Value", ha='center')
        tilt_fix_label = MyQLabel("Fix", ha='center')
        self.tilt_range_X_edit = MyLineEdit('4.0')
        self.tilt_range_Z_edit = MyLineEdit('4.0')
        self.tilt_theta_X_edit = MyLineEdit('0.0')
        self.tilt_sill_edit = MyLineEdit('1.0')
        self.tilt_range_X_checkbox = QtWidgets.QCheckBox()
        self.tilt_range_Z_checkbox = QtWidgets.QCheckBox()
        self.tilt_theta_X_checkbox = QtWidgets.QCheckBox()
        self.tilt_sill_checkbox = QtWidgets.QCheckBox()

        range_X_3D_label = MyQLabel("Range X", ha='right')
        range_Y_3D_label = MyQLabel("Range Y", ha='right')
        range_Z_3D_label = MyQLabel("Range Z", ha='right')
        theta_X_3D_label = MyQLabel("{} X".format(theta), ha='right')
        theta_Y_3D_label = MyQLabel("{} Y".format(theta), ha='right')
        theta_Z_3D_label = MyQLabel("{} Z".format(theta), ha='right')
        sill_3D_label = MyQLabel("Sill", ha='right')

        self.slowness_3D_param_edit = QtWidgets.QLineEdit('Slowness')
        self.slowness_3D_param_edit.setReadOnly(True)
        self.slowness_3D_param_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.slowness_3D_type_combo = QtWidgets.QComboBox()
        self.slowness_3D_type_combo.addItems(types)
        slowness_3D_value_label = MyQLabel("Value", ha='center')
        slowness_3D_fix_label = MyQLabel("Fix", ha='center')
        self.slowness_3D_range_X_edit = MyLineEdit('4.0')
        self.slowness_3D_range_Y_edit = MyLineEdit('4.0')
        self.slowness_3D_range_Z_edit = MyLineEdit('4.0')
        self.slowness_3D_theta_X_edit = MyLineEdit('0.0')
        self.slowness_3D_theta_Y_edit = MyLineEdit('0.0')
        self.slowness_3D_theta_Z_edit = MyLineEdit('0.0')
        self.slowness_3D_sill_edit = MyLineEdit('1.0')
        self.slowness_3D_range_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_range_Y_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_range_Z_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_theta_X_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_theta_Y_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_theta_Z_checkbox = QtWidgets.QCheckBox()
        self.slowness_3D_sill_checkbox = QtWidgets.QCheckBox()

        # Widgets grouping.  Unpacking those will produce clearer code.  #

        labels = (range_X_label, range_Z_label, theta_X_label, sill_label)

        self.slowness_edits = (self.slowness_range_X_edit, self.slowness_range_Z_edit, self.slowness_theta_X_edit, self.slowness_sill_edit)
        self.slowness_checkboxes = (self.slowness_range_X_checkbox, self.slowness_range_Z_checkbox, self.slowness_theta_X_checkbox, self.slowness_sill_checkbox)

        self.slowness_widget = (*labels, *self.slowness_edits, *self.slowness_checkboxes, self.slowness_param_edit, self.slowness_type_combo, slowness_value_label, slowness_fix_label)

        self.xi_edits = (self.xi_range_X_edit, self.xi_range_Z_edit, self.xi_theta_X_edit, self.xi_sill_edit)
        self.xi_checkboxes = (self.xi_range_X_checkbox, self.xi_range_Z_checkbox, self.xi_theta_X_checkbox, self.xi_sill_checkbox)

        self.xi_widget = (*self.xi_edits, *self.xi_checkboxes, xi_param_edit, self.xi_type_combo, xi_value_label, xi_fix_label)

        self.tilt_edits = (self.tilt_range_X_edit, self.tilt_range_Z_edit, self.tilt_theta_X_edit, self.tilt_sill_edit)
        self.tilt_checkboxes = (self.tilt_range_X_checkbox, self.tilt_range_Z_checkbox, self.tilt_theta_X_checkbox, self.tilt_sill_checkbox)

        self.tilt_widget = (*self.tilt_edits, *self.tilt_checkboxes, tilt_param_edit, self.tilt_type_combo, tilt_value_label, tilt_fix_label)

        self.labels_3d = (range_X_3D_label, range_Y_3D_label, range_Z_3D_label, theta_X_3D_label, theta_Y_3D_label, theta_Z_3D_label, sill_3D_label)  # @UnusedVariable

        self.slowness_3D_edits = (self.slowness_3D_range_X_edit, self.slowness_3D_range_Y_edit, self.slowness_3D_range_Z_edit,
                                       self.slowness_3D_theta_X_edit, self.slowness_3D_theta_Y_edit, self.slowness_3D_theta_Z_edit, self.slowness_3D_sill_edit)
        self.slowness_3D_checkboxes = (self.slowness_3D_range_X_checkbox, self.slowness_3D_range_Y_checkbox, self.slowness_3D_range_Z_checkbox,
                                       self.slowness_3D_theta_X_checkbox, self.slowness_3D_theta_Y_checkbox, self.slowness_3D_theta_Z_checkbox, self.slowness_3D_sill_checkbox)

        self.nugget_checkboxes = (self.slowness_checkbox, self.tt_checkbox)

        self.nugget_edits = (self.slowness_edit, self.tt_edit,self.xi_edit,self.tilt_edit)

        # ------- SubWidgets ------- #
        Sub_Curved_Rays_Widget = lay([curv_rays_label, self.curv_rays_combo],
                                     'noMargins')

        Sub_Grid_Coord_Widget = lay([['',        X_label,          Y_label,          Z_label],
                                     [Min_label, self.X_min_label, self.Y_min_label, self.Z_min_label],
                                     [Max_label, self.X_max_label, self.Y_max_label, self.Z_max_label]],
                                    ('setHorSpa', 20),
                                    ('setMinWid', (self.X_min_label, self.Y_min_label, self.Z_min_label,
                                                   Max_label, self.X_max_label, self.Y_max_label, self.Z_max_label), 40))

        cells_no_widget = lay([self.cells_no_labeli, cells_labeli])

        Sub_Step_Widget = lay([['',         Xi_label,         Yi_label,         Zi_label],
                               [step_label, self.step_X_edit, self.step_Y_edit, self.step_Z_edit],
                               ['',         cells_no_widget,  '',               '|']],
                              ('setHorSpa', 0))

        data_groupbox = lay([[self.model_label,    '|',         self.Upper_limit_checkbox,        self.velocity_edit],
                             [self.cells_no_label, cells_label, self.ellip_veloc_checkbox,        ''],
                             [self.rays_no_label,  rays_label,  self.tilted_ellip_veloc_checkbox, ''],
                             [self.mogs_list,      '|',         self.include_checkbox,            ''],
                             ['',                  '',          self.T_and_A_combo,               self.btn_Show_Stats],
                             ['_',                 '',          Sub_Curved_Rays_Widget,           '']],
                            ('setMaxHei', self.mogs_list, self.curv_rays_combo.sizeHint().height() * 3.6))

        self.Grid_groupbox = lay([Sub_Grid_Coord_Widget, Sub_Step_Widget],
                                 'noMargins', ('groupbox', "Grid"))

        self.param_widget = lay([['',            self.slowness_param_edit,   '|',                            xi_param_edit,        '|',                      tilt_param_edit,        '|'],
                                 ['',            self.slowness_type_combo,   '|',                            self.xi_type_combo,   '|',                      self.tilt_type_combo,   '|'],
                                 ['',            slowness_value_label,       slowness_fix_label,             xi_value_label,       xi_fix_label,             tilt_value_label,       tilt_fix_label],
                                 [range_X_label, self.slowness_range_X_edit, self.slowness_range_X_checkbox, self.xi_range_X_edit, self.xi_range_X_checkbox, self.tilt_range_X_edit, self.tilt_range_X_checkbox],
                                 [range_Z_label, self.slowness_range_Z_edit, self.slowness_range_Z_checkbox, self.xi_range_Z_edit, self.xi_range_Z_checkbox, self.tilt_range_Z_edit, self.tilt_range_Z_checkbox],
                                 [theta_X_label, self.slowness_theta_X_edit, self.slowness_theta_X_checkbox, self.xi_theta_X_edit, self.xi_theta_X_checkbox, self.tilt_theta_X_edit, self.tilt_theta_X_checkbox],
                                 [sill_label,    self.slowness_sill_edit,    self.slowness_sill_checkbox,    self.xi_sill_edit,    self.xi_sill_checkbox,    self.tilt_sill_edit,    self.tilt_sill_checkbox]],
                                'noMargins')

        self.slowness_3D_widget = lay([['',               self.slowness_3D_param_edit,   '|'],
                                       ['',               self.slowness_3D_type_combo,   '|'],
                                       ['',               slowness_3D_value_label,       slowness_3D_fix_label],
                                       [range_X_3D_label, self.slowness_3D_range_X_edit, self.slowness_3D_range_X_checkbox],
                                       [range_Y_3D_label, self.slowness_3D_range_Y_edit, self.slowness_3D_range_Y_checkbox],
                                       [range_Z_3D_label, self.slowness_3D_range_Z_edit, self.slowness_3D_range_Z_checkbox],
                                       [theta_X_3D_label, self.slowness_3D_theta_X_edit, self.slowness_3D_theta_X_checkbox],
                                       [theta_Y_3D_label, self.slowness_3D_theta_Y_edit, self.slowness_3D_theta_Y_checkbox],
                                       [theta_Z_3D_label, self.slowness_3D_theta_Z_edit, self.slowness_3D_theta_Z_checkbox],
                                       [sill_3D_label,    self.slowness_3D_sill_edit,    self.slowness_3D_sill_checkbox]],
                                      'noMargins')

        Param_groupbox = lay(['', self.param_widget, self.slowness_3D_widget, ''],
                             ('setColStr', (0, 1), (1, 0), (2, 0), (3, 1)))

        self.Nug_groupbox = lay([[self.slowness_label, self.slowness_edit, self.slowness_checkbox, self.tt_label,   self.tt_edit,   self.tt_checkbox],
                                 [self.xi_label,       self.xi_edit,       self.xi_checkbox,       self.tilt_label, self.tilt_edit, self.tilt_checkbox]],
                                ('groupbox', "Nugget Effect"))

        covar_groupbox = lay([[self.covar_struct_combo,   self.btn_Add_Struct, self.btn_Rem_Struct],
                              [Param_groupbox,            '',                  '|'],
                              [self.Nug_groupbox,         '',                  '|'],
                              [self.auto_update_checkbox, '|',                 self.btn_compute]],
                             'groupbox')

        self.Adjust_Model_groupbox = lay([[bin_label,      self.bin_edit,      self.btn_GO],
                                          [bin_frac_label, self.bin_frac_edit, ''],
                                          [Iter_label,     self.Iter_edit,     '_']],
                                         ('groupbox', "Adjust Model (Simplex Method)"))

        self.Sub_widget = inv_lay([data_groupbox, self.Grid_groupbox, covar_groupbox, self.Adjust_Model_groupbox],
                                  'noMargins')

        self.scrollbar = lay([[self.covariance_fig, self.Sub_widget],
                              [self.comparison_fig, '_']],
                             'scrollbar', 'noMargins', ('setMinWid', 0, 600))

        # Master Grid Disposition #
        inv_lay([self.menu, self.scrollbar],
                'noMargins', ('setVerSpa', 0), parent=self)

        # ------- Actions ------- #
        self.btn_Show_Stats.clicked.connect(self.show_stats)
        self.btn_Add_Struct.clicked.connect(self.add_struct)
        self.btn_Rem_Struct.clicked.connect(self.del_struct)
        self.btn_compute   .clicked.connect(self.compute)
        self.btn_GO        .clicked.connect(self.adjustInThread)

        self.Upper_limit_checkbox       .clicked.connect(self.auto_update)
        self.Upper_limit_checkbox       .clicked.connect(self.update_velocity_display)
        self.ellip_veloc_checkbox       .clicked.connect(self.parameters_displayed_update)
        self.tilted_ellip_veloc_checkbox.clicked.connect(self.parameters_displayed_update)
        self.ellip_veloc_checkbox       .clicked.connect(self.auto_update)
        self.tilted_ellip_veloc_checkbox.clicked.connect(self.auto_update)
        self.include_checkbox           .clicked.connect(self.auto_update)

        self.T_and_A_combo     .currentIndexChanged.connect(self.update_structures)
        self.covar_struct_combo.currentIndexChanged.connect(self.parameters_displayed_update)

        self.slowness_type_combo   .currentIndexChanged.connect(self.change_covar_type_slowness)
        self.xi_type_combo         .currentIndexChanged.connect(self.change_covar_type_xi)
        self.tilt_type_combo       .currentIndexChanged.connect(self.change_covar_type_tilt)
        self.slowness_3D_type_combo.currentIndexChanged.connect(self.change_covar_type_slowness)

        self.step_X_edit.textModified.connect(self.update_temp_grid)
        self.step_Y_edit.textModified.connect(self.update_temp_grid)
        self.step_Z_edit.textModified.connect(self.update_temp_grid)

        for item in (*self.slowness_checkboxes, *self.xi_checkboxes, *self.tilt_checkboxes, *self.slowness_3D_checkboxes, *self.nugget_checkboxes, self.tilt_checkbox, self.xi_checkbox):
            item.clicked.connect(self.fix_verif)

        for item in (*self.slowness_edits, *self.xi_edits, *self.tilt_edits, *self.slowness_3D_edits, *self.nugget_edits):
            item.textModified.connect(self.apply_parameters_changes)
            item.textModified.connect(self.auto_update)

        for item in (self.velocity_edit, self.step_X_edit, self.step_Y_edit, self.step_Z_edit):
            item.textModified.connect(self.auto_update)

        for item in (self.T_and_A_combo, self.curv_rays_combo, self.curv_rays_combo):
            item.currentIndexChanged.connect(self.auto_update)

        # ------- Sizes ------- #
        for item in (self.menu, data_groupbox, self.Grid_groupbox,
                     Param_groupbox, self.Nug_groupbox, self.Adjust_Model_groupbox):
            item.setFixedHeight(item.sizeHint().height())
        self.Sub_widget.setFixedWidth(500)

        for item in (slowness_value_label, xi_value_label, tilt_value_label, slowness_3D_value_label,
                     slowness_fix_label, xi_fix_label, tilt_fix_label, slowness_3D_fix_label,
                     range_X_label, range_Z_label, theta_X_label, sill_label):
            item.setFixedHeight(25)

        # --- Statistics Form --- #

        self.statistics_fig = StatisticsFig(self)
        self.statistics_form = QtWidgets.QWidget()
        lay([self.statistics_fig], 'noMargins', parent=self.statistics_form)
        self.statistics_form.setMinimumSize(self.statistics_form.sizeHint().height(),
                                            self.statistics_form.sizeHint().width())

        # --- Computing form --- #

        self.computing_form = QtWidgets.QWidget()
        self.computing_form.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.progress_lbl = MyQLabel("Computing.\nPlease wait...", ha='center')
        inv_lay([self.progress_lbl], parent=self.computing_form)


class StatisticsFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure()
        super(StatisticsFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312)
        self.ax3 = self.figure.add_subplot(313)
        self.ax2.set_xlabel("Straight Ray Length")
        self.ax3.set_xlabel("Straight Ray Angle")

    def plot(self, data_type, s, hyp, theta, s0, vs):

        if data_type == 'tt':
            data_name = "App. Velocity"
        elif data_type == 'amp':
            data_name = "App. Attenuation"

        self.clear_()
        self.ax1.hist(s, 30)
        self.ax2.plot(hyp, s, 'b+')
        self.ax3.plot(theta, s, 'b+')
        s0, vs = str(s0), str(vs)

        if s0[-4] == 'e':
            s0 = s0[:5] + s0[-4:]
        else:
            s0 = s0[:9]

        if vs[-4] == 'e':
            vs = vs[:5] + vs[-4:]
        else:
            vs = vs[:9]

        self.ax1.set_title("{}: {} $\pm$ {}".format(data_name, s0, vs))
        self.ax2.set_xlabel("Straight Ray Length")
        self.ax3.set_xlabel("Straight Ray Angle")
        self.ax2.set_ylabel(data_name)
        self.ax3.set_ylabel(data_name)

        self.figure.tight_layout(h_pad=1)
        self.draw()

    def clear_(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.draw()


class CovarianceFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(CovarianceFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_subplot(111)
        self.ax.set_ylabel("Covariance")
        self.ax.set_xlabel("Bin Number")

    def plot(self, n2, g, n1, gt):
        self.clear_()
        self.ax.plot(n2, g, '+', n1, gt, 'o')
        self.ax.legend(('Experimental ($C_d^*$)', 'Model ($GC_mG^T+C_0$)'), loc=1)
        self.figure.tight_layout()
        self.draw()

    def clear_(self):
        self.ax.clear()
        self.ax.set_ylabel("Covariance")
        self.ax.set_xlabel("Bin Number")
        self.draw()


class ComparisonFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(ComparisonFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_subplot(111)
        self.ax.set_ylabel("Model Covariance")
        self.ax.set_xlabel("Experimental Covariance")
        self.ax.set_aspect('equal')

    def plot(self, g, gt, gmin, gmax):
        self.clear_()
        self.ax.plot(g, gt, 'o', (gmin, gmax), (gmin, gmax), ':')
        self.figure.tight_layout()
        self.draw()

    def clear_(self):
        self.ax.clear()
        self.ax.set_ylabel("Model Covariance")
        self.ax.set_xlabel("Experimental Covariance")
        self.draw()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    database.create_data_management(database)
    database.load(database, 'database.db')

    Covar_ui = CovarUI()
    Covar_ui.show()

    sys.exit(app.exec_())

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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy import interpolate

from model import Model
from inversion import invLSQR, InvLSQRParams, invGeostat
from utils import set_tick_arrangement, ComputeThread
from utils_ui import MyQLabel, chooseModel, save_warning
from mog import Mog
from database import BhTomoDb
import covar


class InversionUI(QtWidgets.QFrame):
    InvIterationDone = QtCore.pyqtSignal(int, np.ndarray, str)   # Signal when a iteration is done
    InvDone = QtCore.pyqtSignal(int, str)                 # Signal when the inversion is done

    def __init__(self, parent=None):
        super(InversionUI, self).__init__(parent)
        self.setWindowTitle("BhTomoPy/Inversion")
        self.db = BhTomoDb()
        self.lsqrParams = InvLSQRParams()
        self.tomo = None
        self.prev_inv = []
        self.model_ind = ''
        self.init_UI()
        self.initinvUI()
        self.model = None

        # Signals
        self.InvIterationDone.connect(self.handleInvIterationDone) 
        self.InvDone.connect(self.handleInvDone)

    def show(self, dbname):
        super(InversionUI, self).show()
        if dbname != '':
            try:
                self.db.filename = dbname
            except Exception as e:
                    QtWidgets.QMessageBox.warning(self, 'Error', str(e))

        # Gets initial geometry of the widget:
        qr = self.frameGeometry()

        # Shows it at the center of the screen
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()

        # Moves the window's center at the center of the screen
        qr.moveCenter(cp)
        # Then moves it at the top left
        translation = qr.topLeft()

        self.move(translation)
        
    def handleInvIterationDone(self, noIter, tomo_s, type_inv):
        self.algo_label.setText('{} inversion -'.format(type_inv))
        self.noIter_label.setText('Ray Tracing, Iteration {}'.format(noIter))
        self.gv.invFig.plot_lsqr_inv(tomo_s)
    
    def handleInvDone(self, noIter, type_inv):
        self.algo_label.setText('{} inversion -'.format(type_inv))
        self.noIter_label.setText('Finished, {} Iterations Done'.format(noIter))

    def savefile(self):
        if self.model_ind == '':
            # If there's no selected model
            return
        if self.tomo is None:
            return
        if self.algo_combo.currentText() == 'LSQR Solver':
            cov = '-LSQR'
        if self.T_and_A_combo.currentText() == 'Traveltime':
            dType = '-vel'
        else:
            dType = '-att'

        inversion_name, ok = QtWidgets.QInputDialog.getText(self, 'Save inversion results',
                                                            'Name of Inversion:',
                                                            text='tomo (insert date) {} {}'.format(dType, cov))
        if ok:
            inv_res_info = (inversion_name, self.tomo, self.lsqrParams)
            self.model.inv_res.append(inv_res_info)
            self.db.save_model(self.model)

        QtWidgets.QMessageBox.information(self, 'Success', "Database was saved successfully",
                                          buttons=QtWidgets.QMessageBox.Ok)
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

    def openfile(self):
        new_model, self.db = chooseModel(self.db)
        if new_model is not None:
            self.set_current_model(new_model)

    def set_current_model(self, model):
        if self.model is not None:
            if self.model.modified and save_warning(self.db):
                self.model = model
                if model.grid is not None:
                    self.updateDatabaseInfos()
        else:
            self.model = model
            if model.grid is not None:
                self.updateDatabaseInfos()

    def updateDatabaseInfos(self):
        """
        Update the interface with the new database informations
        """
        self.inv_frame.setHidden(True)
        self.gv = Gridviewer(self.model.grid, self)
        self.global_grid.addWidget(self.gv, 1, 1, 7, 2)
        self.update_data()
        self.update_grid()
        self.update_previous()

    def update_previous(self):
        self.prev_inversion_combo.clear()
        self.prev_inv.clear()
        if self.model is not None:
            for result in self.model.inv_res:

                # result[0] == name
                # result[1] == tomo
                # result[2] == params

                self.prev_inversion_combo.addItem(result[0])
                self.prev_inv.append(result)

    def update_data(self):
        for mog in self.model.mogs:
            self.mog_list.addItem(mog.name)
        self.mog_list.setCurrentRow(0)

    def update_grid(self):
        if np.all(self.model.grid.grx == 0) or np.all(self.model.grid.grx == 0):
            QtWidgets.QMessageBox.warning(self, 'Warning', "Please create a Grid before Inversion",
                                          buttons=QtWidgets.QMessageBox.Ok)

        else:
            self.X_min_label.setText(str(np.round(self.model.grid.grx[0], 3)))
            self.X_max_label.setText(str(np.round(self.model.grid.grx[-1], 3)))
            self.step_Xi_label.setText(str(self.model.grid.dx))

            self.Z_min_label.setText(str(np.round(self.model.grid.grz[0], 3)))
            self.Z_max_label.setText(str(np.round(self.model.grid.grz[-1], 3)))
            self.step_Zi_label.setText(str(self.model.grid.dz))

            if self.model.grid.type == '3D':
                self.Y_min_label.setText(str(np.round(self.model.grid.gry[0], 3)))
                self.Y_max_label.setText(str(np.round(self.model.grid.gry[-1], 3)))
                self.step_Yi_label.setText(str(self.model.grid.dy))

            self.num_cells_label.setText(str(self.model.grid.getNumberOfCells()))

    def update_params(self):
        
        self.lsqrParams.numItStraight = int(self.straight_ray_edit.text())
        self.lsqrParams.numItCurved = int(self.curv_ray_edit.text())
        self.lsqrParams.selectedMogs = self.mog_list.selectedIndexes()
        self.lsqrParams.selectedMogs = [i.row() for i in self.lsqrParams.selectedMogs]
        self.lsqrParams.useCont = self.use_const_checkbox.isChecked()
        if self.algo_combo.currentText() == 'LSQR Solver':
            self.lsqrParams.tol = float(self.solver_tol_edit.text())
            self.lsqrParams.wCont = float(self.constraints_weight_edit.text())
            self.lsqrParams.alphax = float(self.smoothing_weight_x_edit.text())
            self.lsqrParams.alphay = float(self.smoothing_weight_y_edit.text())
            self.lsqrParams.alphaz = float(self.smoothing_weight_z_edit.text())
            self.lsqrParams.order = int(self.smoothing_order_combo.currentText())
            self.lsqrParams.nbreiter = float(self.max_iter_edit.text())
            self.lsqrParams.dv_max = 0.01 * float(self.veloc_var_edit.text())

        if self.algo_combo.currentText() == 'Geostatistical':
            covar_ = self.current_covar()
            ind = self.geostat_struct_combo.currentIndex()

            if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                covar_.covar[ind].range[0] = float(self.slowness_range_X_edit.text())
                covar_.covar[ind].range[1] = float(self.slowness_range_Z_edit.text())
                covar_.covar[ind].angle[0] = float(self.slowness_theta_X_edit.text())
                covar_.covar[ind].sill = float(self.slowness_sill_edit   .text())
                covar_.nugget_model = float(self.slowness_edit        .text())
                covar_.nugget_data = float(self.traveltime_edit              .text())

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

    def update_input_params(self):
        self.straight_ray_edit.setText(str(self.lsqrParams.numItStraight))
        self.curv_ray_edit.setText(str(self.lsqrParams.numItCurved))
        self.use_const_checkbox.setChecked(self.lsqrParams.useCont)
        self.solver_tol_edit.setText(str(self.lsqrParams.tol))
        self.constraints_weight_edit.setText(str(self.lsqrParams.wCont))
        self.smoothing_weight_x_edit.setText(str(self.lsqrParams.alphax))
        self.smoothing_weight_y_edit.setText(str(self.lsqrParams.alphay))
        self.smoothing_weight_z_edit.setText(str(self.lsqrParams.alphaz))
        self.smoothing_order_combo.setCurrentIndex(self.lsqrParams.order - 2)
        self.max_iter_edit.setText(str(self.lsqrParams.nbreiter))
        self.veloc_var_edit.setText(str(self.lsqrParams.dv_max))
        self.update_params()

    def doInvLSQR_inThread(self, data, idata, L):
        self.tomo = invLSQR(self.lsqrParams, data, idata, self.model.grid, L, None, self)

    def doInvGeostatistic_inThread(self, data, idata, L):
        self.tomo = invGeostat(self.lsqrParams, data, idata, self.model.grid,self.current_covar(), L, None, self)

    def doInv(self):
        if self.model is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', "First, load a model in order to do Inversion",
                                          buttons=QtWidgets.QMessageBox.Ok)

        if len(self.mog_list.selectedIndexes()) == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Please select Mogs",
                                          buttons=QtWidgets.QMessageBox.Ok)

        elif self.T_and_A_combo.currentText() == 'Traveltime':
            self.lsqrParams.tomoAtt = 0
            data, idata = Model.getModelData(self.model, self.lsqrParams.selectedMogs, 'tt')
            data = np.concatenate((self.model.grid.Tx[idata, :], self.model.grid.Rx[idata, :], data, self.model.grid.TxCosDir[idata, :], self.model.grid.RxCosDir[idata, :]), axis=1)

        # TODO: Faire les autres cas du self.T_and_A_combo

        L = np.array([])
        rays = np.array([])

        # TODO
        if self.use_Rays_checkbox.isChecked():
            # Change L and Rays
            pass

        self.update_params()
        if self.algo_combo.currentText() == 'LSQR Solver':
            self.compute_thread = ComputeThread(self.doInvLSQR_inThread,data,idata,L)
        elif self.algo_combo.currentText() == 'Geostatistic':
            self.compute_thread = ComputeThread(self.doInvGeostatistic_inThread,data,idata,L)

        self.compute_thread.start()

    def plot_inv(self):
        s = self.tomo.s
        self.gv.invFig.plot_lsqr_inv(s)

    def plot_rays(self):
        if self.tomo is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Inversion needed to access Results",
                                          buttons=QtWidgets.QMessageBox.Ok)
            return

        self.raysFig.plot_rays()
        self.update_Tx_elev()
        self.rays_manager.show()

    def plot_ray_density(self):
        if self.tomo is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Inversion needed to access Results",
                                          buttons=QtWidgets.QMessageBox.Ok)
            return

        self.raydensityFig.plot_ray_density()
        self.ray_density_manager.show()

    def plot_residuals(self):
        if self.tomo is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Inversion needed to access Results",
                                          buttons=QtWidgets.QMessageBox.Ok)
            return

        self.residualsFig.plot_residuals()
        self.residuals_manager.show()

    def plot_tomo(self):
        if self.tomo is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', "Inversion needed to access Results",
                                          buttons=QtWidgets.QMessageBox.Ok)
            return

        self.tomoFig.plot_tomo()
        self.tomo_manager.show()

    def load_prev(self):
        n = self.prev_inversion_combo.currentIndex()
        results = self.model.inv_res[n]
        name = results[0]
        tomo = results[1]
        params = results[2]

        self.tomo = tomo
        if '-LSQR' in name:
            self.lsqrParams = params

        # TODO: Faire une classe contenant les paramètres pour les inversions géostatistiques

        self.algo_label.setText(results[0])
        self.noIter_label.setText('|  {} Iterations'.format(self.lsqrParams.numItCurved + self.lsqrParams.numItStraight))
        self.plot_inv()
        self.update_input_params()

    def view_prev(self):
        self.previnvFig.plot_tomo()
        self.prev_inv_manager.show()

    def delete_prev(self):
        n = self.prev_inversion_combo.currentIndex()
        del self.model.inv_res[n]
        self.update_previous()

    def initinvUI(self):

        # ------- Widget Creation ------- #
        # --- Labels --- #
        num_simulation_label        = MyQLabel("Number of Simulations", ha='right')
        slowness_label              = MyQLabel("Slowness", ha='right')
        islowness_label             = MyQLabel("Slowness", ha='center')
        separ_label                 = MyQLabel("|", ha='center')
        traveltime_label            = MyQLabel("Traveltime", ha='right')
        solver_tol_label            = MyQLabel('Solver Tolerance', ha='right')
        max_iter_label              = MyQLabel('Max number of solver iterations', ha='right')
        constraints_weight_label    = MyQLabel('Constraints weight', ha='right')
        smoothing_weight_x_label    = MyQLabel('Smoothing weight x', ha='right')
        smoothing_weight_y_label    = MyQLabel('Smoothing weight y', ha='right')
        smoothing_weight_z_label    = MyQLabel('Smoothing weight z', ha='right')
        smoothing_order_label       = MyQLabel('Smoothing operator order', ha='right')
        veloc_var_label             = MyQLabel('Max velocity varitation per iteration[%]', ha='right')
        range_x_label = MyQLabel('Range X', ha='right')
        range_z_label = MyQLabel('Range Z', ha='right')
        theta_x_label = MyQLabel('theta X', ha='right')
        sill_label = MyQLabel('Sill', ha='right')

        # --- Edits --- #
        self.num_simulation_edit     = QtWidgets.QLineEdit('128')
        self.slowness_edit           = QtWidgets.QLineEdit('0')
        self.traveltime_edit         = QtWidgets.QLineEdit('0')
        self.solver_tol_edit         = QtWidgets.QLineEdit('1e-6')
        self.max_iter_edit           = QtWidgets.QLineEdit('100')
        self.constraints_weight_edit = QtWidgets.QLineEdit('1')
        self.smoothing_weight_x_edit = QtWidgets.QLineEdit('10')
        self.smoothing_weight_y_edit = QtWidgets.QLineEdit('10')
        self.smoothing_weight_z_edit = QtWidgets.QLineEdit('10')
        self.veloc_var_edit          = QtWidgets.QLineEdit('50')

        self.slowness_range_X_edit = QtWidgets.QLineEdit()
        self.slowness_range_Z_edit = QtWidgets.QLineEdit()
        self.slowness_theta_X_edit = QtWidgets.QLineEdit()
        self.slowness_sill_edit = QtWidgets.QLineEdit()

        # - Edits' Disposition - #
        self.num_simulation_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.slowness_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.traveltime_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.solver_tol_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.max_iter_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.constraints_weight_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.smoothing_weight_x_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.smoothing_weight_y_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.smoothing_weight_z_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.veloc_var_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.slowness_range_X_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.slowness_range_Z_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.slowness_theta_X_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.slowness_sill_edit.setAlignment(QtCore.Qt.AlignHCenter)

        self.num_simulation_edit.setFixedWidth(100)
        self.slowness_edit.setFixedWidth(100)
        self.traveltime_edit.setFixedWidth(100)
        self.solver_tol_edit.setFixedWidth(100)
        self.max_iter_edit.setFixedWidth(100)
        self.constraints_weight_edit.setFixedWidth(100)
        self.smoothing_weight_x_edit.setFixedWidth(100)
        self.smoothing_weight_y_edit.setFixedWidth(100)
        self.smoothing_weight_z_edit.setFixedWidth(100)
        self.veloc_var_edit.setFixedWidth(100)

        # - Edits Actions - #
        self.num_simulation_edit.editingFinished.connect(self.update_params)
        self.slowness_edit.editingFinished.connect(self.update_params)
        self.traveltime_edit.editingFinished.connect(self.update_params)
        self.solver_tol_edit.editingFinished.connect(self.update_params)
        self.max_iter_edit.editingFinished.connect(self.update_params)
        self.constraints_weight_edit.editingFinished.connect(self.update_params)
        self.smoothing_weight_x_edit.editingFinished.connect(self.update_params)
        self.smoothing_weight_y_edit.editingFinished.connect(self.update_params)
        self.smoothing_weight_z_edit.editingFinished.connect(self.update_params)
        self.veloc_var_edit.editingFinished.connect(self.update_params)

        # --- CheckBoxes --- #
        self.simulations_checkbox            = QtWidgets.QCheckBox("Simulations")
        self.include_checkbox                = QtWidgets.QCheckBox("Include Experimental Variance")
        self.tilted_ellip_veloc_checkbox     = QtWidgets.QCheckBox("Tilted Elliptical Velocity Anisotropy")
        self.ellip_veloc_checkbox            = QtWidgets.QCheckBox("Elliptical Velocity Anisotropy")

        # --- ComboBoxes --- #
        self.geostat_struct_combo       = QtWidgets.QComboBox()
        self.smoothing_order_combo      = QtWidgets.QComboBox()
        self.slowness_type_combo = QtWidgets.QComboBox()

        # - Comboboxes Actions - #
        self.smoothing_order_combo.activated.connect(self.update_params)

        # --- Combobox's Items --- #
        params = ['Cubic', 'Sperical', 'Gaussian', 'Exponential', 'Linear', 'Thin Plate', 'Gravimetric', 'Magnetic', 'Hole Effect Sine', 'Hole Effect Cosine']
        self.slowness_type_combo.addItems(params)
        self.geostat_struct_combo.addItem("Structure no 1")
        self.smoothing_order_combo.addItems(['2', '1'])

        # --- Slowness Frame --- #
        slownessFrame = QtWidgets.QFrame()
        slownessGrid = QtWidgets.QGridLayout()
        slownessGrid.addWidget(islowness_label)
        slownessFrame.setLayout(slownessGrid)

        # --- Param SubWidget --- #
        sub_param_widget = QtWidgets.QWidget()
        sub_param_grid = QtWidgets.QGridLayout()
        sub_param_grid.addWidget(slownessFrame, 0, 1)
        sub_param_grid.addWidget(self.slowness_type_combo, 1, 1)
        sub_param_grid.addWidget(range_x_label, 2, 0)
        sub_param_grid.addWidget(range_z_label, 3, 0)
        sub_param_grid.addWidget(theta_x_label, 4, 0)
        sub_param_grid.addWidget(sill_label, 5, 0)
        sub_param_grid.addWidget(self.slowness_range_X_edit, 2, 1)
        sub_param_grid.addWidget(self.slowness_range_Z_edit, 3, 1)
        sub_param_grid.addWidget(self.slowness_theta_X_edit, 4, 1)
        sub_param_grid.addWidget(self.slowness_sill_edit, 5, 1)
        sub_param_widget.setLayout(sub_param_grid)

        # --- Scroll Area which contains the Geostatistical Parameters --- #
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(sub_param_widget)

        # --- Parameters Groupbox --- #
        Param_groupbox = QtWidgets.QGroupBox("Parameters")
        Param_grid = QtWidgets.QGridLayout()
        Param_grid.addWidget(scrollArea, 0, 0)
        Param_grid.setVerticalSpacing(0)
        Param_groupbox.setLayout(Param_grid)

        # --- Nugget Effect Groupbox --- #
        Nug_groupbox = QtWidgets.QGroupBox("Nugget Effect")
        Nug_grid = QtWidgets.QGridLayout()
        Nug_grid.addWidget(slowness_label, 0, 0)
        Nug_grid.addWidget(self.slowness_edit, 0, 1)
        Nug_grid.addWidget(separ_label, 0, 3)
        Nug_grid.addWidget(traveltime_label, 0, 4)
        Nug_grid.addWidget(self.traveltime_edit, 0, 5)
        Nug_groupbox.setLayout(Nug_grid)

        # --- Geostatistical inversion Groupbox --- #
        Geostat_groupbox = QtWidgets.QGroupBox("Geostatistical inversion")
        Geostat_grid = QtWidgets.QGridLayout()
        Geostat_grid.addWidget(self.simulations_checkbox, 0, 0)
        Geostat_grid.addWidget(self.ellip_veloc_checkbox, 1, 0)
        Geostat_grid.addWidget(self.include_checkbox, 2, 0)
        Geostat_grid.addWidget(num_simulation_label, 0, 1)
        Geostat_grid.addWidget(self.num_simulation_edit, 0, 2)
        Geostat_grid.addWidget(self.tilted_ellip_veloc_checkbox, 1, 1)
        Geostat_grid.addWidget(self.geostat_struct_combo, 2, 1, 1, 2)
        Geostat_grid.addWidget(Param_groupbox, 3, 0, 1, 3)
        Geostat_grid.addWidget(Nug_groupbox, 4, 0, 1, 3)
        Geostat_grid.setRowStretch(3, 100)
        Geostat_groupbox.setLayout(Geostat_grid)

        # --- LSQR Solver GroupBox --- #
        LSQR_group = QtWidgets.QGroupBox('LSQR Solver')
        LSQR_grid = QtWidgets.QGridLayout()
        LSQR_grid.addWidget(solver_tol_label, 0, 0)
        LSQR_grid.addWidget(max_iter_label, 1, 0)
        LSQR_grid.addWidget(constraints_weight_label, 2, 0)
        LSQR_grid.addWidget(smoothing_weight_x_label, 3, 0)
        LSQR_grid.addWidget(smoothing_weight_y_label, 4, 0)
        LSQR_grid.addWidget(smoothing_weight_z_label, 5, 0)
        LSQR_grid.addWidget(smoothing_order_label, 6, 0)
        LSQR_grid.addWidget(veloc_var_label, 7, 0)
        LSQR_grid.addWidget(self.solver_tol_edit, 0, 1)
        LSQR_grid.addWidget(self.max_iter_edit, 1, 1)
        LSQR_grid.addWidget(self.constraints_weight_edit, 2, 1)
        LSQR_grid.addWidget(self.smoothing_weight_x_edit, 3, 1)
        LSQR_grid.addWidget(self.smoothing_weight_y_edit, 4, 1)
        LSQR_grid.addWidget(self.smoothing_weight_z_edit, 5, 1)
        LSQR_grid.addWidget(self.smoothing_order_combo, 6, 1)
        LSQR_grid.addWidget(self.veloc_var_edit, 7, 1)
        LSQR_group.setLayout(LSQR_grid)

        current = self.Inv_Param_grid.layout()
        widget = current.itemAtPosition(2, 0).widget()
        widget.setHidden(True)
        self.Inv_Param_grid.removeWidget(widget)

        if self.algo_combo.currentText() == 'LSQR Solver':
            self.Inv_Param_grid.addWidget(LSQR_group, 2, 0, 1, 3)
        else:
            self.Inv_Param_grid.addWidget(Geostat_groupbox, 2, 0, 1, 3)
            self.updateInterfaceParams()
        self.repaint

    def updateInterfaceParams(self):
        if self.algo_combo.currentText() == "Geostatistic" and self.model is not None:
            covar_ = self.current_covar()
            ind = self.geostat_struct_combo.currentIndex()

            self.ellip_veloc_checkbox       .setCheckState(covar_.use_xi)
            self.tilted_ellip_veloc_checkbox.setCheckState(covar_.use_tilt)
            self.include_checkbox           .setCheckState(covar_.use_c0)

            if ind != -1:
                if self.model.grid.type == '2D' or self.model.grid.type == '2D+':
                    self.slowness_type_combo  .setCurrentIndex(covar_.covar[ind].type)
                    self.slowness_range_X_edit.setText(str(covar_.covar[ind].range[0]))
                    self.slowness_range_Z_edit.setText(str(covar_.covar[ind].range[1]))
                    self.slowness_theta_X_edit.setText(str(covar_.covar[ind].angle[0]))
                    self.slowness_sill_edit   .setText(str(covar_.covar[ind].sill))
                    self.slowness_edit        .setText(str(covar_.nugget_model))
                    self.traveltime_edit       .setText(str(covar_.nugget_data))

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
                    self.traveltime_edit          .setText(str(covar_.nugget_data))

    def update_Tx_elev(self):
        mog = self.model.mogs[self.mog_list.selectedIndexes()[0].row()]
        n = int(self.trace_num_edit.text()) - 1
        elev = np.unique(mog.data.Tx_z)[n]

        if not self.entire_coverage_check.isChecked():
            self.value_elev_label.setText(str(elev))
        else:
            self.value_elev_label.setText('-')

    def next_trace(self):
        n = int(self.trace_num_edit.text())
        n += 1
        self.trace_num_edit.setText(str(n))
        self.plot_rays()

    def prev_trace(self):
        n = int(self.trace_num_edit.text())
        n -= 1
        self.trace_num_edit.setText(str(n))
        self.plot_rays()

    def init_UI(self):

        # -------- Widgets in RaysFig -------- #
        # --- Edit --- #
        self.trace_num_edit = QtWidgets.QLineEdit('1')

        # - Edit's Actions - #
        self.trace_num_edit.editingFinished.connect(self.plot_rays)

        # - Edit's Disposition - #
        self.trace_num_edit.setAlignment(QtCore.Qt.AlignHCenter)

        # --- Buttons --- #
        next_trace_btn = QtWidgets.QPushButton('Next Tx')
        prev_trace_btn = QtWidgets.QPushButton('Prev Tx')

        # - Buttons' Actions - #
        next_trace_btn.clicked.connect(self.next_trace)
        prev_trace_btn.clicked.connect(self.prev_trace)

        # --- Labels --- #
        coverage_elev_label = MyQLabel('Tx elevation:', ha='right')
        self.value_elev_label = MyQLabel('', ha='left')
        trace_label = MyQLabel('Tx Number: ', ha='right')

        # --- CheckBox --- #
        self.entire_coverage_check = QtWidgets.QCheckBox('Show entire coverage')
        self.entire_coverage_check.stateChanged.connect(self.plot_rays)

        # --- Elevation SubWidget --- #
        sub_coverage_elev_widget = QtWidgets.QWidget()
        sub_coverage_elev_grid = QtWidgets.QGridLayout()
        sub_coverage_elev_grid.addWidget(coverage_elev_label, 0, 0)
        sub_coverage_elev_grid.addWidget(self.value_elev_label, 0, 1)
        sub_coverage_elev_widget.setLayout(sub_coverage_elev_grid)

        # --- Trace SubWidget --- #
        sub_trace_widget = QtWidgets.QWidget()
        sub_trace_grid = QtWidgets.QGridLayout()
        sub_trace_grid.addWidget(trace_label, 0, 0)
        sub_trace_grid.addWidget(self.trace_num_edit, 0, 1)
        sub_trace_grid.setContentsMargins(0, 0, 0, 0)
        sub_trace_widget.setLayout(sub_trace_grid)

        # --- Buttons SubWidget --- #
        sub_buttons_widget = QtWidgets.QWidget()
        sub_buttons_grid = QtWidgets.QGridLayout()
        sub_buttons_grid.addWidget(next_trace_btn, 0, 1)
        sub_buttons_grid.addWidget(prev_trace_btn, 0, 0)
        sub_buttons_grid.setContentsMargins(0, 0, 0, 0)
        sub_buttons_widget.setLayout(sub_buttons_grid)

        sub_coverage_widget = QtWidgets.QWidget()
        sub_coverage_grid = QtWidgets.QGridLayout()
        sub_coverage_grid.addWidget(sub_trace_widget, 0, 0)
        sub_coverage_grid.addWidget(sub_buttons_widget, 1, 0)
        sub_coverage_grid.addWidget(sub_coverage_elev_widget, 2, 0)
        sub_coverage_grid.addWidget(self.entire_coverage_check, 3, 0)
        sub_coverage_grid.setRowStretch(5, 100)
        sub_coverage_widget.setLayout(sub_coverage_grid)

        # ------- Frame to fill invFig's place before loading model ------- #
        self.inv_frame = QtWidgets.QFrame()
        self.inv_frame.setStyleSheet('background: white')

        # -------Manager for RaysFig ------ #
        self.raysFig = RaysFig(self)
        self.raystool = NavigationToolbar2QT(self.raysFig, self)
        self.rays_manager = QtWidgets.QWidget()
        rays_grid = QtWidgets.QGridLayout()
        rays_grid.addWidget(self.raystool, 0, 0, 1, 2)
        rays_grid.addWidget(self.raysFig, 1, 0)
        rays_grid.addWidget(sub_coverage_widget, 1, 1)
        self.rays_manager.setLayout(rays_grid)

        # -------Manager for RayDensityFig ------ #
        self.raydensityFig = RayDensityFig(self)
        self.raydensitytool = NavigationToolbar2QT(self.raydensityFig, self)
        self.ray_density_manager = QtWidgets.QWidget()
        ray_density_grid = QtWidgets.QGridLayout()
        ray_density_grid.addWidget(self.raydensitytool, 0, 0)
        ray_density_grid.addWidget(self.raydensityFig, 1, 0)
        self.ray_density_manager.setLayout(ray_density_grid)

        # -------Manager for ResidualsFig ------ #
        self.residualsFig = ResidualsFig(self)
        self.residualstool = NavigationToolbar2QT(self.residualsFig, self)
        self.residuals_manager = QtWidgets.QWidget()
        residuals_grid = QtWidgets.QGridLayout()
        residuals_grid.addWidget(self.residualstool, 0, 0)
        residuals_grid.addWidget(self.residualsFig, 1, 0)
        self.residuals_manager.setLayout(residuals_grid)

        # -------Manager for TomoFig ------ #
        self.tomoFig = TomoFig(self)
        self.tomotool = NavigationToolbar2QT(self.tomoFig, self)
        self.tomo_manager = QtWidgets.QWidget()
        tomo_grid = QtWidgets.QGridLayout()
        tomo_grid.addWidget(self.tomotool, 0, 0)
        tomo_grid.addWidget(self.tomoFig, 1, 0)
        self.tomo_manager.setLayout(tomo_grid)

        # -------Manager for TomoFig ------ #
        self.previnvFig = PrevInvFig(self)
        self.previnvtool = NavigationToolbar2QT(self.previnvFig, self)
        self.prev_inv_manager = QtWidgets.QWidget()
        prev_inv_grid = QtWidgets.QGridLayout()
        prev_inv_grid.addWidget(self.previnvtool, 0, 0)
        prev_inv_grid.addWidget(self.previnvFig, 1, 0)
        self.prev_inv_manager.setLayout(prev_inv_grid)

        # --- Color for the labels --- #
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)

        # ------- Widgets Creation ------- #
        # --- Buttons Set --- #
        btn_View        = QtWidgets.QPushButton("View")
        btn_Delete      = QtWidgets.QPushButton("Delete")
        btn_Load        = QtWidgets.QPushButton("Load")
        btn_GO          = QtWidgets.QPushButton("GO")

        # - Buttons Action - #
        btn_GO.clicked.connect(self.doInv)
        btn_View.clicked.connect(self.view_prev)
        btn_Delete.clicked.connect(self.delete_prev)
        btn_Load.clicked.connect(self.load_prev)

        # --- Label --- #
        model_label                 = MyQLabel("Model :", ha='center')
        cells_label                 = MyQLabel("Cells", ha='center')
        mog_label                   = MyQLabel("Select Mog", ha='center')
        Min_label                   = MyQLabel("Min", ha='right')
        Max_label                   = MyQLabel("Max", ha='right')
        Min_labeli                  = MyQLabel("Min :", ha='right')
        Max_labeli                  = MyQLabel("Max :", ha='right')
        X_label                     = MyQLabel("X", ha='center')
        Y_label                     = MyQLabel("Y", ha='center')
        Z_label                     = MyQLabel("Z", ha='center')
        algo_label                  = MyQLabel("Algorithm", ha='right')
        straight_ray_label          = MyQLabel("Straight Rays", ha='right')
        curv_ray_label              = MyQLabel("Curved Rays", ha='right')
        step_label                  = MyQLabel("Step :", ha='center')
        Xi_label                    = MyQLabel("X", ha='center')
        Yi_label                    = MyQLabel("Y", ha='center')
        Zi_label                    = MyQLabel("Z", ha='center')

        # These Labels are being set as attributes of the InversionUI class because they need to be modified
        # depending on the model's informations
        self.X_min_label            = MyQLabel("0", ha='center')
        self.Y_min_label            = MyQLabel("0", ha='center')
        self.Z_min_label            = MyQLabel("0", ha='center')
        self.X_max_label            = MyQLabel("0", ha='center')
        self.Y_max_label            = MyQLabel("0", ha='center')
        self.Z_max_label            = MyQLabel("0", ha='center')
        self.step_Xi_label          = MyQLabel("0", ha='center')
        self.step_Yi_label          = MyQLabel("0", ha='center')
        self.step_Zi_label          = MyQLabel("0", ha='center')
        self.num_cells_label        = MyQLabel("0", ha='center')
        self.algo_label             = MyQLabel('', ha='right')
        self.noIter_label           = MyQLabel('', ha='left')

        # --- Setting Label's color --- #
        self.num_cells_label.setPalette(palette)
        self.X_min_label.setPalette(palette)
        self.Y_min_label.setPalette(palette)
        self.Z_min_label.setPalette(palette)
        self.X_max_label.setPalette(palette)
        self.Y_max_label.setPalette(palette)
        self.Z_max_label.setPalette(palette)
        self.step_Xi_label.setPalette(palette)
        self.step_Yi_label.setPalette(palette)
        self.step_Zi_label.setPalette(palette)
        cells_label.setPalette(palette)
        model_label.setPalette(palette)
        self.algo_label.setPalette(palette)
        self.noIter_label.setPalette(palette)

        # --- Edits --- #
        self.straight_ray_edit       = QtWidgets.QLineEdit("1")  # Putting a string as the argument of the QLineEdit initializes
        self.curv_ray_edit           = QtWidgets.QLineEdit("1")  # it to the argument
        self.Min_editi               = QtWidgets.QLineEdit('0.06')
        self.Max_editi               = QtWidgets.QLineEdit('0.12')
        
        self.straight_ray_edit.editingFinished.connect(self.update_params)
        self.curv_ray_edit.editingFinished.connect(self.update_params)

        # - Edits' Disposition - #
        self.straight_ray_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.curv_ray_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.Min_editi.setAlignment(QtCore.Qt.AlignHCenter)
        self.Max_editi.setAlignment(QtCore.Qt.AlignHCenter)

        # - Edits' Actions - #
        self.Min_editi.editingFinished.connect(self.plot_inv)
        self.Max_editi.editingFinished.connect(self.plot_inv)

        # --- Checkboxes --- #
        self.use_const_checkbox = QtWidgets.QCheckBox("Use Constraints")  # The argument of the QCheckBox is the title
        self.use_Rays_checkbox  = QtWidgets.QCheckBox("Use Rays")         # of it
        self.set_color_checkbox = QtWidgets.QCheckBox("Set Color Limits")

        # - Checboxes Actions - #
        self.use_const_checkbox.stateChanged.connect(self.update_params)
        self.set_color_checkbox.stateChanged.connect(self.plot_inv)

        # --- Actions --- #
        openAction = QtWidgets.QAction('Open main data file', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openfile)

        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcut('Ctrl-S')
        saveAction.triggered.connect(self.savefile)

        exportAction = QtWidgets.QAction('Export', self)

        tomoAction = QtWidgets.QAction('Tomogram', self)
        tomoAction.triggered.connect(self.plot_tomo)

        simulAction = QtWidgets.QAction('Simulations', self)

        raysAction = QtWidgets.QAction('Rays', self)
        raysAction.triggered.connect(self.plot_rays)

        densityAction = QtWidgets.QAction('Ray Density', self)
        densityAction.triggered.connect(self.plot_ray_density)

        residAction = QtWidgets.QAction('Residuals', self)
        residAction.triggered.connect(self.plot_residuals)
        # --- ToolBar --- #
        self.tool = QtWidgets.QMenuBar()
        fileMenu = self.tool.addMenu('&File')
        resultsMenu = self.tool.addMenu('&Results')

        resultsMenu.addActions([exportAction, tomoAction, simulAction, raysAction, densityAction, residAction])

        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        # --- List --- #
        self.mog_list            = QtWidgets.QListWidget()

        # - List disposition - #
        self.mog_list.setFixedHeight(50)
        self.mog_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # - List Actions - #
        self.mog_list.itemSelectionChanged.connect(self.update_params)

        # --- combobox --- #
        self.T_and_A_combo            = QtWidgets.QComboBox()
        self.prev_inversion_combo     = QtWidgets.QComboBox()
        self.algo_combo               = QtWidgets.QComboBox()
        self.fig_combo                = QtWidgets.QComboBox()

        # ------- Items in the comboboxes -------- #
        # --- Time and Amplitude Combobox's Items --- #
        self.T_and_A_combo.addItem("Traveltime")
        self.T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        self.T_and_A_combo.addItem("Amplitude - Centroid Frequency")

        # --- Algorithm Combobox's Items --- #
        self.algo_combo.addItem("LSQR Solver")
        self.algo_combo.addItem("Geostatistic")

        # - ComboBoxes Action - #
        self.algo_combo.activated.connect(self.initinvUI)
        self.fig_combo.activated.connect(self.plot_inv)

        # --- Figure's ComboBox's Items --- #

        list1 = ['inferno', 'seismic', 'jet', 'hsv', 'hot',
                 'cool', 'autumn', 'winter', 'spring', 'summer',
                 'gray', 'bone', 'copper', 'pink', 'prism', 'flag']

        self.fig_combo.addItems(list1)

        # ------- Frame for number of Iterations ------- #
        iterFrame = QtWidgets.QFrame()
        iterGrid = QtWidgets.QGridLayout()
        iterGrid.addWidget(self.noIter_label, 0, 1)
        iterGrid.addWidget(self.algo_label, 0, 0)
        iterFrame.setLayout(iterGrid)
        iterFrame.setStyleSheet('background: white')

        # ------- SubWidgets ------- #
        # --- Algo SubWidget --- #
        Sub_algo_Widget = QtWidgets.QWidget()
        Sub_algo_Grid = QtWidgets.QGridLayout()
        Sub_algo_Grid.addWidget(algo_label, 0, 0)
        Sub_algo_Grid.addWidget(self.algo_combo, 0, 1)
        Sub_algo_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_algo_Widget.setLayout(Sub_algo_Grid)

        # ---  Grid Coordinates SubWidget --- #
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
        Sub_Grid_Coord_grid.setContentsMargins(0, 0, 0, 0)
        Sub_Grid_Coord_grid.setVerticalSpacing(3)
        Sub_Grid_Coord_Widget.setLayout(Sub_Grid_Coord_grid)

        # --- Cells SubWidget --- #
        sub_cells_widget = QtWidgets.QWidget()
        sub_cells_grid = QtWidgets.QGridLayout()
        sub_cells_grid.addWidget(self.num_cells_label, 0, 0)
        sub_cells_grid.addWidget(cells_label, 0, 1)
        sub_cells_widget.setLayout(sub_cells_grid)

        # --- Step SubWidget --- #
        Sub_Step_Widget = QtWidgets.QWidget()
        Sub_Step_Grid = QtWidgets.QGridLayout()
        Sub_Step_Grid.addWidget(step_label, 1, 0)
        Sub_Step_Grid.addWidget(self.step_Xi_label, 1, 1)
        Sub_Step_Grid.addWidget(self.step_Yi_label, 1, 2)
        Sub_Step_Grid.addWidget(self.step_Zi_label, 1, 3)
        Sub_Step_Grid.addWidget(Xi_label, 0, 1)
        Sub_Step_Grid.addWidget(Yi_label, 0, 2)
        Sub_Step_Grid.addWidget(Zi_label, 0, 3)
        Sub_Step_Grid.addWidget(sub_cells_widget, 2, 2)
        Sub_Step_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_Step_Grid.setVerticalSpacing(3)
        Sub_Step_Widget.setLayout(Sub_Step_Grid)

        # --- Straight Rays SubWidget --- #
        sub_straight_widget = QtWidgets.QWidget()
        sub_straight_grid = QtWidgets.QGridLayout()
        sub_straight_grid.addWidget(straight_ray_label, 0, 0)
        sub_straight_grid.addWidget(self.straight_ray_edit, 0, 1)
        sub_straight_grid.setContentsMargins(0, 0, 0, 0)
        sub_straight_widget.setLayout(sub_straight_grid)

        # --- Curved Rays SubWidget --- #
        sub_curved_widget = QtWidgets.QWidget()
        sub_curved_grid = QtWidgets.QGridLayout()
        sub_curved_grid.addWidget(curv_ray_label, 0, 0)
        sub_curved_grid.addWidget(self.curv_ray_edit, 0, 1)
        sub_curved_grid.setContentsMargins(0, 0, 0, 0)
        sub_curved_widget.setLayout(sub_curved_grid)

        # ------- SubGroupboxes ------- #
        # --- Data Groupbox --- #
        data_groupbox = QtWidgets.QGroupBox("Data")
        data_grid = QtWidgets.QGridLayout()
        data_grid.addWidget(model_label, 0, 0)
        data_grid.addWidget(self.T_and_A_combo, 1, 0)
        data_grid.addWidget(self.use_const_checkbox, 2, 0)
        data_grid.addWidget(mog_label, 0, 2)
        data_grid.addWidget(self.mog_list, 1, 2, 2, 1)
        data_groupbox.setLayout(data_grid)

        # --- Grid Groupbox --- #
        Grid_groupbox = QtWidgets.QGroupBox("Grid")
        Grid_grid = QtWidgets.QGridLayout()
        Grid_grid.addWidget(Sub_Grid_Coord_Widget, 0, 0)
        Grid_grid.addWidget(Sub_Step_Widget, 0, 1)
        Grid_groupbox.setLayout(Grid_grid)

        # --- Previous Inversion Groupbox --- #
        prev_inv_groupbox = QtWidgets.QGroupBox("Previous Inversions")
        prev_inv_grid = QtWidgets.QGridLayout()
        prev_inv_grid.addWidget(self.prev_inversion_combo, 0, 0, 1, 2)
        prev_inv_grid.addWidget(btn_View, 1, 0)
        prev_inv_grid.addWidget(btn_Delete, 1, 1)
        prev_inv_grid.addWidget(btn_Load, 1, 2)
        prev_inv_grid.addWidget(self.use_Rays_checkbox, 0, 2)
        prev_inv_groupbox.setLayout(prev_inv_grid)

        # --- Number of Iteration Groupbox --- #
        Iter_num_groupbox = QtWidgets.QGroupBox("Number of Iterations")
        Iter_num_grid = QtWidgets.QGridLayout()
        Iter_num_grid.addWidget(sub_straight_widget, 0, 0)
        Iter_num_grid.addWidget(sub_curved_widget, 0, 1)
        Iter_num_groupbox.setLayout(Iter_num_grid)

        # --- Inversion Parameters Groupbox --- #
        Inv_Param_groupbox = QtWidgets.QGroupBox(" Inversion Parameters")
        self.Inv_Param_grid = QtWidgets.QGridLayout()
        self.Inv_Param_grid.addWidget(Sub_algo_Widget, 0, 0)
        self.Inv_Param_grid.addWidget(Iter_num_groupbox, 1, 0, 1, 3)
        self.Inv_Param_grid.addWidget(QtWidgets.QLabel('Place Algo Group'), 2, 0, 1, 3)
        self.Inv_Param_grid.addWidget(btn_GO, 3, 1)
        Inv_Param_groupbox.setLayout(self.Inv_Param_grid)

        # --- Figures Groupbox --- #
        fig_groupbox = QtWidgets.QGroupBox("Figures")
        self.fig_grid = QtWidgets.QGridLayout()
        self.fig_grid.addWidget(self.set_color_checkbox, 0, 0)
        self.fig_grid.addWidget(Min_labeli, 0, 1)
        self.fig_grid.addWidget(self.Min_editi, 0, 2)
        self.fig_grid.addWidget(Max_labeli, 0, 3)
        self.fig_grid.addWidget(self.Max_editi, 0, 4)
        self.fig_grid.addWidget(self.fig_combo, 0, 5)
        fig_groupbox.setLayout(self.fig_grid)

        # --- Figure Groupbox dependent SubWidget --- #
        Sub_right_Widget = QtWidgets.QWidget()
        Sub_right_Grid = QtWidgets.QGridLayout()
        Sub_right_Grid.addWidget(fig_groupbox, 0, 0)
        Sub_right_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_right_Widget.setLayout(Sub_right_Grid)

        # ------- Global Widget Disposition ------- #
        global_widget = QtWidgets.QWidget()
        self.global_grid = QtWidgets.QGridLayout()
        self.global_grid.addWidget(data_groupbox, 0, 0, 3, 1)
        self.global_grid.addWidget(Grid_groupbox, 3, 0)
        self.global_grid.addWidget(prev_inv_groupbox, 5, 0)
        self.global_grid.addWidget(Inv_Param_groupbox, 6, 0)
        self.global_grid.addWidget(Sub_right_Widget, 0, 1)
        self.global_grid.addWidget(iterFrame, 0, 2)
        self.global_grid.addWidget(self.inv_frame, 1, 1, 7, 2)
        self.global_grid.setColumnStretch(2, 300)
        self.global_grid.setVerticalSpacing(1)
        self.global_grid.setRowStretch(7, 100)
        global_widget.setLayout(self.global_grid)

        # ------- Master Grid Disposition ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.tool, 0, 0)
        master_grid.addWidget(global_widget, 1, 0)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)


class InvFig(FigureCanvasQTAgg):
    def __init__(self, gv, ui):
        fig_width, fig_height = 4, 4
        fig = Figure(figsize=(fig_width, fig_height), facecolor='white')
        super(InvFig, self).__init__(fig)
        self.gv = gv
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax = self.figure.add_axes([0.05, 0.06, 0.25, 0.9])
        self.ax3 = self.figure.add_axes([0.375, 0.06, 0.25, 0.9])
        self.ax5 = self.figure.add_axes([0.7, 0.06, 0.25, 0.9])
        divider = make_axes_locatable(self.ax)
        divider.append_axes('right', size=0.5, pad=0.1)

        divider = make_axes_locatable(self.ax3)
        divider.append_axes('right', size=0.5, pad=0.1)

        divider = make_axes_locatable(self.ax5)
        divider.append_axes('right', size=0.5, pad=0.1)

        self.ax2 = self.figure.axes[3]
        self.ax4 = self.figure.axes[4]
        self.ax6 = self.figure.axes[5]
        self.ax.set_visible(False)
        self.ax2.set_visible(False)
        self.ax3.set_visible(False)
        self.ax4.set_visible(False)
        self.ax5.set_visible(False)
        self.ax6.set_visible(False)

    def plot_lsqr_inv(self, s):

        self.ax3.set_visible(True)
        self.ax4.set_visible(True)

        self.ax3.cla()
        self.ax4.cla()
        if self.ui.algo_combo.currentText() == 'LSQR Solver':
            self.ax3.set_title('LSQR')
        elif self.ui.algo_combo.currentText() == 'Geostatistic':
            self.ax3.set_title('Geostatistic')

        self.ax3.set_xlabel('Distance [m]')
        self.ax3.set_ylabel('Elevation [m]')
        self.ax4.set_title('m/ns')

        grid = self.gv.grid
        slowness = s.reshape((grid.grx.size - 1, grid.grz.size - 1)).T
        noIter = self.gv.noIter
        cmax = max(np.abs(1 / s))
        cmin = min(np.abs(1 / s))
        color_limits_state = self.ui.set_color_checkbox.isChecked()
        cmap = self.ui.fig_combo.currentText()

        if color_limits_state:
            cmax = float(self.ui.Max_editi.text())
            cmin = float(self.ui.Min_editi.text())

        h = self.ax3.imshow(np.abs(1 / slowness), interpolation='none', cmap=cmap, vmax=cmax, vmin=cmin,
                            extent=[grid.grx[0], grid.grx[-1], grid.grz[-1], grid.grz[0]])

        Colorbar(self.ax4, h)

        for tick in self.ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(8)

        tick_arrangement = set_tick_arrangement(grid)

        self.ax3.set_xticks(tick_arrangement)
        self.ax3.invert_yaxis()

        self.draw()


class RaysFig(FigureCanvasQTAgg):
    def __init__(self, ui):
        fig_width, fig_height = 4, 10
        fig = Figure(figsize=(fig_width, fig_height), dpi=80, facecolor='white')
        super(RaysFig, self).__init__(fig)
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax = self.figure.add_axes([0.25, 0.1, 0.5, 0.85])

    def plot_rays(self):
        self.ax.cla()
        grid = self.ui.models[self.ui.model_ind].grid
        res = self.ui.tomo.invData.res[:, -1]
        mog = self.ui.mogs[self.ui.mog_list.selectedIndexes()[0].row()]

        n = int(self.ui.trace_num_edit.text()) - 1

        Tx = np.unique(mog.data.Tx_z)
        print(Tx)

        ind1 = np.where(mog.tt != -1.0)[0]
        ind2 = np.where(mog.data.Tx_z[ind1] == Tx[n])[0]
        print(ind1)
        print(ind2)

        rmax = 1.001 * max(np.abs(res.flatten()))
        rmin = -rmax

        c = np.array([[0, 0, 1],
                      [1, 1, 1],
                      [1, 0, 0]])

        c = interpolate.interp1d(np.arange(-100, 101, 100).T, c.T)(np.arange(-100, 101, 2).T)
        m = 200 / (rmax - rmin)
        if not self.ui.entire_coverage_check.isChecked():
            for n in ind2:
                p = m * res[n]
                color = interpolate.interp1d(np.arange(-100, 101, 2), c)(p)
                self.ax.plot(self.ui.tomo.rays[n][:, 0], self.ui.tomo.rays[n][:, -1], c=color)

        elif self.ui.entire_coverage_check.isChecked():
            for n in range(len(self.ui.tomo.rays)):
                p = m * res[n]
                color = interpolate.interp1d(np.arange(-100, 101, 2), c)(p)
                self.ax.plot(self.ui.tomo.rays[n][:, 0], self.ui.tomo.rays[n][:, -1], c=color)

        for tick in self.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(8)

        tick_arrangement = set_tick_arrangement(grid)

        self.ax.set_ylim(grid.grz[0], grid.grz[-1])
        self.ax.set_xticks(tick_arrangement)
        self.ax.set_title('Rays')
        self.ax.set_xlabel('Distance [m]')
        self.ax.set_ylabel('Elevation [m]')
        self.ax.set_axis_bgcolor('grey')
        self.draw()


class RayDensityFig(FigureCanvasQTAgg):
    def __init__(self, ui):
        fig_width, fig_height = 6, 10
        fig = Figure(figsize=(fig_width, fig_height), dpi=80, facecolor='white')
        super(RayDensityFig, self).__init__(fig)
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax = self.figure.add_axes([0.05, 0.1, 0.9, 0.85])
        divider = make_axes_locatable(self.ax)
        divider.append_axes('right', size=0.5, pad=0.1)
        self.ax2 = self.figure.axes[1]

    def plot_ray_density(self):

        dim = self.ui.models[self.ui.model_ind].grid.getNcell()
        grid = self.ui.models[self.ui.model_ind].grid

        tmp = sum(self.ui.tomo.L)
        rd = tmp.toarray()
        rd = rd.reshape((grid.grx.size - 1, grid.grz.size - 1)).T

        h = self.ax.imshow(rd, interpolation='none', cmap='inferno',
                           extent=[grid.grx[0], grid.grx[-1], grid.grz[-1], grid.grz[0]])
        Colorbar(self.ax2, h)

        tick_arrangement = set_tick_arrangement(grid)

        self.ax.set_title('Ray Density')
        self.ax.set_xlabel('Distance [m]')
        self.ax.set_ylabel('Elevation [m]')
        self.ax.set_ylim(grid.grz[0], grid.grz[-1])
        self.ax.set_xticks(tick_arrangement)

        self.draw()


class ResidualsFig(FigureCanvasQTAgg):
    def __init__(self, ui):
        fig_width, fig_height = 10, 10
        fig = Figure(figsize=(fig_width, fig_height), dpi=80, facecolor='white')
        super(ResidualsFig, self).__init__(fig)
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax1 = self.figure.add_axes([0.05, 0.55, 0.4, 0.4])
        self.ax2 = self.figure.add_axes([0.55, 0.55, 0.4, 0.4])
        self.ax3 = self.figure.add_axes([0.05, 0.05, 0.4, 0.4])
        self.ax4 = self.figure.add_axes([0.55, 0.05, 0.4, 0.4])
        divider = make_axes_locatable(self.ax4)
        divider.append_axes('right', size=0.5, pad=0.1)
        self.ax5 = self.figure.axes[4]

        #                      Layout
        # ---------------------------------------
        # |       ax1       |        ax2        |
        # ---------------------------------------
        # |       ax3       |      ax4/ax5      |
        # ---------------------------------------

        self.ax1.set_ylabel('||res||')
        self.ax1.set_xlabel('Iteration')

        self.ax2.set_ylabel('Residuals')
        self.ax2.set_xlabel('Angle with horizontal[°]')

        self.ax3.set_ylabel('Count')
        self.ax3.set_xlabel('Residuals')
        self.ax3.set_title('$\sigma^2$ = ')

        self.ax4.set_ylabel('Tx Depth')
        self.ax4.set_xlabel('Rx Depth')
        self.ax4.set_facecolor('grey')

    def plot_residuals(self):
        model = self.ui.models[self.ui.model_ind]
        data, idata = Model.getModelData(model, self.ui.air, self.ui.lsqrParams.selectedMogs, 'tt')
        data = np.concatenate((model.grid.Tx[idata, :], model.grid.Rx[idata, :], data), axis=1)

        hyp = np.sqrt(np.sum((data[:, 0:3] - data[:, 3:6])**2, axis=1))
        dz = data[:, 2] - data[:, 5]
        theta = 180 / np.pi * np.arcsin(dz / hyp)

        nIt = self.ui.tomo.invData.res.shape[1]
        print(nIt)
        rms = np.zeros(nIt)

        for n in range(nIt):
            rms[n] = self.rmsv(self.ui.tomo.invData.res[n])

        res = self.ui.tomo.invData.res[:, nIt - 1]
        vres = np.var(res)

        depth, i = Model.getModelData(model, self.ui.air, self.ui.lsqrParams.selectedMogs, 'depth', type2='tt')
        dTx = np.sort(np.unique(depth[:, 0]))
        print(dTx)
        dRx = np.sort(np.unique(depth[:, 1]))
        print(dRx)
        imdata = np.empty((len(dTx), len(dRx), ))
        imdata[:] = np.NAN

        # progressBar = QtWidgets.QProgressBar()
        # progressBar.setGeometry(200, 80, 250, 20)
        # progressBar.show()
        for i in range(len(dTx)):
            for j in range(len(dRx)):
                ind = np.logical_and(dTx[i] == depth[:, 0], dRx[j] == depth[:, 1])
                if sum(ind.astype(int)) == 1:
                    imdata[i, j] = res[ind]

                # progressBar.setValue(i/len(dTx))

        z = np.zeros(imdata.shape)
        nan_ind = np.isnan(imdata)
        not_nan_ind = np.isfinite(imdata)
        z[nan_ind] = 0
        z[not_nan_ind] = 1

        self.ax1.plot(np.arange(nIt), rms[:nIt], marker='o', ls='none')
        self.ax1.set_xlim(-0.3, nIt - 0.7)
        self.ax1.set_ylim(min(rms) - 0.3, max(rms) + 0.3)
        self.ax1.set_xticks(np.arange(nIt))

        self.ax2.plot(theta, res, marker='o', ls='none')

        self.ax3.hist(res)
        self.ax3.set_title('$\sigma^2$ = {}'.format(vres))

        h = self.ax4.imshow(imdata, aspect='auto', interpolation='none', cmap='seismic')

        Colorbar(self.ax5, h)

        self.draw()

    def rmsv(self, x):
        x = x.flatten()
        r = np.sqrt(sum(x**2) / len(x))
        return r


class TomoFig(FigureCanvasQTAgg):
    def __init__(self, ui):
        fig_width, fig_height = 6, 10
        fig = Figure(figsize=(fig_width, fig_height), dpi=80, facecolor='white')
        super(TomoFig, self).__init__(fig)
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax = self.figure.add_axes([0.05, 0.07, 0.9, 0.9])
        divider = make_axes_locatable(self.ax)
        divider.append_axes('right', size=0.5, pad=0.1)
        self.ax2 = self.figure.axes[1]
        self.ax2.set_title('m/ns', fontsize=10)
        self.ax.set_xlabel('Distance [m]')
        self.ax.set_ylabel('Elevation [m]')

    def plot_tomo(self):
        # TODO: Changer le titre de la figure tout dépendant du type d'inversion
        grid = self.ui.models[self.ui.model_ind].grid
        s = self.ui.tomo.s

        cmax = max(1 / s)
        cmin = min(1 / s)

        s = s.reshape((grid.grx.size - 1, grid.grz.size - 1)).T

        h = self.ax.imshow(1 / s, interpolation='none', cmap='inferno', vmax=cmax, vmin=cmin,
                           extent=[grid.grx[0], grid.grx[-1], grid.grz[0], grid.grz[-1]])
        Colorbar(self.ax2, h)

        for tick in self.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(7)

        tick_arrangement = set_tick_arrangement(grid)

        self.ax.invert_yaxis()
        self.ax.set_xticks(tick_arrangement)

        self.draw()


class PrevInvFig(FigureCanvasQTAgg):
    def __init__(self, ui):
        fig_width, fig_height = 6, 10
        fig = Figure(figsize=(fig_width, fig_height), dpi=80, facecolor='white')
        super(PrevInvFig, self).__init__(fig)
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax = self.figure.add_axes([0.05, 0.1, 0.9, 0.85])
        divider = make_axes_locatable(self.ax)
        divider.append_axes('right', size=0.5, pad=0.1)
        self.ax2 = self.figure.axes[1]

        self.ax.set_xlabel('Distance [m]')
        self.ax.set_ylabel('Elevation [m]')

    def plot_tomo(self):
        grid = self.ui.models[self.ui.model_ind].grid
        n = self.ui.prev_inversion_combo.currentIndex()
        selected_inv_res = self.ui.models[self.ui.model_ind].inv_res[n]
        s = selected_inv_res[1].s

        cmax = max(1 / s)
        cmin = min(1 / s)

        s = s.reshape((grid.grx.size - 1, grid.grz.size - 1)).T

        self.ax.set_title(selected_inv_res[0])

        h = self.ax.imshow(1 / s, interpolation='none', cmap='inferno', vmax=cmax, vmin=cmin,
                           extent=[grid.grx[0], grid.grx[-1], grid.grz[0], grid.grz[-1]])
        Colorbar(self.ax2, h)

        for tick in self.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(7)

        self.ax2.set_ylabel('m/ns', fontsize=10)
        self.ax2.yaxis.set_label_position("right")

        tick_arrangement = set_tick_arrangement(grid)

        self.ax.set_xticks(tick_arrangement)
        self.ax.invert_yaxis()

        self.draw()


class SimulationsFig(FigureCanvasQTAgg):
    def __init__(self, ui):
        fig_width, fig_height = 6, 10
        fig = Figure(figsize=(fig_width, fig_height), dpi=80, facecolor='white')
        super(PrevInvFig, self).__init__(fig)
        self.ui = ui
        self.init_figure()

    def init_figure(self):
        self.ax = self.figure.add_axes([0.07, 0.07, 0.3, 0.9])
        self.ax2 = self.figure.add_axes([0.07, 0.07, 0.6, 0.9])
        divider = make_axes_locatable(self.ax)
        divider.append_axes('right', size=0.5, pad=0.1)
        divider = make_axes_locatable(self.ax2)
        divider.append_axes('right', size=0.5, pad=0.1)
        self.ax3 = self.figure.axes[2]
        self.ax4 = self.figure.axes[3]


class Gridviewer(QtWidgets.QWidget):
    def __init__(self, grid, ui):
        super(Gridviewer, self).__init__()
        self.grid = grid
        self.ui = ui
        if self.grid.type == '2D':
            self.init2DUI()
        if self.grid.type == '3D':
            self.init3DUI()
        self.noIter = 0

    def init2DUI(self):
        # -------- Manager for InvFig ------- #
        self.invFig = InvFig(self, self.ui)
        inv_grid = QtWidgets.QGridLayout()
        inv_grid.addWidget(self.invFig, 0, 0)
        inv_grid.setVerticalSpacing(0)
        self.setLayout(inv_grid)

    def init3DUI(self):
        # -------- Manager for InvFig ------- #
        self.invFig = InvFig(self, self.ui)
        inv_grid = QtWidgets.QGridLayout()
        inv_grid.addWidget(self.invFig, 0, 0)
        inv_grid.setVerticalSpacing(0)
        self.setLayout(inv_grid)

        y_plane_label = MyQLabel('Y Plane', ha='right')
        self.y_plane_scroll = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        self.ui.fig_grid.addWidget(y_plane_label, 0, 6)
        self.ui.fig_grid.addWidget(self.y_plane_scroll, 0, 7)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    inv_ui = InversionUI()
#    inv_ui.openmain.load_file('C:\\Users\\Utilisateur\\PycharmProjects\\BhTomoPy\\test_constraints.p')
#    inv_ui.openmain.load_file('test_constraints_backup.p')
#    inv_ui.openmain.ok()
    inv_ui.show()
    # residuals = ResidualsFig(inv_ui)
    # residuals.show()

    sys.exit(app.exec_())

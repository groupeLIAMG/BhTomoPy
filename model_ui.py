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

import copy
import sys
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import matplotlib as mpl
from model import Model
from mog import Mog
from grid import Grid, Grid2D
from events_ui import GridEdited
import database


class ModelUI(QtWidgets.QWidget):
    # ------- Signals Emitted ------- #
    modelInfoSignal = QtCore.pyqtSignal(int)
    modellogSignal  = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(ModelUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Models")
        self.update_mog_combo()
        self.initUI()

    def add_model(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Model creation", 'Model name')
        if ok:
            self.load_model(name)
            database.modified = True

    def load_model(self, name):
        model = Model(name)
        database.session.add(model)
        self.model_list.setCurrentRow(0)
        self.modellogSignal.emit("Model {} has been added successfully".format(name))
        self.update_model_list()
        database.modified = True

    def del_model(self):
        model = self.current_model()
        if model is not None:
            self.modellogSignal.emit("Model {} has been deleted successfully".format(model.name))
            database.delete(database, self.current_model())
        self.update_model_list()
        self.model_mog_list.clear()
        database.modified = True

    def current_model(self):

        model = self.model_list.currentItem()
        if model:
            return database.session.query(Model).filter(Model.name == model.text()).first()

    def current_mog(self):

        mog = self.model_mog_list.currentIndex().row()
        if mog != -1:
            return self.current_model().mogs[mog]

    def update_mog_combo(self):
        self.chooseMog = ChooseModelMOG(self)
        self.chooseMog.mog_combo.clear()
        for mog in database.session.query(Mog).all():
            self.chooseMog.mog_combo.addItem(mog.name)

    def add_mog(self):
        self.update_mog_combo()
        if database.session.query(Model).count() != 0:
            self.chooseMog.show()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning',
                                          "Please create a model before adding MOGs to it.",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def remove_mog(self):
        model = self.current_model()
        mog = self.current_mog()
        if model is not None and mog is not None:
            model.mogs.remove(mog)
            self.update_model_mog_list()
            database.modified = True

    def update_model_mog_list(self):
        self.model_mog_list.clear()
        n = self.model_list.currentIndex().row()
        if n != -1:
            for mog in self.current_model().mogs:
                self.model_mog_list.addItem(mog.name)

    def update_model_list(self):
        self.model_list.clear()
        for model in database.session.query(Model).all():
            self.model_list.addItem(model.name)
        self.modelInfoSignal.emit(len(self.model_list))  # sends the information to DatabaseUI
        self.model_list.setCurrentRow(0)

    def create_grid(self):
        model = self.current_model()
        if model is not None:
            if model.mogs:
                g, ok = self.gridEditor(model)
                if g is not None and ok == 1:
                    model.grid = g
                    database.modified = True
            else:
                QtWidgets.QMessageBox.warning(self, 'Warning', "This model has no mogs.")

    def edit_grid(self):
        model = self.current_model()
        if model is not None and model.mogs:
            g, ok = self.gridEditor(model, model.grid)
            if g is not None and ok == 1:
                model.grid = g
                database.modified = True

    def gridEditor(self, model, grid=None):

        g = None
        if grid is not None:
            g = grid
            previousGrid = copy.deepcopy(grid)
        else:
            previousGrid = None

        nBH = len(model.boreholes)

        if nBH == 0 or nBH == 1:
            QtWidgets.QMessageBox.warning(self, 'Warning', "This model's mogs have misdefined boreholes.")
            return

        data = self.prepare_grid_data()
        if g is None:
            if nBH == 2:
                gtype = '2D'
                g, data = Grid2DUI.build_grid(data)

            else:
                # TODO: find out if 2D+ or 3D
                gtype = 'TODO'
                pass

        else:
            gtype = g.type
            if gtype == '2D':
                gtmp, data = Grid2DUI.build_grid(data)
            elif gtype == '2D+':
                # TODO
                pass

        d = QtWidgets.QDialog()
        d.setWindowTitle('BhTomoPy/gridEditor')

        def cancel():
            nonlocal d
            nonlocal g
            nonlocal previousGrid
            if previousGrid is not None:
                g = copy.deepcopy(previousGrid)
            d.done(0)

        def done():
            nonlocal d
            d.done(1)

        def start_constraints():
            pass

        def plot_boreholes():
            view = bhfig_combo.currentText()
            bhsFig.plot_boreholes(model.mogs, view)

        def update_grid_info(mogs, grid):
            ndata = 0
            n_tt_data_picked = 0
            n_amp_data_picked = 0

            for mog in mogs:
                ndata += mog.data.ntrace
                n_tt_data_picked += len(np.where(mog.tt != -1)[0])
                n_amp_data_picked += (len(np.where(mog.amp_tmin != -1)[0]) + len(np.where(mog.amp_tmax != -1)[0])) / 2

            gridinfo.num_data_label.setText(str(ndata))
            gridinfo.num_tt_picked_label.setText(str(n_tt_data_picked))
            gridinfo.num_amp_picked_label.setText(str(n_amp_data_picked))
            gridinfo.num_cell_label.setText(str(grid.getNumberOfCells()))  # TODO: update field when grid is edited

        # -------- Widgets Creation -------- #
        # --- Buttons --- #
        add_edit_btn            = QtWidgets.QPushButton('Add/Edit Constraints')
        cancel_btn              = QtWidgets.QPushButton('Cancel')
        done_btn                = QtWidgets.QPushButton('Done')

        # - Buttons' Actions -#
        add_edit_btn.clicked.connect(start_constraints)
        cancel_btn.clicked.connect(cancel)
        done_btn.clicked.connect(done)

        # --- ComboBox --- #
        bhfig_combo        = QtWidgets.QComboBox()

        # - Combobox items -#
        view_list = ['3D View', 'XY Plane', 'XZ Plane', 'YZ Plane']
        for item in view_list:
            bhfig_combo.addItem(item)

        # - Comboboxes Action -#
        bhfig_combo.activated.connect(plot_boreholes)

        # - Grid Info GroupBox -#
        gridinfo = GridInfoUI()
        grid_info_group         = QtWidgets.QGroupBox('Infos')
        grid_info_grid          = QtWidgets.QGridLayout()
        grid_info_grid.addWidget(gridinfo)
        grid_info_group.setLayout(grid_info_grid)

        # - Boreholes Figure GroupBox -#
        bhsFig = BoreholesFig()
        bhs_group = QtWidgets.QGroupBox('Boreholes')
        bhs_grid = QtWidgets.QGridLayout()
        bhs_grid.addWidget(bhfig_combo, 0, 0)
        bhs_grid.addWidget(bhsFig, 1, 0, 1, 8)
        bhs_group.setLayout(bhs_grid)

        # --- Grid UI --- #

        if gtype == '2D':
            gUI = Grid2DUI(data, g, gridinfo)  # gridinfo used as parent to propagate GridEdited events
        elif gtype == '2D+':
            # TODO:
            pass
        else:
            # TODO: 3D
            pass

        # ------- Master grid's disposition ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(grid_info_group, 0, 0)
        master_grid.addWidget(add_edit_btn, 1, 0)
        master_grid.addWidget(cancel_btn, 2, 0)
        master_grid.addWidget(done_btn, 3, 0)
        master_grid.addWidget(gUI.grid_param_group, 0, 1, 4, 1)
        master_grid.addWidget(bhs_group, 4, 0, 1, 2)
        master_grid.addWidget(gUI.grid_view_group, 0, 2, 5, 1)
        master_grid.setColumnStretch(2, 100)
        master_grid.setRowStretch(4, 100)
        d.setLayout(master_grid)

        plot_boreholes()
        update_grid_info(model.mogs, g)

        d.setWindowModality(QtCore.Qt.ApplicationModal)
        isOk = d.exec_()

        return g, isOk

    def prepare_grid_data(self):
        no = self.model_list.currentRow()
        if no not in range(database.session.query(Model).count()):
            return None

        mogs = self.current_model().mogs
        mog = mogs[0]

        data = GridData()

        data.in_vect = mog.in_vect.T
        data.Tx = np.array([mog.data.Tx_x, mog.data.Tx_y, mog.data.Tx_z]).T
        data.Rx = np.array([mog.data.Rx_x, mog.data.Rx_y, mog.data.Rx_z]).T
        data.TxCosDir = mog.TxCosDir
        data.RxCosDir = mog.RxCosDir

        data.boreholes = self.current_model().boreholes

        if len(mogs) > 1:
            for n in range(1, len(mogs)):

                mog = mogs[n]
                tmp_Txyz = np.array([mog.data.Tx_x, mog.data.Tx_y, mog.data.Tx_z]).T
                tmp_Rxyz = np.array([mog.data.Rx_x, mog.data.Rx_y, mog.data.Rx_z]).T

                data.in_vect = np.concatenate((data.in_vect, mog.in_vect.T), axis=0)
                data.Tx = np.concatenate((data.Tx, tmp_Txyz), axis=0)
                data.Rx = np.concatenate((data.Rx, tmp_Rxyz), axis=0)
                data.TxCosDir = np.concatenate((data.TxCosDir, mog.TxCosDir), axis=0)
                data.RxCosDir = np.concatenate((data.RxCosDir, mog.RxCosDir), axis=0)

            # TODO: Complete

        return data

    def initUI(self):

        # ------- Widgets Creation ------- #

        # --- Buttons Set --- #
        btn_Add_Model                    = QtWidgets.QPushButton("Add Model")
        btn_Remove_Model                 = QtWidgets.QPushButton("Remove Model")
        btn_Create_Grid                  = QtWidgets.QPushButton("Create Grid")
        btn_Edit_Grid                    = QtWidgets.QPushButton("Edit Grid")
        btn_Add_MOG                      = QtWidgets.QPushButton("Add MOG")
        btn_Remove_MOG                   = QtWidgets.QPushButton("Remove MOG")
        # --- Buttons Actions --- #
        btn_Add_Model   .clicked.connect(self.add_model)
        btn_Remove_Model.clicked.connect(self.del_model)
        btn_Remove_MOG  .clicked.connect(self.remove_mog)
        btn_Add_MOG     .clicked.connect(self.add_mog)
        btn_Create_Grid .clicked.connect(self.create_grid)
        btn_Edit_Grid   .clicked.connect(self.edit_grid)

        # --- Lists --- #
        self.model_mog_list              = QtWidgets.QListWidget()
        self.model_list                  = QtWidgets.QListWidget()
        # --- Lists Actions --- #
        self.model_list.currentItemChanged.connect(self.update_model_mog_list)

        # --- Sub Widgets --- #
        # --- Models Sub Widget --- #
        Models_Sub_Widget                = QtWidgets.QWidget()
        Models_Sub_Grid                  = QtWidgets.QGridLayout()
        Models_Sub_Grid.addWidget(btn_Add_Model, 0, 0, 1, 2)
        Models_Sub_Grid.addWidget(btn_Remove_Model, 0, 2, 1, 2)
        Models_Sub_Grid.addWidget(self.model_list, 1, 0, 1, 4)
        Models_Sub_Widget.setLayout(Models_Sub_Grid)

        # --- Grid Sub Widget --- #
        Grid_GroupBox                    = QtWidgets.QGroupBox("Grid")
        Grid_Sub_Grid                    = QtWidgets.QGridLayout()
        Grid_Sub_Grid.addWidget(btn_Create_Grid, 0, 0)
        Grid_Sub_Grid.addWidget(btn_Edit_Grid, 0, 1)
        Grid_GroupBox.setLayout(Grid_Sub_Grid)

        # --- MOGS Sub Widget --- #
        MOGS_Groupbox                    = QtWidgets.QGroupBox("MOGs")
        MOGS_Sub_Grid                    = QtWidgets.QGridLayout()
        MOGS_Sub_Grid.addWidget(btn_Add_MOG, 0, 0, 1, 2)
        MOGS_Sub_Grid.addWidget(btn_Remove_MOG, 0, 2, 1, 2)
        MOGS_Sub_Grid.addWidget(self.model_mog_list, 1, 0, 1, 4)
        MOGS_Groupbox.setLayout(MOGS_Sub_Grid)

        # ------- Grid Disposition ------- #
        master_grid                      = QtWidgets.QGridLayout()
        # --- Sub Widgets Disposition --- #
        master_grid.addWidget(Models_Sub_Widget, 0, 0)
        master_grid.addWidget(Grid_GroupBox, 1, 0)
        master_grid.addWidget(MOGS_Groupbox, 0, 1, 2, 1)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)


class ChooseModelMOG(QtWidgets.QWidget):

    def __init__(self, model, parent=None):
        super(ChooseModelMOG, self).__init__()
        self.setWindowTitle("BhTomoPy/Choose MOGs")
        self.model = model
        self.initUI()

    def add_mog(self):
        model = self.model.model_list.currentItem().text()
        mog = self.mog_combo.currentText()
        self.load_mog(mog, model)

    def load_mog(self, mog, model):
        self.model.model_mog_list.addItem(mog)
        mog = database.session.query(Mog).filter(Mog.name == mog).first()
        model = database.session.query(Model).filter(Model.name == model).first()
        model.mogs.append(mog)
        database.modified = True
        self.model.modellogSignal.emit("{} has been added to {}'s MOGs".format(mog.name, model.name))

    def initUI(self):
        # ------- Widgets ------- #
        # --- ComboBox --- #
        self.mog_combo = QtWidgets.QComboBox()
        # --- Buttons --- #
        add_btn = QtWidgets.QPushButton('Add')
        cancel_btn = QtWidgets.QPushButton('Cancel')
        done_btn = QtWidgets.QPushButton('Done')

        # - Buttons Actions - #
        add_btn.clicked.connect(self.add_mog)
        done_btn.clicked.connect(self.close)

        # --- Buttons SubWidget --- #
        sub_btn_widget = QtWidgets.QWidget()
        sub_btn_grid = QtWidgets.QGridLayout()
        sub_btn_grid.addWidget(add_btn, 0, 0)
        sub_btn_grid.addWidget(cancel_btn, 0, 1)
        sub_btn_grid.addWidget(done_btn, 1, 0, 1, 2)
        sub_btn_grid.setContentsMargins(0, 0, 0, 0)
        sub_btn_widget.setLayout(sub_btn_grid)

        # --- Master Grid --- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.mog_combo, 0, 0)
        master_grid.addWidget(sub_btn_widget, 1, 0)
        self.setLayout(master_grid)


class Grid2DUI(QtWidgets.QWidget):
    def __init__(self, data, grid, parent=None):
        super(Grid2DUI, self).__init__(parent)
        self.data = data
        self.grid = grid
        if np.all(self.grid.grx == 0) and np.all(self.grid.grz == 0):
            self.dx = 1
            self.dz = 1
        else:
            self.dx = self.grid.grx[1] - self.grid.grx[0]
            self.dz = self.grid.grz[1] - self.grid.grz[0]

        self.initUI()
        self.update_bh_origin()
        self.updateProj()

    def get_azimuth_dip(self):
        d = sum(self.data.x0 * self.data.a)
        x = d / self.data.a[0]
        y = d / self.data.a[1]
        az = np.arctan2(y, x)
        dip = np.arcsin(self.data.a[2])
        flip = self.flip_check.isChecked()
        az = az + flip * np.pi
        return az, dip

    def project(self, xyz):
        xyz_p = Grid.proj_plane(xyz, self.data.x0, self.data.a)
        dist = np.sqrt(np.sum((xyz - xyz_p)**2, axis=1))
        az, dip = self.get_azimuth_dip()
        xyz_p = Grid.transl_rotat(xyz_p, self.grid.x0, az, dip)
        return xyz_p, dist

    def update_bh_origin(self):
        self.borehole_combo.clear()
        for borehole in self.data.boreholes:
            self.borehole_combo.addItem(borehole.name)

            self.update_input()

    def update_input(self):
        ind = self.borehole_combo.currentIndex()

        self.dx = float(self.cell_size_x_edit.text())
        self.dz = float(self.cell_size_z_edit.text())

        self.grid.border[0] = float(self.pad_minus_x_edit.text())
        self.grid.border[1] = float(self.pad_plus_x_edit.text())
        self.grid.border[2] = float(self.pad_minus_z_edit.text())
        self.grid.border[3] = float(self.pad_plus_z_edit.text())

        self.grid.flip = self.flip_check.isChecked()

        self.grid.borehole_x0 = ind

        self.grid.x0[0] = self.data.boreholes[ind].X
        self.grid.x0[1] = self.data.boreholes[ind].Y
        self.grid.x0[2] = self.data.boreholes[ind].Z

        self.origin_x_edit.setText(str(self.grid.x0[0]))
        self.origin_y_edit.setText(str(self.grid.x0[1]))
        self.origin_z_edit.setText(str(self.grid.x0[2]))

        self.updateProj()

        self.gridviewFig.plot_grid2D()
        evt = GridEdited()
        evt.data = self.grid
        QtWidgets.QApplication.postEvent(self.parent(), evt)

    def updateProj(self):
        az, dip = self.get_azimuth_dip()
        self.grid.Tx = Grid.transl_rotat(self.data.Tx_p, self.grid.x0, az, dip)
        self.grid.Rx = Grid.transl_rotat(self.data.Rx_p, self.grid.x0, az, dip)
        self.grid.TxCosDir = Grid.transl_rotat(self.data.TxCosDir, np.zeros(3), az, dip)
        self.grid.RxCosDir = Grid.transl_rotat(self.data.RxCosDir, np.zeros(3), az, dip)

#         if not np.isnan(self.data.Tx_Z_water):
#             self.grid.Tx_Z_water = Grid.transl_rotat(self.data.Tx_Z_water, self.grid.x0, az, dip)
#         if not np.isnan(self.data.Rx_Z_water):
#             self.grid.Rx_Z_water = Grid.transl_rotat(self.data.Rx_Z_water, self.grid.x0, az, dip)
        self.grid.in_vect = self.data.in_vect

        xmin = np.min(np.concatenate((self.grid.Tx[self.grid.in_vect, 0], self.grid.Rx[self.grid.in_vect, 0]))) - 0.5 * self.dx
        xmax = np.max(np.concatenate((self.grid.Tx[self.grid.in_vect, 0], self.grid.Rx[self.grid.in_vect, 0]))) + 0.5 * self.dx
        nx = np.ceil((xmax - xmin) / self.dx)

        zmin = np.min(np.concatenate((self.grid.Tx[self.grid.in_vect, 2], self.grid.Rx[self.grid.in_vect, 2]))) - 0.5 * self.dz
        zmax = np.max(np.concatenate((self.grid.Tx[self.grid.in_vect, 2], self.grid.Rx[self.grid.in_vect, 2]))) + 0.5 * self.dz
        nz = np.ceil((zmax - zmin) / self.dz)

        nxm = self.grid.border[0]
        nxp = self.grid.border[1]
        self.grid.grx = xmin + self.dx * np.arange(-nxm, nx + nxp + 1)
        nzm = self.grid.border[2]
        nzp = self.grid.border[3]
        self.grid.grz = zmin + self.dz * np.arange(-nzm, nz + nzp + 1)

    def plot_adjustment(self):
        self.bestfitplaneFig.plot_stats()
        self.bestfitplanemanager.showMaximized()

    @staticmethod
    def build_grid(data):

        grid = Grid2D()
        grid.x0 = [data.boreholes[0].X, data.boreholes[0].Y, data.boreholes[0].Z]
        grid.type = '2D'

        uTx = data.Tx[data.in_vect, :]
        uRx = data.Rx[data.in_vect, :]

        b = np.ascontiguousarray(uTx).view(np.dtype((np.void, uTx.dtype.itemsize * uTx.shape[1])))
        c = np.ascontiguousarray(uRx).view(np.dtype((np.void, uRx.dtype.itemsize * uRx.shape[1])))

        tmpTx = np.unique(b).view(uTx.dtype).reshape(-1, uTx.shape[1])
        tmpRx = np.unique(c).view(uRx.dtype).reshape(-1, uRx.shape[1])

        uTx = np.sort(tmpTx, axis=0)
        uRx = np.sort(tmpRx, axis=0)

        data.x0, data.a = Grid.lsplane(np.concatenate((uTx, uRx), axis=0), nout=2)
        # data.x0 : Centroid of the data = point on the best-fit plane
        # data.a  : Direction cosines of the normal to the best-fit plane
        if data.a[2] < 0:
            data.a = -data.a

        data.Tx_p = Grid.proj_plane(data.Tx, data.x0, data.a)
        data.Rx_p = Grid.proj_plane(data.Rx, data.x0, data.a)

        return grid, data

    def initUI(self):

        # ------- Manager for the Best fit plane Figure ------- #
        self.bestfitplaneFig = BestFitPlaneFig(self.data)
        self.bestfitplanemanager = QtWidgets.QWidget()
        self.bestfitplanetool = NavigationToolbar2QT(self.bestfitplaneFig, self)
        bestfitplanemanagergrid = QtWidgets.QGridLayout()
        bestfitplanemanagergrid.addWidget(self.bestfitplanetool, 0, 0)
        bestfitplanemanagergrid.addWidget(self.bestfitplaneFig, 1, 0)
        self.bestfitplanemanager.setLayout(bestfitplanemanagergrid)

        adjustment_btn          = QtWidgets.QPushButton('Adjustment of Best-Fit Plane')
        # - Buttons' Actions - #
        adjustment_btn.clicked.connect(self.plot_adjustment)

        # --- Edits --- #
        self.pad_minus_x_edit   = QtWidgets.QLineEdit(str(self.grid.border[0]))
        self.pad_plus_x_edit    = QtWidgets.QLineEdit(str(self.grid.border[1]))
        self.pad_minus_z_edit   = QtWidgets.QLineEdit(str(self.grid.border[2]))
        self.pad_plus_z_edit    = QtWidgets.QLineEdit(str(self.grid.border[3]))

        self.cell_size_x_edit   = QtWidgets.QLineEdit(str(self.dx))
        self.cell_size_z_edit   = QtWidgets.QLineEdit(str(self.dz))

        self.origin_x_edit      = QtWidgets.QLineEdit()
        self.origin_y_edit      = QtWidgets.QLineEdit()
        self.origin_z_edit      = QtWidgets.QLineEdit()

        # - Edits' Actions - #
        self.pad_plus_x_edit.editingFinished.connect(self.update_input)
        self.pad_plus_z_edit.editingFinished.connect(self.update_input)
        self.pad_minus_x_edit.editingFinished.connect(self.update_input)
        self.pad_minus_z_edit.editingFinished.connect(self.update_input)

        self.cell_size_x_edit.editingFinished.connect(self.update_input)
        self.cell_size_z_edit.editingFinished.connect(self.update_input)

        # - Edits' Diposition - #
        self.origin_x_edit.setReadOnly(True)
        self.origin_y_edit.setReadOnly(True)
        self.origin_z_edit.setReadOnly(True)

        # --- Labels --- #
        x_label                 = MyQLabel('X', ha='right')
        z_label                 = MyQLabel('Z', ha='right')
        pad_plus_label          = MyQLabel('Padding +', ha='center')
        pad_minus_label         = MyQLabel('Padding -', ha='center')
        cell_size_label         = MyQLabel('Cell Size', ha='center')
        borehole_origin_label   = MyQLabel('Borehole origin', ha='right')
        origin_label            = MyQLabel('Origin', ha='right')

        # --- CheckBox --- #
        self.flip_check              = QtWidgets.QCheckBox('Flip horizontally')
        self.flip_check.setChecked(self.grid.flip)

        # - CheckBox Actions - #
        self.flip_check.stateChanged.connect(self.update_input)

        # --- ComboBoxes --- #
        self.borehole_combo     = QtWidgets.QComboBox()
        self.borehole_combo.setCurrentIndex(self.grid.borehole_x0)

        # - ComboBoxes Actions - #
        self.borehole_combo.activated.connect(self.update_input)

        # --- SubWidgets --- #
        sub_param_widget        = QtWidgets.QWidget()
        sub_param_grid          = QtWidgets.QGridLayout()
        sub_param_grid.addWidget(x_label, 1, 0)
        sub_param_grid.addWidget(z_label, 2, 0)
        sub_param_grid.addWidget(pad_minus_label, 0, 1)
        sub_param_grid.addWidget(pad_plus_label, 0, 2)
        sub_param_grid.addWidget(cell_size_label, 0, 3)
        sub_param_grid.addWidget(self.pad_minus_x_edit, 1, 1)
        sub_param_grid.addWidget(self.pad_minus_z_edit, 2, 1)
        sub_param_grid.addWidget(self.pad_plus_x_edit, 1, 2)
        sub_param_grid.addWidget(self.pad_plus_z_edit, 2, 2)
        sub_param_grid.addWidget(self.cell_size_x_edit, 1, 3)
        sub_param_grid.addWidget(self.cell_size_z_edit, 2, 3)
        sub_param_grid.addWidget(borehole_origin_label, 3, 0)
        sub_param_grid.addWidget(self.borehole_combo, 3, 1)
        sub_param_grid.addWidget(origin_label, 4, 0)
        sub_param_grid.addWidget(self.origin_x_edit, 4, 1)
        sub_param_grid.addWidget(self.origin_y_edit, 4, 2)
        sub_param_grid.addWidget(self.origin_z_edit, 4, 3)
        sub_param_grid.setContentsMargins(0, 0, 0, 0)
        sub_param_widget.setLayout(sub_param_grid)

        # --- GroupBox --- #
        # - Grid parameters GroupBox - #
        self.grid_param_group        = QtWidgets.QGroupBox('Grid Parameters')
        grid_param_grid         = QtWidgets.QGridLayout()
        grid_param_grid.addWidget(sub_param_widget, 0, 0, 1, 3)
        grid_param_grid.addWidget(self.flip_check, 1, 1)
        grid_param_grid.addWidget(adjustment_btn, 2, 1)
        # grid_param_grid.setVerticalSpacing(3)
        self.grid_param_group.setLayout(grid_param_grid)

        # - GridView Figure GroupBox  -#
        self.gridviewFig = GridViewFig(self)
        self.grid_view_group = QtWidgets.QGroupBox('Grid View')
        grid_view_grid = QtWidgets.QGridLayout()
        grid_view_grid.addWidget(self.gridviewFig, 0, 0)
        self.grid_view_group.setLayout(grid_view_grid)


class GridInfoUI(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super(GridInfoUI, self).__init__()
        self.initUI()

    def customEvent(self, event, *args, **kwargs):
        if event.type() == GridEdited._type:
            self.num_cell_label.setText(str(event.data.getNumberOfCells()))

    def initUI(self):

        # -------- Widgets -------- #
        # --- Labels --- #
        cell_label = MyQLabel('Number of cells', ha='center')
        data_label = MyQLabel('Number of data', ha='center')
        tt_picked_label = MyQLabel('Traveltimes picked', ha='left')
        amp_picked_label = MyQLabel('Amplitudes picked', ha='left')

        self.num_cell_label = MyQLabel('0', ha='center')
        self.num_data_label = MyQLabel('0', ha='center')
        self.num_tt_picked_label = MyQLabel('0', ha='right')
        self.num_amp_picked_label = MyQLabel('0', ha='right')

        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(cell_label, 0, 0, 1, 2)
        master_grid.addWidget(self.num_cell_label, 1, 0, 1, 2)
        master_grid.addWidget(data_label, 2, 0, 1, 2)
        master_grid.addWidget(self.num_data_label, 3, 0, 1, 2)
        master_grid.addWidget(self.num_tt_picked_label, 4, 0)
        master_grid.addWidget(tt_picked_label, 4, 1)
        master_grid.addWidget(self.num_amp_picked_label, 5, 0)
        master_grid.addWidget(amp_picked_label, 5, 1)
        self.setLayout(master_grid)
        self.setStyleSheet('background: white')


class BestFitPlaneFig(FigureCanvasQTAgg):
    def __init__(self, data, parent=None):

        fig = mpl.figure.Figure(figsize=(100, 100), facecolor='white')
        super(BestFitPlaneFig, self).__init__(fig)
        self.data = data
        self.initFig()

    def initFig(self):

        # horizontal configruation
        self.ax1 = self.figure.add_axes([0.1, 0.1, 0.2, 0.25])
        self.ax2 = self.figure.add_axes([0.4, 0.1, 0.2, 0.25])

        self.ax4 = self.figure.add_axes([0.1, 0.55, 0.2, 0.25])
        self.ax5 = self.figure.add_axes([0.4, 0.55, 0.2, 0.25])
        self.ax6 = self.figure.add_axes([0.7, 0.55, 0.2, 0.25])

        self.ax4.set_title('Distance between original and projected Tx', y=1.08)
        self.ax5.set_title('Distance between originial and projected Rx', y=1.08)
        self.ax6.set_title('Relative error on ray length after projection [%]', y=1.08)
        self.ax1.set_title('Tx direction cosines after rotation', y=1.08)
        self.ax2.set_title('Rx direction cosines after rotation', y=1.08)

    def plot_stats(self):

        dTx = np.sqrt(np.sum((self.data.Tx - self.data.Tx_p)**2, axis=1))
        dRx = np.sqrt(np.sum((self.data.Rx - self.data.Rx_p)**2, axis=1))
        l_origin = np.sqrt(np.sum((self.data.Tx - self.data.Rx)**2, axis=1))
        l_new = np.sqrt(np.sum((self.data.Tx_p - self.data.Rx_p)**2, axis=1))
        error = 100 * np.abs(l_origin - l_new) / l_origin

        self.ax4.plot(dTx,
                      marker='o',
                      fillstyle='none',
                      color='blue',
                      markersize=5,
                      mew=1,
                      ls='None')

        self.ax5.plot(dRx,
                      marker='o',
                      fillstyle='none',
                      color='blue',
                      markersize=5,
                      mew=1,
                      ls='None')

        self.ax6.plot(error,
                      marker='o',
                      fillstyle='none',
                      color='blue',
                      markersize=5,
                      mew=1,
                      ls='None')


class BoreholesFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(BoreholesFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_boreholes(self, mogs, view):
        self.ax.cla()

        for n in range(len(mogs)):
            mog = mogs[n]
            false_Rx_ind = np.nonzero(not mog.in_Rx_vect.all())  # Verify boolean value
            false_Tx_ind = np.nonzero(not mog.in_Tx_vect.all())  # Verify boolean value

            Tx_zs = np.unique(mog.data.Tx_z)
            Rx_zs = np.unique(mog.data.Rx_z)

            Tx_zs = np.delete(Tx_zs, false_Tx_ind[0])
            Rx_zs = np.delete(Rx_zs, false_Rx_ind[0])

            num_Tx = len(Tx_zs)
            num_Rx = len(Rx_zs)
            Tx_xs = mog.data.Tx_x[:num_Tx]
            Rx_xs = mog.data.Rx_x[:num_Rx]
            Tx_ys = mog.data.Tx_y[:num_Tx]
            Rx_ys = mog.data.Rx_y[:num_Rx]
            self.ax.text(x=Tx_xs[0], y=Tx_ys[0], z=mog.Tx.fdata[0, 2], s=str(mog.Tx.name))
            self.ax.scatter(Tx_xs, Tx_ys, Tx_zs, c='g', marker='o', label="{}'s Tx".format(mog.name), lw=0)
            self.ax.text(x=Rx_xs[0], y=Rx_ys[0], z=mog.Rx.fdata[0, 2], s=str(mog.Rx.name))
            self.ax.scatter(Rx_xs, Rx_ys, Rx_zs, c='b', marker='*', label="{}'s Rx".format(mog.name), lw=0)

            l = self.ax.legend(ncol=1, bbox_to_anchor=(0, 1), loc='upper left', borderpad=0)
            l.draw_frame(False)

            self.ax.plot(mog.Tx.fdata[:, 0], mog.Tx.fdata[:, 1], mog.Tx.fdata[:, 2], color='r')
            self.ax.plot(mog.Rx.fdata[:, 0], mog.Rx.fdata[:, 1], mog.Rx.fdata[:, 2], color='r')

        if view == '3D View':
            self.ax.view_init()
        elif view == 'XY Plane':
            self.ax.view_init(elev=90, azim=90)
        elif view == 'XZ Plane':
            self.ax.view_init(elev=0, azim=90)
        elif view == 'YZ Plane':
            self.ax.view_init(elev=0, azim=0)
        self.draw()


class GridViewFig(FigureCanvasQTAgg):
    def __init__(self, gUI, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(GridViewFig, self).__init__(fig)
        self.gUI = gUI
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.1, 0.1, 0.85, 0.85])
        self.ax.grid(True)

    def plot_grid2D(self):
        self.ax.cla()

        z1 = self.gUI.grid.grz[0] * np.ones(len(self.gUI.grid.grx) + 1).T[:, None]
        z2 = self.gUI.grid.grz[-1] * np.ones(len(self.gUI.grid.grx) + 1).T[:, None]

        x1 = self.gUI.grid.grx[0] * np.ones(len(self.gUI.grid.grz) + 1).T[:, None]
        x2 = self.gUI.grid.grx[-1] * np.ones(len(self.gUI.grid.grz) + 1).T[:, None]

        zz1 = np.concatenate((z1, z2), axis=1)
        xx1 = np.concatenate((x1, x2), axis=1)

        zz2 = np.concatenate((self.gUI.grid.grz.T[:, None], self.gUI.grid.grz.T[:, None]), axis=1)
        xx2 = np.concatenate((self.gUI.grid.grx.T[:, None], self.gUI.grid.grx.T[:, None]), axis=1)

        for i in range(len(self.gUI.grid.grx)):
            self.ax.plot(xx2[i, :], zz1[i, :], color='grey')

        for j in range(len(self.gUI.grid.grz)):
            self.ax.plot(xx1[j, :], zz2[j, :], color='grey')

        self.ax.plot(self.gUI.grid.Tx[self.gUI.grid.in_vect, 0], self.gUI.grid.Tx[self.gUI.grid.in_vect, 2], marker='o', color='green', ls='none')
        self.ax.plot(self.gUI.grid.Rx[self.gUI.grid.in_vect, 0], self.gUI.grid.Rx[self.gUI.grid.in_vect, 2], marker='*', color='blue', ls='none')

        self.ax.set_xlim(min(self.gUI.grid.grx), max(self.gUI.grid.grx))
        self.ax.set_ylim(min(self.gUI.grid.grz), max(self.gUI.grid.grz))

        self.ax.set_aspect('equal', adjustable='box')

        for tick in self.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(10)

        self.draw()

    def plot_grid(self, mogs, origin, flip, pad_x_plus, pad_x_minus, pad_z_plus, pad_z_minus, x_cell_size, z_cell_size):
        self.ax.cla()

        for mog in mogs:
            Tx_zs = np.unique(mog.data.Tx_z)
            Tx_ys = mog.data.Tx_y[:len(Tx_zs)]
            Rx_zs = np.unique(mog.data.Rx_z)
            Rx_ys = mog.data.Rx_y[:len(Rx_zs)]
            orig_Tx = np.zeros(len(Tx_zs))
            orig_Rx = np.zeros(len(Rx_zs))

            if origin == mog.Tx.name:
                self.ax.plot(orig_Tx, -Tx_zs, 'o', c='g')

                if flip:
                    self.ax.plot(np.abs(Tx_ys[0] - Rx_ys[0]) * np.ones(len(Rx_zs)), -Rx_zs, '*', c='b')
                    self.ax.set_xlim([-pad_x_minus, np.abs(Tx_ys[0] - Rx_ys[0]) + pad_x_plus])
                    self.ax.set_xticks(np.arange(-pad_x_minus, np.abs((Tx_ys[0] - Rx_ys[0])) + pad_x_plus, x_cell_size), minor=True)

                else:
                    self.ax.plot(-np.abs((Tx_ys[0] - Rx_ys[0])) * np.ones(len(Rx_zs)), -Rx_zs, '*', c='b')
                    self.ax.set_xlim([-pad_x_minus - np.abs((Tx_ys[0] - Rx_ys[0])), pad_x_plus])
                    self.ax.set_xticks(np.arange(-pad_x_minus - (Tx_ys[0] - Rx_ys[0]), pad_x_plus, x_cell_size), minor=True)

            if origin == mog.Rx.name:
                self.ax.plot(orig_Rx, -Rx_zs, '*', c='b')

                if flip:
                    self.ax.plot(np.abs((Rx_ys[0] - Tx_ys[0])) * np.ones(len(Tx_zs)), -Tx_zs, 'o', c='g')
                    self.ax.set_xlim([-pad_x_minus, np.abs((Rx_ys[0] - Tx_ys[0])) + pad_x_plus])
                    self.ax.set_xticks(np.arange(-pad_x_minus, np.abs((Rx_ys[0] - Tx_ys[0])) + pad_x_plus, x_cell_size), minor=True)

                else:
                    self.ax.plot(-np.abs((Rx_ys[0] - Tx_ys[0])) * np.ones(len(Tx_zs)), -Tx_zs, 'o', c='g')
                    self.ax.set_xlim([-np.abs((Rx_ys[0] - Tx_ys[0])) - pad_x_minus, pad_x_plus])
                    self.ax.set_xticks(np.arange(-np.abs((Rx_ys[0] - Tx_ys[0])) - pad_x_minus, pad_x_plus, x_cell_size), minor=True)

            if max(mog.data.Rx_z) > max(mog.data.Tx_z):
                self.ax.set_ylim([-max(mog.data.Rx_z) - pad_z_minus, pad_z_plus])
                self.ax.set_yticks(np.arange(-max(mog.data.Rx_z) - pad_z_minus, pad_z_plus, z_cell_size), minor=True)
            if max(mog.data.Tx_z) > max(mog.data.Rx_z):
                self.ax.set_ylim([-max(mog.data.Tx_z) - pad_z_minus, pad_z_plus])
                self.ax.set_yticks(np.arange(-max(mog.data.Tx_z) - pad_z_minus, pad_z_plus, z_cell_size), minor=True)

            for tic in self.ax.xaxis.get_major_ticks():
                tic.tick1On = tic.tick2On = False
                # tic.label1On = tic.label2On = False

            for tic in self.ax.yaxis.get_major_ticks():
                tic.tick1On = tic.tick2On = False
                # tic.label1On = tic.label2On = False

            self.ax.set_xlabel('Y', fontsize=16)
            self.ax.set_ylabel('Z', fontsize=16)
            self.ax.grid(which='both', ls='solid')

        self.draw()


class ConstraintsEditorUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ConstraintsEditorUI, self).__init__()
        self.constraintsFig = ConstraintsFig(self)
        self.initUI()

    def initUI(self):
        # -------- Widgets ------- #
        # --- Buttons --- #
        edit_btn                 = QtWidgets.QPushButton('Edit')
        import_btn               = QtWidgets.QPushButton('Import')
        reinit_btn               = QtWidgets.QPushButton('Reinitialize')
        display_btn              = QtWidgets.QPushButton('Display')
        cancel_btn               = QtWidgets.QPushButton('Cancel')
        done_btn                 = QtWidgets.QPushButton('Done')

        # --- Labels --- #
        cmax_label               = MyQLabel('Cmax', ha='center')
        cmin_label               = MyQLabel('Cmin', ha='center')
        property_value_label     = MyQLabel('Value: ', ha='right')
        variance_value_label     = MyQLabel('Value: ', ha='right')

        # --- Edits --- #
        self.cmax_edit           = QtWidgets.QLineEdit('1')
        self.cmin_edit           = QtWidgets.QLineEdit('0')
        self.property_value_edit = QtWidgets.QLineEdit('0')
        self.variance_value_edit = QtWidgets.QLineEdit('0')

        # - Edits Disposition - #
        self.cmax_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.cmin_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.property_value_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.variance_value_edit.setAlignment(QtCore.Qt.AlignHCenter)

        # --- ComboBox --- #
        self.property_combo = QtWidgets.QComboBox()

        # - Combobox Items - #
        properties_list = ['Velocity', 'Attenuation', 'Reservoir', 'Xi', 'Tilt Angle']
        self.property_combo.addItems(properties_list)

        # --- SubWidgets --- #
        # - Property Value SubWidget - #
        sub_property_value_widget = QtWidgets.QWidget()
        sub_property_value_grid = QtWidgets.QGridLayout()
        sub_property_value_grid.addWidget(property_value_label, 0, 0)
        sub_property_value_grid.addWidget(self.property_value_edit, 0, 1)
        sub_property_value_grid.setContentsMargins(0, 0, 0, 0)
        sub_property_value_grid.setHorizontalSpacing(0)
        sub_property_value_widget.setLayout(sub_property_value_grid)

        # - Variance Value SubWidget - #
        sub_variance_value_widget = QtWidgets.QWidget()
        sub_variance_value_grid = QtWidgets.QGridLayout()
        sub_variance_value_grid.addWidget(variance_value_label, 0, 0)
        sub_variance_value_grid.addWidget(self.variance_value_edit, 0, 1)
        sub_variance_value_grid.setContentsMargins(0, 0, 0, 0)
        sub_variance_value_grid.setHorizontalSpacing(0)
        sub_variance_value_widget.setLayout(sub_variance_value_grid)

        # ------- GroupBoxes ------- #
        # --- Constraints GroupBox --- #
        constraints_group = QtWidgets.QGroupBox('Constraints')
        constraints_grid = QtWidgets.QGridLayout()
        constraints_grid.addWidget(self.constraintsFig, 0, 0, 8, 1)
        constraints_grid.addWidget(cmax_label, 0, 1)
        constraints_grid.addWidget(self.cmax_edit, 1, 1)
        constraints_grid.addWidget(cmin_label, 6, 1)
        constraints_grid.addWidget(self.cmin_edit, 7, 1)
        constraints_grid.setColumnStretch(0, 100)
        constraints_grid.setRowStretch(2, 100)
        constraints_group.setLayout(constraints_grid)
        # --- Variance GroupBox --- #
        variance_group = QtWidgets.QGroupBox('Variance')
        variance_grid = QtWidgets.QGridLayout()
        variance_grid.addWidget(sub_variance_value_widget, 0, 0)
        variance_grid.addWidget(display_btn, 1, 0)
        variance_group.setLayout(variance_grid)
        # --- Property GroupBox --- #
        property_group = QtWidgets.QGroupBox('Property')
        property_grid = QtWidgets.QGridLayout()
        property_grid.addWidget(self.property_combo, 0, 0)
        property_grid.addWidget(sub_property_value_widget, 1, 0)
        property_grid.addWidget(edit_btn, 2, 0)
        property_grid.addWidget(import_btn, 3, 0)
        property_grid.addWidget(reinit_btn, 4, 0)
        property_grid.addWidget(variance_group, 5, 0)
        property_group.setLayout(property_grid)

        # ------- Master grid's Layout ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(constraints_group, 0, 0, 6, 1)
        master_grid.addWidget(property_group, 0, 1)
        master_grid.addWidget(cancel_btn, 4, 1)
        master_grid.addWidget(done_btn, 5, 1)
        master_grid.setColumnStretch(0, 100)
        self.setLayout(master_grid)


class ConstraintsFig(FigureCanvasQTAgg):
    def __init__(self, ConstraintsEditor, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(ConstraintsFig, self).__init__(fig)
        self.constraints_editor = ConstraintsEditor
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.08, 0.9, 0.9])
        divider = make_axes_locatable(self.ax)
        divider.append_axes('right', size=0.5, pad=0.1)

    def plot_constraints(self, mog):
        self.ax2 = self.figure.axes[1]
        self.ax.cla()
        self.ax2.cla()
        cmin = self.constraints_editor.cmin_edit.text()
        cmax = self.constraints_editor.cmax_edit.text()

        # h= self.ax.imshow(data, aspect='auto')
        # mpl.colorbar.Colorbar(self.ax2, h)


class GridData(object):
    def __init__(self):
        self.boreholes  = []
        self.in_vect    = np.array([])
        self.Tx         = np.array([])
        self.Rx         = np.array([])
        self.TxCosDir   = np.array([])
        self.RxCosDir   = np.array([])
        self.Tx_Z_water = np.array([])
        self.Rx_Z_water = np.array([])
        self.Tx         = np.array([])
        self.Rx         = np.array([])
        self.Tx_p       = np.array([])
        self.Rx_p       = np.array([])
        self.a          = 0
        self.x0         = 0


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

    Model_ui = ModelUI()
    Model_ui.show()

    sys.exit(app.exec_())

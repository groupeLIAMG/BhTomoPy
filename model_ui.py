import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import matplotlib as mpl
from model import Model
from grid import *


class ModelUI(QtGui.QWidget):
    #------- Signals Emitted -------#
    modelInfoSignal = QtCore.pyqtSignal(int)
    modellogSignal = QtCore.pyqtSignal(str)

    def __init__(self, borehole, mog, parent=None):
        super(ModelUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Models")
        self.borehole = borehole
        self.mog = mog
        self.models = []
        self.update_mog_combo()
        self.initUI()

    def add_model(self):
        name, ok = QtGui.QInputDialog.getText(self, "Model creation", 'Model name')
        if ok :
            self.load_model(name)

    def load_model(self, name):
        self.models.append(Model(name))
        self.model_list.setCurrentRow(0)
        self.modellogSignal.emit("Model {} as been added succesfully".format(name))
        self.update_model_list()

    def del_model(self):
        ind = self.model_list.selectedIndexes()
        for i in ind:
            self.modellogSignal.emit("Model {} as been deleted succesfully".format(self.models[int(i.row())].name))
            del self.models[int(i.row())]
        self.update_model_list()
        self.model_mog_list.clear()

    def update_mog_combo(self):
        self.chooseMog = ChooseModelMOG(self)
        self.chooseMog.mog_combo.clear()
        for mog in self.mog.MOGs:
            self.chooseMog.mog_combo.addItem(mog.name)

    def add_mog(self):
        self.update_mog_combo()
        if len(self.models) != 0:
            self.chooseMog.show()
        else:
            dialog = QtGui.QMessageBox.warning(self, 'Warning', "Please create a model before adding MOGs to it"
                                                    ,buttons=QtGui.QMessageBox.Ok)


    def remove_mog(self):
        n = self.model_list.selectedIndexes()[0].row()
        ind = self.model_mog_list.currentIndex().row()

        del self.models[n].mogs[ind]
        self.update_model_mog_list()
        self.update_models_boreholes()

    def update_model_mog_list(self):
        self.model_mog_list.clear()
        n = self.model_list.currentIndex().row()
        for mog in self.models[n].mogs:
            self.model_mog_list.addItem(mog.name)

    def update_model_list(self):
        self.model_list.clear()
        for model in self.models:
            self.model_list.addItem(model.name)
        self.modelInfoSignal.emit(len(self.model_list)) # we send the information to DatabaseUI
        self.model_list.setCurrentRow(0)

    def update_models_boreholes(self):
        n = self.model_list.currentRow()
        self.models[n].boreholes.clear()

        for mog in self.models[n].mogs:
            if mog.Tx not in self.models[n].boreholes:
                self.models[n].boreholes.append(mog.Tx)
            if mog.Rx not in self.models[n].boreholes:
                self.models[n].boreholes.append(mog.Rx)

    def update_grid_info(self):
        ndata = 0
        n_tt_data_picked = 0
        n_amp_data_picked = 0
        ind = self.model_list.currentIndex().row()

        for mog in self.models[ind].mogs:

            ndata += mog.data.ntrace

            n_tt_data_picked += len(np.where(mog.tt != -1)[0])
            n_amp_data_picked += (len(np.where(mog.amp_tmin != -1)[0]) + len(np.where(mog.amp_tmax != -1)[0]))/2

        self.gridui.gridinfo.num_data_label.setText(str(ndata))
        self.gridui.gridinfo.num_tt_picked_label.setText(str(n_tt_data_picked))
        self.gridui.gridinfo.num_amp_picked_label.setText(str(n_amp_data_picked))
        self.gridui.gridinfo.num_cell_label.setText(str(self.gridui.grid.getNumberOfCells()))

    def start_grid(self):
        self.gridui = gridEditor(self)
        self.gridui.plot_boreholes()
        self.update_grid_info()
        self.gridui.showMaximized()

    def initUI(self):

        #------- Widgets Creation -------#

        #--- Buttons Set ---#
        btn_Add_Model                    = QtGui.QPushButton("Add Model")
        btn_Remove_Model                 = QtGui.QPushButton("Remove Model")
        btn_Create_Grid                  = QtGui.QPushButton("Create Grid")
        btn_Edit_Grid                    = QtGui.QPushButton("Edit Grid")
        btn_Add_MOG                      = QtGui.QPushButton("Add MOG")
        btn_Remove_MOG                   = QtGui.QPushButton("Remove MOG")
        #--- Buttons Actions ---#
        btn_Add_Model.clicked.connect(self.add_model)
        btn_Remove_Model.clicked.connect(self.del_model)
        btn_Remove_MOG.clicked.connect(self.remove_mog)
        btn_Add_MOG.clicked.connect(self.add_mog)
        btn_Create_Grid.clicked.connect(self.start_grid)
        btn_Edit_Grid.clicked.connect(self.start_grid)

        #--- Lists ---#
        self.model_mog_list              = QtGui.QListWidget()
        self.model_list                  = QtGui.QListWidget()

        #--- Sub Widgets ---#
        #--- Models Sub Widget ---#
        Models_Sub_Widget                = QtGui.QWidget()
        Models_Sub_Grid                  = QtGui.QGridLayout()
        Models_Sub_Grid.addWidget(btn_Add_Model, 0, 0, 1, 2)
        Models_Sub_Grid.addWidget(btn_Remove_Model, 0, 2, 1, 2)
        Models_Sub_Grid.addWidget(self.model_list, 1, 0, 1, 4)
        Models_Sub_Widget.setLayout(Models_Sub_Grid)

        #--- Grid Sub Widget ---#
        Grid_GroupBox                    = QtGui.QGroupBox("Grid")
        Grid_Sub_Grid                    = QtGui.QGridLayout()
        Grid_Sub_Grid.addWidget(btn_Create_Grid, 0, 0)
        Grid_Sub_Grid.addWidget(btn_Edit_Grid, 0, 1)
        Grid_GroupBox.setLayout(Grid_Sub_Grid)

        #--- MOGS Sub Widget ---#
        MOGS_Groupbox                    = QtGui.QGroupBox("MOGs")
        MOGS_Sub_Grid                    = QtGui.QGridLayout()
        MOGS_Sub_Grid.addWidget(btn_Add_MOG, 0, 0, 1, 2)
        MOGS_Sub_Grid.addWidget(btn_Remove_MOG, 0, 2, 1, 2)
        MOGS_Sub_Grid.addWidget(self.model_mog_list, 1, 0, 1, 4)
        MOGS_Groupbox.setLayout(MOGS_Sub_Grid)



        #------- Grid Disposition -------#
        master_grid                      = QtGui.QGridLayout()
        #--- Sub Widgets Disposition ---#
        master_grid.addWidget(Models_Sub_Widget, 0, 0)
        master_grid.addWidget(Grid_GroupBox, 1, 0)
        master_grid.addWidget(MOGS_Groupbox, 0, 1, 2, 1)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)


class ChooseModelMOG(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(ChooseModelMOG, self).__init__()
        self.setWindowTitle("BhTomoPy/Choose MOGs")
        self.model = model
        self.initUI()

    def add_mog(self):
        n = self.model.model_list.currentIndex().row()
        ind = self.mog_combo.currentIndex()
        self.load_mog(ind, n)

    def load_mog(self, ind, n):
        self.model.model_mog_list.addItem(self.model.mog.MOGs[ind].name)
        self.model.models[n].mogs.append(self.model.mog.MOGs[ind])
        self.model.update_models_boreholes()
        self.model.modellogSignal.emit("{} as been added to {}'s MOGs".format(self.model.mog.MOGs[ind].name, self.model.models[n].name))


    def initUI(self):
        #------- Widgets -------#
        #--- ComboBox ---#
        self.mog_combo = QtGui.QComboBox()
        #--- Buttons ---#
        add_btn = QtGui.QPushButton('Add')
        cancel_btn = QtGui.QPushButton('Cancel')
        done_btn = QtGui.QPushButton('Done')

        #- Buttons Actions -#
        add_btn.clicked.connect(self.add_mog)
        done_btn.clicked.connect(self.close)

        #--- Buttons SubWidget ---#
        sub_btn_widget = QtGui.QWidget()
        sub_btn_grid = QtGui.QGridLayout()
        sub_btn_grid.addWidget(add_btn, 0, 0)
        sub_btn_grid.addWidget(cancel_btn, 0, 1)
        sub_btn_grid.addWidget(done_btn, 1, 0, 1, 2)
        sub_btn_grid.setContentsMargins(0, 0, 0, 0)
        sub_btn_widget.setLayout(sub_btn_grid)

        #--- Master Grid ---#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(self.mog_combo, 0, 0)
        master_grid.addWidget(sub_btn_widget, 1, 0)
        self.setLayout(master_grid)

class gridEditor(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(gridEditor, self).__init__()
        self.setWindowTitle("BhTomoPy/gridEditor")
        self.gridinfo = GridInfoUI()
        self.constraintseditor = ConstraintsEditorUI()
        self.model = model
        self.type = ''
        self.data = Data()
        self.grid = Grid()
        self.model_ind = self.model.model_list.currentIndex().row()
        self.initUI()

    def update_model_grid(self):
        self.model.models[self.model_ind].grid = self.gUI.grid


    def plot_boreholes(self):

        view = self.bhfig_combo.currentText()
        self.bhsFig.plot_boreholes(self.model.models[self.model_ind].mogs, view)

    def prepare_grid_data(self):

        mogs = self.model.models[self.model_ind].mogs
        mog = mogs[0]

        self.data.in_vect = mog.in_vect.T
        self.data.Tx = np.array([mog.data.Tx_x, mog.data.Tx_y, mog.data.Tx_z]).T
        self.data.Rx = np.array([mog.data.Rx_x, mog.data.Rx_y, mog.data.Rx_z]).T
        self.data.TxCosDir = mog.TxCosDir.T
        self.data.RxCosDir = mog.RxCosDir.T


        self.data.boreholes = self.model.models[self.model_ind].boreholes


        if len(mogs) > 1:
            for n in range(1, len(mogs)):

                mog = mogs[n]
                tmp_Txyz = np.array([mog.data.Tx_x, mog.data.Tx_y, mog.data.Tx_z]).T
                tmp_Rxyz = np.array([mog.data.Rx_x, mog.data.Rx_y, mog.data.Rx_z]).T

                Tx = mog.Tx
                Rx = mog.Rx

                self.data.in_vect = np.concatenate((self.data.in_vect, mog.in_vect.T), axis= 0)


                self.data.Tx = np.concatenate((self.data.Tx, tmp_Txyz), axis= 0)


                self.data.Rx = np.concatenate((self.data.Rx, tmp_Rxyz), axis= 0)

                self.data.TxCosDir = np.concatenate((self.data.TxCosDir, mog.TxCosDir.T), axis= 0)

                self.data.RxCosDir = np.concatenate((self.data.RxCosDir, mog.RxCosDir.T), axis= 0)

            if Tx.Z_water != None:
                #TODO
                pass

    def start_constraints(self):
        self.constraintseditor.constraintsFig.plot_constraints(self.model.models[self.model_ind].mogs[0])

    def initUI(self):
        nBH = len(self.model.models[self.model_ind].boreholes)
        self.prepare_grid_data()
        if np.all(self.grid.grx == 0) and np.all(self.grid.grz == 0):
            if nBH == 2:
                self.type = '2D'
                self.grid, self.data = Grid2DUI.build_grid(self.data)
                self.gUI = Grid2DUI(self.data, self.grid)
                self.gUI.update_bh_origin()

            #-------- Widgets Creation --------#
            #--- Buttons ---#
            add_edit_btn            = QtGui.QPushButton('Add/Edit Constraints')
            cancel_btn              = QtGui.QPushButton('Cancel')
            done_btn                = QtGui.QPushButton('Done')

            #- Buttons' Actions -#
            add_edit_btn.clicked.connect(self.start_constraints)

            #--- ComboBox ---#
            self.bhfig_combo        = QtGui.QComboBox()

            #- Combobox items -#
            view_list = ['3D View', 'XY Plane', 'XZ Plane', 'YZ Plane']
            for item in view_list:
                self.bhfig_combo.addItem(item)

            #- Comboboxes Action -#
            self.bhfig_combo.activated.connect(self.plot_boreholes)

            #- Grid Info GroupBox -#
            grid_info_group         = QtGui.QGroupBox('Infos')
            grid_info_grid          = QtGui.QGridLayout()
            grid_info_grid.addWidget(self.gridinfo)
            grid_info_group.setLayout(grid_info_grid)

            #- Boreholes Figure GroupBox -#
            self.bhsFig = BoreholesFig()
            bhs_group = QtGui.QGroupBox('Boreholes')
            bhs_grid = QtGui.QGridLayout()
            bhs_grid.addWidget(self.bhfig_combo, 0, 0)
            bhs_grid.addWidget(self.bhsFig, 1, 0, 1, 8)
            bhs_group.setLayout(bhs_grid)

            #------- Master grid's disposition -------#
            master_grid = QtGui.QGridLayout()
            master_grid.addWidget(grid_info_group, 0, 0)
            master_grid.addWidget(add_edit_btn, 1, 0)
            master_grid.addWidget(cancel_btn, 2, 0)
            master_grid.addWidget(done_btn, 3, 0)
            master_grid.addWidget(self.gUI.grid_param_group, 0, 1, 4, 1)
            master_grid.addWidget(bhs_group, 4, 0, 1, 2)
            master_grid.addWidget(self.gUI.grid_view_group, 0, 2, 5, 1)
            master_grid.setColumnStretch(2, 100)
            master_grid.setRowStretch(4, 100)
            self.setLayout(master_grid)

class Grid2DUI(QtGui.QWidget):
    def __init__(self, data, grid, parent=None):
        super(Grid2DUI, self).__init__()
        self.data = data
        self.grid = grid
        if np.all(self.grid.grx == 0) and np.all(self.grid.grz == 0):
            self.dx = 1
            self.dz = 1
        else:
            self.dx = self.grid.grx[1] - self.grx[0]
            self.dz = self.grid.grz[1] - self.grz[0]

        self.initUI()


    def get_azimuth_dip(self):
        d = sum(self.data.x0*self.data.a)
        x = d/self.data.a[0]
        y = d/self.data.a[1]
        az = np.arctan2(y, x)
        dip = np.arcsin(self.data.a[2])
        flip = self.flip_check.isChecked()
        az = az + flip*np.pi
        return az, dip

    def project(self, xyz):
        xyz_p = Grid.proj_plane(xyz, self.data.x0, self.data.a);
        dist = np.sqrt(nop.sum((xyz-xyz_p)**2, axis= 1));
        az, dip = self.get_azimuth_dip();
        xyz_p = Grid.transl_rotat(xyz_p, self.grid.x0, az, dip);
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

        self.gridviewFig.plot_grid2D()

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

        uTx = np.sort(tmpTx, axis= 0)
        uRx = np.sort(tmpRx, axis= 0)

        data.x0, data.a = Grid.lsplane(np.concatenate((uTx, uRx), axis= 0))
        # self.data.x0 : Centroid of the data = point on the best-fit plane
        # self.data.a  : Direction cosines of the normal to the best-fit plane
        if data.a[2] < 0 :
            data.a = -data.a

        data.Tx_p = Grid.proj_plane(data.Tx, data.x0, data.a)
        data.Rx_p = Grid.proj_plane(data.Rx, data.x0, data.a)

        return grid, data



    def initUI(self):

        #------- Manager for the Best fit plane Figure -------#
        self.bestfitplaneFig = BestFitPlaneFig(self.data)
        self.bestfitplanemanager = QtGui.QWidget()
        self.bestfitplanetool = NavigationToolbar2QT(self.bestfitplaneFig, self)
        bestfitplanemanagergrid = QtGui.QGridLayout()
        bestfitplanemanagergrid.addWidget(self.bestfitplanetool, 0, 0)
        bestfitplanemanagergrid.addWidget(self.bestfitplaneFig, 1, 0)
        self.bestfitplanemanager.setLayout(bestfitplanemanagergrid)

        adjustment_btn          = QtGui.QPushButton('Adjustment of Best-Fit Plane')
        #- Buttons' Actions -#
        adjustment_btn.clicked.connect(self.plot_adjustment)

        #--- Edits ---#
        self.pad_plus_x_edit    = QtGui.QLineEdit('1')
        self.pad_plus_z_edit    = QtGui.QLineEdit('1')
        self.pad_minus_x_edit   = QtGui.QLineEdit('1')
        self.pad_minus_z_edit   = QtGui.QLineEdit('1')

        self.cell_size_x_edit   = QtGui.QLineEdit('0.2')
        self.cell_size_z_edit   = QtGui.QLineEdit('0.2')

        self.origin_x_edit      = QtGui.QLineEdit()
        self.origin_y_edit      = QtGui.QLineEdit()
        self.origin_z_edit      = QtGui.QLineEdit()

        #- Edits' Actions -#
        self.pad_plus_x_edit.editingFinished.connect(self.update_input)
        self.pad_plus_z_edit.editingFinished.connect(self.update_input)
        self.pad_minus_x_edit.editingFinished.connect(self.update_input)
        self.pad_minus_z_edit.editingFinished.connect(self.update_input)

        self.cell_size_x_edit.editingFinished.connect(self.update_input)
        self.cell_size_z_edit.editingFinished.connect(self.update_input)

        #- Edits' Diposition -#
        self.origin_x_edit.setReadOnly(True)
        self.origin_y_edit.setReadOnly(True)
        self.origin_z_edit.setReadOnly(True)

        #--- Labels ---#
        x_label                 = MyQLabel('X', ha= 'right')
        z_label                 = MyQLabel('Z', ha= 'right')
        pad_plus_label          = MyQLabel('Padding +', ha= 'center')
        pad_minus_label         = MyQLabel('Padding -', ha= 'center')
        cell_size_label         = MyQLabel('Cell Size', ha= 'center')
        borehole_origin_label   = MyQLabel('Borehole origin', ha= 'right')
        origin_label            = MyQLabel('Origin', ha= 'right')

        #--- CheckBox ---#
        self.flip_check              = QtGui.QCheckBox('Flip horizontally')

        #- CheckBox Actions -#
        self.flip_check.stateChanged.connect(self.update_input)

        #--- ComboBoxes ---#
        self.borehole_combo     = QtGui.QComboBox()

        #- ComboBoxes Actions -#
        self.borehole_combo.activated.connect(self.update_input)

        #--- SubWidgets ---#
        sub_param_widget        = QtGui.QWidget()
        sub_param_grid          = QtGui.QGridLayout()
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

        #--- GroupBox ---#
        #- Grid parameters GroupBox -#
        self.grid_param_group        = QtGui.QGroupBox('Grid Parameters')
        grid_param_grid         = QtGui.QGridLayout()
        grid_param_grid.addWidget(sub_param_widget, 0, 0, 1, 4)
        grid_param_grid.addWidget(self.flip_check, 1, 0)
        grid_param_grid.addWidget(adjustment_btn, 2, 0)
        grid_param_grid.setVerticalSpacing(3)
        self.grid_param_group.setLayout(grid_param_grid)

        #- GridView Figure GroupBox -#
        self.gridviewFig = GridViewFig(self)
        self.grid_view_group = QtGui.QGroupBox('Grid View')
        grid_view_grid = QtGui.QGridLayout()
        grid_view_grid.addWidget(self.gridviewFig, 0, 0)
        self.grid_view_group.setLayout(grid_view_grid)




class GridInfoUI(QtGui.QFrame):

    def __init__(self, parent=None):
        super(GridInfoUI, self).__init__()
        self.initUI()

    def initUI(self):


        #-------- Widgets --------#
        #--- Labels ---#
        cell_label = MyQLabel('Number of Cells', ha= 'center')
        data_label = MyQLabel('Number of Data', ha= 'center')
        tt_picked_label = MyQLabel('Traveltimes Picked', ha= 'left')
        amp_picked_label = MyQLabel('Amplitudes Picked', ha= 'left')

        self.num_cell_label = MyQLabel('0', ha= 'center')
        self.num_data_label = MyQLabel('0', ha= 'center')
        self.num_tt_picked_label = MyQLabel('0', ha= 'right')
        self.num_amp_picked_label = MyQLabel('0', ha= 'right')


        master_grid = QtGui.QGridLayout()
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
    def __init__(self, data, parent = None):

        fig = mpl.figure.Figure(figsize= (100, 100), facecolor='white')
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

        self.ax4.set_title('Distance between original and projected Tx', y= 1.08)
        self.ax5.set_title('Distance between originial and projected Rx', y= 1.08)
        self.ax6.set_title('Relative error on ray length after projection [%]', y= 1.08)
        self.ax1.set_title('Tx direction cosines after rotation', y= 1.08)
        self.ax2.set_title('Rx direction cosines after rotation', y= 1.08)

    def plot_stats(self):

        dTx = np.sqrt(np.sum((self.data.Tx - self.data.Tx_p)**2, axis= 1))
        dRx = np.sqrt(np.sum((self.data.Rx - self.data.Rx_p)**2, axis= 1))
        l_origin = np.sqrt(np.sum((self.data.Tx - self.data.Rx)**2, axis= 1))
        l_new = np.sqrt(np.sum((self.data.Tx_p - self.data.Rx_p)**2, axis= 1))
        error = 100 * np.abs(l_origin - l_new)/l_origin

        self.ax4.plot(dTx, marker = 'o',
                           fillstyle= 'none',
                           color= 'blue',
                           markersize= 5,
                           mew= 1,
                           ls = 'None')

        self.ax5.plot(dRx, marker = 'o',
                           fillstyle= 'none',
                           color= 'blue',
                           markersize= 5,
                           mew= 1,
                           ls = 'None')

        self.ax6.plot(error, marker = 'o',
                             fillstyle= 'none',
                             color= 'blue',
                             markersize= 5,
                             mew= 1,
                             ls = 'None')

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
            false_Rx_ind = np.nonzero(mog.in_Rx_vect == False)
            false_Tx_ind = np.nonzero(mog.in_Tx_vect == False)

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
            self.ax.text(x= Tx_xs[0],y=  Tx_ys[0],z= mog.Tx.fdata[0, 2], s= str(mog.Tx.name))
            self.ax.scatter(Tx_xs, Tx_ys, Tx_zs, c='g', marker='o', label="{}'s Tx".format(mog.name), lw=0)
            self.ax.text(x= Rx_xs[0],y= Rx_ys[0],z= mog.Rx.fdata[0, 2] , s= str(mog.Rx.name))
            self.ax.scatter(Rx_xs, Rx_ys, Rx_zs, c='b', marker='*', label="{}'s Rx".format(mog.name), lw=0)

            l = self.ax.legend(ncol=1, bbox_to_anchor=(0, 1), loc='upper left',
                               borderpad=0)
            l.draw_frame(False)


            self.ax.plot(mog.Tx.fdata[:, 0], mog.Tx.fdata[:, 1], mog.Tx.fdata[:, 2], color= 'r')
            self.ax.plot(mog.Rx.fdata[:, 0], mog.Rx.fdata[:, 1], mog.Rx.fdata[:, 2], color= 'r')

        if view == '3D View':
            self.ax.view_init()
        elif view == 'XY Plane':
            self.ax.view_init(elev= 90, azim= 90)
        elif view == 'XZ Plane':
            self.ax.view_init(elev= 0, azim= 90)
        elif view == 'YZ Plane':
            self.ax.view_init(elev= 0, azim= 0)
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


        az, dip = self.gUI.get_azimuth_dip()
        self.gUI.grid.Tx = Grid.transl_rotat(self.gUI.data.Tx_p, self.gUI.grid.x0, az, dip)
        self.gUI.grid.Rx = Grid.transl_rotat(self.gUI.data.Rx_p, self.gUI.grid.x0, az, dip)
        self.gUI.grid.TxCosDir = Grid.transl_rotat(self.gUI.data.TxCosDir.T, np.array([0, 0, 0]), az, dip)
        self.gUI.grid.RxCosDir = Grid.transl_rotat(self.gUI.data.RxCosDir.T, np.array([0, 0, 0]), az, dip)


        self.gUI.grid.in_vect = self.gUI.data.in_vect

        nxm = self.gUI.grid.border[0]
        nxp = self.gUI.grid.border[1]
        nzm = self.gUI.grid.border[2]
        nzp = self.gUI.grid.border[3]


        xmin = min(np.concatenate((self.gUI.grid.Tx[self.gUI.grid.in_vect, 0], self.gUI.grid.Rx[self.gUI.grid.in_vect, 0]), axis= 0).flatten()) - 0.5 * self.gUI.dx
        xmax = max(np.concatenate((self.gUI.grid.Tx[self.gUI.grid.in_vect, 0], self.gUI.grid.Rx[self.gUI.grid.in_vect, 0]), axis= 0).flatten()) + 0.5 * self.gUI.dx
        nx = np.ceil((xmax - xmin)/self.gUI.dx)

        zmin = min(np.concatenate((self.gUI.grid.Tx[self.gUI.grid.in_vect, 2], self.gUI.grid.Rx[self.gUI.grid.in_vect, 2]), axis= 0).flatten()) - 0.5 * self.gUI.dz
        zmax = max(np.concatenate((self.gUI.grid.Tx[self.gUI.grid.in_vect, 2], self.gUI.grid.Rx[self.gUI.grid.in_vect, 2]), axis= 0).flatten()) + 0.5 * self.gUI.dz
        nz = np.ceil((zmax - zmin)/self.gUI.dz)



        self.gUI.grid.grx = xmin + self.gUI.dx * np.arange(-nxm, nx + nxp + 1).T

        self.gUI.grid.grz = zmin + self.gUI.dz * np.arange(-nzm, nz + nzp + 1).T



        z1 = self.gUI.grid.grz[0] * np.ones(len(self.gUI.grid.grx) +1).T[:, None]
        z2 = self.gUI.grid.grz[-1] * np.ones(len(self.gUI.grid.grx) +1).T[:, None]

        x1 = self.gUI.grid.grx[0] * np.ones(len(self.gUI.grid.grz) +1).T[:, None]
        x2 = self.gUI.grid.grx[-1] * np.ones(len(self.gUI.grid.grz) +1).T[:, None]

        #x1 = xmin - self.gUI.dx*nxm * np.ones(len(self.gUI.grid.grz) +1).T[:, None]
        #x2 = xmax + self.gUI.dx*nxp * np.ones(len(self.gUI.grid.grz) +1).T[:, None]

        zz1 = np.concatenate((z1,z2), axis= 1)
        xx1 = np.concatenate((x1, x2), axis= 1)

        zz2 = np.concatenate((self.gUI.grid.grz.T[:, None], self.gUI.grid.grz.T[:, None]), axis = 1)
        xx2 = np.concatenate((self.gUI.grid.grx.T[:, None], self.gUI.grid.grx.T[:, None]), axis = 1)

        for i in range(len(self.gUI.grid.grx)):
            self.ax.plot(xx2[i, :], zz1[i, :], color= 'grey')

        for j in range(len(self.gUI.grid.grz)):
            self.ax.plot(xx1[j, :], zz2[j, :], color= 'grey')

        self.ax.plot(self.gUI.grid.Tx[self.gUI.grid.in_vect, 0], self.gUI.grid.Tx[self.gUI.grid.in_vect, 2], marker= 'o', color= 'green', ls= 'none')
        self.ax.plot(self.gUI.grid.Rx[self.gUI.grid.in_vect, 0], self.gUI.grid.Rx[self.gUI.grid.in_vect, 2], marker= '*', color= 'blue', ls= 'none')

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
                self.ax.plot(orig_Tx, -Tx_zs, 'o', c= 'g')

                if flip:
                    self.ax.plot(np.abs(Tx_ys[0]-Rx_ys[0])*np.ones(len(Rx_zs)), -Rx_zs, '*', c= 'b')
                    self.ax.set_xlim([-pad_x_minus, np.abs(Tx_ys[0]-Rx_ys[0]) + pad_x_plus])
                    self.ax.set_xticks(np.arange(-pad_x_minus, np.abs((Tx_ys[0] - Rx_ys[0])) + pad_x_plus, x_cell_size), minor= True)

                if not flip:
                    self.ax.plot(-np.abs((Tx_ys[0]-Rx_ys[0]))*np.ones(len(Rx_zs)), -Rx_zs, '*', c= 'b')
                    self.ax.set_xlim([-pad_x_minus-np.abs((Tx_ys[0]-Rx_ys[0])), pad_x_plus])
                    self.ax.set_xticks(np.arange(-pad_x_minus- (Tx_ys[0] - Rx_ys[0]),  pad_x_plus, x_cell_size), minor= True)

            if origin == mog.Rx.name:
                self.ax.plot(orig_Rx, -Rx_zs, '*', c='b')

                if flip:
                    self.ax.plot(np.abs((Rx_ys[0] - Tx_ys[0])) * np.ones(len(Tx_zs)), -Tx_zs, 'o', c='g')
                    self.ax.set_xlim([-pad_x_minus, np.abs((Rx_ys[0] - Tx_ys[0]))+ pad_x_plus ])
                    self.ax.set_xticks(np.arange(-pad_x_minus, np.abs((Rx_ys[0] - Tx_ys[0])) + pad_x_plus, x_cell_size), minor= True)

                if not flip:
                    self.ax.plot(-np.abs((Rx_ys[0] - Tx_ys[0])) * np.ones(len(Tx_zs)), -Tx_zs, 'o', c='g')
                    self.ax.set_xlim([-np.abs((Rx_ys[0] - Tx_ys[0]))- pad_x_minus, pad_x_plus])
                    self.ax.set_xticks(np.arange(-np.abs((Rx_ys[0] - Tx_ys[0])) - pad_x_minus, pad_x_plus, x_cell_size ), minor= True)

            if max(mog.data.Rx_z) > max(mog.data.Tx_z):
                self.ax.set_ylim([-max(mog.data.Rx_z)-pad_z_minus, pad_z_plus])
                self.ax.set_yticks(np.arange(-max(mog.data.Rx_z)-pad_z_minus,pad_z_plus , z_cell_size), minor= True)
            if max(mog.data.Tx_z) > max(mog.data.Rx_z):
                self.ax.set_ylim([-max(mog.data.Tx_z) - pad_z_minus, pad_z_plus])
                self.ax.set_yticks(np.arange(-max(mog.data.Tx_z) - pad_z_minus, pad_z_plus, z_cell_size), minor= True)

            for tic in self.ax.xaxis.get_major_ticks():
                tic.tick1On = tic.tick2On = False
                #tic.label1On = tic.label2On = False

            for tic in self.ax.yaxis.get_major_ticks():
                tic.tick1On = tic.tick2On = False
                #tic.label1On = tic.label2On = False

            self.ax.set_xlabel('Y', fontsize= 16)
            self.ax.set_ylabel('Z', fontsize= 16)
            self.ax.grid(which= 'both', ls='solid')


        self.draw()

class ConstraintsEditorUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConstraintsEditorUI, self).__init__()
        self.constraintsFig = ConstraintsFig(self)
        self.initUI()

    def initUI(self):
        #-------- Widgets -------#
        #--- Buttons ---#
        edit_btn                    = QtGui.QPushButton('Edit')
        import_btn                  = QtGui.QPushButton('Import')
        reinit_btn                  = QtGui.QPushButton('Reinitialize')
        display_btn                 = QtGui.QPushButton('Display')
        cancel_btn                  = QtGui.QPushButton('Cancel')
        done_btn                    = QtGui.QPushButton('Done')

        #--- Labels ---#
        cmax_label                  = MyQLabel('Cmax', ha= 'center')
        cmin_label                  = MyQLabel('Cmin', ha= 'center')
        property_value_label        = MyQLabel('Value: ', ha= 'right')
        variance_value_label        = MyQLabel('Value: ', ha= 'right')

        #--- Edits ---#
        self.cmax_edit              = QtGui.QLineEdit('1')
        self.cmin_edit              = QtGui.QLineEdit('0')
        self.property_value_edit    = QtGui.QLineEdit('0')
        self.variance_value_edit    = QtGui.QLineEdit('0')

        #- Edits Disposition -#
        self.cmax_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.cmin_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.property_value_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.variance_value_edit.setAlignment(QtCore.Qt.AlignHCenter)

        #--- ComboBox ---#
        self.property_combo         = QtGui.QComboBox()

        #- Combobox Items -#
        properties_list             = ['Velocity', 'Attenuation', 'Reservoir', 'Xi', 'Tilt Angle' ]
        self.property_combo.addItems(properties_list)

        #--- SubWidgets ---#
        #- Property Value SubWidget -#
        sub_property_value_widget   = QtGui.QWidget()
        sub_property_value_grid     = QtGui.QGridLayout()
        sub_property_value_grid.addWidget(property_value_label, 0, 0)
        sub_property_value_grid.addWidget(self.property_value_edit, 0, 1)
        sub_property_value_grid.setContentsMargins(0, 0, 0, 0)
        sub_property_value_grid.setHorizontalSpacing(0)
        sub_property_value_widget.setLayout(sub_property_value_grid)

        #- Variance Value SubWidget -#
        sub_variance_value_widget   = QtGui.QWidget()
        sub_variance_value_grid     = QtGui.QGridLayout()
        sub_variance_value_grid.addWidget(variance_value_label, 0, 0)
        sub_variance_value_grid.addWidget(self.variance_value_edit, 0, 1)
        sub_variance_value_grid.setContentsMargins(0, 0, 0, 0)
        sub_variance_value_grid.setHorizontalSpacing(0)
        sub_variance_value_widget.setLayout(sub_variance_value_grid)


        #------- GroupBoxes -------#
        #--- Constraints GroupBox ---#
        constraints_group = QtGui.QGroupBox('Constraints')
        constraints_grid = QtGui.QGridLayout()
        constraints_grid.addWidget(self.constraintsFig, 0, 0, 8, 1)
        constraints_grid.addWidget(cmax_label, 0, 1)
        constraints_grid.addWidget(self.cmax_edit, 1, 1)
        constraints_grid.addWidget(cmin_label, 6, 1)
        constraints_grid.addWidget(self.cmin_edit, 7, 1)
        constraints_grid.setColumnStretch(0, 100)
        constraints_grid.setRowStretch(2, 100)
        constraints_group.setLayout(constraints_grid)
        #--- Variance GroupBox ---#
        variance_group              = QtGui.QGroupBox('Variance')
        variance_grid               = QtGui.QGridLayout()
        variance_grid.addWidget(sub_variance_value_widget, 0, 0)
        variance_grid.addWidget(display_btn, 1, 0)
        variance_group.setLayout(variance_grid)
        #--- Property GroupBox ---#
        property_group              = QtGui.QGroupBox('Property')
        property_grid               = QtGui.QGridLayout()
        property_grid.addWidget(self.property_combo, 0, 0)
        property_grid.addWidget(sub_property_value_widget, 1, 0)
        property_grid.addWidget(edit_btn, 2, 0)
        property_grid.addWidget(import_btn, 3, 0)
        property_grid.addWidget(reinit_btn, 4, 0)
        property_grid.addWidget(variance_group, 5, 0)
        property_group.setLayout(property_grid)



        #------- Master grid's Layout -------#
        master_grid                 = QtGui.QGridLayout()
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
        divider.append_axes('right', size= 0.5, pad= 0.1)

    def plot_constraints(self, mog):
        self.ax2 = self.figure.axes[1]
        self.ax.cla()
        self.ax2.cla()
        cmin = self.constraints_editor.cmin_edit.text()
        cmax = self.constraints_editor.cmax_edit.text()

        #h= self.ax.imshow(data, aspect='auto')
        #mpl.colorbar.Colorbar(self.ax2, h)

class Data:
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




class  MyQLabel(QtGui.QLabel):
            def __init__(self, label, ha='left',  parent=None):
                super(MyQLabel, self).__init__(label,parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = ModelUI()
    Model_ui.show()

    sys.exit(app.exec_())

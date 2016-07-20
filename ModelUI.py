import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import matplotlib as mpl
from model import Model


class ModelUI(QtGui.QWidget):
    #------- Signals Emitted -------#
    modelInfoSignal = QtCore.pyqtSignal(int)
    modellogSignal = QtCore.pyqtSignal(str)

    def __init__(self, borehole, mog, parent=None):
        super(ModelUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Models")
        self.borehole = borehole
        self.mog = mog
        self.models = []
        self.grid = gridUI(self)
        self.initUI()

    def add_model(self):
        name, ok = QtGui.QInputDialog.getText(self, "Model creation", 'Model name')
        if ok :
            self.load_model(name)

    def load_model(self, name):
        self.models.append(Model(name))
        self.modellogSignal.emit("Model {} as been added succesfully".format(name))
        self.update_model_list()

    def del_model(self):
        ind = self.model_list.selectedIndexes()
        for i in ind:
            self.modellogSignal.emit("Model {} as been deleted succesfully".format(self.models[int(i.row())]))
            del self.models[int(i.row())]
        self.update_model_list()

    def add_mog(self):
        ind = self.mog.MOG_list.currentIndex().row()
        n = self.model_list.currentIndex().row()
        self.load_mog(ind, n)

    def load_mog(self, ind, n):
        self.model_mog_list.addItem(self.mog.MOGs[ind].name)
        self.models[n].mogs.append(self.mog.MOGs[ind])

    def update_model_mog_list(self):
        n = self.model_list.currentIndex().row()
        for mog in self.models[n].mogs:
            self.model_mog_list.addItem(mog.name)


    def update_model_list(self):
        self.model_list.clear()
        for model in self.models:
            self.model_list.addItem(model.name)
        self.modelInfoSignal.emit(len(self.model_list)) # we send the information to DatabaseUI

    def update_grid_info(self):
        ndata = 0
        n_tt_data_picked = 0
        n_amp_data_picked = 0
        ind = self.model_list.currentIndex().row()

        for mog in self.models[ind].mogs:

            ndata += mog.data.ntrace
            n_tt_data_picked += sum(mog.tt_done.astype(int) + mog.in_vect.astype(int))
            n_amp_data_picked += sum(mog.amp_done.astype(int) + mog.in_vect.astype(int))

        self.grid.gridinfo.num_data_label.setText(str(ndata))
        self.grid.gridinfo.num_tt_picked_label.setText(str(n_tt_data_picked))
        self.grid.gridinfo.num_amp_picked_label.setText(str(n_amp_data_picked))

    def start_grid(self):
        self.grid.showMaximized()
        self.grid.plot_boreholes()
        self.grid.update_bh_origin()
        self.grid.update_origin()
        self.grid.plot_grid_view()
        self.update_grid_info()

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
        btn_Add_MOG.clicked.connect(self.add_mog)
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


class gridUI(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(gridUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/gridUI")
        self.gridinfo = GridInfoUI()
        self.constraintseditor = ConstraintsEditorUI()
        self.model = model

        self.boreholes = self.model.borehole.boreholes

        self.MOGs = self.model.mog.MOGs
        self.initUI()

    def plot_adjustment(self):
        self.bestfitplaneFig.plot_stats()
        self.bestfitplanemanager.showMaximized()

    def plot_boreholes(self):
        self.model_ind = self.model.model_list.currentIndex().row()
        view = self.bhfig_combo.currentText()
        self.bhsFig.plot_boreholes(self.model.borehole.boreholes, self.model.models[self.model_ind].mogs, view)

    def plot_grid_view(self):
        bh = self.borehole_combo.currentText()
        state = self.flip_check.checkState()
        self.gridviewFig.plot_grid(self.model.models[self.model_ind].mogs, bh, state)

    def update_bh_origin(self):
        self.borehole_combo.clear()
        Tx_output = set()
        Rx_output = set()
        for n in range(len(self.model.mog.MOGs)):
            Tx_output.add(self.model.mog.MOGs[n].Tx.name)
            Rx_output.add(self.model.mog.MOGs[n].Rx.name)

        Tx_output = list(Tx_output)
        Rx_output = list(Rx_output)
        for Tx in Tx_output:
            self.borehole_combo.addItem(Tx)
        for Rx in Rx_output:
            self.borehole_combo.addItem(Rx)



    def update_origin(self):
        ind = self.borehole_combo.currentIndex()

        self.origin_x_edit.setText(str(self.model.borehole.boreholes[ind].X))
        self.origin_y_edit.setText(str(self.model.borehole.boreholes[ind].Y))
        self.origin_z_edit.setText(str(self.model.borehole.boreholes[ind].Z))



    def initUI(self):

        #------- Manager for the Best fit plane Figure -------#
        self.bestfitplaneFig = BestFitPlaneFig()
        self.bestfitplanemanager = QtGui.QWidget()
        self.bestfitplanetool = NavigationToolbar2QT(self.bestfitplaneFig, self)
        bestfitplanemanagergrid = QtGui.QGridLayout()
        bestfitplanemanagergrid.addWidget(self.bestfitplanetool, 0, 0)
        bestfitplanemanagergrid.addWidget(self.bestfitplaneFig, 1, 0)
        self.bestfitplanemanager.setLayout(bestfitplanemanagergrid)

        #-------- Widgets Creation --------#
        #--- Buttons ---#
        add_edit_btn            = QtGui.QPushButton('Add/Edit Constraints')
        cancel_btn              = QtGui.QPushButton('Cancel')
        done_btn                = QtGui.QPushButton('Done')
        adjustment_btn          = QtGui.QPushButton('Adjustment of Best-Fit Plane')
        #- Buttons' Actions -#
        adjustment_btn.clicked.connect(self.plot_adjustment)
        add_edit_btn.clicked.connect(self.constraintseditor.show)
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
        self.flip_check.stateChanged.connect(self.plot_grid_view)
        #--- ComboBoxes ---#
        self.borehole_combo     = QtGui.QComboBox()
        self.bhfig_combo        = QtGui.QComboBox()

        #- Combobox items -#
        view_list = ['3D View', 'XY Plane', 'XZ Plane', 'YZ Plane']
        for item in view_list:
            self.bhfig_combo.addItem(item)

        #- ComboBoxes Actions -#
        self.borehole_combo.activated.connect(self.update_origin)
        self.borehole_combo.activated.connect(self.plot_grid_view)
        self.bhfig_combo.activated.connect(self.plot_boreholes)


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
        grid_param_group        = QtGui.QGroupBox('Grid Parameters')
        grid_param_grid         = QtGui.QGridLayout()
        grid_param_grid.addWidget(sub_param_widget, 0, 0, 1, 4)
        grid_param_grid.addWidget(self.flip_check, 1, 0)
        grid_param_grid.addWidget(adjustment_btn, 2, 0)
        grid_param_grid.setVerticalSpacing(3)
        grid_param_group.setLayout(grid_param_grid)

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

        # - Boreholes Figure GroupBox -#
        self.gridviewFig = GridViewFig()
        grid_view_group = QtGui.QGroupBox('Grid View')
        grid_view_grid = QtGui.QGridLayout()
        grid_view_grid.addWidget(self.gridviewFig, 0, 0)
        grid_view_group.setLayout(grid_view_grid)

        #------- Master grid's disposition -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(grid_info_group, 0, 0)
        master_grid.addWidget(add_edit_btn, 1, 0)
        master_grid.addWidget(cancel_btn, 2, 0)
        master_grid.addWidget(done_btn, 3, 0)
        master_grid.addWidget(grid_param_group, 0, 1, 4, 1)
        master_grid.addWidget(bhs_group, 4, 0, 1, 2)
        master_grid.addWidget(grid_view_group, 0, 2, 5, 1)
        master_grid.setColumnStretch(2, 100)
        master_grid.setRowStretch(4, 100)
        self.setLayout(master_grid)

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

        self.num_cell_label = MyQLabel('1000', ha= 'center')
        self.num_data_label = MyQLabel('1000', ha= 'center')
        self.num_tt_picked_label = MyQLabel('1000', ha= 'right')
        self.num_amp_picked_label = MyQLabel('1000', ha= 'right')


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
    def __init__(self, parent = None):

        fig = mpl.figure.Figure(figsize= (100, 100), facecolor='white')
        super(BestFitPlaneFig, self).__init__(fig)
        self.initFig()

    def initFig(self):

        # horizontal configruation
        self.ax1 = self.figure.add_axes([0.1, 0.1, 0.2, 0.25])
        self.ax2 = self.figure.add_axes([0.4, 0.1, 0.2, 0.25])

        self.ax4 = self.figure.add_axes([0.1, 0.55, 0.2, 0.25])
        self.ax5 = self.figure.add_axes([0.4, 0.55, 0.2, 0.25])
        self.ax6 = self.figure.add_axes([0.7, 0.55, 0.2, 0.25])

    def plot_stats(self):

        self.ax4.set_title('Distance between original and projected Tx', y= 1.08)
        self.ax5.set_title('Distance between originial and projected Rx', y= 1.08)
        self.ax6.set_title('Relative error on ray length after projection [%]', y= 1.08)
        self.ax1.set_title('Tx direction cosines after rotation', y= 1.08)
        self.ax2.set_title('Rx direction cosines after rotation', y= 1.08)

class BoreholesFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(BoreholesFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_boreholes(self, boreholes, mogs, view):
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
            self.ax.text(x= Tx_xs[0],y=  Tx_ys[0],z= Tx_zs[0], s= str(mog.Tx.name))
            self.ax.scatter(Tx_xs, Tx_ys, -Tx_zs, c='g', marker='o', label="{}'s Tx".format(mog.name), lw=0)
            self.ax.text(x= Rx_xs[0],y= Rx_ys[0],z= Rx_zs[0], s= str(mog.Rx.name))
            self.ax.scatter(Rx_xs, Rx_ys, -Rx_zs, c='b', marker='*', label="{}'s Rx".format(mog.name), lw=0)

            l = self.ax.legend(ncol=1, bbox_to_anchor=(0, 1), loc='upper left',
                               borderpad=0)
            l.draw_frame(False)

        for bhole in boreholes:
            self.ax.plot(bhole.fdata[:, 0], bhole.fdata[:, 1], bhole.fdata[:, 2], color= 'r')

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
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(GridViewFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.1, 0.1, 0.85, 0.85])
        self.ax.grid(True)

    def plot_grid(self, mogs, origin, flip):
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
                    self.ax.plot((Tx_ys[0]-Rx_ys[0])*np.ones(len(Rx_zs)), -Rx_zs, '*', c= 'b')
                    self.ax.set_xlim([(Tx_ys[0]-Rx_ys[0])-0.2, 0.2])
                if not flip:
                    self.ax.plot(-(Tx_ys[0]-Rx_ys[0])*np.ones(len(Rx_zs)), -Rx_zs, '*', c= 'b')
                    self.ax.set_xlim([-0.2, -(Tx_ys[0]-Rx_ys[0])+0.2])

            if origin == mog.Rx.name:
                self.ax.plot(orig_Rx, -Rx_zs, '*', c='b')

                if flip:
                    self.ax.plot((Rx_ys[0] - Tx_ys[0]) * np.ones(len(Tx_zs)), -Tx_zs, 'o', c='g')
                    self.ax.set_xlim([-0.2, (Rx_ys[0] - Tx_ys[0])+0.2 ])
                if not flip:
                    self.ax.plot(-(Rx_ys[0] - Tx_ys[0]) * np.ones(len(Tx_zs)), -Tx_zs, 'o', c='g')
                    self.ax.set_xlim([-(Rx_ys[0] - Tx_ys[0])-0.2, 0.2])

            self.ax.set_xlabel('Y', fontsize= 16)
            self.ax.set_ylabel('Z', fontsize= 16)
            self.ax.grid(which= 'both', ls='solid')


        self.draw()

class ConstraintsEditorUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ConstraintsEditorUI, self).__init__()

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
        self.cmax_edit              = QtGui.QLineEdit()
        self.cmin_edit              = QtGui.QLineEdit()
        self.property_value_edit    = QtGui.QLineEdit()
        self.variance_value_edit    = QtGui.QLineEdit()

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
        self.constraintsFig = ConstraintsFig()
        constraints_group = QtGui.QGroupBox('Constraints')
        constraints_grid = QtGui.QGridLayout()
        constraints_grid.addWidget(self.constraintsFig, 0, 0, 8, 1)
        constraints_grid.addWidget(cmax_label, 0, 1)
        constraints_grid.addWidget(self.cmax_edit, 1, 1)
        constraints_grid.addWidget(cmin_label, 6, 1)
        constraints_grid.addWidget(self.cmin_edit, 7, 1)
        constraints_grid.setColumnStretch(0, 100)
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
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(4, 3), facecolor='white')
        super(ConstraintsFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        ax = self.figure.add_axes([0.05, 0.08, 0.9, 0.9])
        divider = make_axes_locatable(ax)
        divider.append_axes('right', size= 0.5, pad= 0.1)


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

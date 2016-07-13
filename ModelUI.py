import sys
from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import matplotlib as mpl


class ModelUI(QtGui.QWidget):
    #------- Signals Emitted -------#
    modelInfoSignal = QtCore.pyqtSignal(int)
    modellogSignal = QtCore.pyqtSignal(str)

    def __init__(self, borehole, mog, parent=None):
        super(ModelUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Models")
        self.models = []
        self.grid = gridUI()
        self.initUI()

    def add_model(self):
        name, ok = QtGui.QInputDialog.getText(self, "Model creation", 'Model name')
        if ok :
            self.models.append(name)
            self.modellogSignal.emit("Model {} as been added succesfully".format(name))
        self.update_model_list()

    def del_model(self):
        ind = self.model_list.selectedIndexes()
        for i in ind:
            self.modellogSignal.emit("Model {} as been deleted succesfully".format(self.models[int(i.row())]))
            del self.models[int(i.row())]
        self.update_model_list()


    def update_model_list(self):
        self.model_list.clear()
        for model in self.models:
            self.model_list.addItem(model)
        self.modelInfoSignal.emit(len(self.model_list)) # we send the information to DatabaseUI

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
        btn_Edit_Grid.clicked.connect(self.grid.show)

        #--- Lists ---#
        MOG_list                         = QtGui.QListWidget()
        self.model_list                       = QtGui.QListWidget()

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
        MOGS_Sub_Grid.addWidget(MOG_list, 1, 0, 1, 4)
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

    def __init__(self, parent=None):
        super(gridUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/gridUI")
        self.gridinfo = GridInfoUI()
        self.initUI()

    def plot_adjustment(self):
        self.bestfitplaneFig.plot_stats()
        self.bestfitplanemanager.showMaximized()

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
        #--- Edits ---#
        self.pad_plus_x_edit    = QtGui.QLineEdit()
        self.pad_plus_z_edit    = QtGui.QLineEdit()
        self.pad_minus_x_edit   = QtGui.QLineEdit()
        self.pad_minus_z_edit   = QtGui.QLineEdit()

        self.cell_size_x_edit   = QtGui.QLineEdit()
        self.cell_size_z_edit   = QtGui.QLineEdit()

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
        flip_check              = QtGui.QCheckBox('Flip horizontally')
        #--- ComboBox ---#
        borehole_combo          = QtGui.QComboBox()
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
        sub_param_grid.addWidget(borehole_combo, 3, 1)
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
        grid_param_grid.addWidget(flip_check, 1, 0)
        grid_param_grid.addWidget(adjustment_btn, 2, 0)

        grid_param_group.setLayout(grid_param_grid)

        #- Grid Info GroupBox -#
        grid_info_group         = QtGui.QGroupBox('Infos')
        grid_info_grid          = QtGui.QGridLayout()
        grid_info_grid.addWidget(self.gridinfo)
        grid_info_group.setLayout(grid_info_grid)




        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(grid_info_group, 0, 0)
        master_grid.addWidget(grid_param_group, 0, 1)
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

class gridUI(QtGui.QWidget):

    def __init__(self, parent=None):
        super(gridUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/gridUI")
        self.gridinfo = GridInfoUI()
        self.initUI()

    def plot_adjustment(self):
        self.bestfitplaneFig.plot_stats()
        self.bestfitplanemanager.showMaximized()

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
        #--- Edits ---#
        self.pad_plus_x_edit    = QtGui.QLineEdit()
        self.pad_plus_z_edit    = QtGui.QLineEdit()
        self.pad_minus_x_edit   = QtGui.QLineEdit()
        self.pad_minus_z_edit   = QtGui.QLineEdit()

        self.cell_size_x_edit   = QtGui.QLineEdit()
        self.cell_size_z_edit   = QtGui.QLineEdit()

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
        flip_check              = QtGui.QCheckBox('Flip horizontally')
        #--- ComboBox ---#
        borehole_combo          = QtGui.QComboBox()
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
        sub_param_grid.addWidget(borehole_combo, 3, 1)
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
        grid_param_grid.addWidget(flip_check, 1, 0)
        grid_param_grid.addWidget(adjustment_btn, 2, 0)

        grid_param_group.setLayout(grid_param_grid)

        #- Grid Info GroupBox -#
        grid_info_group         = QtGui.QGroupBox('Infos')
        grid_info_grid          = QtGui.QGridLayout()
        grid_info_grid.addWidget(self.gridinfo)
        grid_info_group.setLayout(grid_info_grid)




        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(grid_info_group, 0, 0)
        master_grid.addWidget(grid_param_group, 0, 1)
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

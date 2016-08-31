# -*- coding: utf-8 -*-
"""

Copyright 2016 Bernard Giroux, Elie Dumas-Lefebvre

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it /will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from PyQt4 import QtGui, QtCore

class CovarUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(CovarUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Covariance")
        self.initUI()

    def initUI(self):
        #--- color for the labels ---#
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        #--- Class For Alignment ---#
        class  MyQLabel(QtGui.QLabel):
            def __init__(self, label, ha='left',  parent=None):
                super(MyQLabel, self).__init__(label,parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)

        #------- Widgets Creation -------#
        #--- Buttons Set ---#
        btn_Show_Stats = QtGui.QPushButton("Show Stats")
        btn_Add_Struct = QtGui.QPushButton("Add Structure")
        btn_Rem_Struct = QtGui.QPushButton("Remove Structure")
        btn_compute = QtGui.QPushButton("Compute")
        btn_GO = QtGui.QPushButton("GO")

        #--- Label ---#
        cells_Label = MyQLabel("Cells", ha= 'center')
        cells_Labeli = MyQLabel("Cells", ha= 'center')
        rays_label = MyQLabel("Rays", ha= 'center')

        curv_rays_label = MyQLabel("Curved Rays", ha= 'right')
        X_label = MyQLabel("X", ha= 'center')
        Y_label = MyQLabel("Y", ha= 'center')
        Z_label = MyQLabel("Y", ha= 'center')
        Xi_label = MyQLabel("X", ha= 'center')
        Yi_label = MyQLabel("Y", ha= 'center')
        Zi_label = MyQLabel("Z", ha= 'center')
        self.X_min_label = MyQLabel("0", ha= 'center')
        self.Y_min_label = MyQLabel("0", ha= 'center')
        self.Z_min_label = MyQLabel("0", ha= 'center')
        self.X_max_label = MyQLabel("0", ha= 'center')
        self.Y_max_label = MyQLabel("0", ha= 'center')
        self.Z_max_label = MyQLabel("0", ha= 'center')

        Min_label = MyQLabel("Min", ha= 'right')
        Max_label = MyQLabel("Max", ha='right')
        step_label = MyQLabel("Step :", ha= 'center')
        slowness_label = MyQLabel("Slowness", ha='right')
        traveltime_label = MyQLabel("Traveltime", ha= 'right')
        separ_label = MyQLabel("|", ha= 'center')
        bin_label = MyQLabel("Bin Length", ha= 'right')
        bin_frac_label = MyQLabel("Fraction of Bins", ha= 'right')
        Iter_label = MyQLabel("Number of Iterations", ha= 'right')


        self.X_min_label.setPalette(palette)
        self.Y_min_label.setPalette(palette)
        self.Z_min_label.setPalette(palette)
        self.X_max_label.setPalette(palette)
        self.Y_max_label.setPalette(palette)
        self.Z_max_label.setPalette(palette)
        cells_Label.setPalette(palette)
        cells_Labeli.setPalette(palette)
        rays_label.setPalette(palette)
        #--- Edits ---#
        cells_Edit = QtGui.QLineEdit()
        step_X_Edit = QtGui.QLineEdit()
        step_X_Edit.setFixedWidth(50)
        step_Y_Edit = QtGui.QLineEdit()
        step_Y_Edit.setFixedWidth(50)
        step_Z_Edit = QtGui.QLineEdit()
        step_Z_Edit.setFixedWidth(50)
        slowness_Edit = QtGui.QLineEdit('0')
        traveltime_Edit = QtGui.QLineEdit('0')
        bin_Edit = QtGui.QLineEdit('50')
        bin_frac_Edit = QtGui.QLineEdit('0.25')
        Iter_Edit = QtGui.QLineEdit('5')


        #--- Checkboxes ---#
        Upper_limit_checkbox = QtGui.QCheckBox("Upper Limit - Apparent Velocity")
        ellip_veloc_checkbox = QtGui.QCheckBox("Elliptical Velocity Anisotropy")
        tilted_ellip_veloc_checkbox = QtGui.QCheckBox("Tilted Elliptical Velocity Anisotropy")
        include_checkbox = QtGui.QCheckBox("Include Experimental Variance")
        slowness_checkbox = QtGui.QCheckBox()
        traveltime_checkbox = QtGui.QCheckBox()
        auto_update_checkbox = QtGui.QCheckBox("Auto Update")


        #--- Text Edits ---#
        futur_Graph1 = QtGui.QTextEdit()
        futur_Graph1.setReadOnly(True)
        futur_Graph2 = QtGui.QTextEdit()
        futur_Graph2.setReadOnly(True)

        #--- combobox ---#
        T_and_A_combo = QtGui.QComboBox()
        T_and_A_combo.addItem("Traveltime")
        T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        T_and_A_combo.addItem("Amplitude - Centroid Frequency")
        curv_rays_combo = QtGui.QComboBox()
        covar_struct_combo = QtGui.QComboBox()
        covar_struct_combo.addItem("Structure no 1")

        #--- List ---#
        self.ray_list = QtGui.QListWidget()

        #------- SubWidgets -------#
        #--- Curved Rays SubWidget ---#
        Sub_Curved_Rays_Widget = QtGui.QWidget()
        Sub_Curved_Rays_Grid = QtGui.QGridLayout()
        Sub_Curved_Rays_Grid.addWidget(curv_rays_label, 0, 0)
        Sub_Curved_Rays_Grid.addWidget(curv_rays_combo, 0, 1)
        Sub_Curved_Rays_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_Curved_Rays_Widget.setLayout(Sub_Curved_Rays_Grid)

        #--- Grid Coordinates SubWidget ---#
        Sub_Grid_Coord_Widget = QtGui.QWidget()
        Sub_Grid_Coord_grid = QtGui.QGridLayout()
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

        #--- Step SubWidget ---#
        Sub_Step_Widget = QtGui.QWidget()
        Sub_Step_Grid = QtGui.QGridLayout()
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


        #------- SubGroupboxes -------#
        #--- Data Groupbox ---#
        data_groupbox = QtGui.QGroupBox("Data")
        data_grid = QtGui.QGridLayout()
        data_grid.addWidget(cells_Label, 0, 0)
        data_grid.addWidget(rays_label, 1, 0)
        data_grid.addWidget(self.ray_list, 2, 0, 3, 1)
        data_grid.addWidget(Upper_limit_checkbox, 0, 1)
        data_grid.addWidget(cells_Edit, 0, 2)
        data_grid.addWidget(ellip_veloc_checkbox, 1, 1)
        data_grid.addWidget(tilted_ellip_veloc_checkbox, 2, 1)
        data_grid.addWidget(include_checkbox, 3, 1)
        data_grid.addWidget(T_and_A_combo, 4, 1)
        data_grid.addWidget(btn_Show_Stats, 4, 2)
        data_grid.addWidget(Sub_Curved_Rays_Widget, 5, 1)
        data_groupbox.setLayout(data_grid)

        #--- Grid Groupbox ---#
        Grid_groupbox = QtGui.QGroupBox("Grid")
        Grid_grid = QtGui.QGridLayout()
        Grid_grid.addWidget(Sub_Grid_Coord_Widget, 0, 0)
        Grid_grid.addWidget(Sub_Step_Widget, 0, 1)
        Grid_groupbox.setLayout(Grid_grid)

        #--- Parameters Groupbox ---#
        Param_groupbox = QtGui.QGroupBox("Parameters")
        Param_grid = QtGui.QGridLayout()
        Param_groupbox.setLayout(Param_grid)

        #--- Nugget Effect Groupbox ---#
        Nug_groupbox = QtGui.QGroupBox("Nugget Effect")
        Nug_grid = QtGui.QGridLayout()
        Nug_grid.addWidget(slowness_label, 0, 0)
        Nug_grid.addWidget(slowness_Edit, 0, 1)
        Nug_grid.addWidget(slowness_checkbox, 0, 2)
        Nug_grid.addWidget(separ_label, 0, 3)
        Nug_grid.addWidget(traveltime_label, 0, 4)
        Nug_grid.addWidget(traveltime_Edit, 0, 5)
        Nug_grid.addWidget(traveltime_checkbox, 0, 6)
        Nug_groupbox.setLayout(Nug_grid)

        #--- Covariance Model Groupbox ---#
        covar_groupbox = QtGui.QGroupBox("Covariance Model")
        covar_grid = QtGui.QGridLayout()
        covar_grid.addWidget(covar_struct_combo, 0, 0)
        covar_grid.addWidget(btn_Add_Struct, 0, 1)
        covar_grid.addWidget(btn_Rem_Struct, 0, 2)
        covar_grid.addWidget(Param_groupbox, 1, 0, 1, 3)
        covar_grid.addWidget(Nug_groupbox, 2, 0, 1, 3)
        covar_grid.addWidget(auto_update_checkbox, 3, 0)
        covar_grid.addWidget(btn_compute, 3, 1)
        covar_groupbox.setLayout(covar_grid)

        #--- Adjust Model Groupbox ---#
        Adjust_Model_groupbox = QtGui.QGroupBox("Adjust Model (Simplex Method)")
        Adjust_Model_grid = QtGui.QGridLayout()
        Adjust_Model_grid.addWidget(bin_label, 0, 0)
        Adjust_Model_grid.addWidget(bin_Edit, 0, 1)
        Adjust_Model_grid.addWidget(bin_frac_label, 1, 0)
        Adjust_Model_grid.addWidget(bin_frac_Edit, 1, 1)
        Adjust_Model_grid.addWidget(Iter_label, 2, 0)
        Adjust_Model_grid.addWidget(Iter_Edit, 2, 1)
        Adjust_Model_grid.addWidget(btn_GO, 0, 3, 3, 1)
        Adjust_Model_grid.setColumnStretch(4, 100)
        Adjust_Model_groupbox.setLayout(Adjust_Model_grid)

        #------- master Grid Disposition -------#
        master_grid = QtGui.QGridLayout()
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

    app = QtGui.QApplication(sys.argv)

    Model_ui = CovarUI()
    Model_ui.show()

    sys.exit(app.exec_())

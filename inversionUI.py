import sys
from PyQt4 import QtGui, QtCore

class InversionUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(InversionUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Inversion")
        self.initUI()

    def initUI(self):
        #--- Color for the labels ---#
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
        btn_View        = QtGui.QPushButton("Show Stats")
        btn_Delete      = QtGui.QPushButton("Add Structure")
        btn_Load        = QtGui.QPushButton("Remove Structure")
        btn_GO          = QtGui.QPushButton("GO")

        #--- Label ---#
        model_label            = MyQLabel("Model :", ha= 'center')
        cells_label            = MyQLabel("Cells", ha= 'center')
        mog_label              = MyQLabel("Select Mog", ha= 'center')
        Min_label              = MyQLabel("Min", ha= 'right')
        Max_label              = MyQLabel("Max", ha='right')
        Min_labeli             = MyQLabel("Min :", ha= 'right')
        Max_labeli             = MyQLabel("Max :", ha='right')
        X_label                = MyQLabel("X", ha= 'center')
        Y_label                = MyQLabel("Y", ha= 'center')
        Z_label                = MyQLabel("Y", ha= 'center')
        algo_label             = MyQLabel("Algorithm", ha= 'right')
        straight_ray_label     = MyQLabel("Straight Rays", ha= 'right')
        curv_ray_label         = MyQLabel("Curved Rays", ha= 'right')
        num_simulation_label   = MyQLabel("Number of Simulations", ha='right')
        slowness_label         = MyQLabel("Slowness", ha='right')
        separ_label            = MyQLabel("|", ha= 'center')
        traveltime_label       = MyQLabel("Traveltime", ha= 'right')
        step_label             = MyQLabel("Step :", ha= 'center')
        Xi_label               = MyQLabel("X", ha= 'center')          # The Xi, Yi and Zi  QLabels are practically the
        Yi_label               = MyQLabel("Y", ha= 'center')          # same as the X, Y and Z  QLabels, it's just that
        Zi_label               = MyQLabel("Z", ha= 'center')          # QtGui does not allow to use the same QLabel
        self.X_min_label       = MyQLabel("0", ha= 'center')          # twice or more. So we had to create new Qlabels
        self.Y_min_label       = MyQLabel("0", ha= 'center')
        self.Z_min_label       = MyQLabel("0", ha= 'center')
        self.X_max_label       = MyQLabel("0", ha= 'center')          # All the self.Something variables are defined
        self.Y_max_label       = MyQLabel("0", ha= 'center')          # that way because they will be modified throughout
        self.Z_max_label       = MyQLabel("0", ha= 'center')          # the processing of BH_THOMO.
        self.step_Xi_label     = MyQLabel("0", ha= 'center')          # Note: there are still a lot of variables which
        self.step_Yi_label     = MyQLabel("0", ha= 'center')          # the self. extension need to be applied.
        self.step_Zi_label     = MyQLabel("0", ha= 'center')          # I just don't know all of them at the moment


        #--- Setting Label's color ---#
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

        #--- Edits ---#
        straight_ray_edit       = QtGui.QLineEdit("1")  # Putting a string as the argument of the QLineEdit initializes
        curv_ray_edit           = QtGui.QLineEdit("1")  # it to the argument
        num_simulation_edit     = QtGui.QLineEdit()
        slowness_edit           = QtGui.QLineEdit('0')
        traveltime_edit         = QtGui.QLineEdit('0')
        Min_editi               = QtGui.QLineEdit()
        Max_editi               = QtGui.QLineEdit()

        #--- Checkboxes ---#
        use_const_checkbox              = QtGui.QCheckBox("Use Constraints")  #The argument of the QCheckBox is the title
        use_Rays_checkbox               = QtGui.QCheckBox("Use Rays")         # of it
        simulations_checkbox            = QtGui.QCheckBox("Simulations")
        ellip_veloc_checkbox            = QtGui.QCheckBox("Elliptical Velocity Anisotropy")
        tilted_ellip_veloc_checkbox     = QtGui.QCheckBox("Tilted Elliptical Velocity Anisotropy")
        include_checkbox                = QtGui.QCheckBox("Include Experimental Variance")
        set_color_checkbox              = QtGui.QCheckBox("Set Color Limits")

        #--- Checkboxes Actions ---#
        use_const_checkbox.setChecked(True)

        #--- Text Edits ---#
        futur_Graph1             = QtGui.QTextEdit()
        futur_Graph1.setReadOnly(True)

        #--- List ---#
        self.mog_list            = QtGui.QListWidget()
        test_list                = QtGui.QListWidget()     #list for the Parameters Groupbox

        #--- combobox ---#
        T_and_A_combo            = QtGui.QComboBox()
        prev_inversion_combo     = QtGui.QComboBox()
        algo_combo               = QtGui.QComboBox()
        geostat_struct_combo     = QtGui.QComboBox()
        fig_combo                = QtGui.QComboBox()


        #------- Items in the comboboxes --------#
        #--- Time and Amplitude Combobox's Items ---#
        T_and_A_combo.addItem("Traveltime")
        T_and_A_combo.addItem("Amplitude - Peak-to-Peak")
        T_and_A_combo.addItem("Amplitude - Centroid Frequency")

        #--- Algorithm Combobox's Items ---#
        algo_combo.addItem("Geostatistic")
        algo_combo.addItem("LSQR Solver")

        #--- Geostatistical Combobox's Items ---#
        geostat_struct_combo.addItem("Structure no 1")

        #--- Figure Combobox'S Items ---#
        fig_combo.addItem("cmr")
        fig_combo.addItem("polarmap")
        fig_combo.addItem("parula")
        fig_combo.addItem("jet")
        fig_combo.addItem("hsv")
        fig_combo.addItem("hot")
        fig_combo.addItem("cool")
        fig_combo.addItem("autumn")
        fig_combo.addItem("spring")
        fig_combo.addItem("winter")
        fig_combo.addItem("summer")
        fig_combo.addItem("gray")
        fig_combo.addItem("bone")
        fig_combo.addItem("copper")
        fig_combo.addItem("pink")
        fig_combo.addItem("prism")
        fig_combo.addItem("flag")
        fig_combo.addItem("colorcube")
        fig_combo.addItem("lines")


        #------- SubWidgets -------#
        #--- Data SubWidget ---#
        Sub_data_Widget = QtGui.QWidget()
        Sub_data_Grid = QtGui.QGridLayout()
        Sub_data_Grid.addWidget(T_and_A_combo, 0, 0)
        Sub_data_Grid.addWidget(use_const_checkbox, 1, 0)
        Sub_data_Grid.setRowStretch(2, 100)
        Sub_data_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_data_Widget.setLayout(Sub_data_Grid)

        #--- Algo SubWidget ---#
        Sub_algo_Widget = QtGui.QWidget()
        Sub_algo_Grid = QtGui.QGridLayout()
        Sub_algo_Grid.addWidget(algo_label, 0, 0)
        Sub_algo_Grid.addWidget(algo_combo, 0, 1)
        Sub_algo_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_algo_Widget.setLayout(Sub_algo_Grid)

        #---  Grid Coordinates SubWidget ---#
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
        Sub_Grid_Coord_grid.setContentsMargins(0, 0, 0, 0)
        Sub_Grid_Coord_Widget.setLayout(Sub_Grid_Coord_grid)

        #--- Step SubWidget ---#
        Sub_Step_Widget = QtGui.QWidget()
        Sub_Step_Grid = QtGui.QGridLayout()
        Sub_Step_Grid.addWidget(step_label, 1, 0)
        Sub_Step_Grid.addWidget(self.step_Xi_label, 1, 1)
        Sub_Step_Grid.addWidget(self.step_Yi_label, 1, 2)
        Sub_Step_Grid.addWidget(self.step_Zi_label, 1, 3)
        Sub_Step_Grid.addWidget(Xi_label, 0, 1)
        Sub_Step_Grid.addWidget(Yi_label, 0, 2)
        Sub_Step_Grid.addWidget(Zi_label, 0, 3)
        Sub_Step_Grid.addWidget(cells_label, 2, 2)
        Sub_Step_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_Step_Widget.setLayout(Sub_Step_Grid)


        #------- SubGroupboxes -------#
        #--- Data Groupbox ---#
        data_groupbox = QtGui.QGroupBox("Data")
        data_grid = QtGui.QGridLayout()
        data_grid.addWidget(model_label, 0, 0)
        data_grid.addWidget(Sub_data_Widget, 1, 0)
        data_grid.addWidget(mog_label, 0, 2)
        data_grid.addWidget(self.mog_list, 1, 2)
        data_groupbox.setLayout(data_grid)

        #--- Grid Groupbox ---#
        Grid_groupbox = QtGui.QGroupBox("Grid")
        Grid_grid = QtGui.QGridLayout()
        Grid_grid.addWidget(Sub_Grid_Coord_Widget, 0, 0)
        Grid_grid.addWidget(Sub_Step_Widget, 0, 1)
        Grid_groupbox.setLayout(Grid_grid)

        #--- Previous Inversion Groupbox ---#
        prev_inv_groupbox = QtGui.QGroupBox("Previous Inversions")
        prev_inv_grid = QtGui.QGridLayout()
        prev_inv_grid.addWidget(prev_inversion_combo, 0, 0, 1, 2)
        prev_inv_grid.addWidget(btn_View, 1, 0)
        prev_inv_grid.addWidget(btn_Delete, 1, 1)
        prev_inv_grid.addWidget(btn_Load, 1, 2)
        prev_inv_grid.addWidget(use_Rays_checkbox, 0, 2)
        prev_inv_groupbox.setLayout(prev_inv_grid)

        #--- Parameters Groupbox ---#
        Param_groupbox = QtGui.QGroupBox("Parameters")
        Param_grid = QtGui.QGridLayout()
        Param_grid.addWidget(test_list, 0, 0)
        Param_groupbox.setLayout(Param_grid)

        #--- Nugget Effect Groupbox ---#
        Nug_groupbox = QtGui.QGroupBox("Nugget Effect")
        Nug_grid = QtGui.QGridLayout()
        Nug_grid.addWidget(slowness_label, 0, 0)
        Nug_grid.addWidget(slowness_edit, 0, 1)
        Nug_grid.addWidget(separ_label, 0, 3)
        Nug_grid.addWidget(traveltime_label, 0, 4)
        Nug_grid.addWidget(traveltime_edit, 0, 5)
        Nug_groupbox.setLayout(Nug_grid)

        #--- Geostatistical inversion Groupbox ---#
        Geostat_groupbox = QtGui.QGroupBox("Geostatistical inversion")
        Geostat_grid = QtGui.QGridLayout()
        Geostat_grid.addWidget(simulations_checkbox, 0, 0)
        Geostat_grid.addWidget(ellip_veloc_checkbox, 1, 0)
        Geostat_grid.addWidget(include_checkbox, 2, 0)
        Geostat_grid.addWidget(num_simulation_label, 0, 1)
        Geostat_grid.addWidget(num_simulation_edit, 0, 2)
        Geostat_grid.addWidget(tilted_ellip_veloc_checkbox, 1, 1)
        Geostat_grid.addWidget(geostat_struct_combo, 2, 1, 1, 2)
        Geostat_grid.addWidget(Param_groupbox, 3, 0, 1, 3)
        Geostat_grid.addWidget(Nug_groupbox, 4, 0, 1, 3)
        Geostat_grid.setRowStretch(3, 100)
        Geostat_groupbox.setLayout(Geostat_grid)

        #--- Number of Iteration Groupbox ---#
        Iter_num_groupbox = QtGui.QGroupBox("Number of Iterations")
        Iter_num_grid = QtGui.QGridLayout()
        Iter_num_grid.addWidget(straight_ray_label, 0, 0)
        Iter_num_grid.addWidget(straight_ray_edit, 0, 1)
        Iter_num_grid.addWidget(curv_ray_label, 0, 2)
        Iter_num_grid.addWidget(curv_ray_edit, 0, 3)
        Iter_num_groupbox.setLayout(Iter_num_grid)

        #--- Inversion Parameters Groupbox ---#
        Inv_Param_groupbox = QtGui.QGroupBox(" Inversion Parameters")
        Inv_Param_grid = QtGui.QGridLayout()
        Inv_Param_grid.addWidget(Sub_algo_Widget, 0, 0)
        Inv_Param_grid.addWidget(Iter_num_groupbox, 1, 0, 1, 3)
        Inv_Param_grid.addWidget(Geostat_groupbox, 2, 0, 1, 3)
        Inv_Param_grid.addWidget(btn_GO, 3, 1)
        Inv_Param_groupbox.setLayout(Inv_Param_grid)

        #--- Figures Groupbox ---#
        fig_groupbox = QtGui.QGroupBox("Figures")
        fig_grid = QtGui.QGridLayout()
        fig_grid.addWidget(set_color_checkbox, 0, 0)
        fig_grid.addWidget(Min_labeli, 0, 1)
        fig_grid.addWidget(Min_editi, 0, 2)
        fig_grid.addWidget(Max_labeli, 0, 3)
        fig_grid.addWidget(Max_editi, 0, 4)
        fig_grid.addWidget(fig_combo, 0, 5)
        fig_groupbox.setLayout(fig_grid)

        #--- Figure Groupbox dependent SubWidget ---#
        Sub_right_Widget = QtGui.QWidget()
        Sub_right_Grid = QtGui.QGridLayout()
        Sub_right_Grid.addWidget(fig_groupbox, 0, 0)
        Sub_right_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_right_Widget.setLayout(Sub_right_Grid)

        #------- Master Grid Disposition -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(data_groupbox, 0, 0, 3, 1)
        master_grid.addWidget(Grid_groupbox, 3, 0)
        master_grid.addWidget(prev_inv_groupbox, 4, 0)
        master_grid.addWidget(Inv_Param_groupbox, 5, 0, 6, 1)
        master_grid.addWidget(Sub_right_Widget, 0, 1)
        master_grid.addWidget(futur_Graph1, 1, 1, 10, 2)
        master_grid.setColumnStretch(2, 300)
        master_grid.setRowStretch(8, 100)
        self.setLayout(master_grid)
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = InversionUI()
    Model_ui.show()

    sys.exit(app.exec_())

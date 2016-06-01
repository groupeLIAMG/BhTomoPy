# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from manual_ttUI import OpenMainData

class SemiAutottUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SemiAutottUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Semi Automatic Traveltime Picking")
        self.openmain = OpenMainData()
        self.initUI()

    def initUI(self):

        #--- Class for alignment ---#
        class  MyQLabel(QtGui.QLabel):
            def __init__(self, label, ha='left',  parent=None):
                super(MyQLabel, self).__init__(label,parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)

        #------ Creation of the Manager for the Upper figure -------#
        self.Fig = Fig()
        self.tool = NavigationToolbar2QT(self.Fig, self)
        self.manager = QtGui.QWidget()
        managergrid = QtGui.QGridLayout()
        managergrid.addWidget(self.tool, 0, 0)
        managergrid.addWidget(self.Fig, 1, 0)
        managergrid.setContentsMargins(0, 0, 0, 0)
        managergrid.setVerticalSpacing(3)
        self.manager.setLayout(managergrid)
        #------- Widgets -------#
        #--- Labels ---#
        Z_min_label                     = MyQLabel(('Z min'), ha= 'center')
        Z_max_label                     = MyQLabel(('Z max'), ha= 'center')
        Tx_label                        = MyQLabel(('Tx'), ha= 'center')
        Rx_label                        = MyQLabel(('Rx'), ha= 'center')
        self.percent_label              = MyQLabel((''), ha= 'center')
        Bin_label                       = MyQLabel(('Bin width [°]'), ha= 'center')
        self.bin_value_label            = MyQLabel(('0'), ha= 'center')
        sn_treshold_process_label       = MyQLabel(('S/N treshold - 1st Cycle processing'), ha= 'right')
        treshold_label                  = MyQLabel(('Selection treshold, 1st Cycle'), ha= 'right')
        weight_label                    = MyQLabel(('Weight - Traces 1st Cycle'), ha= 'right')
        sn_treshold_freq_label          = MyQLabel(('S/N treshold - Dom freq scaling'), ha= 'right')
        Dom_freq_min_label              = MyQLabel(('Dom freq - acceptable min freq'), ha= 'right')
        Dom_freq_max_label              = MyQLabel(('Dom freq - acceptable max freq'), ha= 'right')
        iteration_label                 = MyQLabel(('Iteration No'), ha= 'center')
        self.iteration_num_label        = MyQLabel(('0'), ha= 'center')
        t_label                         = MyQLabel(('t   '), ha= 'right')
        t_min_label                     = MyQLabel(('min'), ha= 'center')
        t_max_label                     = MyQLabel(('max'), ha= 'center')
        A_label                         = MyQLabel(('A   '), ha= 'right')
        A_min_label                     = MyQLabel(('min'), ha= 'center')
        A_max_label                     = MyQLabel(('max'), ha= 'center')
        computation_label               = MyQLabel(('Window - S/N computation'), ha= 'right')
        self.time_units_label           = MyQLabel(('[]'), ha= 'center')

        #--- Edits ---#
        self.Tx_Zmin_edit               = QtGui.QLineEdit()
        self.Tx_Zmax_edit               = QtGui.QLineEdit()
        self.Rx_Zmin_edit               = QtGui.QLineEdit()
        self.Rx_Zmax_edit               = QtGui.QLineEdit()
        self.bin_width_edit             = QtGui.QLineEdit()
        self.sn_treshold_process_edit   = QtGui.QLineEdit()
        self.treshold_edit              = QtGui.QLineEdit()
        self.weight_edit                = QtGui.QLineEdit()
        self.sn_treshold_freq_edit      = QtGui.QLineEdit()
        self.Dom_freq_min_edit          = QtGui.QLineEdit()
        self.Dom_freq_max_edit          = QtGui.QLineEdit()
        self.t_min_edit                 = QtGui.QLineEdit()
        self.t_max_edit                 = QtGui.QLineEdit()
        self.A_min_edit                 = QtGui.QLineEdit()
        self.A_max_edit                 = QtGui.QLineEdit()
        self.time_step_edit             = QtGui.QLineEdit()

        #- Edits Dispotion -#
        self.Tx_Zmin_edit.setFixedWidth(80)
        self.Tx_Zmax_edit.setFixedWidth(80)
        self.Rx_Zmin_edit.setFixedWidth(80)
        self.Rx_Zmax_edit.setFixedWidth(80)
        self.bin_width_edit.setFixedWidth(80)
        self.t_min_edit.setFixedWidth(50)
        self.t_max_edit.setFixedWidth(50)
        self.A_min_edit.setFixedWidth(50)
        self.A_max_edit.setFixedWidth(50)
        self.time_step_edit.setFixedWidth(50)
        self.sn_treshold_process_edit.setFixedWidth(50)
        self.treshold_edit.setFixedWidth(50)
        self.weight_edit.setFixedWidth(50)
        self.sn_treshold_freq_edit.setFixedWidth(50)
        self.Dom_freq_min_edit.setFixedWidth(50)
        self.Dom_freq_max_edit.setFixedWidth(50)

        #--- Buttons ---#
        self.btn_prev_bin               = QtGui.QPushButton('Previous')
        self.btn_next_bin               = QtGui.QPushButton('Next')
        self.btn_prep                   = QtGui.QPushButton('Prepare')
        self.btn_show                   = QtGui.QPushButton('Show')
        self.btn_remove                 = QtGui.QPushButton('Remove')
        self.btn_reinit                 = QtGui.QPushButton('Reinit')
        self.btn_align                  = QtGui.QPushButton('Align Traces')
        self.btn_pick                   = QtGui.QPushButton('Pick mean Trace')
        self.btn_corr                   = QtGui.QPushButton('Pick Traces using Cross correlation')
        #--- Action for Menubar ---#
        saveAction = QtGui.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')

        chooseAction = QtGui.QAction('Choose MOG', self)
        chooseAction.setShortcut('Ctrl+O')
        chooseAction.triggered.connect(self.openmain.show)

        reiniAction = QtGui.QAction('Reinitialize', self)

        usedetrendAction = QtGui.QAction('Use Detrend', self)
        usedetrendAction.setCheckable(True)
        usedetrendAction.setChecked(True)

        alignAction = QtGui.QAction('Align Traces', self)
        alignAction.setShortcut('Ctrl+A')

        pointAction = QtGui.QAction('Point the average Trace', self)
        pointAction.setShortcut('Ctrl+P')

        prevAction = QtGui.QAction(' Previous Group', self)
        prevAction.setShortcut('Ctrl+P')

        nextAction = QtGui.QAction('Next Group', self)
        nextAction.setShortcut('Ctrl+F')

        averAction = QtGui.QAction('Show average Traces', self)

        #--- Menubar ---#
        self.menu = QtGui.QMenuBar()

        #- Menus -#
        filemenu = self.menu.addMenu('&File')
        editmenu = self.menu.addMenu('&Edit')
        actionmenu = self.menu.addMenu('&Action')

        # Menus Actions #
        filemenu.addAction(chooseAction)
        filemenu.addAction(saveAction)

        editmenu.addAction(reiniAction)
        editmenu.addAction(usedetrendAction)

        actionmenu.addAction(alignAction)
        actionmenu.addAction(pointAction)
        actionmenu.addAction(prevAction)
        actionmenu.addAction(nextAction)

        #--- Checkboxes ---#
        self.work_check                 = QtGui.QCheckBox('Work with 1st Cycle')
        self.dom_freq_check             = QtGui.QCheckBox('Dominant frequency scaling')
        self.orig_check                 = QtGui.QCheckBox('Display original Traces')
        self.show_check                 = QtGui.QCheckBox('Show Picks')


        #------- SubWidgets -------#
        #--- Edits and Labels SubWidget ---#
        Sub_E_and_L_widget = QtGui.QWidget()
        Sub_E_and_L_grid = QtGui.QGridLayout()
        Sub_E_and_L_grid.addWidget(sn_treshold_process_label, 0, 1)
        Sub_E_and_L_grid.addWidget(self.sn_treshold_process_edit, 0, 2)
        Sub_E_and_L_grid.addWidget(treshold_label, 1, 1)
        Sub_E_and_L_grid.addWidget(self.treshold_edit, 1, 2)
        Sub_E_and_L_grid.addWidget(weight_label, 2, 1)
        Sub_E_and_L_grid.addWidget(self.weight_edit, 2, 2)
        Sub_E_and_L_grid.addWidget(sn_treshold_freq_label, 3, 1)
        Sub_E_and_L_grid.addWidget(self.sn_treshold_freq_edit, 3, 2)
        Sub_E_and_L_grid.addWidget(Dom_freq_min_label, 4, 1)
        Sub_E_and_L_grid.addWidget(self.Dom_freq_min_edit, 4, 2)
        Sub_E_and_L_grid.addWidget(Dom_freq_max_label, 5, 1)
        Sub_E_and_L_grid.addWidget(self.Dom_freq_max_edit, 5, 2)
        Sub_E_and_L_grid.setVerticalSpacing(0)
        Sub_E_and_L_grid.setContentsMargins(0, 0, 0, 0)
        Sub_E_and_L_grid.setColumnStretch(0, 100)
        Sub_E_and_L_widget.setFixedWidth(250)
        Sub_E_and_L_widget.setLayout(Sub_E_and_L_grid)

        #--- Lower Buttons SubWidget ---#
        Sub_lower_widget = QtGui.QWidget()
        Sub_lower_grid = QtGui.QGridLayout()
        Sub_lower_grid.addWidget(self.btn_show, 0, 0)
        Sub_lower_grid.addWidget(self.btn_remove, 0, 1)
        Sub_lower_grid.addWidget(self.btn_reinit, 0, 2)
        Sub_lower_grid.setHorizontalSpacing(3)
        Sub_lower_grid.setContentsMargins(0, 0, 0, 0)
        Sub_lower_widget.setLayout(Sub_lower_grid)

        #--- trace SubWidget ---#
        Sub_trace_widget = QtGui.QWidget()
        Sub_trace_grid = QtGui.QGridLayout()
        Sub_trace_grid.addWidget(self.btn_align, 0, 0)
        Sub_trace_grid.addWidget(iteration_label, 0, 1)
        Sub_trace_grid.addWidget(self.iteration_num_label, 0, 2)
        Sub_trace_grid.addWidget(self.btn_pick, 1, 0, 1, 3)
        Sub_trace_grid.setContentsMargins(0, 0, 0, 0)
        Sub_trace_widget.setLayout(Sub_trace_grid)

        #--- Time and Amplitude Subwidget ---#
        Sub_T_and_A_widget = QtGui.QWidget()
        Sub_T_and_A_grid = QtGui.QGridLayout()
        Sub_T_and_A_grid.addWidget(t_min_label, 0, 1)
        Sub_T_and_A_grid.addWidget(t_max_label, 0, 2)
        Sub_T_and_A_grid.addWidget(A_min_label, 0, 4)
        Sub_T_and_A_grid.addWidget(A_max_label, 0, 5)
        Sub_T_and_A_grid.addWidget(t_label, 1, 0)
        Sub_T_and_A_grid.addWidget(self.t_min_edit, 1, 1)
        Sub_T_and_A_grid.addWidget(self.t_max_edit, 1, 2)
        Sub_T_and_A_grid.addWidget(A_label, 1, 3)
        Sub_T_and_A_grid.addWidget(self.A_min_edit, 1, 4)
        Sub_T_and_A_grid.addWidget(self.A_max_edit, 1, 5)
        Sub_T_and_A_grid.addWidget(computation_label, 2, 1, 1, 3)
        Sub_T_and_A_grid.addWidget(self.time_units_label, 2, 4)
        Sub_T_and_A_grid.addWidget(self.time_step_edit, 2, 5)
        Sub_T_and_A_grid.setHorizontalSpacing(5)
        Sub_T_and_A_grid.setContentsMargins(0, 0, 0, 0)
        Sub_T_and_A_widget.setLayout(Sub_T_and_A_grid)


        #------- GroupBoxes --------#
        #--- Station GroupBox ---#
        station_group = QtGui.QGroupBox('Stations Tx-Rx')
        station_grid = QtGui.QGridLayout()
        station_grid.addWidget(Tx_label, 0, 1)
        station_grid.addWidget(Rx_label, 0, 2)
        station_grid.addWidget(Z_min_label, 1, 0)
        station_grid.addWidget(self.Tx_Zmin_edit, 1, 1)
        station_grid.addWidget(self.Rx_Zmin_edit, 1, 2)
        station_grid.addWidget(self.percent_label, 1, 3)
        station_grid.addWidget(Z_max_label, 2, 0)
        station_grid.addWidget(self.Tx_Zmax_edit, 2, 1)
        station_grid.addWidget(self.Rx_Zmax_edit, 2, 2)
        station_group.setLayout(station_grid)
        station_group.setFixedWidth(300)

        #--- Bin GroupBox ---#
        bin_group = QtGui.QGroupBox('Bin')
        bin_grid = QtGui.QGridLayout()
        bin_grid.addWidget(Bin_label, 0, 0)
        bin_grid.addWidget(self.bin_width_edit, 0, 1)
        bin_grid.addWidget(self.btn_prev_bin, 1, 0)
        bin_grid.addWidget(self.bin_value_label, 1, 1)
        bin_grid.addWidget(self.btn_next_bin, 1, 2)
        bin_group.setLayout(bin_grid)
        bin_group.setFixedWidth(300)

        #--- No Name GroupBox ---#
        no_group = QtGui.QGroupBox()
        no_grid = QtGui.QGridLayout()
        no_grid.addWidget(self.work_check, 0, 0)
        no_grid.addWidget(self.dom_freq_check, 1, 0)
        no_grid.addWidget(self.orig_check, 2, 0)
        no_grid.addWidget(self.btn_prep, 3, 0)
        no_grid.addWidget(Sub_E_and_L_widget, 4, 0)
        no_grid.addWidget(Sub_lower_widget, 5, 0)
        no_group.setLayout(no_grid)

        #--- Traces GroupBox ---#
        traces_group = QtGui.QGroupBox('Traces')
        traces_grid = QtGui.QGridLayout()
        traces_grid.addWidget(no_group, 0, 0)
        traces_grid.addWidget(Sub_trace_widget, 1, 0)
        traces_grid.addWidget(Sub_T_and_A_widget, 2, 0)
        traces_group.setLayout(traces_grid)
        traces_group.setFixedWidth(300)

        #--- Automatic Picking GroupBox ---#
        auto_group = QtGui.QGroupBox('Automatic Picking')
        auto_grid = QtGui.QGridLayout()
        auto_grid.addWidget(self.show_check, 0, 0)
        auto_grid.addWidget(self.btn_pick, 1, 0, 1, 2)
        auto_group.setLayout(auto_grid)
        auto_group.setFixedWidth(300)



        #------- Master Grid -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0, 1, 5)
        master_grid.addWidget(self.manager, 1, 0, 5, 4)
        master_grid.addWidget(station_group, 2, 4)
        master_grid.addWidget(bin_group, 3, 4)
        master_grid.addWidget(traces_group, 4, 4)
        master_grid.addWidget(auto_group, 5, 4)
        master_grid.setColumnStretch(0, 100)
        #master_grid.addWidget(traces_group)
        self.setLayout(master_grid)

class Fig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(facecolor= 'white')
        super(Fig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        ax1 = self.figure.add_axes([0.08, 0.45, 0.85, 0.5])
        ax2 = self.figure.add_axes([0.08, 0.06, 0.85, 0.3])
        ax1.yaxis.set_ticks_position('left')
        ax1.set_axisbelow(True)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Semi_ui = SemiAutottUI()
    Semi_ui.show()

    sys.exit(app.exec_())
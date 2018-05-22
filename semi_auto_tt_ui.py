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
from PyQt5 import QtWidgets, QtCore
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from utils_ui import MyQLabel

class SemiAutottUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SemiAutottUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Semi Automatic Traveltime Picking")
        self.init_UI()

    def init_UI(self):

        # ------ Creation of the Manager for the Upper figure ------- #
        self.Fig = Fig()
        self.tool = NavigationToolbar2QT(self.Fig, self)
        self.manager = QtWidgets.QWidget()
        managergrid = QtWidgets.QGridLayout()
        managergrid.addWidget(self.tool, 0, 0)
        managergrid.addWidget(self.Fig, 1, 0)
        managergrid.setContentsMargins(0, 0, 0, 0)
        managergrid.setVerticalSpacing(3)
        self.manager.setLayout(managergrid)
        # ------- Widgets ------- #
        # --- Labels --- #
        Z_min_label                     = MyQLabel(('Z min'), ha='center')
        Z_max_label                     = MyQLabel(('Z max'), ha='center')
        Tx_label                        = MyQLabel(('Tx'), ha='center')
        Rx_label                        = MyQLabel(('Rx'), ha='center')
        self.percent_label              = MyQLabel((''), ha='center')
        Bin_label                       = MyQLabel(('Bin width [°]'), ha='center')
        self.bin_value_label            = MyQLabel(('0'), ha='center')
        sn_threshold_process_label      = MyQLabel(('S/N threshold - 1st Cycle processing'), ha='right')
        threshold_label                 = MyQLabel(('Selection threshold, 1st Cycle'), ha='right')
        weight_label                    = MyQLabel(('Weight - Traces 1st Cycle'), ha='right')
        sn_threshold_freq_label         = MyQLabel(('S/N threshold - Dom freq scaling'), ha='right')
        Dom_freq_min_label              = MyQLabel(('Dom freq - acceptable min freq'), ha='right')
        Dom_freq_max_label              = MyQLabel(('Dom freq - acceptable max freq'), ha='right')
        iteration_label                 = MyQLabel(('Iteration No'), ha='center')
        self.iteration_num_label        = MyQLabel(('0'), ha='center')
        t_label                         = MyQLabel(('t   '), ha='right')
        t_min_label                     = MyQLabel(('min'), ha='center')
        t_max_label                     = MyQLabel(('max'), ha='center')
        A_label                         = MyQLabel(('A   '), ha='right')
        A_min_label                     = MyQLabel(('min'), ha='center')
        A_max_label                     = MyQLabel(('max'), ha='center')
        computation_label               = MyQLabel(('Window - S/N computation'), ha='right')
        self.time_units_label           = MyQLabel(('[]'), ha='center')

        # --- Edits --- #
        self.Tx_Zmin_edit               = QtWidgets.QLineEdit()
        self.Tx_Zmax_edit               = QtWidgets.QLineEdit()
        self.Rx_Zmin_edit               = QtWidgets.QLineEdit()
        self.Rx_Zmax_edit               = QtWidgets.QLineEdit()
        self.bin_width_edit             = QtWidgets.QLineEdit()
        self.sn_threshold_process_edit  = QtWidgets.QLineEdit()
        self.threshold_edit             = QtWidgets.QLineEdit()
        self.weight_edit                = QtWidgets.QLineEdit()
        self.sn_threshold_freq_edit     = QtWidgets.QLineEdit()
        self.Dom_freq_min_edit          = QtWidgets.QLineEdit()
        self.Dom_freq_max_edit          = QtWidgets.QLineEdit()
        self.t_min_edit                 = QtWidgets.QLineEdit()
        self.t_max_edit                 = QtWidgets.QLineEdit()
        self.A_min_edit                 = QtWidgets.QLineEdit()
        self.A_max_edit                 = QtWidgets.QLineEdit()
        self.time_step_edit             = QtWidgets.QLineEdit()

        # - Edits Dispotion - #
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
        self.sn_threshold_process_edit.setFixedWidth(50)
        self.threshold_edit.setFixedWidth(50)
        self.weight_edit.setFixedWidth(50)
        self.sn_threshold_freq_edit.setFixedWidth(50)
        self.Dom_freq_min_edit.setFixedWidth(50)
        self.Dom_freq_max_edit.setFixedWidth(50)

        # --- Buttons --- #
        self.btn_prev_bin               = QtWidgets.QPushButton('Previous')
        self.btn_next_bin               = QtWidgets.QPushButton('Next')
        self.btn_prep                   = QtWidgets.QPushButton('Prepare')
        self.btn_show                   = QtWidgets.QPushButton('Show')
        self.btn_remove                 = QtWidgets.QPushButton('Remove')
        self.btn_reinit                 = QtWidgets.QPushButton('Reinit')
        self.btn_align                  = QtWidgets.QPushButton('Align Traces')
        self.btn_pick                   = QtWidgets.QPushButton('Pick mean Trace')
        self.btn_corr                   = QtWidgets.QPushButton('Pick Traces using Cross correlation')
        # --- Action for Menubar --- #
        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')

        chooseAction = QtWidgets.QAction('Choose MOG', self)
        chooseAction.setShortcut('Ctrl+O')
#         chooseAction.triggered.connect(self.openmain.show)

        reiniAction = QtWidgets.QAction('Reinitialize', self)

        usedetrendAction = QtWidgets.QAction('Use Detrend', self)
        usedetrendAction.setCheckable(True)
        usedetrendAction.setChecked(True)

        alignAction = QtWidgets.QAction('Align Traces', self)
        alignAction.setShortcut('Ctrl+A')

        pointAction = QtWidgets.QAction('Point the average Trace', self)
        pointAction.setShortcut('Ctrl+P')

        prevAction  = QtWidgets.QAction('Previous Group', self)
        prevAction.setShortcut('Ctrl+P')

        nextAction  = QtWidgets.QAction('Next Group', self)
        nextAction.setShortcut('Ctrl+F')

        averAction  = QtWidgets.QAction('Show average Traces', self)

        # --- Menubar --- #
        self.menu  = QtWidgets.QMenuBar()

        # - Menus - #
        filemenu    = self.menu.addMenu('&File')
        editmenu    = self.menu.addMenu('&Edit')
        actionmenu  = self.menu.addMenu('&Action')

        # - Menus Actions - #
        filemenu.addAction(chooseAction)
        filemenu.addAction(saveAction)

        editmenu.addAction(reiniAction)
        editmenu.addAction(usedetrendAction)

        actionmenu.addAction(alignAction)
        actionmenu.addAction(pointAction)
        actionmenu.addAction(prevAction)
        actionmenu.addAction(nextAction)
        actionmenu.addAction(nextAction)
        actionmenu.addAction(averAction)

        # --- Checkboxes --- #
        self.work_check             = QtWidgets.QCheckBox('Work with 1st Cycle')
        self.dom_freq_check         = QtWidgets.QCheckBox('Dominant frequency scaling')
        self.orig_check             = QtWidgets.QCheckBox('Display original Traces')
        self.show_check             = QtWidgets.QCheckBox('Show Picks')

        # ------- SubWidgets ------- #
        # --- Edits and Labels SubWidget --- #
        Sub_E_and_L_widget = QtWidgets.QWidget()
        Sub_E_and_L_grid = QtWidgets.QGridLayout()
        Sub_E_and_L_grid.addWidget(sn_threshold_process_label, 0, 1)
        Sub_E_and_L_grid.addWidget(self.sn_threshold_process_edit, 0, 2)
        Sub_E_and_L_grid.addWidget(threshold_label, 1, 1)
        Sub_E_and_L_grid.addWidget(self.threshold_edit, 1, 2)
        Sub_E_and_L_grid.addWidget(weight_label, 2, 1)
        Sub_E_and_L_grid.addWidget(self.weight_edit, 2, 2)
        Sub_E_and_L_grid.addWidget(sn_threshold_freq_label, 3, 1)
        Sub_E_and_L_grid.addWidget(self.sn_threshold_freq_edit, 3, 2)
        Sub_E_and_L_grid.addWidget(Dom_freq_min_label, 4, 1)
        Sub_E_and_L_grid.addWidget(self.Dom_freq_min_edit, 4, 2)
        Sub_E_and_L_grid.addWidget(Dom_freq_max_label, 5, 1)
        Sub_E_and_L_grid.addWidget(self.Dom_freq_max_edit, 5, 2)
        Sub_E_and_L_grid.setVerticalSpacing(0)
        Sub_E_and_L_grid.setContentsMargins(0, 0, 0, 0)
        Sub_E_and_L_grid.setColumnStretch(0, 100)
        Sub_E_and_L_widget.setFixedWidth(250)
        Sub_E_and_L_widget.setLayout(Sub_E_and_L_grid)

        # --- Lower Buttons SubWidget --- #
        Sub_lower_widget = QtWidgets.QWidget()
        Sub_lower_grid = QtWidgets.QGridLayout()
        Sub_lower_grid.addWidget(self.btn_show, 0, 0)
        Sub_lower_grid.addWidget(self.btn_remove, 0, 1)
        Sub_lower_grid.addWidget(self.btn_reinit, 0, 2)
        Sub_lower_grid.setHorizontalSpacing(3)
        Sub_lower_grid.setContentsMargins(0, 0, 0, 0)
        Sub_lower_widget.setLayout(Sub_lower_grid)

        # --- trace SubWidget --- #
        Sub_trace_widget = QtWidgets.QWidget()
        Sub_trace_grid = QtWidgets.QGridLayout()
        Sub_trace_grid.addWidget(self.btn_align, 0, 0)
        Sub_trace_grid.addWidget(iteration_label, 0, 1)
        Sub_trace_grid.addWidget(self.iteration_num_label, 0, 2)
        Sub_trace_grid.addWidget(self.btn_pick, 1, 0, 1, 3)
        Sub_trace_grid.setContentsMargins(0, 0, 0, 0)
        Sub_trace_widget.setLayout(Sub_trace_grid)

        # --- Time and Amplitude Subwidget --- #
        Sub_T_and_A_widget = QtWidgets.QWidget()
        Sub_T_and_A_grid = QtWidgets.QGridLayout()
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

        # ------- GroupBoxes -------- #
        # --- Station GroupBox --- #
        station_group = QtWidgets.QGroupBox('Stations Tx-Rx')
        station_grid = QtWidgets.QGridLayout()
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

        # --- Bin GroupBox --- #
        bin_group = QtWidgets.QGroupBox('Bin')
        bin_grid = QtWidgets.QGridLayout()
        bin_grid.addWidget(Bin_label, 0, 0)
        bin_grid.addWidget(self.bin_width_edit, 0, 1)
        bin_grid.addWidget(self.btn_prev_bin, 1, 0)
        bin_grid.addWidget(self.bin_value_label, 1, 1)
        bin_grid.addWidget(self.btn_next_bin, 1, 2)
        bin_group.setLayout(bin_grid)
        bin_group.setFixedWidth(300)

        # --- No Name GroupBox --- #
        no_group = QtWidgets.QGroupBox()
        no_grid = QtWidgets.QGridLayout()
        no_grid.addWidget(self.work_check, 0, 0)
        no_grid.addWidget(self.dom_freq_check, 1, 0)
        no_grid.addWidget(self.orig_check, 2, 0)
        no_grid.addWidget(self.btn_prep, 3, 0)
        no_grid.addWidget(Sub_E_and_L_widget, 4, 0)
        no_grid.addWidget(Sub_lower_widget, 5, 0)
        no_group.setLayout(no_grid)

        # --- Traces GroupBox --- #
        traces_group = QtWidgets.QGroupBox('Traces')
        traces_grid = QtWidgets.QGridLayout()
        traces_grid.addWidget(no_group, 0, 0)
        traces_grid.addWidget(Sub_trace_widget, 1, 0)
        traces_grid.addWidget(Sub_T_and_A_widget, 2, 0)
        traces_group.setLayout(traces_grid)
        traces_group.setFixedWidth(300)

        # --- Automatic Picking GroupBox --- #
        auto_group = QtWidgets.QGroupBox('Automatic Picking')
        auto_grid = QtWidgets.QGridLayout()
        auto_grid.addWidget(self.show_check, 0, 0)
        auto_grid.addWidget(self.btn_pick, 1, 0, 1, 2)
        auto_group.setLayout(auto_grid)
        auto_group.setFixedWidth(300)

        # ------- Master Grid ------- #
        master_grid = QtWidgets.QGridLayout()
        master_grid.addWidget(self.menu, 0, 0, 1, 5)
        master_grid.addWidget(self.manager, 1, 0, 5, 4)
        master_grid.addWidget(station_group, 2, 4)
        master_grid.addWidget(bin_group, 3, 4)
        master_grid.addWidget(traces_group, 4, 4)
        master_grid.addWidget(auto_group, 5, 4)
        master_grid.setColumnStretch(0, 100)
        master_grid.setVerticalSpacing(0)
        master_grid.setContentsMargins(0, 0, 0, 0)
        self.setLayout(master_grid)


class Fig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(facecolor='white')
        super(Fig, self).__init__(fig)
        self.init_figure()

    def init_figure(self):
        ax1 = self.figure.add_axes([0.08, 0.45, 0.85, 0.5])
        ax2 = self.figure.add_axes([0.08, 0.06, 0.85, 0.3])
        ax1.yaxis.set_ticks_position('left')
        ax1.set_axisbelow(True)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    Semi_ui = SemiAutottUI()
    Semi_ui.show()

    sys.exit(app.exec_())

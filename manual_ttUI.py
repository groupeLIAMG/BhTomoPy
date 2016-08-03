# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
import pickle
import numpy as np
import re




class ManualttUI(QtGui.QFrame):
    KeyPressed = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(ManualttUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Manual Traveltime Picking")
        self.openmain = OpenMainData(self)
        self.mogs = []
        self.air = []
        self.boreholes = []
        self.models = []
        self.filename = ''
        self.mog = 0
        self.initUI()

        self.upperFig.UpperTracePickedSignal.connect(self.lowerFig.plot_trace_data)
        self.upperFig.UpperTracePickedSignal.connect(self.update_control_center)
        self.lowerFig.LowerTracePickedSignal.connect(self.upperFig.plot_amplitude)
        self.lowerFig.LowerTracePickedSignal.connect(self.update_control_center)
        #self.KeyPressed.connect(self.onkey)


    def next_trace(self):
        n = int(self.Tnum_Edit.text())
        n += 1
        if self.main_data_radio.isChecked():
            self.mog.tt_done[n-2] = 1
        elif self.t0_before_radio.isChecked():
            self.air[self.mog.av].tt_done[n-2] = 1
        elif self.t0_after_radio.isChecked():
            self.air[self.mog.ap].tt_done[n-2] = 1

        self.Tnum_Edit.setText(str(n))
        self.update_control_center()

    def prev_trace(self):
        n = int(self.Tnum_Edit.text())
        n -= 1
        self.Tnum_Edit.setText(str(n))
        self.update_control_center()

    def update_control_center(self):
        n = int(self.Tnum_Edit.text())-1

        ind = self.openmain.mog_combo.currentIndex()
        self.mog = self.mogs[ind]
        airshot_before = self.air[self.mog.av]
        airshot_after = self.air[self.mog.ap]
        if len(self.mogs) == 0:
            return
        else:
            if self.main_data_radio.isChecked():
                done = np.round(len(self.mog.tt[self.mog.tt != -1])/len(self.mog.tt) * 100)
                self.xRx_label.setText(str(self.mog.data.Rx_x[n]))
                self.xTx_label.setText(str(self.mog.data.Tx_x[n]))
                self.yRx_label.setText(str(self.mog.data.Rx_y[n]))
                self.yTx_label.setText(str(self.mog.data.Tx_y[n]))
                self.zRx_label.setText(str(np.round(self.mog.data.Rx_z[n], 3)))
                self.zTx_label.setText(str(self.mog.data.Tx_z[n]))
                self.ntrace_label.setText(str(self.mog.data.ntrace))
                self.percent_done_label.setText(str(done))
                self.time.setText(str(np.round(self.mog.tt[n], 4)))
                self.incertitude_value_label.setText(str(np.round(self.mog.et[n], 4)))

            if self.t0_before_radio.isChecked():
                done = np.round(len(airshot_before.tt[airshot_before.tt != -1])/len(airshot_before.tt) * 100)
                self.xRx_label.setText(str(airshot_before.data.Rx_x[n]))
                self.xTx_label.setText(str(airshot_before.data.Tx_x[n]))
                self.yRx_label.setText(str(airshot_before.data.Rx_y[n]))
                self.yTx_label.setText(str(airshot_before.data.Tx_y[n]))
                self.zRx_label.setText(str(np.round(airshot_before.data.Rx_z[n], 3)))
                self.zTx_label.setText(str(airshot_before.data.Tx_z[n]))
                self.ntrace_label.setText(str(airshot_before.data.ntrace))
                self.percent_done_label.setText(str(done))
                self.time.setText(str(np.round(airshot_before.tt[n], 4)))
                self.incertitude_value_label.setText(str(np.round(airshot_before.et[n], 4)))

            if self.t0_after_radio.isChecked():
                done = np.round(len(airshot_after.tt[airshot_after.tt != -1])/len(airshot_after.tt) * 100)
                self.xRx_label.setText(str(airshot_after.data.Rx_x[n]))
                self.xTx_label.setText(str(airshot_after.data.Tx_x[n]))
                self.yRx_label.setText(str(airshot_after.data.Rx_y[n]))
                self.yTx_label.setText(str(airshot_after.data.Tx_y[n]))
                self.zRx_label.setText(str(np.round(airshot_after.data.Rx_z[n], 3)))
                self.zTx_label.setText(str(airshot_after.data.Tx_z[n]))
                self.ntrace_label.setText(str(airshot_after.data.ntrace))
                self.percent_done_label.setText(str(done))
                self.time.setText(str(np.round(airshot_after.tt[n], 4)))
                self.incertitude_value_label.setText(str(np.round(airshot_after.et[n], 4)))

        self.check_save()
        self.upperFig.plot_amplitude()
        self.lowerFig.plot_trace_data()

    def update_a_and_t_edits(self):
        n = int(self.Tnum_Edit.text())
        ind = self.openmain.mog_combo.currentIndex()
        mog = self.mogs[ind]
        if self.lim_checkbox.isChecked():
            A_max = max(mog.data.rdata[:, n].flatten())
            A_min = min(mog.data.rdata[:, n].flatten())

            self.A_min_Edit.setText(str(A_min))
            self.A_max_Edit.setText(str(A_max))
        else:
            self.A_min_Edit.setText(str(-1000))
            self.A_max_Edit.setText(str(1000))
            self.t_min_Edit.setText(str(0))
            self.t_max_Edit.setText(str(int(np.round(self.mog.data.timestp[-1]))))

    def reinit_trace(self):
        n = int(self.Tnum_Edit.text()) - 1
        if self.main_data_radio.isChecked():
            self.mog.tt[n] = -1.0
            self.mog.et[n] = -1.0
            self.mog.tt_done[n] = -1.0
        if self.t0_before_radio.isChecked():
            self.air[self.mog.av].tt[n] = -1.0
            self.air[self.mog.av].et[n] = -1.0
            self.air[self.mog.av].tt_done[n] = -1.0
        if self.t0_after_radio.isChecked():
            self.air[self.mog.ap].tt[n] = -1.0
            self.air[self.mog.ap].et[n] = -1.0
            self.air[self.mog.ap].tt_done[n] = -1.0
        self.update_control_center()

    def next_trace_to_pick(self):
        ind = np.where(self.mog.tt_done == 0)[0]
        to_pick = ind[0] + 1
        self.Tnum_Edit.setText(str(to_pick))
        self.update_control_center()

    def check_save(self):
        if self.save_checkbox.isChecked():
            self.intermediate_saves()

    def intermediate_saves(self):
        if float(self.Tnum_Edit.text()) % 50 == 0:
            save_file = open(self.filename, 'wb')
            pickle.dump((self.boreholes, self.mogs, self.air, self.models), save_file)
            print('saved')

    def reinit_tnum(self):
        self.Tnum_Edit.setText('1')

    def plot_stats(self):
        ind = self.openmain.mog_combo.currentIndex()
        mog = self.mogs[ind]
        self.statsFig1 = StatsFig1()
        self.statsFig1.plot_stats(mog, self.air)
        self.statsFig1.showMaximized()

    def savefile(self):
        save_file = open(self.filename, 'wb')
        pickle.dump((self.boreholes, self.mogs, self.air, self.models), save_file)
        dialog = QtGui.QMessageBox.information(self, 'Success', "Database was saved successfully"
                                                ,buttons=QtGui.QMessageBox.Ok)

    def import_tt_file(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Import')
        self.load_tt_file(filename)
    def load_tt_file(self, filename):
        try:
            file = open(filename, 'r')
        except:
            try:
                file = open(filename + ".dat", 'r')
            except:
                try:
                    file = open(filename + ".DAT", 'r')
                except:
                    dialog = QtGui.QMessageBox.warning(self, 'Warning', "Could not import {} file".format(filename),buttons= QtGui.QMessageBox.Ok)

        info_tt = np.loadtxt(filename)
        for row in info_tt:
            trc_number = int(float(row[0]))
            tt = float(row[1])
            et = float(row[2])
            self.mog.tt_done[trc_number - 1] = 1
            self.mog.tt[trc_number - 1] = tt
            self.mog.et[trc_number - 1] = et


        self.update_control_center()


    def initUI(self):
        blue_palette = QtGui.QPalette()
        blue_palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkCyan)

        #------ Creation of the Manager for the Upper figure -------#
        self.upperFig = UpperFig(self)
        self.uppertool = NavigationToolbar2QT(self.upperFig, self)
        self.uppermanager = QtGui.QWidget()
        uppermanagergrid = QtGui.QGridLayout()
        uppermanagergrid.addWidget(self.uppertool, 0, 0)
        uppermanagergrid.addWidget(self.upperFig, 1, 0)
        uppermanagergrid.setContentsMargins(0, 0, 0, 0)
        uppermanagergrid.setVerticalSpacing(3)
        self.uppermanager.setLayout(uppermanagergrid)

        #------ Creation of the Manager for the Lower figure -------#
        self.lowerFig = LowerFig(self)
        self.lowermanager = QtGui.QWidget()
        lowermanagergrid = QtGui.QGridLayout()
        lowermanagergrid.addWidget(self.lowerFig, 0, 0)
        self.lowermanager.setLayout(lowermanagergrid)

        #------- Widgets Creation -------#
        #--- Buttons ---#
        btn_Prev = QtGui.QPushButton("Previous Trace")
        btn_Next = QtGui.QPushButton("Next Trace")
        btn_Next_Pick = QtGui.QPushButton("Next Trace to Pick")
        btn_Reini = QtGui.QPushButton("Reinitialize Trace")
        btn_Upper = QtGui.QPushButton("Activate Picking - Upper Trace")
        btn_Conti = QtGui.QPushButton("Activate Picking - Shot Gather")
        btn_Stats = QtGui.QPushButton("Statistics")

        #- Buttons' Actions -#
        btn_Next.clicked.connect(self.next_trace)
        btn_Prev.clicked.connect(self.prev_trace)
        btn_Upper.clicked.connect(self.upper_trace_isClicked)
        btn_Conti.clicked.connect(self.lower_trace_isClicked)
        btn_Stats.clicked.connect(self.plot_stats)
        btn_Reini.clicked.connect(self.reinit_trace)
        btn_Next_Pick.clicked.connect(self.next_trace_to_pick)

        #--- Label ---#
        trc_Label = MyQLabel("Trace number :", ha= 'right')
        t_min_label = MyQLabel("t min", ha= 'center')
        t_max_label = MyQLabel("t max", ha= 'center')
        A_min_label = MyQLabel("A min", ha= 'center')
        A_max_label = MyQLabel("A max", ha= 'center')
        position_label = MyQLabel(("Position Tx--Rx"), ha='center')
        x_label = MyQLabel("x", ha= 'center')
        y_label = MyQLabel("y", ha= 'center')
        z_label = MyQLabel("z", ha= 'center')
        Tx_label = MyQLabel("Tx:", ha= 'right')
        Rx_label = MyQLabel("Rx:", ha= 'right')
        done_label = MyQLabel('% Done', ha= 'left')
        self.xTx_label = MyQLabel("", ha= 'right')
        self.yTx_label = MyQLabel("", ha= 'right')
        self.zTx_label = MyQLabel("", ha= 'right')
        self.xRx_label = MyQLabel("", ha= 'right')
        self.yRx_label = MyQLabel("", ha= 'right')
        self.zRx_label = MyQLabel("", ha= 'right')
        self.ntrace_label = MyQLabel("", ha= 'right')
        self.percent_done_label = MyQLabel('', ha= 'right')
        trace_label = MyQLabel("traces", ha= 'left')
        picked_label = MyQLabel("Picked Time:", ha= 'right')
        self.time = QtGui.QLabel("")
        incertitude_label = QtGui.QLabel("±")
        self.incertitude_value_label = QtGui.QLabel("")

        #-- Setting Labels color ---#
        picked_label.setPalette(blue_palette)
        self.time.setPalette(blue_palette)
        incertitude_label.setPalette(blue_palette)
        self.incertitude_value_label.setPalette(blue_palette)

        #--- Actions ---#
        openAction = QtGui.QAction('Open main data file', self)
        openAction.triggered.connect(self.openmain.show)

        saveAction = QtGui.QAction('Save', self)
        saveAction.triggered.connect(self.savefile)

        importAction = QtGui.QAction('Import ...', self)
        importAction.triggered.connect(self.import_tt_file)
        #--- ToolBar ---#
        self.tool = QtGui.QMenuBar()
        filemenu = self.tool.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(importAction)

        #--- Edits ---#
        self.Tnum_Edit = QtGui.QLineEdit('1')
        self.t_min_Edit = QtGui.QLineEdit('0')
        self.t_max_Edit = QtGui.QLineEdit('300')
        self.A_min_Edit = QtGui.QLineEdit('-1000')
        self.A_max_Edit = QtGui.QLineEdit('1000')

        #- Edits' Disposition -#
        self.Tnum_Edit.setFixedWidth(100)
        self.Tnum_Edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.t_min_Edit.setFixedWidth(50)
        self.t_min_Edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.t_max_Edit.setFixedWidth(50)
        self.t_max_Edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.A_min_Edit.setFixedWidth(50)
        self.A_min_Edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.A_max_Edit.setFixedWidth(50)
        self.A_max_Edit.setAlignment(QtCore.Qt.AlignHCenter)

        #- Edits' Actions -#
        self.Tnum_Edit.editingFinished.connect(self.update_control_center)
        self.t_min_Edit.editingFinished.connect(self.upperFig.plot_amplitude)
        self.t_max_Edit.editingFinished.connect(self.upperFig.plot_amplitude)
        self.A_min_Edit.editingFinished.connect(self.upperFig.plot_amplitude)
        self.A_max_Edit.editingFinished.connect(self.upperFig.plot_amplitude)

        #--- Checkboxes ---#
        self.Wave_checkbox = QtGui.QCheckBox("Wavelet tranf. denoising")
        self.veloc_checkbox = QtGui.QCheckBox("Show apparent velocity")
        self.lim_checkbox = QtGui.QCheckBox("Dynamic amplitude limits")
        self.save_checkbox = QtGui.QCheckBox("Intermediate saves")
        self.jump_checkbox = QtGui.QCheckBox("Jump to next unpicked Trace")
        self.pick_checkbox = QtGui.QCheckBox("Pick Tx Data")
        self.pick_checkbox.setDisabled(True)

        #- CheckBoxes' Actions -#
        self.lim_checkbox.stateChanged.connect(self.update_a_and_t_edits)
        self.lim_checkbox.stateChanged.connect(self.upperFig.plot_amplitude)
        self.veloc_checkbox.stateChanged.connect(self.update_control_center)

        #--- Radio Buttons ---#
        self.main_data_radio = QtGui.QRadioButton("Main Data file")
        self.t0_before_radio = QtGui.QRadioButton("t0 Before")
        self.t0_after_radio = QtGui.QRadioButton("t0 After")
        self.tt_picking_radio = QtGui.QRadioButton("Traveltime picking")
        self.trace_selec_radio = QtGui.QRadioButton("Trace selection")

        #- Radio Buttons' Disposition -#
        self.main_data_radio.setChecked(True)
        #self.t0_before_radio.setChecked(True)
        self.tt_picking_radio.setChecked(True)

        #- Radio Buttons' Actions -#

        self.main_data_radio.toggled.connect(self.reinit_tnum)
        self.t0_before_radio.toggled.connect(self.reinit_tnum)
        self.t0_after_radio.toggled.connect(self.reinit_tnum)

        self.main_data_radio.toggled.connect(self.update_control_center)
        self.t0_before_radio.toggled.connect(self.update_control_center)
        self.t0_after_radio.toggled.connect(self.update_control_center)
        #--- Text Edits ---#
        info_Tedit = QtGui.QTextEdit()
        info_Tedit.setReadOnly(True)
        PTime_Tedit = QtGui.QTextEdit()
        PTime_Tedit.setReadOnly(True)

        #--- combobox ---#
        self.pick_combo = QtGui.QComboBox()
        self.pick_combo.addItem("Pick with std deviation")
        self.pick_combo.addItem("Simple Picking")

        #------- subWidgets -------#
        #--- Info Subwidget ---#
        Sub_Info_widget = QtGui.QWidget()
        Sub_Info_grid = QtGui.QGridLayout()
        Sub_Info_grid.addWidget(position_label, 0, 1, 1, 3)
        Sub_Info_grid.addWidget(x_label, 2, 1)
        Sub_Info_grid.addWidget(y_label, 2, 2)
        Sub_Info_grid.addWidget(z_label, 2, 3)
        Sub_Info_grid.addWidget(Tx_label, 3, 0)
        Sub_Info_grid.addWidget(self.xTx_label, 3, 1)
        Sub_Info_grid.addWidget(self.yTx_label, 3, 2)
        Sub_Info_grid.addWidget(self.zTx_label, 3, 3)
        Sub_Info_grid.addWidget(Rx_label, 4, 0)
        Sub_Info_grid.addWidget(self.xRx_label, 4, 1)
        Sub_Info_grid.addWidget(self.yRx_label, 4, 2)
        Sub_Info_grid.addWidget(self.zRx_label, 4, 3)
        Sub_Info_grid.addWidget(self.ntrace_label, 5, 1)
        Sub_Info_grid.addWidget(trace_label, 5, 2)
        Sub_Info_grid.addWidget(done_label, 6, 2)
        Sub_Info_grid.addWidget(self.percent_done_label, 6, 1)
        Sub_Info_widget.setLayout(Sub_Info_grid)
        Sub_Info_widget.setStyleSheet("background: white")

        #--- Picked Time SubWidget ---#
        Sub_picked_widget = QtGui.QWidget()
        Sub_picked_grid = QtGui.QGridLayout()
        Sub_picked_grid.addWidget(picked_label, 0, 0)
        Sub_picked_grid.addWidget(self.time, 0, 1)
        Sub_picked_grid.addWidget(incertitude_label, 0, 2)
        Sub_picked_grid.addWidget(self.incertitude_value_label, 0, 3)
        Sub_picked_widget.setLayout(Sub_picked_grid)
        Sub_picked_widget.setStyleSheet(" Background: white ")

        #--- Trace Subwidget ---#
        Sub_Trace_Widget = QtGui.QWidget()
        Sub_Trace_Grid = QtGui.QGridLayout()
        Sub_Trace_Grid.addWidget(trc_Label, 0, 0)
        Sub_Trace_Grid.addWidget(self.Tnum_Edit, 0, 1)
        Sub_Trace_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_Trace_Widget.setLayout(Sub_Trace_Grid)

        #--- Prev Next SubWidget ---#
        sub_prev_next_widget = QtGui.QWidget()
        sub_prev_next_grid = QtGui.QGridLayout()
        sub_prev_next_grid.addWidget(btn_Prev, 0, 0)
        sub_prev_next_grid.addWidget(btn_Next, 0, 1)
        sub_prev_next_grid.setContentsMargins(0, 0, 0, 0)
        sub_prev_next_widget.setLayout(sub_prev_next_grid)

        #--- Left Part SubWidget ---#
        Sub_left_Part_Widget = QtGui.QWidget()
        Sub_left_Part_Grid = QtGui.QGridLayout()
        Sub_left_Part_Grid.addWidget(Sub_Info_widget, 0, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(Sub_picked_widget, 1, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(Sub_Trace_Widget, 2, 0)
        Sub_left_Part_Grid.addWidget(sub_prev_next_widget, 3, 0)
        Sub_left_Part_Grid.addWidget(btn_Next_Pick, 5, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(btn_Reini, 6, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(self.Wave_checkbox, 7, 0)
        Sub_left_Part_Grid.addWidget(self.veloc_checkbox, 8, 0)
        Sub_left_Part_Grid.addWidget(self.lim_checkbox, 9, 0)
        Sub_left_Part_Grid.addWidget(self.save_checkbox, 10, 0)
        Sub_left_Part_Grid.addWidget(self.jump_checkbox, 11, 0)
        Sub_left_Part_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_left_Part_Widget.setLayout(Sub_left_Part_Grid)

        #--- upper right subWidget ---#
        Sub_upper_right_Widget = QtGui.QWidget()
        Sub_upper_right_Grid = QtGui.QGridLayout()
        Sub_upper_right_Grid.addWidget(self.pick_checkbox, 0, 0)
        Sub_upper_right_Grid.addWidget(self.main_data_radio, 1, 0)
        Sub_upper_right_Grid.addWidget(self.t0_before_radio, 2, 0)
        Sub_upper_right_Grid.addWidget(self.t0_after_radio, 3, 0)
        Sub_upper_right_Grid.addWidget(self.pick_combo, 4, 0, 1, 2)
        Sub_upper_right_Grid.addWidget(btn_Upper, 6, 0, 1, 2)
        Sub_upper_right_Grid.addWidget(btn_Conti, 7, 0, 1, 2)
        Sub_upper_right_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_upper_right_Widget.setLayout(Sub_upper_right_Grid)

        #--- Contiguous Trace Groupbox ---#
        Conti_Groupbox = QtGui.QGroupBox("Shot Gather")
        Conti_Grid = QtGui.QGridLayout()
        Conti_Grid.addWidget(self.tt_picking_radio, 0, 0)
        Conti_Grid.addWidget(self.trace_selec_radio, 1, 0)
        Conti_Grid.setColumnStretch(1, 100)
        Conti_Grid.setContentsMargins(0, 0, 0, 0)
        Conti_Groupbox.setLayout(Conti_Grid)

        #--- Time and Amplitude Labels SubWidget ---#
        Sub_T_and_A_Labels_Widget = QtGui.QWidget()
        Sub_T_and_A_Labels_Grid = QtGui.QGridLayout()
        Sub_T_and_A_Labels_Grid.addWidget(t_min_label, 0, 0)
        Sub_T_and_A_Labels_Grid.addWidget(t_max_label, 0, 1)
        Sub_T_and_A_Labels_Grid.addWidget(A_min_label, 0, 2)
        Sub_T_and_A_Labels_Grid.addWidget(A_max_label, 0, 3)
        Sub_T_and_A_Labels_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_T_and_A_Labels_Widget.setLayout(Sub_T_and_A_Labels_Grid)

        #--- Time and Amplitude Edits SubWidget ---#
        Sub_T_and_A_Edits_Widget = QtGui.QWidget()
        Sub_T_and_A_Edits_Grid = QtGui.QGridLayout()
        Sub_T_and_A_Edits_Grid.addWidget(self.t_min_Edit, 0, 0)
        Sub_T_and_A_Edits_Grid.addWidget(self.t_max_Edit, 0, 1)
        Sub_T_and_A_Edits_Grid.addWidget(self.A_min_Edit, 0, 2)
        Sub_T_and_A_Edits_Grid.addWidget(self.A_max_Edit, 0, 3)
        Sub_T_and_A_Edits_Grid.addWidget(btn_Stats, 1, 0, 1, 4)
        Sub_T_and_A_Edits_Grid.setHorizontalSpacing(0)
        Sub_T_and_A_Edits_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_T_and_A_Edits_Widget.setLayout(Sub_T_and_A_Edits_Grid)

        #--- Time and Ampitude Labels and Edits SubWidget ---#
        Sub_T_and_A_Widget = QtGui.QWidget()
        Sub_T_and_A_Grid   = QtGui.QGridLayout()
        Sub_T_and_A_Grid.addWidget(Sub_T_and_A_Labels_Widget, 0, 0)
        Sub_T_and_A_Grid.addWidget(Sub_T_and_A_Edits_Widget, 1, 0)
        Sub_T_and_A_Grid.setRowStretch(3, 100)
        Sub_T_and_A_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_T_and_A_Widget.setLayout(Sub_T_and_A_Grid)

        #--- Control Center SubWidget ---#
        Control_Center_GroupBox = QtGui.QGroupBox("Control Center")
        Control_Center_Grid = QtGui.QGridLayout()
        Control_Center_Grid.addWidget(Sub_left_Part_Widget, 0, 0, 4, 1)
        Control_Center_Grid.addWidget(Sub_upper_right_Widget, 0, 1)
        Control_Center_Grid.addWidget(Conti_Groupbox, 1, 1)
        Control_Center_Grid.addWidget(Sub_T_and_A_Widget, 2, 1)
        Control_Center_GroupBox.setLayout(Control_Center_Grid)


        #--- Master Grid Disposition ---#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(self.tool, 0, 0, 1, 3)
        master_grid.addWidget(self.uppermanager, 1, 0, 1, 3)
        master_grid.addWidget(self.lowermanager, 2, 0, 1, 2)
        master_grid.addWidget(Control_Center_GroupBox, 2, 2)
        master_grid.setRowStretch(1, 100)
        master_grid.setColumnStretch(1, 100)
        master_grid.setContentsMargins(0, 0, 0, 0)
        master_grid.setVerticalSpacing(0)
        self.setLayout(master_grid)

    def upper_trace_isClicked(self):
        if self.sender().isFlat():
            self.sender().setFlat(False)
            self.upperFig.isTracingOn = False
        else:
            self.sender().setFlat(True)
            self.upperFig.isTracingOn = True

    def lower_trace_isClicked(self):
        if self.sender().isFlat():
            self.sender().setFlat(False)
            self.lowerFig.isTracingOn = False
        else:
            self.sender().setFlat(True)
            self.lowerFig.isTracingOn = True

class OpenMainData(QtGui.QWidget):
    def __init__(self, tt, parent=None):
        super(OpenMainData, self).__init__()
        self.setWindowTitle("Choose Data")
        self.database_list = []
        self.tt = tt
        self.initUI()

    def openfile(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Database')

        self.load_file(filename)

    def load_file(self, filename):
        self.tt.filename = filename
        rname = filename.split('/')
        rname = rname[-1]
        if '.p' in rname:
            rname = rname[:-2]
        if '.pkl' in rname:
            rname = rname[:-4]
        if '.pickle' in rname:
            rname = rname[:-7]
        file = open(filename, 'rb')

        self.tt.boreholes, self.tt.mogs, self.tt.air, self.tt.models = pickle.load(file)

        self.database_edit.setText(rname)
        for mog in self.tt.mogs:

            self.mog_combo.addItem(mog.name)


    def cancel(self):
        self.close()

    def ok(self):
        self.tt.update_control_center()
        self.close()

    def initUI(self):

        #-------  Widgets --------#
        #--- Edit ---#
        self.database_edit = QtGui.QLineEdit()
        #- Edit Action -#
        self.database_edit.setReadOnly(True)
        #--- Buttons ---#
        self.btn_database = QtGui.QPushButton('Choose Database')
        self.btn_ok = QtGui.QPushButton('Ok')
        self.btn_cancel = QtGui.QPushButton('Cancel')

        #- Buttons' Actions -#
        self.btn_cancel.clicked.connect(self.cancel)
        self.btn_database.clicked.connect(self.openfile)
        self.btn_ok.clicked.connect(self.ok)

        #--- Combobox ---#
        self.mog_combo = QtGui.QComboBox()

        #- Combobox's Action -#
        self.mog_combo.activated.connect(self.tt.update_control_center)

        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(self.database_edit, 0, 0, 1, 2)
        master_grid.addWidget(self.btn_database, 1, 0, 1, 2)
        master_grid.addWidget(self.mog_combo, 2, 0, 1, 2)
        master_grid.addWidget(self.btn_ok, 3, 0)
        master_grid.addWidget(self.btn_cancel, 3 ,1)
        self.setLayout(master_grid)


class UpperFig(FigureCanvasQTAgg):

    UpperTracePickedSignal = QtCore.pyqtSignal(bool)

    def __init__(self, tt):
        fig_width, fig_height = 4, 4
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor= 'white')
        super(UpperFig, self).__init__(fig)
        self.initFig()
        self.trc_number = 0
        self.tt = tt
        self.mpl_connect('button_press_event', self.onclick)
        #self.mpl_connect('key_press_event', self.press)
        self.isTracingOn = False


    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.13, 0.935, 0.85])
        self.ax2 = self.ax.twiny()

        self.ax.yaxis.set_ticks_position('left')
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.set_ylabel('Amplitude')

        self.ax2.yaxis.set_ticks_position('none')
        self.ax2.xaxis.set_ticks_position('none')

        self.trace,  = self.ax.plot([],
                                    [],
                                    color='b')

        self.picktt  = self.ax2.axvline(-100,
                                        ymin=0,
                                        ymax=1,
                                        color='g')

        self.picket1 = self.ax2.axvline(-100,
                                        ymin=0,
                                        ymax=1,
                                        color='r')

        self.picket2 = self.ax2.axvline(-100,
                                        ymin=0,
                                        ymax=1,
                                        color='r')

    def plot_amplitude(self):

        n = int(self.tt.Tnum_Edit.text())
        A_min = float(self.tt.A_min_Edit.text())
        A_max = float(self.tt.A_max_Edit.text())
        t_min = float(self.tt.t_min_Edit.text())
        t_max = float(self.tt.t_max_Edit.text())

        self.trc_number = n-1

        if self.tt.main_data_radio.isChecked():
            trace = self.tt.mog.data.rdata[:, n-1]
            y_lim = self.ax.get_ylim()

            if self.tt.mog.tt[self.trc_number] != -1:
                self.picktt.set_xdata(self.tt.mog.tt[self.trc_number])

                if self.tt.pick_combo.currentText() == 'Simple Picking' and self.tt.mog.et[self.trc_number] != -1.0:
                    self.picket1.set_xdata(self.tt.mog.tt[self.trc_number] -
                                           self.tt.mog.et[self.trc_number])
                    self.picket2.set_xdata(self.tt.mog.tt[self.trc_number] +
                                           self.tt.mog.et[self.trc_number])
                elif self.tt.pick_combo.currentText() == 'Pick with std deviation':
                    self.picket1.set_xdata(self.tt.mog.tt[self.trc_number] -
                                           self.tt.mog.et[self.trc_number])
                    self.picket2.set_xdata(self.tt.mog.tt[self.trc_number] +
                                           self.tt.mog.et[self.trc_number])

            else:
                self.picktt.set_xdata(-100)
                self.picket1.set_xdata(-100)
                self.picket2.set_xdata(-100)


        if self.tt.t0_before_radio.isChecked():
            airshot_before = self.tt.air[self.tt.mog.av]
            trace = airshot_before.data.rdata[:,n-1]

            if self.tt.air[self.tt.mog.av].tt[self.trc_number] != -1:
                self.picktt.set_xdata(airshot_before.tt[self.trc_number])

                if self.tt.pick_combo.currentText() == 'Simple Picking' and self.tt.air[self.tt.mog.av].tt[self.trc_number] != -1.0:
                    print('Simple')
                    self.picket1.set_xdata(airshot_before.tt[self.trc_number] -
                                           airshot_before.et[self.trc_number])
                    self.picket2.set_xdata(airshot_before.tt[self.trc_number] +
                                           airshot_before.et[self.trc_number])
                elif self.tt.pick_combo.currentText() == 'Pick with std deviation':
                    print('std')
                    self.picket1.set_xdata(airshot_before.tt[self.trc_number] -
                                           airshot_before.et[self.trc_number])
                    self.picket2.set_xdata(airshot_before.tt[self.trc_number] +
                                           airshot_before.et[self.trc_number])

            else:
                self.picktt.set_xdata(-100)
                self.picket1.set_xdata(-100)
                self.picket2.set_xdata(-100)

        if self.tt.t0_after_radio.isChecked():
            airshot_after = self.tt.air[self.tt.mog.ap]
            trace = airshot_after.data.rdata[:,n-1]
            if airshot_after.tt[self.trc_number] != -1:
                self.picktt.set_xdata(airshot_after.tt[self.trc_number])

                if self.tt.pick_combo.currentText() == 'Simple Picking' and airshot_after.tt[self.trc_number] != -1.0:
                    self.picket1.set_xdata(airshot_after.tt[self.trc_number] -
                                           airshot_after.et[self.trc_number])
                    self.picket2.set_xdata(airshot_after.tt[self.trc_number] +
                                           airshot_after.et[self.trc_number])
                elif self.tt.pick_combo.currentText() == 'Pick with std deviation':
                    self.picket1.set_xdata(airshot_after.tt[self.trc_number] -
                                           airshot_after.et[self.trc_number])
                    self.picket2.set_xdata(airshot_after.tt[self.trc_number] +
                                           airshot_after.et[self.trc_number])

            else:
                self.picktt.set_xdata(-100)
                self.picket1.set_xdata(-100)
                self.picket2.set_xdata(-100)

        if not self.tt.lim_checkbox.isChecked():

            self.ax.set_ylim(A_min, A_max)
        else:
            self.ax.set_ylim( min(trace.flatten()), max(trace.flatten()))

        self.ax2.set_xlim(t_min, t_max)
        self.ax.set_xlim(t_min, t_max)
        if self.tt.main_data_radio.isChecked():
            self.trace.set_xdata(self.tt.mog.data.timestp)
        if self.tt.t0_before_radio.isChecked():
            self.trace.set_xdata(self.tt.air[self.tt.mog.av].data.timestp)
        if self.tt.t0_after_radio.isChecked():
            self.trace.set_xdata(self.tt.air[self.tt.mog.ap].data.timestp)
        self.trace.set_ydata(trace)

        #TODO
        if self.tt.Wave_checkbox.isChecked():
            ind, wavelet = self.wavelet_filtering(mog.data.rdata)

        mpl.axes.Axes.set_xlabel(self.ax, ' Time [{}]'.format(self.tt.mog.data.tunits))


        self.draw()

    def wavelet_filtering(self, rdata):
        shape = np.shape(rdata)
        nptsptrc, ntrace = shape[0], shape[1]
        N = 3
        npts = np.ceil(nptsptrc/2**N)*2**N
        d= npts - nptsptrc
        rdata = np.array([[rdata],
                          [rdata[-1-d:-1, :]]])
        ind_max = np.zeros(ntrace)
        inc_wb = np.round(ntrace/100)
        for n in range(ntrace):
            trace2 = self.denoise(rdata[:, n], wavelet, N)

    def denoise(self, trace, wavelet, N):
        swc = swt(trace, N, wavelet)

    def onclick(self, event):

        if self.isTracingOn is False:
            return

        self.x, self.y = event.x, event.y
        y_lim = self.ax.get_ylim()
        x_lim = self.ax.get_xlim()
        if event.button == 1:

            if self.x != None and self.y != None:

                if self.tt.main_data_radio.isChecked():
                    self.tt.mog.tt[self.trc_number] = event.xdata
                    self.tt.mog.tt_done[self.trc_number] = 1

                if self.tt.t0_before_radio.isChecked():
                    self.tt.air[self.tt.mog.av].tt[self.trc_number] = event.xdata
                    self.tt.air[self.tt.mog.av].tt_done[self.trc_number] = 1
                    self.ax2.set_xlim(x_lim[0], x_lim[-1])
                    self.ax.set_ylim(y_lim[0], y_lim[-1])

                if self.tt.t0_after_radio.isChecked():
                    self.tt.air[self.tt.mog.ap].tt[self.trc_number] = event.xdata
                    self.tt.air[self.tt.mog.ap].tt_done[self.trc_number] = 1
                    self.ax2.set_xlim(x_lim[0], x_lim[-1])
                    self.ax.set_ylim(y_lim[0], y_lim[-1])

                if self.tt.pick_combo.currentText() == "Simple Picking":
                    if self.tt.main_data_radio.isChecked():
                        self.picktt.set_xdata(self.tt.mog.tt[self.trc_number])

                    if self.tt.t0_before_radio.isChecked():
                        print('before tt being plotted')
                        self.picktt.set_xdata(self.tt.air[self.tt.mog.av].tt[self.trc_number])

                    if self.tt.t0_after_radio.isChecked():
                        self.picktt.set_xdata(self.tt.air[self.tt.mog.ap].tt[self.trc_number])


                elif self.tt.pick_combo.currentText() == "Pick with std deviation":

                    if self.tt.main_data_radio.isChecked():
                        self.picktt.set_xdata(self.tt.mog.tt[self.trc_number])
                        self.picket1.set_xdata(self.tt.mog.tt[self.trc_number] -
                                                self.tt.mog.et[self.trc_number])
                        self.picket2.set_xdata(self.tt.mog.tt[self.trc_number] +
                                                self.tt.mog.et[self.trc_number])

                    if self.tt.t0_before_radio.isChecked():
                        self.picktt.set_xdata(self.tt.air[self.tt.mog.av].tt[self.trc_number])
                        self.picket1.set_xdata(self.tt.air[self.tt.mog.av].tt[self.trc_number] -
                                               self.tt.air[self.tt.mog.av].et[self.trc_number])
                        self.picket2.set_xdata(self.tt.air[self.tt.mog.av].tt[self.trc_number] +
                                               self.tt.air[self.tt.mog.av].et[self.trc_number])

                    if self.tt.t0_after_radio.isChecked():
                        self.picktt.set_xdata(self.tt.air[self.tt.mog.ap].tt[self.trc_number])
                        self.picket1.set_xdata(self.tt.air[self.tt.mog.ap].tt[self.trc_number] -
                                               self.tt.air[self.tt.mog.ap].et[self.trc_number])
                        self.picket2.set_xdata(self.tt.air[self.tt.mog.ap].tt[self.trc_number] +
                                               self.tt.air[self.tt.mog.ap].et[self.trc_number])

            self.UpperTracePickedSignal.emit(True)

        elif event.button == 2:

            if self.tt.jump_checkbox.isChecked():

                self.tt.next_trace_to_pick()
            else:
                self.tt.next_trace()

        elif event.button == 3:
            if self.x != None and self.y != None:

                if self.tt.main_data_radio.isChecked():
                    self.tt.mog.et[self.trc_number] = np.abs(self.tt.mog.tt[self.trc_number] - event.xdata)

                if self.tt.t0_before_radio.isChecked():
                    self.tt.air[self.tt.mog.av].et[self.trc_number] = np.abs(self.tt.air[self.tt.mog.av].tt[self.trc_number] - event.xdata)

                if self.tt.t0_after_radio.isChecked():
                    self.tt.air[self.tt.mog.ap].et[self.trc_number] = np.abs(self.tt.air[self.tt.mog.ap].tt[self.trc_number] - event.xdata)


                y_lim = self.ax.get_ylim()
                x_lim = self.ax.get_xlim()

                if self.tt.main_data_radio.isChecked():
                    et = np.abs(self.tt.mog.tt[self.trc_number] - event.xdata)
                    self.picket1.set_xdata(self.tt.mog.tt[self.trc_number] - et)
                    self.picket2.set_xdata(self.tt.mog.tt[self.trc_number] + et)

                if self.tt.t0_before_radio.isChecked():
                    et = np.abs(self.tt.air[self.tt.mog.av].tt[self.trc_number] - event.xdata)
                    self.picket1.set_xdata(self.tt.air[self.tt.mog.av].tt[self.trc_number] - et)
                    self.picket2.set_xdata(self.tt.air[self.tt.mog.av].tt[self.trc_number] + et)

                if self.tt.t0_after_radio.isChecked():
                    et = np.abs(self.tt.air[self.tt.mog.ap].tt[self.trc_number] - event.xdata)
                    self.picket1.set_xdata(self.tt.air[self.tt.mog.ap].tt[self.trc_number] - et)
                    self.picket2.set_xdata(self.tt.air[self.tt.mog.ap].tt[self.trc_number] + et)

                self.ax.set_ylim(y_lim[0], y_lim[-1])

            self.UpperTracePickedSignal.emit(True)


        self.draw()


class LowerFig(FigureCanvasQTAgg):
    LowerTracePickedSignal = QtCore.pyqtSignal(bool)
    def __init__(self, tt):
        fig_width, fig_height = 4, 4
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor= 'white')
        super(LowerFig, self).__init__(fig)
        self.initFig()
        self.tt = tt
        self.mpl_connect('button_press_event', self.onclick)
        self.isTracingOn = False

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.85])
        self.ax.yaxis.set_ticks_position('left')
        self.ax.xaxis.set_ticks_position('bottom')

        self.shot_gather        = self.ax.imshow(np.zeros((2,2)),
                                                interpolation= 'none',
                                                cmap= 'seismic',
                                                aspect= 'auto')

        self.actual_line        = self.ax.axvline(-100,
                                                ymin=0,
                                                ymax=1,
                                                color='black')

        self.unpicked_square,   = self.ax.plot(-100, -100,
                                                marker= 's',
                                                color='red',
                                                markersize= 10,
                                                lw= 0)

        self.picked_square,     = self.ax.plot(-100, -100,
                                                marker= 's',
                                                color='green',
                                                markersize= 10,
                                                lw= 0)

        self.picked_tt_circle,  = self.ax.plot(-100, -100,
                                                marker = 'o',
                                                fillstyle= 'none',
                                                color= 'green',
                                                markersize= 5,
                                                mew= 2,
                                                ls = 'None')

        self.picked_et_circle1, = self.ax.plot(-100, -100,
                                                marker = 'o',
                                                fillstyle= 'none',
                                                color= 'red',
                                                markersize= 5,
                                                mew= 2,
                                                ls = 'None')

        self.picked_et_circle2, = self.ax.plot(-100, -100,
                                                marker = 'o',
                                                fillstyle= 'none',
                                                color= 'red',
                                                markersize= 5,
                                                mew= 2,
                                                ls = 'None')

        self.vapp_plot,         = self.ax.plot(-100, -100,
                                                marker = 'o',
                                                fillstyle= 'none',
                                                color= 'yellow',
                                                markersize= 5,
                                                mew= 2,
                                                ls = 'None')

    def plot_trace_data(self):

        n = int(self.tt.Tnum_Edit.text())
        mog  = self.tt.mog
        self.trc_number = n-1

        t_min = float(self.tt.t_min_Edit.text())
        t_max = float(self.tt.t_max_Edit.text())

        if self.tt.main_data_radio.isChecked():
            #print('main data')
            current_trc = mog.data.Tx_z[n]
            z = np.where(mog.data.Tx_z == current_trc)[0]

            data = mog.data.rdata[:, z[0]:z[-1]]
            cmax = max(np.abs(mog.data.rdata.flatten()))

            unpicked_tt_ind = np.where(mog.tt == -1)[0]
            picked_tt_ind = np.where(mog.tt != -1)[0]

            unpicked_et_ind = np.where(mog.et == -1)[0]
            picked_et_ind = np.where(mog.et != -1)[0]

            tt_done_ind = np.where(mog.tt_done != 0)[0]
            tt_undone_ind = np.where(mog.tt_done == 0)[0]

            actual_data = mog.data.rdata

            self.picked_tt_circle.set_xdata(picked_tt_ind)
            self.picked_tt_circle.set_ydata(self.tt.mog.tt[picked_tt_ind])

            self.picked_et_circle1.set_xdata(picked_et_ind)
            self.picked_et_circle1.set_ydata(self.tt.mog.tt[picked_et_ind] + self.tt.mog.et[picked_et_ind])

            self.picked_et_circle2.set_xdata(picked_et_ind)
            self.picked_et_circle2.set_ydata( self.tt.mog.tt[picked_et_ind] - self.tt.mog.et[picked_et_ind])

            self.actual_line.set_xdata(n-1)

            self.unpicked_square.set_xdata(tt_undone_ind)
            self.unpicked_square.set_ydata(t_max*np.ones(len(tt_undone_ind)))

            self.picked_square.set_xdata(tt_done_ind)
            self.picked_square.set_ydata(t_max*np.ones(len(tt_done_ind)))

            self.shot_gather.set_data(data)
            self.shot_gather.autoscale()
            self.shot_gather.set_extent([z[0], z[-1], self.tt.mog.data.timestp[-1], self.tt.mog.data.timestp[0]])

            if self.tt.veloc_checkbox.isChecked():
                vapp = self.calculate_Vapp()
                hyp = np.sqrt((mog.data.Tx_x[picked_tt_ind]-mog.data.Rx_x[picked_tt_ind])**2
                      + (mog.data.Tx_y[picked_tt_ind] - mog.data.Rx_y[picked_tt_ind] )**2
                      + (mog.data.Tx_z[picked_tt_ind] -  mog.data.Rx_z[picked_tt_ind] )**2)
                tvapp = hyp/vapp

                self.vapp_plot.set_ydata(tvapp)
                self.vapp_plot.set_xdata(picked_tt_ind)
            else:
                self.vapp_plot.set_xdata(-100)
                self.vapp_plot.set_ydata(-100)

            self.draw()

        elif self.tt.t0_before_radio.isChecked():
            airshot_before = self.tt.air[self.tt.mog.av]
            data = airshot_before.data.rdata

            unpicked_tt_ind = np.where(airshot_before.tt == -1)[0]
            picked_tt_ind = np.where(airshot_before.tt != -1)[0]
            #print(picked_tt_ind)

            unpicked_et_ind = np.where(airshot_before.et == -1)[0]
            picked_et_ind = np.where(airshot_before.et != -1)[0]

            cmax = np.abs(max(airshot_before.data.rdata.flatten()))

            tt_done_ind = np.where(airshot_before.tt_done != 0)[0]
            tt_undone_ind = np.where(airshot_before.tt_done == 0)[0]

            actual_data = data

            self.picked_tt_circle.set_xdata(picked_tt_ind)
            self.picked_tt_circle.set_ydata(airshot_before.tt[picked_tt_ind])

            self.picked_et_circle1.set_xdata(picked_et_ind)
            self.picked_et_circle1.set_ydata(airshot_before.tt[picked_et_ind] + airshot_before.et[picked_et_ind])

            self.picked_et_circle2.set_xdata(picked_et_ind)
            self.picked_et_circle2.set_ydata(airshot_before.tt[picked_et_ind] - airshot_before.et[picked_et_ind])

            self.actual_line.set_xdata(n-1)

            self.unpicked_square.set_xdata(tt_undone_ind)
            self.unpicked_square.set_ydata(t_max*np.ones(len(tt_undone_ind)))

            self.picked_square.set_xdata(tt_done_ind)
            self.picked_square.set_ydata(t_max*np.ones(len(tt_done_ind)))

            self.shot_gather.set_data(data)
            self.shot_gather.autoscale()
            self.shot_gather.set_extent([0, airshot_before.data.ntrace -1, t_max, t_min])


            self.draw()


        elif self.tt.t0_after_radio.isChecked():
            airshot_after = self.tt.air[self.tt.mog.ap]
            data = airshot_after.data.rdata

            unpicked_tt_ind = np.where(airshot_after.tt == -1)[0]
            picked_tt_ind = np.where(airshot_after.tt != -1)[0]

            unpicked_et_ind = np.where(airshot_after.et == -1)[0]
            picked_et_ind = np.where(airshot_after.et != -1)[0]

            cmax = np.abs(max(airshot_after.data.rdata.flatten()))

            tt_done_ind = np.where(airshot_after.tt_done != 0)[0]
            tt_undone_ind = np.where(airshot_after.tt_done == 0)[0]

            actual_data = data

            self.picked_tt_circle.set_xdata(picked_tt_ind)
            self.picked_tt_circle.set_ydata(airshot_after.tt[picked_tt_ind])

            self.picked_et_circle1.set_xdata(picked_et_ind)
            self.picked_et_circle1.set_ydata(airshot_after.tt[picked_et_ind] + airshot_after.et[picked_et_ind])

            self.picked_et_circle2.set_xdata(picked_et_ind)
            self.picked_et_circle2.set_ydata(airshot_after.tt[picked_et_ind] - airshot_after.et[picked_et_ind])

            self.actual_line.set_xdata(n-1)

            self.unpicked_square.set_xdata(tt_undone_ind)
            self.unpicked_square.set_ydata(t_max*np.ones(len(tt_undone_ind)))

            self.picked_square.set_xdata(tt_done_ind)
            self.picked_square.set_ydata(t_max*np.ones(len(tt_done_ind)))

            self.shot_gather.set_data(data)
            self.shot_gather.autoscale()
            self.shot_gather.set_extent([0, airshot_after.data.ntrace -1, t_max, t_min])
            self.draw()

        mpl.axes.Axes.set_ylabel(self.ax, 'Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_xlabel(self.ax, 'Trace No')

    def calculate_Vapp(self):
        mog = self.tt.mog
        ind1 = np.not_equal(mog.tt, -1)
        ind2 = np.equal(mog.tt_done, 1).astype(int) + ind1.astype(int) + np.equal(mog.in_vect, 1).astype(int)
        ind2 = np.where(ind2 == 3)
        if len(ind2) == 0 :
            vapp = 0
            return vapp

        hyp = np.sqrt((mog.data.Tx_x[ind2]-mog.data.Rx_x[ind2])**2
                      + (mog.data.Tx_y[ind2] - mog.data.Rx_y[ind2] )**2
                      + (mog.data.Tx_z[ind2] -  mog.data.Rx_z[ind2] )**2)

        tt = mog.tt[ind2]
        et = mog.et[ind2]

        vapp = hyp/tt
        if np.all(et == 0):
            vapp = np.mean(vapp)
        else:
            w = 1/et
            vapp = sum(vapp*w)/sum(w)

        return vapp


    def onclick(self, event):
        if self.isTracingOn is False:
            return

        self.x, self.y = event.x, event.y

        if event.button == 1:
            if self.x != None and self.y != None:

                y_lim = self.ax.get_ylim()
                x_lim = self.ax.get_xlim()

                if self.tt.tt_picking_radio.isChecked():

                    if self.tt.main_data_radio.isChecked():
                        print('Traveltime being picked')
                        self.tt.mog.tt[self.trc_number] = event.ydata
                        self.tt.mog.tt_done[self.trc_number] = 1
                        self.picked_tt_circle.set_ydata(self.tt.mog.tt[self.trc_number])
                    elif self.tt.t0_before_radio.isChecked():
                        print('t0_before being picked')
                        self.tt.air[self.tt.mog.av].tt[self.trc_number] = event.ydata
                        self.tt.air[self.tt.mog.av].tt_done[self.trc_number] = 1
                        self.picked_tt_circle.set_ydata(self.tt.air[self.tt.mog.av].tt[self.trc_number])

                    elif self.tt.t0_after_radio.isChecked():
                        self.tt.air[self.tt.mog.ap].tt[self.trc_number] = event.ydata
                        self.tt.air[self.tt.mog.ap].tt_done[self.trc_number] = 1
                        self.picked_tt_circle.set_ydata(self.tt.air[self.tt.mog.av].tt[self.trc_number])

                elif self.tt.trace_selec_radio.isChecked():

                    idx = np.argmin((np.abs(np.arange(self.tt.mog.data.ntrace) - event.xdata)))
                    self.tt.Tnum_Edit.setText(str(idx + 1))
                    self.tt.update_control_center()

                self.ax.set_ylim(y_lim[0], y_lim[-1])
                self.LowerTracePickedSignal.emit(True)

        elif event.button == 2:
            if self.tt.jump_checkbox.isChecked():

                self.tt.next_trace_to_pick()
            else:
                self.tt.next_trace()


        elif event.button == 3:
            if self.x != None and self.y != None:

                if self.tt.main_data_radio.isChecked():
                    self.tt.mog.et[self.trc_number] =  np.abs(self.tt.mog.tt[self.trc_number] -event.ydata)
                elif self.tt.t0_before_radio.isChecked():
                    self.tt.air[self.tt.mog.av].et[self.trc_number] = np.abs(self.tt.air[self.tt.mog.av].tt[self.trc_number] -event.ydata)
                elif self.tt.t0_after_radio.isChecked():
                    self.tt.air[self.tt.mog.ap].et[self.trc_number] = np.abs(self.tt.air[self.tt.mog.ap].tt[self.trc_number] -event.ydata)

                self.LowerTracePickedSignal.emit(True)


        self.draw()


class StatsFig1(FigureCanvasQTAgg):
    def __init__(self, parent = None):

        fig = mpl.figure.Figure(figsize= (100, 100), facecolor='white')
        super(StatsFig1, self).__init__(fig)
        self.initFig()

    def initFig(self):


        self.ax1 = self.figure.add_axes([0.1, 0.1, 0.2, 0.25])
        self.ax2 = self.figure.add_axes([0.4, 0.1, 0.2, 0.25])
        self.ax3 = self.figure.add_axes([0.7, 0.1, 0.2, 0.25])
        self.ax4 = self.figure.add_axes([0.1, 0.55, 0.2, 0.25])
        self.ax5 = self.figure.add_axes([0.4, 0.55, 0.2, 0.25])
        self.ax6 = self.figure.add_axes([0.7, 0.55, 0.2, 0.25])

    def plot_stats(self, mog, airshots):

        done = (mog.tt_done + mog.in_vect.astype(int)) - 1
        ind = np.nonzero(done == 1)[0]
        print(ind)

        tt, t0 = mog.getCorrectedTravelTimes(airshots)
        print(tt)
        et = mog.et[ind]
        tt = tt[ind]


        hyp = np.sqrt((mog.data.Tx_x[ind]-mog.data.Rx_x[ind])**2
                      + (mog.data.Tx_y[ind] - mog.data.Rx_y[ind] )**2
                      + (mog.data.Tx_z[ind] -  mog.data.Rx_z[ind] )**2)
        dz = mog.data.Rx_z[ind] - mog.data.Tx_z[ind]

        theta = 180/ np.pi * np.arcsin(dz/hyp)

        vapp = hyp/(tt-t0[ind])

        #n = np.arange(len(ind)-1)
        #n = n[ind]
        ind2 = np.less(vapp, 0)
        ind2 = np.nonzero(ind2)[0]

        self.ax4.plot(hyp, tt, marker='o', ls= 'None')
        self.ax5.plot(theta, hyp/tt, marker='o', ls= 'None')
        self.ax2.plot(theta, vapp, marker='o', ls= 'None')
        self.ax6.plot(t0)
        self.ax1.plot(hyp, et, marker='o', ls= 'None')
        self.ax3.plot(theta, et, marker='o', ls= 'None')





        self.figure.suptitle('{}'.format(mog.name), fontsize=20)
        mpl.axes.Axes.set_ylabel(self.ax4, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_xlabel(self.ax4, 'Straight Ray Length[{}]'.format(mog.data.cunits))

        mpl.axes.Axes.set_ylabel(self.ax1, 'Standard Deviation')
        mpl.axes.Axes.set_xlabel(self.ax1, 'Straight Ray Length[{}]'.format(mog.data.cunits))

        mpl.axes.Axes.set_ylabel(self.ax5, 'Apparent Velocity [{}/{}]'.format(mog.data.cunits, mog.data.tunits))
        mpl.axes.Axes.set_xlabel(self.ax5, 'Angle w/r to horizontal[°]')
        mpl.axes.Axes.set_title(self.ax5, 'Velocity before correction')

        mpl.axes.Axes.set_ylabel(self.ax2, 'Apparent Velocity [{}/{}]'.format(mog.data.cunits, mog.data.tunits))
        mpl.axes.Axes.set_xlabel(self.ax2, 'Angle w/r to horizontal[°]')
        mpl.axes.Axes.set_title(self.ax2, 'Velocity after correction')

        mpl.axes.Axes.set_ylabel(self.ax6, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_xlabel(self.ax6, 'Shot Number')
        mpl.axes.Axes.set_title(self.ax6, '$t_0$ drift in air')

        mpl.axes.Axes.set_ylabel(self.ax3, 'Standard Deviation')
        mpl.axes.Axes.set_xlabel(self.ax3, 'Angle w/r to horizontal[°]')



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


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    manual_ui = ManualttUI()
    manual_ui.openmain.load_file('save test.p')
    manual_ui.update_control_center()
    manual_ui.update_a_and_t_edits()
    manual_ui.upperFig.plot_amplitude()
    manual_ui.lowerFig.plot_trace_data()
    manual_ui.showMaximized()
    #manual_ui.load_tt_file('C:\\Users\\Utilisateur\\Documents\\MATLAB\\t0302tt')

    sys.exit(app.exec_())

# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
import pickle
import numpy as np





class ManualttUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(ManualttUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Manual Traveltime Picking")
        self.openmain = OpenMainData(self)
        self.mogs = []
        self.air = []
        self.initUI()
    def next_trace(self):
        n = int(self.Tnum_Edit.text())
        n += 1
        self.Tnum_Edit.setText(str(n))
        self.plot_upper_fig()
        self.update_control_center()

    def prev_trace(self):
        n = int(self.Tnum_Edit.text())
        n -= 1
        self.Tnum_Edit.setText(str(n))
        self.plot_upper_fig()
        self.update_control_center()

    def update_control_center(self):
        n = int(self.Tnum_Edit.text())-1
        ind = self.openmain.mog_combo.currentIndex()
        mog = self.mogs[ind]
        self.xRx_label.setText(str(mog.data.Rx_x[n]))
        self.xTx_label.setText(str(mog.data.Tx_x[n]))
        self.yRx_label.setText(str(mog.data.Rx_y[n]))
        self.yTx_label.setText(str(mog.data.Tx_y[n]))
        self.zRx_label.setText(str(mog.data.Rx_z[n]))
        self.zTx_label.setText(str(mog.data.Tx_z[n]))
        self.ntrace_label.setText(str(mog.data.ntrace))
        self.plot_upper_fig()
        self.plot_lower_fig()

    def plot_upper_fig(self):
        n = int(self.Tnum_Edit.text())
        ind = self.openmain.mog_combo.currentIndex()
        mog = self.mogs[ind]
        A_min = float(self.A_min_Edit.text())
        A_max = float(self.A_max_Edit.text())
        t_min = float(self.t_min_Edit.text())
        t_max = float(self.t_max_Edit.text())
        self.upperFig.plot_amplitude(mog, n, A_min, A_max, t_min, t_max)

    def plot_lower_fig(self):
        n = int(self.Tnum_Edit.text())
        ind = self.openmain.mog_combo.currentIndex()
        mog = self.mogs[ind]
        self.lowerFig.plot_trace_data(mog, n)


    def initUI(self):
        blue_palette = QtGui.QPalette()
        blue_palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkCyan)


        #------ Creation of the Manager for the Lower figure -------#
        self.lowerFig = LowerFig()
        self.lowermanager = QtGui.QWidget()
        lowermanagergrid = QtGui.QGridLayout()
        lowermanagergrid.addWidget(self.lowerFig, 0, 0)
        self.lowermanager.setLayout(lowermanagergrid)

        #------ Creation of the Manager for the Upper figure -------#
        self.upperFig = UpperFig()
        self.uppertool = NavigationToolbar2QT(self.upperFig, self)
        self.uppermanager = QtGui.QWidget()
        uppermanagergrid = QtGui.QGridLayout()
        uppermanagergrid.addWidget(self.uppertool, 0, 0)
        uppermanagergrid.addWidget(self.upperFig, 1, 0)
        uppermanagergrid.setContentsMargins(0, 0, 0, 0)
        uppermanagergrid.setVerticalSpacing(3)
        self.uppermanager.setLayout(uppermanagergrid)
        #------- Widgets Creation -------#
        #--- Buttons ---#
        btn_Prev = QtGui.QPushButton("Previous Trace")
        btn_Next = QtGui.QPushButton("Next Trace")
        btn_Next_Pick = QtGui.QPushButton("Next Trace to Pick")
        btn_Reini = QtGui.QPushButton("Reinitialize Trace")
        btn_Upper = QtGui.QPushButton("Activate Picking - Upper Trace")
        btn_Conti = QtGui.QPushButton("Activate Picking - Contiguous Trace")
        btn_Stats = QtGui.QPushButton("Statistics")

        #- Buttons' Actions -#
        btn_Next.clicked.connect(self.next_trace)
        btn_Prev.clicked.connect(self.prev_trace)
        btn_Upper.clicked.connect(self.upperFig.plot_picked_trace)

        #--- Label ---#
        trc_Label = MyQLabel("Trace number :", ha= 'right')
        t_min_label = MyQLabel("t min", ha= 'center')
        t_max_label = MyQLabel("t max", ha= 'center')
        A_min_label = MyQLabel("A min", ha= 'center')
        A_max_label = MyQLabel("A max", ha= 'center')
        position_label = MyQLabel(("Position Tx--Rx"), ha='center')
        x_label = MyQLabel(("x"), ha= 'center')
        y_label = MyQLabel(("y"), ha= 'center')
        z_label = MyQLabel(("z"), ha= 'center')
        Tx_label = MyQLabel(("Tx:"), ha= 'right')
        Rx_label = MyQLabel(("Rx:"), ha= 'right')
        self.xTx_label = MyQLabel((""), ha= 'right')
        self.yTx_label = MyQLabel((""), ha= 'right')
        self.zTx_label = MyQLabel((""), ha= 'right')
        self.xRx_label = MyQLabel((""), ha= 'right')
        self.yRx_label = MyQLabel((""), ha= 'right')
        self.zRx_label = MyQLabel((""), ha= 'right')
        self.ntrace_label = MyQLabel((""), ha= 'right')
        trace_label = MyQLabel(("traces"), ha= 'left')
        picked_label = MyQLabel(("Picked Time:"), ha= 'right')
        self.time = QtGui.QLabel("")
        incertitude_label = QtGui.QLabel("±")
        self.incertitude_value_label = QtGui.QLabel("")

        #-- Setting Labels color ---#
        picked_label.setPalette(blue_palette)
        self.time.setPalette(blue_palette)
        incertitude_label.setPalette(blue_palette)
        self.incertitude_value_label.setPalette(blue_palette)

        #--- Actions ---#
        openAction = QtGui.QAction(' Open main data file', self)
        openAction.triggered.connect(self.openmain.show)

        saveAction = QtGui.QAction('Save', self)
        #--- ToolBar ---#
        self.tool = QtGui.QMenuBar()
        filemenu = self.tool.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(saveAction)


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
        self.t_min_Edit.editingFinished.connect(self.plot_upper_fig)
        self.t_max_Edit.editingFinished.connect(self.plot_upper_fig)
        self.A_min_Edit.editingFinished.connect(self.plot_upper_fig)
        self.A_max_Edit.editingFinished.connect(self.plot_upper_fig)

        #--- Checkboxes ---#
        Wave_checkbox = QtGui.QCheckBox("Wavelet tranf. denoising")
        veloc_checkbox = QtGui.QCheckBox("Show apparent velocity")
        lim_checkbox = QtGui.QCheckBox("A-dynamic limit")
        save_checkbox = QtGui.QCheckBox("Intermediate saves")
        jump_checkbox = QtGui.QCheckBox("Jump to nex unpicked Trace")
        pick_checkbox = QtGui.QCheckBox("Pick Tx Data")
        pick_checkbox.setDisabled(True)

        #--- Radio Buttons ---#
        main_data_radio = QtGui.QRadioButton("Main Data file")
        t0_before_radio = QtGui.QRadioButton("t0 Before")
        t0_after_radio = QtGui.QRadioButton("t0 After")
        tt_picking_radio = QtGui.QRadioButton("Traveltime picking")
        std_dev_radio = QtGui.QRadioButton("Std deviation picking")
        trace_selec_radio = QtGui.QRadioButton("Trace selection")

        #- Radio Buttons' Actions -#
        main_data_radio.setChecked(True)

        #--- Text Edits ---#
        info_Tedit = QtGui.QTextEdit()
        info_Tedit.setReadOnly(True)
        PTime_Tedit = QtGui.QTextEdit()
        PTime_Tedit.setReadOnly(True)

        #--- combobox ---#
        pick_combo = QtGui.QComboBox()
        pick_combo.addItem("Pick with std deviation")
        pick_combo.addItem("Simple Picking")

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
        Sub_left_Part_Grid.addWidget(Wave_checkbox, 7, 0)
        Sub_left_Part_Grid.addWidget(veloc_checkbox, 8, 0)
        Sub_left_Part_Grid.addWidget(lim_checkbox, 9, 0)
        Sub_left_Part_Grid.addWidget(save_checkbox, 10, 0)
        Sub_left_Part_Grid.addWidget(jump_checkbox, 11, 0)
        Sub_left_Part_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_left_Part_Widget.setLayout(Sub_left_Part_Grid)

        #--- upper right subWidget ---#
        Sub_upper_right_Widget = QtGui.QWidget()
        Sub_upper_right_Grid = QtGui.QGridLayout()
        Sub_upper_right_Grid.addWidget(pick_checkbox, 0, 0)
        Sub_upper_right_Grid.addWidget(main_data_radio, 1, 0)
        Sub_upper_right_Grid.addWidget(t0_before_radio, 2, 0)
        Sub_upper_right_Grid.addWidget(t0_after_radio, 3, 0)
        Sub_upper_right_Grid.addWidget(pick_combo, 4, 0, 1, 2)
        Sub_upper_right_Grid.addWidget(btn_Upper, 6, 0, 1, 2)
        Sub_upper_right_Grid.addWidget(btn_Conti, 7, 0, 1, 2)
        Sub_upper_right_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_upper_right_Widget.setLayout(Sub_upper_right_Grid)

        #--- Contiguous Trace Groupbox ---#
        Conti_Groupbox = QtGui.QGroupBox("Contiguous Traces")
        Conti_Grid = QtGui.QGridLayout()
        Conti_Grid.addWidget(tt_picking_radio, 0, 0)
        Conti_Grid.addWidget(std_dev_radio, 1, 0)
        Conti_Grid.addWidget(trace_selec_radio, 2, 0)
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

        rname = filename.split('/')
        rname = rname[-1]
        if '.p' in rname:
            rname = rname[:-2]
        if '.pkl' in rname:
            rname = rname[:-4]
        if '.pickle' in rname:
            rname = rname[:-7]
        file = open(filename, 'rb')

        boreholes, self.tt.mogs, self.tt.air, models = pickle.load(file)

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
    def __init__(self):
        fig_width, fig_height = 4, 4
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor= 'white')
        super(UpperFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.13, 0.935, 0.85])
        self.ax.yaxis.set_ticks_position('left')
        self.ax.xaxis.set_ticks_position('bottom')

    def plot_amplitude(self, mog, n, A_min, A_max, t_min, t_max, transf_state):
        self.ax.cla()
        trace = mog.data.rdata[:, n]

        self.ax.plot(trace)
        self.ax.set_ylim(A_min, A_max)
        self.ax.set_xlim(t_min, t_max)

        mpl.axes.Axes.set_xlabel(self.ax, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_ylabel(self.ax, 'Amplitude')

        if transf_state:
            ind, wavelet = self.wavelet_filtering(mog.data.rdata)

        self.draw()
    def wavelet_filtering(self, rdata):
        shape = np.shape(rdata)
        nptsptrc, ntrace = shape[0], shape[1]
        N = 3
        npts = np.ceil(nptsptrc/2**N)*2**N
        d= npts - nptsptrc





    def plot_picked_trace(self):
        position = ginput(1)
        print(position)



class LowerFig(FigureCanvasQTAgg):
    def __init__(self):
        fig_width, fig_height = 4, 4
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor= 'white')
        super(LowerFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.85])
        self.ax2 = self.ax.twiny()
        self.ax.yaxis.set_ticks_position('left')
        self.ax.xaxis.set_ticks_position('bottom')

    def plot_trace_data(self, mog, n):
        self.ax.cla()
        current_trc = mog.data.Tx_z[n]
        z = np.where(mog.data.Tx_z == current_trc)[0]
        data = mog.data.rdata[:, z[0]:z[-1]]
        self.ax.plot([n-1, n-1], [0, np.shape(mog.data.rdata)[0]])
        self.ax.imshow(data, interpolation= 'none', aspect= 'auto', extent= [z[0], z[-1], 0, np.shape(mog.data.rdata)[0]])
        mpl.axes.Axes.set_ylabel(self.ax, 'Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_xlabel(self.ax, 'Trace No')
        self.draw()


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
    manual_ui.showMaximized()

    sys.exit(app.exec_())

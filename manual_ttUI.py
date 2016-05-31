import sys
from PyQt4 import QtGui, QtCore
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from mpl_toolkits.axes_grid1 import make_axes_locatable


class ManualttUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(ManualttUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Manual Traveltime Picking")
        self.initUI()

    def initUI(self):

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
        self.uppermanager.setLayout(uppermanagergrid)
        #------- Widgets Creation -------#
        #--- Buttons Set ---#
        btn_Prev = QtGui.QPushButton("Previous Trace")
        btn_Next = QtGui.QPushButton("Next Trace")
        btn_Next_Pick = QtGui.QPushButton("Next Trace to Pick")
        btn_Reini = QtGui.QPushButton("Reinitialize Trace")
        btn_Upper = QtGui.QPushButton("Activate Picking - Upper Trace")
        btn_Conti = QtGui.QPushButton("Activate Picking - Contiguous Trace")
        btn_Stats = QtGui.QPushButton("Statistics")

        #--- Label ---#
        trc_Label = MyQLabel("Trace number :", ha= 'right')
        t_min_label = MyQLabel("t min", ha= 'center')
        t_max_label = MyQLabel("t max", ha= 'center')
        A_min_label = MyQLabel("A min", ha= 'center')
        A_max_label = MyQLabel("A max", ha= 'center')
        #--- Edits ---#
        Tnum_Edit = QtGui.QLineEdit()
        Tnum_Edit.setFixedWidth(100)
        t_min_Edit = QtGui.QLineEdit()
        t_min_Edit.setFixedWidth(50)
        t_max_Edit = QtGui.QLineEdit()
        t_max_Edit.setFixedWidth(50)
        A_min_Edit = QtGui.QLineEdit()
        A_min_Edit.setFixedWidth(50)
        A_max_Edit = QtGui.QLineEdit()
        A_max_Edit.setFixedWidth(50)

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

        #--- Text Edits ---#
        futur_Graph1 = QtGui.QTextEdit()
        futur_Graph1.setReadOnly(True)
        futur_Graph2 = QtGui.QTextEdit()
        futur_Graph2.setReadOnly(True)
        info_Tedit = QtGui.QTextEdit()
        info_Tedit.setReadOnly(True)
        PTime_Tedit = QtGui.QTextEdit()
        PTime_Tedit.setReadOnly(True)

        #--- combobox ---#
        pick_combo = QtGui.QComboBox()
        pick_combo.addItem("Pick with std deviation")
        pick_combo.addItem("Simple Picking")

        #------- subWidgets -------#
        #--- Trace Subwidget ---#
        Sub_Trace_Widget = QtGui.QWidget()
        Sub_Trace_Grid = QtGui.QGridLayout()
        Sub_Trace_Grid.addWidget(trc_Label, 0, 0)
        Sub_Trace_Grid.addWidget(Tnum_Edit, 0, 1)
        Sub_Trace_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_Trace_Widget.setLayout(Sub_Trace_Grid)
        #--- Left Part SubWidget ---#
        Sub_left_Part_Widget = QtGui.QWidget()
        Sub_left_Part_Grid = QtGui.QGridLayout()
        Sub_left_Part_Grid.addWidget(info_Tedit, 0, 0)
        Sub_left_Part_Grid.addWidget(PTime_Tedit, 1, 0)
        Sub_left_Part_Grid.addWidget(Sub_Trace_Widget, 2, 0)
        Sub_left_Part_Grid.addWidget(btn_Prev, 3, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(btn_Next, 3, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(btn_Next_Pick, 3, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(btn_Reini, 3, 0, 1, 2)
        Sub_left_Part_Grid.addWidget(Wave_checkbox, 4, 0)
        Sub_left_Part_Grid.addWidget(veloc_checkbox, 5, 0)
        Sub_left_Part_Grid.addWidget(lim_checkbox, 6, 0)
        Sub_left_Part_Grid.addWidget(save_checkbox, 7, 0)
        Sub_left_Part_Grid.addWidget(jump_checkbox, 8, 0)
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
        Sub_T_and_A_Edits_Grid.addWidget(t_min_Edit, 0, 0)
        Sub_T_and_A_Edits_Grid.addWidget(t_max_Edit, 0, 1)
        Sub_T_and_A_Edits_Grid.addWidget(A_min_Edit, 0, 2)
        Sub_T_and_A_Edits_Grid.addWidget(A_max_Edit, 0, 3)
        Sub_T_and_A_Edits_Grid.addWidget(btn_Stats, 1, 0, 1, 2)
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
        master_grid.addWidget(self.uppermanager, 0, 0, 1, 3)
        master_grid.addWidget(self.lowermanager, 1, 0, 1, 2)
        master_grid.addWidget(Control_Center_GroupBox, 1, 2)
        master_grid.setRowStretch(1, 100)
        master_grid.setColumnStretch(1, 100)
        self.setLayout(master_grid)

class UpperFig(FigureCanvasQTAgg):
    def __init__(self):
        fig_width, fig_height = 4, 4
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor= 'white')
        super(UpperFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        ax = self.figure.add_axes([0.4, 0.1, 0.3, 0.85])
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

class LowerFig(FigureCanvasQTAgg):
    def __init__(self):
        fig_width, fig_height = 4, 4
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor= 'white')
        super(LowerFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.85])
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')





if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = ManualttUI()
    Model_ui.showMaximized()

    sys.exit(app.exec_())

# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtGui, QtCore
from BoreholeUI import BoreholeUI
from MogData import MogData
from mog import Mog, AirShots
from unicodedata import *
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import re

class MOGUI(QtGui.QWidget):

    mogInfoSignal = QtCore.pyqtSignal(int)
    ntraceSignal = QtCore.pyqtSignal(int)
    databaseSignal = QtCore.pyqtSignal(str)


    def __init__(self, parent=None):
        super(MOGUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/MOGs")
        self.MOGs = []
        self.mogdata = MogData()
        self.mog = Mog()
        self.initUI()

    def add_MOG(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File')

        if filename:
            self.load_file_MOG(filename)

    def load_file_MOG(self, filename):
        rname = filename.split('/')  # the split method gives us back a list which contains al the caracter that were
        rname = rname[-1]            # separated by / and the name of file (i.e. rname) is the last item of this list

        # Conditions to get the name of the file itself in order to put it in our MOG_list
        if ".rad" in rname.lower() or ".rd3" in rname.lower() or ".tlf" in rname.lower():
            rname = rname[:-4]

        # Conditions to get the path of the file itself in order to execute it
        if ".rad" in filename.lower() or ".rd3" in filename.lower() or ".tlf" in filename.lower():
            basename = filename[:-4]
        mog = Mog(str(rname))
        self.MOGs.append(mog)
        self.update_List_Widget()
        mog.data.readRAMAC(basename)
        self.MOG_list.setCurrentRow(len(self.MOGs) - 1)
        self.update_edits()

    def update_edits(self):
        """
        this funstion updates the info either in the  MOG's edits or in the info's labels

        """
        ind = self.MOG_list.selectedIndexes()
        for i in ind:
            mog = self.MOGs[i.row()]
            self.Rx_Offset_edit.clear()
            self.Tx_Offset_edit.clear()
            self.Correction_Factor_edit.clear()
            self.Multiplication_Factor_edit.clear()
            self.Nominal_Frequency_edit.clear()

            self.Nominal_Frequency_edit.setText(str(mog.data.rnomfreq))
            self.Rx_Offset_edit.setText(str(mog.data.RxOffset))
            self.Tx_Offset_edit.setText(str(mog.data.TxOffset))

            self.ntraceSignal.emit(mog.data.ntrace)
            self.databaseSignal.emit(mog.data.name)

    def del_MOG(self):
        ind = self.MOG_list.selectedIndexes()
        for i in ind:
            del self.MOGs[int(i.row())]
        self.update_List_Widget()

    def rename(self):
        ind = self.MOG_list.selectedIndexes()
        new_name, ok = QtGui.QInputDialog.getText(self, "Rename", 'new MOG name')
        if ok:
            for i in ind:
                self.MOGs[int(i.row())] = new_name
        self.update_List_Widget()


    def airBefore(self, *args):
        old_rep = os.getcwd()
        if len(self.mogdata.data_rep) != 0 :
            os.chdir(self.mogdata.data_rep)

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open t0 air shot before survey')
        if not filename:
            return
        else:
            ind = self.MOG_list.selectedIndexes()
            for i in ind:
                basename = filename[:-4]
                rname = filename.split('/')
                rname = rname[-1]
                found = False

                for n in range(len(self.air)):
                    if str(basename) in str(self.air[n].name):  # self.air représente une instance de la Classe AirShots?
                        self.MOGs[i.row()].av = n               # étant donné qu'on le définit plus bas, quest ce que ca implique ?
                        found = True
                        break

                if not found:
                    n = len(self.air) + 1

                    data = MogData()
                    data.readRAMAC(basename)

                    distance, ok = QtGui.QInputDialog.getItem(self, "Distance", 'Enter distance between Tx and Rx')
                    distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance)

                    if len(distance_list) > 1:
                        if len(distance_list)!= data.ntrace:
                            raise ValueError(' Number of positions inconsistent with number of traces')

                    self.air[n] = AirShots(str(rname))
                    self.air[n].data = data
                    self.air[n].tt = -1* np.ones(1, data.ntrace)
                    self.air[n].et = -1* np.ones(1, data.ntrace)
                    self.air[n].tt_done = np.zeros((1, data.ntrace), dtype=bool)
                    self.air[n].d_TxRx = distance_list
                    self.air[n].fac_dt = 1
                    self.air[n].ing = np.ones((1, data.ntrace), dtype= bool)

                    if len(distance_list) == 1:
                        self.air[n].method ='fixed_antenna'
                    else:
                        self.air[n].method ='walkaway'
                    self.Air_Shot_Before_edit.setText(self.air[n].name)






#TODO:
    def import_mog(self):
        pass
    def merge(self):
        pass
    def trace_zop(self):
        pass
    def spectra(self):
        pass
    def stats_tt(self):
        pass
    def stats_ampl(self):
        pass
    def ray_coverage(self):
        pass
    def export_tt(self):
        pass
    def export_tau(self):
        pass
    def prune(self):
        pass



    def update_List_Widget(self):
        self.MOG_list.clear()
        for mog in self.MOGs:
            self.MOG_list.addItem(mog.name)

        self.mogInfoSignal.emit(len(self.MOG_list))


    def update_Tx_and_Rx_Widget(self, list):
        self.Tx_combo.clear()
        self.Rx_combo.clear()
        for bh in list:
            self.Tx_combo.addItem(bh.name)
            self.Rx_combo.addItem(bh.name)

    def plot_rawdata(self):
        ind = self.MOG_list.selectedIndexes()
        for i in ind:
            self.rawdataFig.plot_raw_data(self.MOGs[i.row()])
            self.rawdatamanager.show()


    def initUI(self):
        self.rawdataFig = RawDataFig()
        self.rawdatatool = NavigationToolbar2QT(self.rawdataFig, self)
        self.rawdatamanager = QtGui.QWidget()
        rawdatamanagergrid = QtGui.QGridLayout()
        rawdatamanagergrid.addWidget(self.rawdatatool, 0, 0)
        rawdatamanagergrid.addWidget(self.rawdataFig, 1, 0)
        self.rawdatamanager.setLayout(rawdatamanagergrid)
        char1 = lookup("GREEK SMALL LETTER TAU")
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
        btn_Add_MOG                 = QtGui.QPushButton("Add MOG")
        btn_Remove_MOG              = QtGui.QPushButton("Remove MOG")
        btn_Air_Shot_Before         = QtGui.QPushButton("Air Shot Before")
        btn_Air_Shot_After          = QtGui.QPushButton("Air Shot After")
        btn_Rename                  = QtGui.QPushButton("Rename")
        btn_Import                  = QtGui.QPushButton("Import")
        btn_Merge                   = QtGui.QPushButton("Merge")
        btn_Raw_Data                = QtGui.QPushButton("Raw Data")
        btn_Trace_ZOP               = QtGui.QPushButton("Trace ZOP")
        btn_Spectra                 = QtGui.QPushButton("Spectra")
        btn_Stats_tt                = QtGui.QPushButton("Stats tt")
        btn_Stats_Ampl              = QtGui.QPushButton("Stats Ampl.")
        btn_Ray_Coverage            = QtGui.QPushButton("Ray Coverage")
        btn_Export_tt               = QtGui.QPushButton("Export tt")
        btn_export_tau              = QtGui.QPushButton("Export {}".format(char1))
        btn_Prune                   = QtGui.QPushButton("Prune")

        #--- List ---#
        self.MOG_list = QtGui.QListWidget()
        #--- List Actions ---#
        self.MOG_list.itemSelectionChanged.connect(self.update_edits)

        #--- combobox ---#
        self.Type_combo = QtGui.QComboBox()
        self.Tx_combo = QtGui.QComboBox()
        self.Rx_combo = QtGui.QComboBox()
        self.Type_combo.addItem(" Crosshole ")
        self.Type_combo.addItem(" VSP/VRP ")

        #--- Checkbox ---#
        Air_shots_checkbox                  = QtGui.QCheckBox("Use Air Shots")
        Correction_Factor_checkbox          = QtGui.QCheckBox("Fixed Time Step Correction Factor")

        #--- Labels ---#
        Type_label                          = MyQLabel('Type:', ha='right')
        Tx_label                            = MyQLabel('Tx:', ha='right')
        Rx_label                            = MyQLabel('Rx:', ha='right')
        Nominal_Frequency_label             = MyQLabel('Nominal Frequency of Antenna:', ha='right')
        Rx_Offset_label                     = MyQLabel('Antenna Feedpoint Offset - Rx:', ha='right')
        Tx_Offset_label                     = MyQLabel('Antenna Feedpoint Offset - Tx:', ha='right')
        Multiplication_Factor_label         = MyQLabel('Std Dev. Multiplication Factor:', ha='right')
        Date_label                          = MyQLabel('Date:', ha='right')

        #--- Edits ---#
        self.Air_Shot_Before_edit                = QtGui.QLineEdit()
        self.Air_Shot_After_edit                 = QtGui.QLineEdit()
        self.Nominal_Frequency_edit              = QtGui.QLineEdit()
        self.Rx_Offset_edit                      = QtGui.QLineEdit()
        self.Tx_Offset_edit                      = QtGui.QLineEdit()
        self.Correction_Factor_edit              = QtGui.QLineEdit()
        self.Multiplication_Factor_edit          = QtGui.QLineEdit()
        self.Date_edit                           = QtGui.QLineEdit()

        #--- Buttons actions ---#
        btn_Add_MOG.clicked.connect(self.add_MOG)
        btn_Rename.clicked.connect(self.rename)
        btn_Remove_MOG.clicked.connect(self.del_MOG)
        btn_Raw_Data.clicked.connect(self.plot_rawdata)
        #--- Sub Widgets ---#

        #- Sub AirShots Widget-#
        Sub_AirShots_Widget                 = QtGui.QWidget()
        Sub_AirShots_Grid                   = QtGui.QGridLayout()
        Sub_AirShots_Grid.addWidget(Type_label, 0, 1)
        Sub_AirShots_Grid.addWidget(Tx_label, 1, 1)
        Sub_AirShots_Grid.addWidget(Rx_label, 2, 1)
        Sub_AirShots_Grid.addWidget(self.Type_combo, 0, 2, 1, 2)
        Sub_AirShots_Grid.addWidget(self.Tx_combo, 1, 2, 1, 2)
        Sub_AirShots_Grid.addWidget(self.Rx_combo, 2, 2, 1, 2)
        Sub_AirShots_Grid.addWidget(Air_shots_checkbox, 3, 0)
        Sub_AirShots_Grid.addWidget(btn_Air_Shot_Before, 4, 0, 1, 2)
        Sub_AirShots_Grid.addWidget(btn_Air_Shot_After, 5, 0, 1, 2)
        Sub_AirShots_Grid.addWidget(self.Air_Shot_Before_edit, 4, 2, 1, 2)
        Sub_AirShots_Grid.addWidget(self.Air_Shot_After_edit, 5, 2, 1, 2)
        Sub_AirShots_Widget.setLayout(Sub_AirShots_Grid)


        #- Sub Labels, Checkbox and Edits Widget -#
        Sub_Labels_Checkbox_and_Edits_Widget = QtGui.QWidget()
        Sub_Labels_Checkbox_and_Edits_Grid   = QtGui.QGridLayout()
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Nominal_Frequency_label,0, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Rx_Offset_label,1, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Correction_Factor_checkbox, 3, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Tx_Offset_label,2, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Multiplication_Factor_label,4, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Date_label,7, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Nominal_Frequency_edit,0, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Rx_Offset_edit,1, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Tx_Offset_edit,2, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Correction_Factor_edit,3, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Multiplication_Factor_edit,4, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Date_edit, 7, 2)
        Sub_Labels_Checkbox_and_Edits_Widget.setLayout(Sub_Labels_Checkbox_and_Edits_Grid)

        #- Sub Right Buttons Widget -#
        sub_right_buttons_widget            = QtGui.QWidget()
        sub_right_buttons_Grid              = QtGui.QGridLayout()
        sub_right_buttons_Grid.addWidget(btn_Rename, 1, 1)
        sub_right_buttons_Grid.addWidget(btn_Import, 1, 2)
        sub_right_buttons_Grid.addWidget(btn_Merge, 1, 3)
        sub_right_buttons_Grid.addWidget(btn_Raw_Data, 2, 1)
        sub_right_buttons_Grid.addWidget(btn_Trace_ZOP, 2, 2)
        sub_right_buttons_Grid.addWidget(btn_Spectra, 2, 3)
        sub_right_buttons_Grid.addWidget(btn_Stats_tt, 3, 1)
        sub_right_buttons_Grid.addWidget(btn_Stats_Ampl, 3, 2)
        sub_right_buttons_Grid.addWidget(btn_Ray_Coverage, 3, 3)
        sub_right_buttons_Grid.addWidget(btn_Export_tt, 4, 1)
        sub_right_buttons_Grid.addWidget(btn_export_tau, 4, 2)
        sub_right_buttons_Grid.addWidget(btn_Prune, 4, 3)
        sub_right_buttons_Grid.setVerticalSpacing(0)
        sub_right_buttons_Grid.setHorizontalSpacing(0)
        sub_right_buttons_Grid.setRowStretch(0, 100)
        sub_right_buttons_Grid.setRowStretch(5, 100)
        sub_right_buttons_Grid.setColumnStretch(0, 100)
        sub_right_buttons_Grid.setColumnStretch(5, 100)
        sub_right_buttons_widget.setLayout(sub_right_buttons_Grid)

        #- MOG and list Sub Widget -#
        sub_MOG_and_List_widget            = QtGui.QWidget()
        sub_MOG_and_List_Grid              = QtGui.QGridLayout()
        sub_MOG_and_List_Grid.addWidget(btn_Add_MOG, 0, 0, 1, 2)
        sub_MOG_and_List_Grid.addWidget(btn_Remove_MOG, 0, 2, 1, 2)
        sub_MOG_and_List_Grid.addWidget(self.MOG_list, 1, 0, 1, 4)
        sub_MOG_and_List_widget.setLayout(sub_MOG_and_List_Grid)

        #------- Grid Disposition -------#
        master_grid                        = QtGui.QGridLayout()
        #--- Sub Widgets Disposition ---#
        master_grid.addWidget(sub_MOG_and_List_widget, 0, 0)
        master_grid.addWidget(sub_right_buttons_widget, 0, 1)
        master_grid.addWidget(Sub_Labels_Checkbox_and_Edits_Widget, 1, 1)
        master_grid.addWidget(Sub_AirShots_Widget, 1, 0)
        master_grid.setColumnStretch(1, 300)
        self.setLayout(master_grid)

class RawDataFig(FigureCanvasQTAgg):

    def __init__(self):
        fig = mpl.figure.Figure(facecolor='white')
        super(RawDataFig, self).__init__(fig)
        self.initFig()


    def initFig(self):
        ax = self.figure.add_axes([0.05, 0.08, 0.9, 0.9])
        divider = make_axes_locatable(ax)
        divider.append_axes('right', size= 0.5, pad= 0.1)
        ax.set_axisbelow(True)


    def plot_raw_data(self, mogd):
        ax1 = self.figure.axes[0]
        ax2 = self.figure.axes[1]
        ax1.cla()
        ax2.cla()
        mpl.axes.Axes.set_xlabel(ax1, 'Trace No')
        mpl.axes.Axes.set_ylabel(ax1, 'Time units[{}]'.format(mogd.tunits))
        cmax = np.abs(max(mogd.rdata.flatten()))
        h = ax1.imshow(mogd.rdata,cmap='seismic', interpolation='none',aspect= 'auto', vmin= -cmax, vmax= cmax  )
        mpl.colorbar.Colorbar(ax2, h)

        self.draw()





if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)


    MOGUI_ui = MOGUI()
    MOGUI_ui.show()

    #MOGUI_ui.load_file_MOG('testData/formats/ramac/t0102.rad')
    #MOGUI_ui.plot_rawdata()


    sys.exit(app.exec_())
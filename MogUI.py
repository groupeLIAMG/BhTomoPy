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
    moglogSignal = QtCore.pyqtSignal(str)


    def __init__(self, parent=None):
        super(MOGUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/MOGs")
        self.MOGs = []
        self.air = []
        self.data_rep = ''
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

        else:
            self.moglogSignal.emit("Error: MOG file must have either *.rad, *.rd3 or *.tlf extension")
            return

        for rep in basename.split('/')[:-1]:
            self.data_rep = self.data_rep + rep + '/'
        self.data_rep = self.data_rep[:-1]

        mog = Mog(rname)
        self.MOGs.append(mog)
        self.update_List_Widget()
        mog.data.readRAMAC(basename)
        self.MOG_list.setCurrentRow(len(self.MOGs) - 1)
        self.update_spectra_Tx_num_list()
        self.update_spectra_Tx_elev_value_label()
        self.update_edits()
        self.moglogSignal.emit("{} Multi Offset-Gather as been loaded succesfully".format(rname))

    def update_edits(self):
        """
        this function updates the info either in the  MOG's edits or in the info's labels

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
            self.moglogSignal.emit("MOG {} as been deleted".format(self.MOGs[int(i.row())].name))
            del self.MOGs[int(i.row())]
        self.update_List_Widget()

    def rename(self):
        ind = self.MOG_list.selectedIndexes()
        new_name, ok = QtGui.QInputDialog.getText(self, "Rename", 'new MOG name')
        if ok:
            for i in ind:
                self.moglogSignal.emit("MOG {} is now {}".format(self.MOGs[int(i.row())].name, new_name))
                self.MOGs[int(i.row())] = new_name
        self.update_List_Widget()


    def airBefore(self):
        old_rep = os.getcwd()       # this operation gets the first directory
        if len(self.data_rep) != 0 :
            os.chdir(self.data_rep) # if one already have uploaded a file, the next time will be at the same path
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open t0 air shot before survey')
        os.chdir(old_rep)
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
                    if str(basename) in str(self.air[n].name):
                        self.MOGs[i.row()].av = n
                        found = True
                        break

                if not found:
                    n = len(self.air)
                    print(n)
                    print(self.air)

                    data = MogData()
                    data.readRAMAC(basename)
                    print(data.ntrace)

                    distance, ok = QtGui.QInputDialog.getText(self, 'Aishots Before', 'Distance between Tx and Rx :')
                    if ok :
                        distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance)

                        if len(distance_list) > 1:
                            if len(distance_list)!= data.ntrace:
                                self.moglogSignal.emit('Error : Number of positions inconsistent with number of traces')
                                return

                        self.air.append(AirShots(str(rname)))
                        self.air[n].data = data
                        self.air[n].tt = -1* np.ones((1, data.ntrace))
                        self.air[n].et = -1* np.ones((1, data.ntrace))
                        self.air[n].tt_done = np.zeros((1, data.ntrace), dtype=bool)
                        self.air[n].d_TxRx = distance_list
                        self.air[n].fac_dt = 1
                        self.air[n].ing = np.ones((1, data.ntrace), dtype= bool)

                        if len(distance_list) == 1:
                            self.air[n].method ='fixed_antenna'
                        else:
                            self.air[n].method ='walkaway'
                        self.Air_Shot_Before_edit.setText(self.air[n].name[:-4])


    def airAfter(self):
        old_rep = os.getcwd()
        if len(self.mogdata.data_rep) != 0 :
            os.chdir(self.mogdata.data_rep)

        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open t0 air shot before survey')
        os.chdir(old_rep)
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
                    if str(basename) in str(self.air[n].name):
                        self.MOGs[i.row()].ap = n
                        found = True
                        break

                if not found:
                    n = len(self.air) + 1

                    data = MogData()
                    data.readRAMAC(basename)

                    distance, ok = QtGui.QInputDialog.getText(self, "Distance", 'Enter distance between Tx and Rx')
                    if ok:
                        distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance)

                        if len(distance_list) > 1:
                            if len(distance_list)!= data.ntrace:
                                self.moglogSignal.emit('Error : Number of positions inconsistent with number of traces')
                                return

                        self.air[n] = AirShots(str(rname))
                        self.air[n].data = data
                        self.air[n].tt = -1* np.ones((1, data.ntrace))
                        self.air[n].et = -1* np.ones((1, data.ntrace))
                        self.air[n].tt_done = np.zeros((1, data.ntrace), dtype=bool)
                        self.air[n].d_TxRx = distance_list
                        self.air[n].fac_dt = 1
                        self.air[n].ing = np.ones((1, data.ntrace), dtype= bool)

                        if len(distance_list) == 1:
                            self.air[n].method ='fixed_antenna'
                        else:
                            self.air[n].method ='walkaway'
                        self.Air_Shot_After_edit.setText(self.air[n].name[:-4])


    def spectra(self, mog):
        Amax = max(mog.data.rdata.flatten())
        normalised_rdata = mog.data.rdata/Amax

        n = self.Tx_num_list.selectedIndexes()

        dt = mog.data.timec * mog.fac_dt
        Tx = mog.data.Tx_z

        ind = Tx[n]

        traces = normalised_rdata[:, ind]

        nfft = 'TODO'

        fac_f = 1.0
        fac_t = 1.0

        if 'ns' in mog.data.tunits:
            # if the time units are in nanoseconds, the antenna's nominal frenquency is in MHz
            fac_f = 10**6
            fac_t = 10**-9

        elif 'ms' in mog.data.tunits:
            # if the time units are in miliseconds, we assume the dominant frequency to be in kHz
            fac_f = 10**3
            fac_t = 10**-3
            self.info_label.setText("Assuming Tx's nominal frequency is in kHz")

        else:
            self.info_label.setText("Assuming Tx's nominal frequency is in kHz \n and the time step in seconds")

        f0 = mog.data.rnomfreq * fac_f
        dt = dt * fac_t
        Fs = 1/dt

        # Noise on the last 20 ns
        win_snr = np.round(20/mog.data.timec)



#TODO:
    def import_mog(self):
        pass
    def merge(self):
        pass
    def trace_zop(self):
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

    def update_spectra_Tx_num_list(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]
        self.Tx_num_list.clear()
        for Tx in range(len(mog.data.Tx_z)+1):
            self.Tx_num_list.addItem(str(Tx))

    def update_spectra_Tx_elev_value_label(self):
        ind1 = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind1[0].row()]
        self.Tx_elev_value_label.clear()
        ind = self.Tx_num_list.selectedIndexes()
        for j in ind:
            self.Tx_elev_value_label.setText(str((list(mog.data.Tx_z))[j.row()]))

    def search_Tx_elev(self):
        if self.search_combo.currentText() == 'Search with Elevation':
            item = float(self.search_elev_edit.text())
            ind = self.MOG_list.selectedIndexes()
            for i in range(len(self.MOGs[ind[0].row()].data.Tx_z)):
                if self.MOGs[ind[0].row()].data.Tx_z[i] == item:
                    self.Tx_num_list.setCurrentRow(i)
                elif item not in self.MOGs[ind[0].row()].data.Tx_z:
                    idx = np.argmin((np.abs(self.MOGs[ind[0].row()].data.Tx_z-item)))
                    self.Tx_num_list.setCurrentRow(idx)
                    green = QtGui.QPalette()
                    green.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkCyan)
                    self.info_label.setText('{} is not a value in this data, {} is the closest'.format(item, np.around(self.MOGs[ind[0].row()].data.Tx_z[idx], decimals=1 )))
                    self.info_label.setPalette(green)
                self.update_spectra_Tx_elev_value_label()
        elif self.search_combo.currentText() == 'Search with Number':
            item = float(self.search_elev_edit.text())
            if item in range(len(self.Tx_num_list)):
                self.Tx_num_list.setCurrentRow(item)
            else:
                red = QtGui.QPalette()
                red.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
                self.info_label.setText('This data contains only {} traces, {} is out of range'.format(len(self.Tx_num_list) -1, int(item)))
                self.info_label.setPalette(red)


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
            self.rawdataFig.plot_raw_data(self.MOGs[i.row()].data)
            self.moglogSignal.emit(" MOG {}'s Raw Data as been plotted ". format(self.MOGs[i.row()].name))
            self.rawdatamanager.show()

    def plot_spectra(self):
        ind = self.MOG_list.selectedIndexes()
        for i in ind:
            self.spectraFig.plot_spectra(self.MOGs[i.row()].data)
            self.moglogSignal.emit(" MOG {}'s Spectra as been plotted ". format(self.MOGs[i.row()].name))
            self.spectramanager.showMaximized()

    def initUI(self):

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

        #------ Creation of the Manager for the raw Data figure -------#
        self.rawdataFig = RawDataFig()
        self.rawdatatool = NavigationToolbar2QT(self.rawdataFig, self)
        self.rawdatamanager = QtGui.QWidget()
        rawdatamanagergrid = QtGui.QGridLayout()
        rawdatamanagergrid.addWidget(self.rawdatatool, 0, 0)
        rawdatamanagergrid.addWidget(self.rawdataFig, 1, 0)
        self.rawdatamanager.setLayout(rawdatamanagergrid)


        #--- Widgets in Spectra ---#
        #- Labels -#
        Tx_num_label = MyQLabel(('Tx Number'), ha='center')
        Tx_elev_label = QtGui.QLabel('Tx elevation: ')
        self.Tx_elev_value_label = QtGui.QLabel('')
        psd_label = MyQLabel(('PSD Estimation Method'), ha= 'center')
        f_max_label = MyQLabel(('F Max'), ha='center')
        snr_label = MyQLabel(('SNR Scale'), ha='center')
        f_min_label = MyQLabel(('F Max'), ha='right')
        f_maxi_label = MyQLabel(('F Max'), ha='right')
        self.search_info_label = MyQLabel((''), ha= 'center')
        self.info_label = MyQLabel((''), ha= 'center')

        #- Edits -#
        self.f_max_edit = QtGui.QLineEdit()
        self.f_min_edit = QtGui.QLineEdit()
        self.f_maxi_edit = QtGui.QLineEdit()
        self.search_elev_edit = QtGui.QLineEdit()
        #- Edits disposition -#
        self.search_elev_edit.editingFinished.connect(self.search_Tx_elev)
        self.search_elev_edit.setFixedWidth(100)
        #- Comboboxes -#
        self.Tx_num_combo = QtGui.QComboBox()
        self.search_combo = QtGui.QComboBox()
        self.psd_combo = QtGui.QComboBox()
        self.snr_combo = QtGui.QComboBox()

        #- Combobox Items -#
        self.search_combo.addItem('Search with Elevation')
        self.search_combo.addItem('Search with Number')


        #- List Widget -#
        self.Tx_num_list = QtGui.QListWidget()
        self.Tx_num_list.itemSelectionChanged.connect(self.update_spectra_Tx_elev_value_label)

        #- Checkboxes -#
        self.filter_check = QtGui.QCheckBox('Apply Low Pass Filter')
        self.compute_check = QtGui.QCheckBox('Compute & Show')

        #- elevation SubWidget -#
        sub_elev_widget = QtGui.QWidget()
        sub_elev_grid = QtGui.QGridLayout()
        sub_elev_grid.addWidget(Tx_elev_label, 0, 0)
        sub_elev_grid.addWidget(self.Tx_elev_value_label, 0, 1)
        sub_elev_grid.setContentsMargins(0, 0, 0, 0)
        sub_elev_widget.setLayout(sub_elev_grid)

        #- list top SubWidget -#
        sub_Tx_widget = QtGui.QWidget()
        sub_Tx_grid = QtGui.QGridLayout()
        sub_Tx_grid.addWidget(Tx_num_label, 0, 0)
        sub_Tx_grid.addWidget(self.search_combo, 0, 1)
        sub_Tx_grid.addWidget(self.search_elev_edit, 1, 1)
        sub_Tx_widget.setLayout(sub_Tx_grid)

        #- first SubWidget -#
        sub_first_widget            = QtGui.QWidget()
        sub_first_grid              = QtGui.QGridLayout()
        sub_first_grid.addWidget(sub_Tx_widget, 0, 0)
        sub_first_grid.addWidget(self.Tx_num_list, 1, 0)
        sub_first_grid.addWidget(sub_elev_widget, 2, 0)
        sub_first_grid.addWidget(psd_label, 5, 0)
        sub_first_grid.addWidget(self.psd_combo, 6, 0)
        sub_first_grid.addWidget(f_max_label, 8, 0)
        sub_first_grid.addWidget(self.f_max_edit, 9, 0)
        sub_first_grid.addWidget(snr_label, 11, 0)
        sub_first_grid.addWidget(self.snr_combo, 12, 0)
        sub_first_grid.addWidget(self.filter_check, 13, 0)
        sub_first_widget.setLayout(sub_first_grid)


        #- Dominant frequency Groupbox -#
        dominant_frequency_GroupBox =  QtGui.QGroupBox("Dominant Frequency")
        dominant_frequency_Grid     = QtGui.QGridLayout()
        dominant_frequency_Grid.addWidget(f_min_label, 0, 0)
        dominant_frequency_Grid.addWidget(self.f_min_edit, 0, 1)
        dominant_frequency_Grid.addWidget(f_maxi_label, 1, 0)
        dominant_frequency_Grid.addWidget(self.f_maxi_edit, 1, 1)
        dominant_frequency_Grid.addWidget(self.compute_check, 2, 0)
        dominant_frequency_GroupBox.setLayout(dominant_frequency_Grid)

        #- Total Subwidget -#
        sub_total_widget = QtGui.QWidget()
        sub_total_grid = QtGui.QGridLayout()
        sub_total_grid.addWidget(sub_first_widget, 0, 0)
        sub_total_grid.addWidget(dominant_frequency_GroupBox, 2, 0)
        sub_total_grid.setRowStretch(1, 100)
        sub_total_widget.setLayout(sub_total_grid)


        #------ Creation of the Manager for the Spectra figure -------#

        self.spectraFig = SpectraFig()
        self.spectratool = NavigationToolbar2QT(self.spectraFig, self)
        self.spectramanager = QtGui.QWidget()
        spectramanagergrid = QtGui.QGridLayout()
        spectramanagergrid.addWidget(self.spectratool, 0, 0)
        spectramanagergrid.addWidget(self.info_label, 0, 2)
        spectramanagergrid.addWidget(self.search_info_label, 0, 6)
        spectramanagergrid.addWidget(self.spectraFig, 1, 0, 1, 6)
        spectramanagergrid.addWidget(sub_total_widget, 1, 6)
        spectramanagergrid.setColumnStretch(1, 100)
        self.spectramanager.setLayout(spectramanagergrid)


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
        btn_Spectra.clicked.connect(self.plot_spectra)
        btn_Air_Shot_Before.clicked.connect(self.airBefore)
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
        master_grid.setContentsMargins(0, 0, 0, 0)
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

class SpectraFig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(facecolor= 'white')
        super(SpectraFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        ax1 = self.figure.add_axes([0.08, 0.06, 0.3, 0.9])
        ax2 = self.figure.add_axes([0.42, 0.06, 0.3, 0.9])
        ax3 = self.figure.add_axes([0.78, 0.06, 0.2, 0.9])
        ax1.yaxis.set_ticks_position('left')
        ax1.set_axisbelow(True)

    def plot_spectra(self, mogd):
        ax1 = self.figure.axes[0]
        ax2 = self.figure.axes[1]
        ax3 = self.figure.axes[2]
        ax1.cla()
        ax2.cla()
        ax3.cla()
        mpl.axes.Axes.set_title(ax1, 'Normalized amplitude')
        mpl.axes.Axes.set_title(ax2, 'Log Power spectra')
        mpl.axes.Axes.set_title(ax3, 'Signal-to-Noise Ratio')
        mpl.axes.Axes.set_xlabel(ax1, ' Time [{}]'.format(mogd.tunits))
        mpl.axes.Axes.set_ylabel(ax1, 'Rx elevation [{}]'.format(mogd.cunits))
        mpl.axes.Axes.set_xlabel(ax2, 'Frequency [MHz]')
        mpl.axes.Axes.set_xlabel(ax3, 'SNR')



if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)


    MOGUI_ui = MOGUI()
    #MOGUI_ui.show()

    MOGUI_ui.load_file_MOG('testData/formats/ramac/t0302.rad')
    MOGUI_ui.plot_spectra()
    #MOGUI_ui.plot_rawdata()


    sys.exit(app.exec_())
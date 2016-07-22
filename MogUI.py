# -*- coding: utf-8 -*-
import sys
import os
from PyQt4 import QtGui, QtCore
from MogData import MogData
from mog import Mog, AirShots
from database import Database
from ModelUI import gridUI
from unicodedata import *
import matplotlib as mpl
import scipy as spy
from scipy import signal
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
import numpy as np
from numpy import linalg
from numpy import matlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d
import re


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Multi Offset Gather User Interface (MOGUI) Class
#
#-----------------------------------------------------------------------------------------------------------------------
class MOGUI(QtGui.QWidget):

    mogInfoSignal = QtCore.pyqtSignal(int)
    ntraceSignal = QtCore.pyqtSignal(int)
    databaseSignal = QtCore.pyqtSignal(str)
    moglogSignal = QtCore.pyqtSignal(str)


    def __init__(self, borehole, parent=None):
        super(MOGUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/MOGs")
        self.MOGs = []
        self.air = []
        self.borehole = borehole
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

        mogdata = MogData(rname)
        mogdata.readRAMAC(basename)
        mog = Mog(rname, mogdata)
        self.MOGs.append(mog)
        self.update_List_Widget()
        self.MOG_list.setCurrentRow(len(self.MOGs) - 1)
        self.update_spectra_Tx_num_list()
        self.update_spectra_Tx_elev_value_label()
        self.update_edits()
        self.update_prune_edits_info()
        self.update_prune_info()
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

            for i in range(len(self.borehole.boreholes)):
                if mog.Tx ==1 and mog.Rx ==1 :
                    pass
                elif mog.Tx.name == self.borehole.boreholes[i].name:
                    self.Tx_combo.setCurrentIndex(i)

                elif mog.Rx.name == self.borehole.boreholes[i].name:
                    self.Rx_combo.setCurrentIndex(i)
            tot_traces = 0
            for mog in self.MOGs:
                tot_traces += mog.data.ntrace
            self.ntraceSignal.emit(tot_traces)


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
                self.MOGs[int(i.row())].name = new_name
        self.update_List_Widget()



    def airBefore(self):
        # this operation gets the first directory
        old_rep = os.getcwd()
        if len(self.data_rep) != 0 :
            # if one have already  uploaded a file, the next time will be at the same path
            os.chdir(self.data_rep)

        # then we get the filename to process
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open t0 air shot before survey')
        os.chdir(old_rep)
        if not filename:
            # security for an empty filename
            return
        else:
            # We get the selected index f MOG_list to then be able to get the mog instance from MOGS
            ind = self.MOG_list.selectedIndexes()

            # the object ind contains all the selected indexes
            for i in ind:
                #then we get only the real name of the file(i.e. not the path behind it)
                basename = filename[:-4]
                rname = filename.split('/')
                rname = rname[-1]
                found = False

                for n in range(len(self.air)):
                    # then we verify if we've already applied the airshots
                    if str(basename) in str(self.air[n].name):
                        # then we associate the index of the air shot to the selected mog
                        self.MOGs[i.row()].av = n
                        found = True
                        break

                if not found:
                    n = len(self.air)

                    # because of the fact that Airshots files are either rd3, tlf or rad , we apply the method read
                    # ramac to get the informations frome these files
                    try:
                        data = MogData()
                        data.readRAMAC(basename)
                    except:
                        self.moglogSignal.emit('Error: AirShot File must have *.rad, *.tlf or *.rd3 extension')
                        return

                    # Then we ask if the airshots were done in a sucession of positions or at a fixed posisitons
                    distance, ok = QtGui.QInputDialog.getText(self, 'Aishots Before', 'Distance between Tx and Rx :')

                    # The getText method returns a tuple containing the entered data and a boolean factor
                    # (i.e. if the ok button is clicked, it returns True)
                    if ok :
                        distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance)

                        if len(distance_list) > 1:
                            if len(distance_list)!= data.ntrace:
                                self.moglogSignal.emit('Error: Number of positions inconsistent with number of traces')
                                return
                        airshot_before = AirShots(str(rname))
                        self.air.append(airshot_before)
                        self.air[n].data = data
                        self.air[n].tt = -1* np.ones(data.ntrace) # tt stands for the travel time vector
                        self.air[n].et = -1* np.ones(data.ntrace) # to be defined
                        self.air[n].tt_done = np.zeros(data.ntrace, dtype=bool) # the tt_done is a zeros array and whenever a ray arrives,
                                                                                # its value will be changed to one
                        self.air[n].d_TxRx = distance_list  # Contains all the positions for which the airshots have been made
                        self.air[n].fac_dt = 1  # to be defined
                        self.air[n].in_vect = np.ones(data.ntrace, dtype= bool) # in_vect is the vector which help to plot the figures of Airshots

                        if len(distance_list) == 1:
                            self.air[n].method ='fixed_antenna'
                        else:
                            self.air[n].method ='walkaway'
                        self.Air_Shot_Before_edit.setText(self.air[n].name[:-4])


    def airAfter(self):
        # As you can see, the air After method is almost the same as airBefore (refer to airBefore for any questions)
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
                                self.moglogSignal.emit('Error: Number of positions inconsistent with number of traces')
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


    def detrend_rad(self, inp):
        """

        :param inp: the input data to be straightenend
        :return:
        """
        n =30
        m = np.shape(inp)[0]
        m1 = np.mean(inp[0:n,])
        m2 = np.mean(inp[(m-n-1):m,])

        dm = (m2 - m1)/(m-1)

        x = np.matlib.repmat(m1, m, 1)

        subtract = np.add(x[0]*np.ones(m), np.arange(m)*dm)

        out = np.zeros(np.shape(inp))
        for n in range(np.shape(inp)[1]):
            out[:, n]= np.subtract(inp[:, n], subtract)

        return out

    def update_spectra_Tx_num_list(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]
        self.Tx_num_list.clear()
        unique_Tx_z = np.unique(mog.data.Tx_z)

        for Tx in range(len(unique_Tx_z)):
            self.Tx_num_list.addItem(str(Tx))

        self.Tx_num_list.setCurrentRow(0)


    def update_spectra_Tx_elev_value_label(self):
        ind1 = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind1[0].row()]
        self.Tx_elev_value_label.clear()
        ind = self.Tx_num_list.selectedIndexes()
        unique_Tx_z = np.unique(mog.data.Tx_z)
        for j in ind:
            self.Tx_elev_value_label.setText(str((list(unique_Tx_z))[j.row()]))

    def search_Tx_elev(self):
        if self.search_combo.currentText() == 'Search with Elevation':
            try:
                item = float(self.search_elev_edit.text())
            except:
                pass
            ind = self.MOG_list.selectedIndexes()
            for i in range(len(self.MOGs[ind[0].row()].data.Tx_z)):
                if self.MOGs[ind[0].row()].data.Tx_z[i] == item:
                    self.Tx_num_list.setCurrentRow(i)
                elif item not in self.MOGs[ind[0].row()].data.Tx_z:
                    idx = np.argmin((np.abs(self.MOGs[ind[0].row()].data.Tx_z-item)))
                    self.Tx_num_list.setCurrentRow(idx)
                    green = QtGui.QPalette()
                    green.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkCyan)
                    self.search_info_label.setText('{} is not a value in this data, {} is the closest'.format(item, np.around(self.MOGs[ind[0].row()].data.Tx_z[idx], decimals=1 )))
                    self.search_info_label.setPalette(green)
                self.update_spectra_Tx_elev_value_label()

        elif self.search_combo.currentText() == 'Search with Number':
            item = float(self.search_elev_edit.text())
            if item in range(len(self.Tx_num_list)):
                self.Tx_num_list.setCurrentRow(item)
            else:
                red = QtGui.QPalette()
                red.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
                self.search_info_label.setText('This data contains only {} traces, {} is out of range'.format(len(self.Tx_num_list) -1, int(item)))
                self.search_info_label.setPalette(red)

    def update_List_Widget(self):
        self.MOG_list.clear()
        for mog in self.MOGs:
            self.MOG_list.addItem(mog.name)
        self.mogInfoSignal.emit(len(self.MOG_list))


    def update_Tx_and_Rx_Widget(self, liste):
        self.Tx_combo.clear()
        self.Rx_combo.clear()
        for bh in liste:
            self.Tx_combo.addItem(bh.name)
            self.Rx_combo.addItem(bh.name)

    def updateCoords(self):
        ind = self.MOG_list.selectedIndexes()
        iTx = self.Tx_combo.currentIndex()
        iRx = self.Rx_combo.currentIndex()
        for i in ind:
            mog = self.MOGs[i.row()]

            if 'true positions' in mog.data.comment:

                Tx = np.array([mog.data.Tx_x, mog.data.Tx_y, mog.data.Tx_z])
                mog.TxCosDir = np.zeros(np.shape(Tx))

                # Equivalent of unique(Tx, 'rows') of the Matlab version
                b = np.ascontiguousarray(Tx).view(np.dtype((np.void, Tx.dtype.itemsize * Tx.shape[1])))
                tmp = np.unique(b).view(Tx.dtype).reshape(-1, Tx.shape[1])
                tmp = np.sort(tmp, axis=0)
                tmp = tmp[::-1]
                v   = -np.diff(tmp, axis=0)
                # voir quel est le résultat espéré pour d
                # même chose pour l



                #TODO:
                #for n in range(np.shape(tmp)[0]):
                #    ind = Tx[:,1] == tmp[n, 1] and Tx[:,2] == tmp[n, 2] and Tx[:,3] == tmp[n, 3]
                #    mog.TxCosDir[ind, 1] = l[n,1]
                #    mog.TxCosDir[ind, 2] = l[n,2]
                #    mog.TxCosDir[ind, 3] = l[n,3]



            Tx = self.borehole.boreholes[iTx]
            Rx = self.borehole.boreholes[iRx]
            mog.Tx = Tx
            mog.Rx = Rx
            mog.data.Tx_x = np.ones(mog.data.ntrace)
            mog.data.Tx_y = np.ones(mog.data.ntrace)
            mog.data.Rx_x = np.ones(mog.data.ntrace)
            mog.data.Rx_y = np.ones(mog.data.ntrace)

            if self.Type_combo.currentText() == 'Crosshole':
                mog.data.csurvmod = 'SURVEY MODE       = Trans. -MOG'

            elif self.Type_combo.currentText() == 'VSP/VRP':
                mog.data.csurvmod = 'SURVEY MODE       = Trans. -VRP'

            if iTx == iRx:
                dialog = QtGui.QMessageBox.information(self, 'Warning', 'Both Tx and Rx are in the same well',
                                                       buttons=QtGui.QMessageBox.Ok)

            if len(Tx.fdata[:,0]) == 2 and len(Tx.fdata[:,1]) == 2 :
                if abs(Tx.fdata[0, 0] - Tx.fdata[-1, 0]) < 1e-05 and abs(Tx.fdata[0, 1] - Tx.fdata[-1, 1]) < 1e-05 :
                    mog.data.Tx_x = Tx.fdata[0, 0] * np.ones(mog.data.ntrace)
                    mog.data.Tx_y = Tx.fdata[0, 1] * np.ones(mog.data.ntrace)

            if len(Rx.fdata[:, 0]) == 2 and len(Rx.fdata[:, 1]) == 2:
                if abs(Rx.fdata[0, 0] - Rx.fdata[-1, 0]) < 1e-05 and abs(Rx.fdata[0, 1] - Rx.fdata[-1, 1]) <1e-05 :
                    mog.data.Rx_x = Rx.fdata[0, 0] * np.ones(mog.data.ntrace)
                    mog.data.Rx_y = Rx.fdata[0, 1] * np.ones(mog.data.ntrace)

            if Tx != Rx:
                self.moglogSignal.emit("{}'s Tx and Rx are now {} and {}".format(mog.name, Tx.name, Rx.name))


    def plot_rawdata(self):
        ind = self.MOG_list.selectedIndexes()
        for i in ind:
            self.rawdataFig.plot_raw_data(self.MOGs[i.row()].data)
            self.moglogSignal.emit(" MOG {}'s Raw Data as been plotted ". format(self.MOGs[i.row()].name))
            self.rawdatamanager.showMaximized()

    def plot_spectra(self):
        ind                 = self.MOG_list.selectedIndexes()
        n                   = self.Tx_num_list.currentIndex().row()
        mog                 = self.MOGs[ind[0].row()]
        Fmax                = float(self.f_max_edit.text())
        filter_state        = self.filter_check.isChecked()
        scale               = self.snr_combo.currentText()
        estimation_method   = self.psd_combo.currentText()


        self.spectraFig.plot_spectra(mog, n, Fmax, filter_state, scale, estimation_method)
        #self.moglogSignal.emit(" MOG {}'s Spectra as been plotted ". format(mog.name))
        self.spectramanager.showMaximized()

    def plot_zop(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]

        if mog.data.rstepsz == 0:
            self.tol_edit.setText('0.5')
        else:
            self.tol_edit.setText(str(mog.data.rstepsz * 0.5))

        self.zopFig.plot_zop(mog)
        self.moglogSignal.emit(" MOG {}'s Zero-Offset Profile as been plotted ". format(self.MOGs[ind[0].row()].name))
        self.zopmanager.showMaximized()

    def plot_zop_rays(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]
        tol = float(self.tol_edit.text())
        self.zopraysFig.plot_rays(mog, tol)
        self.zopraysmanager.show()


    def plot_statstt(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]
        done = (mog.tt_done.astype(int) + mog.in_vect.astype(int)) - 1
        if len(np.nonzero(done == 1)[0]) == 0:
            dialog = QtGui.QMessageBox.warning(self, 'Warning', "Data not processed",
                                                   buttons=QtGui.QMessageBox.Ok)

        else:
            self.statsttFig.plot_stats(mog, self.air)
            self.moglogSignal.emit("MOG {}'s Traveltime statistics have been plotted".format(self.MOGs[ind[0].row()].name))
            self.statsttmanager.showMaximized()

    def plot_statsamp(self):
        ind = self.MOG_list.selectedIndexes()
        self.statsampFig.plot_stats(self.MOGs[ind[0].row()])
        self.moglogSignal.emit("MOG {}'s Amplitude statistics have been plotted".format(self.MOGs[ind[0].row()].name))
        self.statsampmanager.showMaximized()

    def plot_ray_coverage(self):
        ind = self.MOG_list.selectedIndexes()
        self.raycoverageFig.plot_ray_coverage(self.MOGs[ind[0].row()])
        self.moglogSignal.emit("MOG {}'s Ray Coverage have been plotted".format(self.MOGs[ind[0].row()].name))
        self.raymanager.show()

    def plot_prune(self):
        ind = self.MOG_list.selectedIndexes()
        self.pruneFig.plot_prune(self.MOGs[ind[0].row()], 0 )
        self.moglogSignal.emit("MOG {}'s Prune have been plotted".format(self.MOGs[ind[0].row()].name))
        self.prunemanager.show()


    def export_tt(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Export tt')
        self.moglogSignal.emit('Exporting Traveltime file ...')
        self.moglogSignal.emit('File exported succesfully ')

    def export_tau(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Export tau')
        self.moglogSignal.emit('Exporting tau file ...')
        self.moglogSignal.emit('File exported succesfully ')

    #TODO:
    def compute_SNR(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]
        SNR = np.ones(mog.data.ntrace)

        max_amps = np.amax(np.abs(self.detrend_rad(mog.data.rdata)))
        i = np.nonzero(np.abs(self.detrend_rad(mog.data.rdata)) == max_amps)[0]

        width = 60

        i1 = i - width / 2
        i2 = i + width / 2
        i1[i1 < 1] = 1
        i2[i2 > mog.data.nptsptrc] = mog.data.nptsptrc

        for n in range(mog.data.ntrace):
            SNR[n] = np.std(mog.data.rdata[i1[n]:i2[n], n]) / np.std(mog.data.rdata[:width, n])

        return SNR

    def update_prune(self):
        """
        This method updates the figure containing the points of Tx and Rx
        with the information which is into the different edits of the prune widget
        """
        # First, we get the mog instance's informations
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]

        # List which contain the indexes of the skipped Tx and Rx
        inRx = []
        inTx = []

        # Reinitialisation of the boolean vectors before modification
        mog.in_Rx_vect = np.ones(mog.data.ntrace, dtype= bool)
        mog.in_Tx_vect = np.ones(mog.data.ntrace, dtype= bool)

        # Information from all the edits of the prune widget
        new_min = float(self.min_elev_edit.text())
        new_max = float(self.max_elev_edit.text())
        skip_len_Rx = int(self.skip_Rx_edit.text())
        skip_len_Tx = int(self.skip_Tx_edit.text())
        round_factor = float(self.round_fac_edit.text())
        use_snr = self.tresh_check.isChecked()
        treshold_snr = float(self.tresh_edit.text())
        ang_min = float(self.min_ang_edit.text())
        ang_max = float(self.max_ang_edit.text())

        #-These steps are for the constraining of the Tx's ad Rx's elevation--------------------------------------------
        # Because the truth of multiple values array is ambiguous, we have to do these steps

        # We first create a boolean vector which will have a True value if the elevation is greater or equals the new min
        # and will be False the other way
        min_Tx = np.greater_equal(-np.unique(mog.data.Tx_z),new_min)
        min_Rx = np.greater_equal(-np.unique(np.sort(mog.data.Rx_z)), new_min)

        # Then we create another boolean vector which will have a True value if the elevation is less or equals the new max
        # and will be false the other way
        max_Tx = np.less_equal(-np.unique(mog.data.Tx_z),new_max)
        max_Rx = np.less_equal(-np.unique(np.sort(mog.data.Rx_z)), new_max + 0.0000000001) #À voir avec bernard


        # Finally, we add these two boolean vectors as integer type. The subsequent vector will have values of 1 and 2,
        # but only the 2s are of interest because they mean that the value is true, either in the min vector than the
        # max vector.we than substract 1 to this vector and transform it to a boolean type to have the right points
        # plotted in the pruneFig
        mog.in_Tx_vect = ( min_Tx.astype(int) + max_Tx.astype(int) - 1).astype(bool)
        mog.in_Rx_vect = ( min_Rx.astype(int) + max_Rx.astype(int) - 1).astype(bool)

        # We then append a False boolean vector to fit the lenght of ntrace
        mog.in_Tx_vect = np.append(mog.in_Tx_vect, np.ones(mog.data.ntrace - len(min_Tx), dtype=bool))
        mog.in_Rx_vect = np.append(mog.in_Rx_vect, np.ones(mog.data.ntrace - len(min_Rx), dtype=bool))

        #-These steps are for the skipping of Txs and Rxs---------------------------------------------------------------

        # We first get the unique version of Rx_z and Tx_z
        unique_Rx_z = np.unique(mog.data.Rx_z)
        unique_Tx_z = np.unique(mog.data.Tx_z)

        # And then we apply the skip_len with proper matrix indexing
        unique_Rx_z = unique_Rx_z[::skip_len_Rx + 1]
        unique_Tx_z = unique_Tx_z[::skip_len_Tx + 1]
        # Why the +1 ? its because skipping 0 would bring out an error. The initial skipping value is 1, which skips no values

        # We then look for the indexes of the skipped values
        for i in range(len(np.unique(mog.data.Rx_z))):
            if np.unique(mog.data.Rx_z)[i] not in unique_Rx_z:
                inRx.append(i)
        # And the we assing and False to the skipped points, so the plotting can be successful
        for value in inRx:
            mog.in_Rx_vect[value] = False

        # here its the same thig but for the Txs
        for i in range(len(np.unique(mog.data.Tx_z))):
            if np.unique(mog.data.Tx_z)[i] not in unique_Tx_z:
                inTx.append(i)
        for value in inTx:
            mog.in_Tx_vect[value] = False

        # For the angular restrictions, we first calculate the X-Y distance between the Tx's and Rx's
        dr = np.sqrt((mog.data.Tx_x - mog.data.Rx_x)**2 + (mog.data.Tx_y - mog.data.Rx_y)**2)

        # Then we call the arctan2 function from numpy which gives us the angle for every couple Tx-Rx
        theta = np.arctan2(mog.data.Tx_z-mog.data.Rx_z, dr) * 180 / np.pi

        # After finding all the angles of the Tx-Rx set, we do the same thing we did for the elevation
        min_theta = np.greater_equal(theta, ang_min)
        max_theta = np.less_equal(theta, ang_max)

        intheta = (min_theta.astype(int) + max_theta.astype(int) - 1).astype(bool)

        # We then look for the indexes of the angle values which don't fit in the restrictions
        false_theta = np.where(intheta==False)

        # Then we associate a false value to these indexes in the in_Rx_vect so the plot will contain only the Rx points
        # which fit the constraints values of the min_ang and max_ang edits
        for false_index in false_theta[0]:
            mog.in_Rx_vect[false_index] = False

        if use_snr:
            SNR = self.compute_SNR()

        mog.in_vect = (mog.in_Rx_vect.astype(int) + mog.in_Tx_vect.astype(int) - 1).astype(bool)

        # And then. when all of the steps have been done, we update the prune info subwidget and plot the graphic
        self.update_prune_info()
        self.pruneFig.plot_prune(mog, round_factor)
        # Why wouldn't we apply the modification of the round factor in the update prune method?
        # well it's because the update prune method modifies the boolean vector in_Tx_vect and in_Rx_vect
        # and the applicatiomn of a round facotr modifies the data itself so we had to put it in the plotting


    def update_prune_edits_info(self):
        ind = self.MOG_list.selectedIndexes()
        for i in ind:
            mog = self.MOGs[i.row()]
            self.min_ang_edit.setText(str(mog.pruneParams.thetaMin))
            self.max_ang_edit.setText(str(mog.pruneParams.thetaMax))

            if min(mog.data.Tx_z) < min(mog.data.Rx_z):
                self.min_elev_edit.setText(str(-mog.data.Tx_z[-1]))
                self.max_elev_edit.setText(str(mog.data.Tx_z[0]))

            elif min(mog.data.Rx_z) < min(mog.data.Tx_z):
                self.min_elev_edit.setText(str(-max(mog.data.Rx_z)))
                self.max_elev_edit.setText(str(-min(mog.data.Rx_z)))

    def update_prune_info(self):
        ind = self.MOG_list.selectedIndexes()
        mog = self.MOGs[ind[0].row()]
        selected_angle = float(self.max_ang_edit.text()) - float(self.min_ang_edit.text())
        removed_Tx = mog.data.ntrace - sum(mog.in_Tx_vect)
        removed_Rx = mog.data.ntrace - sum(mog.in_Rx_vect)
        removed_Tx_and_Rx = (removed_Tx + removed_Rx)/mog.data.ntrace * 100
        tot_traces = mog.data.ntrace
        selec_traces = sum(mog.in_vect)
        kept_traces = (selec_traces/tot_traces)*100

        self.value_Tx_info_label.setText(str(len(np.unique(mog.data.Tx_z))))
        self.value_Rx_info_label.setText(str(len(np.unique(mog.data.Rx_z))))
        self.value_Tx_Rx_removed_label.setText(str(np.round(removed_Tx_and_Rx)))
        self.value_ray_angle_removed_label.setText(str(np.round(((180-selected_angle)/180)*100)))
        self.value_traces_kept_label.setText(str(round(kept_traces, 2)))

    def start_merge(self):
        self.mergemog = MergeMog(self)
        self.mergemog.ref_combo.clear()

        if len(self.MOG_list) == 0:
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No MOG in Database",buttons= QtGui.QMessageBox.Ok )
            return
        if len(self.MOG_list) == 1:
            dialog = QtGui.QMessageBox.information(self, 'Warning', "Only 1 MOG in Database",buttons= QtGui.QMessageBox.Ok)
            return

        for mog in self.MOGs:
            self.mergemog.ref_combo.addItem(str(mog.name))

        self.mergemog.getcompat()

    def start_delta_t(self):
        self.deltat = DeltaTMOG(self)
        for mog in self.MOGs:
            self.deltat.min_combo.addItem(str(mog.name))
        self.deltat.getcompat()

    def initUI(self):

        char1 = lookup("GREEK SMALL LETTER TAU")
        char2 = lookup("GREEK CAPITAL LETTER DELTA")

        # -------- Creation of the manager for the Ray Coverage figure -------#
        self.zopraysFig = ZOPRaysFig()
        self.zopraysmanager = QtGui.QWidget()
        self.zopraystool = NavigationToolbar2QT(self.zopraysFig, self)
        zopraysmanagergrid = QtGui.QGridLayout()
        zopraysmanagergrid.addWidget(self.zopraystool, 0, 0)
        zopraysmanagergrid.addWidget(self.zopraysFig, 1, 0)
        self.zopraysmanager.setLayout(zopraysmanagergrid)

        #-------- Creation of the manager for the Ray Coverage figure -------#
        self.raycoverageFig = RayCoverageFig()
        self.raymanager = QtGui.QWidget()
        self.raytool = NavigationToolbar2QT(self.raycoverageFig, self)
        raymanagergrid = QtGui.QGridLayout()
        raymanagergrid.addWidget(self.raytool, 0, 0)
        raymanagergrid.addWidget(self.raycoverageFig, 1, 0)
        self.raymanager.setLayout(raymanagergrid)

        #-------- Creation of the manager for the Stats Amp figure -------#
        self.statsampFig = StatsAmpFig()
        self.statsampmanager = QtGui.QWidget()
        self.statsamptool = NavigationToolbar2QT(self.statsampFig, self)
        statsampmanagergrid = QtGui.QGridLayout()
        statsampmanagergrid.addWidget(self.statsamptool, 0, 0)
        statsampmanagergrid.addWidget(self.statsampFig, 1, 0)
        self.statsampmanager.setLayout(statsampmanagergrid)

        #------- Creation of the manager for the Stats tt figure -------#
        self.statsttFig = StatsttFig()
        self.statsttmanager = QtGui.QWidget()
        self.statstttool = NavigationToolbar2QT(self.statsttFig, self)
        statsttmanagergrid = QtGui.QGridLayout()
        statsttmanagergrid.addWidget(self.statstttool, 0, 0)
        statsttmanagergrid.addWidget(self.statsttFig, 1, 0)
        self.statsttmanager.setLayout(statsttmanagergrid)

        #------- Widgets in Prune -------#
        #--- Labels ---#
        skip_Tx_label = MyQLabel('Number of stations to Skip - Tx', ha='center')
        skip_Rx_label = MyQLabel('Number of stations to Skip - Rx', ha='center')
        round_fac_label = MyQLabel('Rouding Factor', ha='center')
        min_ang_label = MyQLabel('Minimum Ray Angle', ha='center')
        max_ang_label = MyQLabel('Maximum Ray Angle', ha='center')
        min_elev_label = MyQLabel('Minimum Elevation', ha='center')
        max_elev_label = MyQLabel('Maximum Elevation', ha='center')

        #- Labels in Info -#
        Tx_info_label = MyQLabel('Tx', ha='left')
        Rx_info_label = MyQLabel('Rx', ha='left')
        Tx_Rx_removed_label = MyQLabel('% removed - Tx & Rx', ha='left')
        sm_ratio_removed_label = MyQLabel('% removed - S/M ratio', ha='left')
        ray_angle_removed_label = MyQLabel('% removed - Ray angle', ha='left')
        traces_kept_label = MyQLabel('% of traces kept', ha='left')

        self.value_Tx_info_label = MyQLabel('0', ha='right')
        self.value_Rx_info_label = MyQLabel('0', ha='right')
        self.value_Tx_Rx_removed_label = MyQLabel('0', ha='right')
        self.value_sm_ratio_removed_label = MyQLabel('0', ha='right')
        self.value_ray_angle_removed_label = MyQLabel('0', ha='right')
        self.value_traces_kept_label = MyQLabel('100', ha='right')

        #--- Edits ---#
        self.skip_Tx_edit = QtGui.QLineEdit('0')
        self.skip_Rx_edit = QtGui.QLineEdit('0')
        self.round_fac_edit = QtGui.QLineEdit('0')
        self.min_ang_edit = QtGui.QLineEdit()
        self.max_ang_edit = QtGui.QLineEdit()
        self.min_elev_edit = QtGui.QLineEdit()
        self.max_elev_edit = QtGui.QLineEdit()
        self.tresh_edit = QtGui.QLineEdit('0')

        #- Edits Actions -#
        self.skip_Tx_edit.editingFinished.connect(self.update_prune)
        self.skip_Rx_edit.editingFinished.connect(self.update_prune)
        self.min_ang_edit.editingFinished.connect(self.update_prune)
        self.max_ang_edit.editingFinished.connect(self.update_prune)
        self.min_elev_edit.editingFinished.connect(self.update_prune)
        self.max_elev_edit.editingFinished.connect(self.update_prune)
        self.round_fac_edit.editingFinished.connect(self.update_prune)


        #- Edits Disposition -#
        self.skip_Tx_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.skip_Rx_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.round_fac_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.min_ang_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.max_ang_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.min_elev_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.max_elev_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.tresh_edit.setAlignment(QtCore.Qt.AlignHCenter)

        #--- CheckBox ---#
        self.tresh_check = QtGui.QCheckBox('Treshold - SNR')

        #- CheckBox Action -#
        self.tresh_check.stateChanged.connect(self.update_prune)

        #--- Button ---#
        btn_done = QtGui.QPushButton('Done')

        #--- Info Frame ---#
        info_frame = QtGui.QFrame()
        info_frame_grid =QtGui.QGridLayout()
        info_frame_grid.addWidget(self.value_Tx_info_label, 1, 0)
        info_frame_grid.addWidget(Tx_info_label, 1, 1)
        info_frame_grid.addWidget(self.value_Rx_info_label, 2, 0)
        info_frame_grid.addWidget(Rx_info_label, 2, 1)
        info_frame_grid.addWidget(self.value_Tx_Rx_removed_label, 3, 0)
        info_frame_grid.addWidget(Tx_Rx_removed_label, 3, 1)
        info_frame_grid.addWidget(self.value_sm_ratio_removed_label, 4, 0)
        info_frame_grid.addWidget(sm_ratio_removed_label, 4, 1)
        info_frame_grid.addWidget(self.value_ray_angle_removed_label, 5, 0)
        info_frame_grid.addWidget(ray_angle_removed_label, 5, 1)
        info_frame_grid.addWidget(self.value_traces_kept_label, 6, 0)
        info_frame_grid.addWidget(traces_kept_label, 6, 1)
        info_frame_grid.setAlignment(QtCore.Qt.AlignCenter)
        info_frame.setLayout(info_frame_grid)
        info_frame.setStyleSheet('background: white')

        #--- Info GroupBox ---#
        info_group = QtGui.QGroupBox('Informations')
        info_grid = QtGui.QGridLayout()
        info_grid.addWidget(info_frame, 0, 0)
        info_group.setLayout(info_grid)

        #--- Prune SubWidget ---#
        Sub_prune_widget = QtGui.QWidget()
        Sub_prune_grid = QtGui.QGridLayout()
        Sub_prune_grid.addWidget(skip_Tx_label, 0, 0)
        Sub_prune_grid.addWidget(self.skip_Tx_edit, 1, 0)
        Sub_prune_grid.addWidget(skip_Rx_label, 2, 0)
        Sub_prune_grid.addWidget(self.skip_Rx_edit, 3, 0)
        Sub_prune_grid.addWidget(round_fac_label, 4, 0)
        Sub_prune_grid.addWidget(self.round_fac_edit, 5, 0)
        Sub_prune_grid.addWidget(self.tresh_check, 6, 0)
        Sub_prune_grid.addWidget(self.tresh_edit, 7, 0)
        Sub_prune_grid.addWidget(min_ang_label, 8, 0)
        Sub_prune_grid.addWidget(self.min_ang_edit, 9, 0)
        Sub_prune_grid.addWidget(max_ang_label, 10, 0)
        Sub_prune_grid.addWidget(self.max_ang_edit, 11, 0)
        Sub_prune_grid.addWidget(min_elev_label, 12, 0)
        Sub_prune_grid.addWidget(self.min_elev_edit, 13, 0)
        Sub_prune_grid.addWidget(max_elev_label, 14, 0)
        Sub_prune_grid.addWidget(self.max_elev_edit, 15, 0)
        Sub_prune_grid.addWidget(info_group, 16, 0)
        Sub_prune_grid.addWidget(btn_done, 17, 0)
        Sub_prune_widget.setLayout(Sub_prune_grid)

        #-------- Creation of the manager for Prune Figure --------#
        self.pruneFig = PruneFig()
        self.prunetool = NavigationToolbar2QT(self.pruneFig, self)
        self.prunemanager = QtGui.QWidget()
        prunemanagergrid = QtGui.QGridLayout()
        prunemanagergrid.addWidget(self.prunetool, 0, 0, 1, 3)
        prunemanagergrid.addWidget(self.pruneFig, 1, 0, 2, 2)
        prunemanagergrid.addWidget(Sub_prune_widget, 1, 2)
        prunemanagergrid.setColumnStretch(0, 100)
        prunemanagergrid.setRowStretch(0, 100)
        self.prunemanager.setLayout(prunemanagergrid)


        #-------- Widgets in ZOP -------#
        #--- Labels ---#
        tmin_label = MyQLabel('t min', ha= 'right')
        tmax_label = MyQLabel('t max', ha= 'right')
        zmin_label = MyQLabel('z min', ha= 'right')
        zmax_label = MyQLabel('z max', ha= 'right')
        tol_label = MyQLabel('Vertical Tx-Rx Offset Tolerance')

        #--- Edits ---#
        self.tmin_edit = QtGui.QLineEdit()
        self.tmax_edit = QtGui.QLineEdit()
        self.zmin_edit = QtGui.QLineEdit()
        self.zmax_edit = QtGui.QLineEdit()
        self.tol_edit = QtGui.QLineEdit()
        self.color_scale_edit = QtGui.QLineEdit()

        #--- Edits Disposition ---#
        self.tmin_edit.setFixedWidth(80)
        self.tmax_edit.setFixedWidth(80)
        self.zmin_edit.setFixedWidth(80)
        self.zmax_edit.setFixedWidth(80)
        self.tol_edit.setFixedWidth(100)
        self.color_scale_edit.setFixedWidth(80)



        #--- Combobox ---#
        self.color_scale_combo = QtGui.QComboBox()

        #- Combobox items -#
        self.color_scale_combo.addItem('Low')
        self.color_scale_combo.addItem('Medium')
        self.color_scale_combo.addItem('High')

        #--- Checkboxes ---#
        self.veloc_check = QtGui.QCheckBox('Show Apparent Velocity')
        self.const_check = QtGui.QCheckBox("Show BH's Velocity Constaints")
        self.amp_check = QtGui.QCheckBox('Show Amplitude Data')
        self.geo_check = QtGui.QCheckBox('Corr. Geometrical Spreading')


        #--- Buttons ---#
        btn_show = QtGui.QPushButton('Show Rays')
        btn_print = QtGui.QPushButton('Print')

        #--- Buttons' Actions ---#
        btn_show.clicked.connect(self.plot_zop_rays)
        #------- SubWidgets in ZOP -------#
        #--- Time and Elevation SubWidget ---#
        Sub_t_and_z_widget = QtGui.QWidget()
        Sub_t_and_z_grid = QtGui.QGridLayout()
        Sub_t_and_z_grid.addWidget(tmin_label, 0, 0)
        Sub_t_and_z_grid.addWidget(tmax_label, 1, 0)
        Sub_t_and_z_grid.addWidget(zmin_label, 2, 0)
        Sub_t_and_z_grid.addWidget(zmax_label, 3, 0)
        Sub_t_and_z_grid.addWidget(self.tmin_edit, 0, 1)
        Sub_t_and_z_grid.addWidget(self.tmax_edit, 1, 1)
        Sub_t_and_z_grid.addWidget(self.zmin_edit, 2, 1)
        Sub_t_and_z_grid.addWidget(self.zmax_edit, 3, 1)
        Sub_t_and_z_widget.setLayout(Sub_t_and_z_grid)

        #--- tolerance SubWidget ---#
        Sub_tol_widget = QtGui.QWidget()
        Sub_tol_grid = QtGui.QGridLayout()
        Sub_tol_grid.addWidget(tol_label, 0, 0)
        Sub_tol_grid.addWidget(self.tol_edit, 1, 0)
        Sub_tol_grid.setAlignment(QtCore.Qt.AlignCenter)
        Sub_tol_widget.setLayout(Sub_tol_grid)
        #------- Groupboxes in ZOP -------#

        #--- Color Scale GroupBox ---#
        color_group = QtGui.QGroupBox('Color Scale')
        color_grid = QtGui.QGridLayout()
        color_grid.addWidget(self.color_scale_edit, 0, 0)
        color_grid.addWidget(self.color_scale_combo, 1, 0)
        color_grid.setAlignment(QtCore.Qt.AlignCenter)
        color_group.setLayout(color_grid)

        #--- Control GroupBox ---#
        control_group = QtGui.QGroupBox('Control')
        control_grid = QtGui.QGridLayout()
        control_grid.addWidget(Sub_t_and_z_widget, 0, 0)
        control_grid.addWidget(Sub_tol_widget, 1, 0)
        control_grid.addWidget(color_group, 2, 0)
        control_grid.addWidget(self.veloc_check, 3, 0)
        control_grid.addWidget(self.const_check, 4, 0)
        control_grid.addWidget(self.amp_check, 5, 0)
        control_grid.addWidget(self.geo_check, 6, 0)
        control_grid.addWidget(btn_show, 7, 0)
        control_grid.addWidget(btn_print, 8, 0)
        control_group.setLayout(control_grid)


        #------- Creation of the manager for the ZOP figure -------#
        self.zopFig = ZOPFig()
        self.zopmanager = QtGui.QWidget()
        zopmanagergrid = QtGui.QGridLayout()
        zopmanagergrid.addWidget(self.zopFig, 0, 0, 2, 5)
        zopmanagergrid.addWidget(control_group, 0, 5)
        zopmanagergrid.setColumnStretch(1, 100)
        zopmanagergrid.setRowStretch(1, 100)
        self.zopmanager.setLayout(zopmanagergrid)

        #- Checkboxes Actions -#
        self.amp_check.stateChanged.connect(self.zopFig.show_amplitude_data)

        #------- Creation of the Manager for the raw Data figure -------#
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
        f_min_label = MyQLabel(('F Min'), ha='right')
        f_maxi_label = MyQLabel(('F Max'), ha='right')
        self.search_info_label = MyQLabel((''), ha= 'center')
        self.info_label = MyQLabel((''), ha= 'center')

        #- Edits -#
        self.f_max_edit = QtGui.QLineEdit('400')
        self.f_min_edit = QtGui.QLineEdit('0')
        self.f_maxi_edit = QtGui.QLineEdit('400')
        self.search_elev_edit = QtGui.QLineEdit()

        #- Edits Disposition -#
        self.f_max_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.f_min_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.f_maxi_edit.setAlignment(QtCore.Qt.AlignHCenter)
        #- Edits Actions -#
        self.f_max_edit.editingFinished.connect(self.plot_spectra)

        #- Edits disposition -#
        self.search_elev_edit.editingFinished.connect(self.search_Tx_elev)
        self.search_elev_edit.setFixedWidth(100)

        #- Comboboxes -#
        self.search_combo = QtGui.QComboBox()
        self.psd_combo = QtGui.QComboBox()
        self.snr_combo = QtGui.QComboBox()

        #- Combobox Items -#
        self.search_combo.addItem('Search with Elevation')
        self.search_combo.addItem('Search with Number')

        method_list = ['Standard Fourier', 'Welch', 'Burg - Order 2', 'Burg - Order 3', 'Burg - Order 4']
        self.psd_combo.addItems(method_list)

        scale_list = ['Linear', 'Logarithmic']
        self.snr_combo.addItems(scale_list)

        #- ComboBoxes Actions -#
        self.snr_combo.currentIndexChanged.connect(self.plot_spectra)
        self.psd_combo.currentIndexChanged.connect(self.plot_spectra)

        #- List Widget -#
        self.Tx_num_list = QtGui.QListWidget()
        self.Tx_num_list.itemSelectionChanged.connect(self.update_spectra_Tx_elev_value_label)
        self.Tx_num_list.clicked.connect(self.plot_spectra)
        self.Tx_num_list.setFixedWidth(200)

        #- Checkboxes -#
        self.filter_check = QtGui.QCheckBox('Apply Low Pass Filter')
        self.compute_check = QtGui.QCheckBox('Compute and Show')

        #- CheckBoxes Actions -#
        self.filter_check.stateChanged.connect(self.plot_spectra)

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

        #- Fmin and Fmax SubWidget -#
        sub_freq_widget = QtGui.QWidget()
        sub_freq_grid = QtGui.QGridLayout()
        sub_freq_grid.addWidget(f_min_label, 0, 0)
        sub_freq_grid.addWidget(self.f_min_edit, 0, 1)
        sub_freq_grid.addWidget(f_maxi_label, 1, 0)
        sub_freq_grid.addWidget(self.f_maxi_edit, 1, 1)
        sub_freq_widget.setLayout(sub_freq_grid)

        #- Dominant frequency Groupbox -#
        dominant_frequency_GroupBox =  QtGui.QGroupBox("Dominant Frequency")
        dominant_frequency_Grid     = QtGui.QGridLayout()
        dominant_frequency_Grid.addWidget(sub_freq_widget, 0, 0)
        dominant_frequency_Grid.addWidget(self.compute_check, 1, 0)
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
        btn_delta_t_mog             = QtGui.QPushButton(" Create {}t MOG".format(char2))


        #--- List ---#
        self.MOG_list = QtGui.QListWidget()
        #--- List Actions ---#
        self.MOG_list.itemSelectionChanged.connect(self.update_edits)

        #--- ComboBoxes ---#
        self.Type_combo = QtGui.QComboBox()
        self.Tx_combo = QtGui.QComboBox()
        self.Rx_combo = QtGui.QComboBox()

        #- ComboBoxes Dispostion -#
        self.Type_combo.addItem(" Crosshole ")
        self.Type_combo.addItem(" VSP/VRP ")

        #- ComboBoxes Actions -#
        self.Tx_combo.activated.connect(self.updateCoords)
        self.Rx_combo.activated.connect(self.updateCoords)

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

        #- Edits Disposition -#
        self.Date_edit.setReadOnly(True)

        #--- Buttons actions ---#
        btn_Add_MOG.clicked.connect(self.add_MOG)
        btn_Rename.clicked.connect(self.rename)
        btn_Remove_MOG.clicked.connect(self.del_MOG)
        btn_Raw_Data.clicked.connect(self.plot_rawdata)
        btn_Spectra.clicked.connect(self.plot_spectra)
        btn_Air_Shot_Before.clicked.connect(self.airBefore)
        btn_Air_Shot_After.clicked.connect(self.airAfter)
        btn_Merge.clicked.connect(self.start_merge)
        btn_Trace_ZOP.clicked.connect(self.plot_zop)
        btn_Stats_tt.clicked.connect(self.plot_statstt)
        btn_Stats_Ampl.clicked.connect(self.plot_statsamp)
        btn_Ray_Coverage.clicked.connect(self.plot_ray_coverage)
        btn_Export_tt.clicked.connect(self.export_tt)
        btn_export_tau.clicked.connect(self.export_tau)
        btn_Prune.clicked.connect(self.plot_prune)
        btn_delta_t_mog.clicked.connect(self.start_delta_t)


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
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Date_label,7, 0)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Nominal_Frequency_edit,0, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Rx_Offset_edit,1, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Tx_Offset_edit,2, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Correction_Factor_edit,3, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Multiplication_Factor_edit,4, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Date_edit, 7, 1, 1, 2)
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
        sub_right_buttons_Grid.addWidget(btn_delta_t_mog, 5, 2)
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


#-----------------------------------------------------------------------------------------------------------------------
#
#                       MyQLabel Class for easy Label Alignment
#
#-----------------------------------------------------------------------------------------------------------------------
class  MyQLabel(QtGui.QLabel):
    def __init__(self, label, ha='left',  parent= None):
        super(MyQLabel, self).__init__(label,parent)
        if ha == 'center':
            self.setAlignment(QtCore.Qt.AlignCenter)
        elif ha == 'right':
            self.setAlignment(QtCore.Qt.AlignRight)
        else:
            self.setAlignment(QtCore.Qt.AlignLeft)


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Raw Data Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
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


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Spectra Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class SpectraFig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(facecolor= 'white')
        super(SpectraFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax1 = self.figure.add_axes([0.08, 0.06, 0.3, 0.9])
        self.ax2 = self.figure.add_axes([0.42, 0.06, 0.3, 0.9])
        self.ax3 = self.figure.add_axes([0.78, 0.06, 0.2, 0.9])
        self.ax1.yaxis.set_ticks_position('left')
        self.ax1.set_axisbelow(True)

    def plot_spectra(self, mog, n, Fmax, filter_state, scale, method):

        self.ax1.cla()
        self.ax2.cla()
        self.ax3.cla()

        Tx= np.unique(mog.data.Tx_z)

        ind = Tx[n] == mog.data.Tx_z

        fac_f = 1
        fac_t = 1
        if 'ns' in mog.data.tunits:
            fac_f = 10**6
            fac_t = 10**-9
        elif 'ms' in mog.data.tunits:
            fac_f = 10**3
            fac_t = 10**-3

        f0 = mog.data.rnomfreq * fac_f

        dt = mog.data.timec * mog.fac_dt
        dt = dt * fac_t
        Fs = 1/dt

        # Getting the maximum amplitude value for each column
        A = np.amax(mog.data.rdata, axis= 0)

        # Making a matrix which has the same size as rdata but filled with the maximum amplitude of each column
        Amax= np.tile(A, (550,1))

        # Dividing the original rdata by A max in order to have a normalised amplitude matrix
        normalised_rdata = mog.data.rdata/Amax

        traces = normalised_rdata[:, ind]

        if filter_state:
            halfFs = Fs / 2
            wp = 1.4 * f0 / halfFs
            ws = 1.6 * f0 / halfFs
            rp = 3
            rs = 40

            nc, wn = spy.signal.cheb1ord(wp, ws, rp, rs)

            b, a = spy.signal.cheby1(nc, 0.5, wn)
            for nt in range(np.shape(traces)[1]):
                traces[:, nt] = spy.signal.filtfilt(b, a, traces[:, nt], method='gust')

        if method == 'Welch':
            freq, tmp = spy.signal.welch(traces[:,0], Fs)
            Pxx = np.zeros((len(tmp),np.shape(traces)[1]))
            Pxx[:, 0] = tmp
            for nt in range(1,np.shape(traces)[1]):
                freq, Pxx[:, nt] = spy.signal.welch(traces[:, nt], Fs)
            self.ax2.imshow(np.log10(Pxx).T[:, :Fmax], cmap='plasma', aspect='auto',
                        interpolation='none', extent=[0, Fmax, -np.round(np.max(mog.data.Tx_z)), 0])

        if method == 'Standard Fourier':
            Pxx = np.fft.rfft(traces, axis=0)
            self.ax2.imshow(np.log10(np.abs(Pxx)).T[:, :Fmax], cmap='plasma', aspect='auto',
                        interpolation='none', extent=[0, Fmax, -np.round(np.max(mog.data.Tx_z)), 0])

        win_snr = np.round(20 / mog.data.timec)
        SNR = self.data_select(traces, f0, dt, win_snr)
        SNR = SNR[::-1]


        self.ax1.imshow(traces.T, cmap= 'plasma', aspect= 'auto', interpolation= 'none')
        #self.ax2.imshow(np.log10(np.abs(ps)).T[:, :Fmax], cmap= 'plasma', aspect= 'auto',
         #                   interpolation= 'none', extent= [0, Fmax, -np.round(np.max(mog.data.Tx_z)), 0] )


        if scale == 'Linear':
            self.ax3.plot(SNR, range(len(SNR)))


        elif scale == 'Logarithmic':
            self.ax3.plot(SNR, range(len(SNR)))
            self.ax3.set_xscale('log')


        mpl.axes.Axes.set_title(self.ax1, 'Normalized amplitude')
        mpl.axes.Axes.set_title(self.ax2, 'Log Power spectra')
        mpl.axes.Axes.set_title(self.ax3, 'Signal-to-Noise Ratio')
        mpl.axes.Axes.set_xlabel(self.ax1, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_ylabel(self.ax1, 'Rx elevation [{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_xlabel(self.ax2, 'Frequency [MHz]')
        mpl.axes.Axes.set_xlabel(self.ax3, 'SNR')

        self.draw()

    def data_select(self, data, freq, dt, L= 100, treshold= 5, medfilt_len= 10):

        shape = np.shape(data)
        N, M = shape[0], shape[1]
        std_sig = np.zeros(M).T
        ind_data_select = np.zeros(M, dtype= bool).T
        ind_max = np.zeros(M).T
        nb_p = np.round(1/(dt*freq))
        if medfilt_len>0:
            data = spy.signal.medfilt(data)

        for i in range(M):
            Amax        = np.amax(data[:, i])

            ind1        = np.argmax(data[:, i])

            ind_max[i]  = ind1

            ind         = np.arange(ind1-nb_p, ind1+2*nb_p+1)

            if ind[0] < 1:
                ind = np.arange(1, ind1+60)

            elif ind[-1] < 1:
                ind = np.arange(ind1-60, ind1)



            std_sig[i] = np.std(data[int(ind[0]):int(ind[-1]),i])


        std_noise = np.std(data[-1-L: -1, :])
        SNR = std_sig/std_noise
        ind_data_select[SNR > treshold] = True

        return SNR


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Zero Offset Profile (ZOP) Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class ZOPFig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(facecolor= 'white')
        super(ZOPFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax1 = self.figure.add_axes([0.08, 0.06, 0.4, 0.9])
        self.ax2 = self.figure.add_axes([0.6, 0.06, 0.3, 0.85])
        self.ax3 = self.ax2.twiny()

    def plot_zop(self, mog):

        mpl.axes.Axes.set_title(self.ax1, '{}'.format(mog.name))
        mpl.axes.Axes.set_xlabel(self.ax1, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_ylabel(self.ax2, ' Elevation [{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_xlabel(self.ax2, 'Amplitude')
        mpl.axes.Axes.set_xlabel(self.ax3, 'Apparent Velocity [{}/{}]'.format(mog.data.cunits, mog.data.tunits))
        self.ax2.xaxis.set_label_position('top')
        self.ax2.xaxis.set_ticks_position('top')
        self.ax3.xaxis.set_label_position('bottom')
        self.ax3.xaxis.set_ticks_position('bottom')
        self.ax3.set_visible(False)

        self.draw()
    def show_amplitude_data(self, state):
        self.ax3.set_visible(state)
        self.ax3.spines['top'].set_color('red')
        self.ax3.spines['bottom'].set_color('blue')
        self.draw()


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Zero Offset Profile (ZOP) Rays Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class ZOPRaysFig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(figsize=(6,8), facecolor='white')
        super(ZOPRaysFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_rays(self, mog, offset_tol):
        self.ax.cla()
        dz = np.abs(mog.data.Tx_z - mog.data.Rx_z)

        zop = np.less_equal(dz, offset_tol)


        false_ind = np.nonzero(zop == False)

        Tx_zs = mog.data.Tx_z
        Rx_zs = mog.data.Rx_z

        Tx_zs = np.delete(Tx_zs, false_ind[0])
        Rx_zs = np.delete(Rx_zs, false_ind[0])

        num_Tx = len(Tx_zs)
        num_Rx = len(Rx_zs)
        Tx_xs = mog.data.Tx_x[:num_Tx]
        Rx_xs = mog.data.Rx_x[:num_Rx]
        Tx_ys = mog.data.Tx_y[:num_Tx]
        Rx_ys = mog.data.Rx_y[:num_Rx]

        Tx_xs = Tx_xs[:, None]
        Tx_ys = Tx_ys[:, None]
        Tx_zs = Tx_zs[:, None]

        Rx_xs = Rx_xs[:, None]
        Rx_ys = Rx_ys[:, None]
        Rx_zs = Rx_zs[:, None]

        Tx_Rx_xs = np.concatenate((Tx_xs, Rx_xs), axis=1)
        Tx_Rx_ys = np.concatenate((Tx_ys, Rx_ys), axis=1)
        Tx_Rx_zs = np.concatenate((Tx_zs, Rx_zs), axis=1)

        Tx_Rx_xs = Tx_Rx_xs.T
        Tx_Rx_ys = Tx_Rx_ys.T
        Tx_Rx_zs = Tx_Rx_zs.T

        for i in range(num_Tx):
            self.ax.plot(xs= Tx_Rx_xs[:, i], ys= Tx_Rx_ys[:, i], zs= -1*Tx_Rx_zs[:, i], c='g')

        self.ax.plot(mog.Tx.fdata[:, 0], mog.Tx.fdata[:, 1], mog.Tx.fdata[:, 2], color='b')
        self.ax.plot(mog.Rx.fdata[:, 0], mog.Rx.fdata[:, 1], mog.Rx.fdata[:, 2], color='b')

        self.ax.text(x=mog.data.Rx_x[0], y=mog.data.Rx_y[0], z=mog.data.Rx_z[0] + 0.5, s=str(mog.Rx.name))
        self.ax.text(x=mog.data.Tx_x[0], y=mog.data.Tx_y[0], z=mog.data.Tx_z[0] + 0.5, s=str(mog.Tx.name))

        self.ax.scatter(xs=mog.data.Rx_x[0], ys=mog.data.Rx_y[0], zs=mog.data.Rx_z[0], c='black', marker='o')
        self.ax.scatter(xs=mog.data.Tx_x[0], ys=mog.data.Tx_y[0], zs=mog.data.Tx_z[0], c='black', marker='o')

        self.ax.set_xlabel('Tx-Rx X Distance [{}]'.format(mog.data.cunits))
        self.ax.set_ylabel('Tx-Rx Y Distance [{}]'.format(mog.data.cunits))
        self.ax.set_zlabel('Elevation [{}]'.format(mog.data.cunits))

        self.draw()


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Traveltime Statistics Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class StatsttFig(FigureCanvasQTAgg):
    def __init__(self, parent = None):

        fig = mpl.figure.Figure(figsize= (100, 100), facecolor='white')
        super(StatsttFig, self).__init__(fig)
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

        tt, t0 = mog.getCorrectedTravelTimes(airshots)
        et = mog.et[ind]
        tt = tt[ind]

        hyp = np.sqrt((mog.data.Tx_x[ind]-mog.data.Rx_x[ind])**2
                      + (mog.data.Tx_y[ind] + mog.data.Rx_y[ind] )**2
                      + (mog.data.Tx_z[ind] +  mog.data.Rx_z[ind] )**2)
        dz = mog.data.Rx_z[ind] - mog.data.Tx_z[ind]

        theta = 180/ np.pi * np.arcsin(dz/hyp)

        vapp = hyp/(tt-t0[ind])
        n = np.arange(len(ind))
        n = n[ind]
        ind2 = np.less(vapp, 0)
        ind2 = np.nonzero(ind2)[0]

        self.ax4.plot(hyp, tt, marker='o')
        self.ax5.plot(theta, hyp/tt, marker='o')
        self.ax2.plot(theta, vapp, marker='o')
        self.ax6.plot(t0)
        self.ax1.plot(hyp, et, marker='o')
        self.ax3.plot(theta, et, marker='o')

        vapp= hyp/tt
        self.vappFig = VAppFig()
        self.vappFig.plot_vapp(mog, vapp, ind)
        self.vappFig.show()



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


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Apparent Velocity Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class VAppFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(6, 8), facecolor='white')
        super(VAppFig, self).__init__(fig)
        self.initFig()
    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_vapp(self, mog, vapp, ind):
        Tx = np.array([mog.data.Tx_x[ind].T, mog.data.Tx_y[ind].T, mog.data.Tx_z[ind].T ])
        Rx = np.array([mog.data.Rx_x[ind].T, mog.data.Rx_y[ind].T, mog.data.Rx_z[ind].T ])

        vmin = min(vapp)
        vmax = max(vapp)
        X = np.array([[Tx],
                      [Rx]])
        x0, a = self.lsplane(X)
        el = (np.pi - a[2])*180/np.pi
        az = np.arctan(np.cos(a[1])/np.cos(a[1])) * 180/np.pi

        for n in range(len(vapp)):

            self.ax.plot([Tx[0, n], Rx[0, n]], [Tx[0, n], Rx[0, n]], [Tx[0, n], Rx[0, n]])

        self.ax.text2D(0.05, 0.95, "{} - Apparent Velocity".format(mog.name), transform=ax.transAxes)

    def lsplane(self, X):
        '''
        Least-squares plane
        :param X:
        :return:
        x0 : Centroid of the data = point on the best fit plane
        a : Direction cosines of the normal to the best fit plane
        '''

        # First we check the number of data points
        m = np.shape(X)[0]
        if m < 3:
            raise ValueError(' At least 3 data points required')

        # Calculate centroid
        x0 = np.mean(X).T

        # Form a matrix A of translated points
        A = np.array([X[:, 0] - x0[:,0], X[:, 1] - x0[:,1], X[:, 2] - x0[:,2]])

        # Calculate the Single Valued Decomposition of A
        U, S, V = np.linalg.svd(A, full_matrices= False)

        s = min(np.diag(S))
        i = np.nonzero(S == s)
        a = V[:, i]

        return x0, a


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Amplitude Statistics Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class StatsAmpFig(FigureCanvasQTAgg):
    def __init__(self, parent = None):

        fig = mpl.figure.Figure(figsize= (100, 100), facecolor='white')
        super(StatsAmpFig, self).__init__(fig)
        self.initFig()

    def initFig(self):

        # horizontal configruation
        self.ax1 = self.figure.add_axes([0.1, 0.1, 0.2, 0.25])
        self.ax2 = self.figure.add_axes([0.4, 0.1, 0.2, 0.25])
        self.ax3 = self.figure.add_axes([0.7, 0.1, 0.2, 0.25])
        self.ax4 = self.figure.add_axes([0.1, 0.55, 0.2, 0.25])
        self.ax5 = self.figure.add_axes([0.4, 0.55, 0.2, 0.25])
        self.ax6 = self.figure.add_axes([0.7, 0.55, 0.2, 0.25])

    def plot_stats(self, mog):
        self.figure.suptitle('{}'.format(mog.name), fontsize=20)
        mpl.axes.Axes.set_ylabel(self.ax4, r'$\tau_a$')
        mpl.axes.Axes.set_xlabel(self.ax4, 'Straight Ray Length[{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_title(self.ax4, 'Amplitude - Amplitude ratio')
        mpl.axes.Axes.set_ylabel(self.ax5, r'$\tau_a$')
        mpl.axes.Axes.set_xlabel(self.ax5, 'Straight Ray Length[{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_title(self.ax5, 'Amplitude - Centroid Frequency')
        mpl.axes.Axes.set_ylabel(self.ax6, r'$\tau_a$')
        mpl.axes.Axes.set_xlabel(self.ax6, 'Straight Ray Length[{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_title(self.ax6, 'Amplitude - Hybrid')
        mpl.axes.Axes.set_ylabel(self.ax1, r'$\alpha_a$')
        mpl.axes.Axes.set_xlabel(self.ax1, 'Straight Ray Length[{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_title(self.ax1, 'Amplitude - Amplitude ratio')
        mpl.axes.Axes.set_ylabel(self.ax2, r'$\alpha_a$')
        mpl.axes.Axes.set_xlabel(self.ax2, 'Angle w/r to horizontal[°]')
        mpl.axes.Axes.set_title(self.ax2, 'Amplitude - Centroid Frequency')
        mpl.axes.Axes.set_ylabel(self.ax3, r'$\alpha_a$')
        mpl.axes.Axes.set_xlabel(self.ax3, 'Angle w/r to horizontal[°]')
        mpl.axes.Axes.set_title(self.ax3, 'Amplitude - Hybrid')


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Ray Coverage Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class RayCoverageFig(FigureCanvasQTAgg):
    def __init__(self, parent= None):
        fig = mpl.figure.Figure(figsize= (6, 8), facecolor='white')
        super(RayCoverageFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection= '3d')

    def plot_ray_coverage(self, mog):
        self.ax.cla()
        ind1 = mog.tt + mog.in_vect.astype(int)
        ind1 = np.nonzero(ind1 == 0)[0]
        ind2 = np.nonzero(ind1 == 1)[0]


        Tx_xs = mog.data.Tx_x
        Rx_xs = mog.data.Rx_x

        Tx_ys = mog.data.Tx_y
        Rx_ys = mog.data.Rx_y

        Tx_zs = mog.data.Tx_z
        Rx_zs = mog.data.Rx_z

        Tx_xs = Tx_xs[:, None]
        Tx_ys = Tx_ys[:, None]
        Tx_zs = Tx_zs[:, None]

        Rx_xs = Rx_xs[:, None]
        Rx_ys = Rx_ys[:, None]
        Rx_zs = Rx_zs[:, None]

        Tx_Rx_xs = np.concatenate((Tx_xs, Rx_xs), axis=1)
        Tx_Rx_ys = np.concatenate((Tx_ys, Rx_ys), axis=1)
        Tx_Rx_zs = np.concatenate((Tx_zs, Rx_zs), axis=1)

        Tx_Rx_xs = Tx_Rx_xs.T
        Tx_Rx_ys = Tx_Rx_ys.T
        Tx_Rx_zs = Tx_Rx_zs.T
        print(ind1)
        print(Tx_Rx_xs[:, 0])
        print(Tx_Rx_ys[:, 0])
        print(Tx_Rx_zs[:, 0])
        self.ax.plot_wireframe(X= Tx_Rx_xs[:, ind1], Y= Tx_Rx_ys[:, ind1], Z= -1*Tx_Rx_zs[:, ind1], rstride=1, cstride=1, color='red')
        self.ax.plot_wireframe(X= Tx_Rx_xs[:, ind2], Y= Tx_Rx_ys[:, ind2], Z= -1*Tx_Rx_zs[:, ind2], rstride=1, cstride=1, color='red')

        percent_coverage = 100* np.round(len(ind2)/mog.data.ntrace)
        self.ax.set_title(str(percent_coverage) + ' %')

        self.ax.text2D(0.05, 0.95, "Ray Coverage", transform= self.ax.transAxes)
        self.ax.set_xlabel('Tx-Rx X Distance [{}]'.format(mog.data.cunits))
        self.ax.set_ylabel('Tx-Rx Y Distance [{}]'.format(mog.data.cunits))
        self.ax.set_zlabel('Elevation [{}]'.format(mog.data.cunits))



#-----------------------------------------------------------------------------------------------------------------------
#
#                       Prune Figure Class
#
#-----------------------------------------------------------------------------------------------------------------------
class PruneFig(FigureCanvasQTAgg):
    def __init__(self, parent= None):
        fig = mpl.figure.Figure(figsize=(6, 8), facecolor='white')
        super(PruneFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_prune(self, mog, round_factor):
        self.ax.cla()

        false_Rx_ind = np.nonzero(mog.in_Rx_vect == False)
        false_Tx_ind = np.nonzero(mog.in_Tx_vect == False)


        Tx_zs = np.unique(mog.data.Tx_z)
        Rx_zs = np.unique(mog.data.Rx_z)


        Tx_zs = np.delete(Tx_zs, false_Tx_ind[0])
        Rx_zs = np.delete(Rx_zs, false_Rx_ind[0])

        if round_factor == 0:
            pass
        else:
            Tx_zs = round_factor*np.round(Tx_zs/round_factor)
            Rx_zs = round_factor*np.round(Rx_zs/round_factor)

        num_Tx = len(Tx_zs)
        num_Rx = len(Rx_zs)
        Tx_xs = mog.data.Tx_x[:num_Tx]
        Rx_xs = mog.data.Rx_x[:num_Rx]
        Tx_ys= mog.data.Tx_y[:num_Tx]
        Rx_ys = mog.data.Rx_y[:num_Rx]


        self.ax.scatter(Tx_xs, Tx_ys, -Tx_zs, c= 'g', marker= 'o', label= 'Tx')

        self.ax.scatter(Rx_xs, Rx_ys, -Rx_zs, c='b', marker='*', label= 'Rx')

        l = self.ax.legend(ncol=1, bbox_to_anchor=(0, 1), loc='upper left',
                    borderpad=0)
        l.draw_frame(False)

        self.ax.set_xlabel('Tx-Rx X Distance [{}]'.format(mog.data.cunits))
        self.ax.set_ylabel('Tx-Rx Y Distance [{}]'.format(mog.data.cunits))
        self.ax.set_zlabel('Elevation [{}]'.format(mog.data.cunits))

        self.draw()


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Merge MOG Class
#
#-----------------------------------------------------------------------------------------------------------------------
class MergeMog(QtGui.QWidget):

    mergemoglogSignal = QtCore.pyqtSignal(str)

    def __init__(self, mog, parent=None):
        super(MergeMog, self).__init__()
        self.setWindowTitle("Merge MOGs")
        self.mog = mog
        self.initUI()

    def getcompat(self):
        self.comp_list.clear()
        n = self.ref_combo.currentIndex()
        ref_mog = self.mog.MOGs[n]
        ids = []
        nc = 0

        if n == len(self.mog.MOGs):
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No compatible MOG found",buttons= QtGui.QMessageBox.Ok)
            return

        for mog in self.mog.MOGs:
            if mog != ref_mog:
                test1 = ref_mog.Tx == mog.Tx and ref_mog.Rx == mog.Rx
                test2 = False
                test3 = False

                if len(ref_mog.av) == 0 and len(mog.av) == 0:
                    test2 = True
                elif ref_mog.av == mog.av:
                    test2 = True
                if len(ref_mog.ap) == 0 and len(mog.ap) == 0:
                    test3 = True
                elif ref_mog.ap == mog.ap:
                    test3 = True
                test4 = ref_mog.data.TxOffset == mog.data.TxOffset and ref_mog.data.RxOffset == mog.data.RxOffset
                test5 = ref_mog.type == mog.type

                if test1 and test2 and test3 and test4 and test5:
                    nc += 1
                    self.comp_list.addItem("{}".format( mog.name))
                    ids.append(mog.ID)


        if nc == 0 :
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No compatible MOG found",buttons= QtGui.QMessageBox.Ok)

        else:
            self.show()

    def doMerge(self):

        num = self.ref_combo.currentIndex()
        merge_name = self.comp_list.currentItem().text()
        if len(self.comp_list) == 0:
            self.dialog.setText("No compatible MOG found")
            self.dialog.setStandardButtons(QtGui.QMessageBox.Ok)
            self.dialog.setIcon(QtGui.QMessageBox.Warning)
        if merge_name == None:
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No MOG selected for merging",buttons= QtGui.QMessageBox.Ok)
        if not self.new_edit.text():
            dialog = QtGui.QMessageBox.information(self, 'Warning', "Please enter a name for the new MOG",buttons= QtGui.QMessageBox.Ok)


        for i in range(len(self.mog.MOGs)):
            if self.mog.MOGs[i].name == merge_name:
                merging_mog = self.mog.MOGs[i]
                merge_ind = i

        refMog = self.mog.MOGs[num]
        newMog = Mog(self.new_edit.text(), refMog.data)

        newMog.av           = np.array([refMog.av, merging_mog.av])
        newMog.ap           = np.array([refMog.ap, merging_mog.ap])
        newMog.Tx           = refMog.Tx
        newMog.Rx           = refMog.Rx
        newMog.f_et         = np.array([refMog.f_et, merging_mog.f_et])
        newMog.type         = np.array([refMog.type, merging_mog.type])
        newMog.fac_dt       = np.array([refMog.fac_dt, merging_mog.fac_dt])
        newMog.user_fac_dt  = np.array([refMog.user_fac_dt, merging_mog.user_fac_dt])
        newMog.fw           = np.array([refMog.fw, merging_mog.fw])
        newMog.tt           = np.array([refMog.tt, merging_mog.tt])
        newMog.et           = np.array([refMog.et, merging_mog.et])
        newMog.tt_done      = np.array([refMog.tt_done, merging_mog.tt_done])
        newMog.ttTx         = np.array([refMog.ttTx, merging_mog.ttTx])
        newMog.ttTx_done    = np.array([refMog.ttTx_done, merging_mog.ttTx_done])
        newMog.amp_tmin     = np.array([refMog.amp_tmin, merging_mog.amp_tmin])
        newMog.amp_tmax     = np.array([refMog.amp_tmax, merging_mog.amp_tmax])
        newMog.amp_done     = np.array([refMog.amp_done, merging_mog.amp_done])
        newMog.App          = np.array([refMog.App, merging_mog.App])
        newMog.fcentroid    = np.array([refMog.fcentroid, merging_mog.fcentroid])
        newMog.scentroid    = np.array([refMog.scentroid, merging_mog.scentroid])
        newMog.tauApp       = np.array([refMog.tauApp, merging_mog.tauApp])
        newMog.tauApp_et    = np.array([refMog.tauApp_et, merging_mog.tauApp_et])
        newMog.tauFce       = np.array([refMog.tauFce, merging_mog.tauFce])
        newMog.tauFce_et    = np.array([refMog.tauFce_et, merging_mog.tauFce_et])
        newMog.tauHyb       = np.array([refMog.tauHyb, merging_mog.tauHyb])
        newMog.tauHyb_et    = np.array([refMog.tauHyb_et, merging_mog.tauHyb_et])
        newMog.Tx_z_orig    = np.array([refMog.Tx_z_orig, merging_mog.Tx_z_orig])
        newMog.Rx_z_orig    = np.array([refMog.Rx_z_orig, merging_mog.Rx_z_orig])
        newMog.in_vect      = np.array([refMog.in_vect, merging_mog.in_vect])
        newMog.in_Tx_vect   = np.array([refMog.in_Tx_vect, merging_mog.in_Tx_vect])
        newMog.in_Rx_vect   = np.array([refMog.in_Rx_vect, merging_mog.in_Rx_vect])


        if self.erase_check.isChecked() == True :

            self.dialog.setText("following MOGs will be erased : {} {}".format(refMog.name, merging_mog.name))
            self.dialog.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            self.dialog.setIcon(QtGui.QMessageBox.Warning)
            ret = self.dialog.exec_()

            if ret == QtGui.QMessageBox.Ok:
                self.mog.MOGs.remove(refMog)
                self.mog.MOGs.remove(merging_mog)
                self.mog.MOGs.append(newMog)
                self.mog.update_List_Widget()
                self.close()


        elif self.erase_check.isChecked() == False:
            self.mog.MOGs.append(newMog)
            self.mog.update_List_Widget()
            self.close()

    def initUI(self):

        #------- Widgets -------#
        #--- Labels ---#
        ref_label = MyQLabel('Reference MOG', ha= 'center')
        comp_label = MyQLabel('Compatible MOGs', ha= 'center')
        new_label = MyQLabel('New MOG Name', ha ='center')

        #--- Edit ---#
        self.new_edit = QtGui.QLineEdit()

        #--- List ---#
        self.comp_list = QtGui.QListWidget()

        #--- ComboBox ---#
        self.ref_combo = QtGui.QComboBox()

        #--- ComboBoxes Actions ---#
        self.ref_combo.activated.connect(self.getcompat)

        #--- Checkbox ---#
        self.erase_check = QtGui.QCheckBox('Erase MOGs after merge')

        #--- Buttons ---#
        self.btn_cancel = QtGui.QPushButton('Cancel')
        self.btn_merge = QtGui.QPushButton('Merge')

        #- Buttons Actions -#
        self.btn_merge.clicked.connect(self.doMerge)
        self.btn_cancel.clicked.connect(self.close)

        #--- MessageBox ---#
        self.dialog = QtGui.QMessageBox()

        #------- Master Grid -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(ref_label, 0, 0)
        master_grid.addWidget(self.ref_combo, 1, 0)
        master_grid.addWidget(self.erase_check, 3, 0)
        master_grid.addWidget(new_label, 5, 0)
        master_grid.addWidget(self.new_edit, 6, 0)
        master_grid.addWidget(self.btn_cancel, 8, 0)
        master_grid.addWidget(comp_label, 0, 1)
        master_grid.addWidget(self.comp_list, 1, 1, 7, 1)
        master_grid.addWidget(self.btn_merge, 8, 1)

        self.setLayout(master_grid)


#-----------------------------------------------------------------------------------------------------------------------
#
#                       Delta T MOG Class
#
#-----------------------------------------------------------------------------------------------------------------------
class DeltaTMOG(QtGui.QWidget):
    def __init__(self, mog, parent=None):
        super(DeltaTMOG, self).__init__()
        char2 = lookup("GREEK CAPITAL LETTER DELTA")
        self.setWindowTitle("Create {}t MOG".format(char2))
        self.mog = mog
        self.initUI()

    def getcompat(self):
        self.sub_combo.clear()
        n = self.min_combo.currentIndex()
        ref_mog = self.mog.MOGs[n]
        ids = []
        nc = 0
        if n == len(self.mog.MOGs):
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No compatible MOG found",buttons= QtGui.QMessageBox.Ok)
            return
        for mog in self.mog.MOGs:
            if mog != ref_mog:
                test1 = ref_mog.Tx == mog.Tx and ref_mog.Rx == mog.Rx
                test2 = False
                test3 = False

                if len(ref_mog.av) == 0 and len(mog.av) == 0:
                    test2 = True
                if ref_mog.av == mog.av:
                    test2 = True
                if len(ref_mog.ap) == 0 and len(mog.ap) == 0:
                    test3 = True
                if ref_mog.ap == mog.ap:
                    test3 = True
                test4 = ref_mog.data.TxOffset == mog.data.TxOffset and ref_mog.data.RxOffset == mog.data.RxOffset
                test5 = ref_mog.type == mog.type

                if test1 and test2 and test3 and test4 and test5:
                    nc += 1
                    self.sub_combo.addItem(mog.name)
                    ids.append(mog.ID)

            else:
                pass
        if nc == 0 :
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No compatible MOG found",buttons= QtGui.QMessageBox.Ok)

        else:
            self.show()

    def done(self):
        if len(self.sub_combo) == 0:
            dialog = QtGui.QMessageBox.information(self, 'Warning', "No compatible MOG found",buttons= QtGui.QMessageBox.Ok)
        if not self.name_edit.text():
            dialog = QtGui.QMessageBox.information(self, 'Warning', "Please enter a name for new MOG",buttons= QtGui.QMessageBox.Ok)

        # Check if traveltimes were picked
        n = self.min_combo.currentIndex()
        refMog = self.mog.MOGs[n]
        ind = refMog.tt == -1
        if np.any(ind == True):
            dialog = QtGui.QMessageBox.information(self, 'Warning', "Traveltimes were not picked for {}".format(refMog.name)
                                                   ,buttons= QtGui.QMessageBox.Ok)




    def initUI(self):
        #------- Widgets -------#
        #--- Buttons ---#
        cancel_btn = QtGui.QPushButton('Cancel')
        done_btn = QtGui.QPushButton('Done')
        #--- Labels ---#
        min_label = MyQLabel('Minuend MOG', ha= 'center')
        sub_label = MyQLabel('Subtrahend MOG', ha= 'center')
        offset_label = MyQLabel('Offset Tolerance', ha= 'right')
        name_label = MyQLabel('Name of Difference MOG', ha= 'right')
        #--- Edits ---#
        self.offset_edit = QtGui.QLineEdit('0.5')
        self.name_edit = QtGui.QLineEdit()
        #--- ComboBoxes ---#
        self.min_combo = QtGui.QComboBox()
        self.sub_combo = QtGui.QComboBox()

        #--- ComboBoxes' Actions ---#
        self.min_combo.activated.connect(self.getcompat)

        #------- Master grid's disposition -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(min_label, 0, 0)
        master_grid.addWidget(sub_label, 0, 1)
        master_grid.addWidget(self.min_combo, 1, 0)
        master_grid.addWidget(self.sub_combo, 1, 1)
        master_grid.addWidget(offset_label, 2, 0)
        master_grid.addWidget(self.offset_edit, 2, 1)
        master_grid.addWidget(name_label, 3, 0)
        master_grid.addWidget(self.name_edit, 3, 1)
        master_grid.addWidget(cancel_btn, 5, 0)
        master_grid.addWidget(done_btn, 5, 1)
        self.setLayout(master_grid)





if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    MOGUI_ui = MOGUI()
    MOGUI_ui.show()

    MOGUI_ui.load_file_MOG('testData/formats/ramac/t0302.rad')

    sys.exit(app.exec_())
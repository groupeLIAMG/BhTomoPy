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
import re
import unicodedata

from PyQt5 import QtGui, QtWidgets, QtCore

import scipy as spy
from scipy import interpolate
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import axes3d
# from spectrum import arburg

from mog import MogData, Mog, AirShots
from utils import compute_SNR, data_select
from utils_ui import chooseMOG
from borehole import Borehole

from sqlalchemy.orm.attributes import flag_modified

import database
current_module = sys.modules[__name__]
database.create_data_management(current_module)


class MOGUI(QtWidgets.QWidget):  # Multi Offset Gather User Interface

    mogInfoSignal  = QtCore.pyqtSignal(int)
    ntraceSignal   = QtCore.pyqtSignal(int)
    databaseSignal = QtCore.pyqtSignal(str)
    moglogSignal   = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MOGUI, self).__init__()
        self.setWindowTitle("BhTomoPy/MOGs")
        self.initUI()
        self.data_rep = ''

    def add_MOG(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')[0]

        if filename:
            self.load_file_MOG(filename)
            self.update_edits()

    def load_file_MOG(self, filename):
        # Conditions to get the path of the file itself in order to execute it
        if ".rad" in filename.lower() or ".rd3" in filename.lower() or ".tlf" in filename.lower():
            basename = filename[:-4]

        else:
            self.moglogSignal.emit("Error: MOG file must have either *.rad, *.rd3 or *.tlf extension")
            return

        try:
            rname = basename.split('/')  # the split method gives back a list which contains all the strings that were
            rname = rname[-1]            # separated by / and the name of file (i.e. rname) is the last item of this list
            self.data_rep = basename[:-1 - len(rname)]

            mogdata = MogData(rname)
            mogdata.readRAMAC(basename)

            mog = Mog(rname, mogdata)
            database.session.add(mog)
            self.update_List_Widget()
            self.MOG_list.setCurrentRow(database.session.query(Mog).count() - 1)
            self.update_spectra_and_coverage_Tx_num_list()
            self.update_spectra_and_coverage_Tx_elev_value_label()
            self.update_edits()
            self.update_prune_edits_info()
            self.update_prune_info()
            self.moglogSignal.emit("{} Multi Offset-Gather has been loaded successfully".format(rname))
            database.modified = True

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Warning', "MOG could not be opened : '" + str(e)[:42] + "...' [mog_ui 1]",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def update_edits(self):
        """
        Updates the info either in the MOG's edits or in the info's labels
        """
        item = self.MOG_list.currentItem()
        if item is not None:
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()

            if mog is not None:
                self.Rx_Offset_edit.clear()
                self.Tx_Offset_edit.clear()
                self.Correction_Factor_edit.clear()
                self.Multiplication_Factor_edit.clear()
                self.Nominal_Frequency_edit.clear()
                self.Nominal_Frequency_edit.setText(str(mog.data.rnomfreq))
                self.Rx_Offset_edit.setText(str(mog.data.RxOffset))
                self.Tx_Offset_edit.setText(str(mog.data.TxOffset))
                self.Correction_Factor_edit.setText(str(mog.user_fac_dt))
                self.Multiplication_Factor_edit.setText(str(mog.f_et))
                self.Date_edit.setText(mog.data.date)

                if mog.av is not None and mog.ap is not None:
                    self.Air_Shot_Before_edit.setText(mog.av.name[:-4])
                    self.Air_Shot_After_edit.setText(mog.ap.name[:-4])
                else:
                    self.Air_Shot_Before_edit.setText('')
                    self.Air_Shot_After_edit.setText('')

                if mog.useAirShots:
                    self.Air_shots_checkbox.setChecked(True)

                else:
                    self.Air_shots_checkbox.setChecked(False)

                if mog.Tx is None:
                    self.Tx_combo.setCurrentIndex(-1)
                else:
                    self.Tx_combo.setCurrentIndex(self.Tx_combo.findText(mog.Tx.name))

                if mog.Rx is None:
                    self.Rx_combo.setCurrentIndex(-1)
                else:
                    self.Rx_combo.setCurrentIndex(self.Rx_combo.findText(mog.Rx.name))

        tot_traces = 0
        for mog in database.session.query(Mog).all():
            tot_traces += mog.data.ntrace
        self.ntraceSignal.emit(tot_traces)

    updateHandlerMog = False  # focus may be lost twice due to setFocus and/or the QMessageBox. 'updateHandlerMog' prevents that.

    def update_mog_info(self):

        if self.updateHandlerMog:
            return

        self.updateHandlerMog = True

        expFloat = re.compile("^-?[0-9]+([\.,][0-9]+)?$")  # float number, with or without decimals, and allowing negatives

        for item in (self.Nominal_Frequency_edit, self.Rx_Offset_edit, self.Tx_Offset_edit,
                     self.Correction_Factor_edit, self.Multiplication_Factor_edit):

            if item.text() != '' and not expFloat.match(item.text()):
                self.moglogSignal.emit("Error: Some edited information is incorrect.")
                item.setFocus()
                QtWidgets.QMessageBox.warning(self, 'Warning', "Some edited information is incorrect. Edit fields cannot contain letters or special characters.",
                                              buttons=QtWidgets.QMessageBox.Ok)
                self.updateHandlerMog = False
                return

            item.setText(item.text().replace(',', '.'))

        self.updateHandlerMog = False

        item = self.MOG_list.currentItem()
        if item is not None:
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()

            mog.data.rnomfreq = float(self.Nominal_Frequency_edit.text())
            mog.data.RxOffset = float(self.Rx_Offset_edit.text())
            mog.data.TxOffset = float(self.Tx_Offset_edit.text())
            mog.data.date     = self.Date_edit.text()
            flag_modified(mog, 'data')
            mog.user_fac_dt   = float(self.Correction_Factor_edit.text())
            mog.f_et          = float(self.Multiplication_Factor_edit.text())

    def del_MOG(self):
        item = self.MOG_list.currentItem()

        if item is not None:
            mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
            self.moglogSignal.emit("MOG {} has been deleted".format(mog_.name))
            database.delete(database, mog_)
        self.update_List_Widget()
        self.update_edits()
        database.airshots_cleanup(database)
        database.modified = True

    def rename(self):
        item = self.MOG_list.currentItem()
        if item is not None:
            new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename", 'new MOG name')
            if ok:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                self.moglogSignal.emit("MOG {} is now {}".format(mog_.name, new_name))
                mog_.name = new_name
                self.update_List_Widget()
                self.update_edits()
                database.modified = True

    def use_air(self):
        item = self.MOG_list.currentItem()

        if item is not None:
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()

            if self.Air_shots_checkbox.isChecked():
                mog.useAirShots = 1

            else:
                mog.useAirShots = 0

    def airBefore(self):

        # then we get the filename to process
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open t0 air shot before survey')[0]

        if not filename:
            return
        else:
            # We get the selected index of MOG_list to then be able to get the mog instance from MOGS
            item = self.MOG_list.currentItem()

            if item is not None:

                # then we get only the real name of the file (i.e. not the path behind it)
                basename = filename[:-4]
                rname = filename.split('/')
                rname = rname[-1]

                # then we verify if we've already applied the airshots
                airshot = database.session.query(AirShots).filter(AirShots.name == basename).first()
                if airshot is not None:
                    # then we associate the index of the air shot to the selected mog
                    database.session.query(Mog).filter(Mog.name == item.text()).av = airshot

                else:
                    # because of the fact that Airshots files are either rd3, tlf or rad, we apply the method read
                    # ramac to get the informations from these files
                    try:
                        data = MogData()
                        data.readRAMAC(basename)
                    except:
                        self.moglogSignal.emit('Error: AirShot File must have *.rad, *.tlf or *.rd3 extension')
                        return

                    # Then we ask if the airshots were done in a succession of positions or at a fixed position
                    distance, ok = QtWidgets.QInputDialog.getText(self, 'Airshots Before', 'Distance between Tx and Rx :')

                    # The getText method returns a tuple containing the entered data and a boolean factor
                    # (i.e. if the ok button is clicked, it returns True)
                    if ok:
                        if not distance:
                            self.moglogSignal.emit('Error: you must pick distances for the airshot')
                            return

                        distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance)
                        distance_list = [float(i) for i in distance_list]

                        if len(distance_list) > 1:
                            if len(distance_list) != data.ntrace:
                                self.moglogSignal.emit('Error: Number of positions inconsistent with number of traces')
                                return
                        airshot_before = AirShots(str(rname))
                        airshot_before.data = data
                        airshot_before.tt = -1 * np.ones(data.ntrace)  # tt stands for the travel time vector
                        airshot_before.et = -1 * np.ones(data.ntrace)  # to be defined
                        airshot_before.tt_done = np.zeros(data.ntrace, dtype=bool)  # the tt_done is a zeros array and whenever a ray arrives, its value will be changed to one
                        airshot_before.d_TxRx = distance_list  # Contains all the positions for which the airshots have been made
                        airshot_before.fac_dt = 1
                        airshot_before.in_vect = np.ones(data.ntrace, dtype=bool)
                        if len(distance_list) == 1:
                            airshot_before.method = 'fixed_antenna'
                        else:
                            airshot_before.method = 'walkaway'
                        self.Air_Shot_Before_edit.setText(airshot_before.name[:-4])
                        database.session.add(airshot_before)
                        database.session.query(Mog).filter(Mog.name == item.text()).first().av = airshot_before
                        database.modified = True

    def airAfter(self):
        # As you can see, the airAfter method is almost the same as airBefore (refer to airBefore for any questions)

        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open t0 air shot after survey')[0]

        if not filename:
            return
        else:
            item = self.MOG_list.currentItem()

            if item is not None:

                basename = filename[:-4]
                rname = filename.split('/')
                rname = rname[-1]

                airshot = database.session.query(AirShots).filter(AirShots.name == basename).first()
                if airshot is not None:
                    database.session.query(Mog).filter(Mog.name == item.text()).ap = airshot

                else:
                    try:
                        data = MogData()
                        data.readRAMAC(basename)
                    except:
                        self.moglogSignal.emit('Error: AirShot File must have *.rad, *.tlf or *.rd3 extension')
                        return

                    distance, ok = QtWidgets.QInputDialog.getText(self, 'Airshots After', 'Distance between Tx and Rx :')

                    if ok:
                        if not distance:
                            self.moglogSignal.emit('Error: you must pick distances for the airshot')
                            return

                        distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance)
                        distance_list = [float(i) for i in distance_list]

                        if len(distance_list) > 1:
                            if len(distance_list) != data.ntrace:
                                self.moglogSignal.emit('Error: Number of positions inconsistent with number of traces')
                                return
                        airshot_after = AirShots(str(rname))
                        airshot_after.data = data
                        airshot_after.tt = -1 * np.ones(data.ntrace)
                        airshot_after.et = -1 * np.ones(data.ntrace)
                        airshot_after.tt_done = np.zeros(data.ntrace, dtype=bool)
                        airshot_after.d_TxRx = distance_list
                        airshot_after.fac_dt = 1
                        airshot_after.in_vect = np.ones(data.ntrace, dtype=bool)
                        if len(distance_list) == 1:
                            airshot_after.method = 'fixed_antenna'
                        else:
                            airshot_after.method = 'walkaway'
                        self.Air_Shot_After_edit.setText(airshot_after.name[:-4])
                        database.session.add(airshot_after)
                        database.session.query(Mog).filter(Mog.name == item.text()).first().ap = airshot_after
                        database.modified = True

    def update_spectra_and_coverage_Tx_num_list(self):
        item = self.MOG_list.currentItem()
        self.Tx_num_list.clear()

        if item is not None:
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()
            unique_Tx_z = np.unique(mog.data.Tx_z)

            for Tx in range(len(unique_Tx_z)):
                self.Tx_num_list.addItem(str(Tx))
                self.trace_num_combo.addItem(str(Tx))

            self.Tx_num_list.setCurrentRow(0)
            self.trace_num_combo.setCurrentIndex(0)

    def update_spectra_and_coverage_Tx_elev_value_label(self):
        item = self.MOG_list.currentItem()

        if item is not None:
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()
            self.Tx_elev_value_label.clear()
            ind1 = self.Tx_num_list.selectedIndexes()
            ind2 = int(self.trace_num_edit.text())
            unique_Tx_z = np.unique(mog.data.Tx_z)[::-1]
            for i in ind1:
                self.Tx_elev_value_label.setText(str((list(unique_Tx_z))[-i.row()]))

            self.value_elev_label.setText(str((list(unique_Tx_z))[-ind2]))

    def search_Tx_elev(self):
        if self.search_combo.currentText() == 'Search with Elevation':
            try:
                item = float(self.search_elev_edit.text())
            except:
                pass
            item_ = self.MOG_list.selectedIndexes()
            mog = database.session.query(Mog).filter(Mog.name == item_.text()).first()
            for i in range(len(mog.data.Tx_z)):
                if mog.data.Tx_z[i] == item:
                    self.Tx_num_list.setCurrentRow(i + 1)
                elif item not in mog.data.Tx_z:
                    idx = np.argmin((np.abs(np.unique(mog.data.Tx_z) - item)))
                    self.Tx_num_list.setCurrentRow(idx + 1)
                    green = QtGui.QPalette()
                    green.setColor(QtGui.QPalette.Foreground, QtCore.Qt.darkCyan)
                    self.search_info_label.setText('{} is not a value in this data, {} is the closest'.format(item, np.unique(mog.data.Tx_z)[idx], decimals=1))
                    self.search_info_label.setPalette(green)
                self.update_spectra_and_coverage_Tx_elev_value_label()

        elif self.search_combo.currentText() == 'Search with Number':
            item = float(self.search_elev_edit.text())
            if item in range(len(self.Tx_num_list)):
                self.Tx_num_list.setCurrentRow(item)
            else:
                red = QtGui.QPalette()
                red.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
                self.search_info_label.setText('This data contains only {} traces, {} is out of range'.format(len(self.Tx_num_list) - 1, int(item)))
                self.search_info_label.setPalette(red)

    def update_List_Widget(self):
        self.MOG_list.clear()
        for mog in database.session.query(Mog).all():
            self.MOG_list.addItem(mog.name)
        self.mogInfoSignal.emit(len(self.MOG_list))

    def update_Tx_and_Rx_Widget(self, liste):
        self.Tx_combo.clear()
        self.Rx_combo.clear()
        for bh in liste:
            self.Tx_combo.addItem(bh.name)
            self.Rx_combo.addItem(bh.name)

    def updateCoords(self):
        item = self.MOG_list.currentItem()
        if item is not None:
            Tx_name = self.Tx_combo.currentText()
            Rx_name = self.Rx_combo.currentText()
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()

            if 'true positions' in mog.data.comment:

                Tx = np.concatenate((mog.data.Tx_x, mog.data.Tx_y, mog.data.Tx_z), axis=1)
                mog.TxCosDir = np.zeros(np.shape(Tx))

                # Equivalent of unique(Tx, 'rows') of the Matlab version
                b = np.ascontiguousarray(Tx).view(np.dtype((np.void, Tx.dtype.itemsize * Tx.shape[1])))
                tmp = np.unique(b).view(Tx.dtype).reshape(-1, Tx.shape[1])
                tmp = np.sort(tmp, axis=0)
                tmp = tmp[::-1]
                v = -np.diff(tmp, axis=0)
                d = np.sqrt(np.sum(v**2, axis=1))
                l = v / np.kron(d, np.array([1, 1, 1]))

                # TODO: finir la condition pour 'true positions'
                # for n in range(np.shape(tmp)[0]):
                #     ind = Tx[:,1] == tmp[n, 1] and Tx[:,2] == tmp[n, 2] and Tx[:,3] == tmp[n, 3]
                #     mog.TxCosDir[ind, 1] = l[n,1]
                #     mog.TxCosDir[ind, 2] = l[n,2]
                #     mog.TxCosDir[ind, 3] = l[n,3]

            # TODO: Faire une routine dans boreholeUI pour updater les Tx et Rx des MOGS s'ils sont modifiés
            Tx = database.session.query(Borehole).filter(Borehole.name == Tx_name).first()
            Rx = database.session.query(Borehole).filter(Borehole.name == Rx_name).first()
            mog.Tx = Tx
            mog.Rx = Rx
            mog.data.Tx_x = np.ones(mog.data.ntrace)
            mog.data.Tx_y = np.ones(mog.data.ntrace)
            mog.data.Rx_x = np.ones(mog.data.ntrace)
            mog.data.Rx_y = np.ones(mog.data.ntrace)

            if self.Type_combo.currentText() == 'Crosshole':
                mog.data.csurvmod = 'SURVEY MODE       = Trans. -MOG'

                # Vertical boreholes
                if Tx is not None and len(Tx.fdata[:, 0]) == 2 and len(Tx.fdata[:, 1]) == 2:
                    if abs(Tx.fdata[0, 0] - Tx.fdata[-1, 0]) < 1e-05 and abs(Tx.fdata[0, 1] - Tx.fdata[-1, 1]) < 1e-05:
                        mog.data.Tx_x = Tx.fdata[0, 0] * np.ones(mog.data.ntrace)
                        mog.data.Tx_y = Tx.fdata[0, 1] * np.ones(mog.data.ntrace)
                        mog.data.Tx_z = Tx.Z - mog.data.TxOffset - mog.Tx_z_orig
                        mog.TxCosDir = np.matlib.repmat(np.array([0, 0, 1]), mog.data.ntrace, 1)

                if Rx is not None and len(Rx.fdata[:, 0]) == 2 and len(Rx.fdata[:, 1]) == 2:
                    if abs(Rx.fdata[0, 0] - Rx.fdata[-1, 0]) < 1e-05 and abs(Rx.fdata[0, 1] - Rx.fdata[-1, 1]) < 1e-05:
                        mog.data.Rx_x = Rx.fdata[0, 0] * np.ones(mog.data.ntrace)
                        mog.data.Rx_y = Rx.fdata[0, 1] * np.ones(mog.data.ntrace)
                        mog.data.Rx_z = Rx.Z - mog.data.RxOffset - mog.Rx_z_orig
                        mog.RxCosDir = np.matlib.repmat(np.array([0, 0, 1]), mog.data.ntrace, 1)

                # TODO: Forages non verticaux

            # TODO: faire la condition pour le mode VRP
            elif self.Type_combo.currentText() == 'VSP/VRP':
                mog.data.csurvmod = 'SURVEY MODE       = Trans. -VRP'

            if Tx_name == Rx_name:
                QtWidgets.QMessageBox.information(self, 'Warning', 'Both Tx and Rx are in the same well',
                                                  buttons=QtWidgets.QMessageBox.Ok)

            if Tx is not None and Rx is not None and Tx != Rx:
                self.moglogSignal.emit("{}'s Tx and Rx are now {} and {}".format(mog.name, Tx.name, Rx.name))

            flag_modified(mog, 'data')

    def plot_rawdata(self):
        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                self.rawdataFig.plot_raw_data(mog_.data)
                self.moglogSignal.emit(" MOG {}'s Raw Data has been plotted ". format(mog_.name))
                self.rawdatamanager.showMaximized()

        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_spectra(self):
        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                n                   = self.Tx_num_list.currentIndex().row()
                mog                 = database.session.query(Mog).filter(Mog.name == item.text()).first()
                Fmax                = float(self.f_max_edit.text())
                filter_state        = self.filter_check.isChecked()
                scale               = self.snr_combo.currentText()
                estimation_method   = self.psd_combo.currentText()

                self.spectraFig.plot_spectra(mog, n, Fmax, filter_state, scale, estimation_method)
                # self.moglogSignal.emit(" MOG {}'s Spectra has been plotted ". format(mog.name))
                self.spectramanager.showMaximized()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_zop(self):
        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                self.zopFig.plot_zop()
                # mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                # self.moglogSignal.emit(" MOG {}'s Zero-Offset Profile has been plotted ".format(mog_.name))
                self.zopmanager.showMaximized()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_zop_rays(self):
        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                tol = float(self.tol_edit.text())

                self.zopraysFig.plot_rays(mog_, tol)
                self.zopraysmanager.show()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_statstt(self):
        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                done = (mog_.tt_done.astype(int) + mog_.in_vect.astype(int)) - 1

                if len(np.nonzero(done == 1)[0]) == 0:
                    QtWidgets.QMessageBox.warning(self, 'Warning', "Data not processed",
                                                  buttons=QtWidgets.QMessageBox.Ok)

                else:
                    self.statsttFig.plot_stats(mog_)
                    self.moglogSignal.emit("MOG {}'s Traveltime statistics have been plotted".format(mog_.name))
                    self.statsttmanager.showMaximized()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_statsamp(self):

        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                self.statsampFig.plot_stats(mog_)
                self.moglogSignal.emit("MOG {}'s Amplitude statistics have been plotted".format(mog_.name))
                self.statsampmanager.showMaximized()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_ray_coverage(self):

        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                coverage_ind = self.trace_num_combo.currentIndex()
                show_type = self.show_type_combo.currentText()
                entire_state = self.entire_coverage_check.isChecked()
                n = int(self.trace_num_edit.text()) - 1

                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                self.raycoverageFig.plot_ray_coverage(mog_, n, show_type, entire_state)
                # self.moglogSignal.emit("MOG {}'s Ray Coverage have been plotted".format(mog_.name))
                self.raymanager.show()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def plot_prune(self):
        if database.session.query(Mog).count() != 0:
            item = self.MOG_list.currentItem()
            if item is not None:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                if mog_.Tx != 1 and mog_.Tx != 1:
                    self.pruneFig.plot_prune(mog_, 0)
                    self.moglogSignal.emit("MOG {}'s Prune have been plotted".format(mog_.name))
                    self.prunemanager.show()
                else:
                    QtWidgets.QMessageBox.warning(self, 'Warning', "Please select Tx and Rx for MOG",
                                                  buttons=QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def next_trace(self):
        n = int(self.trace_num_edit.text())
        n += 1
        self.trace_num_edit.setText(str(n))
        self.update_spectra_and_coverage_Tx_elev_value_label()
        self.plot_ray_coverage()

    def prev_trace(self):
        n = int(self.trace_num_edit.text())
        n -= 1
        self.trace_num_edit.setText(str(n))
        self.update_spectra_and_coverage_Tx_elev_value_label()
        self.plot_ray_coverage()

    def export_tt(self):
        if database.session.query(Mog).count() != 0:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Export tt')
            self.moglogSignal.emit('Exporting Traveltime file ...')

            mog = database.session.query(Mog).filter(Mog.name == self.MOG_list.currentItem().text()).first()
            ind = np.not_equal(mog.tt, -1).astype(int) + np.equal(mog.in_vect, 1)
            ind = np.where(ind == 2)[0]
            export_file = open(filename, 'w')
            data = np.array([ind, mog.tt[ind], mog.et[ind]]).T
            np.savetxt(filename, data)
            export_file.close()

            self.moglogSignal.emit('File exported successfully ')
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def export_tau(self):
        if database.session.query(Mog).count() != 0:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Export tau')[0]
            self.moglogSignal.emit('Exporting tau file ...')
            # TODO
            self.moglogSignal.emit('File exported successfully ')
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    updateHandlerPrune = False  # focus may be lost twice due to setFocus and/or the QMessageBox. 'updateHandlerPrune' prevents that.

    def update_prune(self):
        """
        This method updates the figure containing the points of Tx and Rx
        with the information which is in the different edits of the prune widget
        """
        if self.updateHandlerPrune:
            return

        self.updateHandlerPrune = True

        expFloat = re.compile("^-?[0-9]+([\.,][0-9]+)?$")  # float number, with or without decimals, and allowing negatives
        expInt   = re.compile("^[0-9]+$")                  # positive integer

        for item in (self.min_elev_edit, self.max_elev_edit,
                     self.round_fac_edit, self.thresh_edit,
                     self.min_ang_edit, self.max_ang_edit):

            if item.text() != '' and not expFloat.match(item.text()):
                item.setFocus()
                QtWidgets.QMessageBox.warning(None, 'Warning', "Some edited information is incorrect. Edit fields cannot contain letters or special characters.",
                                              buttons=QtWidgets.QMessageBox.Ok)
                self.updateHandlerPrune = False
                return

            item.setText(item.text().replace(',', '.'))

        for item in (self.skip_Rx_edit, self.skip_Tx_edit):

            if item.text() != '' and not expInt.match(item.text()):
                item.setFocus()
                QtWidgets.QMessageBox.warning(None, 'Warning', "Some edited information is incorrect. Edit fields cannot contain letters or special characters.",
                                              buttons=QtWidgets.QMessageBox.Ok)
                self.updateHandlerPrune = False
                return

        self.updateHandlerPrune = False

        # First, we get the mog instance's informations
        item = self.MOG_list.currentItem()
        if item is not None:
            mog = database.session.query(Mog).filter(Mog.name == item.text()).first()

            # List which contain the indexes of the skipped Tx and Rx
            inRx = []
            inTx = []

            # Reinitialisation of the boolean vectors before modification
            mog.in_Rx_vect = np.ones(mog.data.ntrace, dtype=bool)
            mog.in_Tx_vect = np.ones(mog.data.ntrace, dtype=bool)

            # Information from all the edits of the prune widget
            new_min = float(self.min_elev_edit.text())
            new_max = float(self.max_elev_edit.text())
            skip_len_Rx = int(self.skip_Rx_edit.text())
            skip_len_Tx = int(self.skip_Tx_edit.text())
            round_factor = float(self.round_fac_edit.text())
            use_snr = self.thresh_check.isChecked()
            threshold_snr = float(self.thresh_edit.text())
            ang_min = float(self.min_ang_edit.text())
            ang_max = float(self.max_ang_edit.text())

            # -These steps are for the constraining of the Tx's ad Rx's elevation--------------------------------------------
            # Because the truth of multiple values array is ambiguous, we have to do these steps

            # We first create a boolean vector which will have a True value if the elevation is greater or equals the new min
            # and will be False the other way
            min_Tx = np.greater_equal(-np.unique(mog.data.Tx_z), new_min)
            min_Rx = np.greater_equal(-np.unique(np.sort(mog.data.Rx_z)), new_min)

            # Then we create another boolean vector which will have a True value if the elevation is less or equals the new max
            # and will be false otherwise
            max_Tx = np.less_equal(-np.unique(mog.data.Tx_z), new_max)
            max_Rx = np.less_equal(-np.unique(np.sort(mog.data.Rx_z)), new_max + 0.0000000001)  # TODO À voir avec bernard

            # Finally, we add these two boolean vectors as integer type. The subsequent vector will have values of 1 and 2,
            # but only the 2s are of interest because they mean that the value is true, either in the min vector than the
            # max vector.we than substract 1 to this vector and transform it to a boolean type to have the right points
            # plotted in the pruneFig
            mog.in_Tx_vect = (min_Tx.astype(int) + max_Tx.astype(int) - 1).astype(bool)
            mog.in_Rx_vect = (min_Rx.astype(int) + max_Rx.astype(int) - 1).astype(bool)

            # We then append a False boolean vector to fit the lenght of ntrace
            mog.in_Tx_vect = np.append(mog.in_Tx_vect, np.ones(mog.data.ntrace - len(min_Tx), dtype=bool))
            mog.in_Rx_vect = np.append(mog.in_Rx_vect, np.ones(mog.data.ntrace - len(min_Rx), dtype=bool))

            # -These steps are for the skipping of Txs and Rxs---------------------------------------------------------------

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
            theta = np.arctan2(mog.data.Tx_z - mog.data.Rx_z, dr) * 180 / np.pi

            # After finding all the angles of the Tx-Rx set, we do the same thing we did for the elevation
            min_theta = np.greater_equal(theta, ang_min)
            max_theta = np.less_equal(theta, ang_max)

            intheta = (min_theta.astype(int) + max_theta.astype(int) - 1).astype(bool)

            # We then look for the indexes of the angle values which don't fit in the restrictions
            false_theta = np.where(not intheta)

            # Then we associate a false value to these indexes in the in_Rx_vect so the plot will contain only the Rx points
            # which fit the constraints values of the min_ang and max_ang edits
            for false_index in false_theta[0]:
                mog.in_Rx_vect[false_index] = False

            if use_snr:
                # TODO: Faire la fonction detrend_rad
                SNR = compute_SNR(mog)

            mog.in_vect = (mog.in_Rx_vect.astype(int) + mog.in_Tx_vect.astype(int) - 1).astype(bool)

            # And then. when all of the steps have been done, we update the prune info subwidget and plot the graphic
            self.update_prune_info()
            self.pruneFig.plot_prune(mog, round_factor)
            # Why wouldn't we apply the modification of the round factor in the update prune method?
            # well it's because the update prune method modifies the boolean vector in_Tx_vect and in_Rx_vect
            # and the applicatiomn of a round facotr modifies the data itself so we had to put it in the plotting

    def update_prune_edits_info(self):
        item = self.MOG_list.currentItem()
        if item is not None:
            try:
                mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
                self.min_ang_edit.setText(str(mog_.pruneParams.thetaMin))
                self.max_ang_edit.setText(str(mog_.pruneParams.thetaMax))

                if min(mog_.data.Tx_z) < min(mog_.data.Rx_z):
                    self.min_elev_edit.setText(str(-mog_.data.Tx_z[-1]))
                    self.max_elev_edit.setText(str(mog_.data.Tx_z[0]))

                elif min(mog_.data.Rx_z) < min(mog_.data.Tx_z):
                    self.min_elev_edit.setText(str(-max(mog_.data.Rx_z)))
                    self.max_elev_edit.setText(str(-min(mog_.data.Rx_z)))
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Warning', "MOG could not be opened : '" + str(e)[:42] + "...' [mog_ui 2]",
                                              buttons=QtWidgets.QMessageBox.Ok)

    def update_prune_info(self):
        item = self.MOG_list.currentItem()

        if item is not None:
            mog_ = database.session.query(Mog).filter(Mog.name == item.text()).first()
            selected_angle = float(self.max_ang_edit.text()) - float(self.min_ang_edit.text())
            removed_Tx = mog_.data.ntrace - sum(mog_.in_Tx_vect)
            removed_Rx = mog_.data.ntrace - sum(mog_.in_Rx_vect)
            removed_Tx_and_Rx = (removed_Tx + removed_Rx) / mog_.data.ntrace * 100
            tot_traces = mog_.data.ntrace
            selec_traces = sum(mog_.in_vect)
            kept_traces = (selec_traces / tot_traces) * 100

            self.value_Tx_info_label.setText(str(len(np.unique(mog_.data.Tx_z))))
            self.value_Rx_info_label.setText(str(len(np.unique(mog_.data.Rx_z))))
            self.value_Tx_Rx_removed_label.setText(str(np.round(removed_Tx_and_Rx)))
            self.value_ray_angle_removed_label.setText(str(np.round(((180 - selected_angle) / 180) * 100)))
            self.value_traces_kept_label.setText(str(round(kept_traces, 2)))

            # TODO: updater le label qui contient la valeur du S/M ration lorsque la fonction computeSNR sera finie

    def start_merge(self):
        self.mergemog = MergeMog(self)
        self.mergemog.ref_combo.clear()

        if len(self.MOG_list) == 0:
            QtWidgets.QMessageBox.information(self, 'Warning', "No MOG in Database",
                                              buttons=QtWidgets.QMessageBox.Ok)
            return
        if len(self.MOG_list) == 1:
            QtWidgets.QMessageBox.information(self, 'Warning', "Only 1 MOG in Database",
                                              buttons=QtWidgets.QMessageBox.Ok)
            return

        for mog in database.session.query(Mog).all():
            self.mergemog.ref_combo.addItem(str(mog.name))

        self.mergemog.getcompat()

    def start_delta_t(self):
        self.deltat = DeltaTMOG(self)

        if len(self.MOG_list) == 0:
            QtWidgets.QMessageBox.information(self, 'Warning', "No MOG in Database",
                                              buttons=QtWidgets.QMessageBox.Ok)
            return

        for mog in database.session.query(Mog).all():
            self.deltat.min_combo.addItem(str(mog.name))

        self.deltat.getcompat()

    def import_mog(self):
        item = chooseMOG(current_module)
        current_module.session.close()
        current_module.engine.dispose()

        if item is not None:
            item = database.session.merge(item)
            database.session.add(item)
            self.update_List_Widget()
            self.MOG_list.setCurrentRow(database.session.query(Mog).count() - 1)
            self.update_spectra_and_coverage_Tx_num_list()
            self.update_spectra_and_coverage_Tx_elev_value_label()
            self.update_edits()
            self.update_prune_edits_info()
            self.update_prune_info()
            self.moglogSignal.emit("Mog '{}' was imported successfully".format(item.name))
            database.modified = True

    def update_color_scale(self):
        if self.color_scale_combo.currentText() == 'Low':
            self.color_scale_edit.setText('28000')
        elif self.color_scale_combo.currentText() == 'Medium':
            self.color_scale_edit.setText('7000')
        elif self.color_scale_combo.currentText() == 'High':
            self.color_scale_edit.setText('700')

    def current_mog(self):

        mog = self.MOG_list.currentItem()
        if mog:
            return database.session.query(Mog).filter(Mog.name == mog.text()).first()

    def initUI(self):

        char1 = unicodedata.lookup("GREEK SMALL LETTER TAU")
        char2 = unicodedata.lookup("GREEK CAPITAL LETTER DELTA")

        # -------- Creation of the manager for the ZOPRay figure ------- #
        self.zopraysFig = ZOPRaysFig()
        self.zopraysmanager = QtWidgets.QWidget()
        self.zopraystool = NavigationToolbar2QT(self.zopraysFig, self)
        zopraysmanagergrid = QtWidgets.QGridLayout()
        zopraysmanagergrid.addWidget(self.zopraystool, 0, 0)
        zopraysmanagergrid.addWidget(self.zopraysFig, 1, 0)
        self.zopraysmanager.setLayout(zopraysmanagergrid)

        # -------- Creation of the manager for the Stats Amp figure ------- #
        self.statsampFig = StatsAmpFig()
        self.statsampmanager = QtWidgets.QWidget()
        self.statsamptool = NavigationToolbar2QT(self.statsampFig, self)
        statsampmanagergrid = QtWidgets.QGridLayout()
        statsampmanagergrid.addWidget(self.statsamptool, 0, 0)
        statsampmanagergrid.addWidget(self.statsampFig, 1, 0)
        self.statsampmanager.setLayout(statsampmanagergrid)

        # ------- Creation of the manager for the Stats tt figure ------- #
        self.statsttFig = StatsttFig()
        self.statsttmanager = QtWidgets.QWidget()
        self.statstttool = NavigationToolbar2QT(self.statsttFig, self)
        statsttmanagergrid = QtWidgets.QGridLayout()
        statsttmanagergrid.addWidget(self.statstttool, 0, 0)
        statsttmanagergrid.addWidget(self.statsttFig, 1, 0)
        self.statsttmanager.setLayout(statsttmanagergrid)

        # ------- Widgets in Prune ------- #
        # --- Labels --- #
        skip_Tx_label   = MyQLabel('Number of stations to Skip - Tx', ha='center')
        skip_Rx_label   = MyQLabel('Number of stations to Skip - Rx', ha='center')
        round_fac_label = MyQLabel('Rounding Factor', ha='center')
        min_ang_label   = MyQLabel('Minimum Ray Angle', ha='center')
        max_ang_label   = MyQLabel('Maximum Ray Angle', ha='center')
        min_elev_label  = MyQLabel('Minimum Elevation', ha='center')
        max_elev_label  = MyQLabel('Maximum Elevation', ha='center')

        # - Labels in Info -#
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

        # --- Edits --- #
        self.skip_Tx_edit = QtWidgets.QLineEdit('0')
        self.skip_Rx_edit = QtWidgets.QLineEdit('0')
        self.round_fac_edit = QtWidgets.QLineEdit('0')
        self.min_ang_edit = QtWidgets.QLineEdit()
        self.max_ang_edit = QtWidgets.QLineEdit()
        self.min_elev_edit = QtWidgets.QLineEdit()
        self.max_elev_edit = QtWidgets.QLineEdit()
        self.thresh_edit = QtWidgets.QLineEdit('0')

        # - Edits Actions -#
        self.skip_Tx_edit.editingFinished.connect(self.update_prune)
        self.skip_Rx_edit.editingFinished.connect(self.update_prune)
        self.min_ang_edit.editingFinished.connect(self.update_prune)
        self.max_ang_edit.editingFinished.connect(self.update_prune)
        self.min_elev_edit.editingFinished.connect(self.update_prune)
        self.max_elev_edit.editingFinished.connect(self.update_prune)
        self.round_fac_edit.editingFinished.connect(self.update_prune)

        # - Edits Disposition -#
        self.skip_Tx_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.skip_Rx_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.round_fac_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.min_ang_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.max_ang_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.min_elev_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.max_elev_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.thresh_edit.setAlignment(QtCore.Qt.AlignHCenter)

        # --- CheckBox --- #
        self.thresh_check = QtWidgets.QCheckBox('Threshold - SNR')

        # - CheckBox Action -#
        self.thresh_check.stateChanged.connect(self.update_prune)

        # --- Button --- #
        btn_done = QtWidgets.QPushButton('Done')

        # --- Info Frame --- #
        info_frame = QtWidgets.QFrame()
        info_frame_grid = QtWidgets.QGridLayout()
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

        # --- Info GroupBox --- #
        info_group = QtWidgets.QGroupBox('Informations')
        info_grid = QtWidgets.QGridLayout()
        info_grid.addWidget(info_frame, 0, 0)
        info_group.setLayout(info_grid)

        # --- Prune SubWidget --- #
        Sub_prune_widget = QtWidgets.QWidget()
        Sub_prune_grid = QtWidgets.QGridLayout()
        Sub_prune_grid.addWidget(skip_Tx_label, 0, 0)
        Sub_prune_grid.addWidget(self.skip_Tx_edit, 1, 0)
        Sub_prune_grid.addWidget(skip_Rx_label, 2, 0)
        Sub_prune_grid.addWidget(self.skip_Rx_edit, 3, 0)
        Sub_prune_grid.addWidget(round_fac_label, 4, 0)
        Sub_prune_grid.addWidget(self.round_fac_edit, 5, 0)
        Sub_prune_grid.addWidget(self.thresh_check, 6, 0)
        Sub_prune_grid.addWidget(self.thresh_edit, 7, 0)
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

        # -------- Creation of the manager for Prune Figure -------- #
        self.pruneFig = PruneFig()
        self.prunetool = NavigationToolbar2QT(self.pruneFig, self)
        self.prunemanager = QtWidgets.QWidget()
        prunemanagergrid = QtWidgets.QGridLayout()
        prunemanagergrid.addWidget(self.prunetool, 0, 0, 1, 3)
        prunemanagergrid.addWidget(self.pruneFig, 1, 0, 2, 2)
        prunemanagergrid.addWidget(Sub_prune_widget, 1, 2)
#         prunemanagergrid.setColumnStretch(0, 100)
#         prunemanagergrid.setRowStretch(0, 100)
        self.prunemanager.setLayout(prunemanagergrid)

        # ------- Widgets in Raycoverage ------- #
        # --- Edit --- #
        self.trace_num_edit = QtWidgets.QLineEdit('1')

        # - Edit's Actions -#
        self.trace_num_edit.editingFinished.connect(self.plot_ray_coverage)
        self.trace_num_edit.editingFinished.connect(self.update_spectra_and_coverage_Tx_elev_value_label)

        # - Edit's Disposition -#
        self.trace_num_edit.setAlignment(QtCore.Qt.AlignHCenter)

        # --- Buttons --- #
        next_trace_btn = QtWidgets.QPushButton('Next Tx')
        prev_trace_btn = QtWidgets.QPushButton('Prev Tx')

        # - Buttons' Actions -#
        next_trace_btn.clicked.connect(self.next_trace)
        prev_trace_btn.clicked.connect(self.prev_trace)

        # --- List --- #
        self.trace_num_combo = QtWidgets.QComboBox()

        # - List Actions -#
        self.trace_num_combo.activated.connect(self.update_spectra_and_coverage_Tx_elev_value_label)
        self.trace_num_combo.activated.connect(self.plot_ray_coverage)

        # --- Labels --- #
        coverage_elev_label = MyQLabel('Tx elevation:', ha='right')
        self.value_elev_label = MyQLabel('', ha='left')
        trace_label = MyQLabel('Tx Number: ', ha='right')

        # --- CheckBox --- #
        self.entire_coverage_check = QtWidgets.QCheckBox('Show entire coverage')
        self.entire_coverage_check.stateChanged.connect(self.plot_ray_coverage)

        # --- Combobox --- #
        self.show_type_combo = QtWidgets.QComboBox()
        show_list = ['Show picked and unpicked', 'Show picked only', 'Show unpicked only']
        self.show_type_combo.addItems(show_list)
        self.show_type_combo.activated.connect(self.plot_ray_coverage)

        # --- Elevation SubWidget --- #
        sub_coverage_elev_widget = QtWidgets.QWidget()
        sub_coverage_elev_grid = QtWidgets.QGridLayout()
        sub_coverage_elev_grid.addWidget(coverage_elev_label, 0, 0)
        sub_coverage_elev_grid.addWidget(self.value_elev_label, 0, 1)
        sub_coverage_elev_widget.setLayout(sub_coverage_elev_grid)

        # --- Trace SubWidget --- #
        sub_trace_widget = QtWidgets.QWidget()
        sub_trace_grid = QtWidgets.QGridLayout()
        sub_trace_grid.addWidget(trace_label, 0, 0)
        sub_trace_grid.addWidget(self.trace_num_edit, 0, 1)
        sub_trace_grid.setContentsMargins(0, 0, 0, 0)
        sub_trace_widget.setLayout(sub_trace_grid)

        # --- Buttons SubWidget --- #
        sub_buttons_widget = QtWidgets.QWidget()
        sub_buttons_grid = QtWidgets.QGridLayout()
        sub_buttons_grid.addWidget(next_trace_btn, 0, 1)
        sub_buttons_grid.addWidget(prev_trace_btn, 0, 0)
        sub_buttons_grid.setContentsMargins(0, 0, 0, 0)
        sub_buttons_widget.setLayout(sub_buttons_grid)

        # --- Global SubWidget --- #
        # First Option
        # sub_coverage_widget = QtWidgets.QWidget()
        # sub_coverage_grid = QtWidgets.QGridLayout()
        # sub_coverage_grid.addWidget(self.trace_num_combo, 0, 0)
        # sub_coverage_grid.addWidget(sub_coverage_elev_widget, 1, 0)
        # sub_coverage_grid.addWidget(self.entire_coverage_check, 2, 0)
        # sub_coverage_grid.addWidget(self.show_type_combo, 3, 0)
        # sub_coverage_grid.setRowStretch(4, 100)
        # sub_coverage_widget.setLayout(sub_coverage_grid)

        # Second Option
        sub_coverage_widget = QtWidgets.QWidget()
        sub_coverage_grid = QtWidgets.QGridLayout()
        sub_coverage_grid.addWidget(sub_trace_widget, 0, 0)
        sub_coverage_grid.addWidget(sub_buttons_widget, 1, 0)
        sub_coverage_grid.addWidget(sub_coverage_elev_widget, 2, 0)
        sub_coverage_grid.addWidget(self.entire_coverage_check, 3, 0)
        sub_coverage_grid.addWidget(self.show_type_combo, 4, 0)
#         sub_coverage_grid.setRowStretch(5, 100)
        sub_coverage_widget.setLayout(sub_coverage_grid)

        # -------- Creation of the manager for the Ray Coverage figure ------- #
        self.raycoverageFig = RayCoverageFig()
        self.raymanager = QtWidgets.QWidget()
        self.raytool = NavigationToolbar2QT(self.raycoverageFig, self)
        raymanagergrid = QtWidgets.QGridLayout()
        raymanagergrid.addWidget(self.raytool, 0, 0, 1, 2)
        raymanagergrid.addWidget(self.raycoverageFig, 1, 0)
        raymanagergrid.addWidget(sub_coverage_widget, 1, 1)
        self.raymanager.setLayout(raymanagergrid)

        # -------- Widgets in ZOP ------- #
        # --- Labels --- #
        tmin_label = MyQLabel('t min', ha='right')
        tmax_label = MyQLabel('t max', ha='right')
        zmin_label = MyQLabel('z min', ha='right')
        zmax_label = MyQLabel('z max', ha='right')
        tol_label = MyQLabel('Vertical Tx-Rx Offset Tolerance')

        # --- Edits --- #
        self.tmin_edit = QtWidgets.QLineEdit()
        self.tmax_edit = QtWidgets.QLineEdit()
        self.zmin_edit = QtWidgets.QLineEdit()
        self.zmax_edit = QtWidgets.QLineEdit()
        self.tol_edit  = QtWidgets.QLineEdit('0.05')
        self.color_scale_edit = QtWidgets.QLineEdit('7000')

        # --- Edits Disposition --- #
        self.tmin_edit.setFixedWidth(80)
        self.tmax_edit.setFixedWidth(80)
        self.zmin_edit.setFixedWidth(80)
        self.zmax_edit.setFixedWidth(80)
        self.tol_edit.setFixedWidth(100)
        self.color_scale_edit.setFixedWidth(80)

        # - Edits Disposition -#
        self.tmin_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.tmin_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.tmax_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.zmin_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.zmax_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.tol_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.color_scale_edit.setAlignment(QtCore.Qt.AlignHCenter)

        # - Edits Actions -#
        self.tmin_edit.editingFinished.connect(self.plot_zop)
        self.tmax_edit.editingFinished.connect(self.plot_zop)
        self.zmin_edit.editingFinished.connect(self.plot_zop)
        self.zmax_edit.editingFinished.connect(self.plot_zop)
        self.tol_edit.editingFinished.connect(self.plot_zop)
        self.color_scale_edit.editingFinished.connect(self.plot_zop)

        # --- Combobox --- #
        self.color_scale_combo = QtWidgets.QComboBox()

        # - ComboBox Actions -#
        self.color_scale_combo.activated.connect(self.update_color_scale)
        self.color_scale_combo.activated.connect(self.plot_zop)

        # - Combobox items -#
        self.color_scale_combo.addItem('Low')
        self.color_scale_combo.addItem('Medium')
        self.color_scale_combo.addItem('High')

        # --- Checkboxes --- #
        self.veloc_check = QtWidgets.QCheckBox('Show Apparent Velocity')
        self.const_check = QtWidgets.QCheckBox("Show BH's Velocity Constaints")
        self.amp_check = QtWidgets.QCheckBox('Show Amplitude Data')

        # - CheckBoxes' Actions -#
        self.veloc_check.stateChanged.connect(self.plot_zop)
        self.const_check.stateChanged.connect(self.plot_zop)
        self.amp_check.stateChanged.connect(self.plot_zop)

        # --- Buttons --- #
        btn_show = QtWidgets.QPushButton('Show Rays')
        btn_print = QtWidgets.QPushButton('Print')

        # --- Buttons' Actions --- #
        btn_show.clicked.connect(self.plot_zop_rays)

        # ------- SubWidgets in ZOP ------- #
        # --- Time and Elevation SubWidget --- #
        Sub_t_and_z_widget = QtWidgets.QWidget()
        Sub_t_and_z_grid = QtWidgets.QGridLayout()
        Sub_t_and_z_grid.addWidget(tmin_label, 0, 0)
        Sub_t_and_z_grid.addWidget(tmax_label, 1, 0)
        Sub_t_and_z_grid.addWidget(zmin_label, 2, 0)
        Sub_t_and_z_grid.addWidget(zmax_label, 3, 0)
        Sub_t_and_z_grid.addWidget(self.tmin_edit, 0, 1)
        Sub_t_and_z_grid.addWidget(self.tmax_edit, 1, 1)
        Sub_t_and_z_grid.addWidget(self.zmin_edit, 2, 1)
        Sub_t_and_z_grid.addWidget(self.zmax_edit, 3, 1)
        Sub_t_and_z_widget.setLayout(Sub_t_and_z_grid)

        # --- tolerance SubWidget --- #
        Sub_tol_widget = QtWidgets.QWidget()
        Sub_tol_grid = QtWidgets.QGridLayout()
        Sub_tol_grid.addWidget(tol_label, 0, 0)
        Sub_tol_grid.addWidget(self.tol_edit, 1, 0)
        Sub_tol_grid.setAlignment(QtCore.Qt.AlignCenter)
        Sub_tol_widget.setLayout(Sub_tol_grid)

        # ------- Groupboxes in ZOP ------- #
        # --- Color Scale GroupBox --- #
        color_group = QtWidgets.QGroupBox('Color Scale')
        color_grid = QtWidgets.QGridLayout()
        color_grid.addWidget(self.color_scale_edit, 0, 0)
        color_grid.addWidget(self.color_scale_combo, 1, 0)
        color_grid.setAlignment(QtCore.Qt.AlignCenter)
        color_group.setLayout(color_grid)

        # --- Control GroupBox --- #
        control_group = QtWidgets.QGroupBox('Control')
        control_grid = QtWidgets.QGridLayout()
        control_grid.addWidget(Sub_t_and_z_widget, 0, 0)
        control_grid.addWidget(Sub_tol_widget, 1, 0)
        control_grid.addWidget(color_group, 2, 0)
        control_grid.addWidget(self.veloc_check, 3, 0)
        control_grid.addWidget(self.const_check, 4, 0)
        control_grid.addWidget(self.amp_check, 5, 0)
        control_grid.addWidget(btn_show, 6, 0)
        control_grid.addWidget(btn_print, 7, 0)
        control_group.setLayout(control_grid)

        # ------- Creation of the manager for the ZOP figure ------- #
        self.zopFig = ZOPFig(self)
        self.zopmanager = QtWidgets.QWidget()
        zopmanagergrid = QtWidgets.QGridLayout()
        zopmanagergrid.addWidget(self.zopFig, 0, 0, 2, 5)
        zopmanagergrid.addWidget(control_group, 0, 5)
#         zopmanagergrid.setColumnStretch(1, 100)
#         zopmanagergrid.setRowStretch(1, 100)
        self.zopmanager.setLayout(zopmanagergrid)

        # ------- Creation of the Manager for the raw Data figure ------- #
        self.rawdataFig = RawDataFig()
        self.rawdatatool = NavigationToolbar2QT(self.rawdataFig, self)
        self.rawdatamanager = QtWidgets.QWidget()
        rawdatamanagergrid = QtWidgets.QGridLayout()
        rawdatamanagergrid.addWidget(self.rawdatatool, 0, 0)
        rawdatamanagergrid.addWidget(self.rawdataFig, 1, 0)
        self.rawdatamanager.setLayout(rawdatamanagergrid)

        # --- Widgets in Spectra --- #
        # - Labels -#
        Tx_num_label = MyQLabel(('Tx Number'), ha='center')
        Tx_elev_label = QtWidgets.QLabel('Tx elevation: ')
        self.Tx_elev_value_label = QtWidgets.QLabel('')
        psd_label = MyQLabel(('PSD Estimation Method'), ha='center')
        f_max_label = MyQLabel(('F Max'), ha='center')
        snr_label = MyQLabel(('SNR Scale'), ha='center')
        f_min_label = MyQLabel(('F Min'), ha='right')
        f_maxi_label = MyQLabel(('F Max'), ha='right')
        self.search_info_label = MyQLabel((''), ha='center')
        self.info_label = MyQLabel((''), ha='center')

        # - Edits -#
        self.f_max_edit = QtWidgets.QLineEdit('400')
        self.f_min_edit = QtWidgets.QLineEdit('0')
        self.f_maxi_edit = QtWidgets.QLineEdit('400')
        self.search_elev_edit = QtWidgets.QLineEdit()

        # - Edits Disposition -#
        self.f_max_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.f_min_edit.setAlignment(QtCore.Qt.AlignHCenter)
        self.f_maxi_edit.setAlignment(QtCore.Qt.AlignHCenter)
        # - Edits Actions -#
        self.f_max_edit.editingFinished.connect(self.plot_spectra)

        # - Edits disposition -#
        self.search_elev_edit.editingFinished.connect(self.search_Tx_elev)
        self.search_elev_edit.setFixedWidth(100)

        # - Comboboxes -#
        self.search_combo = QtWidgets.QComboBox()
        self.psd_combo = QtWidgets.QComboBox()
        self.snr_combo = QtWidgets.QComboBox()

        # - Combobox Items -#
        self.search_combo.addItem('Search with Elevation')
        self.search_combo.addItem('Search with Number')

        method_list = ['Standard Fourier', 'Welch', 'Burg - Order 2', 'Burg - Order 3', 'Burg - Order 4']
        self.psd_combo.addItems(method_list)

        scale_list = ['Linear', 'Logarithmic']
        self.snr_combo.addItems(scale_list)

        # - ComboBoxes Actions -#
        self.snr_combo.currentIndexChanged.connect(self.plot_spectra)
        self.psd_combo.currentIndexChanged.connect(self.plot_spectra)

        # - List Widget -#
        self.Tx_num_list = QtWidgets.QListWidget()
        self.Tx_num_list.itemSelectionChanged.connect(self.update_spectra_and_coverage_Tx_elev_value_label)
        self.Tx_num_list.clicked.connect(self.plot_spectra)
        self.Tx_num_list.setFixedWidth(200)

        # - Checkboxes -#
        self.filter_check = QtWidgets.QCheckBox('Apply Low Pass Filter')
        self.compute_check = QtWidgets.QCheckBox('Compute and Show')

        # - CheckBoxes Actions -#
        self.filter_check.stateChanged.connect(self.plot_spectra)

        # - Elevation SubWidget -#
        sub_elev_widget = QtWidgets.QWidget()
        sub_elev_grid = QtWidgets.QGridLayout()
        sub_elev_grid.addWidget(Tx_elev_label, 0, 0)
        sub_elev_grid.addWidget(self.Tx_elev_value_label, 0, 1)
        sub_elev_grid.setContentsMargins(0, 0, 0, 0)
        sub_elev_widget.setLayout(sub_elev_grid)

        # - list top SubWidget -#
        sub_Tx_widget = QtWidgets.QWidget()
        sub_Tx_grid = QtWidgets.QGridLayout()
        sub_Tx_grid.addWidget(Tx_num_label, 0, 0)
        sub_Tx_grid.addWidget(self.search_combo, 0, 1)
        sub_Tx_grid.addWidget(self.search_elev_edit, 1, 1)
        sub_Tx_widget.setLayout(sub_Tx_grid)

        # - first SubWidget -#
        sub_first_widget            = QtWidgets.QWidget()
        sub_first_grid              = QtWidgets.QGridLayout()
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

        # - Fmin and Fmax SubWidget -#
        sub_freq_widget = QtWidgets.QWidget()
        sub_freq_grid = QtWidgets.QGridLayout()
        sub_freq_grid.addWidget(f_min_label, 0, 0)
        sub_freq_grid.addWidget(self.f_min_edit, 0, 1)
        sub_freq_grid.addWidget(f_maxi_label, 1, 0)
        sub_freq_grid.addWidget(self.f_maxi_edit, 1, 1)
        sub_freq_widget.setLayout(sub_freq_grid)

        # - Dominant frequency Groupbox -#
        dominant_frequency_GroupBox = QtWidgets.QGroupBox("Dominant Frequency")
        dominant_frequency_Grid     = QtWidgets.QGridLayout()
        dominant_frequency_Grid.addWidget(sub_freq_widget, 0, 0)
        dominant_frequency_Grid.addWidget(self.compute_check, 1, 0)
        dominant_frequency_GroupBox.setLayout(dominant_frequency_Grid)

        # - Total Subwidget -#
        sub_total_widget = QtWidgets.QWidget()
        sub_total_grid = QtWidgets.QGridLayout()
        sub_total_grid.addWidget(sub_first_widget, 0, 0)
        sub_total_grid.addWidget(dominant_frequency_GroupBox, 2, 0)
#         sub_total_grid.setRowStretch(1, 100)
        sub_total_widget.setLayout(sub_total_grid)

        # ------ Creation of the Manager for the Spectra figure ------- #
        self.spectraFig = SpectraFig()
        self.spectratool = NavigationToolbar2QT(self.spectraFig, self)
        self.spectramanager = QtWidgets.QWidget()
        spectramanagergrid = QtWidgets.QGridLayout()
        spectramanagergrid.addWidget(self.spectratool, 0, 0)
        spectramanagergrid.addWidget(self.info_label, 0, 2)
        spectramanagergrid.addWidget(self.search_info_label, 0, 6)
        spectramanagergrid.addWidget(self.spectraFig, 1, 0, 1, 6)
        spectramanagergrid.addWidget(sub_total_widget, 1, 6)
#         spectramanagergrid.setColumnStretch(1, 100)
        self.spectramanager.setLayout(spectramanagergrid)

        # ------- Widgets Creation ------- #
        # --- Buttons Set --- #
        btn_Add_MOG         = QtWidgets.QPushButton("Add MOG")
        btn_Remove_MOG      = QtWidgets.QPushButton("Remove MOG")
        btn_Air_Shot_Before = QtWidgets.QPushButton("Air Shot Before")
        btn_Air_Shot_After  = QtWidgets.QPushButton("Air Shot After")
        btn_Rename          = QtWidgets.QPushButton("Rename")
        btn_Import          = QtWidgets.QPushButton("Import")
        btn_Merge           = QtWidgets.QPushButton("Merge")
        btn_Raw_Data        = QtWidgets.QPushButton("Raw Data")
        btn_Trace_ZOP       = QtWidgets.QPushButton("Trace ZOP")
        btn_Spectra         = QtWidgets.QPushButton("Spectra")
        btn_Stats_tt        = QtWidgets.QPushButton("Stats tt")
        btn_Stats_Ampl      = QtWidgets.QPushButton("Stats Ampl.")
        btn_Ray_Coverage    = QtWidgets.QPushButton("Ray Coverage")
        btn_Export_tt       = QtWidgets.QPushButton("Export tt")
        btn_export_tau      = QtWidgets.QPushButton("Export {}".format(char1))
        btn_Prune           = QtWidgets.QPushButton("Prune")
        btn_delta_t_mog     = QtWidgets.QPushButton(" Create {}t MOG".format(char2))

        # --- List --- #
        self.MOG_list = QtWidgets.QListWidget()

        # --- List Actions --- #
        self.MOG_list.itemSelectionChanged.connect(self.update_edits)

        # --- ComboBoxes --- #
        self.Type_combo = QtWidgets.QComboBox()
        self.Tx_combo = QtWidgets.QComboBox()
        self.Rx_combo = QtWidgets.QComboBox()

        # - ComboBoxes Dispostion -#
        self.Type_combo.addItem("Crosshole")
        self.Type_combo.addItem("VSP/VRP")

        # - ComboBoxes Actions -#
        self.Tx_combo.activated.connect(self.updateCoords)
        self.Rx_combo.activated.connect(self.updateCoords)

        # --- CheckBox --- #
        self.Air_shots_checkbox    = QtWidgets.QCheckBox("Use Air Shots")
        Correction_Factor_checkbox = QtWidgets.QCheckBox("Fixed Time Step Correction Factor")

        # - CheckBoxes' Actions -#
        self.Air_shots_checkbox.stateChanged.connect(self.use_air)

        # --- Labels --- #
        Type_label                          = MyQLabel('Type:', ha='right')
        Tx_label                            = MyQLabel('Tx:', ha='right')
        Rx_label                            = MyQLabel('Rx:', ha='right')
        Nominal_Frequency_label             = MyQLabel('Nominal Frequency of Antenna:', ha='right')
        Rx_Offset_label                     = MyQLabel('Antenna Feedpoint Offset - Rx:', ha='right')
        Tx_Offset_label                     = MyQLabel('Antenna Feedpoint Offset - Tx:', ha='right')
        Multiplication_Factor_label         = MyQLabel('Std Dev. Multiplication Factor:', ha='right')
        Date_label                          = MyQLabel('Date:', ha='right')

        # --- Edits --- #
        self.Air_Shot_Before_edit           = QtWidgets.QLineEdit()
        self.Air_Shot_After_edit            = QtWidgets.QLineEdit()
        self.Nominal_Frequency_edit         = QtWidgets.QLineEdit()
        self.Rx_Offset_edit                 = QtWidgets.QLineEdit()
        self.Tx_Offset_edit                 = QtWidgets.QLineEdit()
        self.Correction_Factor_edit         = QtWidgets.QLineEdit()
        self.Multiplication_Factor_edit     = QtWidgets.QLineEdit()
        self.Date_edit                      = QtWidgets.QLineEdit()

        # - Edits Actions -#
        self.Air_Shot_Before_edit.editingFinished.connect(self.update_mog_info)
        self.Air_Shot_After_edit.editingFinished.connect(self.update_mog_info)
        self.Nominal_Frequency_edit.editingFinished.connect(self.update_mog_info)
        self.Rx_Offset_edit.editingFinished.connect(self.update_mog_info)
        self.Tx_Offset_edit.editingFinished.connect(self.update_mog_info)
        self.Correction_Factor_edit.editingFinished.connect(self.update_mog_info)
        self.Multiplication_Factor_edit.editingFinished.connect(self.update_mog_info)
        self.Date_edit.editingFinished.connect(self.update_mog_info)

        # - Edits Disposition -#
        self.Date_edit.setAlignment(QtCore.Qt.AlignHCenter)

        # --- Buttons actions --- #
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
        btn_Import.clicked.connect(self.import_mog)

        # --- Sub Widgets --- #
        # - Sub AirShots Widget-#
        Sub_AirShots_Widget                 = QtWidgets.QWidget()
        Sub_AirShots_Grid                   = QtWidgets.QGridLayout()
        Sub_AirShots_Grid.addWidget(Type_label, 0, 1)
        Sub_AirShots_Grid.addWidget(Tx_label, 1, 1)
        Sub_AirShots_Grid.addWidget(Rx_label, 2, 1)
        Sub_AirShots_Grid.addWidget(self.Type_combo, 0, 2)
        Sub_AirShots_Grid.addWidget(self.Tx_combo, 1, 2)
        Sub_AirShots_Grid.addWidget(self.Rx_combo, 2, 2)
        Sub_AirShots_Grid.addWidget(self.Air_shots_checkbox, 3, 0)
        Sub_AirShots_Grid.addWidget(self.Air_Shot_Before_edit, 4, 2)
        Sub_AirShots_Grid.addWidget(self.Air_Shot_After_edit, 5, 2)
        Sub_AirShots_Grid.addWidget(btn_Air_Shot_Before, 4, 0, 1, 2)
        Sub_AirShots_Grid.addWidget(btn_Air_Shot_After, 5, 0, 1, 2)
        Sub_AirShots_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_AirShots_Widget.setLayout(Sub_AirShots_Grid)

        # - Sub Labels, Checkbox and Edits Widget -#
        Sub_Labels_Checkbox_and_Edits_Widget = QtWidgets.QWidget()
        Sub_Labels_Checkbox_and_Edits_Grid   = QtWidgets.QGridLayout()
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Nominal_Frequency_label, 0, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Rx_Offset_label, 1, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Correction_Factor_checkbox, 3, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Tx_Offset_label, 2, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Multiplication_Factor_label, 4, 1)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(Date_label, 7, 0)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Nominal_Frequency_edit, 0, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Rx_Offset_edit, 1, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Tx_Offset_edit, 2, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Correction_Factor_edit, 3, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Multiplication_Factor_edit, 4, 2)
        Sub_Labels_Checkbox_and_Edits_Grid.addWidget(self.Date_edit, 7, 1, 1, 2)
        Sub_Labels_Checkbox_and_Edits_Widget.setLayout(Sub_Labels_Checkbox_and_Edits_Grid)

        # - Sub Right Buttons Widget -#
        sub_right_buttons_widget            = QtWidgets.QWidget()
        sub_right_buttons_Grid              = QtWidgets.QGridLayout()
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
        sub_right_buttons_widget.setLayout(sub_right_buttons_Grid)

        # - MOG and list Sub Widget -#
        sub_MOG_and_List_widget            = QtWidgets.QWidget()
        sub_MOG_and_List_Grid              = QtWidgets.QGridLayout()
        sub_MOG_and_List_Grid.addWidget(btn_Add_MOG, 0, 0)
        sub_MOG_and_List_Grid.addWidget(btn_Remove_MOG, 0, 1)
        sub_MOG_and_List_Grid.addWidget(self.MOG_list, 1, 0, 1, 2)
        sub_MOG_and_List_Grid.setContentsMargins(0, 0, 0, 0)
        sub_MOG_and_List_widget.setLayout(sub_MOG_and_List_Grid)

        # ------- Grid Disposition ------- #
        master_grid                        = QtWidgets.QGridLayout()
        # --- Sub Widgets Disposition --- #
        master_grid.addWidget(sub_MOG_and_List_widget, 0, 0)
        master_grid.addWidget(sub_right_buttons_widget, 0, 1)
        master_grid.addWidget(Sub_Labels_Checkbox_and_Edits_Widget, 1, 1)
        master_grid.addWidget(Sub_AirShots_Widget, 1, 0)
        master_grid.setContentsMargins(0, 0, 0, 0)

        # ------- set Layout ------- #
        self.setLayout(master_grid)


class MyQLabel(QtWidgets.QLabel):
    def __init__(self, label, ha='left', parent=None):
        super(MyQLabel, self).__init__(label, parent)
        if ha == 'center':
            self.setAlignment(QtCore.Qt.AlignCenter)
        elif ha == 'right':
            self.setAlignment(QtCore.Qt.AlignRight)
        else:
            self.setAlignment(QtCore.Qt.AlignLeft)


class RawDataFig(FigureCanvasQTAgg):

    def __init__(self):
        fig = mpl.figure.Figure(facecolor='white')
        super(RawDataFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        ax = self.figure.add_axes([0.05, 0.08, 0.9, 0.9])
        divider = make_axes_locatable(ax)
        divider.append_axes('right', size=0.5, pad=0.1)
        ax.set_axisbelow(True)

    def plot_raw_data(self, mogd):
        ax1 = self.figure.axes[0]
        ax2 = self.figure.axes[1]
        ax1.cla()
        ax2.cla()
        mpl.axes.Axes.set_xlabel(ax1, 'Trace No')
        mpl.axes.Axes.set_ylabel(ax1, 'Time units[{}]'.format(mogd.tunits))
        cmax = np.abs(max(mogd.rdata.flatten()))
        h = ax1.imshow(mogd.rdata, cmap='seismic', interpolation='none', aspect='auto', vmin=-cmax, vmax=cmax)
        mpl.colorbar.Colorbar(ax2, h)

        self.draw()


class SpectraFig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(facecolor='white')
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

        Tx = np.unique(mog.data.Tx_z)

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
        Fs = 1 / dt

        # Getting the maximum amplitude value for each column
        A = np.amax(mog.data.rdata, axis=0)

        # Making a matrix which has the same size as rdata but filled with the maximum amplitude of each column
        Amax = np.tile(A, (550, 1))

        # Dividing the original rdata by A max in order to have a normalised amplitude matrix
        normalised_rdata = mog.data.rdata / Amax

        traces = normalised_rdata[:, ind]

        if filter_state:
            # Applying Lowpass Filter
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
            freq, tmp = spy.signal.welch(traces[:, 0], Fs)
            Pxx = np.zeros((len(tmp), np.shape(traces)[1]))
            Pxx[:, 0] = tmp
            for nt in range(1, np.shape(traces)[1]):
                freq, Pxx[:, nt] = spy.signal.welch(traces[:, nt], Fs)
            self.ax2.imshow(np.log10(Pxx).T[:, :Fmax],
                            cmap='plasma',
                            aspect='auto',
                            interpolation='none',
                            extent=[0, Fmax, -np.round(np.max(mog.data.Tx_z)), 0])

        if method == 'Standard Fourier':
            Pxx = np.fft.rfft(traces, axis=0)
            self.ax2.imshow(np.log10(np.abs(Pxx)).T[:, :Fmax],
                            cmap='plasma',
                            aspect='auto',
                            interpolation='none',
                            extent=[0, Fmax, -np.round(np.max(mog.data.Tx_z)), 0])

        # TODO: calculer le spectre avec la méthode Burg
        if method == 'Burg - Order 2':
            Pxx = arburg(traces, 2)
            self.ax2.imshow(np.log10(Pxx).T[:, :Fmax], cmap='plasma', aspect='auto',
                            interpolation='none', extent=[0, Fmax, -np.round(np.max(mog.data.Tx_z)), 0])
        if method == 'Burg - Order 3':
            Pxx = arburg(traces[:, nt], 3)
        if method == 'Burg - Order 4':
            Pxx = arburg(traces[:, nt], 4)

        win_snr = np.round(20 / mog.data.timec)
        SNR = data_select(traces, f0, dt, win_snr)
        SNR = SNR[::-1]

        cmax = max(traces.flatten())
        cmin = -cmax

        # These next conditions ensure the consistency ok the link between the signal to noise ratio and the amplitudes
        if mog.data.Rx_z[ind][-1] > mog.data.Rx_z[ind][0]:
            self.ax1.imshow(traces.T,
                            extent=[0, mog.data.nptsptrc, mog.data.Rx_z[ind][0], mog.data.Rx_z[ind][-1]],
                            cmap='plasma',
                            aspect='auto',
                            interpolation='none',
                            vmin=cmin,
                            vmax=cmax)
        else:
            self.ax1.imshow(traces[::1].T,
                            extent=[0, mog.data.nptsptrc, mog.data.Rx_z[ind][-1], mog.data.Rx_z[ind][0]],
                            cmap='plasma',
                            aspect='auto',
                            interpolation='none',
                            vmin=cmin,
                            vmax=cmax)

        if scale == 'Linear':
            if mog.data.Rx_z[ind][0] > mog.data.Rx_z[ind][-1]:
                self.ax3.plot(SNR[::-1], mog.data.Rx_z[ind])
                self.ax3.set_ylim(mog.data.Rx_z[ind][-1], mog.data.Rx_z[ind][0])
            else:
                self.ax3.plot(SNR, mog.data.Rx_z[ind])
                self.ax3.set_ylim(mog.data.Rx_z[ind][0], mog.data.Rx_z[ind][-1])

        elif scale == 'Logarithmic':
            if mog.data.Rx_z[ind][0] > mog.data.Rx_z[ind][-1]:
                self.ax3.plot(SNR[::-1], mog.data.Rx_z[ind])
                self.ax3.set_ylim(mog.data.Rx_z[ind][-1], mog.data.Rx_z[ind][0])
            else:
                self.ax3.plot(SNR, mog.data.Rx_z[ind])
                self.ax3.set_ylim(mog.data.Rx_z[ind][0], mog.data.Rx_z[ind][-1])

            self.ax3.set_xscale('log')

        mpl.axes.Axes.set_title(self.ax1, 'Normalized amplitude')
        mpl.axes.Axes.set_title(self.ax2, 'Log Power spectra')
        mpl.axes.Axes.set_title(self.ax3, 'Signal-to-Noise Ratio')
        mpl.axes.Axes.set_xlabel(self.ax1, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_ylabel(self.ax1, 'Rx elevation [{}]'.format(mog.data.cunits))
        mpl.axes.Axes.set_xlabel(self.ax2, 'Frequency [MHz]')
        mpl.axes.Axes.set_xlabel(self.ax3, 'SNR')

        self.draw()


class ZOPFig(FigureCanvasQTAgg):  # Zero Offset Profile (ZOP) Figure
    def __init__(self, ui):
        fig = mpl.figure.Figure(facecolor='white')
        super(ZOPFig, self).__init__(fig)
        self.ui = ui
        self.initFig()

    def initFig(self):
        self.ax1 = self.figure.add_axes([0.08, 0.06, 0.4, 0.9])
        self.ax2 = self.figure.add_axes([0.6, 0.06, 0.3, 0.85])

    def plot_zop(self):
        self.ax1.cla()
        self.ax2.cla()

        ind = self.ui.MOG_list.selectedIndexes()
        mog = database.session.query(Mog).all()[ind[0].row()]

        mpl.axes.Axes.set_title(self.ax1, '{}'.format(mog.name))
        mpl.axes.Axes.set_xlabel(self.ax1, ' Time [{}]'.format(mog.data.tunits))
        mpl.axes.Axes.set_ylabel(self.ax2, ' Elevation [{}]'.format(mog.data.cunits))

        tol = float(self.ui.tol_edit.text())
        veloc_state = self.ui.veloc_check.isChecked()
        scont_state = self.ui.const_check.isChecked()
        amp_state = self.ui.amp_check.isChecked()
        color_scale = float(self.ui.color_scale_edit.text())

        dz = np.abs(mog.data.Tx_z - mog.data.Rx_z)
        zop_ind = np.where(dz <= tol)[0]

        zop_picked_ind = np.less_equal(dz, tol).astype(int) + np.not_equal(mog.tt, -1).astype(int)
        zop_picked_ind = np.where(zop_picked_ind == 2)[0]

        tt, in_plus, in_minus, vapp = self.calculate_Vapp(mog)

        zmin = np.round(min(mog.data.Rx_z[zop_ind]), 4)
        zmax = np.round(max(mog.data.Rx_z[zop_ind]), 4)
        tmin = np.round(min(tt), 3)
        tmax = np.round(max(tt), 3)

        self.ui.tmin_edit.setText(str(tmin))
        self.ui.tmax_edit.setText(str(tmax))
        self.ui.zmin_edit.setText(str(zmin))
        self.ui.zmax_edit.setText(str(zmax))

        if veloc_state:

            self.ax2.plot(vapp[zop_picked_ind], mog.data.Rx_z[zop_picked_ind],
                          marker='o',
                          fillstyle='none',
                          color='blue',
                          markersize=5,
                          mew=1,
                          ls='None')

            self.ax2.plot([in_plus[zop_picked_ind], in_minus[zop_picked_ind]],
                          [mog.data.Rx_z[zop_ind], mog.data.Rx_z[zop_ind]],
                          color='grey')
            self.ax2.set_xlabel('Apparent velocity [{}/{}]'.format(mog.data.cunits, mog.data.tunits))
            self.ax2.set_ylim(zmin, zmax)

        if scont_state:
            self.ax2.plot(1 / mog.Tx.scont.valeur,
                          mog.Tx.scont.z,
                          color='black')

        # TODO: faire le module bh_tomo_amp afin de pouvoir obtenir les informations sur les amplitudes
        if amp_state:
            rayl = np.sqrt((mog.data.Tx_x[zop_ind] - mog.data.Rx_x[zop_ind])**2 +
                           (mog.data.Tx_y[zop_ind] - mog.data.Rx_y[zop_ind])**2 +
                           (mog.data.Tx_z[zop_ind] - mog.data.Rx_z[zop_ind])**2)

        self.ax1.imshow(mog.data.rdata[:, zop_ind].T,
                        extent=[mog.data.timestp[0], mog.data.timestp[-1], zmin, zmax],
                        interpolation='none',
                        cmap='seismic',
                        aspect='auto',
                        vmin=-color_scale,
                        vmax=color_scale)

        self.ax1.set_ylim(zmin, zmax)
        self.ax1.set_xlim(mog.data.timestp[0], mog.data.timestp[-1])

        self.ax1.plot(mog.tt[zop_picked_ind],
                      mog.data.Rx_z[zop_picked_ind],
                      marker='o',
                      fillstyle='none',
                      color='green',
                      markersize=5,
                      mew=2,
                      ls='None')

        self.draw()

    def calculate_Vapp(self, mog):

        hyp = np.sqrt((mog.data.Tx_x - mog.data.Rx_x)**2 +
                      (mog.data.Tx_y - mog.data.Rx_y)**2 +
                      (mog.data.Tx_z - mog.data.Rx_z)**2)

        tt, t0 = mog.getCorrectedTravelTimes()
        et = mog.et
        vapp = hyp / tt
        in_minus = hyp / (tt - et)
        in_plus = hyp / (tt + et)
        return tt, in_plus, in_minus, vapp


class ZOPRaysFig(FigureCanvasQTAgg):
    def __init__(self):
        fig = mpl.figure.Figure(figsize=(6, 8), facecolor='white')
        super(ZOPRaysFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_rays(self, mog, offset_tol):
        self.ax.cla()
        dz = np.abs(mog.data.Tx_z - mog.data.Rx_z)

        zop = np.less_equal(dz, offset_tol)

        false_ind = np.nonzero(not zop)

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
            self.ax.plot(xs=Tx_Rx_xs[:, i], ys=Tx_Rx_ys[:, i], zs=Tx_Rx_zs[:, i], c='g')

        self.ax.plot(mog.Tx.fdata[:, 0], mog.Tx.fdata[:, 1], mog.Tx.fdata[:, 2], color='b')
        self.ax.plot(mog.Rx.fdata[:, 0], mog.Rx.fdata[:, 1], mog.Rx.fdata[:, 2], color='b')

        self.ax.text(x=mog.data.Rx_x[0], y=mog.data.Rx_y[0], z=max(mog.data.Rx_z) + 0.5, s=str(mog.Rx.name))
        self.ax.text(x=mog.data.Tx_x[0], y=mog.data.Tx_y[0], z=max(mog.data.Tx_z) + 0.5, s=str(mog.Tx.name))

        self.ax.scatter(xs=mog.data.Rx_x[0], ys=mog.data.Rx_y[0], zs=mog.Tx.fdata[0, 2], c='black', marker='o')
        self.ax.scatter(xs=mog.data.Tx_x[0], ys=mog.data.Tx_y[0], zs=mog.Rx.fdata[0, 2], c='black', marker='o')

        self.ax.set_xlabel('Tx-Rx X Distance [{}]'.format(mog.data.cunits))
        self.ax.set_ylabel('Tx-Rx Y Distance [{}]'.format(mog.data.cunits))
        self.ax.set_zlabel('Elevation [{}]'.format(mog.data.cunits))

        self.draw()


class StatsttFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):

        fig = mpl.figure.Figure(figsize=(100, 100), facecolor='white')
        super(StatsttFig, self).__init__(fig)
        self.initFig()

    def initFig(self):

        self.ax1 = self.figure.add_axes([0.1, 0.1, 0.2, 0.25])
        self.ax2 = self.figure.add_axes([0.4, 0.1, 0.2, 0.25])
        self.ax3 = self.figure.add_axes([0.7, 0.1, 0.2, 0.25])
        self.ax4 = self.figure.add_axes([0.1, 0.55, 0.2, 0.25])
        self.ax5 = self.figure.add_axes([0.4, 0.55, 0.2, 0.25])
        self.ax6 = self.figure.add_axes([0.7, 0.55, 0.2, 0.25])

    def plot_stats(self, mog):

        done = (mog.tt_done + mog.in_vect.astype(int))
        ind = np.where(done == 2)[0]

        tt, t0 = mog.getCorrectedTravelTimes()
        et = mog.et[ind]
        tt = tt[ind]

        hyp = np.sqrt((mog.data.Tx_x[ind] - mog.data.Rx_x[ind])**2 +
                      (mog.data.Tx_y[ind] - mog.data.Rx_y[ind])**2 +
                      (mog.data.Tx_z[ind] - mog.data.Rx_z[ind])**2)

        dz = mog.data.Rx_z[ind] - mog.data.Tx_z[ind]

        theta = 180 / np.pi * np.arcsin(dz / hyp)

        vapp = hyp / tt
        # n = np.arange(len(ind))
        # n = n[ind]
        ind2 = np.less(vapp, 0)
        ind2 = np.nonzero(ind2)[0]

        self.ax4.plot(hyp, tt, marker='o', ls='None')
        self.ax5.plot(theta, hyp / (tt + t0[ind]), marker='o', ls='None')  # tt are corrected, must undo t0 correction
        self.ax2.plot(theta, vapp, marker='o', ls='None')
        self.ax6.plot(t0)
        self.ax1.plot(hyp, et, marker='o', ls='None')
        self.ax3.plot(theta, et, marker='o', ls='None')

        vapp = hyp / tt
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


class VAppFig(FigureCanvasQTAgg):  # Apparent Velocity Figure
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(6, 8), facecolor='white')
        super(VAppFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_vapp(self, mog, vapp, ind):
        # for n in vapp:
        #    print(n)
        Tx = np.array([mog.data.Tx_x[ind], mog.data.Tx_y[ind], mog.data.Tx_z[ind]]).T
        Rx = np.array([mog.data.Rx_x[ind], mog.data.Rx_y[ind], mog.data.Rx_z[ind]]).T
        vmax = max(vapp)
        vmin = min(vapp)
        print(vmax, 'vmax')
        print(vmin, 'vmin')
        X = np.concatenate((Tx, Rx), axis=0)

        c = np.array([[0, 0, 1],
                      [0, 1, 0],
                      [1, 0, 0]])

        c = interpolate.interp1d(np.arange(-100, 101, 100).T, c.T)(np.arange(-100, 101, 2).T)
        m = 200 / (vmax - vmin)
        b = -100 - m * vmin

        # TODO: mettre une colorbar qui affiche le scaling de la vitesse apparente
        for n in range(len(vapp)):
            p = m * vapp[n] + b

            color = interpolate.interp1d(np.arange(-100, 101, 2), c)(p)
            self.ax.plot([Tx[n, 0], Rx[n, 0]], [Tx[n, 1], Rx[n, 1]], [Tx[n, 2], Rx[n, 2]], c=color)

        self.ax.text2D(0.05, 0.95, "{} - Apparent Velocity".format(mog.name), transform=self.ax.transAxes)


class StatsAmpFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):

        fig = mpl.figure.Figure(figsize=(100, 100), facecolor='white')
        super(StatsAmpFig, self).__init__(fig)
        self.initFig()

    def initFig(self):

        # horizontal configuration
        self.ax1 = self.figure.add_axes([0.1, 0.1, 0.2, 0.25])
        self.ax2 = self.figure.add_axes([0.4, 0.1, 0.2, 0.25])
        self.ax3 = self.figure.add_axes([0.7, 0.1, 0.2, 0.25])
        self.ax4 = self.figure.add_axes([0.1, 0.55, 0.2, 0.25])
        self.ax5 = self.figure.add_axes([0.4, 0.55, 0.2, 0.25])
        self.ax6 = self.figure.add_axes([0.7, 0.55, 0.2, 0.25])

    def plot_stats(self, mog):
        # TODO: faire le module Bh_Tomo_amp afin d'avoir les données nécessaires pour les statistiques sur les amplitudes pointées
        hyp = np.sqrt((mog.data.Tx_x - mog.data.Rx_x)**2 +
                      (mog.data.Tx_y - mog.data.Rx_y)**2 +
                      (mog.data.Tx_z - mog.data.Rx_z)**2)

        dz = mog.data.Rx_z - mog.data.Tx_z

        theta = 180 / np.pi * np.arcsin(dz / hyp)

        ind = np.nonzero(mog.amp_tmax != -1)[0] == np.nonzero(mog.tauApp != -1)[0]

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


class RayCoverageFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(6, 8), facecolor='white')
        super(RayCoverageFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_ray_coverage(self, mog, n, show_type, entire_state):
        self.ax.cla()
        picked_tt = np.where(mog.tt != -1)[0]
        unpicked_tt = np.where(mog.tt == -1)[0]
        picked = np.where(mog.in_vect == 1)[0]

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

        percent_coverage = 100 * np.round((len(picked_tt) / mog.data.ntrace), 4)
        self.ax.set_title(str(percent_coverage) + ' %')

        self.ax.text2D(0.05, 0.95, "Ray Coverage", transform=self.ax.transAxes)
        self.ax.set_xlabel('Tx-Rx X Distance [{}]'.format(mog.data.cunits))
        self.ax.set_ylabel('Tx-Rx Y Distance [{}]'.format(mog.data.cunits))
        self.ax.set_zlabel('Elevation [{}]'.format(mog.data.cunits))

        if entire_state:
            if show_type == 'Show picked and unpicked':
                self.ax.plot_wireframe(X=Tx_Rx_xs[:, unpicked_tt],
                                       Y=Tx_Rx_ys[:, unpicked_tt],
                                       Z=Tx_Rx_zs[:, unpicked_tt],
                                       color='red')

                self.ax.plot_wireframe(X=Tx_Rx_xs[:, picked_tt],
                                       Y=Tx_Rx_ys[:, picked_tt],
                                       Z=Tx_Rx_zs[:, picked_tt],
                                       color='green')

                self.draw()

            elif show_type == 'Show picked only':
                self.ax.plot_wireframe(X=Tx_Rx_xs[:, picked_tt],
                                       Y=Tx_Rx_ys[:, picked_tt],
                                       Z=Tx_Rx_zs[:, picked_tt],
                                       color='green')
                self.draw()

            elif show_type == 'Show unpicked only':
                self.ax.plot_wireframe(X=Tx_Rx_xs[:, unpicked_tt],
                                       Y=Tx_Rx_ys[:, unpicked_tt],
                                       Z=Tx_Rx_zs[:, unpicked_tt],
                                       color='red')
                self.draw()
        else:
            Tx = np.unique(mog.data.Tx_z)
            ind_unpicked = np.where(Tx_Rx_zs[0, unpicked_tt] == Tx[n])[0]
            ind_picked = np.where(Tx_Rx_zs[0, picked_tt] == Tx[n])[0]

            if show_type == 'Show picked and unpicked':
                tmp_Tx_Rx_xs = Tx_Rx_xs[:, unpicked_tt]
                tmp_Tx_Rx_ys = Tx_Rx_ys[:, unpicked_tt]
                tmp_Tx_Rx_zs = Tx_Rx_zs[:, unpicked_tt]
                self.ax.plot_wireframe(X=tmp_Tx_Rx_xs[:, ind_unpicked],
                                       Y=tmp_Tx_Rx_ys[:, ind_unpicked],
                                       Z=tmp_Tx_Rx_zs[:, ind_unpicked],
                                       color='red')

                tmp_Tx_Rx_xs = Tx_Rx_xs[:, picked_tt]
                tmp_Tx_Rx_ys = Tx_Rx_ys[:, picked_tt]
                tmp_Tx_Rx_zs = Tx_Rx_zs[:, picked_tt]
                self.ax.plot_wireframe(X=tmp_Tx_Rx_xs[:, ind_picked],
                                       Y=tmp_Tx_Rx_ys[:, ind_picked],
                                       Z=tmp_Tx_Rx_zs[:, ind_picked],
                                       color='green')
                self.draw()

            elif show_type == 'Show picked only':
                tmp_Tx_Rx_xs = Tx_Rx_xs[:, picked_tt]
                tmp_Tx_Rx_ys = Tx_Rx_ys[:, picked_tt]
                tmp_Tx_Rx_zs = Tx_Rx_zs[:, picked_tt]
                self.ax.plot_wireframe(X=tmp_Tx_Rx_xs[:, ind_picked],
                                       Y=tmp_Tx_Rx_ys[:, ind_picked],
                                       Z=tmp_Tx_Rx_zs[:, ind_picked],
                                       color='green')

                self.draw()

            elif show_type == 'Show unpicked only':
                tmp_Tx_Rx_xs = Tx_Rx_xs[:, unpicked_tt]
                tmp_Tx_Rx_ys = Tx_Rx_ys[:, unpicked_tt]
                tmp_Tx_Rx_zs = Tx_Rx_zs[:, unpicked_tt]
                self.ax.plot_wireframe(X=tmp_Tx_Rx_xs[:, ind_unpicked],
                                       Y=tmp_Tx_Rx_ys[:, ind_unpicked],
                                       Z=tmp_Tx_Rx_zs[:, ind_unpicked],
                                       color='red')

                self.draw()


class PruneFig(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        fig = mpl.figure.Figure(figsize=(6, 8), facecolor='white')
        super(PruneFig, self).__init__(fig)
        self.initFig()

    def initFig(self):
        self.ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')

    def plot_prune(self, mog, round_factor):
        self.ax.cla()

        false_Rx_ind = np.nonzero(np.logical_not(mog.in_Rx_vect))  # TODO: false_Rx_ind = np.nonzero(mog.in_Rx_vect == False)
        false_Tx_ind = np.nonzero(np.logical_not(mog.in_Tx_vect))

        Tx_zs = np.unique(mog.data.Tx_z)
        Rx_zs = np.unique(mog.data.Rx_z)

        Tx_zs = np.delete(Tx_zs, false_Tx_ind[0])
        Rx_zs = np.delete(Rx_zs, false_Rx_ind[0])

        if round_factor == 0:
            pass
        else:
            Tx_zs = round_factor * np.round(Tx_zs / round_factor)
            Rx_zs = round_factor * np.round(Rx_zs / round_factor)

        num_Tx = len(Tx_zs)
        num_Rx = len(Rx_zs)
        Tx_xs = mog.data.Tx_x[:num_Tx]
        Rx_xs = mog.data.Rx_x[:num_Rx]
        Tx_ys = mog.data.Tx_y[:num_Tx]
        Rx_ys = mog.data.Rx_y[:num_Rx]

        self.ax.scatter(Tx_xs, Tx_ys, -Tx_zs, c='g', marker='o', label='Tx')

        self.ax.scatter(Rx_xs, Rx_ys, -Rx_zs, c='b', marker='*', label='Rx')

        l = self.ax.legend(ncol=1, bbox_to_anchor=(0, 1), loc='upper left', borderpad=0)
        l.draw_frame(False)

        self.ax.set_xlabel('Tx-Rx X Distance [{}]'.format(mog.data.cunits))
        self.ax.set_ylabel('Tx-Rx Y Distance [{}]'.format(mog.data.cunits))
        self.ax.set_zlabel('Elevation [{}]'.format(mog.data.cunits))

        self.draw()


class MergeMog(QtWidgets.QWidget):

    mergemoglogSignal = QtCore.pyqtSignal(str)

    def __init__(self, mog, parent=None):
        super(MergeMog, self).__init__()
        self.setWindowTitle("Merge MOGs")
        self.mog = mog
        self.initUI()

    def getcompat(self):
        self.comp_list.clear()
        n = self.ref_combo.currentIndex()
        ref_mog = database.session.query(Mog).all()[n]
        ids = []
        nc = 0

        if n == database.session.query(Mog).count():
            QtWidgets.QMessageBox.warning(self, 'Warning', "No compatible MOG found", buttons=QtWidgets.QMessageBox.Ok)
            return

        for mog in database.session.query(Mog).all():
            if mog != ref_mog:
                test1 = ref_mog.Tx == mog.Tx and ref_mog.Rx == mog.Rx
                test2 = False
                test3 = False

                if ref_mog.av is None and mog.av is None:
                    test2 = True
                elif ref_mog.av == mog.av:
                    test2 = True
                if ref_mog.ap is None and mog.ap is None:
                    test3 = True
                elif ref_mog.ap == mog.ap:
                    test3 = True
                test4 = ref_mog.data.TxOffset == mog.data.TxOffset and ref_mog.data.RxOffset == mog.data.RxOffset
                test5 = ref_mog.type == mog.type

                if test1 and test2 and test3 and test4 and test5:
                    nc += 1
                    self.comp_list.addItem("{}".format(mog.name))
                    ids.append(mog.ID)

        if nc == 0:
            dialog = QtWidgets.QMessageBox.information(self, 'Warning', "No compatible MOG found", buttons=QtWidgets.QMessageBox.Ok)

        else:
            self.show()

    def doMerge(self):

        item = self.ref_combo.currentText()
        merge_name = self.comp_list.currentItem().text()
        if len(self.comp_list) == 0:
            self.dialog.setText("No compatible MOG found")
            self.dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
            self.dialog.setIcon(QtWidgets.QMessageBox.Warning)
            return
        if merge_name is None:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOG selected for merging", buttons=QtWidgets.QMessageBox.Ok)
            return
        if not self.new_edit.text():
            QtWidgets.QMessageBox.warning(self, 'Warning', "Please enter a name for the new MOG", buttons=QtWidgets.QMessageBox.Ok)
            return

        for i in range(database.session.query(Mog).count()):
            if database.session.query(Mog).all()[i].name == merge_name:
                merging_mog = database.session.query(Mog).all()[i]
                merge_ind = i
        newName = self.new_edit.text()
        refMog = database.session.query(Mog).filter(Mog.name == item).first()
        newMog = Mog(newName, refMog.data)
        database.session.add(newMog)

        newMog.av           = refMog.av
        newMog.ap           = refMog.ap
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

        if self.erase_check.isChecked():

            self.dialog.setText("following MOGs will be erased : {} {}".format(refMog.name, merging_mog.name))
            self.dialog.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            self.dialog.setIcon(QtWidgets.QMessageBox.Warning)
            ret = self.dialog.exec_()

            if ret == QtWidgets.QMessageBox.Ok:
                self.mergemoglogSignal.emit(
                    " {} and {} have been merged and erased to create {}".format(merging_mog.name,
                                                                                 refMog.name,
                                                                                 newName))
                database.delete(database, refMog)
                database.delete(database, merging_mog)
                self.mog.update_List_Widget()
                self.close()

        else:
            self.mergemoglogSignal.emit("MOG {} have been created by the merge of {} and {}".format(newName,
                                                                                                    refMog.name,
                                                                                                    merging_mog.name))
            self.mog.update_List_Widget()
            self.close()

    def initUI(self):

        # ------- Widgets ------- #
        # --- Labels --- #
        ref_label = MyQLabel('Reference MOG', ha='center')
        comp_label = MyQLabel('Compatible MOGs', ha='center')
        new_label = MyQLabel('New MOG Name', ha='center')

        # --- Edit --- #
        self.new_edit = QtWidgets.QLineEdit()

        # --- List --- #
        self.comp_list = QtWidgets.QListWidget()

        # --- ComboBox --- #
        self.ref_combo = QtWidgets.QComboBox()

        # --- ComboBoxes Actions --- #
        self.ref_combo.activated.connect(self.getcompat)

        # --- Checkbox --- #
        self.erase_check = QtWidgets.QCheckBox('Erase MOGs after merge')

        # --- Buttons --- #
        self.btn_cancel = QtWidgets.QPushButton('Cancel')
        self.btn_merge = QtWidgets.QPushButton('Merge')

        # - Buttons Actions -#
        self.btn_merge.clicked.connect(self.doMerge)
        self.btn_cancel.clicked.connect(self.close)

        # --- MessageBox --- #
        self.dialog = QtWidgets.QMessageBox()

        # ------- Master Grid ------- #
        master_grid = QtWidgets.QGridLayout()
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


class DeltaTMOG(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DeltaTMOG, self).__init__()
        char2 = unicodedata.lookup("GREEK CAPITAL LETTER DELTA")
        self.setWindowTitle("Create {}t MOG".format(char2))
        self.initUI()

    def getcompat(self):
        if database.session.query(Mog).count() != 0:
            self.sub_combo.clear()
            n = self.min_combo.currentIndex()
            ref_mog = database.session.query(Mog).all()[n]
            ids = []
            nc = 0
            if database.session.query(Mog).count() == 1:
                QtWidgets.QMessageBox.warning(self, 'Warning', "Only 1 MOG in Database", buttons=QtWidgets.QMessageBox.Ok)
                return
            for mog in database.session.query(Mog).all():
                if mog != ref_mog:
                    test1 = ref_mog.Tx == mog.Tx and ref_mog.Rx == mog.Rx
                    test2 = False
                    test3 = False

                    if ref_mog.av == '' and mog.av == '':
                        test2 = True
                    if ref_mog.av == mog.av:
                        test2 = True
                    if ref_mog.ap == '' and mog.ap == '':
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
            if nc == 0:
                QtWidgets.QMessageBox.warning(self, 'Warning', "No compatible MOG found", buttons=QtWidgets.QMessageBox.Ok)

            else:
                self.show()
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No MOGs in Database",
                                          buttons=QtWidgets.QMessageBox.Ok)

    def done(self):
        if len(self.sub_combo) == 0:
            QtWidgets.QMessageBox.warning(self, 'Warning', "No compatible MOG found", buttons=QtWidgets.QMessageBox.Ok)
        if not self.name_edit.text():
            QtWidgets.QMessageBox.warning(self, 'Warning', "Please enter a name for new MOG", buttons=QtWidgets.QMessageBox.Ok)

        # Check if traveltimes were picked
        n = self.min_combo.currentIndex()
        refMog = database.session.query(Mog).all()[n]
        ind = refMog.tt == -1
        if np.any(ind):
            QtWidgets.QMessageBox.warning(self, 'Warning', "Traveltimes were not picked for {}".format(refMog.name),
                                          buttons=QtWidgets.QMessageBox.Ok)

    def initUI(self):
        # ------- Widgets ------- #
        # --- Buttons --- #
        cancel_btn = QtWidgets.QPushButton('Cancel')
        done_btn = QtWidgets.QPushButton('Done')
        # --- Labels --- #
        min_label = MyQLabel('Minuend MOG', ha='center')
        sub_label = MyQLabel('Subtrahend MOG', ha='center')
        offset_label = MyQLabel('Offset Tolerance', ha='right')
        name_label = MyQLabel('Name of Difference MOG', ha='right')
        # --- Edits --- #
        self.offset_edit = QtWidgets.QLineEdit('0.5')
        self.name_edit = QtWidgets.QLineEdit()
        # --- ComboBoxes --- #
        self.min_combo = QtWidgets.QComboBox()
        self.sub_combo = QtWidgets.QComboBox()

        # --- ComboBoxes' Actions --- #
        self.min_combo.activated.connect(self.getcompat)

        # ------- Master grid's disposition ------- #
        master_grid = QtWidgets.QGridLayout()
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

    app = QtWidgets.QApplication(sys.argv)

    MOGUI_ui = MOGUI()
    MOGUI_ui.show()

    MOGUI_ui.load_file_MOG('testData/formats/ramac/t0302.rad')

    sys.exit(app.exec_())

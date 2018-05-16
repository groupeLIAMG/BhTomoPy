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
import os
import re
import numpy as np


class MogData(object):
    """
    Class to hold multi-offset gather (mog) data
    """

    def __init__(self, name='', date=''):
        self.ntrace      = 0     # number of traces
        self.nptsptrc    = 0     # number of points per trace
        self.rstepsz     = 0     # size of step used
        self.rnomfreq    = 0     # nominal frequency of antenna
        self.csurvmod    = ''    # survey mode
        self.timec       = 0     # the step of time data
        self.rdata       = 0     # raw data
        self.tdata       = None  # time data
        self.timestp     = 0     # matrix of range self.nptstrc containing all the time referencies
        self.Tx_x        = np.array([0.0])   # x position of the transmitter
        self.Tx_y        = np.array([0.0])   # y position of the transmitter
        self.Tx_z        = np.array([0.0])   # z position of the transmitter
        self.Rx_x        = np.array([0.0])   # x position of the receptor
        self.Rx_y        = np.array([0.0])   # y position of the receptor
        self.Rx_z        = np.array([0.0])   # z position of the receptor
        self.antennas    = ''    # name of the antenna
        self.synthetique = False # if 1 results from numerical modelling and 0 for field data
        self.tunits      = ''    # time units
        self.cunits      = ''    # coordinates units
        self.TxOffset    = 0     # length of he transmittor which is above the surface
        self.RxOffset    = 0     # length of he receptor which is above the surface
        self.comment     = ''    # is defined by the presence of any comment in the file
        self.date        = date  # the date of the data sample
        self.name        = name

    def readRAMAC(self, basename):
        """
        loads data in Malå RAMAC format
        """
        rname = os.path.basename(basename)

        self.name = rname
        self.tunits = 'ns'
        self.cunits = 'm'

        self.readRAD(basename)
        self.readRD3(basename)
        
        self.TxOffset = 0
        self.RxOffset = 0

        if not self.synthetique:

            if self.rnomfreq == 100.0:
                self.TxOffset = 0.665
                self.RxOffset = 0.665
            elif self.rnomfreq == 250.0:
                self.TxOffset = 0.325
                self.RxOffset = 0.365

        self.Tx_y = np.zeros(self.ntrace)
        self.Rx_y = np.zeros(self.ntrace)
        self.Tx_x = np.zeros(self.ntrace)
        self.Rx_x = np.zeros(self.ntrace)
        
        try:
            self.readTLF(basename)
        except IOError as e:
            raise e

        self.Tx_z = self.Tx_z[:self.ntrace]
        self.Rx_z = self.Rx_z[:self.ntrace]


    def readRAD(self, basename):
        """
        loads contents of Malå header file (*.rad extension)
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".rad", 'r')
            except:
                try:
                    file = open(basename + ".RAD", 'r')
                except Exception as e:
                    raise IOError("Cannot open RAD file '" + str(e)[:42] + "...' [mog 2]")

        # knowing the file's contents, we make sure to read every line while looking for keywords. When we've found one of
        # these keyword, we either search the int('\d+'), the float(r"[-+]?\d*\.\d+|\d+") or a str by getting the
        # needed information on the line

        # the search function returns 3 things, the type, the span (i.e. the index(es) of the element(s) that was(were) found)
        # and the group(i.e. the found element)

        lines = file.readlines()
        for line in lines:
            if "SAMPLES:" in line:
                self.nptsptrc = int(re.search('\d+', line).group())
            elif "FREQUENCY:" in line:
                self.timec = float(re.search(r"[-+]?\d*\.\d+|\d+", line).group())
            elif "OPERATOR:" in line:
                if 'MoRad' in line or 'syntetic' in line:
                    self.synthetique = True
                else:
                    self.synthetique = False
            elif "ANTENNAS:" in line:
                start, end = re.search('\d+', line).span()
                self.rnomfreq = float(line[start:end])
                self.antennas = line[9:].strip('\n')
            elif "LAST TRACE" in line:
                self.ntrace = int(re.search('\d+', line).group())

        self.timec = 1000.0 / self.timec
        self.timestp = self.timec * np.arange(self.nptsptrc)

        if not self.synthetique:
            self.antennas = self.antennas + "  - Ramac"

        file.close()
#         print(self.nptsptrc)
#         print(self.timec)
#         print(self.synthetique)
#         print(self.rnomfreq)
#         print(self.antennas)
#         print(self.ntrace)

    def readRD3(self, basename):
        """
        loads contents of *.rd3 extension
        RD3 stands for Ray Dream Designer 3 graphics
        """
        try:
            file = open(basename, 'rb')
        except:
            try:
                file = open(basename + ".rd3", 'rb')
            except:
                try:
                    file = open(basename + ".RD3", 'rb')
                except Exception as e:
                    raise IOError("Cannot open RD3 file '" + str(e)[:42] + "...' [mog 3]")

        self.rdata = np.fromfile(file, dtype='int16', count=self.nptsptrc * self.ntrace)
        self.rdata.resize((self.ntrace, self.nptsptrc))
        self.rdata = self.rdata.T

    def readTLF(self, basename):
        """
        loads contents of *.TLF extension
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".tlf", 'r')
            except:
                try:
                    file = open(basename + ".TLF", 'r')
                except Exception as e:
                    raise IOError("Cannot open TLF file '" + str(e)[:42] + "...' [mog 4]")
        self.Tx_z = np.array([])
        self.Rx_z = np.array([])
        lines = file.readlines()[1:]
        for line in lines:
            line_contents = re.findall(r"[-+]?\d*\.\d+|\d+", line)
            tnd          = int(line_contents[0])     # first trace
            tnf          = int(line_contents[1])     # last trace
            Rxd          = float(line_contents[2])   # first coordinate of the Rx
            Rxf          = float(line_contents[3])   # last coordinate of the Rx
            Tx           = float(line_contents[4])   # Tx's fixed position
            nt           = tnf - tnd + 1
            if nt == 1:
                dRx = 1
                if Rxd > Rxf:
                    Rxd = Rxf
            else:
                dRx = (Rxf - Rxd) / (nt - 1)

            vect = np.arange(Rxd, Rxf + dRx / 2, dRx)

            if nt > 0:
                self.Tx_z = np.append(self.Tx_z, (Tx * np.ones(np.abs(nt))))
                self.Rx_z = np.concatenate((self.Rx_z, vect))
        file.close()

    def readSEGY(self, basename):
        """
        :param basename:
        :return:
        """


class PruneParams(object):
    def __init__(self):
        self.stepTx = 0
        self.stepRx = 0
        self.round_factor = 0
        self.use_SNR = 0
        self.threshold_SNR = 0
        self.zmin = -1e99
        self.zmax = 1e99
        self.thetaMin = -90
        self.thetaMax = 90


class Mog():  # Multi-Offset Gather

    def __init__(self, name='', data=MogData()):
        self.pruneParams              = PruneParams()
        self.name                     = name
        self.data                     = data
        self.tau_params               = np.array([])
        self.fw                       = np.array([])
        self.f_et                     = 1
        self.amp_name_Ldc             = ''
        self.type                     = 0
        self.fac_dt                   = 1
        self.user_fac_dt              = 0
        self.useAirShots              = False
        self.av                       = None
        self.ap                       = None
        self.Tx                       = None
        self.Rx                       = None
        self.TxCosDir                 = np.array([])
        self.RxCosDir                 = np.array([])

        self.in_Rx_vect               = np.ones(self.data.ntrace, dtype=bool)
        self.in_Tx_vect               = np.ones(self.data.ntrace, dtype=bool)
        self.in_vect                  = np.ones(self.data.ntrace, dtype=bool)
        self.date                     = self.data.date
        self.tt                       = -1 * np.ones(self.data.ntrace, dtype=float)
        self.et                       = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tt_done                  = np.zeros(self.data.ntrace, dtype=bool)

        if self.data.tdata is None:
            self.ttTx                 = np.array([])
            self.ttTx_done            = np.array([])
        else:
            self.ttTx                 = np.zeros(self.data.ntrace)
            self.ttTx_done            = np.zeros(self.data.ntrace, dtype=bool)

        self.amp_tmin                 = -1 * np.ones(self.data.ntrace, dtype=float)
        self.amp_tmax                 = -1 * np.ones(self.data.ntrace, dtype=float)
        self.amp_done                 = np.zeros(self.data.ntrace, dtype=bool)
        self.App                      = np.zeros(self.data.ntrace, dtype=float)
        self.fcentroid                = np.zeros(self.data.ntrace, dtype=float)
        self.scentroid                = np.zeros(self.data.ntrace, dtype=float)
        self.tauApp                   = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauApp_et                = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauFce                   = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauFce_et                = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauHyb                   = -1 * np.ones(self.data.ntrace, dtype=float)
        self.tauHyb_et                = -1 * np.ones(self.data.ntrace, dtype=float)
        self.Tx_z_orig                = self.data.Tx_z
        self.Rx_z_orig                = self.data.Rx_z

        self.pruneParams.zmin         = min(np.array([self.data.Tx_z, self.data.Rx_z]).flatten())
        self.pruneParams.zmax         = max(np.array([self.data.Tx_z, self.data.Rx_z]).flatten())
        self.modified                 = True

    def correction_t0(self, ndata, air_before, air_after):
        """
        :param ndata:
        :param air_before: instance of class Airshots
        :param air_after: instance of class Airshots
        """

#        show = False  # TODO
        fac_dt_av = 1
        fac_dt_ap = 1
        if not self.useAirShots:
            t0 = np.zeros(ndata)
            return t0, fac_dt_av, fac_dt_ap
        elif air_before.name == '' and air_after.name == '' and self.useAirShots:
            t0 = np.zeros(ndata)
            raise ValueError("t0 correction not applied; Pick t0 before and t0 after for correction")

        v_air = 0.2998
        t0av = np.array([])
        t0ap = np.array([])

        if air_before.name != '':
            if 'fixed_antenna' in air_before.method:
                t0av = self.get_t0_fixed(air_before, v_air)
            if 'walkaway' in air_before.method:
                pass  # TODO: get_t0_wa

        if air_after.name != '':
            if 'fixed_antenna' in air_before.method:
                t0ap = self.get_t0_fixed(air_after, v_air)

            if 'walkaway' in air_before.method:
                pass  # TODO: get_t0_wa

        if np.isnan(t0av) or np.isnan(t0ap):
            t0 = np.zeros((1, ndata))
            raise ValueError("t0 correction not applied;Pick t0 before and t0 after for correction")

        if np.all(t0av == 0) and np.all(t0ap == 0):
            t0 = np.zeros((1, ndata))
        elif t0av == 0:
            t0 = t0ap + np.zeros((1, ndata))
        elif t0ap == 0:
            t0 = t0av + np.zeros((1, ndata))
        else:
            dt0 = t0ap - t0av
            ddt0 = dt0 / (ndata - 1)
            t0 = t0av + ddt0 * np.arange(ndata)  # TODO: pas sur de cette etape là

        return t0, fac_dt_av, fac_dt_ap

    def getCorrectedTravelTimes(self):

        if self.data.synthetique == 1:
            tt = self.tt
            t0 = np.zeros(np.shape(tt))
            return tt, t0

        t0, fac_dt_av, fac_dt_ap = self.correction_t0(len(self.tt), self.av, self.ap)

        if self.av is not None:
            self.av.fac_dt = fac_dt_av

        if self.ap is not None:
            self.ap.fac_dt = fac_dt_ap

        if self.user_fac_dt == 0:
            if fac_dt_av != 1 and fac_dt_ap != 1:
                self.fac_dt = 0.5 * (fac_dt_av + fac_dt_ap)
            elif fac_dt_av != 1:
                self.fac_dt = fac_dt_av
            elif fac_dt_ap != 1:
                self.fac_dt = fac_dt_ap
            else:
                self.fac_dt = 1

        t0 = self.fac_dt * t0
        tt = self.fac_dt * self.tt - t0

        return tt, t0

    @staticmethod
    def get_t0_fixed(shot, v):
        times = shot.tt
        std_times = shot.et
        ind = np.where(times != -1.0)[0]
        if np.all(std_times == -1.0):
            times = np.mean(times[ind])
        else:
            times = sum(times[ind] * std_times[ind]) / sum(std_times[ind])
        t0 = times - float(shot.d_TxRx[0]) / v
        return t0

    @staticmethod
    def merge_mogs(mog_list, name):
        # we assume all mogs in list are compatible
        new_mog = Mog(name)
        
        mog = mog_list[0]
        new_mog.av = mog.av
        new_mog.ap = mog.ap
        new_mog.Tx = mog.Tx
        new_mog.Rx = mog.Rx
        new_mog.f_et = mog.f_et
        new_mog.type = mog.type
        new_mog.fac_dt = mog.fac_dt
        new_mog.user_fac_dt = mog.user_fac_dt
        new_mog.useAirShots = mog.useAirShots
        new_mog.date = mog.data.date
        
        new_mog.data.nptsptrc = mog.data.nptsptrc
        new_mog.data.rstepsz = mog.data.rstepsz
        new_mog.data.rnomfreq = mog.data.rnomfreq
        new_mog.data.csurvmod = mog.data.csurvmod
        new_mog.data.timec = mog.data.timec
        new_mog.data.tdata = mog.data.tdata
        new_mog.data.timestp = mog.data.timestp
        new_mog.data.antennas = mog.data.antennas
        new_mog.data.synthetique = mog.data.synthetique
        new_mog.data.tunits = mog.data.tunits
        new_mog.data.cunits = mog.data.cunits
        new_mog.data.TxOffset = mog.data.TxOffset
        new_mog.data.RxOffset = mog.data.RxOffset
        new_mog.data.comment = mog.data.comment
        new_mog.data.date = mog.data.date

        new_mog.tau_params = mog.tau_params.copy()
        new_mog.fw = mog.fw.copy()
        new_mog.TxCosDir = mog.TxCosDir.copy()
        new_mog.RxCosDir = mog.RxCosDir.copy()
        new_mog.in_Rx_vect = mog.in_Rx_vect.copy()
        new_mog.in_Tx_vect = mog.in_Tx_vect.copy()
        new_mog.in_vect = mog.in_vect.copy()
        new_mog.tt = mog.tt.copy()
        new_mog.et = mog.et.copy()
        new_mog.tt_done = mog.tt_done.copy()
        new_mog.ttTx = mog.ttTx.copy()
        new_mog.ttTx_done = mog.ttTx_done.copy()
        new_mog.amp_tmin = mog.amp_tmin.copy()
        new_mog.amp_tmax = mog.amp_tmax.copy()
        new_mog.amp_done = mog.amp_done.copy()
        new_mog.App = mog.App.copy()
        new_mog.fcentroid = mog.fcentroid.copy()
        new_mog.scentroid = mog.scentroid.copy()
        new_mog.tauApp = mog.tauApp.copy()
        new_mog.tauApp_et = mog.tauApp_et.copy()
        new_mog.tauFce = mog.tauFce.copy()
        new_mog.tauFce_et = mog.tauFce_et.copy()
        new_mog.tauHyb = mog.tauHyb.copy()
        new_mog.tauHyb_et = mog.tauHyb_et.copy()
        new_mog.Tx_z_orig = mog.Tx_z_orig.copy()
        new_mog.Rx_z_orig = mog.Rx_z_orig.copy()
        
        new_mog.data.ntrace = mog.data.ntrace
        new_mog.data.rdata = mog.data.rdata.copy()
        new_mog.data.Tx_x = mog.data.Tx_x.copy()
        new_mog.data.Tx_y = mog.data.Tx_y.copy() 
        new_mog.data.Tx_z = mog.data.Tx_z.copy()
        new_mog.data.Rx_x = mog.data.Rx_x.copy()
        new_mog.data.Rx_y = mog.data.Rx_y.copy()
        new_mog.data.Rx_z = mog.data.Rx_z.copy()

        for n in range(1, len(mog_list)):
            mog = mog_list[n]
            
            new_mog.tau_params = np.r_[new_mog.tau_params, mog.tau_params]
            new_mog.fw = np.r_[new_mog.fw, mog.fw]
            new_mog.TxCosDir = np.c_[new_mog.TxCosDir, mog.TxCosDir]
            new_mog.RxCosDir = np.c_[new_mog.RxCosDir, mog.RxCosDir]
            new_mog.in_Rx_vect = np.r_[new_mog.in_Rx_vect, mog.in_Rx_vect]
            new_mog.in_Tx_vect = np.r_[new_mog.in_Tx_vect, mog.in_Tx_vect]
            new_mog.in_vect = np.r_[new_mog.in_vect, mog.in_vect]
            new_mog.tt = np.r_[new_mog.tt, mog.tt]
            new_mog.et = np.r_[new_mog.et, mog.et]
            new_mog.tt_done = np.r_[new_mog.tt_done, mog.tt_done]
            new_mog.ttTx = np.r_[new_mog.ttTx, mog.ttTx]
            new_mog.ttTx_done = np.r_[new_mog.ttTx_done, mog.ttTx_done]
            new_mog.amp_tmin = np.r_[new_mog.amp_tmin, mog.amp_tmin]
            new_mog.amp_tmax = np.r_[new_mog.amp_tmax, mog.amp_tmax]
            new_mog.amp_done = np.r_[new_mog.amp_done, mog.amp_done]
            new_mog.App = np.r_[new_mog.App, mog.App]
            new_mog.fcentroid = np.r_[new_mog.fcentroid, mog.fcentroid]
            new_mog.scentroid = np.r_[new_mog.scentroid, mog.scentroid]
            new_mog.tauApp = np.r_[new_mog.tauApp, mog.tauApp]
            new_mog.tauApp_et = np.r_[new_mog.tauApp_et, mog.tauApp_et]
            new_mog.tauFce = np.r_[new_mog.tauFce, mog.tauFce]
            new_mog.tauFce_et = np.r_[new_mog.tauFce_et, mog.tauFce_et]
            new_mog.tauHyb = np.r_[new_mog.tauHyb, mog.tauHyb]
            new_mog.tauHyb_et = np.r_[new_mog.tauHyb_et, mog.tauHyb_et]
            new_mog.Tx_z_orig = np.r_[new_mog.Tx_z_orig, mog.Tx_z_orig]
            new_mog.Rx_z_orig = np.r_[new_mog.Rx_z_orig, mog.Rx_z_orig]
            
            new_mog.data.ntrace += mog.data.ntrace
            new_mog.data.rdata = np.c_[new_mog.data.rdata, mog.data.rdata]
            new_mog.data.Tx_x = np.r_[new_mog.data.Tx_x, mog.data.Tx_x]
            new_mog.data.Tx_y = np.r_[new_mog.data.Tx_y, mog.data.Tx_y]
            new_mog.data.Tx_z = np.r_[new_mog.data.Tx_z, mog.data.Tx_z]
            new_mog.data.Rx_x = np.r_[new_mog.data.Rx_x, mog.data.Rx_x]
            new_mog.data.Rx_y = np.r_[new_mog.data.Rx_y, mog.data.Rx_y]
            new_mog.data.Rx_z = np.r_[new_mog.data.Rx_z, mog.data.Rx_z]

        new_mog.pruneParams.zmin = min(np.array([new_mog.data.Tx_z, new_mog.data.Rx_z]).flatten())
        new_mog.pruneParams.zmax = max(np.array([new_mog.data.Tx_z, new_mog.data.Rx_z]).flatten())
        
        return new_mog

class AirShots():
    def __init__(self, name='', data=MogData()):
        self.name = name
        self.data = data
        self.d_TxRx = 0
        self.fac_dt = 1

        self.tt = -1 * np.ones((1, self.data.ntrace), dtype=float)
        self.et = -1 * np.ones((1, self.data.ntrace), dtype=float)
        self.tt_done = np.zeros((1, self.data.ntrace), dtype=bool)
        
        self.modified = True


if __name__ == '__main__':

    m = Mog('M01')
    md = MogData()
    md.readRAMAC('testData/formats/ramac/t0102')
    m.data = md

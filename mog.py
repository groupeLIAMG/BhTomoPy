# -*- coding: utf-8 -*-
"""
Copyright 2016 Bernard Giroux, Elie Dumas-Lefebvre
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it /will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
from MogData import MogData


class AirShots:
    def __init__(self, name=None):
        self.mog = Mog()
        self.name = name
        self.tt = np.array([])     # traveltime vector
        self.et = np.array([])     # traveltime standard vector deviation
        self.data = MogData()      # MogData instance
        self.d_TxRx = 0            # Distance between Tx and Rx
        self.fac_dt = 0            #
        self.ing = 0               #à vérifier avec Bernard (ing et method)
        self.method = 0


        self.initialize()

    def initialize(self):
        """
        We initialize two vectors(i.e. self.tt and self.et) which have a value of -1 for each trace and a vector(i.e. self.tt_done)
        which as a false value for each trace until one actually arrives to the receptor
        """
        if self.mog.data == None :
            return self.mog.data
        self.tt = -1*np.ones((1, self.data.ntrace), dtype = float) #arrival time
        self.et = -1*np.ones((1, self.data.ntrace), dtype = float) #standard deviation of arrival time
        self.tt_done = np.zeros((1, self.data.ntrace), dtype=bool) #boolean indicator of arrival time


class Mog:
    def __init__(self, name= ''):
        self.pruneParams              = PruneParams()
        self.name                     = name          # Name of the multi offset-gather
        self.data                     = MogData()     # Instance of Mogdata
        self.av                       = np.array([])  # Air shot before
        self.ap                       = np.array([])  # Airshot after
        self.Tx                       = 1
        self.Rx                       = 1
        self.tau_params               = np.array([])
        self.fw                       = np.array([])
        self.f_et                     = 1
        self.amp_name_Ldc             = []
        self.type                     = 1
        self.fac_dt                   = 1
        self.user_fac_dt              = 0
        self.pruneParams.stepTx       = 0
        self.pruneParams.stepRx       = 0
        self.pruneParams.round_factor = 0
        self.pruneParams.use_SNR      = 0
        self.pruneParams.treshold_SNR = 0
        self.pruneParams.zmin         = -1e99
        self.pruneParams.zmax         = 1e99
        self.pruneParams.thetaMin     = -90
        self.pruneParams.thetaMax     = 90
        self.useAirShots              = 0
        self.ID                       = Mog.getID()

    def initialize(self):
        if self.data == None:
            return
        self.date                     = self.data.date
        self.tt                       = -1*np.ones((1,self.data.ntrace), dtype= float)
        self.et                       = -1*np.ones((1,self.data.ntrace), dtype= float)
        self.tt_done                  = np.zeros((1, self.data.ntrace), dtype = bool)
        if self.data.tdata == None:
            self.ttTx                 = np.array([])
            self.ttTx_done            = np.array([])
        else:
            self.amp_tmin             = -1*np.ones((1,self.data.ntrace), dtype= float)   # à Définir avec Bernard
            self.amp_tmax             = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.amp_done             = np.zeros((1,self.data.ntrace), dtype= bool)
            self.App                  = np.zeros((1,self.data.ntrace), dtype= float)
            self.fcentroid            = np.zeros((1,self.data.ntrace), dtype= float)
            self.scentroid            = np.zeros((1,self.data.ntrace), dtype= float)
            self.tau_App              = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.tauApp_et            = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.tauFce               = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.tauFce_et            = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.tauHyb               = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.tauHyb_et            = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.tauHyb_et            = -1*np.ones((1,self.data.ntrace), dtype= float)
            self.Tx_z_orig            = self.data.Tx_z
            self.Rx_z_orig            = self.data.Rx_z
            self.inside               = np.ones((1,self.data.ntrace), dtype= bool)  #substitut de obj.in
            self.pruneParams.zmin     = min(np.array([self.data.Tx_z, self.data.Rx_z]))
            self.pruneParams.zmax     = max(np.array([self.data.Tx_z, self.data.Rx_z]))
#TODO:
    def correction_t0(self, ndata, air_before, air_after, *args):
        """
        :param ndata:
        :param air_before: instance of class Airshots
        :param air_after: instance of class Airshots
        :return:
        """
        nargin = len(args)
        if nargin >= 4 :
            show = args[1]
        else:
            show = False
        fac_dt_av = 1
        fac_dt_ap = 1
        if self.useAirShots == 0:
            t0 = np.zeros((1, ndata))
            return
        elif air_before == None and air_after == None and self.useAirShots == 1 :
            t0 = np.zeros((1, ndata))
            raise InterruptedError(" t0 correction not applied;Pick t0 before and t0 after for correction")

        v_air = 0.2998
        t0av = np.array([])
        t0ap = np.array([])

        if air_before == None :
            if 'fixed_antenna' in air_before.method:
                pass
            if 'walkaway' in air_before.method:
                pass

    @staticmethod
    def load_self(mog):
        Mog.getID(mog.ID)
    @staticmethod
    def get_t0_fixed(shot, v):
        times = shot.tt # à vérifier
        std_times = shot.et
        ind = []
        for i in range(len(times.flatten())):
            if times[i] != -1:
                ind.append(i)
        minus_ind = np.transpose(np.nonzero(std_times))

        if len(minus_ind) == 0:
            times = np.mean(times[ind])
        else:
            std_tot = 0
            for i in ind:
                std_tot = std_tot + std_times[i]
            times = sum(times[ind]*std_times[ind]/std_tot)

        t0 = times - shot.d_TxRx/v







    @staticmethod
    def getID(*args):
        nargin = len(args)
        counter = 0
        if nargin == 1:
            if counter == 0:
                counter = args[1]
            elif counter < args[1]:
                counter = args[1]
        if counter == 0:
            counter = 1
        else:
            counter += 1

        ID = counter
        return ID

    def getCorrectedTravelTimes(self, air):
        for element in air:
            if isinstance(element, AirShots):
                pass
            else:
                raise TypeError ("air shot should be instance of class AirShots")

            if self.data.synthetique == 1:
                tt = self.tt
                t0 = np.zeros(tt.size)
                return tt and t0
            else:
                airBefore = air(self.av)
                airAfter = air(self.ap)



class PruneParams:
    def __init__(self):
        self.stepTx = 0
        self.stepRx = 0
        self.round_factor = 0
        self.use_SNR = 0
        self.treshold_SNR = 0
        self.zmin = -1e99
        self.zmax = 1e99
        self.thetaMin = -90
        self.thetaMax = 90






















if __name__ == '__main__':

    m = MogData('M01' )

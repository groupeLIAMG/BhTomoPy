# -*- coding: utf-8 -*-
"""
Copyright 2016 Bernard Giroux
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
class AirShots:
    def __init__(self, name=None):
        self.name = name
        self.tt = np.array([])     # traveltime vector
        self.et = np.array([])     # traveltime standard vector deviation
        self.data = None

    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self.__name = str(name)
        else:
            raise TypeError("Please enter a valid borehole name(i.e. a str)")

    @property
    def data(self):
        return self.__data
    @data.setter
    def data(self,data):
        if isinstance(data, MogData):
            self.__data = data
            self.initialize()
        else:
            raise TypeError("Please enter valid data of type MogData")

    def initialize(self):
        if self.data == None :
            return self.data
        self.tt = -1*np.ones((1, self.data.ntrace), dtype = float) #arrival time
        self.et = -1*np.ones((1, self.data.ntrace), dtype = float) #standard deviation of arrival time
        self.tt_done = np.zeros((1, self.data.ntrace), dtype=bool) #boolean indicator of arrival time


class MogData:
    """
    Class to hold multi-offset gather (mog) data
    """
    def __init__(self, name=None, date=None):
        self.name = name
        self.date = date
        self.av = None             # index of air shot before survey
        self.ap = None             # index of air shot after survey
        self.tt = np.array([])     # traveltime vector
        self.et = np.array([])     # traveltime standard vector deviation
        self.ntrace      = 0       # number of traces in MOG
        self.nptsptrc    = 0       # number of sample per trace
        self.rstepsz     = 0       # theoretical spatial step size between traces
        self.cunits      = ''      # spatial units
        self.rnomfreq    = 0       # nominal frequency of source
        self.csurvmod    = ''      # type of survey
        self.timec       = 0       # sampling period
        self.rdata       = 0       # raw data
        self.timestp     = 0       # time vector
        self.Tx_x        = 0       # x coordinate of source
        self.Tx_z        = 0       # z coordinate of source
        self.TxCosDir    = 0       # direction cosine of source
        self.Rx_x        = 0       # x coordinate of receiver
        self.Rx_z        = 0       # z coordinate of receiver
        self.RxCosDir    = 0       # direction cosine of receiver
        self.antennas    = ''      # type of antenna
        self.synthetique = 0       # true of synthetic data
        self.tunits      = ''      # time units


    # vérification d'entrées
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self.__name = str(name)
        else:
            raise TypeError("Please enter a valid borehole name(i.e. a str)")

    @property
    def date(self):
        return self.__date
    @date.setter
    def date(self, date):
        if isinstance(date, str):
            self.__date = date
        else:
            raise TypeError("please enter a valid date")

    @property
    def data(self):
        return self.__data
    @data.setter
    def data(self,data):
        if isinstance(data, MogData):
            self.__data = data
        else:
            raise TypeError("Please enter valid data of type MogData")

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













    def readRAMAC(self, basename):
        """
        load data in Malå RAMAC format
        """

        self.tunits = 'ns'
        self.cunits = 'm'

        self.readRAD(basename)


    def readRAD(self, basename):
        """
        load content of Malå header file (*.rad extension)
        """








if __name__ == '__main__':

    m = MogData('M01' )

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


class MogData:
    """
    Class to hold multi-offset gather (mog) data
    """
    def __init__(self, name=None):
        self.name = name

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
        self.Rx_x        = 0       # x coordinate of receiver
        self.Rx_z        = 0       # z coordinate of receiver
        self.antennas    = ''      # type of antenna
        self.synthetique = 0       # true of synthetic data
        self.tunits      = ''      # time units


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

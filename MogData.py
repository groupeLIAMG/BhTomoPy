# -*- coding: utf-8 -*-
import scanf
import re
import numpy as np
from os.path import getsize


class MogData:
    """
    Class to hold multi-offset gather (mog) data
    """
    def __init__(self, name=None, date=None):
        self.ntrace       = 0       # number of traces
        self.nptsptrc     = 0       # number of points per trace
        self.rstepsz      = 0       # size of step used
        self.rnomfreq     = 0       # nominal frequency of antenna
        self.csurvmod     = ''      # survey mode
        self.timec        = 0       # the step of time data
        self.rdata        = 0       # raw data
        self.tdata        = None    # time data
        self.timestp      = 0       # matrix of range self.nptstrc containing all the time referencies
        self.Tx_x         = 0       # x position of the transmitor
        self.Tx_y         = 0       # y position of the transmitor
        self.Tx_z         = 0       # z position of the transmitor
        self.Rx_x         = 0       # x position of the receptor
        self.Rx_y         = 0       # y position of the receptor
        self.Rx_z         = 0       # z position of the receptor
        self.antennas     = ''      # name of the antenna
        self.synthetique  = 0       # if 1 results from numerical modelling and 0 for field data
        self.tunits       = 0       # time units
        self.cunits       = ''      # coordinates units
        self.TxOffset     = 0       # length of he transmittor which is above the surface
        self.RxOffset     = 0       # length of he receptor which is above the surface
        self.comment      = ''      # is defined by the presence of any comment in the file
        self.date         = ''      # the date of the data sample
        self.name         = name

    def readRAMAC(self, basename):
        """
        load data in Malå RAMAC format
        """

        self.tunits = 'ns'
        self.cunits = 'm'

        self.readRAD(basename)
        self.readRD3(basename)
        self.readTLF(basename)




        self.TxOffset = 0
        self.RxOffset = 0

        if not self.synthetique:

            if self.rnomfreq == 100.0:
                self.TxOffset = 0.665
                self.RxOffset = 0.665
            elif self.rnomfreq == 250.0:
                self.TxOffset = 0.325
                self.RxOffset = 0.365

        self.Tx_z = self.Tx_z*np.arange(self.ntrace)
        self.Rx_z = self.Rx_z*np.arange(self.ntrace)
        self.Tx_y = np.zeros((1, self.ntrace))
        self.Rx_y = np.zeros((1, self.ntrace))
        self.Tx_x = np.zeros((1, self.ntrace))
        self.Rx_x = np.zeros((1, self.ntrace))


    def readRAD(self, basename):
        """
        load content of Malå header file (*.rad extension)
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".rad", 'r')
            except:
                try:
                    file = open(basename + ".RAD", 'r')
                except:
                    raise IOError (" Cannot open Rad file: {}".format(basename))

        # knowing he file's content, we make sure to read every line while looking for keywords. When we've found on of
        # these keyword, we either search the int('\d+'), the float(r"[-+]?\d*\.\d+|\d+") or a str by getting the
        # needed information on the line

        # the search function returns 3 things, the type, the span(i.e. the index(es) of the element that was found )
        # and the group(i.e. the found element)

        lines = file.readlines()
        for line in lines:
            if "SAMPLES:" in line:
                self.nptsptrc = int(re.search('\d+', line).group())
            elif "FREQUENCY:" in line:
                self.timec = float(re.search(r"[-+]?\d*\.\d+|\d+", line).group())
            elif "OPERATOR:" in line:
                if 'MoRad' in line  or 'syntetic' in line:
                    self.synthetique = True
                else:
                    self.synthetique = False
            elif "ANTENNAS:" in line :
                start, end = re.search('\d+', line).span()
                self.rnomfreq = float(line[start:end])
                self.antennas = line[9:].strip('\n')
            elif "LAST TRACE" in line:
                self.ntrace = int(re.search('\d+', line).group())

        self.timec = self.timec/1000
        self.timestp = self.timec*np.arange(self.nptsptrc)
        if self.synthetique == False :
          self.antennas = self.antennas + "  - Ramac"

        file.close()
        #print(self.nptsptrc)    # these prints will be deleted
        #print(self.timec)
        #print(self.synthetique)
        #print(self.rnomfreq)
        #print(self.antennas)
        #print(self.ntrace)
        #print(self.timestp)


    def readRD3(self, basename):
        """
        load content of *.rd3 extension
        fact: RD3 stands for Ray Dream Designer 3 graphics
        """
        try:
            file = open(basename, 'rb')
        except:
            try:
                file = open(basename + ".rd3", 'rb')
            except:
                try:
                    file = open(basename + ".RD3", 'rb')
                except:
                    raise IOError(" Cannot open RD3 file: {}".format(basename))

        self.rdata = np.fromfile(file, dtype= 'int16', count= self.nptsptrc*self.ntrace)
        self.rdata.resize((self.ntrace, self.nptsptrc))
        self.rdata = self.rdata.T


    def readTLF(self, basename):
        """
        load content of *.TLF extension
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".tlf", 'r')
            except:
                try:
                    file = open(basename + ".TLF", 'r')
                except:
                    raise IOError(" Cannot open TLF file: {}".format(basename))
        self.Tx_z = np.array([])
        self.Rx_z = np.array([])
        lines = file.readlines()[1:]
        for line in lines:
            line_content = re.findall(r"[-+]?\d*\.\d+|\d+", line )
            tnd          = int(line_content[0])     # frist trace
            tnf          = int(line_content[1])     # last trace
            Rxd          = float(line_content[2])   # first coordinate of the Rx
            Rxf          = float(line_content[3])   # last coordinate of the Rx
            Tx           = float(line_content[4])   # Tx's fixed position
            nt           = tnf - tnd + 1
            if nt == 1:
                dRx = 1
                if Rxd > Rxf :
                    Rxd = Rxf
            else:
                dRx = (Rxf - Rxd)/ (nt - 1)


            vect = np.arange(Rxd,Rxf+dRx/2, dRx)

            if nt > 0:
                self.Tx_z = np.append(self.Tx_z, (Tx*np.ones(np.abs(nt))))
                self.Rx_z = np.concatenate((self.Rx_z, vect))
        file.close()
        #print(self.Tx_z)
        #print(self.Rx_z)


    def readSEGY(self, basename):
        """

        :param basename:
        :return:
        """

if __name__ == '__main__':

    m = MogData()
    #m.readRAD('testData/formats/ramac/t0102')
    #m.readRD3('testData/formats/ramac/t0102')
    #m.readTLF('testData/formats/ramac/t0102')
    m.readRAMAC('testData/formats/ramac/t0102')



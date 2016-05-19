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
        self.ntrace = 0
        self.nptsptrc = 0
        self.rstepsz  = 0
        self.rnomfreq = 0
        self.csurvmod = ''
        self.timec = 0
        self.rdata = 0
        self.tdata = None
        self.timestp = 0
        self.Tx_x = 0
        self.Tx_y = 0
        self.Tx_z = 0
        self.Rx_x = 0
        self.Rx_y = 0
        self.Rx_z = 0
        self.antennas = ''
        self.synthetique = 0
        self.tunits = 0
        self.cunits = ''
        self.TxOffset = 0
        self.RxOffset = 0
        self.comment = ''
        self.date = ''
#TODO:
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
        self.Tx_y = np.zeros(1, self.ntrace)
        self.Rx_y = np.zeros(1, self.ntrace)
        self.Tx_x = np.zeros(1, self.ntrace)
        self.Rx_x = np.zeros(1, self.ntrace)


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
                self.antennas = line[9:]
            elif "LAST TRACE" in line:
                self.ntrace = int(re.search('\d+', line).group())  # ca fonctionne dans test, mais pas ici, voir Bernard

        self.timec = self.timec/1000
        self.timestp = self.timec*np.arange(self.nptsptrc)
        if not self.synthetique :
            self.antennas = self.antennas + " - Ramac"

        file.close()
        print(self.nptsptrc)
        print(self.timec)
        print(self.synthetique)
        print(self.rnomfreq)
        print(self.antennas)
        print(self.ntrace)

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
        self.rdata.reshape(self.nptsptrc, self.ntrace)

        print(self.rdata)  # petit problème ici, le print retourne une un array vide. est-ce un problème ?



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
        for line in file:
            tnd = scanf.sscanf(line,'%d')
            tnf = scanf.sscanf(line,'%d')
            self.nt = tnd - tnf + 1           # nt = toujours 1 ?

            Rxd = scanf.sscanf(line, '%f')
            Rxf = scanf.sscanf(line, '%f')

            if self.nt == 1:
                dRx = 1
                if Rxd > Rxf :
                    Rxd = Rxf
                else:
                    dRx = (Rxf - Rxd)/ (self.nt - 1)

            Tx = scanf.sscanf(file, '%f')
            #TODO
            vect = np.arange(start= Rxd, stop= Rxf)

            if self.nt > 0:
                self.Tx_z = np.array([self.Tx_z, Tx*np.ones(1, self.nt)])

        file.close()
    def readEKKO(self, basename):
        """
        well, that's about it
        """
        self.readHD(basename)
        self.readDT1(basename)

    def readHD(self, basename):
        """
        :param basename:
        :return:
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".hd", 'r')
            except:
                try:
                    file = open(basename + ".HD", 'r')
                except:
                    raise IOError(" Cannot open HD file: {}".format(basename))

        self.antennas = 'Ekko'
        self.synthetique = 0
        self.tunits = 'ns'
        self.comment = file.readline()
        line = file.readline()

        if not line:
            if "VRP" in line[1:3]:
                ic = []
                for i in range(len(line)):
                    if line[i] == '=':
                        ic.append(i)
                    count = len(line)
                    tRx_z = re.findall(r"[-+]?\d*\.\d+|\d+", line[ic[2]+1 : count]) # verifier avec Benard , le '\d+.\d+'
            elif "ZOP" or "MOG" in line[1:3]:                                   # cherche les floats
                ic = []
                for i in range(len(line)):
                    if line[i] == '=':
                        ic.append(i)
                    count = len(line)
                    tTx_z = re.findall(r"[-+]?\d*\.\d+|\d+", line[ic[0]+1 : count])
                    tRx_z = re.findall(r"[-+]?\d*\.\d+|\d+", line[ic[1]+1 : count])

        self.date = file.readline() # pas trop sur du resultat
        for line in file:
            if isinstance(line, str):
                if 'NUMBER OF TRACES' not in line:
                    self.ntrace = float(re.search('\d+', line).group())          # re.search('\d+', line).group() returns the
                elif 'NUMBER OF PTS/TRC' not in line:                            # number we are looking for
                    self.nptsptrc = float(re.search('\d+', line).group())
                elif 'TOTAL TIME WINDOW' not in line:
                    nttwin = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                elif 'STEP SIZE USED' not in line:
                    self.rstepsz = re.findall(r"[-+]?\d*\.\d+|\d+", line) # re.findall(r"[-+]?\d*\.\d+|\d+", line) returns
                elif 'POSITION UNITS' not in line:                        # a list which contains al the floats that were
                    self.cunits = line[20:]                               # found
                elif 'NOMINAL FREQUENCY' not in line:
                    self.rnomfreq = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                elif 'ANTENNA SEPARATION' not in line:
                    rantsep = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                elif 'SURVEY MODE' not in line:
                    self.csurvmod = line[21:]
        file.close()


        self.timec = nttwin/self.nptsptrc
        self.timestp = self.timec*np.arange(self.nptsptrc)

        self.Tx_x = np.zeros(1, self.ntrace)
        self.Tx_z = tTx_z*np.ones(1, self.ntrace)
        self.Rx_x = rantsep*np.ones(1, self.ntrace)
        self.Rx_z = tRx_z + self.rstepsz*np.arange(self.ntrace)

    def readDT1(self, basename):
        """

        :param basename:
        :return:
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".dt1", 'r')
            except:
                try:
                    file = open(basename + ".DT1", 'r')
                except:
                    raise IOError(" Cannot open DT1 file: {}".format(basename))

        self.rdata = np.array([])
        for n in range(self.nt):
            header = np.fromfile(file, dtype= 'float32', count= 25)
            np.fromfile(file, dtype= 'char', count = 28)
            be_vector = np.arange(0, np.fromfile(file, dtype='int16',count= header(3))) # est ce que np.fromfile(file, dtype='int16',count= header(3))
            self.rdata = np.concatenate((self.rdata, be_vector))                        # retourne un chiffre ? j'ai de la difficulté a y croire

        file.close()

    def readSEGY(self, basename):
        """

        :param basename:
        :return:
        """

if __name__ == '__main__':

    m = MogData()
    m.readRAD('testData/formats/ramac/t0102')
    m.readRD3('testData/formats/ramac/t0102')




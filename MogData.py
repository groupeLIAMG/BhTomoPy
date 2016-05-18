import scanf
import re
import numpy as np

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
            if isinstance(line, str):
                if "SAMPLES:" not in line:
                    self.nptsptrc = scanf.sscanf(line, '%*8c%d')
                elif "FREQUENCY:" not in line:
                    self.timec = scanf.sscanf(line,'%*10c%f' )
                elif "OPERATOR:" not in line:
                    self.synthetique = re.match('MoRad' and 'once', line) , re.match('synthetic' and 'once', line)  # Vraiment pas sur de cette etape, voir Bernard
                elif "ANTENNAS:" not in line :
                    start, end = re.match('\d+', line)
                    self.rnomfreq = float(line[start:end])
                    self.antennas = line[10:]
                elif "LAST TRACE" not in line:
                    self.ntrace = scanf.sscanf(line, '%*s %*6c%d')
                else:
                    print('Well i dont know whats the problem')

        self.timec = self.timec/1000
        self.timestp = self.timec[:self.nptsptrc - 1]  # Pas sur de cette étape la non plus
                                                           # Pk obj.timec*(0:obj.nptsptrc - 1) dans matlab?
        if self.synthetique == 0 :
            self.antennas = self.antennas + " - Ramac"

        file.close()

    def readRD3(self, basename):
        """
        load content of *.rd3 extension
        fact: RD3 stands for Ray Dream Designer 3 graphics
        """
        try:
            file = open(basename, 'r')
        except:
            try:
                file = open(basename + ".rd3", 'r')
            except:
                try:
                    file = open(basename + ".RD3", 'r')
                except:
                    raise IOError(" Cannot open RD3 file: {}".format(basename))
        self.rdata = file.read(n= 16)


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
        while file.read():
            tnd = scanf.sscanf(file,'%d')
            tnf = scanf.sscanf(file,'%d')
            nt = tnd - tnf + 1           # nt = toujours 1 ?

            Rxd = scanf.sscanf(file, '%f')
            Rxf = scanf.sscanf(file, '%f')

            if nt == 1:
                dRx = 1
                if Rxd > Rxf :
                    Rxd = Rxf
                else:
                    dRx = (Rxf - Rxd)/ (nt - 1)

            Tx = scanf.sscanf(file, '%f')

            if nt > 0:
                self.Tx_z = np.array([self.Tx_z, Tx*np.ones(1, nt)])

        file.close()
    def readEKKO(self, basename):
        """
        """

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
                    scanf.sscanf(line[ic[0]+1 : count], '%f')
                    scanf.sscanf(line[ic[1]+1 : count], '%f')
                    tRx_z = scanf.sscanf(line[ic[2]+1 : count], '%f')
            elif "ZOP" or "MOG" in line[1:3]:
                ic = []
                for i in range(len(line)):
                    if line[i] == '=':
                        ic.append(i)
                    count = len(line)
                    tTx_z = scanf.sscanf(line[ic[0]+1 : count], '%f')
                    tRx_z = scanf.sscanf(line[ic[1]+1 : count], '%f')

        self.date = file.readline() # pas trop sur du resultat

        tline = file.readline()
        if isinstance(line, str):
            if 'NUMBER OF TRACES' not in line:
                self.ntrace = scanf.sscanf(tline,'%*20c %d')
            elif 'NUMBER OF PTS/TRC' not in line:
                self.nptsptrc = scanf.sscanf(tline,'%*20c %d')
            elif 'TOTAL TIME WINDOW' not in line:
                nttwin = scanf.sscanf(tline,'%*20c %f')
            elif 'STEP SIZE USED' not in line:
                self.rstepsz = scanf.sscanf(tline,'%*20c %f')
            elif 'POSITION UNITS' not in line:
                self.cunits = scanf.sscanf(tline,'%*20c %s')
            elif 'NOMINAL FREQUENCY' not in line:
                self.rnomfreq = scanf.sscanf(tline,'%*20c %f')
            elif 'ANTENNA SEPARATION' not in line:
                rantsep = scanf.sscanf(tline,'%*20c %f')
            elif 'SURVEY MODE' not in line:
                self.csurvmod = line[21:]
        file.close()
        self.timec = nttwin/self.nptsptrc
        self.timestp = self.timec








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

    def readSEGY(self, basename):
        """

        :param basename:
        :return:
        """







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
        file = open(basename, 'r')





    def readRD3(self, basename):
        """
        load content of *.rd3 extension
        fact: RD3 stands for Ray Dream Designer 3 graphics
        """
    def readTLF(self, basename):
        """
        load content of *.TLF extension
        """
    def readEKKO(self, basename):
        """
    """

    def readHD(self, basename):
        """

        :param basename:
        :return:
        """

    def readDT1(self, basename):
        """

        :param basename:
        :return:
        """

    def readSEGY(self, basename):
        """

        :param basename:
        :return:
        """






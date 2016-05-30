import sys
from PyQt4 import QtGui, QtCore
from BoreholeUI import BoreholeUI
from ModelUI import ModelUI
from MogUI import MOGUI
from InfoUI import InfoUI
from MogData import MogData
import time

class DatabaseUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(DatabaseUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Database")
        #--- Other Modules Instance ---#
        self.actual_time = time.asctime()[11:16]
        self.bh = BoreholeUI()
        self.model = ModelUI()
        self.mog = MOGUI()
        self.info = InfoUI()
        self.mogdata = MogData()
        self.initUI()
        self.action_list = []

        # DatabaseUI receives the signals, which were emitted by different modules, and transmits the signal to the other
        # modules in order to update them

        self.bh.bhUpdateSignal.connect(self.update_MogUI)
        self.bh.bhInfoSignal.connect(self.update_borehole_info)
        self.mog.mogInfoSignal.connect(self.update_mog_info)
        self.mog.ntraceSignal.connect(self.update_trace_info)
        self.mog.databaseSignal.connect(self.update_database_info)
        self.model.modelInfoSignal.connect(self.update_model_info)
        self.bh.bhlogSignal.connect(self.update_log)
        self.mog.moglogSignal.connect(self.update_log)



    def update_spectra(self, Tx_list):
        self.mog.update_spectra_Tx_num_combo(Tx_list)
        self.mog.update_spectra_Tx_elev_value_label(Tx_list)


    def update_MogUI(self, list_bh):
        self.mog.update_Tx_and_Rx_Widget(list_bh)

    def update_database_info(self, name):
        self.info.update_database(name)

    def update_borehole_info(self, num):
        self.info.update_borehole(num)

    def update_mog_info(self, num):
        self.info.update_mog(num)

    def update_model_info(self, num):
        self.info.update_model(num)

    def update_trace_info(self, num):
        self.info.update_trace(num)

    def update_log(self, action):
        red_palette = QtGui.QPalette()
        red_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)


        self.log.clear()
        self.action_list.append("[{}] {} " .format(self.actual_time, action))
        log_list = []
        for action in self.action_list:
            log_list.insert(0, action)
        for item in log_list:
            #TODO régler le fait que meme si c'est aps une erreur, le message s'affiche en rouge
            if "Error: " in item:
                self.log.setPalette(red_palette)
                self.log.append(item)
            else:
                self.log.append(item)




    def initUI(self):

        white_palette = QtGui.QPalette()
        white_palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)

        #--- Log Widget ---#
        self.log = QtGui.QTextEdit()
        self.log.setReadOnly(True)

        #--- Menubar ---#
        self.tool = QtGui.QMenuBar()
        self.tool.addAction('Open')
        self.tool.addAction('Save')
        self.tool.addAction('Save as')


        #--- GroupBoxes ---#
        #- Boreholes GroupBox -#
        bh_GroupBox =  QtGui.QGroupBox("Boreholes")
        bh_Sub_Grid   = QtGui.QGridLayout()
        bh_Sub_Grid.addWidget(self.bh)
        bh_GroupBox.setLayout(bh_Sub_Grid)

        #- MOGs GroupBox -#
        MOGs_GroupBox =  QtGui.QGroupBox("MOGs")
        MOGs_Sub_Grid   = QtGui.QGridLayout()
        MOGs_Sub_Grid.addWidget(self.mog)
        MOGs_GroupBox.setLayout(MOGs_Sub_Grid)

        #- Models GroupBox -#
        Models_GroupBox =  QtGui.QGroupBox("Models")
        Models_Sub_Grid   = QtGui.QGridLayout()
        Models_Sub_Grid.addWidget(self.model)
        Models_GroupBox.setLayout(Models_Sub_Grid)

        #- Info GroupBox -#
        Info_GroupBox =  QtGui.QGroupBox("Infos")
        Info_Sub_Grid   = QtGui.QGridLayout()
        Info_Sub_Grid.addWidget(self.info)
        Info_GroupBox.setLayout(Info_Sub_Grid)


        #--- Grid ---#
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(self.tool, 0, 0, 1, 3)
        master_grid.addWidget(bh_GroupBox, 1, 0)
        master_grid.addWidget(MOGs_GroupBox, 1, 1, 1, 2)
        master_grid.addWidget(Models_GroupBox, 2, 0, 1, 2)
        master_grid.addWidget(Info_GroupBox, 2, 2)
        master_grid.addWidget(self.log, 3, 0, 2, 3)
        master_grid.setVerticalSpacing(3)
        master_grid.setContentsMargins(2, 2, 2, 2)
        self.setLayout(master_grid)




if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Database_ui = DatabaseUI()


    Database_ui.show()


    sys.exit(app.exec_())
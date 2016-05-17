import sys
from PyQt4 import QtGui, QtCore
import matplotlib as mpl

class InterpretationUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(InterpretationUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Inversion")
        self.initUI()

    def initUI(self):
        #--- Color for the labels ---#
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)

        #--- Class For Alignment ---#
        class  MyQLabel(QtGui.QLabel):
            def __init__(self, label, ha='left',  parent=None):
                super(MyQLabel, self).__init__(label,parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)

        #------- Widgets Creation -------#

        #--- Label ---#
        Min_labeli = MyQLabel("Min :", ha= 'right')
        Max_labeli = MyQLabel("Max :", ha='right')
        slow_label = QtGui.QLabel("Slowness")
        atten_label = QtGui.QLabel("Attentuation")
        type_label = QtGui.QLabel("Type")
        freq_label = MyQLabel("Frequency[MHz]", ha= 'right')


        #--- Edits ---#
        Min_editi = QtGui.QLineEdit()
        Max_editi = QtGui.QLineEdit()
        freq_edit = QtGui.QLineEdit("100")

        #--- Checkbox ---#
        set_color_checkbox = QtGui.QCheckBox("Set Color Limits")

        #--- Text Edits ---#
        futur_Graph1 = QtGui.QTextEdit()
        futur_Graph1.setReadOnly(True)

        #--- combobox ---#
        slow_combo = QtGui.QComboBox()
        atten_combo = QtGui.QComboBox()
        type_combo = QtGui.QComboBox()
        phys_combo = QtGui.QComboBox()
        petro_combo = QtGui.QComboBox()
        fig_combo = QtGui.QComboBox()




        #--- Elements in the comboboxes ---#
        type_combo.addItem("Cokriging")
        type_combo.addItem("Cosimulation")

        phys_combo.addItem("Velocity")
        phys_combo.addItem("Slowness")
        phys_combo.addItem("Attenuation {}".format("alpha"))
        phys_combo.addItem("Volumetric Water Content {}".format("theta"))
        phys_combo.addItem("Dielectric Permittivity {}".format("epsilon"))
        phys_combo.addItem("Dielectric constant {}".format("kappa"))
        phys_combo.addItem("Electric conductivity {}".format("sigma"))
        phys_combo.addItem("Electric resistivity {}".format("ro"))
        phys_combo.addItem("VLoss tangent {}".format("delta"))

        petro_combo.addItem("Topp")
        petro_combo.addItem("CRIM")
        petro_combo.addItem("Hanai-Brugemann")

        fig_combo.addItem("cmr")
        fig_combo.addItem("polarmap")
        fig_combo.addItem("parula")
        fig_combo.addItem("jet")
        fig_combo.addItem("hsv")
        fig_combo.addItem("hot")
        fig_combo.addItem("cool")
        fig_combo.addItem("autumn")
        fig_combo.addItem("spring")
        fig_combo.addItem("winter")
        fig_combo.addItem("summer")
        fig_combo.addItem("gray")
        fig_combo.addItem("bone")
        fig_combo.addItem("copper")
        fig_combo.addItem("pink")
        fig_combo.addItem("prism")
        fig_combo.addItem("flag")
        fig_combo.addItem("colorcube")
        fig_combo.addItem("lines")

        #------- Groupboxes -------#
        #--- Tomograms Groupbox ---#
        Tomo_groupbox = QtGui.QGroupBox("Tomograms")
        Tomo_grid = QtGui.QGridLayout()
        Tomo_grid.addWidget(slow_label, 0, 0)
        Tomo_grid.addWidget(slow_combo, 1, 0, 1, 2)
        Tomo_grid.addWidget(atten_label, 2, 0)
        Tomo_grid.addWidget(atten_combo, 3, 0, 1, 2)
        Tomo_grid.addWidget(type_label, 4, 0)
        Tomo_grid.addWidget(type_combo, 5, 0, 1, 2)
        Tomo_groupbox.setLayout(Tomo_grid)
        #--- Physical Property Groupbox ---#
        Phys_groupbox = QtGui.QGroupBox("Physical Property")
        Phys_grid = QtGui.QGridLayout()
        Phys_grid.addWidget(phys_combo, 0, 0, 1, 2)
        Phys_grid.addWidget(freq_label, 1, 0)
        Phys_grid.addWidget(freq_edit, 1, 1)
        Phys_groupbox.setLayout(Phys_grid)

        #--- Petrophysical Model Groupbox ---#
        Petro_groupbox = QtGui.QGroupBox("Parameters")
        Petro_grid = QtGui.QGridLayout()
        Petro_grid.addWidget(petro_combo, 0, 0)
        Petro_groupbox.setLayout(Petro_grid)

        #--- Figures Groupbox ---#
        fig_groupbox = QtGui.QGroupBox("Figures")
        fig_grid = QtGui.QGridLayout()
        fig_grid.addWidget(set_color_checkbox, 0, 0)
        fig_grid.addWidget(Min_labeli, 0, 1)
        fig_grid.addWidget(Min_editi, 0, 2)
        fig_grid.addWidget(Max_labeli, 0, 3)
        fig_grid.addWidget(Max_editi, 0, 4)
        fig_grid.addWidget(fig_combo, 0, 5)
        fig_groupbox.setLayout(fig_grid)

        #------- Master Grid Disposition -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(Tomo_groupbox, 0, 0)
        master_grid.addWidget(Phys_groupbox, 1, 0)
        master_grid.addWidget(Petro_groupbox, 2, 0)
        master_grid.addWidget(fig_groupbox, 0, 1)
        master_grid.addWidget(futur_Graph1, 1, 1, 3, 5)
        self.setLayout(master_grid)
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = InterpretationUI()
    Model_ui.show()

    sys.exit(app.exec_())

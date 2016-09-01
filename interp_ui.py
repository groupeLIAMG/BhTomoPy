# -*- coding: utf-8 -*-
"""

Copyright 2016 Bernard Giroux, Elie Dumas-Lefebvre

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
import sys
from PyQt4 import QtGui, QtCore
import matplotlib as mpl
from unicodedata import *

class InterpretationUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(InterpretationUI, self).__init__()
        self.setWindowTitle("BhTomoPy/Inversion")
        self.initUI()

    def initUI(self):

        #--- Importation of the greek letters ---#
        char1 = lookup("GREEK SMALL LETTER ALPHA")
        char2 = lookup("GREEK SMALL LETTER THETA")
        char3 = lookup("GREEK SMALL LETTER EPSILON")
        char4 = lookup("GREEK SMALL LETTER KAPPA")
        char5 = lookup("GREEK SMALL LETTER SIGMA")
        char6 = lookup("GREEK SMALL LETTER RHO")
        char7 = lookup("GREEK SMALL LETTER DELTA")

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
        Min_labeli             = MyQLabel("Min :", ha= 'right')
        Max_labeli             = MyQLabel("Max :", ha='right')
        slow_label             = QtGui.QLabel("Slowness")
        atten_label            = QtGui.QLabel("Attentuation")
        type_label             = QtGui.QLabel("Type")
        freq_label             = MyQLabel("Frequency[MHz]", ha= 'right')

        #--- Edits ---#
        Min_editi              = QtGui.QLineEdit()
        Max_editi              = QtGui.QLineEdit()
        freq_edit              = QtGui.QLineEdit("100")

        #--- Checkbox ---#
        set_color_checkbox     = QtGui.QCheckBox("Set Color Limits")

        #--- Text Edits ---#
        futur_Graph1           = QtGui.QTextEdit()
        futur_Graph1.setReadOnly(True)

        #--- combobox ---#
        slow_combo             = QtGui.QComboBox()
        atten_combo            = QtGui.QComboBox()
        type_combo             = QtGui.QComboBox()
        phys_combo             = QtGui.QComboBox()
        petro_combo            = QtGui.QComboBox()
        fig_combo              = QtGui.QComboBox()


        #--- Items in the comboboxes ---#
        #--- Type Combobox's Items ---#
        type_combo.addItem("Cokriging")
        type_combo.addItem("Cosimulation")

        #--- Physical Property Combobox's Items ---#
        phys_combo.addItem("Velocity")
        phys_combo.addItem("Slowness")
        phys_combo.addItem("Attenuation {}".format(char1))
        phys_combo.addItem("Volumetric Water Content {}".format(char2))
        phys_combo.addItem("Dielectric Permittivity {}".format(char3))
        phys_combo.addItem("Dielectric constant {}".format(char4))
        phys_combo.addItem("Electric conductivity {}".format(char5))
        phys_combo.addItem("Electric resistivity {}".format(char6))
        phys_combo.addItem("VLoss tangent {}".format(char7))

        #--- Petrophysical Combobox's Items ---#
        petro_combo.addItem("Topp")
        petro_combo.addItem("CRIM")
        petro_combo.addItem("Hanai-Brugemann")

        #--- Figure Combobox's Items ---#
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
        Tomo_groupbox  = QtGui.QGroupBox("Tomograms")
        Tomo_grid      = QtGui.QGridLayout()
        Tomo_grid.addWidget(slow_label, 0, 0)
        Tomo_grid.addWidget(slow_combo, 1, 0, 1, 2)
        Tomo_grid.addWidget(atten_label, 2, 0)
        Tomo_grid.addWidget(atten_combo, 3, 0, 1, 2)
        Tomo_grid.addWidget(type_label, 4, 0)
        Tomo_grid.addWidget(type_combo, 5, 0, 1, 2)
        Tomo_groupbox.setLayout(Tomo_grid)

        #--- Physical Property Groupbox ---#
        Phys_groupbox  = QtGui.QGroupBox("Physical Property")
        Phys_grid      = QtGui.QGridLayout()
        Phys_grid.addWidget(phys_combo, 0, 0, 1, 2)
        Phys_grid.addWidget(freq_label, 1, 0)
        Phys_grid.addWidget(freq_edit, 1, 1)
        Phys_groupbox.setLayout(Phys_grid)

        #--- Petrophysical Model Groupbox ---#
        Petro_groupbox = QtGui.QGroupBox("Parameters")
        Petro_grid     = QtGui.QGridLayout()
        Petro_grid.addWidget(petro_combo, 0, 0)
        Petro_groupbox.setLayout(Petro_grid)

        #--- Figures Groupbox ---#
        fig_groupbox  = QtGui.QGroupBox("Figures")
        fig_grid      = QtGui.QGridLayout()
        fig_grid.addWidget(set_color_checkbox, 0, 0)
        fig_grid.addWidget(Min_labeli, 0, 1)
        fig_grid.addWidget(Min_editi, 0, 2)
        fig_grid.addWidget(Max_labeli, 0, 3)
        fig_grid.addWidget(Max_editi, 0, 4)
        fig_grid.addWidget(fig_combo, 0, 5)
        fig_grid.setColumnStretch(6, 100)
        fig_groupbox.setLayout(fig_grid)


        #------- Sub Widgets -------#
        #--- Right Part SubWidget ---#
        # The Right part SubWidget is created in order to have a more uniform disposition of the Figure Groupbox
        Sub_right_Widget = QtGui.QWidget()
        Sub_right_Grid = QtGui.QGridLayout()
        Sub_right_Grid.addWidget(fig_groupbox, 0, 0)
        Sub_right_Grid.setContentsMargins(0, 0, 0, 0)
        Sub_right_Widget.setLayout(Sub_right_Grid)

        #------- Master Grid Disposition -------#
        master_grid = QtGui.QGridLayout()
        master_grid.addWidget(Tomo_groupbox, 0, 0, 3, 1)
        master_grid.addWidget(Phys_groupbox, 3, 0, 3, 1)
        master_grid.addWidget(Petro_groupbox, 6, 0)
        master_grid.addWidget(Sub_right_Widget, 0, 1)
        master_grid.addWidget(futur_Graph1, 1, 1, 7, 2)
        master_grid.setColumnStretch(2, 100)
        master_grid.setRowStretch(7, 100)
        self.setLayout(master_grid)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    Model_ui = InterpretationUI()
    Model_ui.show()

    sys.exit(app.exec_())

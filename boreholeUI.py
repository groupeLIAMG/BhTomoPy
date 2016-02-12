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

#---- STANDARD LIBRARY IMPORTS ----

import sys

#---- THIRD PARTY IMPORTS ----

from PySide import QtGui, QtCore

#---- PERSONAL IMPORTS ----

import borehole

class BoreholeUI(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(BoreholeUI, self).__init__(parent)
        
        self.bholes = [] # A list to hold all borehole instances
        self.isUserEvent = True # Flag to disable user generated events 
                                # when UI is being updated programmatically
        
        self.initUI()
        
    def initUI(self):
        
        #----------------------------------------------------------- Toolbar --
       
        #-- Widgets --
        
        # Create the child widgets that will be incorporated in the layout
        # of a subwidget that will be used as a toolbar for the main widget
        # created from class "BoreholeUI".
        
        btn_new = QtGui.QPushButton('Add')        
        btn_new.clicked.connect(self.add_new_bhole) # Connect a slot to signal
        
        self.bname_edit = QtGui.QLineEdit()
        
        btn_remove = QtGui.QPushButton('Remove')
        btn_remove.clicked.connect(self.remove_bhole)
        
        btn_import = QtGui.QPushButton('Import')
        btn_plot = QtGui.QPushButton('Plot')
        
        #-- Grid --
        
        # Create the toolbar subwidget and a grid layout 
        
        toolbar_grid = QtGui.QGridLayout()
        toolbar_widget = QtGui.QWidget()
        
        # Insert the child widgets previously created into the grid
        
        toolbar_grid.addWidget(btn_new, 0, 0)
        toolbar_grid.addWidget(self.bname_edit, 0, 1, 1, 3)
        toolbar_grid.addWidget(btn_remove, 1, 0)
        toolbar_grid.addWidget(btn_import, 1, 1)
        toolbar_grid.addWidget(btn_plot, 1, 2)
           
        # Define the grid layout properties
            
        toolbar_grid.setSpacing(5)
        toolbar_grid.setContentsMargins(0, 0, 0, 0) #(L, T, R, B)
        toolbar_grid.setColumnStretch(3, 100)
        
        # Assign layout to toolbar subwidget
        
        toolbar_widget.setLayout(toolbar_grid)
        
        #--------------------------------------------------------- List View --
        
        # Create a new widget where are going to be listed the borehole names
        
        self.bholeListWidg = QtGui.QListWidget()
        self.bholeListWidg.currentRowChanged.connect(self.sel_bhole_changed)                                                    
        
        #------------------------------------------------------- Coordinates --
        
        #-- Widgets --
        
        class  MyQLabel(QtGui.QLabel):
            def __init__(self, label, ha='left',  parent=None):
                super(MyQLabel, self).__init__(label,parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)
        
        class  MyQDSpinBox(QtGui.QDoubleSpinBox):
            def __init__(self, parent):
                super(MyQDSpinBox, self).__init__(parent)
                self.setDecimals(2)
                self.setSingleStep(1)
                self.setRange(-10000, 10000)
                self.setAlignment(QtCore.Qt.AlignCenter)
                self.valueChanged.connect(parent.bhole_info_changed)
                
        self.X = [MyQDSpinBox(self), MyQDSpinBox(self)]
        self.Y = [MyQDSpinBox(self), MyQDSpinBox(self)]
        self.Z = [MyQDSpinBox(self), MyQDSpinBox(self)]
        self.Zsurf = MyQDSpinBox(self)
        self.Zwater = MyQDSpinBox(self)
        self.Diam = MyQDSpinBox(self)
        
        #-- Layout --
        
        bhcoord_grid = QtGui.QGridLayout()
        self.bhcoord_widget = QtGui.QWidget()
        
        bhcoord_grid.addWidget(MyQLabel('Coordinates', ha='right'), 0, 0)
        bhcoord_grid.addWidget(MyQLabel('Collar', ha='center'), 0, 1)
        bhcoord_grid.addWidget(MyQLabel('Bottom', ha='center'), 0, 2)                       
        row = 1
        bhcoord_grid.addWidget(MyQLabel('X :', ha='right'), row, 0)
        bhcoord_grid.addWidget(self.X[0], row, 1)
        bhcoord_grid.addWidget(self.X[1], row, 2)
        row += 1
        bhcoord_grid.addWidget(MyQLabel('Y :', ha='right'), row, 0)
        bhcoord_grid.addWidget(self.Y[0], row, 1)
        bhcoord_grid.addWidget(self.Y[1], row, 2)
        row += 1
        bhcoord_grid.addWidget(MyQLabel('Elev. :', ha='right'), row, 0)
        bhcoord_grid.addWidget(self.Z[0], row, 1)
        bhcoord_grid.addWidget(self.Z[1], row, 2)
        row += 1
        bhcoord_grid.addWidget(MyQLabel('Elev. Surf. :', ha='center'), row, 0)
        bhcoord_grid.addWidget(MyQLabel('Elev. Water :', ha='center'), row, 1)
        bhcoord_grid.addWidget(MyQLabel('Diam. :', ha='center'), row, 2)
        row += 1
        bhcoord_grid.addWidget(self.Zsurf, row, 0)
        bhcoord_grid.addWidget(self.Zwater, row, 1)
        bhcoord_grid.addWidget(self.Diam, row, 2)
        
        bhcoord_grid.setHorizontalSpacing(15)
        bhcoord_grid.setVerticalSpacing(5)
        bhcoord_grid.setContentsMargins(0, 0, 0, 0) #(L, T, R, B)
        bhcoord_grid.setColumnStretch(3, 100)
        
        self.bhcoord_widget.setLayout(bhcoord_grid)
        
        #---------------------------------------------------- Toolbar Bottom --
        
        #-- Widgets --
        
        btn_ConSlo = QtGui.QPushButton('Constraints slo.')
        btn_ConAtt = QtGui.QPushButton('Constraints att.')
        
        #-- Layout --
        
        lowTbar_grid = QtGui.QGridLayout()
        lowTbar_widget = QtGui.QWidget()
        
        lowTbar_grid.addWidget(btn_ConSlo, 0, 0)
        lowTbar_grid.addWidget(btn_ConAtt, 0, 1)
            
        lowTbar_grid.setSpacing(5)
        lowTbar_grid.setContentsMargins(0, 0, 0, 0) #(L, T, R, B)
        
        lowTbar_widget.setLayout(lowTbar_grid)
        
        #------------------------------------------------------- Main Layout --
        
        # Insert the subwidgets (toolbar and list view) in the main layout and
        # assign it to the main widget
        
        main_grid = QtGui.QGridLayout()
        
        main_grid.addWidget(toolbar_widget, 0, 1)
        main_grid.addWidget(self.bholeListWidg, 1, 1)
        main_grid.addWidget(self.bhcoord_widget, 2, 1)
        main_grid.addWidget(lowTbar_widget, 3, 1)
        
        main_grid.setRowStretch(1, 100)
        main_grid.setColumnStretch(0, 100)
        main_grid.setColumnStretch(2, 100)
        main_grid.setVerticalSpacing(15)
        
        self.setLayout(main_grid)
        
    def add_new_bhole(self):
        
        # Add a new item to the ListView widget with a name corresponding to
        # what is written in the field "bname_edit" if it is not empty. A new
        # object related to the new borehole is also created and added to
        # a list.
        
        if self.bname_edit.text() != '':
            bname = self.bname_edit.text()
            self.bholeListWidg.insertItem(0, bname)             
            self.bholes.insert(0, borehole.Borehole(bname))
            self.bholeListWidg.setCurrentRow (0)
                        
    def remove_bhole(self):        
        # Remove the item currently selected in the list of boreholes
        bindx = self.bholeListWidg.currentRow()
        if bindx != -1:
            self.bholeListWidg.takeItem(bindx)
            del self.bholes[bindx]
        
    def bhole_info_changed(self):
        if self.bholeListWidg.currentRow() == -1:
            # The current list of borehole is empty.
            return
        if self.isUserEvent == False:
            # Prevent a circular logic because the UI is being updated
            # programmatically from the stored internal variables.
            return
        
        bhole = self.bholes[self.bholeListWidg.currentRow()]

        bhole.X = [self.X[0].value(), self.X[1].value()]
        bhole.Y = [self.Y[0].value(), self.Y[1].value()]
        bhole.Z = [self.Z[0].value(), self.Z[1].value()]
        bhole.Zsurf = self.Zsurf.value()
        bhole.Zwater = self.Zwater.value()
        bhole.Diam = self.Diam.value()
        
    def sel_bhole_changed(self, row):
        # Grab values from the UI and store the values into the class
        # instance related to the currently selected borehole in the list.
        self.isUserEvent = False
        bhole = self.bholes[row]
        for i in range(2):
            self.X[i].setValue(bhole.X[i])
            self.Y[i].setValue(bhole.Y[i])
            self.Z[i].setValue(bhole.Z[i])
        self.Zsurf.setValue(bhole.Zsurf)
        self.Zwater.setValue(bhole.Zwater)
        self.Diam.setValue(bhole.Diam)
        self.isUserEvent = True
        
                
if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    
    borehole_ui = BoreholeUI()
    borehole_ui.show()

    sys.exit(app.exec_())
    

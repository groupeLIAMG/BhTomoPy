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

class BoreholeUI(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(BoreholeUI, self).__init__(parent)
        
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
        toolbar_grid.addWidget(self.bname_edit, 0, 1, 1, 2)
        toolbar_grid.addWidget(btn_remove, 1, 0)
        toolbar_grid.addWidget(btn_import, 1, 1)
        toolbar_grid.addWidget(btn_plot, 1, 2)
           
        # Define the grid layout properties
            
        toolbar_grid.setSpacing(5)
        toolbar_grid.setContentsMargins(0, 0, 0, 0)
        toolbar_grid.setColumnStretch(3, 100)
        
        # Assign layout to toolbar subwidget
        
        toolbar_widget.setLayout(toolbar_grid)
        
        #--------------------------------------------------------- List View --
        
        # Create a new widget where are going to be listed the borehole names
        
        self.bhole_list = QtGui.QListWidget()
        
        #------------------------------------------------------- Main Layout --
        
        # Insert the subwidgets (toolbar and list view) in the main layout and
        # assign it to the main widget
        
        main_grid = QtGui.QGridLayout()        
        main_grid.addWidget(toolbar_widget, 0, 0)
        main_grid.addWidget(self.bhole_list, 1, 0)
        main_grid.setRowStretch(1, 100)
        self.setLayout(main_grid)
        
    def add_new_bhole(self):
        
        # Add a new item to the ListView widget with a name corresponding to
        # what is written in the field "bname_edit" if it is not empty.
        
        if self.bname_edit.text() != '':
            self.bhole_list.insertItem(0, self.bname_edit.text())
            
        
    def remove_bhole(self):
        
        # Remove the item currently selected in the list of boreholes
    
        self.bhole_list.takeItem(self.bhole_list.currentRow())
        
if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    
    borehole = BoreholeUI()
    borehole.show()

    sys.exit(app.exec_())
    

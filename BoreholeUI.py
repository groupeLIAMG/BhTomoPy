import sys
from PyQt4 import QtGui, QtCore
#from borehole import Borehole, BoreholeSetup, BoreholeFig

class BoreholeUI(QtGui.QFrame):
    def __init__(self, parent=None):
        super(BoreholeUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Borehole")
        self.initUI()

    def initUI(self):

    #------ Fig Plot -----#
        #self.bholeFig = BoreholeFig()


        class  MyQLabel(QtGui.QLabel):
            def __init__(self, label, ha='left',  parent=None):
                super(MyQLabel, self).__init__(label,parent)
                if ha == 'center':
                    self.setAlignment(QtCore.Qt.AlignCenter)
                elif ha == 'right':
                    self.setAlignment(QtCore.Qt.AlignRight)
                else:
                    self.setAlignment(QtCore.Qt.AlignLeft)

        #------- Widget Link -------#
        self.bh_Creation = BH_Creation()

        #------- Widget Creation -------#
        #--- Buttons Set---#
        btn_Add               = QtGui.QPushButton("Add")
        btn_Remove            = QtGui.QPushButton("Remove")
        btn_Import            = QtGui.QPushButton("Import")
        btn_Plot              = QtGui.QPushButton("Plot")
        btn_Constraints_veloc = QtGui.QPushButton("Constraints Veloc.")
        btn_Constraints_atten = QtGui.QPushButton("Constraints Atten.")

        #--- Buttons Actions ---#
        btn_Add.clicked.connect(self.bh_Creation.show)

        #--- Labels ---#
        Coord_label              = MyQLabel('Coordinates:', ha='center')
        Collar_label             = MyQLabel('Collar:', ha='center')
        Bottom_label             = MyQLabel('Bottom:', ha='center')
        X_label                  = MyQLabel('X:', ha='right')
        Y_label                  = MyQLabel('Y:', ha='right')
        Elev_label               = MyQLabel('Elevation:', ha='right')
        Elev_surf_label          = QtGui.QLabel("Elevation at surface:")
        Elev_water_label         = MyQLabel('water elevation:', ha='right')
        Diam_label               = MyQLabel('Diameter:', ha='right')

        #--- Edits ---#
        X_edit                   = QtGui.QLineEdit()
        Y_edit                   = QtGui.QLineEdit()
        Z_edit                   = QtGui.QLineEdit()
        Xmax_edit                = QtGui.QLineEdit()
        Ymax_edit                = QtGui.QLineEdit()
        Zmax_edit                = QtGui.QLineEdit()
        Z_surf_edit              = QtGui.QLineEdit()
        Z_water_edit             = QtGui.QLineEdit()
        Diam_edit                = QtGui.QLineEdit()

        #--- list ---#
        self.bh_list             = QtGui.QListWidget()

        #--- sub widgets ---#
        #--- Diam ---#
        sub_Diam_widget          = QtGui.QWidget()
        sub_Diam_Grid            = QtGui.QGridLayout()
        sub_Diam_Grid.addWidget(Diam_label, 0, 0)
        sub_Diam_Grid.addWidget(Diam_edit, 0, 1)
        sub_Diam_Grid.setContentsMargins(0, 0, 0, 0)
        sub_Diam_widget.setLayout(sub_Diam_Grid)

        #--- Upper Buttons ---#
        sub_upper_buttons_widget = QtGui.QWidget()
        sub_upper_buttons_Grid   = QtGui.QGridLayout()
        sub_upper_buttons_Grid.addWidget(btn_Add, 0, 0)
        sub_upper_buttons_Grid.addWidget(btn_Remove, 0, 1)
        sub_upper_buttons_Grid.addWidget(btn_Import, 0, 2)
        sub_upper_buttons_Grid.addWidget(btn_Plot, 0, 3)
        sub_upper_buttons_widget.setLayout(sub_upper_buttons_Grid)

        #------- Grid Disposition -------#
        master_grid     = QtGui.QGridLayout()

        #--- Buttons Disposition ---#
        master_grid.addWidget(sub_upper_buttons_widget, 0, 0, 1, 4)
        master_grid.addWidget(btn_Constraints_veloc, 9, 0, 1, 2)
        master_grid.addWidget(btn_Constraints_atten, 9, 2, 1, 2)

        #--- List Disposition ---#
        master_grid.addWidget(self.bh_list, 2, 0, 1, 4)

        #--- Labels Disposition ---#
        master_grid.addWidget(Coord_label, 3, 0)
        master_grid.addWidget(Collar_label, 3, 1)
        master_grid.addWidget(Bottom_label, 3, 2)
        master_grid.addWidget(X_label, 4, 0)
        master_grid.addWidget(Y_label, 5, 0)
        master_grid.addWidget(Elev_label, 6, 0)
        master_grid.addWidget(Elev_surf_label, 7, 0)
        master_grid.addWidget(Elev_water_label, 8, 0)

        #--- Edits Disposition ---#
        master_grid.addWidget(X_edit, 4, 1)
        master_grid.addWidget(Y_edit, 5, 1)
        master_grid.addWidget(Z_edit, 6, 1)
        master_grid.addWidget(Xmax_edit, 4, 2)
        master_grid.addWidget(Ymax_edit, 5, 2)
        master_grid.addWidget(Zmax_edit, 6, 2)
        master_grid.addWidget(Z_surf_edit, 7, 1)
        master_grid.addWidget(Z_water_edit, 8, 1)

        #--- Others ---#
        master_grid.addWidget(sub_Diam_widget, 8, 2)

        #------- Grid settings -------#
        master_grid.setColumnStretch(3, 100)
        master_grid.setRowStretch(2, 100)

        #------- set Layout -------#
        self.setLayout(master_grid)



class BH_Creation(QtGui.QWidget):
    def __init__(self, parent=None):
        super(BH_Creation, self).__init__()
        self.setWindowTitle("Borehole creation")
        self.setWindowFlags(QtCore.Qt.Window)
        self.initUI()

    #------- Widget Creation -------#
    def initUI(self):
        bh_edit               = QtGui.QLineEdit()
        btn_ok                = QtGui.QPushButton("Ok")

        #------- Grid Creation -------#

        creation_grid = QtGui.QGridLayout()
        creation_grid.addWidget(bh_edit, 0, 1)
        creation_grid.addWidget(btn_ok, 0, 2)
        self.setLayout(creation_grid)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    BoreholeUI_ui = BoreholeUI()
    BoreholeUI_ui.show()

    sys.exit(app.exec_())


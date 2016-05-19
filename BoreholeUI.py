import sys
from PyQt4 import QtGui, QtCore
from borehole import Borehole, BoreholeFig

class BoreholeUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(BoreholeUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Borehole")
        self.boreholes = []
        self.initUI()

    def add_bhole(self):
        name, ok = QtGui.QInputDialog.getText(self, "borehole creation", 'borehole name')
        if ok :
            self.boreholes.append(Borehole(str(name)))
            self.update_List_Widget()
            self.bh_list.setCurrentRow(len(self.boreholes) - 1)
            self.update_List_Edits()


    def update_List_Widget(self):
        self.bh_list.clear()
        for bh in self.boreholes:
            self.bh_list.addItem(bh.name)

    def update_List_Edits(self):
        ind = self.bh_list.selectedIndexes()
        for i in ind :
            bh = self.boreholes[i.row()]
            self.X_edit.setText(str(bh.X))
            self.Y_edit.setText(str(bh.Y))
            self.Z_edit.setText(str(bh.Z))
            self.Xmax_edit.setText(str(bh.Xmax))
            self.Ymax_edit.setText(str(bh.Ymax))
            self.Zmax_edit.setText(str(bh.Zmax))
            self.Z_surf_edit.setText(str(bh.Z_surf))
            self.Z_water_edit.setText(str(bh.Z_water))
            self.Diam_edit.setText(str(bh.diam))


    def del_bhole(self):
        ind = self.bh_list.selectedIndexes()
        for i in ind:
            del self.boreholes[int(i.row())]
        self.update_List_Widget()

    def update_bhole_data(self):
        ind = self.bh_list.selectedIndexes()
        for i in ind :
            bh         = self.boreholes[i.row()]
            bh.X       = float(self.X_edit.text())
            bh.Y       = float(self.Y_edit.text())
            bh.Z       = float(self.Z_edit.text())
            bh.Xmax    = float(self.Xmax_edit.text())
            bh.Ymax    = float(self.Ymax_edit.text())
            bh.Zmax    = float(self.Zmax_edit.text())
            bh.Z_surf  = float(self.Z_surf_edit.text())
            bh.Z_water = float(self.Z_water_edit.text())
            bh.diam    = float(self.Diam_edit.text())

    def initUI(self):

        #------ Fig Plot -----#
        self.bholeFig = BoreholeFig()

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

        #------- Widget Link -------#
        self.bh_Creation      = BH_Creation()
        self.bh_Removal       = BH_Removal()

        #------- Widget Creation -------#
        #--- Buttons Set---#
        btn_Add               = QtGui.QPushButton("Add")
        btn_Remove            = QtGui.QPushButton("Remove")
        btn_Import            = QtGui.QPushButton("Import")
        btn_Plot              = QtGui.QPushButton("Plot")
        btn_Constraints_veloc = QtGui.QPushButton("Constraints Veloc.")
        btn_Constraints_atten = QtGui.QPushButton("Constraints Atten.")

         #--- list ---#
        self.bh_list             = QtGui.QListWidget()

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
        self.X_edit                   = QtGui.QLineEdit()
        self.Y_edit                   = QtGui.QLineEdit()
        self.Z_edit                   = QtGui.QLineEdit()
        self.Xmax_edit                = QtGui.QLineEdit()
        self.Ymax_edit                = QtGui.QLineEdit()
        self.Zmax_edit                = QtGui.QLineEdit()
        self.Z_surf_edit              = QtGui.QLineEdit()
        self.Z_water_edit             = QtGui.QLineEdit()
        self.Diam_edit                = QtGui.QLineEdit()

        #--- List Actions ---#
        self.bh_list.itemSelectionChanged.connect(self.update_List_Edits)
        #--- Edits Actions ---#
        self.X_edit.editingFinished.connect(self.update_bhole_data)
        self.Y_edit.editingFinished.connect(self.update_bhole_data)
        self.Z_edit.editingFinished.connect(self.update_bhole_data)
        self.Xmax_edit.editingFinished.connect(self.update_bhole_data)
        self.Ymax_edit.editingFinished.connect(self.update_bhole_data)
        self.Zmax_edit.editingFinished.connect(self.update_bhole_data)
        self.Z_surf_edit.editingFinished.connect(self.update_bhole_data)
        self.Z_water_edit.editingFinished.connect(self.update_bhole_data)
        self.Diam_edit.editingFinished.connect(self.update_bhole_data)

        #--- Buttons Actions ---#
        btn_Add.clicked.connect(self.add_bhole)
        btn_Remove.clicked.connect(self.del_bhole)


        #--- sub widgets ---#
        #--- Diam ---#
        sub_Diam_widget          = QtGui.QWidget()
        sub_Diam_Grid            = QtGui.QGridLayout()
        sub_Diam_Grid.addWidget(Diam_label, 0, 0)
        sub_Diam_Grid.addWidget(self.Diam_edit, 0, 1)
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
        master_grid.addWidget(self.X_edit, 4, 1)
        master_grid.addWidget(self.Y_edit, 5, 1)
        master_grid.addWidget(self.Z_edit, 6, 1)
        master_grid.addWidget(self.Xmax_edit, 4, 2)
        master_grid.addWidget(self.Ymax_edit, 5, 2)
        master_grid.addWidget(self.Zmax_edit, 6, 2)
        master_grid.addWidget(self.Z_surf_edit, 7, 1)
        master_grid.addWidget(self.Z_water_edit, 8, 1)

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
        bh_label             = QtGui.QLabel("BH Name :")
        btn_ok                = QtGui.QPushButton("Ok")

        #------- Grid Creation -------#

        creation_grid = QtGui.QGridLayout()
        creation_grid.addWidget(bh_edit, 1, 0)
        creation_grid.addWidget(btn_ok, 1, 1)
        creation_grid.addWidget(bh_label, 0, 0)
        self.setLayout(creation_grid)


class BH_Removal(QtGui.QWidget):
    def __init__(self, parent=None):
        super(BH_Removal, self).__init__()
        self.setWindowTitle("BH Removal")
        self.setWindowFlags(QtCore.Qt.Window)
        self.initUI()

    #------- Widget Creation -------#
    def initUI(self):
        model_label             = QtGui.QLabel("BH Name :")
        model_edit               = QtGui.QLineEdit()
        btn_ok                = QtGui.QPushButton("Ok")
        #------- Grid Creation -------#

        creation_grid = QtGui.QGridLayout()
        creation_grid.addWidget(model_label,0, 0 )
        creation_grid.addWidget(model_edit, 1, 0)
        creation_grid.addWidget(btn_ok, 1, 1)
        self.setLayout(creation_grid)


if __name__ == '__main__':


    app = QtGui.QApplication(sys.argv)

    BoreholeUI_ui = BoreholeUI()
    BoreholeUI_ui.show()

    sys.exit(app.exec_())


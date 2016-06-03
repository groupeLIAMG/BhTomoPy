import sys
from PyQt4 import QtGui, QtCore
from borehole import Borehole
from database import Database
import numpy as np
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import axes3d
import time

class BoreholeUI(QtGui.QWidget):

    #------- Signals -------#
    bhlogSignal = QtCore.pyqtSignal(str)
    bhUpdateSignal = QtCore.pyqtSignal(list)  # this signal sends the informaion to update the Tx and Rx comboboxes in MogUI
    bhInfoSignal = QtCore.pyqtSignal(int)     #this signal sends the information to update the number of borholes in infoUI


    def __init__(self, parent=None):
        super(BoreholeUI, self).__init__()
        self.setWindowTitle("bh_thomoPy/Borehole")
        self.boreholes = []   # we initialize a list which will contain instances of Borehole class
        self.db = Database()
        self.initUI()
        self.actual_time = time.asctime()[11:16]


    def import_bhole(self):
        """
        This method opens a QFileDialog, takes the name that the user as selected, updates the borehole's informations
        and then shows its name in the bh_list

        """
        filename              = QtGui.QFileDialog.getOpenFileName(self, 'Import Borehole')
        if filename:
            rname             = filename.split('/')
            rname             = rname[-1]
            rname             = rname.strip('.xyz')
            bh                = Borehole(str(rname))
            bh.fdata          = np.loadtxt(filename)
            bh.X              = bh.fdata[0,0]
            bh.Y              = bh.fdata[0,1]
            bh.Z              = bh.fdata[0,2]
            bh.Xmax           = bh.fdata[-1,0]
            bh.Ymax           = bh.fdata[-1,1]
            bh.Zmax           = bh.fdata[-1,2]
            self.boreholes.append(bh)
            self.update_List_Widget()
            self.bh_list.setCurrentRow(len(self.boreholes) - 1)
            self.update_List_Edits()
            self.bhlogSignal.emit("{}.xyz as been loaded succesfully".format(rname))



    def add_bhole(self):
        """
        This method will create an instance of the Borehole class and initialize it, while showing the value of all its
        attributes in the coordinates edits
        """
        name, ok = QtGui.QInputDialog.getText(self, "Borehole creation", "Borehole's name")
        if ok :
            self.boreholes.append(Borehole(str(name)))
            self.update_List_Widget()
            self.bh_list.setCurrentRow(len(self.boreholes) - 1)
            self.update_List_Edits()
            self.bhlogSignal.emit("{} borehole as been added sucesfully".format(name))


    def update_List_Widget(self):
        """
        Updates the information in the bh_list, then emits the instances contained in boreholes and the
        lenght of bh_list to DatabaseUI
        """
        self.bh_list.clear()
        for bh in self.boreholes:
            self.bh_list.addItem(bh.name)
        self.bhInfoSignal.emit(len(self.bh_list))
        self.bhUpdateSignal.emit(self.boreholes)


    def update_List_Edits(self):
        """
        Updates the coordinates edits information with the attributes of the Borehole class instance
        """
        ind = self.bh_list.selectedIndexes()
        for i in ind:
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
        """
        Deletes a borehole instance from boreholes
        """
        ind = self.bh_list.selectedIndexes()
        for i in ind:
            self.bhlogSignal.emit("{} as been deleted".format(self.boreholes[i].name))
            del self.boreholes[int(i.row())]

        self.update_List_Widget()


    def update_bhole_data(self):
        """
        Updates the borehole's attributes by getting the text in the coordinates edits
        """
        ind = self.bh_list.selectedIndexes()
        for i in ind:
            bh                = self.boreholes[i.row()]
            bh.X              = float(self.X_edit.text())
            bh.Y              = float(self.Y_edit.text())
            bh.Z              = float(self.Z_edit.text())
            bh.Xmax           = float(self.Xmax_edit.text())
            bh.Ymax           = float(self.Ymax_edit.text())
            bh.Zmax           = float(self.Zmax_edit.text())
            bh.Z_surf         = float(self.Z_surf_edit.text())
            bh.Z_water        = float(self.Z_water_edit.text())
            bh.diam           = float(self.Diam_edit.text())
            bh.fdata[0,0]     = bh.X
            bh.fdata[0,1]     = bh.Y
            bh.fdata[0,2]     = bh.Z
            bh.fdata[-1,0]    = bh.Xmax
            bh.fdata[-1,1]    = bh.Ymax
            bh.fdata[-1,2]    = bh.Zmax


    def plot(self):
        """
        Plots the all the Borehole instance in boreholes
        """
        self.bholeFig = BoreholeFig()
        self.bholeFig.plot_bholes(self.boreholes)

        for bh in self.boreholes:
            self.bhlogSignal.emit("{} have been plotted".format(bh.name))
        self.bholeFig.show()


    def attenuation_constraints(self):
        """
        Knowing the values of attenuation depending on elevation, we can define the attenuation on the borehole's trajectory
        with the project method and then associate an exactitude value (covariance) to each of them if it is given in the *.con file.
        We then associate the Cont instance to the borehole's acont attribute
        """
        ind = self.bh_list.selectedIndexes()
        acont = Cont()
        for i in ind:
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
            rname = filename.split('/')
            rname = rname[-1]
            rname = rname[:-4]
            if ".con" in filename:
                bh = self.boreholes[i.row()]
                cont = np.loadtxt(filename)

                acont.x, acont.y, acont.z, c = bh.project(bh.fdata, cont[:, 0])

                acont.x = acont.x.flatten()
                acont.y = acont.y.flatten()
                acont.z = acont.z.flatten()
                acont.valeur = cont[:, 1]

                if  np.size(cont, axis= 1) == 3:
                     acont.variance = cont[:,2]
                else:
                    acont.variance = np.zeros(len(cont[:,1]))

                bh.acont = acont
                self.bhlogSignal.emit("{} Attenuation Constraints have been applied to Borehole {} ".format(rname, bh.name))
            else:
                self.bhlogSignal.emit("Error: the file's extension must be *.con")
                break


    def slowness_constraints(self):
        """
        Practically the same method as attenuation_constraints but reversed
        """
        ind = self.bh_list.selectedIndexes()
        scont = Cont()
        for i in ind:
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
            if ".con" in filename:
                bh = self.boreholes[i.row()]
                cont = np.loadtxt(filename)

                scont.x, scont.y, scont.z, c = bh.project(bh.fdata, cont[:, 0])

                scont.x = scont.x.flatten()
                scont.y = scont.y.flatten()
                scont.z = scont.z.flatten()
                scont.valeur = 1/cont[:, 1]

                if  np.size(cont, axis= 1) == 3:
                    # inversion of a random variable http://math.stackexchange.com/questions/269216/inverse-of-random-variable
                     scont.variance = cont[:,2]/(cont[:,1]**4)
                else:
                    scont.variance = np.zeros(len(cont[:,1]))

                bh.scont = scont

            else:
                self.bhlogSignal.emit("Error: the file's extension must be *.con")
                break

    def initUI(self):

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


        #------- Widget Creation -------#
        #--- Buttons Set---#
        btn_Add                  = QtGui.QPushButton("Add")
        btn_Remove               = QtGui.QPushButton("Remove")
        btn_Import               = QtGui.QPushButton("Import")
        btn_Plot                 = QtGui.QPushButton("Plot")
        btn_Constraints_veloc    = QtGui.QPushButton("Constraints Veloc.")
        btn_Constraints_atten    = QtGui.QPushButton("Constraints Atten.")

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
        self.X_edit              = QtGui.QLineEdit()
        self.Y_edit              = QtGui.QLineEdit()
        self.Z_edit              = QtGui.QLineEdit()
        self.Xmax_edit           = QtGui.QLineEdit()
        self.Ymax_edit           = QtGui.QLineEdit()
        self.Zmax_edit           = QtGui.QLineEdit()
        self.Z_surf_edit         = QtGui.QLineEdit()
        self.Z_water_edit        = QtGui.QLineEdit()
        self.Diam_edit           = QtGui.QLineEdit()

        #--- Edits Settings ---#

        self.Diam_edit.setFixedSize(90, 20)

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
        btn_Import.clicked.connect(self.import_bhole)
        btn_Plot.clicked.connect(self.plot)
        btn_Constraints_atten.clicked.connect(self.attenuation_constraints)
        btn_Constraints_veloc.clicked.connect(self.slowness_constraints)

        #--- sub widgets ---#
        #--- Diam ---#
        sub_Diam_widget          = QtGui.QWidget()
        sub_Diam_Grid            = QtGui.QGridLayout()
        sub_Diam_Grid.addWidget(Diam_label, 0, 0)
        sub_Diam_Grid.addWidget(self.Diam_edit, 0, 1)
        sub_Diam_Grid.setContentsMargins(0, 0, 0, 0)
        sub_Diam_Grid.setAlignment(QtCore.Qt.AlignLeft)
        sub_Diam_widget.setLayout(sub_Diam_Grid)

        #--- Edits and Labels SubWidget ---#
        sub_E_and_L_widget          = QtGui.QWidget()
        sub_E_and_L_grid            = QtGui.QGridLayout()
        sub_E_and_L_grid.addWidget(Coord_label, 0, 0)
        sub_E_and_L_grid.addWidget(Collar_label, 0, 1)
        sub_E_and_L_grid.addWidget(Bottom_label, 0, 2)
        sub_E_and_L_grid.addWidget(X_label, 1, 0)
        sub_E_and_L_grid.addWidget(self.X_edit, 1, 1)
        sub_E_and_L_grid.addWidget(self.Xmax_edit, 1, 2)
        sub_E_and_L_grid.addWidget(Y_label, 2, 0)
        sub_E_and_L_grid.addWidget(self.Y_edit, 2, 1)
        sub_E_and_L_grid.addWidget(self.Ymax_edit, 2, 2)
        sub_E_and_L_grid.addWidget(Elev_label, 3, 0)
        sub_E_and_L_grid.addWidget(self.Z_edit, 3, 1)
        sub_E_and_L_grid.addWidget(self.Zmax_edit, 3, 2)
        sub_E_and_L_grid.addWidget(Elev_surf_label, 4, 0)
        sub_E_and_L_grid.addWidget(self.Z_surf_edit, 4, 1)
        sub_E_and_L_grid.addWidget(Elev_water_label, 5, 0)
        sub_E_and_L_grid.addWidget(self.Z_water_edit, 5, 1)
        sub_E_and_L_widget.setLayout(sub_E_and_L_grid)

        #--- Upper Buttons ---#
        sub_upper_buttons_widget = QtGui.QWidget()
        sub_upper_buttons_Grid   = QtGui.QGridLayout()
        sub_upper_buttons_Grid.addWidget(btn_Add, 0, 0)
        sub_upper_buttons_Grid.addWidget(btn_Remove, 0, 1)
        sub_upper_buttons_Grid.addWidget(btn_Import, 0, 2)
        sub_upper_buttons_Grid.addWidget(btn_Plot, 0, 3)
        sub_upper_buttons_Grid.setContentsMargins(0, 0, 0, 0)
        sub_upper_buttons_widget.setLayout(sub_upper_buttons_Grid)

        #--- Lower Buttons ---#
        sub_lower_buttons_widget = QtGui.QWidget()
        sub_lower_buttons_Grid   = QtGui.QGridLayout()
        sub_lower_buttons_Grid.addWidget(btn_Constraints_veloc, 0, 0)
        sub_lower_buttons_Grid.addWidget(btn_Constraints_atten, 0, 1)
        sub_lower_buttons_Grid.setContentsMargins(0, 0, 0, 0)
        sub_lower_buttons_widget.setLayout(sub_lower_buttons_Grid)

        #------- Grid Disposition -------#
        master_grid     = QtGui.QGridLayout()
        master_grid.addWidget(sub_upper_buttons_widget, 0, 0)
        master_grid.addWidget(self.bh_list, 1, 0)
        master_grid.addWidget(sub_E_and_L_widget, 2, 0)
        master_grid.addWidget(sub_Diam_widget, 3, 0)
        master_grid.addWidget(sub_lower_buttons_widget, 4, 0)
        master_grid.setContentsMargins(0, 0, 0, 0)

        #------- set Layout -------#
        self.setLayout(master_grid)

class BoreholeFig(FigureCanvasQTAgg):


    def __init__(self):
        """
        Here we create a 3d figure in which we will plot the Borehole instances trajectory(i.e. their respective fdata)
        """

        fig_width, fig_height = 6, 8
        fig = mpl.figure.Figure(figsize=(fig_width, fig_height), facecolor='white')
        super(BoreholeFig, self).__init__(fig)
        self.initFig()


    def initFig(self):
        ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.9], projection='3d')
        ax.set_axisbelow(True)


    def plot_bholes(self, bhole_list):
        ax = self.figure.axes[0]
        ax.cla()
        for bhole in bhole_list:
            ax.plot(bhole.fdata[:,0] ,bhole.fdata[:,1],bhole.fdata[:, 2], label=bhole.name)

        l = ax.legend(ncol=1, bbox_to_anchor=(0, 1), loc='upper left',
                    borderpad=0)
        l.draw_frame(False)

        self.draw()

class Cont:
    """
    This class represents either the slowness constraints(i.e. bh.scont) or the attenuation constraints(i.e. bh.acont).
    We created a class for Cont because it as its own attributes.
    """
    def __init__(self):
        self.x = np.array([])
        self.y = np.array([])
        self.z = np.array([])
        self.valeur = np.array([])
        self.variance = np.array([])


if __name__ == '__main__':


    app = QtGui.QApplication(sys.argv)

    BoreholeUI_ui = BoreholeUI()
    BoreholeUI_ui.show()

    sys.exit(app.exec_())


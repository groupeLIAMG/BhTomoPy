import numpy as np
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


class Borehole:
    """
    Class to hold borehole data
    """
    def __init__(self, name=None,X = 0, Y = 0, Z = 0 , Xmax = 0, Ymax = 0, Zmax = 0, Z_surf = 0, Z_water = "" , diam =0, scont = np.array([]), acont = np.array([]), fdata = np.array([[0,0,0],[0,0,0,]]) ):
        self.name = name
        self.X = X
        self.Y = Y
        self.Z = Z
        self.Xmax = Xmax
        self.Ymax = Ymax
        self.Zmax = Zmax
        self.Z_surf = Z_surf
        self.Z_water = Z_water
        self.scont = scont
        self.acont = acont
        self.diam = diam
        self.fdata = fdata

    # Here we define all the attrbutes for the Broehole class

    def setname(self, name):
        try:
            if isinstance(name, str):
                self.name = name

        except:
            raise TypeError

    def setX(self, X):
        try:

            if isinstance(X, float or int):
                self.X = X
        except:
            raise TypeError

    def setY(self, Y):
        try:
            if isinstance(Y, float or int):
                self.Y = Y
        except:
            raise TypeError

    def setZ(self, Z):
        try:
            if isinstance(Z, float or int):
                self.Z = Z
        except:
            raise TypeError

    #TODO
    #def setXmax(self,Xmax):
    #ef setYmax(self,Ymax):
    #def setZmax(self,Zmax):
    #def setZ_surf(self,Xmax):
    #def setZ_water(self,Xmax):
    #def setdiam(self,Xmax):
    #def setfdata(self):












        
        

        
if __name__ == '__main__':
    
    bh = Borehole('B01' )
    bh.X = 3
    print(bh.X)
    

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
    def __init__(self, name=None,X = 0, Y = 0, Z = 0 , Xmax = 0, Ymax = 0, Zmax = 0, Z_surf = 0, Z_water = "" , diam =0, scont = np.array([]), acont = np.array([]), fdata = np.array([[0,0,0],[0,0,0]]) ):
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

    # Here we define all the attributes for the Borehole class
    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, name):
        try:
            if isinstance(name, str):
                self.__name = name
        except:
            raise TypeError

    @property
    def X(self):
        return self.__X
    @X.setter
    def X(self, X):
        try:
            if isinstance(X, float or int):
                self.__X = X
        except:
            raise TypeError

    @property
    def Y(self):
        return self.__Y
    @Y.setter
    def Y(self, Y):
        try:
            if isinstance(Y, float or int):
                self.__Y = Y
        except:
            raise TypeError

    @property
    def Z(self):
        return self.__Z
    @Z.setter
    def Z(self, Z):
        try:
            if isinstance(Z, float or int):
                self.__Z = Z
        except:
            raise TypeError

    @property
    def Xmax(self):
        return self.__Xmax
    @Xmax.setter
    def Xmax(self,Xmax):
        try:
            if isinstance(Xmax, float or int):
                self.__Xmax = Xmax
        except:
            raise TypeError

    @property
    def Ymax(self):
        return self.__Ymax
    @Ymax.setter
    def Ymax(self,Ymax):
        try:
            if isinstance(Ymax, float or int):
                self.__Ymax = Ymax
        except:
            raise TypeError

    @property
    def Zmax(self):
        return self.__Zmax
    @Zmax.setter
    def Zmax(self,Zmax):
        try:
            if isinstance(Zmax, float or int):
                self.__Zmax = Zmax
        except:
            raise TypeError

    @property
    def Z_surf(self):
        return self.__Z_surf
    @Z_surf.setter
    def Z_surf(self,Z_surf):
        try:
            if isinstance(Z_surf, float or int):
                self.__Z_surf = Z_surf
        except:
            raise TypeError

    @property
    def Z_water(self):
        return self.__Z_water
    @Z_water.setter
    def Z_water(self,Z_water):
        try:
            if isinstance(Z_water, float or int):
                self.__Z_water = Z_water
        except:
            raise TypeError

    @property
    def diam(self):
        return self.__diam
    @diam.setter
    def diam(self,diam):
        try:
            if isinstance(diam, float or int):
                self.__diam = diam
        except:
            raise TypeError

# As u see, we set the @property and @something.setter to be able the either get the information from one attribute of the Borehole class
# or to change its value while verifying if the new value respects the criteria to be valid simply by calling Borehole.something this
# will help one who wants to get acces to this data by shorting the syntax of the script

    @property
    def fdata(self):
        return self.__fdata
    @fdata.setter
    def fdata(self, fdata):
        try:
            l = fdata.shape
            if len(l) == 2:
                if l[1] == 3 :
                # We only verify the column index of the matrix to be sure the number of dimensions is 3
                # We don't need to verifiy the line index because only the dimensions are in need to be restrained
                    for element in fdata.flat:
                    # We use the .flat function to iterate over all of the elements of the fdata matrix
                        if isinstance(element, float or int):
                            self.__fdata = fdata
        except:
            raise TypeError

#def














        
        

        
if __name__ == '__main__':
    
    bh = Borehole('B01' )
    bh.X = 3
    print(bh.X)
    

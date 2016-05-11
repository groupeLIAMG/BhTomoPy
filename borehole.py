# -*- coding: utf-8 -*-
import numpy as np

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

    def __init__(self, name=None, X=0, Y=0, Z=0, Xmax=0, Ymax=0, Zmax=0, Z_surf=0, Z_water="", diam=0,
                 scont=np.array([]), acont=np.array([]), fdata=np.array([[0, 0, 0], [0, 0, 0]])):
        """Attributes:
        name: name of the borehole(BH)
        X, Y and Z: the BH's top cartesian coordinates
        Xmax, Ymax and Zmax : the BH's bottom cartesian coordinates
        Z_surf:
        Z_water: elevation of the water table
        diam: the BH's diameter
        scont:
        acont:
        fdata: the BH's trajectory's coordinates discrete evolution"""

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


    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if isinstance(name, str):
            self.__name = name
        else:
            raise TypeError

    @property
    def X(self):
        return self.__X

    @X.setter
    def X(self, X):
        if isinstance(X, float or int):
            self.__X = X
        else:
            raise TypeError

    @property
    def Y(self):
        return self.__Y

    @Y.setter
    def Y(self, Y):
        if isinstance(Y, float or int):
            self.__Y = Y
        else:
            raise TypeError

    @property
    def Z(self):
        return self.__Z

    @Z.setter
    def Z(self, Z):
        if isinstance(Z, float or int):
            self.__Z = Z
        else:
            raise TypeError

    @property
    def Xmax(self):
        return self.__Xmax

    @Xmax.setter
    def Xmax(self, Xmax):
        if isinstance(Xmax, float or int):
            self.__Xmax = Xmax
        else:
            raise TypeError

    @property
    def Ymax(self):
        return self.__Ymax

    @Ymax.setter
    def Ymax(self, Ymax):
        if isinstance(Ymax, float or int):
            self.__Ymax = Ymax
        else:
            raise TypeError

    @property
    def Zmax(self):
        return self.__Zmax

    @Zmax.setter
    def Zmax(self, Zmax):
        if isinstance(Zmax, float or int):
            self.__Zmax = Zmax
        else:
            raise TypeError

    @property
    def Z_surf(self):
        return self.__Z_surf

    @Z_surf.setter
    def Z_surf(self, Z_surf):
        if isinstance(Z_surf, float or int):
            self.__Z_surf = Z_surf
        else:
            raise TypeError

    @property
    def Z_water(self):
        return self.__Z_water

    @Z_water.setter
    def Z_water(self, Z_water):
        if isinstance(Z_water, float or int):
            self.__Z_water = Z_water
        else:
            raise TypeError

    @property
    def diam(self):
        return self.__diam

    @diam.setter
    def diam(self, diam):
        if isinstance(diam, float or int):
            self.__diam = diam
        else:
            raise TypeError

        # As you see, we set the @property and @something.setter to be able the either get the information from one attribute of the Borehole class
        # or to change its value while verifying if the new value respects the criteria to be valid simply by calling Borehole.something. This
        # will help one who wants to get access to this data, by shorting the syntax of the script

    @property
    def fdata(self):
        return self.__fdata

    @fdata.setter
    def fdata(self, fdata):
        l = fdata.shape
        if len(l) == 2:
            if l[1] == 3:
            # We only verify the column index of the matrix to be sure the number of dimensions is 3
            # We don't need to verifiy the line index because only the physical dimensions are in need to be restrained
            # not the lenght of the trajectory
                if isinstance(fdata, np.array):
                    self.__fdata = fdata
        else:
            raise TypeError

    @staticmethod
    def project(fdata, ldepth):
        """Project measurement points on borehole trajectory

        Attributes:

        fdata: matrix(n, 3) where the 3 columns represent the x, y and z coordinates
        of the BH's trajectory for a single n value.
        The n are sorted in growing order, from the top to the bottom of the borehole.

        ldepth: vector(1,m) which reprensents the position of the m measurement points (from top to bottom)

        Note: the discrete points of the BH's trajectory are not the same as the discrete points of the ldepth
                that's why we do this function; to determine the projection of the ldepth point on the fdata trajectory.

        name: name of the borehole

        x: x coordinates of all measurement points
        y: y coordinates of all measurement points
        z: z coordinates of all measurement points
        c: direction of cosines at measurements points which point downwards
        """

        npts = ldepth.size
        # the x,y and z coordinates are initially a matrix which contains as much 0 as the number of measurement points
        # we can see the c value as the combination of the three cartesian coordinates in unitary form
        x = np.zeros((1, npts))
        y = np.zeros((1, npts))
        z = np.zeros((1, npts))
        c = np.zeros((npts, 3))
    #TODO:
    #voir la sytaxe pour depthBH afin de vor si le résultat obtenu correspond à celui de la version mathlab.
        depthBH = np.cumsum(np.sqrt(np.sum(np.diff(fdata, n=1, axis=0) ** 2, axis=1)))


        #Knowing that de BH's depth is a matrix which contains the distance between every points of fdata, and that ldepth
        # contains the points where the data was taken,we need to first make sure that every points taken in charge by ldepth is in the range of the BH's depth.
        # As a matter of fact, we verify if each points of ldepth is contained in between the volume(i.e. between X and Xmax and the same for Y and Z)
        # If so, we take the closest point under our point of interest(i.e. i2[0]) and the closest point above our point of interest (i.e. i1[-1])
        # So you can anticipate that these points will change for every index of the ldepth vector.


        for n in range(npts):
            i1 = np.nonzero(ldepth[n] >= depthBH)
            if i1.size == 0:
                x = np.zeros((1, npts))
                y = np.zeros((1, npts))
                z = np.zeros((1, npts))
                c = np.zeros((npts, 3))
                raise ValueError
            i1 = i1[-1]

            i2 = np.nonzero(ldepth[n] < depthBH)
            if i2.size == 0:
                x = np.zeros((1, npts))
                y = np.zeros((1, npts))
                z = np.zeros((1, npts))
                c = np.zeros((npts, 3))
                raise ValueError
            i2 = i2[0]


            #Here we calculate the distance between the points which have the same index than the closest points above and under
            d = np.sqrt(np.sum(fdata[i2, :] - fdata[i1, :]) ** 2)
            l = (fdata[i2, :] - fdata[i1, :]) / d
            # the l value represents the direction cosine for every dimension

            d2 = ldepth[n] - depthBH[i1]

            x[n] = fdata[i1, 0] + d2 * l[0]
            y[n] = fdata[i1, 1] + d2 * l[1]
            z[n] = fdata[i1, 2] + d2 * l[2]
            c[n, :] = 1

            #We represent the ldepth's point of interest coordinates by adding the direction cosine of every dimension to
            # the closest upper point's coordinates


if __name__ == '__main__':
    ldepth = np.array([0, 1, 2, 3, 4, 5])

    bh = Borehole('B01')

# -*- coding: utf-8 -*-
"""
Copyright 2017 Bernard Giroux, Elie Dumas-Lefebvre, Jerome Simon
email: Bernard.Giroux@ete.inrs.ca

This file is part of BhTomoPy.

BhTomoPy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np


class Borehole:
    """
    Class holding borehole data
    """

    def __init__(self, name=''):

        self.name = name
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.Xmax = 0.0
        self.Ymax = 0.0
        self.Zmax = 0.0
        self.Z_surf = 0.0
        self.Z_water = 0.0
        self.scont = np.array([])
        self.acont = np.array([])
        self.fdata = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        self.modified = True

    @staticmethod
    def project(fdata, ldepth):
        """
        Project measurement points on borehole trajectory

        INPUT:

        fdata: matrix(n, 3) where the 3 columns represent the x, y and z coordinates
        of the BH's trajectory for a single n value.
        The n are sorted in growing order, from the top to the bottom of the borehole.

        ldepth: vector(1,m) which reprensents the position of the m measurement points (from top to bottom)

        Note: the discrete points of the BH's trajectory are not the same as the discrete points of the ldepth
                that's why we do this function; to determine the projection of the ldepth point on the fdata trajectory.

        OUTPUT:

        x: x coordinates of all measurement points
        y: y coordinates of all measurement points
        z: z coordinates of all measurement points
        c: direction of cosines at measurements points which point downwards
        """

        npts = ldepth.size
        # the x,y and z coordinates are initially a matrix which contains as much 0 as the number of measurement points
        # we can see the c value as the combination of the three cartesian coordinates in unitary form
        x = np.zeros((npts, 1))
        y = np.zeros((npts, 1))
        z = np.zeros((npts, 1))
        c = np.zeros((npts, 3))

        depthBH = np.append(np.array([[0]]), np.cumsum(np.sqrt(np.sum(np.diff(fdata, n=1, axis=0) ** 2, axis=1))))

        # Knowing that de BH's depth is a matrix which contains the distance between every points of fdata, and that
        # ldepth contains the points where the data was taken,we need to first make sure that every points taken in
        # charge by ldepth is in the range of the BH's depth.  As a matter of fact, we verify if each points of ldepth
        # is contained in between the volume (i.e. between X and Xmax and the same for Y and Z).  If so, we take the
        # closest point under our point of interest (i.e. i2[0]) and the closest point above our point of interest
        # (i.e. i1[-1]). So you can anticipate that these points will change for every index of the ldepth vector.

        for n in range(npts):
            i1, = np.nonzero(ldepth[n] >= depthBH)
            i2, = np.nonzero(ldepth[n] < depthBH)
            if i1.size == 0 or i2.size == 0:
                raise ValueError('Depth data outside trajectory range')
            i1 = i1[-1]
            i2 = i2[0]

            # Here we calculate the distance between the points which have the same index than the closest points above
            # and under
            d = np.sqrt(np.sum(fdata[i2, :] - fdata[i1, :]) ** 2)
            l = (fdata[i2, :] - fdata[i1, :]) / d
            # the l value represents the direction cosine for every dimension

            d2 = ldepth[n] - depthBH[i1]

            x[n] = fdata[i1, 0] + d2 * l[0]
            y[n] = fdata[i1, 1] + d2 * l[1]
            z[n] = fdata[i1, 2] + d2 * l[2]
            c[n, :] = l

            # We represent the ldepth's point of interest coordinates by adding the direction cosine of every dimension
            # to the closest upper point's coordinates
        return x, y, z, c


if __name__ == '__main__':
    fdatatest = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4], [5, 5, 5]], dtype=np.float64)
    ldepthtest = np.array([1, 2, 3, 4, 5], dtype=np.float64)
    bh1 = Borehole('BH1')
    bh1.fdata = fdatatest
    x, y, z, c = Borehole.project(fdatatest, ldepthtest)
    print(x)
    print(y)
    print(z)
    print(c)

# -*- coding: utf-8 -*-
"""

Copyright 2016 Bernard Giroux, Elie Dumas-Lefebvre

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
import scipy as spy
from scipy.sparse import linalg

class InvLSQRParams:
    def __init__(self):
        self.tomoAtt        = 0
        self.selectedMogs   = []
        self.numItStraight  = 0
        self.numItCurved    = 0
        self.saveInvData    = 1
        self.useCont        = 0
        self.tol            = 0
        self.wCont          = 0
        self.alphax         = 0
        self.alphay         = 0
        self.alphaz         = 0
        self.order          = 1
        self.nbreiter       = 0
        self.dv_max         = 0

def invLSQR(params, data, idata, grid, L, app= None, ui= None):
    """
    Input:
    params:  Instance of lsqrParams class whose parameters have been
             edited in InversionUI or manually

    data:   (m, 15) array :
                          - data[:, 3]     == Tx(i.e. Tx_x, Tx_y, Tx_z)
                          - data[:, 3:6]   == Rx(i.e. Rx_x, Rx_y, Rx_z)
                          - data[:, 6:9]   == data from model(i.e. tt, et, trace_num)
                          - data[:, 9:12]  == TxCosDir
                          - data[:, 12:15] == RxCosDir

    idata: (n,) bool array:
                          - Values at a one index of this vector will be True if the mog.in_vect is True and mog.tt vector does not
                            equal -1.0 at this same index

                            ex:
                                mog.tt = np.array([ -1.0, 87.341, 79.649, -1.0])
                                mog.in_vect = np.array([ 1, 1, 0, 0])

                                idata = np.array([ False, True, False, False])

    grid: instance of Grid class

    L:
        First iteration:
                        - Sparse matrix which contains the trajectory of straight rays.
                        Rays are straight because we assume to have a homogeneous slowness/velocity model.

        Second iteration and more:
                                  - Sparse matrix which contains the tracjectory of curved rays.
                                  Rays are now curved because we've been able to build our
                                  slowness/velocity model from the scipy.sparse.linalg.lsqr method.

    app:
        if using Bh_Tomo/InversionUI:
            The application which contains the InversionUI QWidget.
            We need it to process the ui events such as the resfresh of the invFig

        if not using Bh_Tomo/InversionUI::
            app is set to none

    ui: the InversionUI QWidget
    """

    # Frst we call a Tomo class instance. It will hold the data we will process along the way.
    tomo = Tomo()


    if data.shape[1] >= 9:
        tomo.no_trace = data[:, 8]

    if np.all(L == 0):
        # We get the straights rays for the first iteration
        L = grid.getForwardStraightRays(idata)

    tomo.x = 0.5*(grid.grx[0:-2] + grid.grx[1:-1])
    tomo.z = 0.5*(grid.grz[0:-2] + grid.grz[1:-1])

    if not np.all(grid.gry == 0):
        tomo.y = 0.5*(grid.gry[0:-2] + grid.gry[1:-1])
    else:
        tomo.y = np.array([])

    cont = np.array([])
    #TODO:  Ajouter les conditions par rapport au contraintes de v�locit� appliqu�es dans grid editor


    # Getting our spatial derivative elements
    # These will smoothen the subsequent slowness/velocity model
    Dx, Dy, Dz = grid.derivative(params.order)

    for noIter in range(params.numItCurved + params.numItStraight):
        if ui != None and app != None:
            ui.gv.noIter = noIter
            app.processEvents()

        if noIter == 0:
            # Calculating the mean slowness from the picked tts and the ray lenghts
            mean_s = np.mean(data[:, 6]/ L.sum(axis= 1))
        else:
            mean_s = np.mean(tomo.s)

        # Making sur to have a b array whit (m,) shape
        mta = L.sum(axis= 1)*mean_s
        mta = np.hstack(mta).T

        tmp = mta.flat
        tmp = list(tmp)

        mta = np.asarray(tmp)

        dt = data[:, 6] - mta
        dt = dt.T

        if noIter == 0:
            s_o = mean_s * np.ones(L.shape[1]).T

        A = spy.sparse.vstack([L, Dx*params.alphax, Dz*params.alphaz])

        b = np.concatenate((dt, np.zeros(Dx.shape[0]), np.zeros(Dz.shape[0])))

        if not np.all(cont == 0) and params.useCont == 1:
            #TODO faire les modifications aux matrices A et b avec les contraintes
            pass

        ans = linalg.lsqr(A, b, atol= params.tol, btol= params.tol, iter_lim = params.nbreiter)
        # See http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.sparse.linalg.lsqr.html for documentation
        x = ans[0]

        if noIter == 0:
            tomo.res[0] = ans[3]
        else:
            np.append(tomo.res, ans[3])


        if max(abs(s_o/(x+mean_s) - 1)) > params.dv_max:
            fac = min(abs( (s_o/(params.dv_max+1)-mean_s)/x ))
            x = fac*x
            s_o = x + mean_s

        tomo.s = x + mean_s

        # Applying the resulting model to Tx and Rx to get new tt and L and the trajectory of curved rays
        tt, L, tomo.rays = grid.raytrace(tomo.s, data[:, 0:3], data[:, 3:6])

        if ui != None:
            ui.algo_label.setText('LSQR Inversion -')
            ui.noIter_label.setText('Ray Tracing, Iteration {}'.format(noIter+1))
            ui.gv.invFig.plot_lsqr_inv(tomo.s)
        else:
            print('LSQR Inversion - Ray Tracing, Iteration {}'.format(noIter+1))

        if params.saveInvData == 1:
            tt = L * tomo.s
            if noIter == 0:
                tomo.invData.res = np.array([data[:, 6] - tt]).T
                tomo.invData.s = np.array([tomo.s]).T

            else:
                tomo.invData.res = np.concatenate((tomo.invData.res, np.array([data[:, 6] - tt]).T), axis= 1)
                tomo.invData.s = np.concatenate((tomo.invData.s, np.array([tomo.s]).T), axis= 1)

        tomo.L = L

                #Results:
                #       tomo.invData.res:
                #                       - shape: (m, noIter+1)
                #                       - values: residuals from comparison between original tt (i.e. data[:, 6])
                #                                 and tt calculated from the slowness model and the L sparse matrix
                #
                #       tomo.invData.res:
                #                       - shape: (n, noIter+1)
                #                       - values: slowness models from ech iterations

    if ui != None:
        ui.algo_label.setText('LSQR Inversion -')
        ui.noIter_label.setText('Finished, {} Iterations Done'.format(noIter+1))
    else:
        print('LSQR Inversion - Finished, {} Iterations Done'.format(noIter+1))

    return tomo


class Tomo:
    def __init__(self):
        self.rays   = np.array([])
        self.L      = np.array([])
        self.invData = invData()
        self.no_trace = np.array([])
        self.x = np.array([])
        self.y = np.array([])
        self.z = np.array([])
        self.s = 0
        self.res = np.array([0])
        self.var_res = np.array([])

class invData:
    def __init__(self):
        self.res = np.array([0])
        self.s = np.array([0])

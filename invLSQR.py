import numpy as np
import scipy as spy
from scipy.sparse import linalg

def invLSQR(params, data, idata, grid, L, app= None, ui= None):
        tomo = Tomo()

        if data.shape[1] >= 9:
            tomo.no_trace = data[:, 8]

        if np.all(L == 0):
             L = grid.getForwardStraightRays(idata)

        tomo.x = 0.5*(grid.grx[0:-2] + grid.grx[1:-1])
        tomo.z = 0.5*(grid.grz[0:-2] + grid.grz[1:-1])

        if not np.all(grid.gry == 0):
            tomo.y = 0.5*(grid.gry[0:-2] + grid.gry[1:-1])
        else:
            tomo.y = np.array([])

        cont = np.array([])
        #TODO:  Ajouter les conditions par rapport au contraintes de vélocité appliquées dans grid editor



        Dx, Dy, Dz = grid.derivative(params.order)

        for noIter in range(params.numItCurved + params.numItStraight):
            if ui != None and app != None:
                ui.gv.noIter = noIter
                app.processEvents()

            if noIter == 0:
                l_moy = np.mean(data[:, 6]/ L.sum(axis= 1))
            else:
                l_moy = np.mean(tomo.s)

            # We make sur to have a b array whit (m,) shape
            mta = L.sum(axis= 1)*l_moy
            mta = np.hstack(mta).T

            tmp = mta.flat
            tmp = list(tmp)

            mta = np.asarray(tmp)

            dt = data[:, 6] - mta
            dt = dt.T

            if noIter == 0:
                s_o = l_moy * np.ones(L.shape[1]).T

            A = spy.sparse.vstack([L, Dx*params.alphax, Dz*params.alphaz])
            #print(A.shape)

            b = np.concatenate((dt, np.zeros(Dx.shape[0]), np.zeros(Dz.shape[0])))
            #print(b.shape)
            #A = L
            #b = dt

            if not np.all(cont == 0) and params.useCont == 1:
                #TODO
                pass

            ans = linalg.lsqr(A, b, atol= params.tol, btol= params.tol, iter_lim = params.nbreiter)
            x = ans[0]

            if noIter == 0:
                tomo.res[0] = ans[3]
            else:
                np.append(tomo.res, ans[3])


            if max(abs(s_o/(x+l_moy) - 1)) > params.dv_max:
                fac = min(abs( (s_o/(params.dv_max+1)-l_moy)/x ))
                x = fac*x
                s_o = x + l_moy

            tomo.s = x + l_moy

            tt, L, tomo.rays = grid.raytrace(tomo.s, data[:, 0:3], data[:, 3:6])

            if ui != None:
                ui.algo_label.setText('LSQR Inversion -')
                ui.noIter_label.setText('Ray Tracing, Iteration {}'.format(noIter+1))
                ui.gv.invFig.plot_inv(tomo.s)
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
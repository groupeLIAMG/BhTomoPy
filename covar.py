# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 20:55:29 2016

@author: giroux

Copyright 2017 Bernard Giroux, Jerome Simon
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

from collections import namedtuple
from enum import IntEnum
import sys

import numpy as np
from scipy.special import erfcinv
from scipy import linalg
# import pyfftw.interfaces.numpy_fft as np_fft


class Covariance(object):
    """
    Base class for Covariance models
    """
    def __init__(self, r, a, s):
        """
        Parameters
            r : ranges
            a : angles
            s : coefficient matrix of the coregionalization model
        """
        self.range = r
        self.angle = a
        self.sill = s
        self.type = None  # To be defined by CovarianceModels

    def trans(self, cx):
        d = cx.ndim
        if d == 2:
            d = cx.shape[1]

        if d != self.range.size:
            raise ValueError('Dimensionality of input data inconsistent')

        if d > 1:
            if d == 2:
                cang = np.cos(self.angle[0] / 180 * np.pi)
                sang = np.sin(self.angle[0] / 180 * np.pi)
                rot = np.array([[cang, -sang], [sang, cang]])
            else:
                cangz = np.cos(self.angle[2] / 180 * np.pi)
                sangz = np.sin(self.angle[2] / 180 * np.pi)
                cangy = np.cos(self.angle[1] / 180 * np.pi)
                sangy = np.sin(self.angle[1] / 180 * np.pi)
                cangx = np.cos(self.angle[0] / 180 * np.pi)
                sangx = np.sin(self.angle[0] / 180 * np.pi)
                rotz = np.array([[cangz, -sangz, 0], [sangz, cangz, 0], [0, 0, 1]])
                roty = np.array([[cangy, 0, sangy], [0, 1, 0], [-sangy, 0, cangy]])
                rotx = np.array([[1, 0, 0], [0, cangx, -sangx], [0, sangx, cangx]])
                rot = np.dot(np.dot(rotz, roty), rotx)

            cx = np.dot(cx, rot)
            t = np.tile(self.range, (cx.shape[0], 1))
        else:
            # rot = np.array([])
            t = self.range

        cx = cx / t
        return cx  # ,rot

    def compute(self, x, x0):
        h = self.compute_h(x, x0)
        return self._compute(h)

    def computeK(self, cx, m, n):
        h = self.compute_hK(cx, m, n)
        return self._compute(h)

    def compute_h(self, x, x0):
        n1, d = x.shape
        n2, d2 = x0.shape
        if d != d2:
            raise ValueError('Dimensionality of input data inconsistent')

        t1 = self.trans(x)
        t2 = self.trans(x0)
        h = 0
        for ii in np.arange(d):
            # TODO: debug this for n2>1
            tmp1 = np.tile(t1[:, ii], (n2, 1)).T
            tmp2 = np.tile(t2[:, ii], (n1, 1))
            h = h + (tmp1 - tmp2)**2

        return np.sqrt(h)

    def compute_hK(self, cx, m, n):
        t = self.trans(cx)
        t = np.dot(t, t.T)
        h = np.sqrt(-2. * t + np.dot(t.diagonal().reshape(-1, 1), np.ones((1, n + m))) +
                    np.dot(np.ones((n + m, 1)), t.diagonal().reshape(1, -1)))
        h = h[:n, :]
        return h


class CovarianceCubic(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Cubic

    def _compute(self, h):
        return np.kron((1.0 - 3.0 * np.minimum(h, 1)**2 + 2.0 * np.minimum(h, 1)**3), self.sill)


class CovarianceExponential(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Exponential

    def _compute(self, h):
        return np.kron(np.exp(-h), self.sill)


class CovarianceGaussian(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Gaussian

    def _compute(self, h):
        return np.kron(np.exp(-h**2), self.sill)


class CovarianceGravimetric(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Gravimetric

    def _compute(self, h):
        return np.kron((h**2 + 1)**-0.5, self.sill)


class CovarianceHoleEffectCosine(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Hole_Effect_Cosine

    def _compute(self, h):
        return np.kron(np.cos(2.0 * np.pi * h), self.sill)


class CovarianceHoleEffectSine(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Hole_Effect_Sine

    def _compute(self, h):
        return np.kron(np.sin(np.maximum(np.finfo(float).eps, 2.0 * np.pi * h)) /
                       np.maximum(np.finfo(float).eps, 2.0 * np.pi * h),
                       self.sill)


class CovarianceLinear(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Linear

    def _compute(self, h):
        return np.kron((1.0 - h), self.sill)


class CovarianceMagnetic(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Magnetic

    def _compute(self, h):
        return np.kron((h**2 + 1)**-1.5, self.sill)


class CovarianceNugget(Covariance):
    def __init__(self, s, d=2):
        if d == 1:
            a = []
        elif d == 2:
            a = np.array([0.0])
        elif d == 3:
            a = np.array([0.0, 0.0, 0.0])
        else:
            raise ValueError('Covariance should be 1D, 2D or 3D')

        Covariance.__init__(self, np.ones((d, )), a, s)
        self.type = CovarianceModels.Nugget

    def compute(self, x, x0):
        d = x.ndim
        if d == 2:
            d = x.shape[1]
        self.range = np.ones((d, ))
        if d == 3:
            self.angle = np.zeros((3, ))
        else:
            self.angle = np.array([0.0])

        h = self.compute_h(x, x0)
        return np.kron((h == 0), self.sill)

    def _compute(self, h):
        return np.kron((h == 0), self.sill)


class CovarianceSpherical(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Spherical

    def _compute(self, h):
        return np.kron((1 - (1.5 * np.minimum(h, 1) - 0.5 * (np.minimum(h, 1))**3)), self.sill)


class CovarianceThinPlate(Covariance):
    def __init__(self, r, a, s):
        Covariance.__init__(self, r, a, s)
        self.type = CovarianceModels.Thin_Plate

    def _compute(self, h):
        return np.kron(h**2 * np.log(np.maximum(h, np.finfo(float).eps)), self.sill)


class CovarianceModels(IntEnum):
    Cubic = 0
    Spherical = 1
    Gaussian = 2
    Exponential = 3
    Linear = 4
    Thin_Plate = 5
    Gravimetric = 6
    Magnetic = 7
    Hole_Effect_Sine = 8
    Hole_Effect_Cosine = 9
    Nugget = 10

    @staticmethod
    def buildCov(ctype, r, a, s):
        if ctype == 0:
            return CovarianceCubic(r, a, s)
        elif ctype == 1:
            return CovarianceSpherical(r, a, s)
        elif ctype == 2:
            return CovarianceGaussian(r, a, s)
        elif ctype == 3:
            return CovarianceExponential(r, a, s)
        elif ctype == 4:
            return CovarianceLinear(r, a, s)
        elif ctype == 5:
            return CovarianceThinPlate(r, a, s)
        elif ctype == 6:
            return CovarianceGravimetric(r, a, s)
        elif ctype == 7:
            return CovarianceMagnetic(r, a, s)
        elif ctype == 8:
            return CovarianceHoleEffectSine(r, a, s)
        elif ctype == 9:
            return CovarianceHoleEffectCosine(r, a, s)
        elif ctype == 10:
            return CovarianceNugget(s)
        else:
            raise ValueError('Undefined covariance model')

    @staticmethod
    def detDefault2D():
        return CovarianceSpherical(np.array([4.0, 4.0]), np.array([0.0]), 1.0)

    @staticmethod
    def detDefault3D():
        return CovarianceSpherical(np.array([4.0, 4.0, 4.0]), np.array([0.0, 0.0, 0.0]), 1.0)


class Structure(object):

    def __init__(self, dim_type):
        if dim_type == '2D' or dim_type == '2D+':
            self.slowness = CovarianceModels.detDefault2D()
        elif dim_type == '3D':
            self.slowness = CovarianceModels.detDefault3D()
        else:
            raise TypeError
        self.xi                = None
        self.tilt              = None
        self.nugget_slowness   = 0.0
        self.nugget_traveltime = 0.0
        self.nugget_xi         = 0.0
        self.nugget_tilt       = 0.0
        self.use_c0            = False
        self.use_xi            = False
        self.use_tilt          = False


def cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok, verbose=False):
    """
    Translation of cokri matlab function from D. Marcotte (adapted
    for covariance classes defined in this file)

    Ref paper:
    @Article{marcotte91,
      Title                    = {Cokriging with matlab},
      Author                   = {Marcotte, Denis},
      Journal                  = {Computers and Geosciences},
      Year                     = {1991},
      Number                   = {9},
      Pages                    = {1265--1280},
      Volume                   = {17},
      DOI                      = {10.1016/0098-3004(91)90028-C}
    }

    INPUT

    x:     The n x (p+d) data matrix. This data matrix can be imported from an
            existing ascii file. Missing values are coded 'nan' (not-a-number)
    x0:    The m x d matrix of coordinates of points to estimate
    cm:    List of covariance models
    itype: Code to indicate which type of cokriging is to be performed:
             1:  simple cokriging
             2:  ordinary cokriging with one nonbias condition
                 (Isaaks and Srivastava).
             3:  ordinary cokriging with p nonbias condition.
             4:  universal cokriging with drift of order 1.
             5:  universal cokriging with drift of order 2.
             99: cokriging is not performed, only sv is computed.
    avg:   Mean of the data (for simple cokriging)
    block: Vector (1 x d), giving the size of the block to estimate;
            any values when point cokriging is required
    nd:    Vector (1 x d), giving the discretization grid for block cokriging;
            put every element equal to 1 for point cokriging.
    ival:  Code for cross-validation.
             0:  no cross-validation
             1:  cross-validation is performed  by removing one variable at a
                 time at a given location.
             2:  cross-validation is performed by removing all variables at a
                 given location
    nk:    Number of nearest neighbors in x matrix to use in the cokriging
           (this includes locations with missing values even if all variables
            are missing)
    rad:   Search radius for neighbors
    ntok:  Points in x0 will be kriged by groups of ntok grid points.
            When ntok>1, the search will find the nk nearest samples within
            distance rad from the current ntok grid points centroid

    OUTPUT

    x0s:   m x (d+p) matrix of the m points (blocks) to estimate by the
            d coordinates and p cokriged estimates.
    s:     m x (d+p) matrix of the m points (blocks) to estimate by the
            d coordinates and the p cokriging variances.
    sv:    1 x p vector of variances of points (blocks) in the universe.
    idout: (nk x p) x 2 matrix giving the identifiers of the lambda weights for
            the last cokriging system solved.
    l:     ((nk x p) + nc) x (ntok x p) matrix with lambda weights and
            Lagrange multipliers of the last cokriging system solved.
    K:     Left covariance matrix of the cokriging system
    K0:    Right covariance matrix of the cokriging system

    """

    x0s = np.array([])
    s = np.array([])
    sv = np.array([])
    idout = np.array([])
    l = np.array([])
    K = np.array([])
    K0 = np.array([])

    if not isinstance(cm, list):
        cm = [cm]

    m, d = x0.shape

    #  check for cross-validation

    if ival >= 1:
        ntok = 1
        x0 = x[:, :d]
        nd = np.ones((nd,))
        m, d = x0.shape

    if np.isscalar(cm[0].sill):
        p = 1
    else:
        p = cm[0].sill.shape[0]

    n, t = x.shape
    nk = min(nk, n)
    ntok = min(ntok, m)
    idp = np.arange(p).reshape((p, 1))
    ng = np.prod(nd)

    # compute point (ng=1) or block (ng>1) variance

    for i in range(d):
        if i == 0:
            nl = 1
        else:
            nl = np.prod(nd[:i])
        if i == d - 1:
            nr = 1
        else:
            nr = np.prod(nd[i + 1:])

        t = np.arange(.5 * (1. / nd[i] - 1), .5 * (1. - 1. / nd[i]) + 100 * np.finfo(float).eps, 1. / nd[i])
        t = t.reshape((-1, 1))
        if i == 0:
            t2 = np.kron(np.ones((nl, 1)), np.kron(t, np.ones((nr, 1))))
        else:
            t2 = np.hstack((t2, np.kron(np.ones((nl, 1)), np.kron(t, np.ones((nr, 1))))))

    grid = t2 * (np.ones((ng, 1)) * block)
    t = np.hstack((grid, np.zeros((ng, p))))

    # for block cokriging, a double grid is created by shifting slightly the
    # original grid to avoid the zero distance effect (Journel and Huijbregts, p.96)

    if ng > 1:
        grid += (np.ones((ng, 1)) * block) / (ng * 1.e6)

    x0s, s, idl, l, K, K0 = _cokri2(t, grid, np.array([]), cm, sv, 99, avg, ng)

    # sv contain the variance of points or blocks in the universe

    i = 0
    sv = means(means(K0[i:ng * p:p, i:ng * p:p]).T)
    for i in range(1, p):
        sv = np.hstack((sv, means(means(K0[i:ng * p:p, i:ng * p:p]).T)))

    if verbose:
        nskip = int(np.log10(m / ntok))
        nskip = int(10**(nskip - 2))
        if nskip < 1:
            nskip = 1

    # start cokriging
    for i in np.arange(0, m, ntok):
        nnx = min((m - i, ntok))
        if verbose and ((i + 1) % nskip == 0):
            print('Cokriging - loop ' + str(int(i / ntok) + 1) + '/' + str(1 + int(m / ntok)))

        # sort x samples in increasing distance relatively to centroid of 'ntok'
        # points to krige
        centx0 = np.dot(np.ones((n, 1)), means(x0[i:i + nnx, :]))
        tx = np.dot((x[:, :d] - centx0) * (x[:, :d] - centx0), np.ones((d, 1)))
        j = np.argsort(tx, axis=0).flatten()
        tx = tx[j, :]

        # keep samples inside search radius; create an identifier of each sample
        # and variable (id)
        ii = 0
        t = x[j[ii], :]
        idl = np.hstack((np.ones((p, 1)) * j[ii], idp))
        ii += 1
        while ii < nk and tx[ii] < rad * rad:
            t = np.vstack((t, x[j[ii], :]))
            idl = np.vstack((idl, np.hstack((np.ones((p, 1)) * j[ii], idp))))
            ii += 1

        if verbose and ((i + 1) % nskip == 0):
            print('  Processing ' + str(int(nnx)) + ' points with ' + str(t.shape[0]) + ' data points')
            sys.stdout.flush()

        t2 = x0[i:i + nnx, :]

        # if block cokriging discretize the block

        t2 = np.kron(t2, np.ones((ng, 1))) - np.kron(np.ones((nnx, 1)), grid)

        # check for cross-validation

        if ival >= 1:
            est = np.zeros((1, p))
            sest = np.zeros((1, p))

            # each variable is cokriged in its turn

            if ival == 1:
                npp = 1
            else:
                npp = p

            for ip in np.arange(0, npp, p):

                # because of the sort, the closest sample is the sample to
                # cross-validate and its value is in row 1 of t; a temporary vector
                # keeps the original values before performing cokriging
                vtemp = t[0, d + ip:d + ip + npp]
                t[0, d + ip:d + ip + npp] = np.zeros((1, npp)) + np.nan
                x0ss, ss, idout, l, K, K0 = _cokri2(t, t2, idl, cm, sv, itype, avg, ng)
                est[ip:ip + npp] = x0ss[ip:ip + npp]
                sest[ip:ip + npp] = ss[ip:ip + npp]
                t[0, d + ip:d + ip + npp] = vtemp

            if x0s.size == 0:
                x0s = np.hstack((t2, est))
            else:
                x0s = np.vstack((x0s, np.hstack((t2, est))))
            if s.size == 0:
                s = np.hstack((t2, sest))
            else:
                s = np.vstack((s, np.hstack((t2, sest))))

        else:
            x0ss, ss, idout, l, K, K0 = _cokri2(t, t2, idl, cm, sv, itype, avg, ng)
            if x0s.size == 0:
                x0s = np.hstack((x0[i:i + nnx, :], x0ss))
            else:
                x0s = np.vstack((x0s, np.hstack((x0[i:i + nnx, :], x0ss))))
            if s.size == 0:
                s = np.hstack((x0[i:i + nnx, :], ss))
            else:
                s = np.vstack((s, np.hstack((x0[i:i + nnx, :], ss))))

    return x0s, s, sv, idout, l, K, K0


def _cokri2(x, x0, idl, cm, sv, itype, avg, ng):

    x0s = np.array([])
    s = np.array([])
    l = np.array([])
    K = np.array([])
    K0 = np.array([])
    nc = 0

    n, t = x.shape
    m, d = x0.shape
    if np.isscalar(cm[0].sill):
        p = 1
    else:
        p = cm[0].sill.shape[0]

    # if no samples found in the search radius, return NaN
    if n == 0:
        x0s = np.nan * np.ones((m / ng, p))
        s = np.nan * np.ones((m / ng, p))
        return x0s, s, idl, l, K, K0

    cx = np.vstack((x[:, :d], x0))

    # calculation of left covariance matrix K and right covariance matrix K0

    K = np.zeros((n * p, (n + m) * p))
    for c in cm:
        K = K + c.computeK(cx, m, n)
    K0 = K[:, n * p:(n + m) * p]
    K = K[:, :n * p]

    # constraints are added according to cokriging type

    if itype == 99:
        # the system does not have to be solved
        return x0s, s, idl, l, K, K0

    if itype == 2:
        # cokriging with one non-bias condition (Isaaks and Srivastava, 1990, p.410)
        K = np.vstack((np.hstack((K, np.ones((n * p, 1)))), np.ones((1, 1 + n * p))))
        K[-1:-1] = 0.0
        K0 = np.vstack((K0, np.ones((1, m * p))))
        nc = 1
    elif itype >= 3:
        # ordinary cokriging (Myers, Math. Geol, 1982)

        t = np.kron(np.ones((1, n)), np.eye(p))
        K = np.vstack((np.hstack((K, t.T)), np.hstack((t, np.zeros((p, p))))))
        K0 = np.vstack((K0, np.kron(np.ones((1, m)), np.eye(p))))
        nc = p

        # cokriging with one non-bias condition in the z direction
        if itype == 3.5:
            t = np.kron(cx[:n, d - 1], np.eye(p))
            K = np.vstack((np.hstack((K, np.vstack((t, np.zeros((p, p)))))),
                           np.hstack((t.T, np.zeros((p, p + p))))))
            t = np.kron(cx[n:n + m, d - 1].T, np.eye(p))
            K0 = np.vstack((K0, t))
            nc += p
        if itype >= 4:
            # universal cokriging ; linear drift constraints
            nca = p * d
            t = np.kron(cx[:n, :], np.eye(p))
            K = np.vstack((np.hstack((K, np.vstack((t, np.zeros((p, nca)))))),
                           np.hstack((t.T, np.zeros((nca, nc + nca))))))
            t = np.kron(cx[n:n + m, :].T, np.eye(p))
            K0 = np.vstack((K0, t))
            nc = nc + nca

        if itype == 5:
            # universal cokriging ; quadratic drift constraints

            nca = p * d * (d + 1) / 2
            cx2 = np.empty((cx.shape[0], np.sum(1 + np.arange(d))))
            ic = 0
            for i in range(d):
                for j in range(i, d):
                    cx2[:, ic] = cx[:, i] * cx[:, j]
                    ic += 1
            t = np.kron(cx2[:n, :], np.eye(p))
            K = np.vstack((np.hstack((K, np.vstack((t, np.zeros((nc, nca)))))),
                           np.hstack((t.T, np.zeros((nca, nc + nca))))))
            t = np.kron(cx2[n:n + m, :].T, np.eye(p))
            K0 = np.vstack((K0, t))
            nc = nc + nca

    # columns of k0 are summed up (if necessary) for block cokriging

    m = int(m / ng)
    t = np.empty((K0.shape[0], m * p))
    ic = 0
    for i in range(m):
        for ip in range(p):
            j = ng * p * i + ip
            t[:, ic] = means(K0[:, j:(i + 1) * ng * p:p].T)
            ic += 1
    K0 = t

    t = x[:, d:d + p]
    if itype < 3:
        # if simple cokriging or cokriging with one non bias condition, the means
        # are substracted
        t = (t - np.ones((n, 1)) * avg).T
    else:
        t = t.T

    # removal of lines and columns in K and K0 corresponding to missing values
    z = t.flatten(order='F')
    iz = np.logical_not(np.isnan(z))
    iz2 = np.hstack((iz, np.ones((nc,), dtype=bool)))
    nz = np.sum(iz)

    if nz == 0:
        x0s = np.nan
        s = np.nan
        return x0s, s, idl, l, K, K0
    else:
        K = K[iz2, :]
        K = K[:, iz2]
        K0 = K0[iz2, :]
        idl = idl[iz, :]

        # solution of the cokriging system

        l = linalg.solve(K, K0)

        # calculation of cokriging estimates

        t = np.dot(l[:nz, :].T, z[iz])
        t = t.reshape((p, m), order='F')

        # if simple or cokriging with one constraint, means are added back

        if itype < 3:
            t = t.T + np.ones((m, 1)) * avg
        else:
            t = t.T
        x0s = t

        # calculation of cokriging variances

        s = np.kron(np.ones((m, 1)), sv)
        t = np.diag(np.dot(l.T, K0))
        t = t.reshape((p, m), order='F')
        s = s - t.T

    return x0s, s, idl, l, K, K0


def means(x):
    if x.ndim == 1:
        return x

    m, n = x.shape
    m = np.sum(x, axis=0) / m
    return m.reshape(1, -1)


def norminv(p, mu=0.0, sigma=1.0):
    """
    quick and dirty translation of matlab function
    """
    x0 = -np.sqrt(2.0) * erfcinv(2.0 * p)
    return sigma * x0 + mu


def nscore(data, w1=0, w2=0, dmin=np.nan, dmax=np.nan, doPlot=False):
    """
    Normal score transform

    INPUT
        data : array of data to transform into normal scores
        w1,dmin : Extrapolation options for lower tail
           w1=0 -> no extrapolation
           w1=1 -> linear interpolation
           w1>1 -> gradual power interpolation
        w2,dmax : Extrapolation options for upper tail
           w2=0 -> no extrapolation
           w2=1 -> linear interpolation
           w2>1 -> gradual power interpolation
        doPlot : show the CCPDF

    OUTPUT
        data_ns : data after transformation
        o_nscore: data needed to do inverse transform
    """
    d = data.copy()

    n = d.size

    _id = np.arange(n)

    pk = _id / n + 0.5 / n
    normscore = norminv(pk)

    tmp = np.vstack((d, _id)).T
    s_sort = tmp[tmp[:, 0].argsort(), ]
    data_ns = np.zeros(normscore.shape)
    data_ns[np.int64(s_sort[:, 1])] = normscore

    if doPlot:
        import matplotlib.pyplot as plt
        sd_org = np.sort(d)
        pk_org = pk.copy()

        fig, ax = plt.subplots(ncols=2)
        ax[0].hist(data)
        ax[0].set_title('Original data')
        ax[0].set_xlabel('X')
        ax[0].set_ylabel('PDF')

        ax[1].hist(normscore)
        ax[1].set_xlabel('X, normal score transformed')
        ax[1].set_ylabel('PDF')
        ax[1].set_title('Normal Score Data')

        plt.show()

    if w1 >= 1.0:
        if np.isnan(dmin):
            dmin = np.min(d) - 1.e-9

        if dmin > np.min(d):
            dmin = np.min(d) - 1.e-9

        d1 = np.min(d)

        nbin = 10
        pk1 = np.min(pk)

        dlow = np.linspace(dmin, d1, nbin + 1)
        dlow = dlow[:10]
        pklow = pk1 * ((dlow - dmin) / (d1 - dmin))**w1

        d = np.hstack((dlow, d))
        pk = np.hstack((pklow, pk))

    if w2 >= 1.0:
        if np.isnan(dmax):
            dmax = np.max(d) + 1.e-9

        if dmax < np.max(d):
            dmax = np.max(d) + 1.e-9

        dk = np.max(d)
        nbin = 10
        pkk = np.max(pk)
        dhigh = np.linspace(dk, dmax, nbin + 1)
        dhigh = dhigh[1:]

        pkhigh = pkk + (1 - pkk) * ((dhigh - dk) / (dmax - dk))**w2

        d = np.hstack((d, dhigh))
        pk = np.hstack((pk, pkhigh))

    if w1 >= 1.0 or w2 >= 1.0:
        n = d.size
        _id = np.arange(n)
        normscore = norminv(pk)

    #    tmp = np.vstack((d, _id)).T
    #    s_sort = tmp[tmp[:,0].argsort(),]
    #    d_nscore = np.zeros(d.shape)
    #    d_nscore[np.int64(s_sort[:,1])] = normscore

    if doPlot:
        sd = np.sort(d)
        plt.figure(1)
        l1, = plt.plot(sd, pk, 'r-*', markersize=8)
        l2, = plt.plot(sd_org, pk_org, 'kd', markersize=10, fillstyle='none')
        plt.xlabel('X')
        plt.ylabel('CPDF')
        plt.title('ORIG CDF')
        plt.legend((l1, l2), ('ORG+Head+Tail', 'ORIGINAL'))
        plt.show()

    O_nscore = namedtuple('O_nscore', ['pk', 'd', 'normscore'])
    o_nscore = O_nscore(pk, d, normscore)

    return data_ns, o_nscore


def inscore(data, o_nscore, doPlot=False):

    ind = np.nonzero(np.isfinite(o_nscore.normscore))

    d_orig = np.sort(o_nscore.d)

    d_out = np.interp(data, o_nscore.normscore[ind], d_orig[ind])

    if doPlot:
        import matplotlib.pyplot as plt
        plt.plot(o_nscore.normscore[ind], d_orig[ind], 'k-*')
        plt.plot(data, d_out, 'go', fillstyle='none')
        plt.show()

    return d_out


def variof1(x, icode=1, nt=None):
    """
    @Article{marcotte96,
      Title                    = {Fast variogram computation with FFT},
      Author                   = {Marcotte, Denis},
      Journal                  = {Conputers and Geosciences},
      Year                     = {1996},
      Month                    = dec,
      Number                   = {10},
      Pages                    = {1175--1186},
      Volume                   = {22},
      DOI                      = {10.1016/S0098-3004(96)00026-X}
    }
    """
    if nt is None:
        import multiprocessing
        try:
            nt = int(multiprocessing.cpu_count() / 2)
        except NotImplementedError:
            nt = 1

    x1 = x.copy()
    n, p = x1.shape
    nrows = 2 * n - 1
    ncols = 2 * p - 1

    # find the closest multiple of 8 to obtain a good compromise between
    # speed (a power of 2) and memory required

    nr2 = int(np.ceil(nrows / 8) * 8)
    nc2 = int(np.ceil(ncols / 8) * 8)

    # form an indicator  matrix:                         1's for all data values
    #                                                     0's for missing values
    # in data matrix, replace missing values by 0

    x1id = np.logical_not(np.isnan(x1))         # 1 for a data value; 0 for missing
    x1[np.logical_not(x1id)] = 0.0              # missing replaced by 0

    fx1 = np_fft.fft2(x1, [nr2, nc2], threads=nt)              # fourier transform of x1

    if icode == 1:
        fx1_x1 = np_fft.fft2(x1 * x1, [nr2, nc2], threads=nt)  # fourier transform of x1*x1

    fx1id = np_fft.fft2(x1id, [nr2, nc2], threads=nt)          # fourier transform of the indicator matrix

    # compute number of pairs at all lags

    nh11 = np.round(np.real(np_fft.ifft2(np.conj(fx1id) * fx1id, threads=nt)))

    # compute the different structural functions according to icode

    if icode == 1:                                       # variogram is computed
        gh11 = np.real(np_fft.ifft2(np.conj(fx1id) * fx1_x1 + np.conj(fx1_x1) * fx1id - 2 * np.conj(fx1) * fx1, threads=nt))
        gh11 = gh11 / np.maximum(nh11, 1) / 2

    else:                                                # covariogram is computed

        m1 = np.real(np_fft.ifft2(np.conj(fx1) * fx1id), threads=nt) / np.maximum(nh11, 1)   # compute tail mean
        m2 = np.real(np_fft.ifft2(np.conj(fx1id) * fx1), threads=nt) / np.maximum(nh11, 1)   # compute head mean

        gh11 = np.real(np_fft.ifft2(np.conj(fx1) * fx1, threads=nt))
        gh11 = gh11 / np.maximum(nh11, 1) - m1 * m2

    # reduce matrix to required size and shift so that the 0 lag appears at the center of each matrix
    nh11 = np.vstack((np.hstack((nh11[:n, :p], nh11[:n, nc2 - p + 1:nc2])),
                      np.hstack((nh11[nr2 - n + 1:nr2, :p], nh11[nr2 - n + 1:nr2, nc2 - p + 1:nc2]))))
    gh11 = np.vstack((np.hstack((gh11[:n, :p], gh11[:n, nc2 - p + 1:nc2])),
                      np.hstack((gh11[nr2 - n + 1:nr2, :p], gh11[nr2 - n + 1:nr2, nc2 - p + 1:nc2]))))

    gh11 = np_fft.fftshift(gh11)
    nh11 = np_fft.fftshift(nh11)

    return gh11, nh11


def varioexp2d(x, y, v, nbclas, lclas, vdir, vtol, bandwidth):
    """
    Experimental variogram in 2D

    INPUT
        x : X coordinates   (nv,)
        y : Y coordinates   (nv,)
        v : values          (nv,)
        nbclas : nb of classes
        lclas  : length of classes. Scalar or n x 2 array with lag limits
                    on each line (min, max)
        vdir   : directions (azimuth)  (deg)
        vtol   : tolerance angle (90° for omni-directional variogram) (deg)
        bandwidth : ignored if vtol >= 90°

    OUTPUT
        gexp : 3d array of size nclas x 3 x ndir
                1st "column" : average distance
                2nd "column" : nb of pairs
                3rd "column" : variogram
    """
    if len(lclas) == 1:
        lclas = lclas * np.vstack((np.arange(0, nbclas),
                                   np.arange(1, (1 + nbclas)))).T
    ncl = lclas.shape[0]

    if vdir.shape[0] != vtol.size:
        raise ValueError('Number of directions inconsistent with nb of regularization')
    ndir = vdir.shape[0]

    n = x.size
    gexp = np.zeros((ncl, 3, ndir))
    u = _poletocart(np.vstack((vdir, np.zeros((ndir,)))).T)
    tol = np.cos(vtol * np.pi / 180)

    for i in range(n - 1):
        yt = np.vstack((i + np.zeros((n - i - 1, ), dtype=int), np.arange(i + 1, n, dtype=int))).T

        dx = x[yt[:, 1]] - x[yt[:, 0]]
        dy = y[yt[:, 1]] - y[yt[:, 0]]
        ht = np.sqrt(dx * dx + dy * dy)

        uobs = np.zeros((dx.shape[0], 3))
        uobs[:, 0] = dx / ht
        uobs[:, 1] = dy / ht

        for idir in range(ndir):

            da = np.dot(uobs, u[idir, :].T)
            if vtol[idir] < 90.0:
                # compute distance between pts and azimuth line
                c = -(u[idir, 0] * x[i] + u[idir, 1] * y[i])
                dist = (np.abs(u[idir, 0] * x[yt[:, 1]] + u[idir, 1] * y[yt[:, 1]] + c) /
                        np.sqrt(u[idir, 0] * u[idir, 0] + u[idir, 1] * u[idir, 1]))
                ind = np.logical_and(np.abs(da) >= tol[idir], dist < bandwidth[idir])
            else:
                ind = np.abs(da) >= tol[idir]

            h = ht[ind]
            yy = yt[ind, :]

            var = 0.5 * (v[yy[:, 0]] - v[yy[:, 1]])**2

            for ic in range(ncl):
                ind = np.logical_and(h > lclas[ic, 0], h <= lclas[ic, 1])
                gexp[ic, 1, idir] += np.sum(ind)
                gexp[ic, 0, idir] += np.sum(h[ind])
                gexp[ic, 2, idir] += np.sum(var[ind])

    for idir in range(ndir):
        ind = gexp[:, 1, idir] > 0
        gexp[ind, 0, idir] /= gexp[ind, 1, idir]
        gexp[ind, 2, idir] /= gexp[ind, 1, idir]

    return gexp


def _poletocart(pole):
    pole *= np.pi / 180.0
    x = np.zeros((pole.shape[0], 3))
    x[:, 0] = np.cos(pole[:, 1]) * np.sin(pole[:, 0])
    x[:, 1] = np.cos(pole[:, 1]) * np.cos(pole[:, 0])
    x[:, 2] = -np.sin(pole[:, 1])
    return x


def computeJ(L, e):

    nt = np.size(L, 1)
    np_ = np.size(L, 2) / 2

    J = L**2
    Js = J[:, 1:np_] + J[:, (np_ + 1):] * np.kron(np.ones(nt, 1), (e[(np_ + 1):]**2).T)  # l_x^2 + l_z^2 * xi^2
    Js = np.sqrt(Js)  # equals to t / s_x

    Jxi = J[:, (np_ + 1):] * np.kron(np.ones(nt, 1), (e[1:np_]).T) * np.kron(np.ones(nt, 1), (e[(np_ + 1):]).T)

    ind = Js != 0
    Jxi[ind] = Jxi[ind] / Js[ind]

    J = np.array([Js, Jxi])
    return J


def computeJ2(L, e):

    nt = np.size(L, 1)
    np_ = np.size(L, 2) / 2

    n = len(e) / 3

    if np_ != n:
        raise ValueError("Error (computeJ2) - L et e sizes not compatible")

    s = (e[1:n]).T
    xi = (e[(n + 1):(2 * n)]).T
    theta = (e[(2 * n + 1):(3 * n)]).T

    co = np.cos(theta)
    si = np.sin(theta)

    tmp = (L[:, 1:np_] * np.kron(np.ones(nt, 1), co) + L[:, (np_ + 1):] * np.kron(np.ones(nt, 1), si))**2
    tmp = (tmp + np.kron(np.ones(nt, 1), xi**2) *
           (L[:, 1:np_] * np.kron(np.ones(nt, 1), si) - L[:, (np_ + 1):] * np.kron(np.ones(nt, 1), co))**2)
    Js = np.sqrt(tmp)

    tmp = (L[:, 1:np_] * np.kron(np.ones(nt, 1), si) - L[:, (np_ + 1):] * np.kron(np.ones(nt, 1), co))**2
    Jxi = np.kron(np.ones(nt, 1), s) * np.kron(np.ones(nt, 1), xi) * tmp

    ind = Js != 0
    Jxi[ind] = Jxi[ind] / Js[ind]

    tmp = L[:, 1:np_]**2 - L[:, (np_ + 1):]**2
    tmp = tmp * np.kron(np.ones(nt, 1), np.sin(2 * theta))
    tmp = tmp - 2 * L[:, 1:np_] * L[:, (np_ + 1):] * np.kron(np.ones(nt, 1), np.cos(2 * theta))
    Jtheta = np.kron(np.ones(nt, 1), s) * np.kron(np.ones(nt, 1), (xi**2 - 1)) * tmp

    Jtheta[ind] = Jtheta[ind] / Js[ind]

    J = np.array([Js, Jxi, Jtheta])
    return J


def moy_bloc(xy, lclas):

    k = np.floor(len(xy) / lclas)

    m = np.mean(np.reshape(xy[1:k * lclas], lclas, k))
    m[k] = np.mean(xy[(k - 1) * lclas + 1:])

    return m


if __name__ == '__main__':

    testBasic = False
    testCokri = False
    testCokriBlock = False

    test2 = False
    testNormScore = False
    testExample2 = False
    testVariof = False
    testVarioExp = True

    if testBasic:
        x = np.array([[0.0, 0.0],
                      [0.0, 1.0],
                      [0.0, 10.0],
                      [0.0, 20.0],
                      [0.0, 25.0]])

        cm = Covariance(np.array([10.0, 3.0]), np.array([30]), 2.5)

        cm = CovarianceCubic(np.array([10.0, 3.0]), np.array([30]), 2.5)

        h = cm.compute_h(x, x)
        k = cm.compute(x, x)

        cm = CovarianceExponential(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k2 = cm.compute(x, x)

        cm = CovarianceGaussian(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k3 = cm.compute(x, x)

        cm = CovarianceGravimetric(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k4 = cm.compute(x, x)

        cm = CovarianceHoleEffectCosine(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k5 = cm.compute(x, x)

        cm = CovarianceHoleEffectSine(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k6 = cm.compute(x, x)

        cm = CovarianceLinear(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k7 = cm.compute(x, x)

        cm = CovarianceMagnetic(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k8 = cm.compute(x, x)

        cm = CovarianceNugget(np.array([2.5]))
        k9 = cm.compute(x, x)

        cm = CovarianceSpherical(np.array([10.0, 3.0]), np.array([30]), 2.5)
        k10 = cm.compute(x, x)

        cm = CovarianceModels.buildCov(5, np.array([10.0, 3.0]), np.array([30]), 2.5)
        k11 = cm.compute(x, x)

        c = np.array([[2.5, 1.4], [1.8, 1.0]])

        cm = CovarianceSpherical(np.array([10.0, 3.0]), np.array([30]), c)
        k10b = cm.compute(x, x)

        cm = Covariance(np.array([10.0, 3.0, 5.0]), np.array([30, 15, 10.0]), 2.5)

        x = np.array([[0.0, 0.0, 0.0],
                      [0.0, 1.0, 5.0],
                      [0.0, 10.0, 4.0],
                      [0.0, 20.0, 8.0],
                      [0.0, 25.0, 3.0]])

        h2 = cm.compute_h(x, np.zeros((1, 3)))

        t = cm.trans(x)

    if testCokri:

        import matplotlib.pyplot as plt

        x = np.array([[0.1, 0.1, 1.2],
                      [5.1, 3.3, 0.7],
                      [1.2, 7.8, 1.3],
                      [8.8, 5.5, 0.3],
                      [9.9, 1.9, 1.5]])

        xx = np.arange(0.0, 10.1, 0.25).reshape((-1, 1))
        yy = np.arange(0.0, 8.1, 0.25).reshape((-1, 1))

        nx = xx.size
        ny = yy.size
        x0 = np.hstack((np.kron(xx, np.ones((ny, 1))),
                        np.kron(np.ones((nx, 1)), yy)))

        cm = CovarianceSpherical(np.array([10.0, 3.0]), np.array([30]), 0.6)

        itype = 1
        avg = 1.0
        block = np.array([1, 1])
        nd = np.array([1, 1])
        ival = 0
        nk = 10000
        rad = 100.0
        ntok = 10000

        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)
        plt.imshow(x0s[:, 2].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()

        itype = 2
        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)
        plt.imshow(x0s[:, 2].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()

        c = np.array([[2.5, 1.4], [1.8, 1.0]])
        cm = CovarianceSpherical(np.array([10.0, 3.0]), np.array([30]), c)

        avg = np.array([[1.0, 1.3]])
        x = np.array([[0.1, 0.1, 1.2, 2.3],
                      [5.1, 3.3, 0.7, 1.4],
                      [1.2, 7.8, 1.3, 0.1],
                      [8.8, 5.5, 0.3, -0.1],
                      [9.9, 1.9, 1.5, 0.9]])

        itype = 1
        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)
        plt.imshow(x0s[:, 2].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()
        plt.imshow(x0s[:, 3].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()

        itype = 2
        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)
        plt.imshow(x0s[:, 2].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()
        plt.imshow(x0s[:, 3].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()

    if testCokriBlock:

        c = np.array([[2.5, 1.4], [1.8, 1.0]])
        cm = CovarianceSpherical(np.array([10.0, 3.0]), np.array([30]), c)

        avg = np.array([[1.0, 1.3]])
        x = np.array([[0.1, 0.1, 1.2, 2.3],
                      [5.1, 3.3, 0.7, 1.4],
                      [1.2, 7.8, 1.3, 0.1],
                      [8.8, 5.5, 0.3, -0.1],
                      [9.9, 1.9, 1.5, 0.9]])

        itype = 2
        block = np.array([2, 2])
        nd = np.array([2, 2])
        ival = 0
        nk = 10000
        rad = 100.0
        ntok = 10000

        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)
        plt.imshow(x0s[:, 2].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()
        plt.imshow(x0s[:, 3].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()

        itype = 3
        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)
        plt.imshow(x0s[:, 2].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()
        plt.imshow(x0s[:, 3].reshape((41, 33)).T)
        plt.colorbar()
        plt.show()

    if test2:

        x = np.array([[0.0, 0.0],
                      [0.0, 1.0],
                      [0.0, 10.0]])
        x2 = np.array([[0.0, 20.0],
                       [0.0, 25.0]])

        cm = CovarianceSpherical(np.array([10.0, 3.0]), np.array([30]), 0.6)

        k1 = cm.compute(x, x2)

        x = np.array([[0.0, 0.0],
                      [0.0, 1.0],
                      [0.0, 10.0],
                      [0.0, 20.0],
                      [0.0, 25.0]])

        k2 = cm.computeK(x, 2, 3)

        print(k1)
        print(k2)

    if testNormScore:
        data = np.array([1.2, 3.2, 3.3, 9.4, 2.9, 4.4, 3.5, 6.5, 8.7, 6.6, 5.5, 3.9, 1.1, 0.4])

        data_ns1, o_ns1 = nscore(data, w1=1.0, dmin=-1.0, w2=1.0, dmax=12.0, doPlot=True)

        data_ns2, o_ns2 = nscore(data, doPlot=True)

        d_out = inscore(data_ns2, o_ns2, doPlot=True)

    if testExample2:
        x = np.array([[-3.0,  6.0, 1.0,  5.0,  0.0, 4.0],
                      [-8.0, -5.0, 0.0, 52.0, 38.0, np.nan],
                      [ 3.0, -3.0, 3.0, 67.0,  6.0, 58.0]])
        x0 = np.array([[ 0.0,  0.0,  0.0],
                       [10.0, 20.0, 33.0]])
        block = np.array([5.0, 10.0, 5.0])
        nd = np.array([3, 3, 2])

        c1 = np.array([[20.0, 10.0,  5.0],
                       [10.0, 25.0,  3.0],
                       [ 5.0,  3.0, 12.0]])
        c2 = np.array([[ 50.0, -20.0, 15.0],
                       [-20.0,  25.0, -7.0],
                       [ 15.0,  -7.0, 15.0]])
        cm = [CovarianceNugget(c1, 3), CovarianceSpherical(np.array([50.0, 30.0, 10.0]), np.array([0.0, 0.0, 30.0]), c2)]
        itype = 3
        avg = np.array([0.0, 0.0, 0.0])
        ival = 0
        nk = 3
        rad = 100
        ntok = 2

        x0s, s, sv, idout, l, K, K0 = cokri(x, x0, cm, itype, avg, block, nd, ival, nk, rad, ntok)

    if testVariof:
        m1 = np.array([[3.0, 6.0, 5.0], [7.0, 2.0, 2.0], [4.0, np.NaN, 0.0]])
        gh11, nh11 = variof1(m1)

        m2 = np.array([[3.0, 6.0, 5.0, 1.0], [7.0, 2.0, 2.0, np.NaN], [2.0, 4.0, np.NaN, 0.0], [1.0, 3.0, 2.0, 0.0]])
        gh22, nh22 = variof1(m2)

        m3 = np.array([[3.0, 6.0, 5.0, 1.0], [7.0, 2.0, 2.0, np.NaN], [2.0, 4.0, np.NaN, 0.0]])
        gh33, nh33 = variof1(m3)

    if testVarioExp:
        x = np.array([[0.1, 0.1, 1.2],
                      [5.1, 3.3, 0.7],
                      [1.2, 7.8, 1.3],
                      [8.8, 5.5, 0.3],
                      [9.9, 1.9, 1.5]])

        y = x[:, 1].flatten()
        v = x[:, 2].flatten()
        x = x[:, 0].flatten()

        nbclas = 3
        lclas = np.array([5.0])
        vdir = np.array([0.0, 45.0])
        vreg = np.array([45.0, 45.0])
        bw = np.array([2.0, 2.0])

        g = varioexp2d(x, y, v, nbclas, lclas, vdir, vreg, bw)

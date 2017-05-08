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
from sqlalchemy import Column, String, PickleType
from data_manager import Base

class Model(Base):
    
    __tablename__ = "Model"
    name       = Column(String, primary_key=True)  # Model's name
    mogs       = Column(PickleType)    # List of mogs contained in the model
    boreholes  = Column(PickleType)    # List of boreholes contained in the model
    grid       = Column(PickleType)  # Model's grid
    tt_covar   = Column(PickleType)  # Model's Traveltime covariance model
    amp_covar  = Column(PickleType)  # Model's Amplitude covariance model
    inv_res    = Column(PickleType)  # Results of inversion
    tlinv_res  = Column(PickleType)  # Time-lapse inversion results
    
    def __init__(self, name= ''):
        self.name       = name  # Model's name
        self.mogs       = []    # List of mogs contained in the model
        self.boreholes  = []    # List of boreholes contained in the model
        self.grid       = None  # Model's grid
        self.tt_covar   = None  # Model's Traveltime covariance model
        self.amp_covar  = None  # Model's Amplitude covariance model
        self.inv_res    = []  # Results of inversion
        self.tlinv_res  = None  # Time-lapse inversion results

    @staticmethod
    def getModelData(model, air, selected_mogs, type1, type2= ''):
        data = np.array([])
        type2 = ''

        tt = np.array([])
        et = np.array([])
        in_vect = np.array([])
        mogs = []
        for i in selected_mogs:
            mogs.append(model.mogs[i])

        if type1 == 'tt':
            fac_dt = 1

            mog = mogs[0]
            ind = np.not_equal(mog.tt, -1).T
            tt, t0 = mog.getCorrectedTravelTimes(air)
            tt = tt.T
            et = fac_dt*mog.f_et*mog.et.T
            in_vect = mog.in_vect.T
            no = np.arange(mog.data.ntrace).T

            if len(mogs) > 1:
                for n in range(1, len(model.mogs)):
                    mog = mogs[n]
                    ind = np.concatenate((ind, np.not_equal(mog.tt, -1).T), axis= 0)
                    tt = np.concatenate((tt, mog.getCorrectedTravelTimes(air)[0].T), axis= 0)
                    et = np.concatenate((et, fac_dt*mog.et*mog.f_et.T), axis= 0)
                    in_vect = np.concatenate((in_vect, mog.in_vect.T), axis= 0)
                    no = np.concatenate((no, np.arange(mog.ntrace + 1).T), axis = 0)

            ind = np.equal((ind.astype(int) + in_vect.astype(int)), 2)

            data = np.array([tt[ind], et[ind], no[ind]]).T


            return data, ind

        if type2 == 'depth':
            data, ind = getModelData(model, air, selected_mogs, type1) # @UndefinedVariable
            mog = mogs[0]
            tt = mog.Tx_z_orig.T
            et = mog.Rx_z_orig.T
            in_vect = mog.in_vect.T
            if len(mogs) > 1:
                for n in (1, len(mogs)):
                    tt = np.concatenate((tt, mogs[n].Tx_z_orig.T), axis= 0)
                    et = np.concatenate((et, mogs[n].Rx_z_orig.T), axis= 0)
                    in_vect = np.concatenate((in_vect, mogs[n].in_vect.T), axis= 0)

            ind = np.equal((ind.astype(int) + in_vect.astype(int)), 2)
            data = np.array([tt[ind], et[ind], no[ind]]).T
            return data, ind









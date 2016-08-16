import numpy as np

class Model:
    def __init__(self, name= ''):
        self.name       = name  # Model's name
        self.mogs       = []    # List of mogs contained in the model
        self.boreholes  = []    # List of boreholes contained in the model
        self.grid       = None  # Model's grid
        self.tt_covar   = None  # Model's Traveltime covariance model
        self.amp_covar  = None  # Model's Amplitude covariance model
        self.inv_res    = None  # Results of inversion
        self.tlinv_res  = None  # Time-lapse inversion results

    @staticmethod
    def getModelData(model, air, selected_mogs, type):
        data = np.array([])
        type2 = ''

        tt = np.array([])
        et = np.array([])
        in_vect = np.array([])
        mogs = []
        for i in selected_mogs:
            mogs.append(model.mogs[i.row()])

        if type == 'tt':
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








import numpy as np

def data_select(data, freq, dt, L= 100, treshold= 5, medfilt_len= 10):

        shape = np.shape(data)
        N, M = shape[0], shape[1]
        std_sig = np.zeros(M).T
        ind_data_select = np.zeros(M, dtype= bool).T
        ind_max = np.zeros(M).T
        nb_p = np.round(1/(dt*freq))
        width = 60
        if medfilt_len>0:
            data = spy.signal.medfilt(data)

        for i in range(M):
            Amax        = np.amax(data[:, i])

            ind1        = np.argmax(data[:, i])

            ind_max[i]  = ind1

            ind         = np.arange(ind1-nb_p, ind1+2*nb_p+1)

            if ind[0] < 1:
                ind = np.arange(1, ind1+width)

            elif ind[-1] < 1:
                ind = np.arange(ind1-width, ind1)



            std_sig[i] = np.std(data[int(ind[0]):int(ind[-1]),i])


        std_noise = np.std(data[-1-L: -1, :])
        SNR = std_sig/std_noise
        ind_data_select[SNR > treshold] = True

        return SNR

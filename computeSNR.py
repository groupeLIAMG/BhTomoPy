import numpy as np
#from detrend_rad import detrend_rad



def compute_SNR(mog):
        SNR = np.ones(mog.data.ntrace)

        max_amps = np.amax(np.abs(detrend_rad(mog.data.rdata)))
        i = np.nonzero(np.abs(detrend_rad(mog.data.rdata)) == max_amps)[0]

        width = 60

        i1 = i - width / 2
        i2 = i + width / 2
        i1[i1 < 1] = 1
        i2[i2 > mog.data.nptsptrc] = mog.data.nptsptrc

        for n in range(mog.data.ntrace):
            SNR[n] = np.std(mog.data.rdata[i1[n]:i2[n], n]) / np.std(mog.data.rdata[:width, n])

        return SNR
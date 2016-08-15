




class Covariance:
    """
    Covariance Base class for Covariance models

    E. Dumas-Lefebvre
    B. Giroux
    2016-08-15
    """
    def __init__(self, r, a, s):
        self.range = r
        self.angle = a
        self.sill = s
        self.type = '' # To be defined by CovarianceModels Class

    def trans(selfsel, cx):
        pass
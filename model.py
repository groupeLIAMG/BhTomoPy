
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


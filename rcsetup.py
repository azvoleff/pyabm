"""
Sets up parameters for a model run. Used to read in settings from any provided 
rc file, and set default values for any parameters that are not provided in the 
rc file.

NOTE: Based off the rcsetup.py functions used in matplotlib.
"""

def validate_float(s):
    'convert s to float or raise'
    try: return float(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to float' % s)

def validate_int(s):
    'convert s to int or raise'
    try: return int(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to int' % s)

def validate_writable_dir(s):
    """Checks that a directory exists and is writable, fails if the 
    directory does not exist or if s is not a string"""

    try:
        s = s + '' #check that it is a string
    except TypeError:
        raise TypeError("%s is not a writable directory"%s)
    if not os.path.exists(s)
        raise IOError("%s is not a writable directory"%s)

    return True

class validate_nseq_float:
    def __init__(self, n):
        self.n = n
    def __call__(self, s):
        'return a seq of n floats or raise'
        if type(s) is str:
            ss = s.split(',')
            if len(ss) != self.n:
                raise ValueError('You must supply exactly %d comma separated values'%self.n)
            try:
                return [float(val) for val in ss]
            except ValueError:
                raise ValueError('Could not convert all entries to floats')
        else:
            assert type(s) in (list,tuple)
            if len(s) != self.n:
                raise ValueError('You must supply exactly %d values'%self.n)
            return [float(val) for val in s]


# Maps keys to values and validation functions
defaultParams = {
    # Model-wide parameters
    'model.timesteps' : [25, validate_int]
    'model.time_interval' : [1, validate_float]
    'model.initial_num_persons' : [5000, validate_int]
    'model.initial_num_households' : [750, validate_int]
    'model.initial_num_neighborhoods' : [65, validate_int]
    'model.datapath' : [get_home_dir(), validate_writable_dir]
    
    # Person agent parameters
    'hazard_death' : [[.2, .03, .1, .2, .3, .6, .7, .8, .98, 1], validate_nseq_float(defaultParams['model.timesteps'])]
    'hazard_birth' : [[0, .03, .1, .2, .3, .6, .7, .8, .98, 1], validate_nseq_float(defaultParams['model.timesteps'])]
    'hazard_marriage' : [[0, 0, .1, .2, .3, .6, .7, .8, .98, 1], validate_nseq_float(defaultParams['model.timesteps'])]

    # Household agent parameters
    'prob_any_non_wood_fuel' : [.5, validate_float]
    'prob_own_house_plot' : [.5, validate_float]
    'prob_own_any_land' : [.5, validate_float]
    'prob_rented_out_land' : [.5, validate_float]

    # Neighborhood agent parameters
    'prob_elec' : [.1, validate_float]

    # Landscape parameters
    'initial_proportion_veg' : [.3, validate_proportion]
    'initial_proportion_ag' : [.3, validate_proportion]
    'initial_proportion_private_infrastructure' : [.1, validate_proportion]
    'initial_proportion_public_infrastructure' : [..05, validate_proportion]
}

# Used for testing whether default values validate properly
if __name__ == '__main__':
    rc = defaultParams
    rc['datapath'][0] = '/'
    for key in rc:
        if not rc[key][1](rc[key][0]) == rc[key][0]:
            print "%s: %s != %s"%(key, rc[key][1](rc[key][0]), rc[key][0])

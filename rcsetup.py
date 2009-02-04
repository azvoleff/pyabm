"""
Sets up parameters for a model run. Used to read in settings from any provided 
rc file, and set default values for any parameters that are not provided in the 
rc file.

NOTE: Based off the rcsetup.py functions used in matplotlib.
"""

import os
import tempfile

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

def validate_unit_interval(s):
    "Checks that s is a number between 0 and 1, inclusive, or raises an error."
    try:
        s = float(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to float'%s)
    if s < 0 and s > 1:
        raise ValueError('"%s" is not between 0 and 1'%s)
    return float(s)

def validate_writable_dir(s):
    """Checks that a directory exists and is writable. Fails if the 
    directory does not exist or if s is not a string"""

    try:
        s = s + '' #check that it is a string
    except TypeError:
        raise TypeError("%s is not a writable directory"%s)
    if not os.path.exists(s):
        raise IOError("%s is not a writable directory"%s)
    try:
        t = tempfile.TemporaryFile(dir=s)
        t.write('1')
        t.close()
    except OSError:
        raise OSError("%s is not a writable directory"%s)
    return s

class validate_nseq_float:
    def __init__(self, n):
        self.n = n
    def __call__(self, s):
        """return a seq of n floats or raises error. If n == -1, then length 
        doesn't matter"""
        if type(s) is str:
            ss = s.split(',')
            if self.n != -1 and len(ss) != self.n:
                raise ValueError('You must supply exactly %d comma separated values'%self.n)
            try:
                return [float(val) for val in ss]
            except ValueError:
                raise ValueError('Could not convert all entries to floats')
        else:
            assert type(s) in (list,tuple)
            if self.n != -1 and len(s) != self.n:
                raise ValueError('You must supply exactly %d values'%self.n)
            return [float(val) for val in s]

def validate_boolean(s):
    if s in [True, False]:
        return s
    else:
        try:
            s + ''
        except TypeError:
            # s is not a string
            raise TypeError("%s is not a boolean"%s)
        else:
            # s is a string
            raise TypeError("'%s' is a string. It should be a boolean (either True or False with no quotes)."%s)

def _get_home_dir():
    """Find user's home directory if possible.
    Otherwise raise error.

    :see:  http://mail.python.org/pipermail/python-list/2005-February/263921.html
    """
    path=''
    try:
        path=os.path.expanduser("~")
    except:
        pass
    if not os.path.isdir(path):
        for evar in ('HOME', 'USERPROFILE', 'TMP'):
            try:
                path = os.environ[evar]
                if os.path.isdir(path):
                    break
            except: pass
    if path:
        return path
    else:
        raise RuntimeError('please define environment variable $HOME')

default_RCfile_docstring = """# Default values of parameters for the Chitwan Valley Non-Spatial Agent-based 
# Model. Values are read in to set defaults prior to initialization of the 
# model by the runModel script.
#
# Alex Zvoleff, aiz2101@columbia.edu"""

# defaultParams maps parameter keys to default values and to validation 
# functions. Any comments after "START OF RC DEFINITION" will be included when 
# the default rc file is build using the write_RCfile function.
##################################
###***START OF RC DEFINITION***###
defaultParams = {
    # Model-wide parameters
    'model.timezero' : [1996, validate_float], # The beginning of the model
    'model.endtime' : [2020, validate_float], # When the model stops
    'model.timestep' : [1, validate_float], # The size of each timestep
    'model.initial_num_persons' : [5000, validate_int],
    'model.initial_num_households' : [750, validate_int],
    'model.initial_num_neighborhoods' : [65, validate_int],
    'model.datapath' : [_get_home_dir(), validate_writable_dir],
    'model.use_psyco': [True, validate_boolean],
    
    # Person agent parameters
    'hazard_birth' : [[0, .03, .1, .2, .3, .6, .7, .8, .98, 1], validate_nseq_float(-1)],
    'hazard_death' : [[.2, .03, .1, .2, .3, .6, .7, .8, .98, 1], validate_nseq_float(-1)],
    'hazard_marriage' : [[0, 0, .1, .2, .3, .6, .7, .8, .98, 1], validate_nseq_float(-1)],

    # Household agent parameters
    'prob_any_non_wood_fuel' : [.5, validate_unit_interval],
    'prob_own_house_plot' : [.5, validate_unit_interval],
    'prob_own_any_land' : [.5, validate_unit_interval],
    'prob_rented_out_land' : [.5, validate_unit_interval],

    # Neighborhood agent parameters
    'prob_elec' : [.1, validate_float],

    # Landscape parameters
    'initial_proportion_veg' : [.3, validate_unit_interval],
    'initial_proportion_ag' : [.3, validate_unit_interval],
    'initial_proportion_private_infrastructure' : [.1, validate_unit_interval],
    'initial_proportion_public_infrastructure' : [.05, validate_unit_interval],
}
###***END OF RC DEFINITION***###
################################

class RcParams(dict):
    """
    A dictionary object including validation

    Validation functions are contained in rcsetup.py.
    """

    validate = dict([ (key, converter) for key, (default, converter) in \
                     defaultParams.iteritems() ])

    def __setitem__(self, key, val):
        try:
            cval = self.validate[key](val)
            dict.__setitem__(self, key, cval)
        except KeyError:
            raise KeyError('%s is not a valid rc parameter.\
See rcParams.keys() for a list of valid parameters.'%key)

def write_RCfile(outputFilename, docstring=None, updated_params=None):
    """Write default rcParams to a file after optionally updateing them from an 
    rcParam dictionary."""

    # TODO: fix this to find the proper path for rcsetup.py
    rcsetupFile = open("rcsetup.py", "r")

    linenum = 0
    line = rcsetupFile.readline()
    while line:
        linenum += 1
        if line == "###***START OF RC DEFINITION***###\n":
            break
        line = rcsetupFile.readline()

    outputLines = []
    defEnded = False # Flag for whether the "END OF RC DEFINITION" block is reached
    line = rcsetupFile.readline()
    while line:
        linenum += 1

        if line == "###***END OF RC DEFINITION***###\n":
            defEnded = True
            break

        # Remove linebreak
        line = line.rstrip("\n")

        # First pull out any comment, store the remaining back in line
        comment = ''.join(line.partition("#")[1:3])
        line = ''.join(line.partition("#")[0])

        # Now pull out key, and strip single quotes, double quotes and blank 
        # spaces
        key = ''.join(line.partition(":")[0].strip("\'\" "))

        # Now pull out value
        value_validation_tuple = line.partition(':')[2].partition("#")[0].strip(", ")
        value = value_validation_tuple.rpartition(",")[0].strip("[]")
        
        outputLines.append((key, value, comment, linenum))

        # TODO: Check for duplicate keys
        #if 
        #    warnings.warn("Duplicate values for %s are provided in rcsetup.py"%key)

        line = rcsetupFile.readline()

    if not defEnded:
        warnings.warn('failed to reach "END OF RC DEFINITION" block')

    # Remove opening and closing braces of the dictionary definition
    del outputLines[0]
    del outputLines[-1]

    ret = RcParams([ (key, default) for key, (default, converter) in \
                    defaultParams.iteritems() ])

    # TODO: Fix this so it works
    # Check keys and values to make sure they validate
#    for (key, value, comment, linenum) in outputLines:
#        # Skip blank lines and comment lines
#        if '' in [key, value]:
#            continue
#        if defaultParams.has_key(key):
#            ret[key] = value # try to convert to proper type or raise
#        else:
#            print >> sys.stderr, """
#Bad key "%s" on line %s in %s.""" % (key, linenum, "rcsetup.py")

    # Finally, write to outputFilename
    outFile = open(outputFilename, "w")
    if docstring == None:
        outFile.writelines(default_RCfile_docstring + "\n\n")
    else:
        outFile.writelines(docstring + "\n\n")

    for (key, value, comment, linenum) in outputLines:
        if key == "" and value == "":
            outFile.write(comment + "\n") # if comment is blank, just writes a blank line to the file
        else:
            if comment != '':
                # precede comment by a blank space
                comment = ' ' + comment
            line = ''.join([key, " : ", value, comment, "\n"])
            outFile.write(line)

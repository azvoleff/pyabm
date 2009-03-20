"""
Sets up parameters for a model run. Used to read in settings from any provided 
rc file, and set default values for any parameters that are not provided in the 
rc file.

NOTE: Based off the rcsetup.py functions used in matplotlib.
"""

import os
import tempfile

import warnings

def validate_float(s):
    'convert s to float or raise'
    try: 
        if type(s) == str:
            return float(eval(s))
        else:
            return float(s)
    except NameError:
        raise ValueError('Could not convert "%s" to float'%s)
    except ValueError:
        raise ValueError('Could not convert "%s" to float'%s)

def validate_int(s):
    'convert s to int or raise'
    try: return int(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to int' % s)

def validate_unit_interval(s):
    "Checks that s is a number between 0 and 1, inclusive, or raises an error."
    s = validate_float(s)
    if s < 0 or s > 1:
        raise ValueError('"%s" is not between 0 and 1'%s)
    return s

def validate_readable_file(s):
    """Checks that a file exists and is readable."""
    if (type(s) != str):
        raise TypeError("%s is not a readable file"%s)
    if not os.path.exists(s):
        raise IOError("%s does not exist"%s)
    try:
        file = open(s, 'r')
        file.readline()
        file.close()
    except OSError:
        raise OSError("error reading file %s"%s)
    return s

def validate_writable_dir(s):
    """Checks that a directory exists and is writable. Fails if the 
    directory does not exist or if s is not a string"""
    if (type(s) != str):
        raise TypeError("%s is not a writable directory"%s)
    if not os.path.exists(s):
        raise IOError("%s does not exist"%s)
    try:
        t = tempfile.TemporaryFile(dir=s)
        t.write('1')
        t.close()
    except OSError:
        raise OSError("cannot write to model output directory %s"%s)
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
                return [validate_float(val) for val in ss]
            except ValueError:
                raise ValueError('Could not convert all entries to floats')
        else:
            assert type(s) in (list,tuple), "%s is not a list or tuple"%(s)
            if self.n != -1 and len(s) != self.n:
                raise ValueError('You must supply exactly %d values'%self.n)
            return [validate_float(val) for val in s]

def validate_boolean(s):
    if s in [True, False]:
        return s
    elif s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    else:
        raise TypeError("%s is not a boolean"%s)

def validate_time_units(s):
    if (type(s) != str):
        raise TypeError("%s is not a valid unit of time"%s)
    if s.lower() in ['months', 'years', 'decades']:
        return s.lower()
    else:
        raise ValueError("%s is not a valid unit of time"%s)

def validate_RandomState(s):
    if s == 'None' or s == None:
        return None
    else:
        return validate_int(s)

def novalidation(s):
    "Performs no validation on object. (used in testing)."
    return s

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

# default_params maps parameter keys to default values and to validation 
# functions. Any comments after "default_params = {" and before the closing 
# brace will be included when the default rc file is build using the 
# write_RC_file function.
##################################
###***START OF RC DEFINITION***###
default_params = {
    # Model-wide parameters
    'model.timezero' : [1996, validate_float], # The beginning of the model
    'model.endtime' : [2020, validate_float], # When the model stops
    'model.timestep' : [1/12., validate_float], # The size of each timestep
    'model.time_units' : ["months", validate_time_units], # The size of each timestep
    'model.RandomState' : [None, validate_RandomState], # Seeds the random number generator (useful for regenerating results later)
    'model.initial_num_persons' : [5000, validate_int],
    'model.initial_num_households' : [750, validate_int],
    'model.initial_num_neighborhoods' : [65, validate_int],
    'model.resultspath' : ["/media/Restricted/chitwanABM_runs", novalidation],
    'model.use_psyco': [True, validate_boolean],
    
    # Location of input data (these are restricted data)
    'input.census_file' : ["/media/Restricted/CVABM_initialization_data/DS0004_export.csv", novalidation],
    'input.relationships_grid_file' : ["/media/Restricted/CVABM_initialization_data/DS0016_export.csv", novalidation],
    'input.households_file' : ["/media/Restricted/CVABM_initialization_data/DS0002_export.csv", novalidation],
    'input.neighborhoods_file' : ["/media/Restricted/CVABM_initialization_data/DS0014_export.csv", novalidation],
    
    # Person agent parameters
    'hazard_time_units': ['decades', validate_time_units], # Specifies the time period for which precalculated hazards are specified
    'hazard_birth' : [[0, .2, .9, .9, .5, .1, 0, 0, 0, 0, 0], validate_nseq_float(-1)],
    'hazard_death' : [[.3, .05, .01, .02, .04, .1, .4, .9, .99, .999, 1], validate_nseq_float(-1)],
    'hazard_marriage' : [[0, .4, .99, .99, .5, .3, .2, .05, .002, .01, .01], validate_nseq_float(-1)],
    'hazard_migration' : [[0, .2, .2, .1, .1, .05, .02, .01, .01, 01], validate_nseq_float(-1)],

    # Household agent parameters
    'prob_any_non_wood_fuel' : [.5, validate_unit_interval],
    'prob_own_house_plot' : [.5, validate_unit_interval],
    'prob_own_any_land' : [.5, validate_unit_interval],
    'prob_rented_out_land' : [.5, validate_unit_interval],

    # Neighborhood agent parameters
    'prob_elec' : [.1, validate_unit_interval],

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
    """
    def __init__(self, *args):
        dict.__init__(self, *args)
        self.validate = dict([ (key, converter) for key, (default, converter) in \
                     default_params.iteritems() ])

        # original_strings stores the unconverted strings representing the 
        # originally input values (prior to conversion). This allows printing to an 
        # rc file the original values without running to problems with precision 
        # from floating point -> string -> floating point conversions
        self.original_strings = {}

    def __setitem__(self, key, val):
        try:
            self.original_strings[key] = str(val)
            cval = self.validate[key](val)
            dict.__setitem__(self, key, cval)
        except KeyError:
            raise KeyError('%s is not a valid rc parameter.\
See rcParams.keys() for a list of valid parameters.'%key)

def write_RC_file(outputFilename, docstring=None, updated_params=RcParams()):
    """Write default rcParams to a file after optionally updating them from an 
    RcParam dictionary. Any keys in updated_params that are not already defined 
    in rcsetup.py are ignored (as rcsetup.py would reject unknown keys anyways 
    when the rc file is read back in)."""

    # TODO: fix this to find the proper path for rcsetup.py
    rcsetup_script = open("rcsetup.py", "r")

    linenum = 0
    line = rcsetup_script.readline()
    while line:
        linenum += 1
        if line == "###***START OF RC DEFINITION***###\n":
            break
        line = rcsetup_script.readline()

    output_lines = [] # Stores lines to output to new rc file
    rcsetup_params = RcParams() # Build an RcParams dictionary object to validate
    defEnded = False # Flag for whether the "END OF RC DEFINITION" block is reached
    line = rcsetup_script.readline()
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
        value = value_validation_tuple.rpartition(",")[0].strip("[]\"\'")
        
        # Validate keys/values
        if key != '' and value != '':
            rcsetup_params[key] = value
            #print "rcsetup_params key: %s, value: %s, origstring: %s"%(key, rcsetup_params[key], rcsetup_params.original_strings[key])
            if key in updated_params.keys():
                #print "updated_params key: %s, value: %s, origstring: %s\n"%(key, updated_params[key], updated_params.original_strings[key])
                new_value = updated_params.original_strings[key]
                conv = updated_params[key]
                output_lines.append((key, new_value, comment, linenum))
        else:
            output_lines.append((key, value, comment, linenum))

        # TODO: Check for duplicate keys
        #if 
        #    warnings.warn("Duplicate values for %s are provided in rcsetup.py"%key)

        line = rcsetup_script.readline()

    if not defEnded:
        warnings.warn('failed to reach "END OF RC DEFINITION" block')

    # Remove opening and closing braces of the dictionary definition
    assert output_lines[0][0] == "default_params = {", "error reading default_params opening brace"
    del output_lines[0]
    assert output_lines[-1][0] == "}", "error reading default_params closing brace"
    del output_lines[-1]

    # Finally, write rc file to outputFilename.
    outFile = open(outputFilename, "w")
    if docstring == None:
        outFile.writelines("%s\n\n"%(default_RCfile_docstring))
    else:
        outFile.writelines("%s\n\n"%(docstring))
    
    for (key, value, comment, linenum) in output_lines:
        if key == "" and value == "":
            outFile.write("%s\n"%(comment)) # if comment is blank, just writes a blank line to the file
        else:
            if comment != '':
                # precede comment by a blank space
                comment = ' ' + comment
            outFile.write("%s : %s %s \n"%(key, value, comment))

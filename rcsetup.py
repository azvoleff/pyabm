"""
Part of Chitwan Valley agent-based model.

Sets up parameters for a model run. Used to read in settings from any provided 
rc file, and set default values for any parameters that are not provided in the 
rc file.

NOTE: Based off the rcsetup.py functions used in matplotlib.

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

import os
import sys
import tempfile
import copy

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
    """
    Checks that a directory exists and is writable. Fails if the directory does 
    not exist or if s is not a string
    """
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
        """
        Return a seq of n floats or raises error. If n == -1, then length 
        doesn't matter.
        """
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
    """
    Find user's home directory if possible. Otherwise raise error.

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
        raise RuntimeError('Error finding user home directory: \
                please define environment variable $HOME')

def read_rcparams_defaults():
    try:
        rcparams_file = open(os.path.join(sys.path[0], "rcparams.default"), "r")
    except IOError:
        raise IOError('could not find rcparams.defaults file')

    linenum = 0
    line = rcparams_file.readline()
    while line:
        linenum += 1
        if line == "###***START OF RC DEFINITION***###\n":
            break
        line = rcparams_file.readline()

    ret = {}
    line = rcparams_file.readline()
    while line:
        linenum += 1

        # Remove linebreak
        line = line.rstrip("\n")

        # First pull out any comment, store the remaining back in line
        #comment = ''.join(line.partition("#")[1:3])
        #line = ''.join(line.partition("#")[0])

        # Now pull out key, and strip single quotes, double quotes and blank 
        # spaces
        key = ''.join(line.partition(":")[0].strip("\'\" "))

        # Now pull out value and converter
        value_validation_tuple = line.partition(':')[2].partition("#")[0].strip(", ")
        value = value_validation_tuple.rpartition(",")[0].strip("[]\"\'")
        converter = value_validation_tuple.rpartition(",")[2].strip("[]\"\' ")

        if key != '' and value != '':
            if ret.has_key(key):
                warnings.warn("Duplicate values for %s are provided in rcsetup.py"%key)
            # Convert 'converter' from a string to a reference to the 
            # validationo object
            converter = eval(converter)
            ret[key] = (value, converter)

        line = rcparams_file.readline()
    return ret

# Load the rcparams_defaults into a dictionary
rcparams_defaults_dict = read_rcparams_defaults()

class RcParams(dict):
    """
    A dictionary object including validation
    """
    def __init__(self, *args):
        dict.__init__(self, *args)
        self.validate = dict([ (key, converter) for key, (default, converter) in \
                     rcparams_defaults_dict.iteritems() ])
        # self.original_value stores the unconverted strings representing the 
        # originally input values (prior to conversion). This allows printing 
        # to an rc file the original values without running into problems with 
        # errors due to machine precision while doing floating point -> string 
        # -> floating point conversions
        self.original_value = {}

    def __setitem__(self, key, val):
        try:
            self.original_value[key] = val
            cval = self.validate[key](val)
            dict.__setitem__(self, key, cval)
        except KeyError:
            raise KeyError('\'%s\' is not a valid rc parameter. \
See default_params.keys() for a list of valid parameters.'%key)

# Convert the rcparams_defaults dictionary into an RcParams instance. This 
# process will also validate that the values in rcparams_defaults are valid by 
# using the validation function specifed in rcparams_defaults to convert each 
# parameter value.
default_params = RcParams()
for key, (default, converter) in rcparams_defaults_dict.iteritems():
        default_params[key] = default

def read_rc_file(fname='chitwanABMrc'):
    """
    Returns an RcParams instance containing the the keys / value combinations 
    read from an rc file.
    """
    # Make a deep copy of the default_params RcParams instance that will then 
    # be updateed with the the values read in from the rc_file
    rcfile_params = RcParams()
    cnt = 0
    for line in file(fname):
        cnt += 1
        strippedline = line.split('#',1)[0].strip()
        if not strippedline: continue
        tup = strippedline.split(':',1)
        if len(tup) !=2:
            warnings.warn('Illegal line #%d\n\t%s\n\tin file "%s"'%\
                          (cnt, line, fname))
            continue
        key, val = tup
        key = key.strip()
        val = val.strip()
        if rcfile_params.has_key(key):
            warnings.warn('Duplicate key in file "%s", line #%d'%(fname,cnt))

        # Validate the values read in from the rc file
        try:
            rcfile_params[key] = val # try to convert to proper type or raise
        except:
            print >> sys.stderr, """
Bad key "%s" on line %d in %s."""%(key, cnt, fname)
    return rcfile_params

# The default string used as the header of rc_files (if an alternative one is 
# not provided).
default_RCfile_docstring = """# Default values of parameters for the Chitwan Valley Non-Spatial Agent-based 
# Model. Values are read in to set defaults prior to initialization of the 
# model by the runModel script.
#
# Alex Zvoleff, aiz2101@columbia.edu"""

def write_RC_file(outputFilename, docstring=None, updated_params={}):
    """
    Write default rcParams to a file after optionally updating them from an 
    RcParam dictionary. Any keys in updated_params that are not already defined 
    in rcsetup.py are ignored (as read_rc_file would reject unknown keys anyways 
    when the rc file is read back in).
    """
    try:
        rcparams_file = open(os.path.join(sys.path[0], "rcparams.default"), "r")
    except IOError:
        raise IOError('could not find rcparams.defaults file')

    linenum = 0
    line = rcparams_file.readline()
    while line:
        linenum += 1
        if line == "###***START OF RC DEFINITION***###\n":
            break
        line = rcparams_file.readline()

    output_lines = [] # Stores lines to output to new rc file
    line = rcparams_file.readline()
    while line:
        linenum += 1

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
        
        if key != '' and value != '':
            # Validate keys / values
            default_params.validate[key](value)
            # Update key value from updated_params
            if key in updated_params.keys():
                value = updated_params.original_value[key]
        output_lines.append((key, value, comment, linenum))

        line = rcparams_file.readline()

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

def get_rc_params():
    """
    Loads rcParams by first starting with the default parameter values from 
    rcparams.default (already stored in the RcParams instance 'default_params', 
    and then by checking for a chitwanABMrc in:
    
        1) the current working directory
        1) the user's home directory
        2) the directory in which the chitwanABM module is located

    If a chitwanABMrc is found, the default_params are updated with the values 
    from the rc file. The rc_params are then returned.
    """
    rc_file_params = None
    for path in [os.getcwd(), _get_home_dir(), sys.path[0]]:
        rc_file = os.path.join(path, "chitwanABMrc")
        if os.path.exists(rc_file):
            rc_file_params = read_rc_file(rc_file)
            print "Using rc file at %s"%(rc_file)
            break
    
    # If an rc file was found, update the default_params with the values from 
    # that rc file.
    if rc_file_params != None:
        for key in rc_file_params.iterkeys():
            default_params[key] = rc_file_params[key]
    else:
        print "No rc file found. Using default model parameters."

    return default_params

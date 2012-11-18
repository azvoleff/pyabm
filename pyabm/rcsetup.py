# Copyright 2012 Alex Zvoleff
#
# This file is part of the pyabm agent-based modeling toolkit.
# 
# pyabm is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# pyabm is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with
# pyabm.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact Alex Zvoleff in the Department of Geography at San Diego State 
# University with any comments or questions. See the README.txt file for 
# contact information.

"""
Sets up parameters for a model run. Used to read in settings from any provided 
rc file, and set default values for any parameters that are not provided in the 
rc file.

.. note:: The rcsetup.py functionality used in ChitwanABM was originally based 
          off of the the rcsetup.py module used in matplotlib.
"""

from __future__ import division

import os
import sys
import tempfile
import copy
import logging
import inspect
from pkg_resources import resource_string

import numpy as np

logger = logging.getLogger(__name__)

class KeyError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def validate_float(s):
    'convert s to float or raise'
    try: 
        if type(s) == str:
            return float(eval(s))
        else:
            return float(s)
    except NameError, ValueError:
        raise ValueError('Could not convert "%s" to float'%s)

def validate_int(s):
    'convert s to int or raise'
    try:
        if type(s) == str:
            ret = int(eval(s))
        else:
            ret = int(s)
    except NameError:
        raise ValueError('Could not convert "%s" to int'%s)
    if ret != float(s):
        raise ValueError('"%s" is not an int'%s)
    return ret

def validate_string(s):
    'convert s to string'
    try:
        if type(s) == str:
            ret = s
        else:
            ret = str(s)
    except NameError:
        raise ValueError('Could not convert "%s" to string'%s)
    if ret != str(s):
        raise ValueError('"%s" is not a string'%s)
    ret = ret.strip("\"'")
    return ret

def validate_unit_interval(s):
    "Checks that s is a number between 0 and 1, inclusive, or raises an error."
    s = validate_float(s)
    if s < 0 or s > 1:
        raise ValueError('"%s" is not on the closed unit interval [0,1]'%s)
    return s

def validate_readable_file(s):
    """Checks that a file exists and is readable."""
    if (type(s) != str):
        raise TypeError("%s is not a readable file"%s)
    if not os.path.exists(s):
        raise IOError("%s does not exist"%s)
    if not os.path.isfile(s):
        raise IOError("%s is not a readable file"%s)
    try:
        file = open(s, 'r')
        file.readline()
        file.close()
    except OSError:
        raise OSError("error reading file %s"%s)
    return s

def validate_readable_file_warning(s):
    """
    Checks that a file exists and is readable. Only logs a warning if the 
    file is not readable (does not raise error).
    """
    if (type(s) != str):
        logger.warn("%s is not a readable file"%s)
        return s
    if not os.path.exists(s):
        logger.warn("%s does not exist"%s)
        return s
    try:
        file = open(s, 'r')
        file.readline()
        file.close()
    except IOError:
        logger.warn("error reading file %s"%s)
    return s

def validate_readable_dir(s):
    """
    Checks that a directory exists and is readable. Fails if the directory does 
    not exist or if s is not a string.
    """
    if (type(s) != str):
        raise TypeError("%s is not a readable directory"%s)
    if not os.path.isdir(s):
        raise TypeError("%s is not a directory"%s)
    try:
        ls = os.listdir(s)
    except:
        raise OSError("cannot read directory %s"%s)
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
        raise OSError("cannot write to directory %s"%s)
    return s

class validate_nseq_float:
    def __init__(self, n):
        self.n = n
    def __call__(self, s):
        'return a seq of n floats or raise'
        if type(s) is str:
            ss = s.strip('( )')
            ss = ss.split(',')
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

class validate_nseq_int:
    def __init__(self, n):
        self.n = n
    def __call__(self, s):
        'return a seq of n ints or raise'
        if type(s) is str:
            ss = s.strip('( )')
            ss = ss.split(',')
            if len(ss) != self.n:
                raise ValueError('You must supply exactly %d comma separated values'%self.n)
            try:
                return [int(val) for val in ss]
            except ValueError:
                raise ValueError('Could not convert all entries to ints')
        else:
            assert type(s) in (list,tuple)
            if len(s) != self.n:
                raise ValueError('You must supply exactly %d values'%self.n)
            return [int(val) for val in s]

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

def validate_random_seed(s):
    if s == 'None' or s == None:
        return None
    else:
        return validate_int(s)

class validate_probability:
    """
    Validates a probability specified as a dictionary where each key is a tuple 
    specifying the interval to which the probability applies (in 
    probability_time_units).  The interval tuple is specified as::

        [lower, upper)

    (closed interval on the lower bound, open interval on the upper), and the 
    value specified for each inteval tuple key is the probability for that 
    interval. 
    
    The 'min', 'max' values passed to the validate_probability function give 
    the minimum (inclusive) and maximum values (exclusive) for which 
    probabilities must be specified.  validate_probability will check that 
    probabilities are specified for all values of t between this minimum and 
    maximum value, including the minimum value ('min') in [min, max) and up to 
    but excluding the maximum value 'max'.
    
    This function validates the probabilities lie on the unit interval, and 
    then returns a dictionary object where there is a key for each age value in 
    the interval specified. Therefore,::

        {(0,2):.6, (2,5):.9}

    would be converted to::

        {0:.6, 1:.6, 2:.9, 3:.9, 4:.9}
    """
    def __init__(self, min, max):
        self.min = min
        self.max = max
    def __call__(self, s):
        error_msg = """Invalid probability parameter dictionary: %s

        probabilities must be specified in a dictionary of key, value pairs in the 
        following format:

            (lower_limit, upper_limit) : probability

        probabilities apply to the interval [lower_limit, upper_limit), including the 
        lower limit, and excluding the upper limit. The units in which the 
        lower and upper limits are specified should be consistent with the 
        units of time specified by the probability_time_units rc parameter."""

        try:
            if type(s) == str:
                input = eval(s)
            else:
                input = s
        except TypeError:
            raise TypeError(error_msg%(s))
        except SyntaxError:
            raise SyntaxError(error_msg%(s))
        if type(input) != dict:
            raise SyntaxError(error_msg%(s))

        probability_dict = {}
        key_converter_tuple = validate_nseq_int(2) 
        for item in input.iteritems():
            # First convert the probability interval tuple (item[0]) from a string 
            # to a length 2 tuple of ints
            # Validate that key is a length 2 tuple
            key = key_converter_tuple(item[0])

            # Now process the key and values, and check that they fall within 
            # the specified overall interval for this probability type
            lower_lim, upper_lim = validate_int(key[0]), validate_int(key[1])
            if lower_lim > upper_lim:
                raise ValueError("lower_lim > upper_lim for probability dictionary key '(%s, %s)'."%(key))
            elif lower_lim == upper_lim:
                raise ValueError("lower_lim = upper_lim for probability dictionary key '(%s, %s)'."%(key))
            probability = validate_unit_interval(item[1])
            for t in xrange(lower_lim, upper_lim):
                if t in probability_dict:
                    raise ValueError("probability is specified twice for dictionary key '%s'."%(t))
                probability_dict[t] = probability
        for key in probability_dict.keys():
            if key < self.min or key >= self.max:
                raise ValueError("A probability is given for a time outside the \
specified overall probability interval.\nA probability is given for time %s, but the overall \
probability interval is [%s, %s)."%(key, self.min, self.max))
        return probability_dict

def validate_prob_dist(s):
    # TODO: Finish documenting this section.
    """
    Validates a probability distribution specified as a dictionary where each 
    key is a tuple specifying the interval to which the probability applies (in 
    probability_time_units). 
    """
    error_msg = """
    Invalid probability distribution parameter tuple: %s

    Probability distributions must be specified in a length two tuple
    in the following format:

        ([a, b, c, d], [1, 2, 3])

    where a, b, c, and d are bin limits, and 1, 2, and 3 are the probabilities 
    assigned to each bin. Notice one more bin limit must be specified than the 
    number of probabilities given (to close the interval).
    """
    try:
        if type(s) == str:
            prob_dist_tuple = eval(s)
        else:
            prob_dist_tuple = s
    except TypeError:
        raise TypeError(error_msg%(s))
    except SyntaxError:
        raise SyntaxError(error_msg%(s))
    if type(prob_dist_tuple) != tuple:
        raise SyntaxError(error_msg%(s))

    if not (len(prob_dist_tuple[0])==2 and type(prob_dist_tuple[1])==int) and \
            (len(prob_dist_tuple[0]) != (len(prob_dist_tuple[1]) + 1)):
                # The first clause of the above if statement is to catch the 
                # case where the probability distribution is over a single 
                # interval.  Here we need to make sure the probability (for 
                # which there is only one value in this case) is stored as a 
                # length 1 tuple as this is the format expected by the 
                # statistics functions.
                raise SyntaxError("Length of probability tuple must be 1 less than the length of the bin limit tuple - error reading %s"%key)

    return prob_dist_tuple

def validate_time_bounds(values):
    """Converts and validates the start and stop time for the model. Checks to 
    ensure consistency, and rejects unlikely inputs, like years < minyear or > 
    maxyear ."""
    minyear, maxyear = 1990, 2201
    values = values.replace(' ', '')
    try:
        values = values.split('),(')
    except IndexError:
        raise IndexError(error_msg)
    if len(values) > 2:
        raise ValueError(error_msg)
    bounds = []
    for date in values:
        date = date.strip('()').split(',')
        bound = []
        if len(date) > 2:
            raise ValueError(error_msg)
        for item in date:
            try:
                bound.append(validate_int(item))
            except ValueError, msg:
                raise ValueError("Invalid date. In model start/stop time, a [year, month] date of \
%s is given. %s"%(date, msg))
        if len(bound) == 2:
            # len(bound)=2 means a year and month are specified, as (year, 
            # month). So validate that the second item in bound, the number of  
            # the month, is between 1 and 12
            if bound[1] < 1 or bound[1] > 12:
                raise ValueError("In model start/stop time, a month number of \
%s is given. The month number must be an integer >=1 and <= 12"%bound[1])
        if bound[0] < minyear or bound[0] > maxyear:
            # These year limits are to avoid accidentally incorrect entries. If 
            # the model is actually supposed to be run beyond these limits, 
            # these limits on the max/min year can be changed.
            raise ValueError("In model start/stop time, a year of \
%s is given. The year must be an integer >=%sand <= %s"%(bound[0], minyear, maxyear))
        bounds.append(bound)
    if len(bounds[0])==1 or len(bounds[1])==1:
        raise ValueError("In model start/stop time, no month is specified.")

    # Check that start and stop dates are valid:
    if (bounds[0][0] == bounds[1][0] and bounds[0][1] >= bounds[1][1]) or \
            (bounds[0][0] > bounds[1][0]):
        raise ValueError("Specified model start time is >= model stop time.")
    return bounds

def novalidation(s):
    "Performs no validation on object. (used in testing)."
    return s

def _get_home_dir():
    """
    Find user's home directory if possible. Otherwise raise error.

    see:  http://mail.python.org/pipermail/python-list/2005-February/263921.html
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

class RcParams(dict):
    """
    A dictionary object including validation
    """
    def __init__(self, validation=True, *args):
        self._validation = validation
        dict.__init__(self, *args)
        self._validation_dict = None
        # self.original_value stores the unconverted strings representing the 
        # originally input values (prior to conversion). This allows printing 
        # to an rc file the original values given by a user or rc file without 
        # running into problems with errors due to machine precision while 
        # doing floating point -> string -> floating point conversions
        self.original_value = {}

    def setup_validation(self, rcparams_defaults_dict):
        self._validation_dict = dict([(key, converter) for key, (default, 
            converter) in rcparams_defaults_dict.iteritems()])

    def __setitem__(self, key, val):
        self.original_value[key] = val
        if self._validation:
            try:
                cval = self._validation_dict[key](val)
                dict.__setitem__(self, key, cval)
            except KeyError, msg:
                raise KeyError('%s is not a valid rc parameter. \
See rcParams.keys() for a list of valid parameters. %s'%(key, msg))
        else:
            dict.__setitem__(self, key, val)

    def validate_items(self):
        for key, val in self.original_value.iteritems():
            try:
                cval = self._validation_dict[key](val)
                dict.__setitem__(self, key, cval)
            except KeyError, msg:
                logger.error('problem processing %s rc parameter. %s'%(key, msg))

def parse_rcparams_defaults(module_name):
    """
    Parses the pyabm rcparams.defaults file as well as the rcparams.defaults 
    file (if any) for the calling module. Returns a list of tuples:

        (filename, linenum, key, value, comment)
    """
    parsed_lines = []
    key_dict = {}
    try:
        rcparams_lines = resource_string(module_name, 'rcparams.default').splitlines()
    except IOError:
        raise IOError('ERROR: Could not open rcparams.defaults file in %s'%module_name)
    logger.debug("Loading rcparams.defaults from %s"%module_name)
    for preamble_linenum in xrange(1, len(rcparams_lines)):
        if rcparams_lines[preamble_linenum] == "###***START OF RC DEFINITION***###":
            break
    for linenum in xrange((preamble_linenum + 1), len(rcparams_lines)):
        # Remove linebreak
        line = rcparams_lines[linenum]
        # Pull out key, and strip single quotes, double quotes and blank 
        # spaces
        comment = ''.join(line.partition("#")[1:3])
        line = ''.join(line.partition("#")[0])
        key = ''.join(line.partition(":")[0].strip("\'\" "))
        # Now pull out value and converter
        value_validation_tuple = line.partition(':')[2].partition("#")[0].strip(", ")
        value = value_validation_tuple.rpartition("|")[0].strip("[]\"\' ")
        converter = value_validation_tuple.rpartition("|")[2].strip("[]\"\' ")
        if key != '':
            if key in key_dict:
                logger.warn("Duplicate values for %s are provided in %s rcparams.default."%(key, module_name))
            # Convert 'converter' from a string to a reference to the 
            # validation object
            converter = eval(converter)
            key_dict[key] = (value, converter)
        parsed_lines.append((module_name, linenum, key, value, comment))
    return parsed_lines, key_dict

def read_rc_file(default_params, fname=os.path.basename(os.getcwd()) +'rc'):
    """
    Returns an RcParams instance containing the the keys / value combinations 
    read from an rc file. The rc file name defaults to the module name plus 'rc'.
    """
    rcfile_params = RcParams(validation=True)
    rcfile_params.setup_validation(default_params)
    cnt = 0
    for line in file(fname):
        cnt += 1
        strippedline = line.split('#',1)[0].strip()
        if not strippedline: continue
        tup = strippedline.split(':',1)
        if len(tup) !=2:
            logger.warn('illegal line #%d in file "%s"'%(cnt, fname))
            continue
        key, val = tup
        key = key.strip()
        val = val.strip()
        if key in rcfile_params:
            logger.warn('duplicate key in file "%s", line #%d'%(fname,cnt))

        # Validate the values read in from the rc file
        try:
            rcfile_params[key] = val # try to convert to proper type or raise
        except Exception:
            logger.warning('Failure while reading rc parameter %s on line %d in %s. Will revert to default parameter value.'%(key, cnt, fname))
    return rcfile_params

class rc_params_management():
    """
    This class manages the RcParams instance used by pyabm and shared by any 
    calling modules.
    """
    def __init__(self):
        self._initialized = False
        self._validated = False
        self._rcParams = None
        self._default_parsed_lines = None
        self._default_rcparams_dict = None
        self.load_default_params(__name__)

    def load_default_params(self, module_name):
        """
        Load the rcparams_defaults into a dictionary, which will be used to tie 
        keys to converters in the definition of the RcParams class.
        
        The function can be called repeatedly to load new defaults (from 
        different modules who share the same rc_params_management instance, for 
        example). If the function is called more than once, any default 
        parameters that are not explicitly overwritten will be left unchanged.
        """
        default_parsed_lines, default_rcparams_dict = parse_rcparams_defaults(module_name)
        if self._default_parsed_lines == None and self._default_rcparams_dict == None:
            self._default_parsed_lines = default_parsed_lines
            self._default_rcparams_dict = default_rcparams_dict
        else:
            self._default_parsed_lines.extend(default_parsed_lines)
            self._default_rcparams_dict.update(default_rcparams_dict)
        # Convert the rcparams_defaults dictionary into an RcParams 
        # instance.  This process will also validate that the values in 
        # rcparams_defaults are valid by using the validation function 
        # specified in rcparams_defaults to convert each parameter value.
        if self._rcParams == None:
            self._rcParams = RcParams(validation=False)
        self._rcParams.setup_validation(self._default_rcparams_dict)
        self._rcParams._validation = False
        for key, (default, converter) in default_rcparams_dict.iteritems():
            try:
                self._rcParams[key] = default
            except Exception, msg:
                raise Exception("ERROR: Problem processing rcparams.default key '%s'. %s"%(key, msg))
        self._rcParams._validation = True

    def is_initialized(self):
        return self._initialized

    def is_validated(self):
        return self._validated

    def validate_params(self):
        self._rcParams.validate_items()
        self._validated = True

    def get_params(self):
        if not self.is_initialized():
            logger.warning("rcparams not yet initialized")
        if not self.is_validated():
            logger.warning("rcparams not yet validated - must call validate_params")
        return self._rcParams

    def initialize(self, module_name, custom_rc_file=None):
        """
        Loads rcParams by first starting with the default parameter values from 
        rcparams.default (already stored in the attribute 'default_params', and 
        then by checking for an rc file in:
            
            1) the path specified by the 'custom_rc_file' parameter
            2) the current working directory
            3) the user's home directory
            4) the directory in which the calling module is located

        The script searches in each of these locations, in order, and reads the 
        first and only the first rc file that is found. If a rc file is found, 
        the default_params are updated with the values from the rc file. The 
        rc_params are then returned.

        The name of the rc file can be specified as a parameter ``rcfile_name`` 
        to the script. If not given, the rc file name defaults to the name of 
        the calling module passed as an input parameter, with an 'rc' suffix.

        Note that this function can be called more than once, in order to 
        initialize different sets of parameters from different rc files.
        """
        rc_file_params = None
        rc_file_paths = [os.getcwd(), _get_home_dir(), sys.path[0]]
        rcfile_name = os.path.split(module_name)[-1] + 'rc'
        rc_file_paths = [os.path.join(path, rcfile_name) for path in rc_file_paths]
        if custom_rc_file != None: rc_file_paths = [custom_rc_file] + rc_file_paths
        for rc_file_path in rc_file_paths:
            if os.path.exists(rc_file_path):
                logger.info("Loading custom rc_file %s"%rc_file_path)
                rc_file_params = read_rc_file(self._default_rcparams_dict, rc_file_path)
                break
        
        self._rcParams._validation = False
        # If an rc file was found, update the default_params with the values 
        # from that rc file.
        if rc_file_params != None:
            for key in rc_file_params.iterkeys():
                self._rcParams[key] = rc_file_params.original_value[key]
                logger.info("custom '%s' parameter loaded"%key)
        else:
            logger.info("no rc file found. Using parameters from rcparams.default")

        # Now run the validation on all the items in the default_params 
        # instance (as values read from rcparams.defaults have not yet been 
        # validated).
        self.validate_params()
        self._rcParams._validation = True
        self._initialized = True

        # Check if a random_seed was loaded from the rcfile. If not (if 
        # random_seed==None), then choose a random random_seed, and store it in 
        # rcParams so that it can be written to a file at the end of model 
        # runs, and saved for later reuse (for testing, etc.).
        if self._rcParams['random_seed'] == None:
            # Seed the random_seed with a known random integer, and save the seed for 
            # later reuse (for testing, etc.).
            self._rcParams['random_seed'] = int(10**8 * np.random.random())
        np.random.seed(int(self._rcParams['random_seed']))
        logger.debug("Random seed set to %s"%int(self._rcParams['random_seed']))

    def write_RC_file(self, outputFilename, docstring=None):
        """
        Write default rcParams to a file after updating them from the currently 
        loaded rcParams dictionary. Any keys in the updated dictionary that are 
        not already defined in the default parameter files (rcparams.defaults) 
        used to build the rcParams dictionary are ignored (as read_rc_file 
        would reject unknown keys anyways when the rc file is read back in).
        """
        # The default string used as the header of rc_files (if an alternative one 
        # is not provided).
        default_RCfile_docstring = """# Default values of parameters for the Chitwan Valley Agent-based Model. Values 
# are read in to set defaults prior to initialization of the model by the 
# runmodel script.
#
# Alex Zvoleff, azvoleff@mail.sdsu.edu"""
        
        if self._default_parsed_lines == None:
            logger.warning("rcparams_defaults have not yet been read into this rc_params_management instance")

        # Finally, write rc file to outputFilename.
        outFile = open(outputFilename, "w")
        if docstring == None:
            outFile.writelines("%s\n\n"%(default_RCfile_docstring))
        else:
            outFile.writelines("%s\n\n"%(docstring))
        
        for (module, linenum, key, value, comment) in self._default_parsed_lines:
            if key == "" and value == "":
                outFile.write("%s\n"%(comment)) # if comment is blank, just write a newline to the file
                continue
            elif comment != '':
                # If there is a comment at the end of a line with a key : value 
                # pair, ensure the comment is preceded by a blank space
                comment = ' ' + comment
            # Update the keyvalues from any rcparams instance handed to the 
            # write_RC_file function:
            if key in self._rcParams:
                value = self._rcParams[key]
            outFile.write("%s : %s%s\n"%(key, value, comment))
        outFile.close()

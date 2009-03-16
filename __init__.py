"""
Part of Chitwan Valley agent-based model.

Sets up rc parameters so that they can be loaded and reused by other parts of 
the model.

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

import os
import sys
import warnings

import numpy as np

from rcsetup import defaultParams
from rcsetup import RcParams

class IDError(Exception):
    pass

class IDGenerator(object):
    """A generator class for consecutive unique ID numbers. IDs can be assigned 
    externally by other code, and tracked in this class with the use_ID 
    function. The use_ID function will raise an error if called with an ID that has 
    already been assigned."""
    def __init__(self):
        # Start at -1 so the first ID will be 0
        self._last_ID = -1
        self._used_IDs = []

    def reset(self):
        self.__init__()

    def next(self):
        newID = self._last_ID + 1
        while newID in self._used_IDs:
            newID += 1
        self._last_ID = newID
        self._used_IDs.append(newID)
        return self._last_ID

    def use_ID(self, used_ID):
        # TODO: This will get very slow when dealing with large numbers of IDs. 
        # It might be better to just set _last_ID to the maximum value in 
        # _used_IDs whenever the use_ID function is called
        if used_ID in self._used_IDs:
            raise IDError("ID %s has already been used"%(used_ID))
        self._used_IDs.append(used_ID)

def boolean_choice(trueProb=.5):
    """A function that returns true or false depending on whether a randomly
    drawn float is less than trueProb"""
    if np.random.rand() < trueProb:
        return True
    else:
        return False

def _is_writable_dir(p):
    """
    p is a string pointing to a putative writable dir -- return True p
    is such a string, else False
    """
    try: p + ''  # test is string like
    except TypeError: return False
    try:
        t = tempfile.TemporaryFile(dir=p)
        t.write('1')
        t.close()
    except OSError: return False
    else: return True

fname = 'chitwanABMrc' #TODO: write a function to find this
def rc_params(fname):
    'Return the default params updated from the values in the rc file'

    if not os.path.exists(fname):
        warnings.warn('could not find rc file; returning defaults')
        ret = RcParams([ (key, default) for key, (default, converter) in \
                        defaultParams.iteritems() ])
        return ret

    cnt = 0
    rc_temp = {}
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
        if key in rc_temp:
            warnings.warn('Duplicate key in file "%s", line #%d'%(fname,cnt))
        rc_temp[key] = (val, line, cnt)

    ret = RcParams([ (key, default) for key, (default, converter) in \
                    defaultParams.iteritems() ])

    for key, (val, line, cnt) in rc_temp.iteritems():
        if defaultParams.has_key(key):
            ret[key] = val # try to convert to proper type or raise
        else:
            print >> sys.stderr, """
Bad key "%s" on line %d in %s.""" % (key, cnt, fname)

    return ret

# this is the instance used by the model
rcParams = rc_params(fname)

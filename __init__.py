"""
Part of Chitwan Valley agent-based model.

Sets up rc parameters so that they can be loaded and reused by other parts of 
the model.

Alex Zvoleff, azvoleff@mail.sdsu.edu
"""

from rcsetup import defaultParams

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

def rc_params(fname):
    'Return the default params updated from the values in the rc file'

    if not os.path.exists(fname):
        message = 'could not find rc file; returning defaults'
        ret = RcParams([ (key, default) for key, (default, converter) in \
                        defaultParams.iteritems() ])
        warnings.warn(message)
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
Bad key "%s" on line %d in
%s.""" % (key, cnt, fname)

    # datapath stores the directory in which to save model output
    if ret['datapath'] is None:
        ret['datapath'] = get_data_path()

    return ret

# this is the instance used by the model
rcParams = rc_params(fname)

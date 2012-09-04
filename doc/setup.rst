pyabm Installation Instructions
===============================================================================

Dependencies
_______________________________________________________________________________

Python
-------------------------------------------------------------------------------

pyabm has been tested to be functional on Linux, Windows 7, and 
Mac OS 10.6.4. The toolkit needs a standard Python installation (2.7.x)
along with several Python dependencies:
    
- Numpy - Numpy is required.

- Matplotlib - Matplotlib is required (to enable the automatic plotting of the 
  results of each model run).

- OGR - OGR is required to output shapefiles of neighborhoods locations, and to 
  process input mask files and world files.

Git
-------------------------------------------------------------------------------

Git is required for downloading the development versions of pyabm, and is also 
used to track and output the version of pyabm used for a model run. On Linux 
Git can be installed from your standard package manager. On Windows, download 
msysgit from http://code.google.com/p/msysgit/. For Mac OS, see 
http://code.google.com/p/git-osx-installer/downloads/list.

Installation
_______________________________________________________________________________

To install the toolkit, download the stable version of the code from the 
`Python Package Index (PyPI) <http://pypi.python.org/pypi/pyabm>`_.

The latest version of the code (unstable) is available as a `zipped snapshot 
from Github <https://github.com/azvoleff/pyabm/zipball/master>`_.

You can also `browse the source at GitHub 
<https://github.com/azvoleff/pyabm>`_.

The development source can also be downloaded via git from::
    git://github.com/azvoleff/pyabm.git

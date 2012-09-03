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

Model Installation
_______________________________________________________________________________

To get the toolkit, simply download the latest stable version of the 
code from::
    http://rohan.sdsu.edu/~zvoleff/research/pyabm.php

The development snapshot (latest version of the code, but it may not always 
be functional) can be downloaded from::
    http://git.azvoleff.com/pyabm/snapshot

The development source can also be downloaded via git from::
    git://git.azvoleff.com/pyabm

To install the pyabm toolkit, simply unzip the code into a folder on 
your computer.  After installing Python and the dependencies listed above, 
you will need to add the folder containing the model to your computer's 
Python path so that the code modules will load correctly.

Adding pyabm directory to Python path on Linux and Mac OS:
-------------------------------------------------------------------------------

On Linux and Mac OS, you will need to add a line to your user 
profile telling Python where the pyabm files are located. You can 
do this one of two ways. To temporarily add the pyabm path to your 
Python path, open XTerm and type::
    export PYTHONPATH=/path/to/pyabm/folder

Replace "/path/to/pyabm/folder" with the correct full path to the 
pyabm folder. For example, if the code is on your desktop, this 
might be "/Users/azvoleff/Desktop/pyabm" on a Mac, or 
"/home/azvoleff/Desktop/pyabm" on Linux.

To make this change permanent, add the line::
    export PYTHONPATH=/path/to/pyabm/folder
to the ".profile" file in your home directory.

Adding pyabm directory to Python path on Windows XP:
-------------------------------------------------------------------------------

Adding pyabm directory to Python path on Windows 7:
-------------------------------------------------------------------------------

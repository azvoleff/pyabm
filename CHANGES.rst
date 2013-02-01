=====================
pyabm Changelog
=====================

Version 0.3.3 - 2013/02/01
___________________________

New Features
------------
- Make GDAL an optional dependency.
- Deprecate ArcGIS support.
- Allow using SSL for email sending.
- Allow setting batch_run_python_path to none (disables the threaded batch run 
  script).
- Add validate_string_list function to rcsetup.py.

Bug Fixes
------------
- Ensure package data (rcparams.default) is correctly installed.
- Only attempt a git diff when in a git repo.


Version 0.3.2 - 2012/11/19
___________________________

- Prepare for Python 3.
- Add rc parameter to force ArcGIS or GDAL/OGR (though ArcGIS usage is 
  currently disabled until a future version of PyABM).
- Store PyABM version in __version__ in __init__.py
- Set git, Rscript, and tail binary paths to None as default.
- Add example pyabmrc files: pyabmrc.linux and pyabmrc.windows
- Move git functions into PyABM utility module
- Other miscellaneous bug fixes

Version 0.3.2 - 2012/11/19
___________________________

- Prepare for Python 3.
- Add rc parameter to force ArcGIS or GDAL/OGR (though ArcGIS usage is 
  currently disabled until a future version of PyABM).
- Store PyABM version in __version__ in __init__.py
- Set git, Rscript, and tail binary paths to None as default.
- Add example pyabmrc files: pyabmrc.linux and pyabmrc.windows
- Move git functions into PyABM utility module
- Other miscellaneous bug fixes

Version 0.3.1 - 2012/09/04
___________________________

- Release for PIRE 2011.

Version 0.3 - 2012/09/04
_________________________

- Release for PIRE 2011.

Version 0.2 - 2010/08/11
_________________________

- Release for PIRE 2010.

Version 0.1 - 2009/08/20
_________________________

- Release for PIRE 2009.

#!/usr/bin/python
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
# See the README.rst file for author contact information.
"""
Contains functions to input and output data to various formats. Also attempts 
to load GDAL to handle geospatial data, logging a warning if GDAL is not 
available.
"""

import sys
import logging

logger = logging.getLogger(__name__)

from pyabm import rc_params
rcParams = rc_params.get_params()

try:
    from file_io_ogr import *
except ImportError:
    logger.warning("Failed to load GDAL/OGR. Cannot process spatial data.")

def write_point_process(nodes, outputFile):
    'Writes input node instances to a text file in R point-process format.'
    ofile = open(outputFile, "w")
    # Calculate bounding box:
    xvals = []
    yvals = []
    for node in nodes.values():
        xvals.append(node.getX())
        yvals.append(node.getY())
    xl = min(xvals)
    xu = max(xvals)
    yl = min(yvals)
    yu = max(yvals)
    ofile.write(str(len(nodes)))
    ofile.write("\n***R spatial point process***\n" %vars())
    ofile.write("%(xl).11e %(xu).11e %(yl).11e %(yu).11e 1\n" %vars())
    for x, y in zip(xvals, yvals):
        ofile.write("%(x).11e %(y).11e\n" %vars())
    ofile.close()
    return 0

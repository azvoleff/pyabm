#!/usr/bin/python
# Copyright 2011 Alex Zvoleff
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
Chooses either file_io_arcgis.py or file_io_ogr.py to handle shapefile i/o.
Returns an error if neither is available.
"""

import sys
import logging

logger = logging.getLogger(__name__)

from pyabm import rc_params
rcParams = rc_params.get_params()

if rcParams['geoprocessor'].lower() == 'arcgis':
    try:
        from file_io_arcgis import *
    except:
        logger.error("Failed to load ArcGIS geoprocessor. Cannot process spatial data. If GDAL/OGR is installed, set 'geoprocessor' rcparam to 'ArcGIS'.")
elif rcParams['geoprocessor'].lower() == 'gdal/ogr':
    try:
        from file_io_ogr import *
    except:
        logger.error("Failed to load GDAL/OGR. Cannot process spatial data. If ArcGIS is installed, set 'geoprocessor' rcparam to 'ArcGIS'.")
else:
    logger.error("Unknown option %s for geoprocessor rcparam"%rcParams['geoprocessor'])

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

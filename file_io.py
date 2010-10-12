#!/usr/bin/python
"""
Chooses either file_io_arcgis.py or file_io_ogr.py to handle shapefile i/o.
Returns an error if neither is available.

Alex Zvoleff, aiz2101@columbia.edu
"""

import sys

try:
    from file_io_arcgis import *
except:
    try:
        from file_io_ogr import *
    except ImportError:
        print "ERROR: failed to load ArcGIS or OGR. Cannot process shapefiles."

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

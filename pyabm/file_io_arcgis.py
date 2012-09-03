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
Functions for reading coordinate and segment files from ArcGIS, and for
converting generated networks into an ArcGIS coverage or shapefile. Also
handles writing network statistics fields to a given shapefile
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

import arcgisscripting
gp = arcgisscripting.create()

def convertToShpUnits(shapefile, input):
    'Converts input units to match linear units of datasource.'
    #TODO: Fix this function so it actually handles conversions, rather
    # than just throwing an error
    inputLength, inputUnits = input.split()
    inputUnits = inputUnits.lower()
    desc = gp.Describe(shapefile)
    shpUnits = desc.SpatialReference.LinearUnitName.lower()
    if shpUnits != inputUnits and shpUnits + 's' != inputUnits:
        logger.error("Shapefile units do not match input units")
        return 1
    else:
        return float(inputLength)

def getFieldType(fieldValue):
    'Returns ArcGIS field type appropriate for the given value'
    if type(fieldValue) == float:
        return 'DOUBLE'
    elif type(fieldValue) == int:
        return 'LONG'
    elif type(fieldValue) == str:
        return 'TEXT'

def readNodesFromShp(shapefile):
    'Reads nodes and node weights from a point shapefile.'
    rows = gp.searchCursor(shapefile)
    desc = gp.describe(shapefile)
    nodes = {}
    row = rows.next()
    while row:
        feat = row.GetValue(desc.ShapeFieldName)
        weight = row.getValue("Weight")
        FID = row.getValue("FID")

        pt = feat.getPart(0)
        #part.reset()
        #pt = part.next()
        nodes[FID] = network.Node(FID, pt.x, pt.y, weight)
        row = rows.next()
    del rows # ensure cursor closes
    return nodes

def readNetFromShp(inputShapefile):
    'Reads segs and nodes from the given shapefile'
    rows = gp.searchCursor(inputShapefile)
    desc = gp.describe(inputShapefile)
    net = network.Network()
    row = rows.next()
    while row:
        feat = row.GetValue(desc.ShapeFieldName)
        ptIDs = [row.getValue("pt1"), row.getValue("pt2")]
        ptWeights = [row.getValue("pt1Weight"), row.getValue("pt2Weight")]
        length = row.getValue("Length")
        FID = row.getValue("FID")

        # read nodes
        part = feat.getPart(0)
        part.reset()
        pt = part.next()
        nodes = []
        for n in xrange(2):
            nodes.append(network.Node(ptIDs[n], pt.x, pt.y, ptWeights[n]))
            pt = part.next()
        row = rows.next()
        net.addSeg(network.Seg(FID, nodes[0], nodes[1], length))
    del rows # ensure cursor closes
    return net
    
def writeFieldToShp(shapefile, fieldValues, field):
    'Writes a field (provided as a dictionary by FID) to a shapefile.'
    fields = gp.listFields(shapefile, field)
    field_found = fields.next()
    if not field_found:
        fieldType = getFieldType(fieldValues.values()[0])
        gp.addField(shapefile, field, fieldType) 
    rows = gp.updateCursor(shapefile)
    row = rows.next()
    while row:
        FID = row.getValue("FID")
        try:
            thisFID = fieldValues[FID]
        except KeyError:
            pass
        else:
            row.setValue(field, thisFID)
            rows.updateRow(row)
        row = rows.next()
    del rows
    return 0

def readFieldFromShp(shapefile, field):
    'Reads field values from a shapefile and returns them as a dictionary by FID.'
    rows = gp.searchCursor(shapefile)
    desc = gp.describe(shapefile)
    row = rows.next()
    fieldValues = {}
    while row:
        FID = row.getValue("FID")
        fieldValue = row.getValue(field)
        fieldValues[FID] = fieldValue
        row = rows.next()
    del rows # ensure cursor closes
    return fieldValues

def genShapefile(network, projFile, outputShape):
    'Generates a shapefile from a network class instance.'
    if not os.path.exists(projFile): 
        gp.addError(projFile + " does not exist")
        return 1
    rootDir, fc = os.path.split(outputShape)
    gp.CreateFeatureclass_management(rootDir, fc, 'POLYLINE')

    # setup fields
    lengthField = "Length"
    gp.addfield(outputShape, lengthField, "FLOAT") 
    netIDField = "netID"
    gp.addfield(outputShape, netIDField, "LONG") 
    pt1Field = "pt1"
    gp.addfield(outputShape, pt1Field, "LONG") 
    pt2Field = "pt2"
    gp.addfield(outputShape, pt2Field, "LONG") 
    pt1WeightField = "pt1Weight"
    gp.addfield(outputShape, pt1WeightField, "FLOAT") 
    pt2WeightField = "pt2Weight"
    gp.addfield(outputShape, pt2WeightField, "FLOAT") 
    gp.deleteField_management(outputShape,"Id")
    
    # get information about the new featureclass for later use
    outDesc = gp.describe(outputShape)
    shapefield = outDesc.ShapeFieldName

    lineArray = gp.createobject("Array")
    point = gp.createobject("Point")
    rows = gp.insertCursor(outputShape)
    row = rows.newrow()
    for segment in network.getEdges():
        node1, node2 = segment.getNodes()
        row.SetValue(netIDField, int(network.getNetID(node1)))
        row.SetValue(lengthField, segment.getWeight())
        row.SetValue(pt1Field, node1.getID())
        row.SetValue(pt2Field, node2.getID())
        row.SetValue(pt1WeightField, node1.getWeight())
        row.SetValue(pt2WeightField, node2.getWeight())
        for n, node in zip(xrange(2), [node1, node2]):
            point.id = n
            point.x = node.getX()
            point.y = node.getY()
            lineArray.add(point)
        row.SetValue(shapefield, lineArray)
        rows.insertrow(row)
        lineArray.removeall()
        row = rows.newrow()
    del rows # ensure cursor closes
    gp.defineprojection_management(outputShape, projFile)
    return 0

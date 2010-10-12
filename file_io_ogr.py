#!/usr/bin/python
"""
Functions for reading coordinate and segment files from ArcGIS, and for
converting generated networks into an ArcGIS coverage or shapefile. Also
handles writing network statistics fields to a given shapefile. Uses OGR
to process shapefiles.

Alex Zvoleff, aiz2101@columbia.edu
"""

import sys
import os

try:
    from osgeo import ogr
except ImportError:
    import ogr

try:
    from osgeo import osr
except ImportError:
    import osr

def getFieldType(fieldValue):
    'Returns OGR field type appropriate for the given value'
    if type(fieldValue) == float:
        return ogr.OFTReal
    elif type(fieldValue) == int:
        return ogr.OFTInteger
    elif type(fieldValue) == str:
        return ogr.OFTString

def write_NBH_shapefile(neighborhoods, output_file):
    'Generates a shapefile from a network class instance.'
    shpDriver = ogr.GetDriverByName('ESRI Shapefile')
    ds = shpDriver.CreateDataSource(output_file)
    
    # By default create the polygon shapefile in WGS-84 - UTM 44 North
    outcs = osr.SpatialReference()
    outcs.SetProjCS("UTM 44N (WGS84)")
    outcs.SetWellKnownGeogCS("WGS84")
    outcs.SetUTM(44, True)
    layer = ds.CreateLayer('ChitwanABM', srs=outcs, geom_type=ogr.wkbPoint)

    # setup fields
    NID_field = ogr.FieldDefn("NID", ogr.OFTInteger)
    RID_field = ogr.FieldDefn("RID", ogr.OFTInteger)
    agveg_field = ogr.FieldDefn("agveg", ogr.OFTReal)
    nonagveg_field = ogr.FieldDefn("nonagveg", ogr.OFTReal)
    pubbldg_field = ogr.FieldDefn("pubbldg", ogr.OFTReal)
    privbldg_field = ogr.FieldDefn("privbldg", ogr.OFTReal)
    other_field = ogr.FieldDefn("other", ogr.OFTReal)
    total_area_field = ogr.FieldDefn("total_area", ogr.OFTReal)
    perc_agveg_field = ogr.FieldDefn("perc_agveg", ogr.OFTReal)
    perc_veg_field = ogr.FieldDefn("perc_veg", ogr.OFTReal)
    perc_bldg_field = ogr.FieldDefn("perc_bldg", ogr.OFTReal)

    layer.CreateField(NID_field)
    layer.CreateField(RID_field)
    layer.CreateField(agveg_field)
    layer.CreateField(nonagveg_field)
    layer.CreateField(pubbldg_field)
    layer.CreateField(privbldg_field)
    layer.CreateField(other_field)
    layer.CreateField(total_area_field)
    layer.CreateField(perc_agveg_field)
    layer.CreateField(perc_veg_field)
    layer.CreateField(perc_bldg_field)

    # write features to shapefile
    for neighborhood in neighborhoods:
        new_feature = ogr.Feature(feature_def = layer.GetLayerDefn())

        new_feature.SetField("NID", neighborhood.get_ID())
        new_feature.SetField("RID", neighborhood.get_parent_agent().get_ID())
        new_feature.SetField("agveg", neighborhood._land_agveg)
        new_feature.SetField("nonagveg", neighborhood._land_nonagveg)
        new_feature.SetField("pubbldg", neighborhood._land_pubbldg)
        new_feature.SetField("privbldg", neighborhood._land_privbldg)
        new_feature.SetField("other", neighborhood._land_other)

        total_area = neighborhood._land_agveg + neighborhood._land_nonagveg + \
                neighborhood._land_pubbldg + neighborhood._land_privbldg + \
                neighborhood._land_other
        percent_agveg = neighborhood._land_agveg / total_area
        percent_veg = (neighborhood._land_agveg + neighborhood._land_nonagveg) \
                / total_area
        percent_bldg = (neighborhood._land_privbldg + neighborhood._land_pubbldg) \
                / total_area

        new_feature.SetField("total_area", total_area)
        new_feature.SetField("perc_agveg", percent_agveg)
        new_feature.SetField("perc_veg", percent_veg)
        new_feature.SetField("perc_bldg", percent_bldg)

        x, y = neighborhood.get_coords()
        wkt = 'Point(%f %f)' %(x, y)
        geom = ogr.CreateGeometryFromWkt(wkt)
        new_feature.SetGeometry(geom)

        layer.CreateFeature(new_feature)
    ds.Destroy()

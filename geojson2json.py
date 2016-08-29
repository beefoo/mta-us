# -*- coding: utf-8 -*-

# Description: converts geojson file to svg
# Example usage:
#   python geojson2svg.py -gf data/nycboroughboundaries.geojson

import argparse
import json
import os
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-w', dest="WIDTH", default="800", help="Width of SVG")
parser.add_argument('-gf', dest="GEOJSON_INPUT_FILE", default="data/nycboroughboundaries.geojson", help="Path to GeoJSON file")
parser.add_argument('-pc', dest="PROPERTY_CLASSNAME", default="borough", help="Feature property that should be used as path classname")

# init input
args = parser.parse_args()
WIDTH = int(args.WIDTH)

# read geojson
features = []
with open(args.GEOJSON_INPUT_FILE) as f:
    geojson = json.load(f)
    features = geojson['features']

# find min/max lat/lng
lats = []
lngs = []
for feature in features:
    for path in feature['geometry']['coordinates']:
        for latlng in path:
            lats.append(-1*latlng[0])
            lngs.append(latlng[1])
minLat = min(lats)
maxLat = max(lats)
minLng = min(lngs)
maxLng = max(lngs)

for feature in features:
    className = feature['properties'][args.PROPERTY_CLASSNAME]
    attr = 'class="%s"' % className
    coordinates = feature['geometry']['coordinates']
    for path in coordinates:
        for latlng in path:
            lat = latlng[0]
            lng = latlng[1]

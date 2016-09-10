# -*- coding: utf-8 -*-

# Description: converts geojson file to json
# Example usage:
#   python getBoroughBoundaries.py

import argparse
import json
import math
import os
import re
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-gf', dest="GEOJSON_INPUT_FILE", default="data/nycboroughboundaries.geojson", help="Path to GeoJSON file")
parser.add_argument('-jf', dest="JSON_OUTPUT_FILE", default="data/nycboroughboundaries.json", help="Path to output JSON file")
parser.add_argument('-pl', dest="PROPERTY_LABEL", default="borough", help="Feature property that should be used as path label")

# init input
args = parser.parse_args()

# string to identifier
def strToId(s):
    s = s.lower()
    # Remove invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '_', s)
    # Remove leading characters until we find a letter or underscore
    s = re.sub('^[^a-zA-Z_]+', '_', s)
    return s

# read geojson
features = []
with open(args.GEOJSON_INPUT_FILE) as f:
    geojson = json.load(f)
    features = geojson['features']

print "Found %s features" % len(features)

# loop through each feature
jsonFeatures = []
for feature in features:
    label = feature['properties'][args.PROPERTY_LABEL]
    identifier = strToId(label)
    coordinates = feature['geometry']['coordinates']
    the_index = next((i for (i, f) in enumerate(jsonFeatures) if f["id"] == identifier), len(jsonFeatures))
    if the_index >= len(jsonFeatures):
        jsonFeatures.append({
            "id": identifier,
            "label": label,
            "polygons": []
        })
    for path in coordinates:
        jsonPolygon = []
        for lnglat in path:
            jsonPolygon.append(lnglat)
        jsonFeatures[the_index]["polygons"].append(jsonPolygon)

# write to file
with open(args.JSON_OUTPUT_FILE, 'w') as f:
    json.dump({
        "boroughs": jsonFeatures
    }, f)
    print "Successfully wrote data to file: %s" % args.JSON_OUTPUT_FILE

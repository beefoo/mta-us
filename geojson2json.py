# -*- coding: utf-8 -*-

# Description: converts geojson file to json
# Example usage:
#   python geojson2json.py -gf data/nycboroughboundaries.geojson -jf data/nycboroughboundaries.json

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

# interpolate
def lerp(a, b, amt):
    return a + (b - a) * amt

# limit
def lim(a, a0, a1):
    if a < a0:
        return a0
    elif a > a1:
        return a1
    else:
        return a

# normalize
def norm(a, a0, a1):
    return lim((a-a0) / (a1-a0), 0, 1)

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
        for lnglat in path:
            lngs.append(lnglat[0])
            lats.append(lnglat[1])
minLat = min(lats)
maxLat = max(lats)
minLng = min(lngs)
maxLng = max(lngs)
ratio = 1.0 * (maxLng-minLng) / (maxLat-minLat)
# ratio = 1.0
print "Found %s features with boundaries (%s, %s, %s, %s) and ratio (%s:1)" % (len(features), maxLat, minLat, minLng, maxLng, ratio)

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
            "paths": []
        })
    for path in coordinates:
        jsonPath = []
        for lnglat in path:
            lng = lnglat[0]
            lat = lnglat[1]
            y = norm(lat, minLat, maxLat)
            x = norm(lng, minLng, maxLng)
            jsonPath.append([x, 1.0-y])
        jsonFeatures[the_index]["paths"].append(jsonPath)

# write to file
with open(args.JSON_OUTPUT_FILE, 'w') as f:
    json.dump({
        "aspect_ratio": ratio,
        "features": jsonFeatures
    }, f)
    print "Successfully wrote data to file: %s" % args.JSON_OUTPUT_FILE

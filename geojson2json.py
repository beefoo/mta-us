# -*- coding: utf-8 -*-

# Description: converts geojson file to svg
# Example usage:
#   python geojson2json.py -gf data/nycboroughboundaries.geojson

import argparse
import json
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
        for latlng in path:
            lats.append(-1*latlng[0])
            lngs.append(latlng[1])
minLat = min(lats)
maxLat = max(lats)
minLng = min(lngs)
maxLng = max(lngs)
print "Found %s features with boundaries (%s, %s, %s, %s)" % (len(features), -1*maxLat, -1*minLat, minLng, maxLng)

# loop through each feature
jsonFeatures = []
for feature in features:
    label = feature['properties'][args.PROPERTY_LABEL]
    coordinates = feature['geometry']['coordinates']
    for path in coordinates:
        jsonFeature = {
            "id": strToId(label),
            "label": label
        }
        jsonPath = []
        for latlng in path:
            lat = -1*latlng[0]
            lng = latlng[1]
            y = norm(lat, minLat, maxLat)
            x = norm(lng, minLng, maxLng)
            jsonPath.append([x, y])
        jsonFeature["path"] = jsonPath
        jsonFeatures.append(jsonFeature)

# write to file
with open(args.JSON_OUTPUT_FILE, 'w') as f:
    json.dump(jsonFeatures, f)
    print "Successfully wrote data to file: %s" % args.JSON_OUTPUT_FILE

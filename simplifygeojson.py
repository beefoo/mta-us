# -*- coding: utf-8 -*-

# Description: simplifies the lines in a geojson file
# Example usage:
#   python simplifygeojson.py -if data/nycsubway.geojson -of data/nycsubway_simplified_%s.geojson -r 0.1 -mp 10
#   python simplifygeojson.py -if data/nycboroughs.geojson -of data/nycboroughs_simplified_%s.geojson -r 0.3
#   python simplifygeojson.py -if data/nycparks.geojson -of data/nycparks_simplified_%s.geojson -r 0.1

import argparse
import json
from polysimplify import VWSimplifier

# input
parser = argparse.ArgumentParser()
parser.add_argument('-if', dest="INPUT_FILE", default="data/nycsubway.geojson", help="Path to input geojson file")
parser.add_argument('-of', dest="OUTPUT_FILE", default="data/nycsubway_simplified_%s.geojson", help="Path to output geojson file")
parser.add_argument('-r', dest="SIMPLIFY_PERCENT", default="0.1", type=float, help="Target percent of points from existing points")
parser.add_argument('-mp', dest="MIN_POINTS", default="10", type=int, help="Minimum number of points")

# init input
args = parser.parse_args()
MIN_POINTS = args.MIN_POINTS

# read geojson file
geojson = {}
with open(args.INPUT_FILE) as f:
    geojson = json.load(f)

# simplify a line
def simplify(line, percent):
    global MIN_POINTS
    lineLen = len(line)
    minLen = min([MIN_POINTS, lineLen])
    simplifier = VWSimplifier(line)
    targetLen = max([int(round(lineLen*percent)), minLen])
    simplified = simplifier.from_number(targetLen)
    return simplified.tolist()

# recursively simplify arr of lines
def simplifyRecursive(arr, percent):
    # this is a line
    if isinstance(arr[0], list) and isinstance(arr[0][0], float):
        return simplify(arr, percent)

    # this is an array of lines
    elif isinstance(arr[0], list):
        results = []
        for subArr in arr:
            result = simplifyRecursive(subArr, percent)
            results.append(result)
        return results

# retrieve geojson features
features = geojson['features']
featureLen = len(features)
print "Found %s features in %s" % (len(features), args.INPUT_FILE)
for i, feature in enumerate(features):
    # retrieve feature coordinates
    coordinates = feature['geometry']['coordinates']
    simplifiedCoordinates = simplifyRecursive(coordinates, args.SIMPLIFY_PERCENT)
    geojson['features'][i]['geometry']['coordinates'] = simplifiedCoordinates
    print "Simplified feature %s of %s" % (i+1, featureLen)

# write new geojson
filename = args.OUTPUT_FILE % args.SIMPLIFY_PERCENT
with open(filename, 'w') as f:
    json.dump(geojson, f)

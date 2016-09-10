# -*- coding: utf-8 -*-

# Description: converts json file to svg
# Example usage:
#   python json2svg.py -jf data/nycboroughboundaries.json -sf data/nycboroughboundaries.svg

import argparse
import json
import os
import svgwrite
from svgwrite import inch, px
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-jf', dest="JSON_INPUT_FILE", default="data/nycboroughboundaries.json", help="Path to JSON file")
parser.add_argument('-sf', dest="SVG_OUTPUT_FILE", default="data/nycboroughboundaries.svg", help="Path to output SVG file")
parser.add_argument('-bc', dest="BG_COLOR", default="#A2CAEA", help="Background color")
parser.add_argument('-fc', dest="FILL_COLOR", default="#F2EAD6", help="Fill color of features")
parser.add_argument('-w', dest="WIDTH", default="800", type=int, help="Width of image in px")

# init input
args = parser.parse_args()

# read json data
features = []
aspect_ratio = 1.0
with open(args.JSON_INPUT_FILE) as f:
    data = json.load(f)
    features = data["features"]
    aspect_ratio = data['aspect_ratio']

# Init svg
WIDTH = args.WIDTH
HEIGHT = WIDTH
dwg = svgwrite.Drawing(args.SVG_OUTPUT_FILE, size=(WIDTH*px, HEIGHT*px), profile='full')

# Draw bg
dwgBg = dwg.add(dwg.g(id='background'))
dwgBg.add(dwg.rect(size=(WIDTH*px, HEIGHT*px), fill=args.BG_COLOR))
print "Initialized svg with size %s x %s px" % (WIDTH, HEIGHT)

# Draw features
for feature in features:
    dwgFeatures = dwg.add(dwg.g(id=feature["id"]))
    for path in feature["paths"]:
        points = []
        for point in path:
            x = int(round(point[0]*WIDTH))
            y = int(round(point[1]*WIDTH))
            points.append((x, y))
        dwgFeatures.add(dwg.polygon(points=points, fill=args.FILL_COLOR))

# Save
dwg.save()
print "Saved svg %s" % args.SVG_OUTPUT_FILE

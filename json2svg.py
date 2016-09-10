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
parser.add_argument('-fc', dest="BOROUGH_COLOR", default="#F2EAD6", help="Fill color of boroughs")
parser.add_argument('-w', dest="WIDTH", default="600", type=int, help="Width of image in px")

# init input
args = parser.parse_args()

# get boundaries
def boundaries(features):
    lngs = []
    lats = []
    for feature in features:
        for polygon in feature["polygons"]:
            for lnglat in polygon:
                lngs.append(lnglat[0])
                lats.append(lnglat[1])
    minLng = min(lngs)
    maxLng = max(lngs)
    minLat = min(lats)
    maxLat = max(lats)
    return [minLng, minLat, maxLng, maxLat]

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

def lnglatToPx(lnglat, bounds, width, height):
    x = (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * width
    y = (1.0 - (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * height
    return (int(round(x)), int(round(y)))

# read json data
boroughs = []
with open(args.JSON_INPUT_FILE) as f:
    data = json.load(f)
    boroughs = data["boroughs"]

# Determine bounds
boundaries = boundaries(boroughs)

# Init svg
WIDTH = args.WIDTH
HEIGHT = WIDTH
dwg = svgwrite.Drawing(args.SVG_OUTPUT_FILE, size=(WIDTH*px, HEIGHT*px), profile='full')

# Draw bg
dwgBg = dwg.add(dwg.g(id='background'))
dwgBg.add(dwg.rect(size=(WIDTH*px, HEIGHT*px), fill=args.BG_COLOR))
print "Initialized svg with size %s x %s px" % (WIDTH, HEIGHT)

# Draw boroughs
for borough in boroughs:
    dwgFeatures = dwg.add(dwg.g(id=borough["id"]))
    for polygon in borough["polygons"]:
        points = []
        for point in polygon:
            points.append(lnglatToPx(point, boundaries, WIDTH, HEIGHT))
        dwgFeatures.add(dwg.polygon(points=points, fill=args.BOROUGH_COLOR))

# Save
dwg.save()
print "Saved svg %s" % args.SVG_OUTPUT_FILE

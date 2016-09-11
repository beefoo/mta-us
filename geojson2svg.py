# -*- coding: utf-8 -*-

# Description: converts json file to svg
# Example usage:
#   python geojson2svg.py

import argparse
import json
import math
import os
import re
import svgwrite
from svgwrite import inch, px
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-cf', dest="CONFIG_FILE", default="config.json", help="Path to input config file")
parser.add_argument('-sf', dest="SVG_OUTPUT_FILE", default="data/nyc.svg", help="Path to output SVG file")
parser.add_argument('-bc', dest="BG_COLOR", default="#A2CAEA", help="Background color")
parser.add_argument('-w', dest="WIDTH", default="2000", type=int, help="Width of image in px")
parser.add_argument('-ma', dest="MIN_AREA", default="100", type=int, help="Min width of polygon")
parser.add_argument('-r', dest="ROTATE_DEGREES", default="-29.0", type=float, help="Degrees to rotate")

# init input
args = parser.parse_args()

# config geojson sources
geojsons = []
with open(args.CONFIG_FILE) as f:
    geojsons = json.load(f)

# get boundaries
def boundaries(groups):
    lngs = []
    lats = []
    for group in groups:
        for feature in group['features']:
            for lnglat in feature["coordinates"]:
                lngs.append(lnglat[0])
                lats.append(lnglat[1])
    minLng = min(lngs)
    maxLng = max(lngs)
    minLat = min(lats)
    maxLat = max(lats)
    return [minLng, minLat, maxLng, maxLat]

def polygonArea(corners):
    n = len(corners) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area


def lnglatToPx(lnglat, bounds, width, height):
    x = (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * width
    y = (1.0 - (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * height
    return (int(round(x)), int(round(y)))

def rotate(degrees, point1, point0):
    (x1, y1) = point1
    (x0, y0) = point0
    rad = math.radians(degrees)
    x2 = math.cos(rad)*(x1-x0)-math.sin(rad)*(y1-y0)+x0
    y2 = math.sin(rad)*(x1-x0)+math.cos(rad)*(y1-y0)+y0
    return (int(round(x2)), int(round(y2)))

# string to identifier
def strToId(s):
    s = s.lower()
    # Remove invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '_', s)
    # Remove leading characters until we find a letter or underscore
    # s = re.sub('^[^a-zA-Z_]+', '_', s)
    return s

groups = []
for g in geojsons:
    # read geojson data
    with open(g['file']) as f:
        geojson = json.load(f)
        features = geojson['features']
        print "Found %s features in %s" % (len(features), g['file'])
        for feature in features:
            group = feature['properties'][g['groupBy']]
            groupId = strToId(group)
            groupIndex = next((i for (i, g) in enumerate(groups) if g["id"] == groupId), len(groups))
            if groupIndex >= len(groups):
                groups.append({
                    "id": groupId,
                    "type": g["id"],
                    "label": group,
                    "features": []
                })
            coordinates = feature['geometry']['coordinates']
            geoType = feature['geometry']['type']
            color = g['color']
            if type(color) is dict:
                if groupId in color:
                    color = color[groupId]
                else:
                    color = False
            for multiLnglats in coordinates:
                if geoType!="MultiPolygon":
                    multiLnglats = [multiLnglats]
                for lnglats in multiLnglats:
                    groups[groupIndex]["features"].append({
                        "label": feature['properties'][g['label']],
                        "coordinates": lnglats,
                        "color": color,
                        "draw": g['draw'],
                        "strokeWidth": g['strokeWidth']
                    })

# Determine bounds
bounds = boundaries(groups)

# Init svg
WIDTH = args.WIDTH
HEIGHT = int(round(WIDTH / 1.005))
dwg = svgwrite.Drawing(args.SVG_OUTPUT_FILE, size=(WIDTH*px, HEIGHT*px), profile='full')

# Draw bg
dwgBg = dwg.add(dwg.g(id='background'))
dwgBg.add(dwg.rect(size=(WIDTH*px, HEIGHT*px), fill=args.BG_COLOR))
print "Initialized svg with size %s x %s px" % (WIDTH, HEIGHT)
center = (WIDTH/2.0, HEIGHT/2.0)

# Draw groups
for g in geojsons:
    groupsOfType = [group for group in groups if group["type"]==g["id"]]
    dwgType = dwg.add(dwg.g(id=g["id"]))
    for group in groupsOfType:
        dwgFeatures = dwgType.add(dwg.g(id=group["id"]))
        for feature in group["features"]:
            points = []
            for lnglat in feature["coordinates"]:
                point = lnglatToPx(lnglat, bounds, WIDTH, HEIGHT)
                point = rotate(args.ROTATE_DEGREES, point, center)
                points.append(point)
            if feature["color"]:
                if feature["draw"]=="polygon":
                    area = polygonArea(points)
                    if area > args.MIN_AREA:
                        dwgFeatures.add(dwg.polygon(points=points, fill=feature["color"]))
                else:
                    dwgFeatures.add(dwg.polyline(points=points, stroke=feature["color"], stroke_width=feature["strokeWidth"], fill="none"))

# Save
dwg.save()
print "Saved svg %s" % args.SVG_OUTPUT_FILE

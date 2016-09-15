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
parser.add_argument('-rs', dest="RESIZE_AMOUNT", default="0.9", type=float, help="Amount to resize")

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

def getPathsRecursive(arr):
    # this is a line
    if isPath(arr):
        return arr

    # this is an array of lines
    elif isinstance(arr[0], list):
        results = []
        for subArr in arr:
            result = getPathsRecursive(subArr)
            if isPath(result):
                results.append(result)
            else:
                results += result
        return results


def isPath(arr):
    return isinstance(arr[0], list) and isinstance(arr[0][0], float)

def lnglatToPx(lnglat, bounds, width, height):
    x = (lnglat[0] - bounds[0]) / (bounds[2] - bounds[0]) * width
    y = (1.0 - (lnglat[1] - bounds[1]) / (bounds[3] - bounds[1])) * height
    return (int(round(x)), int(round(y)))

def polygonArea(corners):
    n = len(corners) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area

def resize(amount, point1, point0):
    (x1, y1) = point1
    (x0, y0) = point0
    # translate to (0,0), scale, translate back to (cx,cy)
    x2 = (x1 - x0) * amount + x0
    y2 = (y1 - y0) * amount + y0
    return (x2, y2)

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
            paths = getPathsRecursive(coordinates)
            for path in paths:
                groups[groupIndex]["features"].append({
                    "label": feature['properties'][g['label']],
                    "coordinates": path,
                    "color": color,
                    "draw": g['draw'],
                    "strokeWidth": g['strokeWidth']
                })

# Determine bounds
bounds = boundaries(groups)
print "Bounds geo (lat/lng): [%s, %s, %s, %s]" % (bounds[0], bounds[1], bounds[2], bounds[3])
WIDTH = args.WIDTH
HEIGHT = int(round(WIDTH / 1.005))
center = (WIDTH/2.0, HEIGHT/2.0)

# convert everything to pixels
xs = []
ys = []
for gi, group in enumerate(groups):
    for fi, feature in enumerate(group["features"]):
        points = []
        for lnglat in feature["coordinates"]:
            point = lnglatToPx(lnglat, bounds, WIDTH, HEIGHT)
            # point = resize(args.RESIZE_AMOUNT, point, center)
            point = rotate(args.ROTATE_DEGREES, point, center)
            points.append(point)
            xs.append(point[0])
            ys.append(point[1])
        groups[gi]["features"][fi]["points"] = points
minX = min(xs)
maxX = max(xs)
minY = min(ys)
maxY = max(ys)
print "Bounds after rotation (px): [%s, %s, %s, %s]" % (minX, minY, maxX, maxY)

# adjust pixels after rotation
translateX = -1 * minX
translateY = -1 * minY
WIDTH = maxX - minX
HEIGHT = maxY - minY
for gi, group in enumerate(groups):
    for fi, feature in enumerate(group["features"]):
        for pi, point in enumerate(feature["points"]):
            groups[gi]["features"][fi]["points"][pi] = (point[0]+translateX, point[1]+translateY)
print "Bounds after adjustment (px): [0, 0, %s, %s]" % (WIDTH, HEIGHT)

# Init svg
dwg = svgwrite.Drawing(args.SVG_OUTPUT_FILE, size=(WIDTH*px, HEIGHT*px), profile='full')

# Draw bg
dwgBg = dwg.add(dwg.g(id='background'))
dwgBg.add(dwg.rect(size=(WIDTH*px, HEIGHT*px), fill=args.BG_COLOR))
print "Initialized svg with size %s x %s px" % (WIDTH, HEIGHT)

# Draw features
for g in geojsons:
    groupsOfType = [group for group in groups if group["type"]==g["id"]]
    dwgType = dwg.add(dwg.g(id=g["id"]))
    for group in groupsOfType:
        dwgFeatures = dwgType.add(dwg.g(id=group["id"]))
        for feature in group["features"]:
            points = feature["points"]
            color = feature["color"]
            if color and points:
                if feature["draw"]=="polygon":
                    area = polygonArea(points)
                    if area > args.MIN_AREA:
                        dwgFeatures.add(dwg.polygon(points=points, fill=color))
                else:
                    dwgFeatures.add(dwg.polyline(points=points, stroke=color, stroke_width=feature["strokeWidth"], fill="none"))

# Save
dwg.save()
print "Saved svg %s" % args.SVG_OUTPUT_FILE

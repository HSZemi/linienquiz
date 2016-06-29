#! /usr/bin/env python3

import json
import sys, math, os
import svgwrite

STROKES = [(svgwrite.rgb(200,0,0, 'rgb'),4), (svgwrite.rgb(0,0,150, 'rgb'), 3.5), (svgwrite.rgb(100,100,100, 'RGB'),2)]
WIDTH = 400
HEIGHT = 400
MAPZOOM = 16

class mappoint:
	def __init__(self, lat, lon):
		self.lat = lat
		self.lon = lon
		
	def __str__(self):
		return "( {0} | {1} )".format(self.lat, self.lon)
	
	def mapcoords(self, center_lat, center_lon, zoomlevel, width, height):
		center_lon_rad = math.radians(center_lon);
		center_lat_rad = math.radians(center_lat);
		pos_lon_rad = math.radians(self.lon);
		pos_lat_rad = math.radians(self.lat);
		n = pow(2.0, zoomlevel);

		centerTileX = ((center_lon + 180) / 360) * n;
		centerTileY = (1 - (math.log(math.tan(center_lat_rad) + 1.0/math.cos(center_lat_rad)) / math.pi)) * n / 2.0;
		
		#print("centerTileX = {0}".format(centerTileX))
		#print("centerTileY = {0}".format(centerTileY))
		
		posTileX = ((self.lon + 180) / 360) * n;
		posTileY = (1 - (math.log(math.tan(pos_lat_rad) + 1.0/math.cos(pos_lat_rad)) / math.pi)) * n / 2.0;
		
		#print("posTileX = {0}".format(posTileX))
		#print("posTileY = {0}".format(posTileY))
		
		diffTileX = posTileX - centerTileX
		diffTileY = posTileY - centerTileY
		
		#print("diffTileX = {0}".format(diffTileX))
		#print("diffTileY = {0}".format(diffTileY))
		
		diffPixlesX = 256 * diffTileX
		diffPixlesY = 256 * diffTileY
		
		#print("diffPixlesX = {0}".format(diffPixlesX))
		#print("diffPixlesY = {0}".format(diffPixlesY))
		
		xPos = (width / 2) + diffPixlesX
		yPos = (height / 2) + diffPixlesY
		
		return [int(xPos), int(yPos)]

def areacoords(centercoords):
	l = [centercoords]
	for dx in range(-1,2):
		for dy in range(-1,2):
			if(not ((abs(dx) == 1 and abs(dy) == 1) or (dx == 0 and dy == 0))):
				l.append((centercoords[0]+dx, centercoords[1]+dy))
	return l

def out_of_bounds(a,b, w,h):
	if(a[0] < 0 and b[0] < 0):
		return True
	if(a[0] > w and b[0] > w):
		return True
	if(a[1] < 0 and b[1] < 0):
		return True
	if(a[1] > h and b[1] > h):
		return True
	return False


def file2segments(filename):
	if(not os.path.isfile(filename)):
		print("Error: {0} is not an existing file.".format(filename))
		sys.exit()
	segments = []
	with open(filename, "r") as f:
		data = json.load(f)
		for feature in data['features']:
			if 'geometry' in feature:
				if (feature['geometry']['type'] == 'LineString'):
					segments.append(feature['geometry']['coordinates'])
				if (feature['geometry']['type'] == 'Polygon'):
					for linesegment in feature['geometry']['coordinates']:
						segments.append(linesegment)
	return segments

def main():
	if(len(sys.argv) < 3):
		print("Usage: {0} <output.svg> <input1.json> [<input2.json [input3.json [...]]]".format(sys.argv[0]))
		sys.exit()
	
	outputfile = sys.argv[1]
	inputfiles = sys.argv[2:]
	
	linesets = []
	first = True
	MAPCENTER = (0,0)
	FACTOR = 0
	smin_lon = 99999999
	smax_lon = -99999999
	smin_lat = 99999999
	smax_lat = -99999999
	
	for infile in inputfiles:
		segments = file2segments(infile)
		if(first):
			min_lon = 99999999
			max_lon = -99999999
			min_lat = 99999999
			max_lat = -99999999
			for line in segments:
				for coords in line:
					min_lon = min(min_lon, coords[0])
					max_lon = max(max_lon, coords[0])
					min_lat = min(min_lon, coords[1])
					max_lat = max(max_lon, coords[1])
			MAPCENTER = (((max_lon + min_lon)/2), ((max_lat + min_lat)/2))
		data = []
		for line in segments:
			newline = []
			for coords in line:
				newline.append(mappoint(coords[1], coords[0]))
			data.append(newline)
		
		mapsegments = []
		for line in data:
			for i in range(1,len(line)):
				coords0 = line[i-1].mapcoords(MAPCENTER[0], MAPCENTER[1], MAPZOOM, WIDTH, HEIGHT)
				coords1 = line[i].mapcoords(MAPCENTER[0], MAPCENTER[1], MAPZOOM, WIDTH, HEIGHT)
				#for coords in areacoords(centercoords):
					#if(coords[0] >= 0 and coords[0] < width and coords[1] >= 0 and coords[1] < height):
						#pix[coords] = (200,0,0)
				mapsegments.append([coords0, coords1])
		
		if(first):
			for s in mapsegments:
				smin_lon = min(smin_lon, s[0][0])
				smin_lon = min(smin_lon, s[0][0])
				smax_lon = max(smax_lon, s[1][0])
				smax_lon = max(smax_lon, s[1][0])
				smin_lat = min(smin_lat, s[0][1])
				smin_lat = min(smin_lat, s[0][1])
				smax_lat = max(smax_lat, s[1][1])
				smax_lat = max(smax_lat, s[1][1])
			
		drawwidth = WIDTH - 20
		drawheight = HEIGHT - 20
			
		factor_x = drawwidth / (smax_lon - smin_lon)
		factor_y = drawheight / (smax_lat - smin_lat)
			
		FACTOR = min(factor_x, factor_y)
			
		for s in mapsegments:
			s[0][0] = (s[0][0] - smin_lon) * FACTOR  + 10 + ((drawwidth - (smax_lon - smin_lon) * FACTOR ) / 2)
			s[1][0] = (s[1][0] - smin_lon) * FACTOR  + 10 + ((drawwidth - (smax_lon - smin_lon) * FACTOR) / 2)
			s[0][1] = (s[0][1] - smin_lat) * FACTOR  + 10 + ((drawheight - (smax_lat - smin_lat) * FACTOR) / 2)
			s[1][1] = (s[1][1] - smin_lat) * FACTOR  + 10 + ((drawheight - (smax_lat - smin_lat) * FACTOR) / 2)
			
		linesets.append(mapsegments)
		first = False
			
	dwg = svgwrite.Drawing(outputfile, size=(WIDTH, HEIGHT), profile='tiny')
	for lineset, stroke in reversed(list(zip(linesets, STROKES))):
		for segment in lineset:
			if(not out_of_bounds((segment[0][0], segment[0][1]), (segment[1][0],segment[1][1]), WIDTH, HEIGHT)):
				dwg.add(dwg.line((segment[0][0], segment[0][1]), (segment[1][0],segment[1][1]), stroke=stroke[0], stroke_width=stroke[1], stroke_linecap="round"))
	dwg.save()
		
		
		
	

if __name__ == "__main__":
	main()

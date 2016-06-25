#! /bin/bash

for i in svg/*.svg; do inkscape --export-area-page --export-png=maps/`basename -s .svg $i`.png $i; done
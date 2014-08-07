#!/bin/sh
set -e
for width in 57 77 114 144; do
    inkscape -e touch-icon-${width}.png -w ${width} -h ${width} coffeestats-logo.svg
done

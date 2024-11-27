#!/bin/bash

# Create directories
mkdir -p dependencies
cd dependencies

# Download python-vlc and its dependencies for Raspberry Pi
pip3 download python-vlc --platform linux_armv7l --only-binary=:all: --python-version 3.7

# Create a tar file
cd ..
tar -czf vlc_dependencies.tar.gz dependencies/ 
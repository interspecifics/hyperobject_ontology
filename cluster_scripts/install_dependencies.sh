#!/bin/bash

# Update package list
sudo apt-get update

# Install VLC and required packages for framebuffer output
sudo apt-get install -y vlc vlc-plugin-base libvlc-dev

# Extract dependencies
tar -xzf vlc_dependencies.tar.gz

# Install python-vlc from wheel
cd dependencies
pip3 install --user *.whl

# Clean up
cd ..
rm -rf dependencies vlc_dependencies.tar.gz
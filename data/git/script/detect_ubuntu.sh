#!/bin/bash

if command -v git &> /dev/null; then
    # Get version
    VERSION=$(git --version | grep -oP 'version \K[0-9]+\.[0-9]+\.[0-9]+')
    echo "{\"is_installed\": true, \"version\": \"$VERSION\"}"
    exit 0
else
    echo "{\"is_installed\": false, \"version\": null}"
    exit 1
fi
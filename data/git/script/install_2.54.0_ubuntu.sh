#!/bin/bash

add-apt-repository ppa:git-core/ppa -y
apt update
apt install git=1:2.54.0-* -y
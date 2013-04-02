#!/bin/sh

export PYTHONPATH=$PYTHONPATH:./src

HOME=`pwd`
cd src
python tank/web/main.py --running_dir=$HOME

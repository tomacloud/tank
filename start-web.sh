#!/bin/sh

export PYTHONPATH=$PYTHONPATH:./src

. venv/bin/activate 

HOME=`pwd`
cd src
python tank/web/main.py --running_dir=$HOME

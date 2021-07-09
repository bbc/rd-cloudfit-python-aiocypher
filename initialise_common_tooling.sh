#!/bin/bash

#
# Clone the commontooling repository
#

set -e

BRANCH=$1

if [ -z "$BRANCH" ]
then
    BRANCH="master"
fi

if [ ! -d "commontooling" ]
then
    git clone git@github.com:bbc/rd-cloudfit-commontooling.git commontooling --depth=1 --no-single-branch --branch=$BRANCH
fi

cd commontooling
git checkout $BRANCH
git pull
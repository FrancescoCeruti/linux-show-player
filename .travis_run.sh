#!/usr/bin/env bash

# Build on Travis CI

if [ ! $(env | grep TRAVIS_JOB_ID ) ] ; then
  echo "This script is supposed to run on Travis CI"
  exit 1
fi

RECIPE="dist/AppImage/Recipe"
mkdir -p ./out/

if [ -f $RECIPE ] ; then
  bash -ex $RECIPE
else
  # There is no Recipe
  echo "Recipe not found, is $RECIPE missing?"
  exit 1
fi

ls -lh out/*.AppImage
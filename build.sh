#!/bin/bash

# Check that we're in a dir containing the package
# TODO: make sure it's the RIGHT package!
if [ ! -f PACKAGE ]; then
  echo "Error: PACKAGE file not found. Run this from the project root."
  exit 1
fi

# Make sure it's actually the Anny package, not some other RV package
if ! grep -q '^package:[[:space:]]*Anny' PACKAGE; then
  echo "Error: PACKAGE found, but it isn't the Anny package. Aborting."
  exit 1
fi

# Pull the version straight from the PACKAGE file so there's one source of truth
VERSION=$(grep '^version:' PACKAGE | awk '{print $2}')
PKG_NAME="anny-${VERSION}.rvpkg"

echo "Building ${PKG_NAME}"

# Remove stale version
rm -f "../${PKG_NAME}"

# Repackage
zip -r "../${PKG_NAME}" PACKAGE Python -x '*__pycache__*' -x '*.pyc'

echo "Done: ../${PKG_NAME}"

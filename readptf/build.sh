#!/bin/bash
# first build readptf for PTF with 1.8.6 standard variable name length
make clean
make
# clean everything and build readptf2 for PTF with 2.x longer variable name length
make clean
make -f makefile2
make clean

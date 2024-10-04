#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Axiliary utility 

reads dec*.endf files from a directory 
and stores selected data in python pickle file
named endf.pickle

"""

import melendfmod.isotope as isotope

lci = isotope.lisotope()
lci.fReadENDF()
lci.fSavePickle()

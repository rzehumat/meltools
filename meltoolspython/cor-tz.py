#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
python script cor-tz.py 
written by Petr Vokac, ÚJV Řež, a.s
March 2011
September 2015, compatibility with Python3
August 2017, change of model organization 
License: as-is

expects "readptf.exe" on PATH !

expects cor-tz config name as command 
line argument (cor-tz.conf default)

specific input options:

lVars   - list of variables
lRing   - list of ring numbers
lSerTit - list of titles for each series

lVars, lRing, lSerTit should have the same length

'''

import meltoolsmod.cortz as cortz

if __name__ == "__main__":
 cortz.fMain()
pass

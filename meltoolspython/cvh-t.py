#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
python script cvh-t.py 
written by Petr Vokac, UJV Rez, a.s.
February 2011,
September 2017 -- change of modules structure
License: as-is

expects "readptf.exe" on PATH !

expects cvh-t config name as command 
line argument (no default provided)

specific input options:

 scvhlist    file name of cvh list for cvh-* plots
 shslist     file name of hs list for cvh-* plots

scvhlist is obligatory, it should be formated :

cvxxx x0 vsc

where: 

xxx is the volume number
x0  is the volume offset on the x axis
vsc is the volume scale factor (default = 1.0)

see function pvpyx.fGetCVROffset for details

shslist is optional, it should be formated :

xxxx x0 dx1 dx2 ...

where:

xxxx is the heat structure number
x0   is the heat structure offset on the x axis
dx1  is the thickness of the first hs layer
dx2  ...

see function pvpyx.fGetHSROffset for details

note: water level is not implemented, CVH-TVAP used for whole volume

'''

import meltoolsmod.cvht as cvht
if __name__ == "__main__":
 cvht.fMain()
pass


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate example time input"""
import sys

k = 0
n = 0
ipl = 10
sys.stdout.write("begin time\n")
for i in range(14, 20):
    if i == 14:
        lj = range(19 * 2, 24 * 2)
    else:
        lj = range(24 * 2)
    pass
    for j in lj:
        xt = i * 24 * 3600.0 + j * 3600.0 / 2.0
        st = " " + str(xt)
        sys.stdout.write(st)
        k += 1
        n += 1
        if k > ipl:
            k = 0
            sys.stdout.write("\n")
        pass
    pass
pass
sys.stdout.write("\n")
sys.stdout.write("end time\n")
sys.stdout.write("# %d time points requested\n" % (n))

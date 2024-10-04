#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# plot legend for cor-volf
#
# read configuration from cor-volf.conf
#
# different configuration file can be specified
# as the first command line argument
#
# output :
#   colorsc.pdf - color rectangles in column
#   colorsr.pdf - color rectangles in row
#
import sys
import pyx
import meltoolsmod.pvpyx as pvpyx


def fPlotRect(c, svol, col, x, z, w, h, xtfc, xtfs, xtp):
    """plot one color rectangle"""
    if svol in ["fl", "flc", "flb"]:
        p = pyx.path.rect(x, z, w, h / 2.0)
        c.fill(p, [col, pyx.deco.filled([col]), pyx.deco.color.transparency(xtfc)])
        p = pyx.path.rect(x, z + h / 2.0, w, h / 2.0)
        c.fill(p, [col, pyx.deco.filled([col]), pyx.deco.color.transparency(xtfs)])
    elif svol in ["por", "porb"]:
        p = pyx.path.rect(x, z, w, h)
        c.fill(p, [col, pyx.deco.filled([col]), pyx.deco.color.transparency(xtp)])
    else:
        p = pyx.path.rect(x, z, w, h)
        c.fill(p, [col, pyx.deco.filled([col])])
    pass


pass

if __name__ == "__main__":

    pyx.text.set(mode="latex")
    pyx.unit.set(defaultunit="mm", uscale=1.0)

    xtfc = 0.1
    xtfs = 0.7
    xtp = 0.5

    co = pvpyx.copt()
    sf = "cor-volf.conf"
    if len(sys.argv) > 1:
        sf = sys.argv[1]
    pass
    co.readopt(sf)
    co.printopt()
    lvolf = co.lCompList
    lvolfc = co.lcCompList

    c = pyx.canvas.canvas()

    h = 10.0
    w = 10.0
    z = 100.0
    dz = 1.1 * h

    for col, svol in zip(lvolfc, lvolf):
        fPlotRect(c, svol, col, 0.0, z, w, h, xtfc, xtfs, xtp)
        c.text(1.1 * w, z + h / 2.0, svol, [pyx.text.halign.boxleft])
        z -= dz
    pass

    c.writePDFfile("colorsc")

    c = pyx.canvas.canvas()

    x = 0.0
    h = 7.0
    w = 10.0
    z = 100.0
    dz = 1.1 * h
    dw = 1.1 * w

    for col, svol in zip(lvolfc, lvolf):
        fPlotRect(c, svol, col, x, z, w, h, xtfc, xtfs, xtp)
        c.text(
            x + 0.5 * w,
            z - 0.6 * h,
            svol,
            [pyx.text.halign.boxcenter, pyx.text.size.large],
        )
        x += dw
    pass

    c.writePDFfile("colorsr")
pass

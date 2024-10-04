#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import pyx
import meltoolsmod.pvmisc as pvmisc
import meltoolsmod.pvpyx as pvpyx


def fMain():
    # generic step in z axis
    dz = 0.1
    dx = 0.1

    pyx.text.set(mode="latex")

    if len(sys.argv) > 1:
        sf = sys.argv[1]
    else:
        print("Enter config file as a command line argument")
        sys.exit(2)
    pass

    co = pvpyx.copt()
    co.spdfdir = "cvh-liqlev"
    co.spdffn = "cvh-liqlev.pdf"
    co.readopt(sf)
    co.printopt()
    imaxname = pvpyx.fCleanOutput(co.spdfdir, co.iClean)
    pyx.unit.set(defaultunit=co.sunits, uscale=co.xscale)

    lscvx = []  # list of lists of cvh equivalent cylinder radius

    # reads cvh fl definitions from MELPTF
    icv0 = 0
    ifl0 = 0

    lscvt, lscvz, lscvv, lfl, lflfrom, lflto, lflfromz, lfltoz = pvmisc.fGetCVFLSetup(
        co.sptf
    )
    lscv, lx0, lcvi, lcvvsc, lczb, lczt = pvpyx.fGetCVROffset(lscvt, co.scvhlist)
    lscvx = pvpyx.fCVCrossSections(lscvt, lscvz, lscvv, lscv, lcvvsc)
    pvpyx.fCorrectFlz(lflfrom, lflto, lflfromz, lfltoz, lscv, lx0, lscvt, lscvz)
    # set up ztics
    if len(co.lztics) > 0:
        # tics from configuration file
        lztics = []
        for sz in co.lztics:
            lztics.append(float(sz))
        pass
    else:  # no ztics in input
        lztics = pvpyx.fGetZTics(lscvt, lscvz, lscv)
    pass
    zmax1 = lztics[-1]
    zmin1 = lztics[0]

    ltime = pvmisc.fReadTime(sptf=co.sptf)
    lzzz = pvmisc.fReadCVHVar("CVH-LIQLEV", lcvi, co.sptf)
    lzzzc = pvmisc.fReadCVHVar("CVH-CLIQLEV", lcvi, co.sptf)
    nt0 = len(ltime)
    ltr = pvpyx.fCheckOutputRange(nt0, co.iStart, co.iStop, co.iStep, imaxname)
    for iRec in ltr:
        c = pyx.canvas.canvas()
        # z axis

        pvpyx.fPlotZaxis(c, zmin1, zmax1, lztics, dx, dz, co.lztics)
        if len(co.lxtics) > 0:
            pvpyx.fPlotXaxis(c, zmin1, zmax1, co.lxtics, dx, dz)
        pass

        lzz = lzzz[iRec]
        lzzc = lzzzc[iRec]
        for scv in lscv:
            ilscvt = lscvt.index(scv)
            lz = lscvz[ilscvt]
            lv = lscvv[ilscvt]
            lx = lscvx[ilscvt]
            ilscv = lscv.index(scv)
            x0 = co.x00 + lx0[ilscv]
            zz = lzz[ilscv]
            zzc = lzzc[ilscv]
            ii = len(lz)
            # swollen water level
            bPlWl = True
            if lczb[ilscv] != "#N/A":
                if zz < float(lczb[ilscv]):
                    bPlWl = False
            if bPlWl:
                pvpyx.fPlotCVHWL(c, lz, lx, x0, zz, pyx.color.cmyk.SkyBlue, tr=0.5)
            # pyx.color.cmyk.GreenYellow)
            # collapsed water level
            bPlWl = True
            if lczb[ilscv] != "#N/A":
                if zzc < float(lczb[ilscv]):
                    bPlWl = False
            if bPlWl:
                pvpyx.fPlotCVHWL(c, lz, lx, x0, zzc, pyx.color.cmyk.SkyBlue)
            pvpyx.fPlotCVHBorder(c, lz, lx, x0, scv, lczb[ilscv], lczt[ilscv])
        pass

        pvpyx.fPlotFLSimple(
            c, lfl, lscv, co.x00, co.xra, lx0, lflfrom, lflto,
            lflfromz, lfltoz,
            flcol=pyx.deco.color.rgb.blue,
        )

        sf = "./%s/%04d" % (co.spdfdir, iRec)
        sz = "Time = %.1f\,s = %s, Plot record %d" % (
            ltime[iRec],
            pvmisc.fCas(ltime[iRec]),
            iRec,
        )
        c.text(0.1, zmin1 - 0.01, sz, [pyx.text.halign.boxleft])
        c.text(0.1, zmax1 + 0.01, co.sTitle, [pyx.text.halign.boxleft])
        c.writePDFfile(sf)
        sys.stdout.write("%d," % (iRec))
    pass
    print("\nFinished - single page pdfs are in ./%s/" % (co.spdfdir))
    if pvpyx.fJoinPdf(co.spdffn, co.spdfdir):
        print("Output written to ./pdf/%s" % co.spdffn)
    pass


pass  # end of the main section of the code

if __name__ == "__main__":
    print("I am just a module.")
pass

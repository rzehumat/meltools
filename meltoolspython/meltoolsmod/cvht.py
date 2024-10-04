#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyx

import meltoolsmod.pvmisc as pvmisc
import meltoolsmod.pvpyx as pvpyx


def fMain():

    # generic step in z axis
    dz = 0.1
    dx = 0.1

    pyx.text.set(mode="latex")
    mcgr = pyx.color.gradient.Rainbow  # temperature color scale type

    if len(sys.argv) > 1:
        sf = sys.argv[1]
    else:
        print("Enter config file as a command line argument")
        sys.exit(2)
    pass

    co = pvpyx.copt()
    co.spdfdir = "cvh-t"
    co.spdffn = "cvh-t.pdf"
    co.dxtscale = 5 * dx  # default temperature scale thickness
    co.x0tscale = -15 * dx  # default temperature scale left position
    co.readopt(sf)
    co.printopt()
    imaxname = pvpyx.fCleanOutput(co.spdfdir, co.iClean)
    pyx.unit.set(defaultunit=co.sunits, uscale=co.xscale)

    lscvt, lscvz, lscvv, lfl, lflfrom, lflto, lflfromz, lfltoz = pvmisc.fGetCVFLSetup(
        co.sptf
    )
    lscv, lx0, lcvi, lcvvsc, lczb, lczt = pvpyx.fGetCVROffset(lscvt, co.scvhlist)
    lscvx = pvpyx.fCVCrossSections(lscvt, lscvz, lscvv, lscv, lcvvsc)

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

    # read HS variable values if requested
    if len(co.shslist) > 0:
        t = pvmisc.fSPHS(co.sptf)
        # print (len(t))
        lHSNumber, lHSNumberofNodes, lHSba, lHSlal, lxaux = pvmisc.fSPHS(co.sptf)
        lhs, lhsx0, llhsx = pvpyx.fGetHSROffset(co.shslist, lHSNumber, lHSNumberofNodes)
        lhst = pvmisc.fReadHSVar("HS-TEMP", lhs, co.sptf)
    pass
    #
    if len(co.lHSlal) > 0:
        lHSlal = co.lHSlal
    # read CVH variable values
    ltime = pvmisc.fReadTime(sptf=co.sptf)
    lzzv = pvmisc.fReadCVHVar("CVH-TVAP", lcvi, co.sptf)
    lzzl = pvmisc.fReadCVHVar("CVH-TLIQ", lcvi, co.sptf)
    lzzz = pvmisc.fReadCVHVar("CVH-LIQLEV", lcvi, co.sptf)
    nt0 = len(ltime)
    ltr = pvpyx.fCheckOutputRange(nt0, co.iStart, co.iStop, co.iStep, imaxname)
    for iRec in ltr:
        c = pyx.canvas.canvas()
        pvpyx.fPlotZaxis(c, zmin1, zmax1, lztics, dx, dz, co.lztics)
        if len(co.lxtics) > 0:
            pvpyx.fPlotXaxis(c, zmin1, zmax1, co.lxtics, dx, dz)
        pass
        lzz = lzzv[iRec]
        if len(co.shslist) > 0:  # 170906 lhst may not exist
            lflat = [x for sublist in lhst[iRec] for x in sublist]
        else:
            lflat = []
        pass
        # print (lzz+[390]+lflat)
        tmax = max([390] + lflat + lzzl[iRec] + lzzv[iRec])
        tmin = min([290] + lflat + lzzl[iRec] + lzzv[iRec])
        # print (tmin,tmax)
        pvpyx.fPlotScale(
            c, mcgr, co.x0tscale, zmin1, co.x0tscale + co.dxtscale,
            zmax1, tmax, tmin, co.lttics
        )
        # pvpyx.fPlotCVHOneColor(c,mcgr,co.x00,lscv,lx0,lscvt,lscvz,lscvv,lscvx,lzz,tmax,tmin)
        # pvpyx.fPlotFLSimple(c,lfl,lscv,co.x00,co.xra,lx0,lflfrom,lflto,lflfromz,lfltoz)
        # rint(len(co.shslist))
        if len(co.shslist) > 0:
            # rint(tmax, tmin, iRec)
            # rint(lHSlal)
            pvpyx.fPlotHSTemp(
                c, mcgr, co.x00, lhs, lhsx0, llhsx, lhst[iRec],
                lHSNumber, lHSba, lHSlal, tmax, tmin
            )
        pass
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


pass

if __name__ == "__main__":
    print("I am just a module.")
pass

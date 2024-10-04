#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pyx
import math

import meltoolsmod.pvmisc as pvmisc
import meltoolsmod.pvpyx as pvpyx
import meltoolsmod.cortlhmod as cortlhmod


def fMain():

    co = pvpyx.copt()
    sf = "cor-tlh.conf"
    if len(sys.argv) > 1:
        sf = sys.argv[1]
    pass
    co.spdfdir = "cor-tlh"
    co.spdffn = "cor-tlh.pdf"
    co.readopt(sf)
    co.printopt()

    spdfdir = "cor-tlh"  # subdirectory for single page pdfs
    spdffn = "cor-tlh.pdf"  # joined pdf file name

    mcgr = pyx.color.gradient.Rainbow
    pyx.text.set(mode="latex")
    pyx.unit.set(defaultunit=co.sunits, uscale=co.xscale)
    tts = pyx.text.size.normalsize

    imaxname = pvpyx.fCleanOutput(co.spdfdir, co.iClean)

    lr0 = []
    lr1 = []
    lrr = []
    lz0 = []
    lz1 = []

    print("Reading /SP data ...")
    print(co.sptf)
    nRings, nRows, lz, lr, lcha, lbyp = pvmisc.fSP1(sptf=co.sptf)

    print("Number of rings: ", nRings)
    print("Radiuses: ", lr)
    print("Number of axial elevations: ", nRows)
    print("Elevations: ", lz)

    for svar in [
        "xRVESS",
        "xRVLH",
        "dzlh2",
        "dzlh1",
        "dzrv2",
        "dzrv1",
        "nlh2",
        "nlh1",
        "ntlp",
    ]:
        if getattr(co, svar) is None:
            print("Variable %s not specified in the configuration file" % (svar))
            bReadPickle = True
            break
        pass
    else:
        bReadPickle = False
    pass
    if bReadPickle:
        # read auxiliary data from the pickle file when necessary --- backward compatibility
        print("Reading cor_to_lhead.pickle")
        import pickle

        f = open("cor_to_lhead.pickle", "rb")  # python2 'r' vs. python3 'rb'
        lz = pickle.load(f)
        lr = pickle.load(f)
        co.ntlp = pickle.load(f)
        # cylindrical vessel wall thickness
        co.dzrv1 = pickle.load(f)  # = 0.140+0.009 # steel
        co.dzrv2 = pickle.load(f)  # = 0.070       # isolation
        # spherical vessel wall thickness
        co.dzlh1 = pickle.load(f)  # = 0.165+0.009 # steel
        co.dzlh2 = pickle.load(f)  # = 0.070       # isolation
        co.nlh1 = pickle.load(f)  # = 7 # steel
        co.nlh2 = pickle.load(f)  # = 2 # isolation
        co.xRVLH = pickle.load(f)  # core_data.rvlh
        co.xRVESS = pickle.load(f)  # core_data.rvess # reactor vessel inner radius
        f.close()
        print(
            co.xRVESS,
            co.xRVLH,
            co.nlh2,
            co.nlh1,
            co.dzlh2,
            co.dzlh1,
            co.dzrv2,
            co.dzrv1,
            co.ntlp,
        )
    pass
    nrad = len(lr)
    xRCOR = lr[nrad - 2]
    xDZRV = co.dzrv1 + co.dzrv2
    xDZLH = co.dzlh1 + co.dzlh2
    xHLST = lz[co.ntlp]
    xHSCP = lz[co.ntlp]
    iNLH = co.nlh1 + co.nlh2 + 1
    iNLHTA = nrad

    x0 = 0.0
    xr = lr[-1]
    y0 = lz[0]

    # internal wall - intersection of hemisphere and cylinder
    yi = (co.xRVLH - math.sqrt(co.xRVLH**2 - co.xRVESS**2)) + y0
    xfii = 180.0 * math.asin(co.xRVESS / co.xRVLH) / math.pi - 90

    # external wall - intersection of hemisphere and cylinder
    yo1 = (
        co.xRVLH - math.sqrt((co.xRVLH + co.dzlh1) ** 2 - (co.xRVESS + co.dzrv1) ** 2)
    ) + y0
    xfio1 = (
        180.0 * math.asin((co.xRVESS + co.dzrv1) / (co.xRVLH + co.dzlh1)) / math.pi - 90
    )

    # external wall - intersection of hemisphere and cylinder
    yo = (co.xRVLH - math.sqrt((co.xRVLH + xDZLH) ** 2 - (co.xRVESS + xDZRV) ** 2)) + y0
    xfio = 180.0 * math.asin((co.xRVESS + xDZRV) / (co.xRVLH + xDZLH)) / math.pi - 90

    # print co.dzrv1, co.dzrv2,co.dzlh1 , co.dzlh2,co.nlh1 , co.nlh2,lr[-1],co.xRVESS,(yo-yi)

    tanfi = xDZRV / (yo - yi)  # tangent of corner divison line
    tanfi1 = co.dzrv1 / (yo1 - yi)  # tangent of corner divison line
    try:
        tanfi2 = co.dzrv2 / (yo - yo1)
    except:
        # no isolation
        tanfi2 = 0.0
    pass
    # print tanfi,tanfi1,tanfi2

    ltime = pvmisc.fReadTime(sptf=co.sptf)
    sf = "COR-TLH"
    l = pvmisc.fReadVar(sf, iMess=1, sptf=co.sptf, sOpt="0")  # no time

    lsf = ["SS", "PD", "MP1", "MP2"]
    lvolf = []
    lt = []
    for sf1 in lsf:
        sf = "COR-VOLF-%s" % (sf1)
        lvolf1 = pvmisc.fReadVar(sf, iMess=1, sptf=co.sptf, sOpt="0")  # no time
        lvolf.append(lvolf1)
        sf = "COR-T%s" % (sf1)
        lt1 = pvmisc.fReadVar(sf, iMess=1, sptf=co.sptf, sOpt="0")  # no time
        lt.append(lt1)
    pass

    # select time records
    nt0 = len(ltime)
    ltr = pvpyx.fCheckOutputRange(nt0, co.iStart, co.iStop, co.iStep, imaxname)

    for it in ltr:
        c = pyx.canvas.canvas()

        # colors in the debris bed/pool
        cortlhmod.fDBPoolColors(
            c, mcgr, it, l, lt, lvolf, nRings, nRows, co.ntlp, lr, lz, co.xRVLH, x0, y0
        )

        # colors in the wall
        cortlhmod.fColorWall(
            c,
            mcgr,
            x0,
            y0,
            tanfi1,
            tanfi2,
            co.xRVESS,
            xDZRV,
            co.xRVLH,
            xDZLH,
            xHLST,
            co.nlh1,
            co.nlh2,
            lr,
            lz,
            xfii,
            xfio,
            yi,
            yo,
            co.dzlh1,
            co.dzlh2,
            co.dzrv1,
            co.dzrv2,
            ltime,
            l,
            it,
        )

        # following is not dependent on the time
        # grid in the lower plenum
        cortlhmod.fDBPoolGrid(c, lr, lz, x0, y0, xHSCP, xDZRV, xHLST, xDZLH)

        # plot nodalization of the RPV wall
        cortlhmod.fWallGrid(
            c,
            lr,
            lz,
            co.xRVESS,
            co.xRVLH,
            xHLST,
            x0,
            y0,
            co.dzlh1,
            co.dzlh2,
            co.dzrv1,
            co.dzrv2,
            co.nlh1,
            co.nlh2,
            tanfi1,
            tanfi2,
        )

        # plot titles
        x = ltime[it]
        xtboxt = pyx.text.text(0.0, 0.0, "{\\tiny X}").bbox().height()
        ss = "\\ \\\\Time = %.1f\,s = %s, Plot record %d" % (x, pvmisc.fCas(x), it)
        c.text(
            x0,
            lz[0] - (xtboxt + xDZLH),
            ss,
            [pyx.text.halign.boxleft, pyx.text.valign.top, tts],
        )
        c.text(
            x0,
            xHLST + xtboxt,
            "\\noindent " + co.sTitle + "\\\\ \\,",
            [pyx.text.halign.boxleft, pyx.text.valign.bottom, tts],
        )
        # write single page figure
        spdf = "./%s/%04d" % (co.spdfdir, it)
        c.writePDFfile(spdf)
        sys.stdout.write("%d," % (it))
    pass
    print("\nFinished - single page pdfs are in ./%s/" % (co.spdfdir))
    if pvpyx.fJoinPdf(co.spdffn, co.spdfdir):
        print("Output written to ./pdf/%s" % (co.spdffn))
    pass


pass

if __name__ == "__main__":
    print("I am just a module.")
pass

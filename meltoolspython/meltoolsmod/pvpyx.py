#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 library for MELCOR post-processing using pyx
 Petr Vokac, NRI Rez plc
 2011
 licence "as-is"

 25.9.2014: copt noutfdig --- number of digits in the file name can be changed
 23.4.2015 python3 compatibility
"""
import pyx
import subprocess as subp
import math


def fListDir(sdir):
    """return list of files in the sdir"""
    lsf = []
    p = subp.Popen(["ls", sdir], stdin=subp.PIPE, stdout=subp.PIPE)
    for fname in p.stdout:
        lsf.append(fname.strip().decode("utf-8"))
    p.stdin.close()
    return lsf


pass


def fCheckPdfTk():
    """check whether pdftk is present in the system"""
    # pdftk --version returns 5 lines when present
    #
    try:
        # this causes error on Mac when pdftk is not present
        p = subp.Popen(
            ["pdftk", "--version"],
            stdin=subp.PIPE,
            stdout=subp.PIPE,
            stderr=subp.STDOUT,
        )
    except:
        return False
    pass
    s = ""
    i = 0
    for line in p.stdout:
        i += 1
        if i < 3:
            s = line.strip()
        pass
    pass
    print(s.decode("utf-8"))
    return i > 3


pass


def fJoinPdf(spdfname, spdfdir):
    """join single page pdfs to one pdf,
    uses pdftk when it is available,
    pyPdf otherwise - it currently does not work ,
    """
    bPdfTk = False
    bpdf = False
    bPdfTk = fCheckPdfTk()
    if bPdfTk:
        lspdf = fListDir(spdfdir)
        spdf = " ".join(lspdf)
        scommand = "pdftk %s cat output ../pdf/%s" % (spdf, spdfname)
        print("Runing pdftk ...")
        p = subp.Popen([scommand], shell=True, cwd=spdfdir)
    else:
        try:
            # unfortunately pyPdf died out
            import pyPdf  # PdfFileWriter, PdfFileReader

            bpdf = True
        except:
            bpdf = False
        pass

        # try to use pyPdf if pdftk is not available
        if bpdf:
            inputFileNames = fListDir(spdfdir)
            output = pyPdf.PdfFileWriter()
            lpg = []
            for pdfFileName in inputFileNames:
                sf = "%s/%s" % (spdfdir, pdfFileName)
                fb = file(sf, "rb")
                inputpdf = pyPdf.PdfFileReader(fb)
                pg = inputpdf.getPage(0)
                lpg.append(pg)
                fb.close()  # this causes a problem: attempt to read closed file or too many open files
            pass
            for pg in lpg:
                output.addPage(pg)  # adds the first page of each document
            pass
            outputFileName = "./pdf/%s" % (spdfname)
            outputStream = file(outputFileName, "wb")
            output.write(outputStream)
            outputStream.close()
        pass
    pass

    return bpdf or bPdfTk


pass


def fCleanOutput(spdfdir, iClean=0):
    """remove pdf files from previous runs"""
    imaxname = 0
    p = subp.Popen(["mkdir", "-p", spdfdir])
    if iClean == 1:
        print("Deleting pdfs from %s folder, checking pdf folder ..." % (spdfdir))
        p = subp.Popen(["rm -f ./" + spdfdir + "/*.pdf"], shell=True)
    else:
        print(
            "Checking number of files in the %s folder, checking pdf folder ..."
            % (spdfdir)
        )
        p = subp.Popen(["ls", spdfdir], stdin=subp.PIPE, stdout=subp.PIPE)
        for fname in p.stdout:
            sname = fname.strip()[:-4]  # 25.9.2014 remove .pdf, not number of digits
            try:
                iname = int(sname)
            except:
                iname = 0
            pass
            # print iname
            if iname > imaxname:
                imaxname = iname
            pass
        pass
        p.stdin.close()
    # print imaxname
    pass
    p = subp.Popen(["mkdir", "-p", "pdf"])
    return imaxname


pass


def fCheckOutputRange(nt0, icstart, icstop, icstep, imaxname):
    """check output range of figures:
    nt0      : number of time records in the plot file
    icstart  : requested start index
    icstop   : requested stop index
    icstep   : requested step index
    imaxname : last figure already plotted
    """
    print("Checking output range ...")
    if icstop > 0:
        if icstop < nt0:
            nt0 = icstop
        pass
    pass
    nt1 = nt0
    if icstart < 0:
        icstart = 0
    if imaxname > icstart:
        icstart = imaxname + 1
    if icstart > (nt1):
        icstart = nt1
    if icstep < 1:
        icstep = 1
    if icstep > (nt1 - icstart):
        icstep = nt1 - icstart
    if icstep < 1:
        print("Nothing to plot")
        exit(0)
    pass
    ltr = list(range(icstart, nt0, icstep))
    nr = len(ltr)
    if nr == 1:
        print("Plot %d figure: %d" % (nr, icstart))
    else:
        if icstep > 1:
            print(
                "Plot %d figures: %d ... %d, step %d" % (nr, icstart, nt0 - 1, icstep)
            )
        else:
            print("Plot %d figures: %d ... %d" % (nr, icstart, nt0 - 1))
        pass
    pass
    return ltr


pass


# generic class for options
class copt:
    """class to read and store options from configuration file"""

    def __init__(self):
        self.defaults()

    pass

    def defaults(self):
        self.iStart = 0
        self.iStop = 0
        self.iStep = 1
        self.sTitle = ""
        self.scvhlist = ""  # filename - list of cvh volumes and ofsets
        self.shslist = ""  # filename - list of hs offsets
        self.spdfdir = ""  # directory for single page pdfs
        self.spdffn = ""  # output filename
        self.sptf = "MELPTF"  # default MELCOR plot file
        self.x00 = 0.0  # x offset of cvh position (it is added to cvh x position)
        self.scvDown = ""  # downcomer cvh volumes
        self.xra = 0.3  # length of arrows of flowpaths
        self.sunits = "cm"  # pyx scale units
        self.xscale = 2.0  # pyx scale factor
        self.iClean = 0
        self.bPrintOpt = False
        self.noutfdig = 4
        self.lCompList = [
            "fu",
            "cl",
            "cn",
            "ss",
            "ns",
            "pb",
            "pd",
            "mb1",
            "mp1",
            "mb2",
            "mp2",
        ]
        self.lCCompList = [
            pyx.color.cmyk.Red,
            pyx.color.cmyk.YellowGreen,
            pyx.color.cmyk.RoyalBlue,
            pyx.color.cmyk.OliveGreen,
            pyx.color.cmyk.Violet,
            pyx.color.cmyk.Yellow,
            pyx.color.cmyk.Dandelion,
            pyx.color.cmyk.Lavender,
            pyx.color.cmyk.Orchid,
            pyx.color.cmyk.Maroon,
            pyx.color.cmyk.Brown,
        ]
        self.lztics = []
        self.lxtics = []
        self.lttics = []
        self.lSerTit = []
        self.lVars = []
        self.lRing = []
        self.dxtscale = None
        self.x0tscale = None
        self.lHSlal = []
        self.xRVESS = None
        self.xRVLH = None
        self.nlh2 = None
        self.nlh1 = None
        self.dzlh2 = None
        self.dzlh1 = None
        self.dzrv2 = None
        self.dzrv1 = None
        self.ntlp = None

    pass

    def readopt(self, sf):
        """reads configuration file,
          configuration file is composed of keywords - values pairs on one line,
          not all keywords should be entered, defaulds are provided

          keywords :

           iStart      start time record number
           iStop       stop time record number (zero => plot all)
           iStep       step in number of tome records (one => plot all between iStart and iStop)
           sTitle      title of the chart
           scvhlist    file name of cvh list for cvh-* plots
           shslist     file name of hs list for cvh-* plots
           spdfdir     folder to put single page pdfs
           spdffn      file name of joined pdf (it is put into pdf subfolder)
           x00         horizontal offset for all the cvh volumes in cvh-* plots
           scvDown     list of downcomer volumes for cor-volf plot
           iClean      0 - keep previous single page pdfs, 1 - delete them
           sptf        file name of the melcor binary plot file (MELPTF default)
           bPrintOpt   True print options, False do not
           sCompList   list of components for cor-volf plot
           scCompList  list of colors for components (should be valid PyX cmyk color names)
           xra         size of arrow
           sunits      change xscale accordingly
           xscale      larger value -> smaller text
           ztics       ticks of z axis for cvh-* plots
           xtics       ticks of x axis for cvh-* plots (no axis is plotted when omitted)
           lSerTit     list of titles for series in tz charts
           lVars       list of variables for cor-tz plot
           lRing       list of ring numbers for cor-tz plot (same number as lVars)
           dxtscale    temperature scale thickness
           x0tscale    temperature scale left position
           noutfdig    number of digits in single page pdf file name
        for cor-tlh only:
           xRVESS      radius of the vessel
           xRVLH       radius of the lower head
           nlh2        number of temperature points - isolation
           nlh1        number of temperature points - steel
           dzlh2       spherical vessel wall thickness - isolation
           dzlh1       spherical vessel wall thickness - steel
           dzrv2       cylindrical vessel wall thickness - isolation
           dzrv1       cylindrical vessel wall thickness - steel
           ntlp        lower plenum top node
        """
        f = open(sf, "r")
        for line in f:
            s = line.split()
            try:
                sk = s[0]
            except:
                sk = ""
            pass
            try:
                sv = " ".join(s[1:])
            except:
                sv = ""
            # print "keyword: %s value: %s" % (sk,sv)
            if sk == "":
                pass
            elif sk == "iStart":
                self.iStart = int(sv)
            elif sk == "iStop":
                self.iStop = int(sv)
                if self.iStop > 0:
                    self.iStop += 1
                pass
            elif sk == "iStep":
                self.iStep = int(sv)
            elif sk == "sTitle":
                self.sTitle = sv
            elif sk == "scvhlist":
                self.scvhlist = sv
            elif sk == "shslist":
                self.shslist = sv
            elif sk == "spdfdir":
                self.spdfdir = sv
            elif sk == "spdffn":
                self.spdffn = sv
            elif sk == "x00":
                self.x00 = float(sv)
            elif sk == "scvDown":
                self.scvDown = sv
            elif sk == "iClean":
                self.iClean = int(sv)
            elif sk == "sptf":
                self.sptf = sv
            elif sk == "bPrintOpt":
                try:
                    isv = int(sv)
                    ba = bool(isv)
                except:
                    if sv == "False":
                        ba = False
                    else:
                        ba = bool(sv)
                    pass
                pass
                self.bPrintOpt = ba
            elif sk == "sCompList":
                print(sv)
                self.lCompList = []
                for s in sv.split():
                    self.lCompList.append(s.strip().lower())
                pass
            elif sk == "scCompList":
                print(sv)
                self.lcCompList = []
                for s in sv.split():
                    ss = "pyx.color.cmyk.%s" % (s.strip())
                    self.lcCompList.append(eval(ss))
                pass
            elif sk == "xra":
                self.xra = float(sv)
            elif sk == "sunits":
                self.sunits = sv
            elif sk == "xscale":
                self.xscale = float(sv)
            elif sk == "ztics":
                for s in sv.split():
                    self.lztics.append(s)
                pass
            elif sk == "xtics":
                for s in sv.split():
                    self.lxtics.append(s)
                pass
            elif sk == "ttics":
                for s in sv.split():
                    self.lttics.append(s)
                pass
            elif sk == "lSerTit":
                for s in sv.split():
                    self.lSerTit.append(s)
                pass
            elif sk == "lVars":
                for s in sv.split():
                    self.lVars.append(s)
                pass
            elif sk == "lRing":
                for s in sv.split():
                    self.lRing.append(s)
                pass
            elif sk == "dxtscale":
                for s in sv.split():
                    self.dxtscale = float(s)
                pass
            elif sk == "x0tscale":
                for s in sv.split():
                    self.x0tscale = float(s)
                pass
            elif sk == "noutfdig":
                self.noutfdig = int(sv)
            elif sk == "lHSlal":
                for s in sv.split():
                    self.lHSlal.append(float(s))
                pass
            elif sk in ["xRVESS", "xRVLH", "dzlh2", "dzlh1", "dzrv2", "dzrv1"]:
                setattr(self, sk, float(sv))
            elif sk in ["nlh2", "nlh1", "ntlp"]:
                setattr(self, sk, int(sv))
            pass
        pass
        f.close()

    pass

    def printopt(self):
        """prints options when bPrintOpt is True"""
        if self.bPrintOpt:
            print("Options check")
            print("iStart = %d" % (self.iStart))
            print("iStep = %d" % (self.iStep))
            print("iStop = %d" % (self.iStop))
            print("sTitle = %s" % (self.sTitle))
            print("scvhlist = %s" % (self.scvhlist))
            print("spdfdir = %s" % (self.spdfdir))
            print("noutfdig = %d" % (self.noutfdig))
            print("spdffn = %s" % (self.spdffn))
            print("sptf = %s" % (self.sptf))
            print("x00 = %f" % (self.x00))
            print(self.bPrintOpt)
        pass

    pass


pass  # end copt class


#
def fTempCol(x, tmax, tmin):
    """convert temperature to color scale
     input:
      x - current temperature
      tmax - maximum temperature in plot
      tmin - minimum temperature in plot

    return relative temperature in range
    0 - 1
    """
    xx = x
    if xx < tmin:
        xx = tmin
    if xx > tmax:
        xx = tmax
    if tmax > tmin:
        xr = (xx - tmin) / (tmax - tmin)
    else:
        xr = 1.0
    pass
    return 1.0 - xr


pass


def fPlotScale(c, mcgr, x0, y0, x1, y1, tmax, tmin, ltp=[]):
    """plot temperature color scale in K

    input:
     c     - canvas to plot
     mcrr  - color pallete
     x0    - x bottom left
     y0    - y bottom left
     x1    - x top right
     y1    - y top right
     tmax  - maximum temperature
     tmin  - minimum temperature
     ltp   - list of predefined temperature ticks (optional)

     if x0<x1 print temperature tics at right
     if x1<x0 print temperature tics at left

    """
    # pts=pyx.text.size.Large
    pts = pyx.text.size.normalsize
    xtboxt = pyx.text.text(0.0, 0.0, "{\\tiny X}").bbox().height()
    iMax = 1000
    xMax = 1000.0
    dy = (y0 - y1) / xMax
    y = y1
    for i in range(iMax):
        p = pyx.path.path(
            pyx.path.moveto(x0, y),
            pyx.path.lineto(x1, y),
            pyx.path.lineto(x1, y + dy),
            pyx.path.lineto(x0, y + dy),
            pyx.path.closepath(),
        )
        mc = mcgr.getcolor(float(i) / xMax)
        c.stroke(p, [mc, pyx.deco.filled([mc])])
        y += dy
    pass
    lx = []
    for sx in ltp:
        x = int(sx)
        if x >= tmin and x <= tmax:
            lx.append(x)
        pass
    pass
    dx = float(round((tmax - tmin) / 10.0))
    ndx = int(round(math.log(dx, 10)))
    # rint(dx,ndx,pow(10,ndx))
    dx = pow(10, ndx)
    if len(lx) < 3:
        lx = []
        tmin1 = round(tmin / pow(10, ndx)) * pow(10, ndx)
        for i in range(int(round((tmax - tmin) / dx))):
            x = float(tmin1 + i * dx)
            lx.append(x)
        pass
        lx = list(set(lx))
        if len(lx) < 5:
            lx.append(int(tmax) - 1)
            lx.append(int(tmin) + 1)
        pass
    pass
    dy = y1 - y0
    if x1 > x0:
        ha = pyx.text.halign.boxleft
    else:
        ha = pyx.text.halign.boxright
    pass
    for i in lx:
        x = float(i)
        if tmin - dx / 1000.0 <= x <= tmax + dx / 1000.0:
            xi = fTempCol(x, tmax, tmin)
            c.text(
                x1, y1 - xi * dy, "\\,%d\\ " % (i), [ha, pyx.text.valign.middle, pts]
            )
        pass
    pass
    c.text(
        (x0 + x1) / 2.0,
        y1 + xtboxt,
        "\\textit{T} [K]",
        [pyx.text.halign.boxcenter, pyx.text.valign.bottom, pts],
    )


pass


def fGetCVROffset(lscvt, sfile):
    """reads list of cvhs to plot from the configuration file

    input :
     lscvt - list of cvh volumes (output of pvmisc.fGetCVFLSetup)
     sfile - configuration file name
    output :
     lscv   list of cvh volumes to plot
     lx0    list of horizontal offsets
     lcvi   list of volume indexes
     lcvvsc list of volume scale factor (optional column 3 in the CVH list)
     lczb   list of minimum elevation to plot (optional column 4 in the CVH list)
     lczt   list of maximum elevation to plot (optional column 5 in the CVH list)

    used in cvh-t.py, cvh-liqlev.py
    """

    lscv = []  # list of cvh volumes to plot
    lx0 = []  # list of horizontal offsets
    lcvi = []  # list of volume indexes
    lcvvsc = []  # list of volume scale factor
    lczb = []  # list of bottom elevations (optional min)
    lczt = []  # list of top elevations (optional max)

    f = open(sfile, "r")
    for line in f:
        ss = line.split()
        try:
            icvi = lscvt.index(ss[0])
        except:
            icvi = -1
        pass
        if icvi >= 0:
            lscv.append(ss[0])
            lx0.append(float(ss[1]))
            lcvi.append(icvi)
            try:
                xvsc = float(ss[2])
            except:
                xvsc = 1.0
            pass
            lcvvsc.append(xvsc)
            try:
                zb = ss[3]
            except:
                zb = "#N/A"
            pass
            lczb.append(zb)
            try:
                zt = ss[4]
            except:
                zt = "#N/A"
            pass
            lczt.append(zt)
        pass
    pass
    f.close
    return (lscv, lx0, lcvi, lcvvsc, lczb, lczt)


pass


def fGetHSROffset(sfile, lHSNumber, lHSNumberofNodes):
    """open list of heat structures and horizontal offsets
    it can be used for vertical cylindrical heat structures

    input :
     sfile - file name
             (list of heat structures to plot, offsets and node thicknesses)
     lHSNumber - list of all heat structures
     lHSNumberofNodes - list of number of nodes for all heat structures

    output :
     lhs - list of heat structures to plot
     lx0 - list of horizontal offsets
     llx - list of node thicknesses

    used in cvh-t.py
    """
    lhs = []  # list of hs
    lx0 = []  # list of horizontal offsets
    llx = []  # list of list of width of each node
    f = open(sfile, "r")
    for line in f:
        if len(line) == 0:
            continue
        if line[0] == "#":
            continue
        ss = line.split()
        if len(ss) == 0:
            continue
        try:
            ihs = int(ss[0])
        except:
            continue
        pass
        try:
            ihsi = lHSNumber.index(ihs)
        except:
            ihsi = -1
        pass
        if ihsi >= 0:
            lhs.append(ihs)
            lx0.append(float(ss[1]))
            lx = []
            x = 0.1
            for i in range(2, len(ss)):
                x = float(ss[i])
                lx.append(x)
            pass
            # append the same value for all remaining nodes
            nlx = len(lx)
            if nlx < lHSNumberofNodes[ihsi]:
                for i in range(nlx + 1, lHSNumberofNodes[ihsi]):
                    lx.append(x)
                pass
            pass
            llx.append(lx)
        pass
    pass
    f.close()
    return (lhs, lx0, llx)


pass


# def fCVCrossSections(lscvt,lscvzt,lscvvt,lscv=[],lcvvsc=[],lczb=[],lczt=[]) :
def fCVCrossSections(lscvt, lscvzt, lscvvt, lscv=[], lcvvsc=[]):
    """calculate cross sections for all volumes for simplicity,
     apply scaling factors for selected volumes,
     return list of lists of cvh equivalent cylinder radius

    input :
     lscvt - list of cvh volumes (output of pvmisc.fGetCVFLSetup)
     lscvzt - list of lists of cvh elevations (output of pvmisc.fGetCVFLSetup)
     lscvvt - list of lists of cvh volumes (output of pvmisc.fGetCVFLSetup)
     lscv   - list of volumes to plot optional default = [] (output of fGetCVROffset)
     lcvvsc - list of scale factors for volumes to plot optional default = [] (output of fGetCVROffset)
    output :
     lscvx  list of list of cross sections for each volume and elevation
    """
    # used in cvh-t.py
    lscvx = []
    for i in range(len(lscvzt)):
        try:
            xvsc = lcvvsc[lscv.index(lscvt[i])]
        except:
            xvsc = 1.0
        pass
        lx = []
        lz = lscvzt[i]
        lv = lscvvt[i]
        x = 0.0
        ii = len(lz)
        for iz in range(0, ii - 1):
            lx.append(x)
            v = (lv[iz + 1] - lv[iz]) * xvsc
            z = lz[iz + 1] - lz[iz]
            x = math.sqrt((v / z) / math.pi)
            lx.append(x)
        pass
        lx.append(x)
        lscvx.append(lx)
    pass
    return lscvx


pass


def fGetZTics(lscvt, lscvz, lscv):
    """determine ztics if not specified in the config file

    used in cvh-t.py, cvh-liqlev.py
    """
    zmin1 = 1.0e5
    zmax1 = -1.0e5
    # loop over all volumes
    for i in range(len(lscvz)):
        try:
            icv = lscv.index(lscvt[i])
        except:
            icv = -1
        pass
        if icv >= 0:
            # select only volumes to plot
            # print lscvt[i],lscv[icv]
            for z in lscvz[i]:
                if z > zmax1:
                    zmax1 = z
                if z < zmin1:
                    zmin1 = z
            pass
        pass
    pass
    zd = zmax1 - zmin1
    zdd = zd / 10.0
    for zi in range(0, 11):
        z = zi * zdd + zmin1
        lztics.append(z)
    pass
    return lztics


pass


def fPlotZaxis(c, zmin, zmax, lztics, dx, dz, lsztics=[]):
    """plot vertical axis for cvh charts

    used in cvh-t.py, cvh-liqlev.py
    """
    lx = []
    p = pyx.path.path(pyx.path.moveto(0.0, zmin), pyx.path.lineto(0.0, zmax))
    c.stroke(p)
    if len(lsztics) > 0:
        for sz in lsztics:
            z = float(sz)
            p = pyx.path.path(pyx.path.moveto(-1.0 * dx, z), pyx.path.lineto(0.0, z))
            c.stroke(p)
            c.text(-0.1, z, sz, [pyx.text.halign.boxright])
            # bb = p.bbox()
            # x = bb.left().tom()
            # lx.append(x)
        pass
    else:
        for z in lztics:
            p = pyx.path.path(pyx.path.moveto(-1.0 * dx, z), pyx.path.lineto(0.0, z))
            c.stroke(p)
            sz = "%5.1f" % (z)
            c.text(-1.0 * dx, z, sz, [pyx.text.halign.boxright])
            # bb = p.bbox()
            # x = bb.left().tom()
            # lx.append(x)
        pass
    pass
    # x = min(lx)
    return -1


pass


def fPlotXaxis(c, zmin, zmax, lsxtics, dx, dz):
    """plot horizontal axis for cvh charts
    it can be used during preparation of cvh list
    of horizontal offsets

    specify xtics in the config file to show x axis

    used in cvh-liqlev.py, cvh-t.py
    """
    # x axis
    xmin = float(lsxtics[0])
    xmax = float(lsxtics[-1])
    p = pyx.path.path(
        pyx.path.moveto(xmin, zmin - dz), pyx.path.lineto(xmax, zmin - dz)
    )
    c.stroke(p)
    for sx in lsxtics:
        x = float(sx)
        p = pyx.path.path(
            pyx.path.moveto(x, zmin - dz), pyx.path.lineto(x, zmin - 2 * dz)
        )
        c.stroke(p)
        c.text(x, zmin - 2 * dz, sx, [pyx.text.halign.boxcenter, pyx.text.valign.top])
    pass
    return -1


pass


def fPlotCVHOneColor(
    c, mcgr, x00, lscv, lx0, lscvt, lscvz, lscvv, lscvx, ltvar, tmax, tmin
):
    """plots cvh volume with color indicating gas tepmperature
    used in cvh-t.py
    """
    for scv in lscv:
        ilscvt = lscvt.index(scv)
        # print scv, ilscvt, len(lscvz)
        lz = lscvz[ilscvt]
        lv = lscvv[ilscvt]
        lx = lscvx[ilscvt]
        ilscv = lscv.index(scv)
        x0 = x00 + lx0[ilscv]
        fPlotCVH1TColor(c, mcgr, x0, lz, lx, tmax, tmin, ltvar[ilscv])
        c.text(
            x0,
            (lz[-1] + lz[0]) / 2.0,
            scv,
            [pyx.text.halign.boxcenter, pyx.text.valign.middle],
        )
    pass
    return -1


pass


def fPlotCVH1TColor(c, mcgr, x0, lz, lx, tmax, tmin, t):
    ii = len(lz)
    p = pyx.path.path(pyx.path.moveto(x0, lz[0]), pyx.path.lineto(x0 + lx[0], lz[0]))
    for i in range(1, ii):
        p.append(pyx.path.lineto(x0 + lx[2 * i - 1], lz[i - 1]))
        p.append(pyx.path.lineto(x0 + lx[2 * i], lz[i]))
    pass
    for i in range(ii - 1, 0, -1):
        p.append(pyx.path.lineto(x0 - lx[2 * i], lz[i]))
        p.append(pyx.path.lineto(x0 - lx[2 * i - 1], lz[i - 1]))
    pass
    p.append(pyx.path.lineto(x0 - lx[0], lz[0]))
    p.append(pyx.path.closepath())
    x = fTempCol(t, tmax, tmin)
    mc = mcgr.getcolor(x)
    c.stroke(p, [pyx.deco.filled([mc])])
    return -1


pass


def fPlotHSTemp(
    c, mcgr, x00, lhs, lhsx0, llhsx, llhst, lHSNumber, lHSba, lHSlal, tmax, tmin
):
    """plots heat structures temperature map
    used in cvh-t.py

    input :
      c           pyx canvas to plot
      mcgr        pyx color scale for temperatures
      x00         global horizontal offset
      lhs         list of HSs to plot
      lhsx0       list of horizontal offsets of HS to plot
      llhsx       list of lists of node thicknesses (plot on horizontal axis)
      llhst       list of lists of node temperatures
      lHSNumber   list of HSs numbers (all HS from the binary plot file)
      lHSba       list of HSs base elevations
      lHSlal      list of HSs axial lengths
      tmax        maximum of temperature scale
      tmin        minimum of temperature scale

    """
    for i in range(len(llhst)):
        lhst = llhst[i]
        x0 = x00 + lhsx0[i]
        ihs = lHSNumber.index(lhs[i])
        z0 = lHSba[ihs]
        dz = lHSlal[ihs]
        n = len(lhst)
        for j in range(n):
            # print i,j
            if j > 0 and j < n - 1:
                dx = (llhsx[i][j - 1] + llhsx[i][j]) / 2.0
            else:
                if j == 0:
                    dx = llhsx[i][j] / 2.0
                else:
                    dx = llhsx[i][-1] / 2.0
                pass
            pass
            xt = fTempCol(lhst[j], tmax, tmin)
            # rint(x0,z0,dx,dz,lhst[j],xt)
            p = pyx.path.rect(x0, z0, dx, dz)
            mc = mcgr.getcolor(xt)
            c.fill(p, [pyx.deco.filled([mc])])
            x0 += dx
        pass
    pass
    return -1


pass


def fHSTempTZ(inode, lhs, llhst, lHSNumber, lHSba, lHSlal):
    """for list of HS return list of node temperatures and list of elevations

    input :
      inode       node number
      lhs         list of HSs to plot
      llhst       list of lists of node temperatures
      lHSNumber   list of HSs numbers (all HS from the binary plot file)
      lHSba       list of HSs base elevations
      lHSlal      list of HSs axial lengths
    return :
      tuple : lz  list of elevations
              lx  list of temperatures
    """
    lz = []
    lx = []
    # print lHSNumber
    for i in range(len(llhst)):
        lhst = llhst[i]
        # print lhs[i]
        ihs = lHSNumber.index(lhs[i])
        z = lHSba[ihs] + lHSlal[ihs] / 2.0
        x = lhst[inode - 1]
        lz.append(z)
        lx.append(x)
    pass
    laux = list(zip(lz, lx))
    laux = sorted(laux)
    lz, lx = list(zip(*laux))
    return (list(lz), list(lx))


pass


def fHSVar1Z(lhs, lhsv, lHSNumber, lHSba, lHSlal):
    """for list of HS return list of values and list of elevations

    input :
      lhs         list of HSs to plot
      lhsv        list of values for all the hs
      lHSNumber   list of HSs numbers (all HS from the binary plot file)
      lHSba       list of HSs base elevations
      lHSlal      list of HSs axial lengths
    return :
      tuple : lz  list of elevations
              lx  list of values

    usefull for variables with one value per hs
    """
    lz = []
    lx = []
    # print lHSNumber
    for ihs in lhs:
        i = lHSNumber.index(ihs)
        z = lHSba[i] + lHSlal[i] / 2.0
        x = lhsv[i]
        lz.append(z)
        lx.append(x)
    pass
    laux = list(zip(lz, lx))
    laux = sorted(laux)
    lz, lx = list(zip(*laux))
    return (list(lz), list(lx))


pass


def fCorrectFlz(lflfrom, lflto, lflfromz, lfltoz, lscv, lx0, lscvt, llscvz):
    """correct zero lenght arrows for flow paths for before plotting

    input:
     lflfrom   list of from cvh volumes
     lflto     list of to cvh volumes
     lflfromz  list of from elevations
     lfltoz    list of to elevations
     lscv      list of cvh volumes
     llscvz    list of lists of cvh elevations
     lx0       list of cvh radial offsets for plotting

    output:
     lflfromz  list of from elevations
     lfltoz    list of to elevations

    used in cvh-liqlev for vver-440/213 input model
    """
    # print lflto
    # print lscv
    nfl = len(lflfrom)
    dz = 0.001
    dzz = 10.0 * dz
    for i in range(nfl):
        dzi = math.fabs(lflfromz[i] - lfltoz[i])
        if dzi < dz:
            # print i, dzi
            iTo = lscvt.index(lflto[i])
            zTo = (llscvz[iTo][-1] + llscvz[iTo][0]) / 2.0
            iFrom = lscvt.index(lflfrom[i])
            zFrom = (llscvz[iFrom][-1] + llscvz[iFrom][0]) / 2.0
            try:
                iTo = lscv.index(lflto[i])
            except:
                iTo = -1
            pass
            try:
                iFrom = lscv.index(lflfrom[i])
            except:
                iFrom = -1
            pass
            if (
                iTo >= 0 and iFrom >= 0
            ):  # only for flow paths connecting plotted cvh volumes
                xFrom = lx0[iFrom]
                xTo = lx0[iTo]
                dxi = math.fabs(xFrom - xTo)
                dzv = math.fabs(zFrom - zTo)
                if dxi < dz or dzv > dz:
                    if zTo > zFrom:
                        lflfromz[i] -= dzz
                        lfltoz[i] += dzz
                    else:
                        lflfromz[i] += dzz
                        lfltoz[i] -= dzz
                    pass
                pass
            pass
        pass
    pass


pass


def fPlotFLSimple(
    c,
    lfl,
    lscv,
    x00,
    xra,
    lx0,
    lflfrom,
    lflto,
    lflfromz,
    lfltoz,
    flcol=pyx.deco.color.grey.black,
):
    """plot flow paths
    used in cvh-t.py, cvh-liqlev.py
    """
    ifln = len(lfl)
    for i in range(ifln):
        try:
            iFrom = lscv.index(lflfrom[i])
        except:
            iFrom = -1
        try:
            iTo = lscv.index(lflto[i])
        except:
            iTo = -1
        if iFrom >= 0 and iTo >= 0:
            x1 = x00 + lx0[iFrom]
            x2 = x00 + lx0[iTo]
            z1 = float(lflfromz[i])
            z2 = float(lfltoz[i])
            p = pyx.path.path(pyx.path.moveto(x1, z1), pyx.path.lineto(x2, z2))
            c.stroke(
                p, [pyx.deco.arrow(size=xra), pyx.deco.color.transparency(0.5), flcol]
            )
            cp = pyx.path.circle(x1, z1, xra / 10.0)
            c.fill(cp, [pyx.deco.color.transparency(0.5), flcol])
        pass
    pass
    return -1


pass


def frange(x0, x1, dx, xuscale=0.0):
    """A range function, that does accept float increments...
    used in fSwollenArea
    """
    lx = []
    if x0 >= x1:
        x1 = x0
    elif x1 < x0 + 1.99 * dx:
        dx = (x1 - x0) / 2.01
    nx = int((x1 - x0) / dx)
    if nx <= 0:
        nx = 1
    if nx < 4:
        lx.append(x0 + (x1 - x0) / 2.0)
    elif nx < 5:
        lx.append(x0 + dx + xuscale)
        lx.append(x1 - dx - xuscale)
    else:
        xx1 = x1 - dx - xuscale
        xx0 = x0 + dx + xuscale
        lx.append(xx1)
        lx.append(xx0)
        dxx = 3 * dx
        nxx = int((xx1 - xx0) / dxx) + 1
        dxx = (xx1 - xx0) / float(nxx)
        for i in range(nxx):
            lx.append(i * dxx + xx0)
        pass
    pass
    return lx


pass


def fSwollenArea(c, col, z0, z1, r0, r1, dr, xuscale):
    """plot swollen area using collored disks
    not used anymore -- too slow rendering for animations
    """
    if z1 > z0 and r1 > r0:
        p = pyx.path.rect(r0, z0, r1 - r0, z1 - z0)
        c.stroke(p, [col, pyx.style.linewidth(0.2 * xuscale)])
        if z1 > z0 + dr:
            lz = frange(z0, z1, dr)
            lr = frange(r0, r1, dr)
            for zz in lz:
                for rrr in lr:
                    p = pyx.path.circle(rrr, zz, dr)
                    c.stroke(p, [col, pyx.deco.filled([col]), pyx.style.linewidth(0.0)])
                    pass
                pass
            pass
        pass
    pass


pass


def fPlotCVHWL(c, lz, lx, x0, zz, pcol, tr=0.0, zmin="#N/A", zmax="#N/A"):
    """plot water level in CVH
    input
     c     pyx canvas to plot
     lz    list of elevations
     lx    list of cross sections
     x0    horizontal offset
     zz    water level
     pcol  pyx color to fill boxes below water level
     tr    pyx transparency
     zmin  minimum elevation to plot (currently not used)
     zmax  maximum elevation to plot (currently not used)
    """
    ii = len(lz)
    # swollen water level
    ilevel = ii - 1
    p = pyx.path.path(pyx.path.moveto(x0, lz[0]), pyx.path.lineto(x0 + lx[0], lz[0]))
    for i in range(1, ii):
        if lz[i] < zz:
            p.append(pyx.path.lineto(x0 + lx[2 * i - 1], lz[i - 1]))
            p.append(pyx.path.lineto(x0 + lx[2 * i], lz[i]))
        else:
            p.append(pyx.path.lineto(x0 + lx[2 * i - 1], lz[i - 1]))
            p.append(pyx.path.lineto(x0 + lx[2 * i], zz))
            ilevel = i
            break
    pass
    if zz < lz[ilevel]:
        p.append(pyx.path.lineto(x0 - lx[2 * (ilevel)], zz))
    else:
        p.append(pyx.path.lineto(x0 - lx[2 * (ilevel)], lz[ilevel]))
    for i in range(ilevel - 1, -1, -1):
        p.append(pyx.path.lineto(x0 - lx[2 * i + 1], lz[i]))
        p.append(pyx.path.lineto(x0 - lx[2 * i], lz[i]))
    pass
    p.append(pyx.path.closepath())
    c.fill(p, [pyx.deco.filled([pcol]), pyx.deco.color.transparency(tr)])


pass


def fPlotCVHBorder(c, lz, lx, x0, scvname="", zmin="#N/A", zmax="#N/A"):
    """plot CVH border
    input
     c        pyx canvas to plot
     lz       list of elevations
     lx       list of cross sections
     x0       horizontal offset
     scvname  name of cvh to plot
     zmin     minimum elevation to plot
     zmax     maximum elevation to plot

    """
    ii = len(lz)
    try:
        zb = float(zmin)
        ib = -1
    except:
        zb = lz[0]
        ib = 0
    pass
    try:
        zt = float(zmax)
        it = -1
    except:
        it = ii
        zt = lz[-1]
    pass
    if it < 0:
        for i in range(1, ii):
            if lz[i] > zt:
                lz[i] = zt
                lz = lz[: i + 1]
                lx = lx[: i + 1]
                lx.append(lx[-1])
                break
            pass
        pass
        ii = len(lz)
    pass
    if ib < 0:
        for i in range(ii - 1, -1, -1):
            if lz[i] < zb:
                lz[i] = zb
                if i > 0:
                    lz = lz[i:]
                    lx = lx[i:]
                pass
            pass
        pass
        ii = len(lz)
    pass
    # print lz
    p = pyx.path.path(pyx.path.moveto(x0, lz[0]), pyx.path.lineto(x0 + lx[0], lz[0]))
    for i in range(1, ii):
        p.append(pyx.path.lineto(x0 + lx[2 * i - 1], lz[i - 1]))
        p.append(pyx.path.lineto(x0 + lx[2 * i], lz[i]))
    pass
    p.append(pyx.path.lineto(x0 - lx[2 * (ii - 1)], lz[ii - 1]))
    for i in range(ii - 2, -1, -1):
        p.append(pyx.path.lineto(x0 - lx[2 * i + 1], lz[i]))
        p.append(pyx.path.lineto(x0 - lx[2 * i], lz[i]))
    pass
    p.append(pyx.path.closepath())
    c.stroke(p)
    if scvname != "":
        c.text(x0, (lz[ii - 1] + lz[0]) / 2.0, scvname, [pyx.text.halign.boxcenter])
    pass


pass

if __name__ == "__main__":
    print(eval("__doc__"))
    print(dir())
pass

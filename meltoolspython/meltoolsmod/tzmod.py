#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generic library for plotting values against z axis
import pyx
import math

# default globals
xtitle = "Temperature [K]"
ytitle = "Elevation [m]"
zmin = 0.0
zmax = 10.0
nColumns = 2

llz = [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]]
llv = [[5.0, 6.0, 7.0, 8.0, 9.0, 10.0]]
ltitle = ["T1"]

# set up colors and symbols
# colors for line in graphs
lcolors = [
    pyx.color.cmyk.Red,
    pyx.color.cmyk.Green,
    pyx.color.cmyk.Blue,
    pyx.color.cmyk.Peach,
    pyx.color.cmyk.Brown,
    pyx.color.cmyk.Fuchsia,
    pyx.color.cmyk.OrangeRed,
    pyx.color.cmyk.ForestGreen,
    pyx.color.cmyk.Cerulean,
    pyx.color.cmyk.Tan,
    pyx.color.cmyk.Lavender,
    pyx.color.cmyk.RubineRed,
    pyx.color.cmyk.PineGreen,
    pyx.color.cmyk.Cyan,
    pyx.color.cmyk.Dandelion,
    pyx.color.cmyk.Gray,
    pyx.color.cmyk.Thistle,
]

# symbols to distinguish lines in chart
lsymbols = [
    pyx.graph.style.symbol.circle,
    pyx.graph.style.symbol.plus,
    pyx.graph.style.symbol.cross,
    pyx.graph.style.symbol.triangle,
    pyx.graph.style.symbol.square,
    #
    pyx.graph.style.symbol.circle,
    pyx.graph.style.symbol.plus,
    pyx.graph.style.symbol.cross,
    pyx.graph.style.symbol.triangle,
    pyx.graph.style.symbol.square,
    #
    pyx.graph.style.symbol.circle,
    pyx.graph.style.symbol.triangle,
    pyx.graph.style.symbol.square,
    pyx.graph.style.symbol.circle,
    pyx.graph.style.symbol.triangle,
]

xgs = 0.2
lsymsize = [
    xgs * 1.0,
    xgs * 1.0,
    xgs * 1.0,
    xgs * 1.0,
    xgs * 1.0,
    xgs * 0.4,
    xgs * 0.4,
    xgs * 0.4,
    xgs * 0.4,
    xgs * 0.4,
    xgs * 0.7,
    xgs * 0.7,
    xgs * 0.7,
    xgs * 0.7,
    xgs * 0.7,
]

lsymfill = [
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.stroked(),
    pyx.deco.filled([lcolors[10]]),
    pyx.deco.filled([lcolors[11]]),
    pyx.deco.filled([lcolors[12]]),
    pyx.deco.filled([lcolors[13]]),
    pyx.deco.filled([lcolors[14]]),
]

llinestyle = [
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
    pyx.style.linestyle.solid,
]

llinewidth = [
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
    pyx.style.linewidth.Thick,
]


lline = [
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
]
lsymb = [
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
]


def fPlotTZ(lzc=[]):
    global llz
    global llv
    global lcolors
    global lsymbols
    global ltitle
    global xtitle
    global ytitle
    global zmin
    global zmax
    global nColumns
    global lsymsize
    global lsymfill

    # pyx.text.set(mode="latex")
    pyx.text.set(cls=pyx.text.LatexRunner)
    nc = len(lcolors)
    ns = len(llz)
    if ns > nc:
        ns = nc
    pass
    fCheckMinMax()
    my_axis_painter = pyx.graph.axis.painter.regular(
        gridattrs=[
            pyx.attr.changelist(
                [pyx.style.linestyle.dashdotted, pyx.style.linestyle.dotted]
            ),
            pyx.attr.changelist([pyx.style.linewidth.thin, pyx.style.linewidth.Thin]),
        ]
    )

    if len(lzc) > 0:
        lznodticks = []
        for i in range(len(lzc) - 1):
            lznodticks.append(
                pyx.graph.axis.tick.tick(
                    (lzc[i] + lzc[i + 1]) / 2.0, label="%02d" % (i + 1)
                )
            )
        pass
        g = pyx.graph.graphxy(
            width=19,
            key=pyx.graph.key.key(
                pos="bc", hinside=0, vinside=0, vdist=2.0, columns=nColumns
            ),
            x=pyx.graph.axis.linear(title=xtitle, painter=my_axis_painter),
            y=pyx.graph.axis.linear(
                title=ytitle, painter=my_axis_painter, min=lzc[0], max=lzc[-1]
            ),
            y2=pyx.graph.axis.linear(
                title="Axial node [-] (at node center elevation)",
                min=lzc[0],
                max=lzc[-1],
                manualticks=lznodticks,
                parter=None,
            ),
        )
    else:
        if zmin == zmax or (zmin == 0.0 and zmax == 10.0):
            fSetZMinMax()
        g = pyx.graph.graphxy(
            width=19,
            key=pyx.graph.key.key(
                pos="bc", hinside=0, vinside=0, vdist=2.0, columns=nColumns
            ),
            x=pyx.graph.axis.linear(title=xtitle, painter=my_axis_painter),
            y=pyx.graph.axis.linear(
                title=ytitle, painter=my_axis_painter, min=zmin, max=zmax
            ),
        )

    pass

    for i in range(len(llz)):
        d = pyx.graph.data.values(x=llv[i], y=llz[i], title=ltitle[i])
        st = []
        ii = len(lline) - 1
        if i < ii:
            ii = i
        pass
        if lline[ii]:
            st.append(
                pyx.graph.style.line([lcolors[ii], llinestyle[ii], llinewidth[ii]])
            )
        if lsymb[ii]:
            st.append(
                pyx.graph.style.symbol(
                    lsymbols[ii],
                    size=lsymsize[ii],
                    symbolattrs=[lcolors[ii], lsymfill[ii]],
                )
            )
        g.plot(d, st)
    pass
    return g


pass


def fTransCorTempZ(lv, lzc, nRings, nRows, zoff=0.0, bChz=False):
    """transform data :
    input :
    lv - list of core data (temperatures)
    lzc - list of node elevations bottoms and top of the top most one
    nRings - number of core rings
    nRows - number axial nodes
    zoff - axial offset
    bChz - False : only values > 270
           True : all values
    """
    llx = []
    llz = []
    lxmax = []
    lxmin = []
    nr = len(lv) // nRows  # for some core variables, there is no full data set
    for i in range(nr):
        lx = []
        lz = []
        for j in range(nRows):
            x = lv[i * nRows + j]
            if x > 270.0 or bChz:  # skip temperature below zero
                lx.append(x)
                lz.append((lzc[j] + lzc[j + 1]) / 2.0 + zoff)
            pass
        pass
        llx.append(lx)
        llz.append(lz)
    pass
    return (llx, llz)


pass


def fWriteTimeTitle(g, xtime, itime, sTitle):
    ss = "Time = %.1f\,s = %.1f\,h, Plot record %d" % (xtime, xtime / 3600.0, itime)
    g.text(g.width / 2, -3.0, ss, [pyx.text.halign.center, pyx.text.valign.top])
    g.text(
        g.width / 2,
        g.height + 0.2,
        sTitle,
        [pyx.text.halign.center, pyx.text.valign.bottom],
    )


pass


def fSetZMinMax():
    """set minimum and maximum of z axis,
    used in fPlotTZ"""
    global llz
    global zmin
    global zmax
    lzmin = []
    lzmax = []
    for lz in llz:
        if len(lz) > 0:
            lzmin.append(min(lz))
            lzmax.append(max(lz))
        pass
    pass
    if len(lzmin) > 0:
        zmin = min(lzmin)
    else:
        zmin = 0.0
    pass
    if len(lzmax) > 0:
        zmax = max(lzmax)
    else:
        zmax = zmin + 1.0
    pass


pass


def fCheckMinMax():
    """y values should not be the same
    error pyx graph?"""
    global llv
    global min
    global max
    epsm = 0.001
    lmin = []
    lmax = []
    for l in llv:
        if len(l) > 0:
            x = min(l)
        else:
            x = 0.0
        pass
        # avoid non numeric results 3.5.2011
        if isinstance(x, (int, float)):
            lmin.append(x)
        if len(l) > 0:
            x = max(l)
        else:
            x = 0.0
        pass
        if isinstance(x, (int, float)):
            lmax.append(x)
    pass
    #  print lmin
    #  print lmax
    if len(lmin) > 0:
        xmin = min(lmin)
    else:
        xmin = 0.0
    pass
    if len(lmax) > 0:
        xmax = max(lmax)
    else:
        xmax = 0.0
    pass
    if math.fabs(xmax - xmin) < epsm:
        try:
            llv[0][0] += epsm
        except:
            pass
        pass
        try:
            llv[0][-1] -= epsm
        except:
            pass
        pass
    pass


pass

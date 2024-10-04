#! /usr/bin/env python
# -*- coding: utf-8 -*-


def fPackageDir():
    s1 = __file__
    s2 = __package__ + "/aux.py"
    n1 = len(s1)
    n2 = len(s2)
    return s1[: n1 - n2]


pass

"""auxiliary functions to read ENDF decay data files"""


def fHead(hl):
    """parse endf head string
    see [ENDF6FM] 0.6.3.3 HEAD Record
    """
    c1 = hl[0:11]
    c2 = hl[11:22]
    l1 = hl[22:33]
    l2 = hl[33:44]
    l3 = hl[44:55]
    l4 = hl[55:66]
    return (c1, c2, l1, l2, l3, l4)


pass


def fFloat(cx):
    """convert endf float to python float"""
    scx = cx.strip()
    ie = 0
    i = scx.rfind("+")
    if i > 1:
        ie = int(scx[i:])
        scx = scx[:i]
    pass
    i = scx.rfind("-")
    if i > 1:
        ie = int(scx[i:])
        scx = scx[:i]
    pass
    scx = scx.rstrip("E")
    scx = scx.rstrip("e")
    x = float(scx)
    x *= 10**ie
    return x


pass


def fZA(za):
    """convert endf ZA variable to Z and A"""
    x = fFloat(za)
    a = int(round(x))
    z = int(a / 1000)
    a -= z * 1000
    return (z, a)


pass

"""other auxiliary functions"""


def fMelFltStr(x, y):
    """attempt for short format of float for MELCOR,
    add dot and zero when the float has integer value
    """
    sx = " " + str(x)
    if not "." in sx:
        sx += ".0"
    sy = " %.5g" % (y)
    if (not "." in sy) and (not "e" in sy):
        sy += ".0"
    return sx + sy


pass

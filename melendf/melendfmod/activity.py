#!/usr/bin/env python
# -*- coding: utf-8 -*-

import melendfmod.g as g


# ******************************************
class activity(object):
    """activity class
    used to store data read from ORIGEN output
    """

    def __init__(self, abr="", z=0, a=0, isomer=0, x=0.0):
        self.abr = abr
        self.z = z
        self.a = a
        self.isomer = isomer
        self.x = x

    pass

    def fPrint(self):
        print(self.abr, self.x, self.z, self.a, self.isomer)

    pass


pass


# ******************************************
class lactivity(object):
    """lactivity class --- list of activity classes"""

    def __init__(self):
        self.l = []

    pass

    def fAdd(self, act):
        self.l.append(act)

    pass

    def fRead(self, sfn, bVerbose=False):
        """read ORIGEN output segment"""
        print("Reading %s input file ..." % (sfn))
        lig = []
        f = open(sfn, "r")
        for line in f:
            s = line.split()
            if len(s) > 1:  # 10.11.2013 check empty line
                x = 0.0
                z = g.gcel.fGetZ(s[0])
                if z > 0:
                    ta = g.gcel.fGetA(s[0])
                    if ta[0] > 0:
                        x = float(s[1])
                        if x > 0.0:
                            ca = activity(s[0], z, ta[0], ta[1], x)
                            self.fAdd(ca)
                        pass
                    pass
                pass
                if x <= 0.0:
                    lig.append(s[0])
                pass
            pass
        pass
        f.close()
        if len(lig) > 0 and bVerbose:
            print("Items ignored from file %s :" % (sfn))
            # 150513 print(string.join(sorted(set(lig))," "))
            print(" ".join(sorted(set(lig))))
        pass

    pass

    def fMultiplyActi(self, x):
        """multiply activities by x"""
        for ci in self.l:
            ci.x *= x
        pass

    pass

    def fPrint(self):
        for ca in self.l:
            ca.fPrint()
        pass

    pass


pass

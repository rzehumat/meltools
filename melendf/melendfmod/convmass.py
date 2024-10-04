#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


class ConvMass(object):
    """auxiliary class for
    conversion of ORIGEN outputs to different irradiation mass

    input:
     sdirii  - directory with input files
     muinp   - mass of uranium for irradiated sample in the input directory
     sdirio  - output directory
     muout   - mass of uranium for irradiated sample in the output directory
     suff    - suffix of data files, default ".txt"
     bDoIt   - do the conversin on class initiation, default True

    fConvMass does the conversion

    """

    def __init__(self, sdirii, muinp, sdirio, muout, suff=".txt", bDoIt=True):
        # input data
        self.sdirii = sdirii
        self.muinp = muinp
        self.sdirio = sdirio
        self.muout = muout
        self.suff = suff
        # internal data
        self.sfo = "%-8s %6.3e\n"  # output format
        self.lst = []
        self.ll = []
        # do it immediately if no changes necessary
        if bDoIt:
            self.fConvMass()

    pass

    def fReadFile(self, sf):
        l1 = []
        l2 = []
        f = open(sf, "r")
        for line in f:
            s = line.split()
            if len(s) > 1:
                l1.append(s[0])
                l2.append(float(s[1]))
            pass
        pass
        f.close()
        self.ll = (l1, l2)

    pass

    def fWriteFile(self, sf):
        f = open(sf, "w")
        for s, x in zip(self.ll[0], self.ll[1]):
            if x > 0.0:
                f.write(self.sfo % (s, x))
        pass
        f.close()

    pass

    def fConvData(self):
        n = len(self.ll[0])
        for ie in range(n):
            self.ll[1][ie] = self.ll[1][ie] * self.muout / self.muinp
        pass

    pass

    def fConvDir(self):
        for sf in self.lsf:
            print("Converting file " + sf)
            self.fReadFile(os.path.join(self.sdirii, sf))
            self.fConvData()
            self.fWriteFile(os.path.join(self.sdirio, sf))
        pass

    pass

    def fGetFiles(self):
        self.lsf = [
            f
            for f in os.listdir(self.sdirii)
            if os.path.isfile(os.path.join(self.sdirii, f)) and f[-4:] == self.suff
        ]

    pass

    def fConvMass(self):
        """do the mass conversion"""
        self.fGetFiles()  # get files in the input directory
        if not os.path.exists(self.sdirio):
            os.mkdir(self.sdirio)
        self.fConvDir()

    pass


pass
# end of ConvMass

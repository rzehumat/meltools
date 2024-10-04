#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import scipy
import scipy.linalg

# import math
import pickle
import melendfmod.aux as aux
import melendfmod.spectrum as spectrum
import melendfmod.g as g


class isotope(object):
    """isotope class:
    store isotope properties from the ENDF decay data,
    store activity
    """

    def __init__(self):
        # endf data
        self.z = 0  # number of protons
        self.a = 0  # number of nucleaons
        self.liso = 0  # isomer
        self.t12 = 0.0  # decay half time
        self.elp = 0.0
        self.eem = 0.0
        self.ehp = 0.0
        self.lrtyp = []  # list of tuples (rtyp,rfs,q,br)
        self.lspectrum = []
        # auxiliary decay data
        self.lchild = []
        # activity data
        self.acti = 0.0
        self.aacti = None  # it will be scipy.array of activities

    pass

    #
    def fCopyENDFdata(self):
        newisot = isotope()
        for sattr in [
            "z",
            "a",
            "liso",
            "t12",
            "elp",
            "eem",
            "ehp",
            "lrtyp",
            "lspectrum",
        ]:
            setattr(newisot, sattr, getattr(self, sattr))
            # I will generate lchild again
        pass
        return newisot

    pass

    # isotope
    def fReadENDF(self, sfn=None):
        """reads endf data files"""
        if sfn is None:
            # sfn=os.path.dirname(__file__)+"data-endf"
            sfn = aux.fPackageDir() + "data-endf"
        pass
        nndk = (
            -1
        )  # ==-1: ndk not read, >0: nndk=ndk, Total number of decay modes given.
        nst = (
            -1
        )  # -1 not read, Nucleus stability flag (NST=0, radioactive; NST=1, stable)
        istyp = -1  # auxiliary variable
        iner = (
            -1
        )  # auxiliary variable  NER Total number of tabulated discrete energies for a given spectral type (STYP).
        f = open(sfn, "r")
        for line in f:
            i = 0
            ii = 66
            hl = line[i : i + ii]
            i += ii
            ii = 4
            mat = int(line[i : i + ii])
            i += ii
            ii = 2
            mf = int(line[i : i + ii])
            i += ii
            ii = 3
            mt = int(line[i : i + ii])
            i += ii
            ii = 5
            ns = int(line[i : i + ii])  # line counter
            if mt == 457:
                if nst == 0 and nndk > 0:  # radioactive and ndk read
                    t = aux.fHead(hl)
                    rtyp = aux.fFloat(t[0])
                    rfs = aux.fFloat(t[1])
                    q = aux.fFloat(t[2])
                    br = aux.fFloat(t[4])
                    self.lrtyp.append((rtyp, rfs, q, br))
                    nndk -= 1  # decrease counter nndk
                    continue
                pass
                if ns == 1:  # first line
                    za, awr, lis, liso, snst, snsp = aux.fHead(hl)
                    nst = int(snst)
                    nsp = int(snsp)
                    self.z, self.a = aux.fZA(za)
                    self.liso = int(liso)
                    nndk = -1  # ndk not read, reset counter
                    continue
                pass
                if nst == 0 and ns == 2:
                    t12, dt12, l1, l2, npl, n2 = aux.fHead(hl)
                    self.t12 = aux.fFloat(t12)
                    continue
                pass
                if nst == 0 and ns == 3:
                    t = aux.fHead(hl)
                    self.elp = aux.fFloat(t[0])
                    self.eem = aux.fFloat(t[2])
                    self.ehp = aux.fFloat(t[4])
                    continue
                pass
                if nst == 0 and ns > 3 and nndk < 0:
                    spi, par, l1, l2, ndk6, ndk = aux.fHead(hl)
                    nndk = int(ndk)
                    continue
                pass
                if nst == 0 and ns > 3 and nndk == 0 and istyp == -1 and iner < 0:
                    fnula, styp, lcon, inula, isest, ner = aux.fHead(hl)
                    self.lspectrum.append(spectrum.spectrum())
                    self.lspectrum[-1].styp = aux.fFloat(styp)
                    self.lspectrum[-1].lcon = int(lcon)
                    self.lspectrum[-1].lner = int(ner)
                    istyp = 0
                    continue
                pass
                if nst == 0 and ns > 3 and nndk == 0 and istyp == 0 and iner < 0:
                    fd, dfd, erav, derav, fc, dfc = aux.fHead(hl)
                    self.lspectrum[-1].fd = aux.fFloat(fd)
                    self.lspectrum[-1].dfd = aux.fFloat(dfd)
                    self.lspectrum[-1].erav = aux.fFloat(erav)
                    self.lspectrum[-1].derav = aux.fFloat(derav)
                    istyp = -1
                    iner = int(ner)
                    ner = ""  # invalidate ner
                    if int(lcon) != 1:
                        inl = 2  # number of next records to read
                    continue
                pass
                # gamma, change conditions later
                if (
                    nst == 0
                    and ns > 3
                    and nndk == 0
                    and istyp == -1
                    and iner > 0
                    and (int(lcon) != 1)
                ):
                    if inl == 2:
                        er, der, inula, inula, snt, inula = aux.fHead(hl)
                        self.lspectrum[-1].lsd.append(spectrum.spectrumd())
                        self.lspectrum[-1].lsd[-1].er = aux.fFloat(er)
                        self.lspectrum[-1].lsd[-1].der = aux.fFloat(der)
                        nt = int(
                            snt
                        )  # Number of entries given for each discrete energy (ER).
                    elif inl == 1:
                        rtyp, type, ri, dri, ris, dris = aux.fHead(hl)
                        self.lspectrum[-1].lsd[-1].rtyp = aux.fFloat(rtyp)
                        self.lspectrum[-1].lsd[-1].type = aux.fFloat(type)
                        self.lspectrum[-1].lsd[-1].ri = aux.fFloat(ri)
                        self.lspectrum[-1].lsd[-1].dri = aux.fFloat(dri)
                        self.lspectrum[-1].lsd[-1].ris = aux.fFloat(ris)
                        self.lspectrum[-1].lsd[-1].dris = aux.fFloat(dris)
                    elif inl == 0:
                        ricc, dricc, rick, drick, ricl, dricl = aux.fHead(hl)
                        self.lspectrum[-1].lsd[-1].ricc = aux.fFloat(ricc)
                        self.lspectrum[-1].lsd[-1].dricc = aux.fFloat(dricc)
                        self.lspectrum[-1].lsd[-1].ricl = aux.fFloat(ricl)
                        self.lspectrum[-1].lsd[-1].dricl = aux.fFloat(dricl)
                        self.lspectrum[-1].lsd[-1].rick = aux.fFloat(rick)
                        self.lspectrum[-1].lsd[-1].drick = aux.fFloat(drick)
                    pass
                    inl -= 1
                    if inl < 0 or (inl == 0 and nt == 6):
                        """For gamma ray emission (STYP=0.0), no other information is
                        required if X-ray, Auger electron, conversion electron, and
                        pair formation intensities have not been calculated for these
                        transitions. In this case NT=6."""
                        iner -= 1
                        if iner == 0:
                            iner = -1
                        if int(lcon) == 0:
                            inl = 2
                    pass

                    # print ns
                    continue
                pass
            pass
            if mt == 454:
                # not implemented yet
                pass
            pass
        pass
        f.close()

    pass

    #
    def fPrint(self):
        """debug printout
        print isotope data
        """
        print(
            "Z = %d A = %d Isomer = %d T1/2 = %e s"
            % (self.z, self.a, self.liso, self.t12)
        )
        print("ELP = %f EEM = %f EHP = %f" % (self.elp, self.eem, self.ehp))
        print("RTYP: ", self.lrtyp)
        print("CHILDS: ", self.lchild)
        print("Activity %e Bq" % (self.acti))
        if self.aacti != None:
            print(self.aacti)
        for spec in self.lspectrum:
            spec.fPrint()
        pass

    pass

    #
    def fEnergy(self):
        """return average released energy in eV per decay"""
        p = 0.0
        if (self.elp) > 0.0:
            p += self.elp
        if (self.eem) > 0.0:
            p += self.eem
        if (self.ehp) > 0.0:
            p += self.ehp
        return p

    pass

    #
    def fDecay(self, lt):
        """calculate decay of isotope without radioactive child"""
        if self.acti > 0.0:
            self.aacti[0] = self.acti
            a = self.aacti[0]
            nt = len(lt)
            for i in range(1, nt):
                dt = lt[i] - lt[i - 1]
                if dt > g.dtmin:
                    xexp = -1.0 * dt * g.ln12 / self.t12
                    # a = a * math.exp(xexp)
                    a = a * scipy.exp(xexp)
                pass
                self.aacti[i] += a
            pass
        pass

    pass

    #
    def fSetChilds(self):
        """generate auxiliary index list of childs
        observed rtyp values:
        [5.5, 1.0, 2.0, 3.0, 4.0, 5.0, 1.5, 7.0, 1.1, 1.55, 2.77, 2.4, 2.7, 2.6, 7.7, 1.555, 1.4, 6.0, 1.5555]
        use lisotope.fGetLrtyp0() to get this list
        """
        for rtyp in self.lrtyp:
            t = (0, 0, 0)
            if rtyp[0] == 1.0:
                t = (self.z + 1, self.a, int(rtyp[1]))
            if rtyp[0] == 2.0:
                t = (self.z - 1, self.a, int(rtyp[1]))
            if rtyp[0] == 3.0:
                t = (self.z, self.a, int(rtyp[1]))
            if rtyp[0] == 4.0:
                t = (self.z - 2, self.a - 4, int(rtyp[1]))
            if rtyp[0] == 5.0:
                t = (self.z, self.a - 1, int(rtyp[1]))
            if rtyp[0] == 6.0:
                t = (0, 0, 0)
            if rtyp[0] == 7.0:
                t = (self.z - 1, self.a - 1, int(rtyp[1]))
            if rtyp[0] >= 10.0:
                t = (0, 0, 0)
            if rtyp[0] == 1.1:
                t = (self.z + 2, self.a, int(rtyp[1]))
            if rtyp[0] == 1.4:
                t = (self.z - 1, self.a - 4, int(rtyp[1]))
            if rtyp[0] == 1.5:
                t = (self.z + 1, self.a - 1, int(rtyp[1]))
            if rtyp[0] == 1.55:
                t = (self.z + 1, self.a - 2, int(rtyp[1]))
            if rtyp[0] == 1.555:
                t = (self.z + 1, self.a - 3, int(rtyp[1]))
            if rtyp[0] == 1.5555:
                t = (self.z + 1, self.a - 4, int(rtyp[1]))
            if rtyp[0] == 1.6:
                t = (self.z - 1, self.a - 4, int(rtyp[1]))
            if rtyp[0] == 2.4:
                t = (self.z - 3, self.a - 4, int(rtyp[1]))
            if rtyp[0] == 2.6:
                t = (0, 0, 0)
            if rtyp[0] == 2.7:
                t = (self.z - 2, self.a - 1, int(rtyp[1]))
            if rtyp[0] == 2.77:
                t = (self.z - 3, self.a - 2, int(rtyp[1]))
            if rtyp[0] == 5.5:
                t = (self.z - 2, self.a - 2, int(rtyp[1]))
            if rtyp[0] == 7.7:
                t = (self.z - 2, self.a - 2, int(rtyp[1]))
            self.lchild.append(t)
        pass

    pass

    #
    def fGetLrtyp0(self):
        """return list of rtyp
        generated from the list of tuples
        (rtyp,rfs,q,br)

        it is not used directly by the code,
        it is just called from lisotope.fGetLrtyp0()
        and the output was used to setup isotope.fSetChilds()
        function

        check for changes when ENDF is updated
        """
        l = []
        for rtyp in self.lrtyp:
            l.append(rtyp[0])
        pass
        return l

    pass


pass  # end of isotope


# ******************************************
class lisotope(object):
    """lisotope class --- list of isotope classes"""

    def __init__(self):
        self.l = []  # list of isotope classes
        self.lza = []  # auxiliary list of (z,a,liso) tuples
        self.lt = []  # list of times for activities
        self.lg = []  # lists of indexes of MELCOR element groups for each isotope class
        self.llpower = (
            []
        )  # list of lists of element specific powers, one list per melcor element
        self.lpower = []  # total power
        #
        self.llgamma = None

    pass

    # lisotope
    def fCopyENDFdata(self):
        newlisot = lisotope()
        for isot in self.l:
            newlisot.l.append(isot.fCopyENDFdata())
        pass
        newlisot.lza = self.lza
        newlisot.lg = self.lg
        return newlisot

    pass

    # lisotope
    def fAddSpectraPickle(self, sfn="spectra.pickle", speci=None):
        if speci == None:
            spec = spectrum.spectra()
            spec.fLoadPickle(sfn)
        else:
            spec = speci
        pass
        for lspectrum, cisot in zip(spec.llspectrum, self.l):
            cisot.lspectrum = lspectrum
        pass
        print("Spectra added to isotopes data")

    pass

    # lisotope
    def fGammaSet(self):
        self.llgamma = []
        emin = 10000.0  # 10keV
        xminmax = 5000.0  # discard lines with intensity xminmax times less than maximum
        for i in range(len(self.lt)):
            xmax = 0.0
            lgamma1 = []
            for ciso in self.l:
                if ciso.aacti[i] > 0.0:
                    for spectrum in ciso.lspectrum:
                        if spectrum.styp == 0.0:
                            for sd in spectrum.lsd:
                                x = ciso.aacti[i] * sd.ri * spectrum.fd
                                if x > xmax:
                                    xmax = x
                                if sd.er > emin:
                                    tline = (
                                        sd.er / 1000.0,
                                        x,
                                        ciso.z,
                                        ciso.a,
                                        ciso.liso,
                                    )
                                    lgamma1.append(tline)
                                pass
                            pass
                        pass
                    pass
                pass
            pass
            xmin = xmax / xminmax
            lgamma2 = []
            for tline in lgamma1:
                if tline[1] > xmin:
                    lgamma2.append(
                        (tline[0], tline[1] / xmax, tline[2], tline[3], tline[4])
                    )
                pass
            pass
            lgamma1 = sorted(lgamma2, key=lambda tup: tup[0])
            self.llgamma.append(lgamma1)
        pass

    pass

    # lisotope
    def fGammaPrint(self, sfn="gamma.txt"):
        """print gamma lines of all isotopes at all times"""
        f = open(sfn, "w")
        for time, lgamma in zip(self.lt, self.llgamma):
            f.write("********************************\n")
            f.write("Time = %g s (%g d) \n" % (time, time / (24 * 3600.0)))
            f.write("* E [keV]    y [1]        Isot *\n")
            for tline in lgamma:
                f.write(
                    "%e %e %s \n"
                    % (
                        tline[0],
                        tline[1],
                        g.gcel.fGetOrigenName((tline[2], tline[3], tline[4])),
                    )
                )
            pass
        pass
        f.write("********************************\n")
        f.close()

    pass

    # lisotope
    def fGetLrtyp0(self):
        """return list of rtyp
        generated from the list of tuples
        (rtyp,rfs,q,br)
        ouput is used to code isotope.fSetChilds() function
        """
        l = []
        for ci in self.l:
            l += ci.fGetLrtyp0()
        pass
        l = list(set(l))
        return l

    pass

    # lisotope
    def fPrintMelInc(self, sfn):
        """MELCOR 1.8.6
        output of elements powers
        for DCH input
        to the file sfn
        """
        itf = 999
        # pv121218  nmaxchar=79
        nmaxchar = 70
        fo = open(sfn, "a+")
        for iel, lpower in enumerate(self.llpower):
            iout = 0
            nchar = 2 * nmaxchar
            for xt, p in zip(self.lt, lpower):
                sn = aux.fMelFltStr(xt, p)
                nsn = len(sn)
                if nchar + nsn > nmaxchar:
                    if iout > 0:
                        fo.write("%s\n" % s)
                    pass
                    iout += 1
                    s = "dchnem%02d%02d" % (iel, iout)
                pass
                s = s + sn
                nchar = len(s)
            pass
            fo.write("%s\n" % (s))
        pass
        iout = 0
        fo.write("dchdecpow  tf-%03d\n" % (itf))
        fo.write("tf%03d%02d total-power %d 1.0 0.0\n" % (itf, iout, len(self.lt)))
        nchar = 2 * nmaxchar
        s = ""
        iout = 10
        for xt, p in zip(self.lt, self.lpower):
            sn = aux.fMelFltStr(xt, p)
            nsn = len(sn)
            if nchar + nsn > nmaxchar:
                if iout > 10:
                    fo.write("%s\n" % s)
                iout += 1
                s = "tf%03d%02d" % (itf, iout)
            pass
            s = s + sn
            nchar = len(s)
        pass
        fo.write("%s\n" % (s))
        fo.write("**Obligatory Compounds**\n")
        inext = len(g.gcel.lelmel)
        for dummy, ldumcomp in zip(g.gcel.ldummy, g.gcel.lldumycomp):
            inext += 1
            fo.write("dchnem%02d%02d %s %e\n" % (inext, 0, dummy, 1.0e-9))
            xnorm = 0.0
            lpower = scipy.zeros(len(self.llpower[0]))
            for dumcomp in ldumcomp:
                xnorm += dumcomp[1] * dumcomp[2]
                i = g.gcel.lelmel.index(dumcomp[0])
                lpower += dumcomp[1] * dumcomp[2] * scipy.array(self.llpower[i])
            pass
            lpower = lpower / xnorm
            iout = 0
            iel = inext
            nchar = 2 * nmaxchar
            for xt, p in zip(self.lt, lpower):
                sn = aux.fMelFltStr(xt, p)
                nsn = len(sn)
                if nchar + nsn > nmaxchar:
                    if iout > 0:
                        fo.write("%s\n" % s)
                    pass
                    iout += 1
                    s = "dchnem%02d%02d" % (iel, iout)
                pass
                s = s + sn
                nchar = len(s)
            pass
            fo.write("%s\n" % (s))
        pass
        fo.write("%s\n" % ("."))
        fo.close()

    pass

    # lisotope
    def fAdd(self, ci):
        """add new isotope to the list"""
        self.l.append(ci)

    pass

    # lisotope
    def fPrint(self):
        """debug print"""
        for ci in self.l:
            ci.fPrint()

    pass

    # lisotope
    def fPrintAct(self, lpa, sfn="activity.txt"):
        """print out of activities of selected
        isotopes into column formated ascii file
        """
        laa = []
        for pa in lpa:
            iz = g.gcel.fGetZ(pa)
            ia, isom = g.gcel.fGetA(pa)
            t = (iz, ia, isom)
            i = self.fIndex(t)
            if i >= 0:
                l = self.l[i].aacti.tolist()
                laa.append(l)
            else:
                print("Isotope for output not found: %s" % (pa))
            pass
        pass
        f = open(sfn, "w")
        for i in range(len(self.lt)):
            f.write("%e" % (self.lt[i]))
            for aa in laa:
                f.write(" %e" % (float(aa[i])))
            pass
            f.write("\n")
        pass
        f.close()

    pass

    # lisotope
    def fPrintActCsv(self, lpa, sfn1):
        """print out of activities of selected
        isotopes into a csv file for Nucleonica, in Bq
        """
        xmin = 1.0e-20
        for i in range(len(self.lt)):
            sfn = "%s%04d.csv" % (sfn1, i)
            f = open(sfn, "w")
            f.write("Nuclide,  Activity (Bq)\n")
            for pa in lpa:
                iz = g.gcel.fGetZ(pa)
                ia, isom = g.gcel.fGetA(pa)
                t = (iz, ia, isom)
                j = self.fIndex(t)
                if j >= 0:
                    x = self.l[j].aacti[i]
                    if x > xmin:
                        spa = pa[:1].upper() + pa[1:]
                        f.write("%s, %e\n" % (spa, x))
                    pass
                else:
                    print("Isotope for output not found: %s" % (pa))
                pass
            pass
            f.close()
        pass

    pass

    # lisotope
    def fPrintActInp(self, lpa, sfn1):
        """print out of activities of selected
        isotopes into origen like output, in Bq
        """
        xmin = 1.0e-20
        for i in range(len(self.lt)):
            sfn = "%s%04d.txt" % (sfn1, i)
            f = open(sfn, "w")
            for pa in lpa:
                iz = g.gcel.fGetZ(pa)
                ia, isom = gcel.fGetA(pa)
                t = (iz, ia, isom)
                j = self.fIndex(t)
                if j >= 0:
                    x = self.l[j].aacti[i]
                    if x > xmin:
                        f.write("%s %e\n" % (pa, x))
                    pass
                else:
                    print("Isotope for output not found: %s" % (pa))
                pass
            pass
            f.close()
        pass

    pass

    # lisotope
    def fGetChainInfo(self, s):
        """print out decay chain information for isotopes
        input s (string) is a space separated list of isotope names
        """
        for ss in s.split():
            self.fGetChainInfo1(ss)
        pass

    pass

    # lisotope
    def fGetChainInfo1(self, ss, n=0):
        """print out decay chain information for isotope
        input ss (string) is an isotope name
              n  (integer) should be 0 for parent isotope
                           it is then >0 in recursive calls
                           for childs
        """
        nn = n
        if n > 1000:
            return 1
        pass
        t = g.gcel.fGetZAI(ss)
        i = self.fIndex(t)
        if i < 0:
            print(ss, t, "Not found")
        else:
            print(ss, t)
            if len(self.l[i].lrtyp) != len(self.l[i].lchild):
                self.fSetChilds()
            pass
            pass
            for rtyp, child in zip(self.l[i].lrtyp, self.l[i].lchild):
                print(g.gcel.fGetOrigenName(child), child, rtyp)
                n += 1
            pass
            for child in self.l[i].lchild:
                ii = self.fIndex(child)
                if ii >= 0:
                    self.fGetChainInfo1(g.gcel.fGetOrigenName(child), n)
                pass
            pass
            if nn == 0:
                print("Decay matrix for :", t)
                lch = self.fGetChain(t)
                print(lch)
                print(self.fGetDecayMatrix(lch))
            pass
        pass
        return 0

    pass

    # lisotope
    def fCheckBpBmConflict(self):
        """not used any more"""
        for ci in self.l:
            lBetap = []
            lBetam = []
            for i, rtyp in enumerate(ci.lrtyp):
                if rtyp[0] >= 1.0 and rtyp[0] < 2.0:
                    lBetam.append(i)
                if rtyp[0] >= 2.0 and rtyp[0] < 3.0:
                    lBetap.append(i)
            pass
            if len(lBetam) > 0 and len(lBetap) > 0:
                t = ci.z, ci.a, ci.liso
                print("Beta +- conflict", g.gcel.fGetOrigenName(t), t)
                xBetap = 0.0
                xBetam = 0.0
                for i in lBetam:
                    xBetam += ci.lrtyp[i][3]
                for i in lBetap:
                    xBetap += ci.lrtyp[i][3]
                if xBetam >= xBetap:
                    pass
                pass
            pass
        pass

    pass

    # lisotope
    def fPrintPower(self, sfn="power.txt"):
        """print out of class specific powers (in W/kg)
        and total core power (in W for the whole core)
        into column formated ascii file
        """
        f = open(sfn, "w")
        for i, xtime in enumerate(self.lt):
            f.write("%e" % (float(xtime)))
            for j in range(len(self.llpower)):
                f.write(" %g" % (self.llpower[j][i]))
            pass
            f.write(" %g" % (self.lpower[i]))
            f.write("\n")
        pass
        f.close()

    pass

    # lisotope
    def fPrintTotalPower(self, sfn="powertot.txt", sunit="s"):
        """print out total core power (in W for the whole core)
        into column formated ascii file
        """
        xk = 1.0  # time scale constant, xk=1.0 for seconds
        if sunit == "m":
            xk = 60.0
        elif sunit == "h":
            xk = 3600.0
        elif sunit == "d":
            xk = 3600.0 * 24.0
        elif sunit == "y":
            xk = 3600.0 * 24.0 * 365.2425
        pass
        f = open(sfn, "w")
        for i, xtime in enumerate(self.lt):
            f.write("%g %g\n" % (float(xtime) / xk, self.lpower[i]))
        pass
        f.close()

    pass

    # lisotope
    def fReadENDF(self, sdir=None, bVerbose=True):
        """reads the initial database the ENDF data files
        all data file should be located in the directory
        sdir
        """
        if sdir is None:
            sdir = aux.fPackageDir() + "data-endf"
        pass
        try:
            lf = os.listdir(sdir)
        except:
            print("function lisotope.fReadENDF")
            print('Error reading "%s" folder' % (sdir))
            sys.exit(1)
        pass
        if bVerbose:
            print("ENDF decay data files will be read from:")
            print("%s folder" % (sdir))
            print(
                "Reading ENDF decay data files (. means read, x means stable isotope excluded)"
            )
        pass
        i = 0
        j = 0
        for sfn in lf:
            if sfn[0] == ".":
                continue  # avoid failure due to hidden files
            ci = isotope()
            ci.fReadENDF(sdir + "/" + sfn)
            if ci.t12 == 0.0:
                j += 1
                if bVerbose:
                    sys.stdout.write("x")  # zero half time - discarded isotope
            else:
                if bVerbose:
                    sys.stdout.write(".")  # included radioactive isotope
                self.fAdd(ci)
                i += 1
            if bVerbose:
                sys.stdout.flush()
        pass
        if bVerbose:
            print("\n%4d endf files read" % (i + j))
            print("%4d radioactive isotopes stored" % (i))
            print("%4d stable isotopes discarded" % (j))
        pass

    pass

    #
    def fSavePickle(self, spath=None, bSpectra=True):
        """save the database to a pickle file(s)"""
        if spath is None:
            spath = aux.fPackageDir() + "data-pickle/"
        pass
        sfn = spath + "endf.pickle"
        f = open(sfn, "wb")
        pickle.dump(self.l, f)
        f.close()
        print(sfn, "written")
        if bSpectra:
            sfn = spath + "spectra.pickle"
            spec = spectrum.spectra()
            for cisot in self.l:
                za = (cisot.z, cisot.a, cisot.liso)
                spec.lza.append(za)
                spec.llspectrum.append(cisot.lspectrum)
                cisot.lspectrum = []
            pass
            spec.fSavePickle(sfn)
        pass

    pass

    #
    # def fLoadPickle(self,sfn="endf.pickle",bVerbose=True,bMove=True) :
    # default location is now in ../data-pickle/endf.pickle
    def fLoadPickle(self, sfn=None, bVerbose=True, bMove=True):
        """load the database from the pickle file"""
        if sfn is None:
            sfn = aux.fPackageDir() + "data-pickle/endf.pickle"
        pass

        # 15.04.2015 python3 #f=open(sfn,'r')
        f = open(sfn, "rb")
        self.l = pickle.load(f)
        f.close()
        self.fUpdateLZA()
        # self.fSetupMELCORelgr(bVerbose,bMove)

    pass

    #
    def fUpdateLZA(self):
        """update auxiliary lza index"""
        self.lza = []
        for ci in self.l:
            t = (ci.z, ci.a, ci.liso)
            self.lza.append(t)
        pass

    pass

    #
    def fIndex(self, t):
        """get index of the isotope
        auxiliary index lza is
        updated if necessary
        """
        if len(self.lza) == 0:
            self.fUpdateLZA()
        pass
        if len(self.lza) == 0:
            return -1
        pass
        try:
            i = self.lza.index(t)
        except:
            i = -1
        pass
        return i

    pass

    #
    def fInitializeforDecay(self):
        """create array of zeros to store activities of
        the isotopes in the decay chain
        """
        nt = len(self.lt)
        for ci in self.l:
            ci.aacti = scipy.zeros([nt])
        pass

    pass

    #
    def fResetActi(self, i):
        """sets initial activity to activity at decay time i
        and delete the decay table
        """
        for ci in self.l:
            ci.acti = ci.aacti[i]
            ci.aacti = None
        pass

    pass

    #
    def fSetChilds(self):
        """generate auxiliary index list of childs"""
        for ci in self.l:
            ci.fSetChilds()
        pass

    pass

    #
    def fDecay(self, bChain=True, bVerbose=False):
        """calculate activities for input times"""
        bChainEncountered = False
        if bVerbose:
            print("Calculation of decay chains ...")
        for ci, t in zip(self.l, self.lza):
            if ci.acti > 0.0:
                if bChain:
                    lch = self.fGetChain(t)
                    if len(lch) < 2:
                        ci.fDecay(self.lt)
                    else:
                        self.fDecayChain(lch, bVerbose)
                        bChainEncountered = True
                    pass
                else:
                    ci.fDecay(self.lt)
                pass
            pass
        pass
        if bChainEncountered and bVerbose:
            sys.stdout.write("\n")

    pass

    #
    def fGetDecayMatrix(self, lch):
        """set up decay matrix"""
        n = len(lch)
        em = scipy.zeros([n, n])
        lami = scipy.zeros([n])
        for i in range(n):
            j = self.lza.index(lch[i])
            lam = g.ln12 / self.l[j].t12
            em[i][i] = -1.0 * lam
            lami[i] = lam
            for k in range(len(self.l[j].lchild)):
                try:
                    m = lch.index(self.l[j].lchild[k])
                except:
                    m = -1
                pass
                if m >= 0:
                    em[m][i] = lam * self.l[j].lrtyp[k][3]
                pass
            pass
        pass
        return em, lami

    pass
    pass

    #
    def fDecayChain(self, lch, bVerbose=False):
        """calculate decay chain using matrix exponential"""
        if bVerbose:
            sel = g.gcel.fGetOrigenName(lch[0])
            sys.stdout.write("%s %d" % (sel, len(lch)))
            sys.stdout.flush()
        pass
        n = len(lch)
        em, lami = self.fGetDecayMatrix(lch)
        j = self.fIndex(lch[0])
        aa = scipy.zeros([n])
        aa[0] = self.l[j].acti / float(lami[0])
        ab = scipy.mat(scipy.zeros([n]))
        ab = scipy.zeros([n])
        aa = scipy.mat(aa).transpose()
        self.l[j].aacti[0] = self.l[j].acti
        for i in range(1, len(self.lt)):
            dt = self.lt[i] - self.lt[i - 1]
            if dt > g.dtmin:
                emt = em * dt
                eemx = scipy.mat((scipy.linalg.expm(emt)))
                ab = eemx * aa
            else:
                ab = aa
            pass
            for j in range(n):
                k = self.lza.index(lch[j])
                x = float(ab[j, 0]) * float(lami[j])
                self.l[k].aacti[i] += x
            pass
            aa = ab
        pass
        if bVerbose:
            sys.stdout.write("|")
        pass

    pass

    #
    def fGetChain(self, t):
        """set up decay chain"""
        # avoid recursive infinite decay chain ?
        # check if it is still needed
        lInfi = [
            (36, 100, 0),  # Kr100
            (37, 100, 0),  # Rb100
            (38, 100, 0),  # Sr100
            (39, 100, 0),  # Y100
            (39, 100, 1),  # Y100M
            (40, 100, 0),  # Zr100
            (41, 100, 0),  # Nb100
            (41, 100, 1),  # Nb100M
            (42, 100, 0),  # Mo100
            (43, 100, 0),  # Tc100
            (43, 116, 0),  # Tc116
            (44, 116, 0),  # Ru116
            (45, 116, 0),  # Rh116
            (45, 116, 1),  # Rh116M
            (46, 116, 0),  # Pd116
            (47, 116, 0),  # Ag116
            (47, 116, 1),  # Ag116M
            (47, 116, 2),  # Ag116M
            (47, 128, 0),  # Ag128
            (48, 116, 0),  # Cd116
            (48, 128, 0),  # Cd128
            (49, 116, 0),  # In116
            (49, 128, 0),  # In128
            (49, 128, 1),  # In128M
            (50, 128, 0),  # Sn128
            (50, 128, 1),  # Sn128M
            (51, 128, 0),  # Sb128
            (51, 128, 1),  # Sb128M
            (52, 128, 0),  # Te128
            (53, 128, 0),  # I128
        ]
        ichmaxlen = 10000
        k = 0
        lch = []
        lchn = [t]
        lchnn = []
        while len(lchn) > 0 and len(lch) < ichmaxlen:
            for tt in lchn:
                try:
                    k = lInfi.index(tt)
                except:
                    k = -1
                pass
                if k >= 0:
                    ichmaxlen = 100
                j = self.lza.index(tt)
                for ttt in self.l[j].lchild:
                    i = self.fIndex(ttt)
                    if i >= 0:
                        if self.l[i].t12 > 0.0:
                            lchnn.append(ttt)
                pass
                lch.append(tt)
                if len(lch) >= ichmaxlen and ichmaxlen > 100:
                    print("Decay chain truncated:", g.gcel.fGetOrigenName(t), t)
                    break
                pass
            pass
            lchn = []
            for ttt in lchnn:
                lchn.append(ttt)
            pass
            lchnn = []
        pass
        return lch

    pass

    #
    def fSetupMELCORelgr(self, bVerbose=True, bMove=True):
        """
        set up MELCOR elements groups to calculate power
        """
        if len(self.lza) == 0:
            self.fUpdateLZA()
        pass
        iu = g.gcel.lelmel.index("U")
        self.lg = []
        self.llpower = []
        # lists of specific powers
        for iz in g.gcel.lelmelz:
            l = []
            self.llpower.append(l)
        pass
        # list of melcor elements for each isotope
        if bVerbose:
            print("Isotopes moved to another element:")
        pass
        for i, ci in enumerate(self.l):
            try:
                j = g.gcel.lelmelz.index(ci.z)
            except:
                j = iu
            pass
            if bMove:
                try:
                    k = g.gcel.lmovei.index(self.lza[i])
                except:
                    k = -1
                pass
                if k >= 0:
                    try:
                        jj = g.gcel.lelmel.index(g.gcel.lmove[k][1])
                    except:
                        jj = -1
                    pass
                    if jj >= 0:
                        if bVerbose:
                            print(
                                g.gcel.lmove[k],
                                ": ",
                                j,
                                g.gcel.lelmel[j],
                                " -> ",
                                jj,
                                g.gcel.lelmel[jj],
                            )
                        j = jj
                    pass
                pass
            pass
            self.lg.append(j)
        pass

    pass

    #
    def fScale(self, xk):
        """
        Scale calculated activities by factor xk
        xk is the ratio of core mass to irradiated mass
        """
        for ci in self.l:
            ci.aacti = xk * ci.aacti
        pass

    pass

    def fPower(self, elmass):
        """calculate specific power of elements and total power of the core
        elmass is element class -- masses in the core
        (converted already in config.fReadMasses())
        activities are in Bq in the core
        (scaled by fScale)
        """
        n = len(self.lt)
        self.lpower = scipy.zeros([n])
        for i in range(len(self.llpower)):
            self.llpower[i] = scipy.zeros([n])
        for ci, gi in zip(
            self.l, self.lg
        ):  # ci is isotope, gi is melcor element index for this isotope
            iz = g.gcel.lelmelz[
                gi
            ]  # iz is Z of MELCOR element group gi, ci belongs to group gi
            ed = g.xeVJ * ci.fEnergy()
            for i in range(n):  # loop over all time points
                p = ed * float(ci.aacti[i])
                if elmass[iz - 1] > 0.0:
                    self.llpower[gi][i] += (
                        p / elmass[iz - 1]
                    )  # in W/(1kg of FP el), H with iz=1 has index 0!
                self.lpower[i] += p  # in W in whole core
            pass
        pass

    pass

    #
    def fSetActivities(self, lcacti):
        """set activities from ORIGEN output"""
        lig = []
        for cacti in lcacti.l:
            t = (cacti.z, cacti.a, cacti.isomer)
            i = self.fIndex(t)
            if i >= 0:
                self.l[i].acti = cacti.x
            else:
                lig.append(cacti.abr)
            pass
        pass
        return lig

    pass


pass


# end of lisotope class
# ******************************************
class llisotope:
    """llisotope class --- list of lisotope classes"""

    def __init__(self):
        self.l = []

    pass

    def fSum(self, cli):
        """create new lisotope instance and
        calculate sum of activities for each isotope
        """
        # cli = lisotope()
        # if g.bPickle:
        # cli.fLoadPickle(bVerbose=True)
        # else:
        # cli.fReadENDF()
        # cli.fUpdateLZA()
        # pass
        for i in range(len(cli.l)):
            for clii in self.l:
                cli.l[i].acti += clii.l[i].acti
        return cli

    pass


pass
# end of llisotope class

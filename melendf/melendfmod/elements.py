#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string


class elements(object):
    """elements class,
    auxiliary class for

    conversion between: element abbreviation <-> Z

    distribution of elements to MELCOR groups

    """

    def __init__(self):
        # list of elements ordered according to Z

        line1 = ["H", "He"]
        line2 = ["Li", "Be", "B", "C", "N", "O", "F", "Ne"]
        line3 = ["Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar"]
        metals1 = ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"]
        metals2 = ["Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd"]
        line4 = ["K",  "Ca", *metals1, "Ga", "Ge", "As", "Se", "Br", "Kr"]
        line5 = ["Rb", "Sr", *metals2,  "In", "Sn", "Sb", "Te", "I", "Xe"]
        lanthanides = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb"]
        metals3 = ["Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"]
        line6 = ["Cs", "Ba", *lanthanides, *metals3, "Tl", "Pb", "Bi", "Po", "At", "Rn"]
        metals4 = ["Lr", "Ku", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn"]
        actinides = ["Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No"]
        line7 = ["Fr", "Ra", *actinides, *metals4]
        self.labr = [
            *line1,
            *line2,
            *line3,
            *line4,
            *line5,
            *line6,
            *line7
        ]
        # output will be calculated only for selected MELCOR elements
        self.lelmel = [
            "Kr", "Xe", "Rb", "Cs", "Sr", "Ba", "Br", "I",
            "Se", "Te", "Ru", "Rh", "Pd", "Nb", "Mo", "Tc",
            "Zr", "Ce", "Np", "Pu", "Y", "La", "Pr", "Nd",
            "Pm", "Sm", "Eu", "U", "Ag", "Sn", "As", "Sb",
            "Cd", "Am", "Cm"
        ]
        # isotopes to move, the first guess from ori2003 and update for endf.py in 2012
        self.lmove = [
            ("CU66  ", "Ni"),
            ("SE77M ", "As"),
            ("SE79M ", "As"),
            ("KR83M ", "Br"),
            ("Y89M  ", "Sr"),
            ("Y90   ", "Sr"),
            ("Y91M  ", "Sr"),
            ("NB95  ", "Zr"),
            ("NB95M ", "Zr"),
            ("NB97  ", "Zr"),
            ("NB97M ", "Zr"),
            #   ("TC99M ","Mo"), #removed
            ("TC103 ", "Mo"),  # new
            ("AG109M", "Pd"),
            ("AG111M", "Pd"),
            ("AG112 ", "Pd"),
            ("IN115M", "Cd"),
            ("IN117 ", "Cd"),
            ("IN117M", "Cd"),
            ("IN118 ", "Cd"),
            ("XE134M", "I"),
            ("BA136M", "Cs"),
            ("BA137M", "Cs"),
            ("HO166 ", "Dy"),
            ("W183M ", "Ta"),
            ("RE188 ", "W"),
            ("RB90 ", "Kr"),  # new
            ("RB88 ", "Kr"),  # new
            ("I132", "Te"),  # new
            ("RH106", "Ru"),  # new
            ("PR144", "Ce"),  # new
            ("PR144M", "Ce"),  # new
            ("RH103M", "Ru"),  # new
            ("RH105M", "Ru"),  # new
            ("RH106", "Ru"),  # new
            ("RH100", "Pd"),  # new
        ]
        #
        self.lmovei = []  # list of tuples Z,A,isomer for moved isotopes
        for move in self.lmove:
            t = self.fGetZAI(move[0])
            self.lmovei.append(t)
        pass
        #
        self.lelmelz = []  # Z for each melcor element group
        for el in self.lelmel:
            i = self.labr.index(el) + 1
            self.lelmelz.append(i)
        pass
        #
        # list of dummy compounds
        self.ldummy = ["CI"]
        # list of lists of dummy compound recipe: tuple of name, weight in compound, average element mass number
        self.lldumycomp = [[("Cs", 1.0, 133), ("I", 1.0, 127)]]

    pass

    def fPrint(self):
        """print out the data for checking"""
        for i, sabr in enumerate(self.labr):
            print("%3d %2s" % (i + 1, sabr))
        pass

    pass

    def fPrintMELCORElements(self):
        """information print of MELCOR elements and compounds"""
        print("MELCOR elements list")
        for i, sel in enumerate(self.lelmel):
            print("%2d %s" % (i + 1, sel))
        pass
        print("MELCOR compounds")
        for i, (sdummy, ldc) in enumerate(zip(self.ldummy, self.lldumycomp)):
            print("%2d %s, composed of" % (i + 1, sdummy))
            for t in ldc:
                print("%10s fraction %g mass %g " % t)
        pass

    pass

    def fGetZ(self, s):
        """return element Z for given element abbreviation,
        works with ORIGEN isotope format:
        N[N]X[X][X][M]
        where N is letter
              X is number
              M is isomer indicator
        character in [] is optional

        when the element is not recognized,
        return -1
        """
        sab = s.strip()
        if sab == "SUMTOT":
            i = -1
            return i
        pass
        sab = sab[:2]
        if len(sab) < 2:
            i = -1
            return i
        pass
        # s1=string.ascii_uppercase(sab[0])
        s1 = sab[0].upper()
        # i = string.letters.find(sab[1])
        i = string.ascii_letters.find(sab[1])
        if i < 0:
            s2 = ""
        else:
            # s2=string.lower(sab[1])
            s2 = sab[1].lower()
        pass
        sab = s1 + s2
        try:
            i = self.labr.index(sab) + 1
        except:
            i = -1
        pass
        return i

    pass

    def fGetA(self, s):
        """return element A and isomer state
        for given element abbreviation,
        works with ORIGEN isotope format:
        N[N]X[X][X][M]
        where N is letter
              X is number
              M is isomer indicator
        character in [] is optional

        when the element is not recognized,
        return -1
        """
        sab = s.strip()
        iIsomer = 0
        if len(sab) >= 2:
            if sab[-1] == "M" or sab[-1] == "m":
                iIsomer = 1
                sab = sab[:-1]
            else:
                iIsomer = 0
            pass
            if len(sab) < 2:
                return (-1, 0)
            pass
            i = 1
            # j = string.letters.find(sab[i])
            j = string.ascii_letters.find(sab[i])
            if j >= 0:
                i += 1
            pass
            sab = sab[i:]
            try:
                i = int(sab)
            except:
                i = -1
            pass
        else:
            i = -1
        pass
        return (i, iIsomer)

    pass

    def fGetZAI(self, s):
        """input origen isotope name
        return Z,A,isomer
        """
        iz = self.fGetZ(s)
        ia, ii = self.fGetA(s)
        return iz, ia, ii

    pass

    def fGetAbr(self, iz):
        """return element abbreviation
        for given element Z
        """
        i = iz - 1
        if i < len(self.labr) and i >= 0:
            s = self.labr[i]
        else:
            s = "none"
        pass
        return s

    pass

    def fGetOrigenName(self, t):
        """get ORIGEN isotope name
        input T is the tuple of integers containing
        Z,A,isomer
        """
        sel = self.fGetAbr(t[0])
        sa = "%d" % (t[1])
        sm = " "
        if t[2] > 0:
            sm = "M"
        return sel + sa + sm

    pass


pass

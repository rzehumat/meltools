#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 python module for browseptf.py 
 written by Petr Vokac, UJV Rez, a.s.
 December 2008
 License: as-is

changes:
 12.1.2009: added (lVarFLValv,lFLV), FL-V-N-OC moved to lVarFLValv
 16.1.2009: added (lVarCFVALU,lCFVALU )
 19.5.2009: initiate iCORR=0
  9.3.2011: comments, clean up
 13.2.2012: fListVar replaced by fReadVarKey
  5.4.2012: fGetRN1Class to treat FPs classes from auxiliary file rn1class.txt
 22.9.2017: fGetRN1Class removed: RN1 class names read from MELPTF 
"""

import subprocess as subp
import sys

# from operator import itemgetter, attrgetter

# global lists
lVarKey = []  # list of tuples: (variable name, dimension, list of key)
# initiated in fInitiate

lvar1 = []  # list of variables, variable name [ + dot key ]
# initiated in fInitiate

lpGnuPlot = []  # list of pointers to gnuplot instances
lVarIndex = []  # list of tuples ( list of variables, list of description )
lVarNCG = []  # list of variables concerning NCG

# global lists of variables
lCor = []  # list of core nodes in melcor notation (strings)
lCv = []  # list of cvh volumes, strings: "cvxxx (volume name)"
lFl = []  # list of flow paths, strings: "fl%03d cv:%03d->%03d"
lHS = []  # list of heat structures, and hs nodes (strings)
lHS1 = []  # list of heat structures (strings)
lFLV = []  # list valve-flowpath
lCFVALU = []  # list of control function names
lFLBLK = []  # list of flowpaths with blockages
lCorCvh = []  # list of core cvhs
lCFnumbers = []  # list of valid CF numbers from index
lFL_FRUNBLK = []  # list of valid flowpath numbers with blockages from index
lTYCTL = []  # list of cvh volume types for RN1
lNCG = []  # list of NCG materials
lRN1Class = []  # list of RN classes


# definition of functions
def fPytVer():
    """return string with python version"""
    t = sys.version_info
    s = "%d.%d.%d" % (t[0], t[1], t[2])
    return s


pass


def fPriRun():
    """print info about python and plaform"""
    s1 = fPytVer()
    s = "Running Python %s on %s" % (s1, sys.platform)
    print(s)


pass


def fCheckMELPTF(sptf="MELPTF"):
    """check existence of the MELPTF file"""
    try:
        f = open(sptf, "r")
        f.close
        print("%s exists, go on ... " % (sptf))
        return 1
    except:
        print("file %s is not in the current folder!" % (sptf))
        print("Make a link to MELCOR plot file in the current folder and try again.")
        print("or you can rename default MELPTF by the first command line argument")
        print("")
        return 0
    pass


pass


def fCheckGnuplot():
    """check whether gnuplot is present in the system"""
    # check sys.platform here if necessary
    sgnuplot = "gnuplot"
    #
    p = subp.Popen(
        [sgnuplot, "--version"], stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.STDOUT
    )
    s = ""
    for line in p.stdout:
        s = line.strip().decode("utf-8")
    pass
    print(s)


pass


def fReadVarKey(sptf="MELPTF"):
    """reads list of variables from MELPTF"""
    bVarNext = True
    p = subp.Popen(
        ["readptf.exe", sptf, "index"],
        stdin=subp.PIPE,
        stdout=subp.PIPE,
        stderr=subp.STDOUT,
    )
    l = []
    for line in p.stdout:
        if bVarNext:
            svar = line.strip().decode("UTF-8")
            bVarNext = False
            li = []
        else:
            s = line.decode("UTF-8").split()
            for ss in s:
                if ss == "*":
                    l.append((svar, len(li), li))
                    bVarNext = True
                    break
                else:
                    try:
                        li.append(int(ss))
                    except:
                        pass
                pass
        pass
    pass
    # return sorted(l, key=itemgetter(0))
    return sorted(l)


pass


def fInitVarIndex():
    """reads variable index from binary file
    currently deals just with:
      CFVALU list lCFnumbers,
      FL-FRUNBLK list lFL_FRUNBLK
      COR-QCNV list lCorCvh
    it could be generalized later"""
    # output to global lists
    global lCFnumbers, lFL_FRUNBLK, lCorCvh, lVarKey, lvar1
    for tvar in lVarKey:
        if "FL-FRUNBLK" == tvar[0]:
            for i in tvar[2]:
                lFL_FRUNBLK.append(i)
            pass
        pass
        if "CFVALU" == tvar[0]:
            for i in tvar[2]:
                lCFnumbers.append(i)
            pass
        pass
        if "COR-QCNV" == tvar[0]:
            for i in tvar[2]:
                lCorCvh.append(i)
            pass
        pass
    pass
    for tvar in lVarKey:
        if tvar[1] < 2 and tvar[2][0] > 0:
            s = "%s.%d" % (tvar[0], tvar[2][0])
        else:
            if tvar[1] < 2:
                s = tvar[0]
            else:
                s = tvar[0] + "."
            pass
        pass
        lvar1.append(s)
    pass


pass


def fSP(sptf="MELPTF"):
    """reads .SP/ section from binary file"""
    global lTYCTL, lNCG, lFL_FRUNBLK, lHS, lHS1, lFl, lFLV, lCFVALU, lFLBLK, lRN1Class
    sCORR = " COR-NUMBER-RADIAL-RINGS((0))"
    sCORA = " COR-NUMBER-AXIAL-SEGMENTS((0))"
    sCVHV = " CVH-VOLUME-NAME(("
    sFLPN = " FL-PATH-NUMBER(("
    lifl = []
    sFLPFROM = " FL-PATH-FROM(("
    lFLPFROM = []
    sFLPTO = " FL-PATH-TO(("
    lFLPTO = []
    sHSN = " HS-NAME(("
    sHSi = " HS-NUMBER-OF-NODES(("
    sFLV = " FL-VALVED-PATH(("
    sCFnu = " CF-FUNCTION-NUMBER(("
    sCFna = " CF-FUNCTION-NAME(("
    sCVHTypeName = " CVH-TYPE-NAME(("
    sNCG = " NCG-MATERIAL(("
    sRN1CLASSNAME = "RN1-CLASS-NAME(("
    lHSi = []  # number of hs nodes, temporary list local to fSP
    p = subp.Popen(
        ["readptf.exe", sptf, "sp"],
        stdin=subp.PIPE,
        stdout=subp.PIPE,
        stderr=subp.STDOUT,
    )

    iCORR = 0  # avoid error if no core in the output
    iCORA = 0
    for bline in p.stdout:
        # print line[:len(sCORR)]
        line = bline.decode("UTF-8")
        if line[: len(sCORR)] == sCORR:
            iCORR = int(float(line[len(sCORR) :]))
            continue
        if line[: len(sCORA)] == sCORA:
            iCORA = int(float(line[len(sCORA) :]))
            continue
        if line[: len(sCVHV)] == sCVHV:
            s = line[len(sCVHV) :].split(")")
            i = int(s[0])
            ss = s[2].rstrip().lower()
            sss = "cv%03d" % (i)
            if ss != sss:
                lCv.append("%s (%s)" % (sss, ss))
            else:
                lCv.append(sss)
            pass
            continue
        # flow path number
        if line[: len(sFLPN)] == sFLPN:
            s = line[len(sFLPN) :].split(")")
            x = float(s[-1])
            ifl = int(x)
            lifl.append(ifl)
            continue
        # flow path from
        if line[: len(sFLPFROM)] == sFLPFROM:
            s = line[len(sFLPFROM) :].split(")")
            x = float(s[-1])
            i = int(x)
            lFLPFROM.append(i)
            continue
        # flow path to
        if line[: len(sFLPTO)] == sFLPTO:
            s = line[len(sFLPTO) :].split(")")
            x = float(s[-1])
            i = int(x)
            lFLPTO.append(i)
            continue
        if line[: len(sHSN)] == sHSN:
            s = line[len(sHSN) :].split(")")
            i = int(s[0])
            ss = s[2].rstrip().lower()
            sss = "%05d" % (i)
            if ss != sss:
                lHS1.append("%s (%s)" % (sss, ss))
            else:
                lHS1.append(sss)
            pass
            continue
        if line[: len(sHSi)] == sHSi:
            s = line[len(sHSi) :].split(")")
            i = int(float(s[-1]))
            lHSi.append(i)
            continue
        if line[: len(sFLV)] == sFLV:
            s = line[len(sFLV) :].split(")")
            i = int(s[0])
            xfl = float(s[2].rstrip())
            ifl = int(xfl)
            lFLV.append("v%02d(fl%03d)" % (i, ifl))
            continue
        # currently not used - may be later to check cf ordering consistency
        # if line[:len(sCFnu)]==sCFnu :
        # s=line[len(sCFnu):].split(")")
        # i = int (s[0])
        # xcf = float (s[2].rstrip())
        # icf=int (xcf)
        # lCFVALU.append("%d cf%d" % (i,icf))
        # continue

        if line[: len(sCFna)] == sCFna:
            s = line[len(sCFna) :].split(")")
            i = int(s[0])
            if len(s) > 3:
                sn = ")".join(s[2:]).rstrip()
            else:
                sn = s[2].rstrip()
            pass
            if i in lCFnumbers:
                lCFVALU.append("cf%d %s" % (i, sn))
            continue

        if line[: len(sCVHTypeName)] == sCVHTypeName:
            s = line[len(sCVHTypeName) :].split(")")
            i = int(s[0])
            sn = s[2].rstrip()
            s = "%02d %s" % (i, sn)
            lTYCTL.append(s)
            continue
        pass

        if line.strip()[: len(sRN1CLASSNAME)] == sRN1CLASSNAME:
            s = line.strip()[len(sRN1CLASSNAME) :].split(")")
            i = int(s[0])
            sn = s[2].rstrip()
            s = "%02d %s" % (i, sn)
            lRN1Class.append(s)
            continue
        pass

        if line[: len(sNCG)] == sNCG:
            s = line[len(sNCG) :].split(")")
            i = int(s[0])
            sn = s[2].rstrip()
            lNCG.append(sn)
        pass

    pass

    # setup flowpaths
    for i in range(len(lifl)):
        sss = "fl%03d cv:%03d->%03d" % (lifl[i], lFLPFROM[i], lFLPTO[i])
        lFl.append(sss)
        if lifl[i] in lFL_FRUNBLK:
            lFLBLK.append(sss)
    pass

    for ir in range(iCORR):
        for ia in range(iCORA):
            s = "%d%02d" % (ir + 1, ia + 1)
            lCor.append(s)
        pass
    pass

    for i, sHS in enumerate(lHS1):
        j = lHSi[i]
        for k in range(j):
            lHS.append("%s %02d" % (sHS, k + 1))
        pass
    pass

    # for 185 - function names are not in /sp
    if len(lCFVALU) == 0:
        for i in lCFnumbers:
            lCFVALU.append("cf%d" % (i))
        pass
    pass

    lTYCTL.sort()
    lNCG.append("TOTAL")


pass


def fTitle(sptf="MELPTF"):
    """get sequence title from the binary file"""
    p = subp.Popen(
        ["readptf.exe", sptf, "list"],
        stdin=subp.PIPE,
        stdout=subp.PIPE,
        stderr=subp.STDOUT,
    )
    ss = ""
    for line in p.stdout:
        ss = line.strip()
        if len(ss) > 0:
            break
        pass
    pass
    p.stdin.close()
    return ss


pass


def fPlot(
    strplt="\nplot cos(x)\n",
    lcp=0,
    sTitle="",
    sfT='fT(x)=x/3600.0\nset xlabel "Time [h]"\n',
):
    """sends command string to gnuplot"""
    global lpGnuPlot
    while len(lpGnuPlot) < lcp + 1:
        fNewPlot(sTitle, sfT)
    pass
    pGnuplot = lpGnuPlot[lcp]
    # rint(strplt)
    # pGnuplot.stdin.write(bytes(strplt, 'UTF-8'))
    pGnuplot.stdin.write(strplt.encode("utf-8"))
    pGnuplot.stdin.flush()


pass


def fFormatVar(lVar, sptf="MELPTF"):
    """prepares gnuplot command string
    from list of variables"""
    pltstr = "\nplot \\\n"
    pltstr0 = pltstr
    sp1 = ""
    sap = '\\"'
    # sdap='.\\\"' # dot moved to fInit
    sdap = '\\"'
    for sVarwi in lVar:
        sVarv = sVarwi.split()
        sVar = sVarv[0]
        pltstr1 = ""
        iOK = -1
        try:
            iOK = lvar1.index(sVar)
        except:
            # print "Variable %s does not exist!" % (sVar)
            pass
        pass
        if iOK >= 0:
            pltstr1 = (
                '"< readptf.exe %s %s%s%s " using (fT($1)):2 title "%s" with lines'
                % (sptf, sap, sVar, sap, sVar)
            )
        else:
            ss = sVar.split("#")
            sss = ss[0]
            iOK = -1
            try:
                iOK = lvar1.index(sss)
            except:
                print("Variable %s does not exist!" % (sss))
            pass
            try:
                iv = int(ss[-1])
            except:
                iOK = -1
            pass
            if iOK >= 0:
                if len(sVarv) > 3:
                    pltstr1 = (
                        '"< readptf.exe %s %s%s%s " using (fT($1)):%d title "%s %s %s" with lines'
                        % (sptf, sap, sss, sdap, iv + 1, sss, sVarv[1], sVarv[3])
                    )
                else:
                    if len(sVarv) > 1:
                        pltstr1 = (
                            '"< readptf.exe %s %s%s%s " using (fT($1)):%d title "%s %s" with lines'
                            % (sptf, sap, sss, sdap, iv + 1, sss, sVarv[1])
                        )
                    else:
                        pltstr1 = (
                            '"< readptf.exe %s %s%s%s " using (fT($1)):%d title "%s#%d" with lines'
                            % (sptf, sap, sss, sdap, iv + 1, sss, iv)
                        )
                    pass
                pass
            else:
                try:
                    bOK = ss[-1] == "max"
                except:
                    bOK = 0
                pass
                if bOK:
                    pltstr1 = (
                        '"< readptf.exe %s %s%s%s 2 " using (fT($1)):2 title "MAX %s" with lines'
                        % (sptf, sap, sss, sdap, sss)
                    )
                    iOK = 1
                else:
                    try:
                        bOK = ss[-1] == "min"
                    except:
                        bOK = 0
                    pass
                    if bOK:
                        pltstr1 = (
                            '"< readptf.exe %s %s%s%s 2 " using (fT($1)):3 title "MIN %s" with lines'
                            % (sptf, sap, sss, sdap, sss)
                        )
                        iOK = 1
                    else:
                        try:
                            bOK = ss[-1] == "min0"
                        except:
                            bOK = 0
                        pass
                        if bOK:
                            pltstr1 = (
                                '"< readptf.exe %s %s%s%s 3 " using (fT($1)):3 title "(MIN>0) %s" with lines'
                                % (sptf, sap, sss, sdap, sss)
                            )
                            iOK = 1
                        else:
                            try:
                                bOK = ss[-1] == "sum"
                            except:
                                bOK = 0
                            pass
                            if bOK:
                                pltstr1 = (
                                    '"< readptf.exe %s %s%s%s 4 " using (fT($1)):2 title "Sum %s" with lines'
                                    % (sptf, sap, sss, sdap, sss)
                                )
                                iOK = 1
                            pass
                        pass
                    pass
                pass
            pass
        pass
        if iOK >= 0:
            pltstr = pltstr + sp1 + pltstr1
            sp1 = ", \\\n"
        pass
    pass
    pltstr = pltstr + "\n"
    pass
    return pltstr


pass


def fInitiate(sptf="MELPTF"):
    """checks environment,
    reads variable names from the plot file
    initiate browser variables
    """
    global lVarKey
    print("")
    fPriRun()
    fCheckGnuplot()
    if fCheckMELPTF(sptf=sptf):
        lVarKey = fReadVarKey(sptf=sptf)
        fInitVarIndex()
        fSP(sptf=sptf)
        fInitLists()
    pass
    return fTitle(sptf)


pass


def fGnuplotTerm(st1):
    """select gnuplot terminal type
    added 11.4.2018
    """
    if sys.platform == "win32":
        sgt = 'set term wxt title "%s"\n' % (st1)
    elif sys.platform == "darwin":
        sgt = 'set term aqua title "%s"\n' % (st1)
    else:
        sgt = 'set term x11 title "%s"\n' % (st1)
    pass
    return sgt


pass


def fNewPlot(sTitle, sfT='fT(x)=x/3600.0\nset xlabel "Time [h]"\n'):
    """initialize new gnuplot instance,
    checks sys.platform to select terminal,
    wxt for win32
    X11 for Linux
    aqua for OS X Darwin
    """
    global lpGnuPlot
    #
    sgnuplot = "gnuplot"
    # pGnuPlot = subp.Popen([sgnuplot], stdin=subp.PIPE, shell=True)
    pGnuPlot = subp.Popen([sgnuplot], stdin=subp.PIPE)
    pGnuPlot.stdin.write("set grid\n".encode("utf-8"))
    pGnuPlot.stdin.write(sfT.encode("utf-8"))
    lpGnuPlot.append(pGnuPlot)
    ip = len(lpGnuPlot)
    s = sTitle.split()
    if "Plot" in s:
        st1 = sTitle.decode("utf-8")
    else:
        st1 = "%s - Plot %d" % (sTitle.decode("utf-8"), ip)
    pass
    # 11.4.2018
    sgt = fGnuplotTerm(st1)
    pGnuPlot.stdin.write(sgt.encode("utf-8"))
    return st1


pass


def fGetRN1Class():
    """if there is file rn1class.txt
    present in the current folder,
    it tries to read it

    each line in the rn1class.txt file
    should be RN1 class name

    """
    l = []
    sfn = "rn1class.txt"
    try:
        print("Trying to find rn1class.txt with RN1 classes definition ...")
        f = open(sfn, "r")
    except:
        print("rn1class.txt not found, I will use default 16 classes")
        return None
    pass
    for line in f:
        l.append(line.strip())
    pass
    f.close()
    return l


pass


def fInitLists():
    """initialises global lists

    lVarIndex is list of tuples containing two items:
     list of variables
     list of index interpretation

    some lists are fixed for now:
     list of RN clases
    """
    global lVarIndex, lVarNCG, lRN1Class
    # removed 170922
    # l = fGetRN1Class()
    # if l==None :
    # # radionuclide classes DCH-RM-8, fixed for now
    # lRN1Class = [
    # "Noble-Gases",        # 1
    # "Alkali-Metals",      # 2
    # "Alkaline-Earths",    # 3
    # "Halogens",           # 4
    # "Chalcogens",         # 5
    # "Platinoids",         # 6
    # "Transitions Metals",  # 7
    # "Tetravalens",        # 8
    # "Trivalents",         # 9
    # "Uranium",            #10
    # "More-Volatile",      #11
    # "Less-Volatile",      #12
    # "Boron",              #13
    # "Water",              #14
    # "Concrete",           #15
    # "CsI" ]                #16
    # else :
    # lRN1Class=l
    # pass
    #
    # following lists were prepared by hand using :
    # readptf.exe MELPTF list > list.txt
    # awk 'BEGIN {i=0;sv=""} {if (($2-i)>1) printf("\"%s\",\n", sv) ; i=$2;sv=$1}' list.txt > vars.txt
    #

    # variables for all flowpaths
    lVarFL = [
        "FL-VELLIQ",
        "FL-VELVAP",
        "FL-MFLOW",
        "FL-MFLOW.1",
        "FL-MFLOW.2",
        "FL-MFLOW.3",
        "FL-MFLOW.4",
        "FL-MFLOW.5",
        "FL-MFLOW.6",
        "FL-MFLOW.7",
        "FL-MFLOW.8",
        "FL-MFLOW.9",
        "FL-MFLOW.10",
        "FL-I-MFLOW.1",
        "FL-I-MFLOW.2",
        "FL-I-MFLOW.3",
        "FL-I-MFLOW.4",
        "FL-I-MFLOW.5",
        "FL-I-MFLOW.6",
        "FL-I-MFLOW.7",
        "FL-I-MFLOW.8",
        "FL-I-MFLOW.9",
        "FL-I-MFLOW.10",
        "FL-I-H2O-MFLOW",
        "FL-VOID",
        "FL-EFLOW.P",
        "FL-EFLOW.A",
        "FL-I-EFLOW.P",
        "FL-I-EFLOW.A",
    ]

    # variables for blocked flowpaths
    lVarFLBLK = ["FL-FRUNBLK"]

    # variables for all valves
    lVarFLValv = ["FL-V-N-OC"]

    # cvh variables
    lVarCVH = [
        "CVH-P",
        "CVH-RHO",
        "CVH-RHO.1",
        "CVH-RHO.2",
        "CVH-RHO.3",
        "CVH-RHO.4",
        "CVH-RHO.5",
        "CVH-RHO.6",
        "CVH-RHO.7",
        "CVH-RHO.8",
        "CVH-RHO.9",
        "CVH-RHO.10",
        "CVH-E",
        "CVH-E.1",
        "CVH-E.2",
        "CVH-E.3",
        "CVH-E.4",
        "CVH-E.5",
        "CVH-E.6",
        "CVH-E.7",
        "CVH-E.8",
        "CVH-E.9",
        "CVH-E.10",
        "CVH-TLIQ",
        "CVH-TVAP",
        "CVH-MASS",
        "CVH-MASS.1",
        "CVH-MASS.2",
        "CVH-MASS.3",
        "CVH-MASS.4",
        "CVH-MASS.5",
        "CVH-MASS.6",
        "CVH-MASS.7",
        "CVH-MASS.8",
        "CVH-MASS.9",
        "CVH-MASS.10",
        "CVH-X.3",
        "CVH-X.4",
        "CVH-X.5",
        "CVH-X.6",
        "CVH-X.7",
        "CVH-X.8",
        "CVH-X.9",
        "CVH-X.10",
        "CVH-VOLLIQ",
        "CVH-VOLFOG",
        "CVH-VOLVAP",
        "CVH-CVOLLIQ",
        "CVH-ECV",
        "CVH-ECV.1",
        "CVH-ECV.2",
        "CVH-ECV.3",
        "CVH-ECV.4",
        "CVH-ECV.5",
        "CVH-ECV.6",
        "CVH-ECV.7",
        "CVH-ECV.8",
        "CVH-ECV.9",
        "CVH-ECV.10",
        "CVH-VELLIQCV",
        "CVH-VELVAPCV",
        "CVH-LIQLEV",
        "CVH-CLIQLEV",
        "CVH-PPART.1",
        "CVH-PPART.2",
        "CVH-PPART.3",
        "CVH-PPART.4",
        "CVH-PPART.5",
        "CVH-PPART.6",
        "CVH-PPART.7",
        "CVH-PPART.8",
        "CVH-PPART.9",
        "CVH-PPART.10",
        "CVH-QUALITY",
        "CVH-TSAT(P)",
        "CVH-TSAT(A)",
        "CVH-PSAT(TLIQ)",
        "CVH-PSAT(TVAP)",
        "CVH-ATM-FR",
        "CVH-VOID-P",
        "CVH-VOID-T",
        "CVH-H",
        "CVH-H.1",
        "CVH-H.2",
        "CVH-H.3",
        "CVH-H.4",
        "CVH-H.5",
        "CVH-H.6",
        "CVH-H.7",
        "CVH-H.8",
        "CVH-H.9",
        "CVH-H.10",
        "CVH-VIRVOLIQ",
        "CVH-VIRVOVAP",
        "RN1-ATMG",
        "RN1-ARMG",
        "RN1-VTMG",
        "RN1-VRMG",
        "RN1-ATML",
        "RN1-ARML",
        "RN1-VTML",
        "RN1-VRML",
        "RN1-XMRLSE-1-1",
        "RN1-XMRLSE-1-2",
        "RN1-XMRLSE-1-3",
        "RN1-XMRLSE-2-1",
        "RN1-XMRLSE-2-2",
        "RN1-XMRLSE-2-3",
        "RN1-XMRLSE-3-1",
        "RN1-XMRLSE-3-2",
        "RN1-XMRLSE-3-3",
        "RN1-XMRLSE-4-1",
        "RN1-XMRLSE-4-2",
        "RN1-XMRLSE-4-3",
        "RN1-XMRLSE-5-1",
        "RN1-XMRLSE-5-2",
        "RN1-XMRLSE-5-3",
        "RN1-XMRLSE-6-1",
        "RN1-XMRLSE-6-2",
        "RN1-XMRLSE-6-3",
        "RN1-XMRLSE-7-1",
        "RN1-XMRLSE-7-2",
        "RN1-XMRLSE-7-3",
        "RN1-XMRLSE-8-1",
        "RN1-XMRLSE-8-2",
        "RN1-XMRLSE-8-3",
        "RN1-XMRLSE-9-1",
        "RN1-XMRLSE-9-2",
        "RN1-XMRLSE-9-3",
        "RN1-XMRLSE-10-1",
        "RN1-XMRLSE-10-2",
        "RN1-XMRLSE-10-3",
        "RN1-XMRLSE-11-1",
        "RN1-XMRLSE-11-2",
        "RN1-XMRLSE-11-3",
        "RN1-XMRLSE-12-1",
        "RN1-XMRLSE-12-2",
        "RN1-XMRLSE-12-3",
        "RN1-XMRLSE-13-1",
        "RN1-XMRLSE-13-2",
        "RN1-XMRLSE-13-3",
        "RN1-XMRLSE-14-1",
        "RN1-XMRLSE-14-2",
        "RN1-XMRLSE-14-3",
        "RN1-XMRLSE-15-1",
        "RN1-XMRLSE-15-2",
        "RN1-XMRLSE-15-3",
        "RN1-XMRLSE-16-1",
        "RN1-XMRLSE-16-2",
        "RN1-XMRLSE-16-3",
        "RN1-MMDW",
        "RN1-GSDW",
        "RN1-MMDD",
        "RN1-GSDD",
        "RN1-MMDC-1",
        "RN1-MMDC-2",
        "RN1-GSDC-1",
        "RN1-GSDC-2",
        "RN1-PH",
        "BUR-N-SE",
        "BUR-O2-RAT",
        "BUR-O2-TOT",
        "BUR-H2-RAT",
        "BUR-H2-TOT",
        "BUR-D2-RAT",
        "BUR-D2-TOT",
        "BUR-CO-RAT",
        "BUR-CO-TOT",
        "BUR-H2O-RAT",
        "BUR-H2O-TOT",
        "BUR-CO2-RAT",
        "BUR-CO2-TOT",
        "BUR-POWER",
        "BUR-ENERGY",
    ]

    lVarHS = ["HS-TEMP"]

    lVarHS1 = [
        "HS-ENERGY-INPUT",
        "HS-ENERGY-STORED",
        "HS-POOL-FRAC-L",
        "HS-MTC-L",
        "HS-MASS-FLUX-L",
        "HS-ENERGY-FLUX-L",
        "HS-HTC-ATMS-L",
        "HS-HTC-POOL-L",
        "HS-QFLUX-ATMS-L",
        "HS-QFLUX-POOL-L",
        "HS-QTOTAL-ATMS-L",
        "HS-QTOTAL-POOL-L",
        "HS-FILM-THICK-L",
        "HS-FILM-MASS-L",
        "HS-FILM-ENTH-L",
        "HS-DELM-STEAM-L",
        "HS-DELM-DROP-L",
        "HS-DELM-POOL-L",
        "HS-DELE-ATMS-L",
        "HS-DELE-POOL-L",
        "HS-FILM-TEMP-L",
        "HS-POOL-FRAC-R",
        "HS-MTC-R",
        "HS-MASS-FLUX-R",
        "HS-ENERGY-FLUX-R",
        "HS-HTC-ATMS-R",
        "HS-HTC-POOL-R",
        "HS-QFLUX-ATMS-R",
        "HS-QFLUX-POOL-R",
        "HS-QTOTAL-ATMS-R",
        "HS-QTOTAL-POOL-R",
        "HS-FILM-THICK-R",
        "HS-FILM-MASS-R",
        "HS-FILM-ENTH-R",
        "HS-DELM-STEAM-R",
        "HS-DELM-DROP-R",
        "HS-DELM-POOL-R",
        "HS-DELE-ATMS-R",
        "HS-DELE-POOL-R",
        "HS-FILM-TEMP-R",
        "HS-RAD-FLUX-L",
        "HS-RAD-FLUX-R",
    ]

    lVarCFVALU = ["CFVALU"]

    lVarRN1Class = ["RN1-TOTMAS-1", "RN1-TOTMAS-2", "RN1-TYCLT"]

    lVarCorCvh = ["COR-QCNV"]

    lVarTYCTL = ["RN1-TYTOT-2"]
    for i in range(len(lRN1Class)):
        s = "RN1-TYCLT-%d-2" % (i)
        lVarTYCTL.append(s)
    pass

    lVarNCG = [
        "CVH-E",
        "CVH-H",
        "CVH-H",
        "CVH-PPART",
        "CVH-ECV",
        "CVH-X",
        "CVH-MASS",
        "CVH-RHO",
        "FL-I-MFLOW",
        "FL-MFLOW",
    ]
    lVarNCG1 = ["CVH-TOT-E", "CVH-TOT-M"]

    lVarIndex = [
        (lVarCVH, lCv),
        (lVarFL, lFl),
        (lVarHS, lHS),
        (lVarHS1, lHS1),
        (lVarFLValv, lFLV),
        (lVarCFVALU, lCFVALU),
        (lVarFLBLK, lFLBLK),
        (lVarRN1Class, lRN1Class),
        (lVarCorCvh, lCorCvh),
        (lVarTYCTL, lTYCTL),
        (lVarNCG1, lNCG),
    ]


pass  # end of fInitList function


def fGetVarIndex(svar):
    """search in index for variable information"""
    global lVarIndex
    lIndex = []
    for lv in lVarIndex:
        try:
            iIndex = lv[0].index(svar)
            lIndex = lv[1]
            break
        except:
            continue
        pass
    pass
    # print svar,lIndex
    return lIndex


pass


def fIsNCG(svar):
    """check whether variable concerns non-condensable gas"""
    global lVarNCG, lNCG
    sR = ""
    i = -1
    # print svar
    for s in lVarNCG:
        if len(svar) > len(s) and svar[: len(s)] == s:
            i = lVarNCG.index(s)
            # print svar
            break
    pass
    if i >= 0:
        s = svar.split(".")
        try:
            j = int(s[1])
        except:
            j = 0
        pass
        if j > 0:
            sR = lNCG[j - 1]
    pass
    return sR


pass


def fFormatOptions(loptions):
    """format gnuplot script for options"""
    sx = "set xrange [%s:%s]\n" % (loptions[0], loptions[1])
    sy = "set yrange [%s:%s]\n" % (loptions[2], loptions[3])
    if loptions[4] == "Seconds":
        st = 'fT(x)=x\nset xlabel "Time [s]"\n'
    if loptions[4] == "Minutes":
        st = 'fT(x)=x/60.0\nset xlabel "Time [m]"\n'
    if loptions[4] == "Hours":
        st = 'fT(x)=x/3600.0\nset xlabel "Time [h]"\n'
    return (sx + sy, st)


pass

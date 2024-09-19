#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import meltoolsmod.tzmod as tzmod
import meltoolsmod.pvmisc as pvmisc
import meltoolsmod.pvpyx as pvpyx

def fMain():

 sf="cor-tz.conf"
 if len(sys.argv)>1 :
  sf=sys.argv[1]
 pass
 
 co=pvpyx.copt()
 co.spdfdir="cor-tz"
 co.spdffn="cor-tz.pdf"
 co.readopt(sf)
 co.printopt()

 imaxname=pvpyx.fCleanOutput(co.spdfdir,co.iClean) 
 lt = pvmisc.fReadTime(sptf=co.sptf)
 nt0=len(lt)
 ltr = pvpyx.fCheckOutputRange(nt0,co.iStart,co.iStop,co.iStep,imaxname)
 if len(ltr)== 0 :
  print("Nothing to plot")
  sys.exit(0)
 pass
  
 nRings,nRows,lzc,lr,lcha,lbyp = pvmisc.fSP1(co.sptf)

 lVarsu = list (set (co.lVars))
 lllv=[]
 for sVar in lVarsu :
  llv = pvmisc.fReadVar(sVar, iMess=1, sptf=co.sptf,iCol=-1, sOpt="0" )
  lllv.append(llv)
 pass
 
 for itime in ltr :
  xtime = lt[itime]

  tzmod.llv=[]
  tzmod.llz=[]
  for i in range(len(co.lVars)) :
   j = lVarsu.index(co.lVars[i])
   lx,lz = tzmod.fTransCorTempZ(lllv[j][itime],lzc,nRings,nRows)
   tzmod.llv.append(lx[int(co.lRing[i])-1])
   tzmod.llz.append(lz[int(co.lRing[i])-1])
  pass
  nllv = 0 
  for lv in tzmod.llv :
   nllv+=len(lv)
  pass
  if nllv>0 :
   tzmod.ltitle= co.lSerTit 
   tzmod.nColumns=len(tzmod.ltitle)
#   tzmod.fSetZMinMax()
   g = tzmod.fPlotTZ(lzc)
   tzmod.fWriteTimeTitle(g,xtime,itime,co.sTitle)

   sf="./%s/%04d" % (co.spdfdir,itime)
   g.writePDFfile(sf)
   sys.stdout.write("%d," % (itime))
  else :
   sys.stdout.write("%dX," % (itime))
  pass
 pass
 
 print("\nFinished - single page pdfs are in ./%s/" % (co.spdfdir))
 if pvpyx.fJoinPdf(co.spdffn,co.spdfdir) :
  print("Output written to ./pdf/%s" % co.spdffn)
 pass
pass # end main

if __name__ == "__main__":
 print("I am just a module.")
pass    

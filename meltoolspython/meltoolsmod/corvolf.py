#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math 
import pyx 
import meltoolsmod.pvmisc as pvmisc
import meltoolsmod.pvpyx as pvpyx

def fMain():

 # transparency for fluid and porosity
 xtfc = 0.1
 xtfs = 0.7
 xtp  = 0.5

 #read configuration
 co=pvpyx.copt()
 sf="cor-volf.conf"
 if len(sys.argv)>1 :
  sf=sys.argv[1]
 pass
 co.spdfdir="cor-volf"
 co.spdffn="cor-volf.pdf"
 co.readopt(sf)
 co.printopt()
 lvolf=co.lCompList
 lvolfc=co.lcCompList

 #setup pyx
 #pyx.text.set(mode="latex")
 pyx.text.set(cls=pyx.text.LatexRunner)
 pyx.unit.set(defaultunit=co.sunits,uscale=co.xscale)
 tts=pyx.text.size.normalsize
 #tts=text.size.scriptsize

 #set color for downcomer 
 for svolf in ["fl","flc","flb"] :
  try :
   i=lvolf.index(svolf)
  except :
   i=-1
  pass
  if i>=0 :
   break
  pass
 pass
 if i>=0 :
  col_down=lvolfc[i]
 else :
  col_down=pyx.color.cmyk.SkyBlue   
 pass
 
 #setup downcomer volumes
 lcvDown=[]
 #print co.scvDown
 for scv in co.scvDown.split() :
  icv = int (scv)
  lcvDown.append(icv)
 pass
 #print "lcvDown= ", lcvDown

 #setup core geometry 
 lr0 = []
 lr1 = []
 lrr = []
 lz0 = []
 lz1 = []
 print("Reading /SP data ...")
 nRings,nRows,lz,lr,lcha,lbyp = pvmisc.fSP1(sptf=co.sptf)
 
 print("Number of rings: ", nRings)
 print("Core radii [m]: ", lr)
 print("Number of axial elevations: ",nRows)
 print("Axial node elevations [m]: ", lz)
 print("Reading COR-TSVC data ...")
 lid=pvmisc.fLID(sptf=co.sptf)
 nNull = len(lcha[-1])
 
 if len ( lcvDown ) > 0 :
  print("Reading downcomer volumes elevations ...")
  t = pvmisc.fGetCVHAlt(lcvDown,sptf=co.sptf)
  icvDown=len(lcvDown)-1
  #print icvDown
  lchad = lcha [-1]
  nchad = len (lchad)
  for i in range(nchad) :
   if lchad[nchad-(i+1)] == -1 :
    if lz[nchad-(i+1)] < t[0][icvDown][0] :
     icvDown-=1
    pass
    lchad[nchad-(i+1)] = lcvDown[icvDown]
   else :
    break
   pass
  pass 
 pass
 
 #print lcha
 #print lbyp
 
 lcv = []
 for lcha1 in lcha :
  for icv in lcha1 :
   if icv>=0 :
    try :
     i=lcv.index(icv)
    except :
     lcv.append(icv)
    pass
   pass
  pass
 pass
 print("Volumes associated with channels:")
 print(lcv)
 lcvb = []
 for lbyp1 in lbyp :
  for icv in lbyp1 :
   if icv>=0 :
    try :
     i=lcvb.index(icv)
    except :
     lcvb.append(icv)
    pass
   pass
  pass
 pass
 print("Volumes associated with bypass:")
 print(lcvb)

 #print empty grid to check the geometry 
 bDebug=False
 if bDebug :
  c = pyx.canvas.canvas()
 pass
 r1 = 0.0
 rr1 = 0.0
 for i,r in enumerate(lr) :
  r0 = r1
  r1 = r
  sx = math.pi * ( r1**2 - r0**2 )
  dr = math.sqrt(sx)
  rr0 = rr1
  rr1 = rr1 + dr
  z0 = -10000.0
  for jj,z in enumerate(lz) :
   if z0<=-10000.0 :
    z0=z
    z1=z
   else :
    z0=z1
    z1=z
    ii = (jj-1) + i*nRows
    bPrint =  lid [ ii ] > 0 
    if bPrint and bDebug :
     p = pyx.path.rect(rr0,z0,rr1-rr0,z1-z0)
     c.stroke(p)
    pass
    lz0.append(z0)
    lz1.append(z1)
    lr0.append(rr0)
    lr1.append(rr1)
    lrr.append(rr0)
   pass
  pass 
 pass
 if bDebug :
  c.writePDFfile("cor-volf-grid")
 pass
 
 nl = len(lid)
 l  = []      # initiate empty list for data
 # read time    
 ltime = pvmisc.fReadTime(sptf=co.sptf)

 #initiate list of zeros to fill data for PWR
 lzero = [] 
 for i in range(len(ltime)) :
   lzero.append(0.0)
 pass

 #read data for requested volume fractions
 for svolf in lvolf :
  sf="COR-VOLF-%s" % (svolf.upper())
  # for PWR fill bypass variables by zeros for internal rings
  if svolf in [ "porb", "pb", "mb1", "mb2" ] : 
    bFillZero = ( len(pvmisc.fIndexVar(sf,sptf=co.sptf)) == nRows )
    # or ( svolf in [ "flb", "flc" ] and "fl" in lvolf )
    # added 6.4.2012 for MELCOR 2 compatibility
  elif svolf in [ "sh", "fm" ] or ( svolf in [ "flb", "flc" ] and "fl" in lvolf ):
    bFillZero = True
  else :
    bFillZero = False
  pass
  if bFillZero :
   ll=[]
   for i in range(nRings-2) :
    for j in range(nRows) :
     ll.append(lzero)
    pass
   pass
   pass
   lsh = pvmisc.fReadVarC(nRows,sf,iMess=1,sptf=co.sptf,sOpt="0")
   for lsh1 in lsh :
    ll.append(lsh1)
   pass
   for j in range(nRows) :
    ll.append(lzero)
   pass
  else :
   ll=pvmisc.fReadVarC(nl,sf,iMess=1,sptf=co.sptf,sOpt="0")
  pass
  if len(ll[0])==0 :
   print("Variable %s not found in the plot file" % (sf))
   print("Remove component %s from the component list" % (svolf))
   print("Exiting ...")
   sys.exit(0)
  pass
  l.append(ll)
 pass

 # subtract porosity from debris fraction
 # porosity without debris cause an error
 for t in [ ("por","pd") , ("porb","pb") ] :
  try :
   ip = lvolf.index(t[0])
  except :
   ip = -1
  pass
  if ip >= 0 :
   ideb = lvolf.index(t[1])
   for i in range(len(l[ideb])) :
    for j in range(len(l[ideb][i])) :
     l[ideb][i][j]-=l[ip][i][j]
    pass
   pass
  pass 
 pass

 # 6.4.2012, based on MELCOR2 results
 # remove duplicity of flc+flb and fl for PWR
 try :
  iflc = lvolf.index("flc")
 except :
  iflc = -1
 pass
 try :
  iflb = lvolf.index("flb")
 except :
  iflb = -1
 pass
 try :
  ifl = lvolf.index("fl")
 except :
  ifl = -1
 pass
 if iflc>=0 and iflb>=0 and ifl>=0 :
  for i in range(len(l[ifl])) :
   for j in range(len(l[ifl][i])) :
    if l[iflc][i][j]>0.0 or l[iflb][i][j]>0.0 : l[ifl][i][j]=0.0
   pass
  pass
 pass

 #read water levels 
 licv = pvmisc.fLCVHi(lcv,sptf=co.sptf)
 lwcs = pvmisc.fReadCVHVarC("CVH-LIQLEV",licv,sptf=co.sptf,iMess=1)
 lwcc = pvmisc.fReadCVHVarC("CVH-CLIQLEV",licv,sptf=co.sptf,iMess=1)
 licv = pvmisc.fLCVHi(lcvb,sptf=co.sptf)
 lwbs = pvmisc.fReadCVHVarC("CVH-LIQLEV",licv,sptf=co.sptf,iMess=1)
 lwbc = pvmisc.fReadCVHVarC("CVH-CLIQLEV",licv,sptf=co.sptf,iMess=1)
 
 #check figures already plotted
 imaxname=pvpyx.fCleanOutput(co.spdfdir,co.iClean)
 # calculate number of figures to plot
 nt0=len(ltime)
 ltr = pvpyx.fCheckOutputRange(nt0,co.iStart,co.iStop,co.iStep,imaxname)

 # plot figures
 for it in ltr :
  # calculate water levels in the cell
  lzchas=pvmisc.fCalWLC(lcha,lcv,lwcs,lz0,lz1,nRows,it)
  lzbyps=pvmisc.fCalWLC(lbyp,lcvb,lwbs,lz0,lz1,nRows,it)
  lzchac=pvmisc.fCalWLC(lcha,lcv,lwcc,lz0,lz1,nRows,it)
  lzbypc=pvmisc.fCalWLC(lbyp,lcvb,lwbc,lz0,lz1,nRows,it)

  # initiate empty canvas
  c = pyx.canvas.canvas()

  # plot channel water levels in the downcomer
  i=nRings-1    
  lcha1=lcha[i]
  icv0=0
  for jj,icv in enumerate(lcha1) :
   if icv!=icv0 :
    ii = jj + i*nRows
    r0=lr0[ii]
    r1=lr1[ii]
    z0=lz0[ii]
    z1=lz1[ii]
    icv0=icv
    try : 
     ilw = lcv.index(icv)
    except :
     ilw = -1
    pass
#    print i,jj,ii,icv,ilw
    if ilw>=0 :
     zs=lwcs[ilw][it]
     zc=lwcc[ilw][it]
     if zs>lz[-1] :
      zs=lz[-1]
     if zs<z0 :
      zs=z0
     pass
     if zc>lz[-1] :
      zc=lz[-1]
     if zc<z0 :
      zc=z0
     pass
     #pvpyx.fSwollenArea(c,col_down,zc,zs,r0,r1,xuscale,xuscale)
     p = pyx.path.rect(r0,z0,r1-r0,zc-z0)
     c.fill(p,[col_down,pyx.deco.filled([col_down]),pyx.deco.color.transparency(xtfc)])
     p = pyx.path.rect(r0,zc,r1-r0,zs-zc)
     c.fill(p,[col_down,pyx.deco.filled([col_down]),pyx.deco.color.transparency(xtfs)])
    pass
   pass
  pass
  #plot material fractions
  for i,rr in enumerate(lr0):
   lrr[i]=rr
  pass
  for iv,ll in enumerate(l) :
   for i,lll in enumerate(ll) :
    #rint iv,i,it
    x=lll[it] 
    if x>0.0 :
     r0=lr0[i]
     r1=lr1[i]
     z0=lz0[i]
     z1=lz1[i]
     rr=lrr[i]
     r1=rr+x*(r1-r0)
     if lvolf[iv]=="flc" or lvolf[iv]=="fl" :
      dz=lzchac[i]*(z1-z0)
      p = pyx.path.rect(rr,z0,r1-rr,dz)
      c.fill(p,[lvolfc[iv],pyx.deco.filled([lvolfc[iv]]),pyx.deco.color.transparency(xtfc)])
      dzs=lzchas[i]*(z1-z0)
      #pvpyx.fSwollenArea(c,lvolfc[iv],z0+dz,z0+dzs,rr,r1,xuscale,xuscale)
      p = pyx.path.rect(rr,z0+dz,r1-rr,dzs-dz)
      c.fill(p,[lvolfc[iv],pyx.deco.filled([lvolfc[iv]]),pyx.deco.color.transparency(xtfs)])
     elif lvolf[iv]=="flb" :
      dzs=lzbyps[i]*(z1-z0)
      dz=lzbypc[i]*(z1-z0)
      p = pyx.path.rect(rr,z0,r1-rr,dz)
      c.fill(p,[lvolfc[iv],pyx.deco.filled([lvolfc[iv]]),pyx.deco.color.transparency(xtfc)])
      #pvpyx.fSwollenArea(c,lvolfc[iv],z0+dz,z0+dzs,rr,r1,xuscale,xuscale)
      p = pyx.path.rect(rr,z0+dz,r1-rr,dzs-dz)
      c.fill(p,[lvolfc[iv],pyx.deco.filled([lvolfc[iv]]),pyx.deco.color.transparency(xtfs)])
     elif lvolf[iv]=="por" or lvolf[iv]=="porb" :
      p = pyx.path.rect(rr,z0,r1-rr,z1-z0)
      c.fill(p,[lvolfc[iv],pyx.deco.filled([lvolfc[iv]]),pyx.deco.color.transparency(xtp)])
     else :
      p = pyx.path.rect(rr,z0,r1-rr,z1-z0)
      c.fill(p,[lvolfc[iv],pyx.deco.filled([lvolfc[iv]])])
     pass 
     lrr[i]=r1
    pass
   pass
  pass
  #plot grid 
  for i,id in enumerate(lid) :
   if id > 0 :
    r0=lr0[i]
    r1=lr1[i]
    z0=lz0[i]
    z1=lz1[i]
    p = pyx.path.rect(r0,z0,r1-r0,z1-z0)
    c.stroke(p)  
   pass
  pass
  #determine height of text
  xtboxt = pyx.text.text(0.0, 0.0, "{\\tiny X}").bbox().height()
  xtboxn = pyx.text.text(0.0, 0.0, "X").bbox().height()
  #type ring numbers
  for i in range(0,nRings) :
   ii=i*nRows
   r0=lr0[ii]
   r1=lr1[ii]
   z0=lz0[ii]-xtboxt
   z1=lz1[ii]
   ss = "%d" % (i+1)
   c.text((r0+r1)/2.0,z0,ss,[pyx.text.halign.boxcenter,pyx.text.valign.top,tts])
  #type row numbers
  for i in range(0,nRows) :
   r0=lr0[i]
   r1=lr1[i]
   z0=lz0[i]
   z1=lz1[i]  
   ss = "%02d\\," % (i+1)  
   c.text(r0,(z0+z1)/2.0,ss,[pyx.text.halign.boxright,pyx.text.valign.middle,tts])
  pass
  r0 = lr0[0]
  z0 = lz0[0]-(2*xtboxt+xtboxn)
  #print it
  x=ltime[it]
  ss = "Time = %.1f\,s = %s, Plot record %d" % (x, pvmisc.fCas(x),it)  
  c.text(r0,z0,ss,[pyx.text.halign.boxleft,pyx.text.valign.top,tts])
  z0 = lz1[nRows-1]+xtboxt
  c.text(r0,z0,co.sTitle,[pyx.text.halign.boxleft,pyx.text.valign.bottom,tts])
  sformat = "./%s/%0" + str(co.noutfdig) + "d"
  spdf = sformat % (co.spdfdir,it)
  c.writePDFfile(spdf)
  #sys.stdout.write("%d," % (it))
  print ( ("%d," % (it)) ,end="",flush=True ),
 pass
 print("\nFinished - single page pdfs are in ./%s/" % (co.spdfdir))
 if pvpyx.fJoinPdf(co.spdffn,co.spdfdir) :
  print("Output written to ./pdf/%s" % co.spdffn)
 pass
pass # end of the main section

if __name__ == "__main__":
 print("I am just a module.")
pass    

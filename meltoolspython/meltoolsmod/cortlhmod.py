#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 python module cvhtlhmod.py 
 written by Petr Vokac, NRI Rez plc
 August, November 2009
 March 2011
 License: as-is

 this module is used only by cvh-lht.py
'''
import pyx
import math 
import meltoolsmod.pvpyx as pvpyx
bPrint = True
tmin=300.0
tmax=3000.0
tmaxx=6000.0 # ultimate maximum of the temperature scale
ltp=["100","200","300","400","500","600","700","800","900","1000",
     "1100","1200","1300","1400","1500","1600","1700","1800","1900","2000",
     "2100","2200","2300","2400","2500","2600","2700","2800","2900","3000",
     "3100","3200","3300","3400","3500","3600","3700","3800","3900","4000",
     "4100","4200","4300","4400","4500","4600","4700","4800","4900","5000",
     "5100","5200","5300","5400","5500","5600","5700","5800","5900","6000",
     "6100","6200","6300","6400","6500","6600","6700","6800","6900","7000"]

def fSetMaxMin(tmax1,tmin1) :
 '''set maximum and minimum temperature for the color scale
 '''
 global tmin
 global tmax
 global tmaxx
 tmin=tmin1
 tmax=tmax1
 if tmax>tmaxx :
  tmax=tmaxx
 pass 
pass

def fTempCol(x) : 
 '''convert temperature to color scale
    return relative temperature in range

    obsolent: generalized version is in pvpyx.py module
 '''
 global tmin
 global tmax
 xx=x
 if xx<tmin :
  xx=tmin 
 if xx>tmax :
  xx=tmax
 xr=(xx-tmin)/(tmax-tmin)
 return 1.0-xr
pass

def fPlotScale(c,mcgr,x0,y0,x1,y1) :
 '''plot temperature color scale
    used only in this module
    
    obsolent: generalized version is in pvpyx.py module
 '''
 global tmin
 global tmax
 iMax=1000
 xMax=float(iMax)
 ltp=["100","200","300","400","500","600","700","800","900","1000",
     "1100","1200","1300","1400","1500","1600","1700","1800","1900","2000",
     "2100","2200","2300","2400","2500","2600","2700","2800","2900","3000",
     "3100","3200","3300","3400","3500","3600","3700","3800","3900","4000",
     "4100","4200","4300","4400","4500","4600","4700","4800","4900","5000",
     "5100","5200","5300","5400","5500","5600","5700","5800","5900","6000",
     "6100","6200","6300","6400","6500","6600","6700","6800","6900","7000"]
 li=[]
 for xt in ltp :
  xi = fTempCol(float(xt))
  li.append(int(xMax*xi))
 pass
 dy=(y0-y1)/xMax
 y=y1 
 for i in range (1,iMax) :
  p = pyx.path.rect(x0,y,x1-x0,dy)
  mc=mcgr.getcolor(float(i)/xMax)
  c.fill(p,[mc,pyx.deco.filled([mc])])
  try :
   it=li.index(i)
  except:
   it=-1
  pass
  y+=dy
  if (it>=0) :
   c.text(x1,y+dy,"\\,"+ltp[it],[pyx.text.halign.boxleft,pyx.text.size.large])   
 pass
 c.text(x1,y1,"\\raisebox{1.2ex}{\\textit{T}\\,[K]}",[pyx.text.halign.boxleft,pyx.text.size.large])   
pass

def fColorWall(c,mcgr,x0,y0,tanfi1,tanfi2,xRVESS,xDZRV,xRVLH,xDZLH,xHLST,nlh1,nlh2,lr,lz,xfii,xfio,yi,yo,dzlh1,dzlh2,dzrv1,dzrv2,ltime,l,it) :
 '''plot colors for the rpv wall nodes'''
 global tmin
 global tmax
 global ltp
 global bPrint
 nlh=nlh1+nlh2
 #color scale
 dx=pyx.text.text(0.0, 0.0, "TT").bbox().width()
 x=x0+xRVESS+xDZRV+dx
 pvpyx.fPlotScale(c,mcgr,x,y0-xDZLH,x+dx,xHLST,tmax,tmin,ltp)
# #blue boundary of the wall - or blue background
# p = path.path(path.moveto(x0,y0))                     # move to rpv bottom
# p.append(path.arc(x0,y0+xRVLH,xRVLH,-90.0,xfii))      # arc - internal wall
# p.append(path.lineto(xRVESS,xHLST))                   # cylinder - internal wall
# p.append(path.lineto(xRVESS+xDZRV,xHLST))             # top 
# p.append(path.lineto(xRVESS+xDZRV,yo))                # cylinder - outer wall
# p.append(path.arcn(x0,y0+xRVLH,xRVLH+xDZLH,xfio,-90)) # arc - outer wall
# p.append(path.closepath())
# c.stroke(p,[color.cmyk.Blue,deco.filled([color.cmyk.Blue])])

 # temperature colors in the spherical wall
 xfi0 = -90.0
 x00=x0
 y00=y0
 sinfi0=0
 cosfi0=1
 ii=0 # ii is index of temperature point 
 iii=0
 for xr in lr :
  if xr!=lr[-1] : # skip corner node
   sinfi = xr / xRVLH
   xfir=math.asin(sinfi)
   cosfi = math.sqrt ( 1.0 - sinfi**2 )
   xfid = 180 * xfir / math.pi - 90.0
   # isolation + steel wall
   for i in range(nlh,-1,-1) :
    #print iii,ii,xr,i
    if i>nlh1 and nlh2>0:
     dr=dzlh2/float(nlh2)
     drup=dr/2.0
     if i<nlh :
      drdown=dr/2.0
     else :
      drdown=0.0
     pass
     drLHl = (i-nlh1)*dr+drdown+dzlh1
    else :
     dr=dzlh1/float(nlh1)     
     drup=dr/2.0
     drdown=dr/2.0
     if i==0:
      drup=0.0
     if i==nlh1 :
      if nlh2>0 :
       drdown=0.5*dzlh2/float(nlh2)
      else :
       drdown=0.0
     pass
     drLHl = i*dr+drdown
    pass
    dr=drdown+drup
    rLHl  = xRVLH + drLHl     
    y00 = (y0-drLHl) + rLHl * (1.0-cosfi0)
    y01 = (y0-drLHl) + rLHl * (1.0-cosfi)
    x00 = x0 + rLHl * sinfi0
    x01 = x0 + rLHl * sinfi
    x02 = x01 - dr * sinfi
    y02 = y01 + dr * cosfi
    p = pyx.path.path(pyx.path.moveto(x00,y00),
                      pyx.path.arc(x0,y0+xRVLH,rLHl,xfi0,xfid),
                      pyx.path.lineto(x02,y02),
                      pyx.path.arcn(x0,y0+xRVLH,rLHl-dr,xfid,xfi0), 
                      pyx.path.closepath()
                 )
    x=fTempCol(l[it][ii])
    mc=mcgr.getcolor(x)
    c.fill(p,[mc,pyx.deco.filled([mc])])
    ii=ii+1
   pass
   xfi0=xfid
   sinfi0=sinfi
   cosfi0=cosfi
  pass
  iii+=1
 pass
 # temperature colors in the spherical wall - corner node
 sinfi = lr[-1] / xRVLH
 xfir=math.asin(sinfi)
 cosfi = math.sqrt ( 1.0 - sinfi**2 )
 xfid = 180 * xfir / math.pi - 90.0
 for i in range(nlh,-1,-1) :
  #print iii,ii,xfir,i, "sphere corner"
  if i>nlh1 and nlh2>0 :
   dr=dzlh2 / float(nlh2)
   drup=dr/2.0
   drdown=dr/2.0
   dx1=dzrv2/float(nlh2)
   dxleft=dx1/2.0
   dxright=dx1/2.0
   if i==nlh :
    drdown=0.0
    dxright=0.0
   pass
   drLHl = dzlh1 + (i-nlh1)*dr + drdown 
   dx    = dzrv1 + (i-nlh1)*dzrv2/float(nlh2) + dxright 
   dy    = dzrv1/tanfi1 + ((i-nlh1)*dzrv2/float(nlh2)+dxright)/tanfi2
   dy2   = dzrv1/tanfi1 + ((i-nlh1)*dzrv2/float(nlh2)-dxleft)/tanfi2
  else :
   dr=dzlh1 / float(nlh1)
   drup=dr/2.0
   drdown=dr/2.0
   dx1=dzrv1/float(nlh1)
   dxleft=dx1/2.0
   dxright=dx1/2.0
   if i==0:
    drup=0.0
    dxleft=0.0
   if i==nlh1:
    if (nlh2>0) :
     drdown=0.5*dzlh2/float(nlh2)
     dxright=0.5*dzrv2/float(nlh2)
     dy=(i*dzrv1/float(nlh1))/tanfi1 + dxright/tanfi2
     dy2=(i*dzrv1/float(nlh1)-dxleft)/tanfi1
    else:
     drdown=0.0
     dxright=0.0
     dy=(i*dzrv1/float(nlh1))/tanfi1 
     dy2=(i*dzrv1/float(nlh1)-dxleft)/tanfi1 
    pass
   else:
    dy=(i*dzrv1/float(nlh1))/tanfi1 + dxright/tanfi1
    dy2=(i*dzrv1/float(nlh1)-dxleft)/tanfi1 
   pass
   drLHl = i*dr+drdown
   dx=i*dzrv1/float(nlh1)+dxright
  pass
  dr=drdown+drup
  rLHl  = xRVLH + drLHl
  x00 = x0 + rLHl * sinfi0 
  y00 = (y0-drLHl) + rLHl * (1.0-cosfi0)
  x01 = xRVESS + dx    # end point of the external arc
  y01 = yi + dy
  x02 = xRVESS + dx-(dxleft+dxright)  # starting point of the internal arc
  y02 = yi + dy2
  xfid1=180 * math.acos((y0+xRVLH-y01)/rLHl)/math.pi - 90
  xfid2=180 * math.acos((y0+xRVLH-y02)/(rLHl-dr))/math.pi - 90
  p = pyx.path.path(pyx.path.moveto(x00,y00),
                pyx.path.arc(x0,y0+xRVLH,rLHl,xfi0,xfid1),
                pyx.path.lineto(x02,y02),
                pyx.path.arcn(x0,y0+xRVLH,rLHl-dr,xfid2,xfi0), 
                pyx.path.closepath()
               )
  x=fTempCol(l[it][ii])
  mc=mcgr.getcolor(x)
  c.fill(p,[mc,pyx.deco.filled([mc])])
  ii=ii+1
 pass
 # temperature colors in the cylindrical wall - corner node
 dzmax=lz[0]+xRVLH-math.sqrt(xRVLH**2-xRVESS**2)
 #replaced 12.3.2011
 #dzz = 1.e+6
 #for z in lz:
 # dzz1 = math.fabs(z-dzmax)
 # if dzz1>dzz :
 #  dzmax1=z
 #  break
 # pass
 # dzz=dzz1
 #pass 
 dzmax1=xHLST
 for i,z in enumerate(lz) :
  if z>=xHLST :
   i0cw=i  # i0cw is the index of the lowest cylindrical node in lz above transitional one 
   break
  if z>dzmax+1e-7 : # 7.5.2014 added +1e-7
   dzmax1=z
   i0cw=i
   break
  pass
 pass
 if bPrint :
  print("Check dzmax1 and i0cw:")
  print("xHLST=%f,dzmax=%f,dzmax1=%f,z=%f,i0cw=%d" % (xHLST,dzmax,dzmax1,z,i0cw))
  bPrint = False
 pass
 iii+=1
 #replaced 12.3.2011
 for i in range(nlh,-1,-1) :
  #print iii,ii,i,dzmax1,dzmax, "cylinder corner"
  if i>nlh1 and nlh2>0 :
   dx1=dzrv2/float(nlh2)
   dxleft=dx1/2.0
   dxright=dx1/2.0
   if i==nlh :
    dxright=0.0
   pass
   dx  = dzrv1+(i-nlh1)*dx1+dxright
   dy  = dzrv1/tanfi1 + ((i-nlh1)*dx1+dxright)/tanfi2
   dy3 = dzrv1/tanfi1+((i-nlh1)*dx1-dxleft)/tanfi2
  else :
   dx1=dzrv1/float(nlh1)
   dxleft=dx1/2.0
   dxright=dx1/2.0
   if i==0 :
    dxleft=0.0
   pass
   if i==nlh1:
    if nlh2>0 :
     dxright=0.5*dzrv2/float(nlh2)
     dy  = i*dx1/tanfi1 + dxright/tanfi2
     dy3 = (i*dx1-dxleft)/tanfi1
    else :
     dxright=0.0
     dy     = i*dx1/tanfi1
     dy3    = (i*dx1-dxleft)/tanfi1
    pass
   else :
    dy=   i*dx1/tanfi1 + dxright/tanfi1
    dy3 = (i*dx1-dxleft)/tanfi1
   pass
   dx=i*dx1+dxright
  pass
  x00=xRVESS+dx
  y00=yi+dy
  x01=x00
  y01=dzmax1
  x02=x00-(dxright+dxleft)
  y02=y01
  x03=x02
  y03=yi+dy3
  p = pyx.path.path(pyx.path.moveto(x00,y00),
                pyx.path.lineto(x01,y01),
                pyx.path.lineto(x02,y02),
                pyx.path.lineto(x03,y03),
                pyx.path.closepath()
                )
  #print it,ii,len(l[it])
  x=fTempCol(l[it][ii])
  mc=mcgr.getcolor(x)
  c.fill(p,[mc,pyx.deco.filled([mc])])
  ii+=1  
 pass
 #temperatures in the rest of the cylindrical wall
 for ilz in range(i0cw,len(lz)) :
  xz=lz[ilz]
  #change 7.5.2014 dzmax -> dzmax1
  #if lz[ilz]>dzmax and xz<xHLST :
  if xz<xHLST :
   iii+=1
   #print xz,lz[ilz+1], xHLST
   for i in range(nlh,-1,-1) :
    #print iii,ii,ilz,i, "cylinder"
    if ii >= len(l[it]) :
     print("")
     print(" warning cor-tlh: ii=",ii," len(l[it])=",len(l[it])," ilz= ",ilz, "len(lz)=",len(lz), i)
     break
    pass
    if i>nlh1 and nlh2>0 :
     dx1=dzrv2/float(nlh2)
     dxleft=dx1/2.0
     dxright=dx1/2.0
     if i==nlh :
      dxright=0.0
     pass
     dx=dzrv1+(i-nlh1)*dx1+dxright
    else :
     dx1=dzrv1/float(nlh1)
     dxleft=dx1/2.0
     dxright=dx1/2.0
     if i==0 :
      dxleft=0.0
     pass
     if i==nlh1:
      if nlh2>0 :
       dxright=0.5*dzrv2/float(nlh2)
      else:
       dxright=0.0
      pass
     pass
     dx=i*dx1+dxright
    pass
    x00=xRVESS+dx
    y00=xz
    x01=x00
    y01=lz[ilz+1]
    x02=x01-(dxright+dxleft)
    y02=y01
    x03=x02
    y03=y00
    p = pyx.path.path(pyx.path.moveto(x00,y00),
                  pyx.path.lineto(x01,y01),
                  pyx.path.lineto(x02,y02),
                  pyx.path.lineto(x02,y03),
                  pyx.path.closepath()
                )
    #print ii
    x=fTempCol(l[it][ii])
    mc=mcgr.getcolor(x)
    c.fill(p,[mc,pyx.deco.filled([mc])])
    ii+=1  
   pass  
  pass
 pass
pass

def fDBPoolGrid(c,lr,lz,x0,y0,xHSCP,xDZRV,xHLST,xDZLH) :
 '''red grid in the lower plenum'''
 xr=lr[-1]
 ck=pyx.color.cmyk.Black
 for z in lz :
  if (z < xHSCP) :
   p = pyx.path.path(pyx.path.moveto(x0,z),pyx.path.lineto(xr+xDZRV,z))
   c.stroke(p,[pyx.style.linestyle.dashed,ck])
 pass
 for r in lr :
   p = pyx.path.path(pyx.path.moveto(r,y0-xDZLH),pyx.path.lineto(r,xHLST))
   c.stroke(p,[pyx.style.linestyle.dashed,ck])
 pass
 p = pyx.path.path(pyx.path.moveto(x0,y0-xDZLH),pyx.path.lineto(x0,xHLST))
 c.stroke(p,[pyx.style.linestyle.dashed,ck])
pass

def fWallGrid (c,
 lr,lz,xRVESS,xRVLH,xHLST,x0,y0,dzlh1,dzlh2,dzrv1,dzrv2,nlh1,nlh2,tanfi1,tanfi2) :
 '''plot  bottom head nodalization
     vessel wall - yellow lines
     vessel isolation - green lines
 '''
 #vessel wall - yellow lines
 iNLH=nlh1+nlh2+1
 for i in range(0,nlh1+1) :
  rVessl= xRVESS+i*dzrv1/float(nlh1)
  drLHl = i*dzlh1/float(nlh1)
  rLHl  = xRVLH + drLHl
  xfi=180.0*math.asin(rVessl/rLHl)/math.pi-90.0
  p = pyx.path.path(pyx.path.moveto(x0,y0-drLHl),
                pyx.path.arc(x0,y0+xRVLH,rLHl,-90.0,xfi),
                pyx.path.lineto(rVessl,xHLST))
  c.stroke(p,[pyx.color.cmyk.Yellow])
 pass
 if nlh2>0:
  #green lines - isolation
  nxs=nlh1+1
  for i in range(nxs,iNLH) :
   rVessl= xRVESS+dzrv1+(i-nlh1)*dzrv2/float(nlh2)
   drLHl = (i-nlh1)*dzlh2/float(nlh2)
   rLHl  = xRVLH + dzlh1 + drLHl
   xfi=180.0*math.asin(rVessl/rLHl)/math.pi-90.0
   p = pyx.path.path(pyx.path.moveto(x0,y0-(drLHl+dzlh1)),
                 pyx.path.arc(x0,y0+xRVLH,rLHl,-90.0,xfi),
                 pyx.path.lineto(rVessl,xHLST))
   c.stroke(p,[pyx.color.cmyk.Green])
  pass
 pass 
 #green and yellow radial lines
 xfi0=0.0
 #do not assign a pointer but copy the list
 lr1 = []
 lr1.extend(lr)
 lr1.insert(0,0.0)
 for xr in lr1 :
  sinfi1 = xr / xRVLH
  xfi=math.asin(sinfi1)
  cosfi1 = math.sqrt ( 1.0 - sinfi1**2 )
  x1 = xr
  y1 = xRVLH * (1.0 - cosfi1) + y0
  cosfi2=cosfi1
  sinfi2=sinfi1
  if xr==lr1[-1]:
   cosfi1=1.0/math.sqrt(1+tanfi1**2)
   sinfi1=math.sqrt(1.0-cosfi1**2)
   cosfi2=1.0/math.sqrt(1+tanfi2**2)
   sinfi2=math.sqrt(1.0-cosfi2**2)
   x2 = x1 + dzrv1
   y2 = y1 + dzrv1 / tanfi1 
   p = pyx.path.path(pyx.path.moveto(x1,y1),pyx.path.lineto(x2,y2))
   c.stroke(p,[pyx.color.cmyk.Yellow])
   if nlh2>0 : 
    x3 = x2 + dzrv2 
    y3 = y2 + dzrv2 / tanfi2 
    p = pyx.path.path(pyx.path.moveto(x2,y2),pyx.path.lineto(x3,y3))
    c.stroke(p,[pyx.color.cmyk.Green])
   pass
  else :
   x2 = x1 + dzlh1 * sinfi1
   y2 = y1 - dzlh1 * cosfi1
   p = pyx.path.path(pyx.path.moveto(x1,y1),pyx.path.lineto(x2,y2))
   c.stroke(p,[pyx.color.cmyk.Yellow])
   if nlh2>0 : 
    x3 = x2 + dzlh2 * sinfi2
    y3 = y2 - dzlh2 * cosfi2
    p = pyx.path.path(pyx.path.moveto(x2,y2),pyx.path.lineto(x3,y3))
    c.stroke(p,[pyx.color.cmyk.Green])
   pass
  pass
  xff=xfi0 + (xfi-xfi0)/2.0
  sinfix = math.sin(xff)
  cosfix = math.cos(xff)
  if xff > 0.0 :
   for i in range(0,nlh1+1) :
    drLHl = i*dzlh1/float(nlh1)
    rLHl  = xRVLH + drLHl
    x = rLHl * sinfix
    y = rLHl * (1.0-cosfix) + (y0-drLHl)
    p = pyx.path.circle(x,y,dzlh1/30.0)
    # circle - put there color 
    c.stroke(p,[pyx.color.cmyk.Yellow])
   pass
   if nlh2>0 :
    nxs=nlh1+1
    for i in range(nxs,iNLH) :
     drLHl = (i-nlh1)*dzlh2/float(nlh2)
     rLHl  = xRVLH + dzlh1 + drLHl
     x = rLHl * sinfix
     y = rLHl * (1.0-cosfix) + (y0-(drLHl+dzlh1))
     p = pyx.path.circle(x,y,dzlh1/30.0)
     c.stroke(p,[pyx.color.cmyk.Green])
    pass
   pass
  pass
  xfi0=xfi
 pass 
 #yb=y1
 #z0=yb
 dzmax=lz[0]+xRVLH-math.sqrt(xRVLH**2-xRVESS**2)
 dzz = 1.e+6
 for i in range(len(lz)):
  dzz1 = math.fabs(lz[i]-dzmax)
  if dzz1>dzz :
   i0=i-1
   break
  pass
  dzz=dzz1
 pass 
 z0=lz[i0]
 for xz in lz :
  if xz>lz[i0] and xz<=xHLST :
   x1 = xRVESS
   p = pyx.path.path(pyx.path.moveto(xRVESS,xz),pyx.path.lineto(xRVESS+dzrv1,xz))
   c.stroke(p,[pyx.color.cmyk.Yellow])
   for i in range(0,nlh1+1) :
    dr = i*dzrv1/float(nlh1)
    p = pyx.path.circle(xRVESS+dr,(xz+z0)/2.0,dzlh1/30.0)
    c.stroke(p,[pyx.color.cmyk.Yellow])
   pass
   if nlh2>0 :
    p = pyx.path.path(pyx.path.moveto(xRVESS+dzrv1,xz),pyx.path.lineto(xRVESS+dzrv1+dzrv2,xz))
    c.stroke(p,[pyx.color.cmyk.Green]) 
    nxs=nlh1+1
    for i in range(nxs,iNLH) :
     dr = dzrv1+(i-nlh1)*dzrv2/float(nlh2)
     p = pyx.path.circle(xRVESS+dr,(xz+z0)/2.0,dzlh1/30.0)
     c.stroke(p,[pyx.color.cmyk.Green])
    pass
   pass 
   z0=xz 
  pass
 pass
pass

def fGetMaxMin(it,nRings,nRows,ntlp,lt) :
 '''calculate maximum and minimum in list lt
    values < 200 are ignored'''
 lmax = []
 lmin = []
 nvar = len (lt)
 for lt1 in lt :
  l=lt1[it]
  xmin=3000.0
  xmax=300.0
  for i in range(nRings) :
   for j in range(ntlp) :
    x = l[i*nRows+j]
    if x<xmin and x>200.0 :
     xmin = x
    if x>xmax :
     xmax = x
   pass
  pass
  lmax.append(xmax)
  lmin.append(xmin)
 pass
 xmin = min (lmin)
 xmax = max (lmax)
 if xmin > xmax :
  xmin = xmax
 pass
 return (xmax,xmin)
pass

def fDBPoolColors(c,mcgr,it,l,lt,lvolf,nRings,nRows,ntlp,lr,lz,xRVLH,x0,y0) :
 '''chart of debris bed and pool temperature color scale'''
 lvolft=[]
 lvolf1=lvolf[0][0]
 for x in lvolf1 :
  lvolft.append(0.0)
 pass
 xtmin=6000.0
 xtmax=0.0
 xtmin1=min(l[it])
 xtmax1=max(l[it])
 #replaced 12.3.2011
 xtmax2,xtmin2 = fGetMaxMin(it,nRings,nRows,ntlp,lt)
 xtmin = min ([xtmin, xtmin1, xtmin2])
 xtmax = max ([xtmax, xtmax1, xtmax2])
# if xtmin1 < xtmin :
#  xtmin=xtmin1
# if xtmax1 > xtmax :
#  xtmax=xtmax1
# for lt1 in lt :
#  xtmin1=min(lt1[it])
#  xtmax1=max(lt1[it])
#  if xtmin1 < xtmin :
#   xtmin=xtmin1
#  if xtmax1 > xtmax :
#   xtmax=xtmax1
# pass
 fSetMaxMin(xtmax,xtmin)
# print xtmax, xtmin

# print lvolf1
# print lvolft
 nComp = len (lvolf) 
 nCell = len (lvolft) 
 for iComp in range(nComp) :
  for iRing in range(nRings) :
   for iRow in range(ntlp) :
    iCell = iRing * nRows + iRow
    #print(iCell)
    xvf = lvolf[iComp][it][iCell] 
    xte = lt[iComp][it][iCell] 
    if xvf > 0.0 and xte > 0.0 :
     x=fTempCol(xte)
     mc=mcgr.getcolor(x)
     if iRing>0 :
      x00=lr[iRing-1]
     else :
      x00=0.0
     pass
     sv=math.pi*(lr[iRing]**2-x00**2)
     x01=math.sqrt(lvolft[iCell]*sv/math.pi+x00**2) 
     y01=lz[iRow]
     xsinfi=x01/xRVLH
     xcosfi=math.sqrt(1.0-xsinfi**2)
     y01v=y0+(1.0-xcosfi)*xRVLH
     sv=xvf*sv+math.pi*x01**2
     x02=math.sqrt(sv/math.pi)
     y02=y01
     x03=x02
     y03=lz[iRow+1]
     x04=x01
     y04=y03
     if y01v>=y01 :
      xfi1 = 180*math.asin(xsinfi)/math.pi - 90
      xsinfi=x02/xRVLH
      xfi2 = 180*math.asin(xsinfi)/math.pi - 90 
      p = pyx.path.path(pyx.path.moveto(x01,y01v),
                    pyx.path.arc(x0,y0+xRVLH,xRVLH,xfi1,xfi2),
                    pyx.path.lineto(x03,y03),
                    pyx.path.lineto(x04,y04),
                    pyx.path.closepath())
      #print (iCell,iComp)
      #print(x01,y01v)
      #print(x0,y0+xRVLH,xRVLH,xfi1,xfi2)
      #print(x03,y03)
      #print(x04,y04)
      # 170829
      if xfi1<xfi2:
       c.fill(p,[mc,pyx.deco.filled([mc])])
       lvolft[iCell]=lvolft[iCell]+xvf
      pass 
     else :
      p = pyx.path.path(pyx.path.moveto(x01,y01),
                    pyx.path.lineto(x02,y02),
                    pyx.path.lineto(x03,y03),
                    pyx.path.lineto(x04,y04),
                    pyx.path.closepath())
      c.fill(p,[mc,pyx.deco.filled([mc])])
      lvolft[iCell]=lvolft[iCell]+xvf
     pass  
    pass
   pass
  pass 
 pass
pass


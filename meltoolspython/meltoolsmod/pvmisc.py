#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# library with miscelaneous functions 
# for MELCOR post-processing
# 
# Petr Vokac, NRI Rez plc
# 2008,2009,2010,2011
# licence "as-is"
#
# 23.4.2015 compatibility with python3

import subprocess as subp
import pickle
import sys
import math
import operator 

def fXinL(x,l) :
 '''add x into list l, 
    sort list l
    return index of x in sorted list'''
 ll = sorted(l+[x])
 i = ll.index(x)
 return i
pass 

def fReadVarKey(sptf="MELPTF") :
 '''reads list of variables from MELPTF''' 
 bVarNext=True
 p = subp.Popen(["readptf.exe", sptf, "index"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 l = []
 for bline in p.stdout :
   line = bline.decode("utf-8")
   if bVarNext :
     svar = line.strip()
     bVarNext=False
     li=[]
   else :
     s = line.split()
     for ss in s:
       if ss=="*" :
        l.append( (svar,len(li),li) )
        bVarNext=True
        break
       else :
        try :
         li.append ( int(ss) )
        except:
         pass
       pass
   pass
 pass
 return sorted(l, key=operator.itemgetter(0))
pass

def fGetVarKey(svar,sptf="MELPTF") :
 '''get index for one variable''' 
 lvk = fReadVarKey(sptf)
 for s,n,l in lvk :
  if s==svar : return l
 pass
 return None
pass

def fCas(xx,iClock=0) :
 '''converts time in seconds to string 
    input : 
     xx real value of time in seconds
     iClock > 0 return xDhh:mm:ss format
            ==0 (default) return just hours in %05.2f h format
    return :    
     formated string
 '''
 if iClock > 0 : 
  id = 0 
  ih = 0 
  im = 0 
  sNeg = " " 
  x =xx
  if (x<0.0) :
    sNeg="-"  
    x = -1.0 * x
  pass
  xd = x / (24.0*3600.0) 
  id = int(xd) ;
  if (id>0) : 
    x = x - float(id) * (24.0*3600.0) 
  pass
  xh =  x / 3600.0 
  ih = int(xh) 
  if (ih>0) : 
    x = x - float(ih) * 3600.0 
  pass
  xm = x / 60.0 ;
  im = int (xm) ;
  if (im>0) : 
    x = x - im * 60.0 ;
  pass
  if (id>0) :
    shh= "%s%dD%02d:%02d:%02d" % (sNeg,id,ih,im,x) 
  else :
    shh = "%s%02d:%02d:%02d" % (sNeg,ih,im,x) 
  pass
 else :
  shh = "%05.2f h" % (xx/3600.0)
 pass
 return shh
pass
# end of fCas

def fCorRA(sptf="MELPTF") : 
 '''reads .SP/ section from binary file
    return tuple :
     number of core radial rings
     number of core axial levels
 '''
 sCORR   = " COR-NUMBER-RADIAL-RINGS((0))"
 sCORA   = " COR-NUMBER-AXIAL-SEGMENTS((0))"
 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 iCORR=0
 iCORA=0
 for bline in p.stdout :
  line = bline.decode("utf-8")
  #print line[:len(sCORR)]
  if line[:len(sCORR)]==sCORR :
   iCORR = int ( float (line[len(sCORR):]) )
   continue
  if line[:len(sCORA)]==sCORA :
   iCORA = int ( float (line[len(sCORA):]) )
   continue
  if (iCORR>0) and (iCORA>0) :
   break 
 pass
 return (iCORR, iCORA)
pass 
# end of fCorRA

#
# COR-VESSEL-INNER-RADIUS((0))2.8246210E+00                               
# COR-HLST((0))4.0693000E+01                              
# COR-VESSEL-THICKNESS((0))2.4080000E-01                                  
# COR-LOWER-HEAD-THICKNESS((0))2.4080000E-01   
#

def fSP1(sptf="MELPTF") : 
 '''reads .SP/ section from binary file
    return tuple containing:
     iCORR number of core rings
     iCORA number of core axial levels
     lz    list of node bottom elevations and the top node top elevation
     lr    list of ring radiuses
     lcha  list of channel cvh volumes
     lbyp  list of bypass cvh volumes
 '''
 sCORR   = " COR-NUMBER-RADIAL-RINGS((0))"
 sCORA   = " COR-NUMBER-AXIAL-SEGMENTS((0))"
 sCorEle = " COR-LEVEL-ELEVATION(("
 sCorEll = " COR-LEVEL-LENGTH(("
 sCorRar = " COR-RADIAL-RINGS(("
 sCorCha = " COR-CHANNEL-CVH-VOLUME(("
 sCorByp = " COR-BYPASS-CVH-VOLUME(("
 sCorAxa = " COR-AXIAL-AREA((" # for 1.8.5
 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 lz = []
 ldz = []
 lr = []
 lra = []
 lcha = []
 lbyp = []
 for bline in p.stdout :
  line = bline.decode("utf-8")
  #rint (line)
  if line[:len(sCORR)]==sCORR :
   iCORR = int ( float (line[len(sCORR):]) )
   continue
  if line[:len(sCORA)]==sCORA :
   iCORA = int ( float (line[len(sCORA):]) )
   continue
  if line[:len(sCorEle)]==sCorEle :
   s=line[len(sCorEle):].split(")")
   z=float(s[-1])
   if len(lz)<iCORA :
    lz.append(z)
   continue
  if line[:len(sCorEll)]==sCorEll :
   s=line[len(sCorEll):].split(")")
   dz=float(s[-1])
   if len(ldz)<iCORA :
    ldz.append(dz)
   continue
  if line[:len(sCorRar)]==sCorRar :
   s=line[len(sCorRar):].split(")")
   r=float(s[-1])
   if len(lr)<iCORR :
    lr.append(r)
   continue
  if line[:len(sCorAxa)]==sCorAxa :
   s=line[len(sCorAxa):].split(")")
   r=float(s[-1])
   if len(lra)<iCORR :
    lra.append(r)
   continue
  if line[:len(sCorCha)]==sCorCha :
   s=line[len(sCorCha):].split(")")
   i=int(s[0][0])
   #jj=int(s[0][1:])
   x=float(s[-1])
   icv=int(x)
   if len(lcha)<i :
    lcha1=[]
    lcha1.append(icv)
    lcha.append(lcha1)
   else :
    lcha[i-1].append(icv)
   continue
  if line[:len(sCorByp)]==sCorByp :
   s=line[len(sCorByp):].split(")")
   i=int(s[0][0])
   x=float(s[-1])
   icv=int(x)
   if len(lbyp)<i :
    lbyp1=[]
    lbyp1.append(icv)
    lbyp.append(lbyp1)
   else :
    lbyp[i-1].append(icv)
   continue
 pass
 p.stdin.close()
 #rint (lz,ldz)
 z=lz[-1]+ldz[-1]
 lz.append(z)
 # 1.8.5 missing ring radius
 if (len(lr)==0) :
  if len(lra)==iCORR :
   xs=0.0
   for xa in lra :
    xs+=xa
    r = math.sqrt(xs/math.pi)
    lr.append(r)
   pass
  pass
 pass
 # correct cvh volumes ids for null nodes
 lid=fLID(sptf=sptf)
 for i in range(iCORR) :
  for j in range(iCORA) :
   ijj = i * iCORA + j
   if lid[ijj] == 0 :
    lcha[i][j]=-1
    lbyp[i][j]=-1
  pass
 pass
 t = (iCORR,iCORA,lz,lr,lcha,lbyp)
 return t
pass

def fGetlCv(sptf="MELPTF") :
 '''return list of all cvhs'''
 lCv=[]
 sCVHV = " CVH-VOLUME-NAME(("
 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  if line[:len(sCVHV)]==sCVHV :
   s=line[len(sCVHV):].split(")")
   i = int (s[0])
   ss=s[2].rstrip().lower()
   sss="cv%03d" % (i)
   lCv.append(sss)
   continue
 pass
 return lCv
pass

def fLID(sptf="MELPTF") : 
 '''determine number active and null core nodes
    return list of id: 
    1 active core cell, 
    0 null core cell'''
 p = subp.Popen(["readptf.exe", sptf, "COR-TSVC", "0"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 lid = []
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ss = line.split()
  for s in ss :
   x = float(s)
   if x>0.0 :
    lid.append(1)
   else :
    lid.append(0)
   pass
  pass
  break
 pass
 p.stdin.close()
 return lid
pass

def fReadTime(iMess=1,sptf="MELPTF") :
 '''get time from WARP variable
    return list of floats'''
 if (iMess==1):
  print("Reading time data ...")
 pass
 ltime=[]
 p = subp.Popen(["readptf.exe", sptf, "WARP"], 
                   stdin=subp.PIPE,
                   stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  s=line.split()
  try :
   ltime.append(float(s[0]))
  except :
   print(line)
  pass
 pass
 return ltime
pass

def fReadVar(sf, iMess=0, sptf="MELPTF", iCol=-1, sOpt="1") :
 '''read data for variable 
    return list of lists (time records) or list of floats
    input:
     sf    variable name
     iMess print information message, no message default
     sptf  melcor plot file
     iCol is column number starting from 0 = first column (even for sOpt="0" !)
     iCol = -1 => all columns in list 
     sOpt options on the readptf commandline
 '''
 if (iMess==1) :
  print("Read %s data ..." % (sf))
 pass
 l=[]
 p = subp.Popen(["readptf.exe", sptf, sf, sOpt], 
                  stdin=subp.PIPE,
                  stdout=subp.PIPE, 
                  stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ls = line.split()
  if len(ls)==1 :
    try :
     x = float (ls[0])
    except :
     x = 0.0
    pass
    l.append(x)
  else :  
   if iCol==-1 :
    ll=[]
    for ss in ls:
     try :
      x = float (ss)
     except :
      x = 0.0
     pass
     ll.append(x)
    pass
    l.append(ll)
   else :
    try :
     x = float (ls[iCol])
    except :
     x= 0.0
    pass
    l.append(x)
   pass
  pass
 pass
 p.stdin.close()
 return l
pass

def fReadVarIndex(sptf, index) :
 '''read data for variable 
    return list of lists (time records) or list of floats
    input:
     sf    variable name
     iMess print information message, no message default
     sptf  melcor plot file
     iCol is column number starting from 0 = first column (even for sOpt="0" !)
     iCol = -1 => all columns in list 
     sOpt options on the readptf commandline
 '''
 l=[] 
 p = subp.Popen(["readptf.exe", sptf, "varindex", "%s" % (index)], 
                  stdin=subp.PIPE,
                  stdout=subp.PIPE, 
                  stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ls = line.split()
  x = float (ls[0])
  y = float (ls[1])
  l.append([x,y])  
 pass
 p.stdin.close()
 return l
pass

def fReadVarC(nl,sf,iMess=0,sptf="MELPTF",sOpt="1") :
 '''read data for variable sf
    input :
     nl    number of columns to return
     sf    variable name
     iMess print information message, no message default
     sptf  melcor plot file
     sOpt options on the readptf commandline, include time default
    return :
     each data column in one list
    '''
 if (iMess==1) :
  print("Read %s data ..." % (sf))
 pass
 l=[]
 for i in range(0,nl) :
  ll=[]
  l.append(ll)
 pass
 p = subp.Popen(["readptf.exe", sptf, sf, sOpt], 
                  stdin=subp.PIPE,
                  stdout=subp.PIPE, 
                  stderr=subp.STDOUT)
 for bline in p.stdout :
   line = bline.decode("utf-8")
   s = line.split()
   for i,ll in enumerate(l) :
     try :
      x = float (s[i])
     except :
      x = 0.0
     pass
     ll.append(x)
   pass   
 pass
 p.stdin.close()
 return l
pass

def fLCVHi(licv,sptf="MELPTF") :
 '''get list of cvh indexes in MELPTF for cvh numbers 
    return list of integers
    (zero based index of cvh volumes, add 1 to get column number without time !)
    used in cor-volf.py
 '''
 licvt=[]
 lcvi=[]
 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
#  print line
  ss=line.split("(")
  #control volumes
  if ss[0]==" CVH-VOLUME-NAME" :
   sss=ss[2].split(")")
   i=int(sss[0])
   licvt.append(i)
  pass
 pass
 for icv in licv :
   try :
    icvi=licvt.index(icv)
   except :
    icvi=-1
   pass 
   lcvi.append(icvi)
 pass
 return lcvi
pass

def fReadCVHVar(sVar,lcvi,sptf="MELPTF",iMess=1) :
 '''read data for variable without time column
    lcvi is list of columns-1, it can be output of fLCVHi 
         (zero based index, no time)
    one list per time record
    '''
 if (iMess==1) :
  print("Read %s data ..." % (sVar))
 pass
 lzzz=[]
 p = subp.Popen(["readptf.exe", sptf, sVar,"0"], 
                  stdin=subp.PIPE,
                  stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ss = line.split()
  lzz=[]
  for i in range(len(lcvi)) :
   lzz.append(0.0)
  pass
  for i in range(len(lcvi)) :
    if (lcvi[i]>=0) :
     lzz[i]=float(ss[lcvi[i]])
  pass
  lzzz.append(lzz)
 pass
 return lzzz
pass

def fReadCVHVarC(sVar,lcvi,sptf="MELPTF",iMess=1) :
 '''read data for variable without time column
    lcvi is list of columns (zero based index, no time)
    one list per volume
    used in cor-volf.py
    '''
 if (iMess==1) :
  print("Read %s data ..." % (sVar))
 pass
 lzzz=[]
 p = subp.Popen(["readptf.exe", sptf, sVar,"0"], 
                  stdin=subp.PIPE,
                  stdout=subp.PIPE, stderr=subp.STDOUT)
 for i in range(len(lcvi)) :
  lzz=[]
  lzzz.append(lzz)
 pass
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ss = line.split()
  for i in range(len(lcvi)) :
    if (lcvi[i]>=0) :
     lzzz[i].append(float(ss[lcvi[i]]))
  pass
 pass
 return lzzz
pass

def fGetCVHAlt(lcv,sptf="MELPTF") :
 '''read cvh altitude volume table 
    input 
     list of integers - volume numbers
    return 
     list of lists of floats - elevations
     list of lists of floats - volumes

    fGetCVFLSetup provides also list of elevations

 '''
 lscvz=[]
 lscvv=[]
 llcv=[]
 icv0=0
 icv=0
 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ss=line.split("(")
  if ss[0]==" CVH-ALTITUDE" :
   sss=ss[2].split(")")
   icv=int(sss[0])
   if icv!=icv0 :
    if icv0>0 :
     lz.sort()
     lv.sort()
     if icv0 in lcv :
      llcv.append(icv0)
      lscvz.append(lz) 
      lscvv.append(lv) 
     pass
    pass
    lz = []
    lv = []
    icv0=icv
   pass
   sss=line.split("/")
   z=float(sss[-1])
   lz.append(z)
  pass
  if ss[0]==" CVH-VOLUME" :
   sss=ss[2].split(")")
   icv=int(sss[0])
   if icv!=icv0 :
    print("Error CVH-VOLUME ",icv,icv0)
    stop
   sss=line.split("/")
   z=float(sss[-1])
   lv.append(z)
  pass
 pass
 if (icv in lcv) and (not (icv in llcv)) :
  lz.sort()
  lv.sort()
  llcv.append(icv)
  lscvz.append(lz) 
  lscvv.append(lv) 
 pass
 #sort llcv according to lcv
 lscvzs=[]
 lscvvs=[]
 #print llcv
 #print lcv
 for icv in lcv :
  try :
   i = llcv.index(icv)
  except :
   continue 
  pass
  lscvzs.append(lscvz[i])
  lscvvs.append(lscvv[i])
 pass
 t = ( lscvzs, lscvvs) 
 return t
pass

def fGetCVHAltMid(llz) :
 '''cvh midpoint altitude 
    input 
     list of lists of elevations (can be output of fGetCVHAlt or fGetCVFLSetup)
    return 
     list of volumes midpoint elevations
 '''
 lz = []
 for l in llz :
  z =  sum(l) / float (len (l))
  lz.append(z)
 pass
 return lz
pass

def fReadHSVar(sVar,lhs,sptf="MELPTF",iMess=1) :
 '''read data for variable without time column

    input 
     sVar  HS variable containing all per node values (e.g. HS-TEMP)
     lhs   is list of heat structures
     sptf  MELCOR plot file, default MELPTF
     iMess print message, default yes 
    output
     list of lists (one per time record) of lists (one per hs) of values
    '''
 if (iMess==1) :
  print("Read %s data ..." % (sVar))
 pass
 llhsi = fGetHS_TEMP_Indexes(lhs,sptf=sptf)
 #print llhsi
 lllv=[]
 p = subp.Popen(["readptf.exe", sptf, sVar,"0"], 
                  stdin=subp.PIPE,
                  stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ss = line.split()
  llv=[]
  for lhsi in llhsi :
   lv=[]
   for ihsi in lhsi :
    lv.append(float(ss[ihsi]))
   pass
   llv.append(lv)
  pass
  lllv.append(llv)
 pass
 return lllv
pass

def fStripHSVars(lllv,i=0) :
 '''for lllv - output of fReadHSVar
    strip data for just one node
    by default the first temperature node
 '''
 mm = []
 for llv in lllv :
     m=[]
     for lv in llv :
         x = lv[i]
         m.append(x)
     pass
     mm.append (m)
 pass
 return mm
pass

def fGetHS_TEMP_Indexes( lhsn, sptf="MELPTF" ) :
 '''for list of HS numbers get list of HS-TEMP columns 
    one list per hs
    used in fReadHSVar
 '''
 llhsi  = []
 for ihsn in lhsn :
  lhsi=[]
  llhsi.append(lhsi)
 pass
 lhsi1 = []
 bRead = False
 p = subp.Popen(["readptf.exe", sptf, "index"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  if line.strip()=="*" :
   if bRead :
    break
  pass
  if bRead :
   s = line.split()
   for ss in s :
    lhsi1.append(ss)
   pass
   continue
  pass
  if line.strip()=="HS-TEMP" :
   bRead = True
  pass
 pass
 #print lhsi1
 for i,sh in enumerate ( lhsi1 ):
  ssh = sh [0:-2]
  ihs = int(ssh)
  try :
   ii = lhsn.index(ihs)
  except :
   ii = -1
  pass
  if ii>=0 :
   llhsi[ii].append(i)
  pass
 pass
 return llhsi
pass

def fGetHS_TEMP_Mask( lhsn, sptf="MELPTF" ) :
 '''for list of HS numbers get list of HS-TEMP columns 

    input 
     lhsn list of heat structures
     sptf MELCOR plot file (MELPTF by default)

    return 
     list containing 1.0 or 0.0
          1.0 this column belongs to hs from the lhsn
          0.0 this column does not belong to hs from the lhsn 

    note: this function was not used and tested yet

    use e.g. fDotList, fMulList or fMulListGeps 
    to further process returned list
 '''
 lhsi  = []
 lhsi1 = []
 bRead = False
 p = subp.Popen(["readptf.exe", sptf, "index"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  if line.strip=="*" :
   if bRead :
    break
  pass
  if bRead :
   s = line.split()
   for ss in s :
    lhsi1.append(ss)
    lhsi.append(0.0) 
  pass
  if line.strip=="HS-TEMP" :
   bRead = True
  pass
 pass
 for i,sh in enumerate( lshi1 ):
  ssh = sh [0:-2]
  if ssh in lhsn :
   lhsi[i]=1.0
 pass
 return lhsi
pass

def fDotList(l1,l2) :
 '''calculate dot product of two single dimension lists
    return float

    not tested
 ''' 
 sk = 0
 for x1,x2 in zip(l1,l2) :
  sk+=x1*x2
 pass 
 return sk
pass

def fMulList(l1,l2) :
 '''multiply list l1 by list l2
    return list

    not tested
 ''' 
 l=[]
 for x1,x2 in zip(l1,l2) :
  l.append(x1*x2)
 pass 
 return l
pass

def fMulListGeps(l1,l2,eps=1.0e-9) :
 '''multiply list l1 by list l2
    and return list containing only values 
    greater than eps

    not tested
 ''' 
 l=[]
 for x1,x2 in zip(l1,l2) :
  y = x1*x2
  if math.fabs(y)<eps :
   l.append(y)
 pass 
 return l
pass

def fGetCVFLSetup(sptf="MELPTF") :
 '''reads cvh fl definitions from MELPTF sp section

   output :
    lscvt     list of all cvh
    lscvz     list of lists of cvh elevations
    lscvv     list of lists of cvh volumes 
    lfl       list of all flowpaths
    lflfrom   list of all from volumes 
    lflto     list of all to volumes
    lflfromz  list of from elevations 
    lfltoz    list of to elevations

    used e.g. in cvh-t.py

 '''
 
 lscvt   =[]  
 lscvz   =[]  
 lscvv   =[]  
 lfl     =[]  
 lflfrom =[]  
 lflto   =[]  
 lflfromz=[]  
 lfltoz  =[]  
 icv0=0  
 ifl0=0  
 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                      stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  ss=line.split("(")
  #control volumes
  if ss[0]==" CVH-VOLUME-NAME" :
   sss=ss[2].split(")")
   i=int(sss[0])
   scv="cv%03d" % i
   lscvt.append(scv)
  if ss[0]==" CVH-ALTITUDE" :
   sss=ss[2].split(")")
   #print sss
   icv=int(sss[0])
   if icv!=icv0 :
    if icv0>0 :
     lz.sort()
     lv.sort()
     lscvz.append(lz) 
     lscvv.append(lv) 
    pass
    lz = []
    lv = []
    icv0=icv
   pass
   sss=line.split("/")
   z=float(sss[-1])
   lz.append(z)
  pass
  if ss[0]==" CVH-VOLUME" :
   sss=ss[2].split(")")
   icv=int(sss[0])
   if icv!=icv0 :
    print("Error CVH-VOLUME ",icv,icv0)
    stop
   sss=line.split("/")
   z=float(sss[-1])
   lv.append(z)
  #flow paths
  if ss[0]==" FL-PATH-FROM" :
   #print ss
   sss=ss[2].split(")")
   #print sss
   ifl=int(sss[0])
   if ifl!=ifl0 :
    if ifl0>0 :
     ssss="fl%03d" % (ifl0)
     lfl.append(ssss)
     lflfrom.append(sflfrom)
     lflto.append(sflto)
     lflfromz.append(zfrom)
     lfltoz.append(zto)
    pass
    ifl0=ifl
   pass
   z=float(sss[-1])
   sflfrom=("cv%03d" % z )
  pass
  if ss[0]==" FL-PATH-TO" :
   sss=ss[2].split(")")
   ifl=int(sss[0])
   if ifl!=ifl0 :
    print(ss)
    print("Error in flowpaths setup")
    stop
   pass
   z=float(sss[-1])
   sflto=("cv%03d" % z )
  pass
  if ss[0]==" FL-PATH-Z-FROM" :
   sss=ss[2].split(")")
   ifl=int(sss[0])
   if ifl!=ifl0 :
    print(ss)
    print("Error in flowpaths setup")
    stop
   pass
   zfrom=float(sss[-1])
  pass
  if ss[0]==" FL-PATH-Z-TO" :
   sss=ss[2].split(")")
   ifl=int(sss[0])
   if ifl!=ifl0 :
    print(ss)
    print("Error in flowpaths setup")
    stop
   pass
   zto=float(sss[-1])
  pass
 pass
 #add the last volume
 if icv0>0 and icv==icv0:
     lz.sort()
     lv.sort()
     lscvz.append(lz) 
     lscvv.append(lv) 
 pass
 #add the last flowpath
 if ifl0>0 and ifl==ifl0 :
   ssss="fl%03d" % (ifl0)
   lfl.append(ssss)
   lflfrom.append(sflfrom)
   lflto.append(sflto)
   lflfromz.append(zfrom)
   lfltoz.append(zto)
 pass
 #
 return (lscvt,lscvz,lscvv,lfl,lflfrom,lflto,lflfromz,lfltoz)
pass

def fGetSPStr(line,sF,lF) :
 '''auxilary function used in fSPHS
    checks if sF is found in the line 
    and adds sF into lF 
    note that lF is called by reference
    '''
 if line[:len(sF)]==sF :
  s=line[len(sF):].split(")")
  lF.append(s[-1])
  return True
 else :
  return False
 pass
pass

def fSPHS(sptf = "MELPTF") : # reads .SP/ section from binary file
 '''get informations about heat structures
    from the .SP/ section of the binary plot file

    input :
     sptf   binary file name (default MELPTF)

    output :
     lHSNumber         list of HS numbers from HS-NUMBER((i))
     lHSNumberofNodes  list of number of nodes from HS-NUMBER-OF-NODES((iHSnumber))
     lHSba             list of HS elevations from HS-BASE-ALTITUDE((iHSnumber))
     lHSlal            list of HS left axial lengths from HS-LEFT-AXIAL-LENGTH((iHSnumber)) 
     lHSName           list of HS names
 
    currently, it can be used to set up elevations of core boundary cylindrical HSs:
    z[i] = lHSba[i] +  lHSlal[i]/2.0

 '''
 sHSNumber        = " HS-NUMBER(("
 sHSName          = " HS-NAME(("
 sHSNumberofNodes = " HS-NUMBER-OF-NODES(("
 sHSlcv           = " HS-LEFT-VOLUME(("
 sHSrcv           = " HS-RIGHT-VOLUME(("
 sHSlal           = " HS-LEFT-AXIAL-LENGTH(("
 sHSral           = " HS-RIGHT-AXIAL-LENGTH(("
 sHSba            = " HS-BASE-ALTITUDE(("
 lHSNumber        = []
# lHSName          = []
 lHSNumberofNodes = []
# lHSlcv           = []
# lHSrcv           = []
 lHSlal           = []
# lHSral           = []
 lHSba            = []
 lHSName          = []

#  HS-NUMBER((33))2.0010000E+03                                            
#  HS-NAME((2001))R01                                                      
#  HS-NUMBER-OF-NODES((2001))2.0000000E+00                                 
#  HS-MULTIPLICITY((2001))1.0000000E+00                                    
#  HS-LEFT-VOLUME((2001))1.3100000E+02                                     
#  HS-RIGHT-VOLUME((2001))1.1000000E+01                                    
#  HS-LEFT-SURFACE-AREA((2001))1.0000000E-02                               
#  HS-RIGHT-SURFACE-AREA((2001))1.0000000E-02                              
#  HS-GEOMETRY((2001))RECTANGULAR                                          
#  HS-LEFT-AXIAL-LENGTH((2001))1.0000000E-02                               
#  HS-RIGHT-AXIAL-LENGTH((2001))1.0000000E-02                              
#  HS-BASE-ALTITUDE((2001))4.0475000E+00                                   
#  HS-ORIENTATION((2001))0.0000000E+00          

 p = subp.Popen(["readptf.exe", sptf, "sp"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 for bline in p.stdout :
  line = bline.decode("utf-8")
  if fGetSPStr(line,sHSNumber,lHSNumber) :
   continue
  if fGetSPStr(line,sHSNumberofNodes,lHSNumberofNodes) :
   continue
  if fGetSPStr(line,sHSba,lHSba) :
   continue
  if fGetSPStr(line,sHSlal,lHSlal) :
   #rint(line)
   continue
  if fGetSPStr(line,sHSName,lHSName) :
   continue  
 pass
 p.stdin.close()
 n = len (lHSNumber) 
 for i in range (n) :
  lHSNumber[i] = int (float(lHSNumber[i]))
  lHSNumberofNodes[i] = int (float(lHSNumberofNodes[i]))
  lHSba[i] = float(lHSba[i])
  lHSlal[i] = float (lHSlal[i])
  lHSName[i]=lHSName[i].strip()
 pass
 return ( lHSNumber, lHSNumberofNodes, lHSba, lHSlal, lHSName )
pass

def fIndexVar(sVar,sptf="MELPTF") : 
 '''reads variable index from binary file for a variable sVar'''
 # the same function is in readptf.py
 p = subp.Popen(["readptf.exe", sptf, "index"], stdin=subp.PIPE,
                     stdout=subp.PIPE, stderr=subp.STDOUT)
 iVar=0
 li=[]
 for bline in p.stdout :
  line = bline.decode("utf-8")
  if iVar == 1 :
   s = line.split() 
   if len (s) < 1 :
    break 
   for ss in s :
    try :
     i = int (ss)
    except :
     break 
    pass
    li.append(i)
   pass
  if line.strip()=="*" :
   if iVar == 1 :
    break
   else :
    continue
   pass
  pass
  if line.strip() == sVar :
   iVar=1
  pass
 pass
 return li
pass

def fIndexCORTLH(sptf) :
 '''for COR-TLH splits indexes to 
    ring numbers and
    layer numbers
 '''
 sVar = "COR-TLH"
 li = fIndexVar(sVar,sptf=sptf)
 lring = []
 llayer = []
 for i in li :
  iring,ilayer = divmod(i,100)
  lring.append(iring)
  llayer.append(ilayer)
 pass
 return (lring,llayer)
pass

def fMaxCORTLHPL(sptf) :
 '''Max COR-TLH per layer

    return maximum temperature of lower head layers'''

 sVar="COR-TLH"
 lr,la = fIndexCORTLH(sptf=sptf)
 llx = fReadVar(sVar, sptf=sptf) 
 lsa = set (la)
 lsr = set (lr)
 llm = []
 for lx in llx :
  lm = [lx[0]]
  for i in range(len(lsa)) :
   lm.append(0.0)
  pass
  for i in range(len(la)) :
   ia = la[i]
   if lm[ia]<lx[i+1] :
    lm[ia]=lx[i+1]
   pass
  pass
  llm.append(lm)
 pass 
 return llm
pass

def fSumCols(sVar,lcol,sptf="MELPTF") :
 '''Calculates sum of selected columns for variable sVar
    input :
     sVar variable name
     lcol list of columns numbers (as string or integers)
          (time is column 0)
    return 
     list of tuples (time, value)      

 '''
 llv = fReadVar(sVar, iMess=0, sptf=sptf)
 lx = []
 for lv in llv :
  x = 0
  for si in lcol :
   i=int(si)
   #x+=lv[i-1] # time is in column 1
   x+=lv[i] # time is in column 0
  pass
  lx.append( (lv[0],x) )
 pass
 return lx
pass 

def fPrintList(sFile,llx,bT=False) :
 '''print list of values into a space separated ascii file

    input :
     sFile file name or * for stdout
     llx   two dimensional list
     bT    boolean transpose, default False
           True one value from each list in row
           False one list in one row
    return :
     nothing

    note: use fReadSPSData to read file back
 '''
 if sFile=="*" :
  f=sys.stdout
 else :
  f=open(sFile,'w')
 pass
 if bT :
  nr = len(llx[0])
  nc = len(llx)
  for i in range(nr) :
   for j in range(nc) :
    f.write ("%f " % (llx[j][i]))
   pass
   f.write ("\n")
  pass
 else :
  for lx in llx :
   for x in lx :
    f.write ("%f " % (x))
   pass
   f.write ("\n")
  pass
 f.close()
pass

def fSumCor(lVar,sptf="MELPTF",iCoreSP=19,iFollSP=11) :
 '''vver-440 specific function

    calculates sum of values for three zones of the core
    nodalization: 
     upper core  
     followers zone
     lower plenum

    input :
     lVar - list of core variable 
     sptf - MELPTF file name
     iFollSP - the top most axial level to include to the lower plenum (bottom node is 1)
     iCoreSP - the top most axial level to include to the follower zone  

    return :
     list of tuples : (time, sum core, sum followers, sum lower plenum)

 '''
 #print sptf, iCoreSP,iFollSP
 (nR,nA) = fCorRA(sptf=sptf)
 nV = len(lVar)
 if nV>1 :
  lllx = []
  k = 0
  for sVar in lVar :
   k+=1
   #print k,sVar
   laux=fReadVar(sVar,iMess=0,sptf=sptf)
   lllx.append(laux)
  pass
  llx = lllx[0]
  nT = len(llx)
  #print lVar
  #print len(lllx)
  nC = len(llx[0])
  for k in range(1,nV) :
   #print k, len(lllx[k])
   for j in range(nT)   :
    for i in range(1,nC) :
     x=lllx[k][j][i]
     llx[j][i]+=x
    pass
   pass
  pass
 else :
  llx = fReadVar(lVar[0],iMess=0,sptf=sptf) 
 pass
 lxout=[]
 for lx in llx :
  xcor = 0.0
  xfol = 0.0
  xlp  = 0.0
  for i in range(nR) :
   for j in range(nA) :
    x = lx[ i*nA + j + 1 ] 
    if j < iFollSP :
     xlp+=x
    else :
     if j < iCoreSP : 
      xfol+=x
     else :
      xcor+=x
     pass
    pass 
  pass
  lxout.append( (lx[0],xcor,xfol,xlp) )
 pass
 return lxout
pass

def fCalWLC(lcha,lcv,lw,lz0,lz1,nRows,it) :
 '''Calculate water level in the cell
    used in cor-volf.py '''
 lzcha=[]
 for i,lcha1 in enumerate(lcha) :
  for jj,icv in enumerate(lcha1) :
      try :
       ilw = lcv.index(icv)
      except :
       ilw = -1
      pass
      if ilw>=0 :          
       z=lw[ilw][it]
       ii = jj + i*nRows
       z0=lz0[ii]
       z1=lz1[ii]
       if z>=z1 :
           zf = 1.0
       elif z>z0 :
           zf = (z-z0)/(z1-z0)
       else :
           zf = 0.0
       pass
      else :
       zf=0.0
      pass 
      lzcha.append(zf)
  pass
 pass
 return lzcha
pass

def fReadSPSData(sf,lc=[]) :
 '''reads space separated ascii data
 
    input:
        sf - file name
        lc - list of column numbers 
             optional return all columns by default

    output:
        ll - list of list data values 

    note: use fPrintList to output data 
 '''
 ll=[]
 f = open(sf,'r')
 for line in f :
  l = []
  s = line.split()
  if len (lc) > 0 :
   for i in lc :
    ss = s[i-1] 
    try :
     x = float(ss)
    except :
     x = "#N/A" 
    pass
    l.append(x)
   pass
  else :
   for ss in s :
    try :
     x = float(ss)
    except :
     x = "#N/A" 
    pass
    l.append(x)   
   pass
  pass
  if len(l) > 0 :
   ll.append(l)
  pass
 pass 
 return ll
pass

def transposed(lists):
   '''transpose lists
      from http://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
   '''
   if not lists: return []
   return list(map(lambda *row: list(row), *lists))
pass

def transposed2(lists, defval=0):
   '''transpose lists, put default value if size is insufficient
      from http://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
   '''
   if not lists: return []
   return list(map(lambda *row: [elem or defval for elem in row], *lists))
pass

def fSumVarsCol(lVars,liCol=[],sptf="MELPTF") :
 ''' calculate sum of specified columns for list of variables 

     input:
      lVars - list of variables (string)
      liCol - list of column index to sum for each variable
              (string or integer or list of integers)
              0 is time column !!!
              default = 1 
     
     output 
      tuple : (list of times, list of values)

     used e.g. in melpycal/sumvarcol.py
 '''
 lx = []
 lTime = fReadTime(iMess=0,sptf=sptf)
 for xt in lTime :
  lx.append(0.0) 
 pass
 for i in range (len(lVars)) :
  if ( type(liCol[i])==list ) :
   laux,lx1 = transposed( fSumCols(lVars[i],liCol[i],sptf=sptf) )
  else :
   try :
    iCol = int (liCol[i]) # index is not obligatory 
   except :
    iCol = 1 # assume the first column not counting time
   pass
   lx1 = fReadVar(lVars[i],iMess=0,iCol=iCol-1,sptf=sptf,sOpt="0") # do not include time column
  pass
  if len(lx1)== len(lx) :
   for j in range(len (lx)):
    lx[j]+=lx1[j]
   pass
  else :
   print("#variable %s skipped" % (lVars[i]))
  pass
 pass
 return (lTime,lx)
pass

def fSumVars(lVars,sptf="MELPTF") :
 ''' calculate sum for list of variables

     input:
      lVars - list of variables (string)
     
     output 
      list of list of values, time is the first value in the list
 '''
 llx = fReadVar(lsVar[0],iMess=0,iCol=-1,sptf=sptf,sOpt="1") # include time column
 for i in range(1,len(lsVar)) :
  llx1 = fReadVar(lsVar[i],iMess=0,iCol=-1,sptf=sptf,sOpt="0") # do not include time column
  for j in range(len(llx)):
   for k in range (len(llx1[j])) :
    llx[j][k+1]+=llx1[j][k]
   pass
  pass
 pass
 return llx
pass

def fSumLists(l) :
 '''l is list of lists of floats
    it can be output of fReadVarC

    return list of i-th item from each list 
 '''
 nr=len(l[0])
 nc=len(l)
 lr = []
 for i in range(nr) :
  xs = 0.0
  for j in range(nc) :
   xs+=l[j][i]
  pass
  lr.append(xs)
 pass
 return lr
pass

def fSubList(lx1,lx,ly) :
 '''return sublist of ly  
    
    input :
     lx1 list of items from lx 
     lx  list of items
     ly  list of values for items in lx

    return :
     ly1  list of values for items in lx1
 '''
 ly1=[]
 for x in lx1 :
  i = lx.index(x)
  y = ly[i]
  ly1.append(y)
 pass 
 return ly1 
pass

def fCVStoICV(lcvs) :
 '''convert list of strings to integer skipping first two letters
    eg: flxxx -> xxx, cvxxx -> xxx 
    
    note: use fLCVHi to get list of cvh colums from cvh numbers
 '''
 licv = []
 for scv in lcvs :
  icv = int (scv[2:])
  licv.append(icv)
 pass
 return licv
pass

def fTimeIntegral(l) :
 '''calculate simple integral for a list of lists,
    assuming list contain [time,value] pairs  

    use scipy later?
 ''' 
 xi=0.0
 x0 = 0.0
 y0 = 0.0
 li=[]
 for ll in l:
  x=ll[0]
  y=ll[1]
  xi+= (x-x0) * (y+y0) / 2.0  
  x0=x
  y0=y
  li.append([x,xi])
 pass
 return li
pass

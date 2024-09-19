#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

   python module for calculation of decay power input for the MELCOR
   code, based on ORIGEN-Scale output for the end of cycle fuel
   irradiation history

   Petr Vokac
   UJV Rez, a.s.
   June 2012
   "as-is" license

   Nomenclature:

   Z - proton number
   A - atomic number

   References :

   [ENDF6FM]
   ENDF-6 Formats Manual
   Data Formats and Procedures for the Evaluated Nuclear Data Files ENDF/B-VI and ENDF/B-VII
   Written by the Members of the Cross Sections Evaluation Working Group
   Edited by A. Trkov, M. Herman and D. A. Brown
   CSEWG Document ENDF-102, Report BNL-90365-2009 Rev.2

   Modifications:

   30.7.2012 : added function fMelFltStr
    1.8.2012 : handling of compound dummies
   21.9.2012 : handling of upper case filenames from SKODA (s=line.strip() #.lower())
   9.11.2012 : added forgotten conversion of activities for "activity.txt" output. 
               New member function lisotope.fScale() added,
               lisotope.fPower() modified not to scale powers,
               activities are scaled when masses are read
  12.11.2012 : in lactivity.fRead() ignore activitities equal (or less than) zero
  13.11.2012 : additional options to config.conf to facilitate output
               nmaxchar=79 instead of nmaxchar=80
  18.12.2012 : nmaxchar=70 instead of nmaxchar=79, is it an error in MELCOR?
    9.4.2013 : tested by pychecker: f.close -> f.close()
   18.4.2013 : added description of functions for pydoc
  14.10.2013 : added ConvMass for input data normalization to common U mass
             : check the time in the config is monotonous
  10.11.2013 : check empty line in the activity (Ci) input files
  18.11.2013 : gamma spectra 
  15.04.2015 : compatibility with python3 
  15.04.2015 : calculate inventory for the time "zero" (first time in array)
  13.05.2015 : compatibility with python3 
   9.09.2015 : corrected error in elmass fRead(self, ...)
  28.07.2016 : checking of total initial inventory output
               corrected config printout when initial inventory output requested
'''
#import additional modules
import sys
import string
import os
import pickle
import scipy.linalg
import math

'''auxiliary functions to read ENDF decay data files'''
def fHead(hl) :
 '''parse endf head string
    see [ENDF6FM] 0.6.3.3 HEAD Record
 '''  
 c1 = hl[0:11]
 c2 = hl[11:22]
 l1 = hl[22:33]
 l2 = hl[33:44]
 l3 = hl[44:55]
 l4 = hl[55:66]
 return (c1,c2,l1,l2,l3,l4)
pass
def fFloat(cx) :
 '''convert endf float to python float''' 
 scx=cx.strip()
 ie=0
 i=scx.rfind("+")
 if i>1 :
  ie = int(scx[i:])
  scx = scx[:i]
 pass
 i=scx.rfind("-")
 if i>1 :
  ie = int(scx[i:])
  scx = scx[:i]
 pass
 scx=scx.rstrip("E")
 scx=scx.rstrip("e")
 x = float (scx)
 x*=10**ie
 return x
pass
def fZA(za) :
 '''convert endf ZA variable to Z and A'''   
 x=fFloat(za)
 a = int(round(x))
 z = int (a/1000)
 a-=z*1000
 return (z,a)
pass
'''other auxiliary functions'''
def fMelFltStr(x,y) :
 '''attempt for short format of float for MELCOR,
    add dot and zero when the float has integer value
 '''
 sx=" "+str(x)
 if not "." in sx : sx+=".0"
 sy=" %.5g" % (y)
 if (not "." in sy) and (not "e" in sy) : sy+=".0"
 return sx+sy
pass

#******************************************
class elements :
 '''elements class,
    auxiliary class for

    conversion between: element abbreviation <-> Z

    distribution of elements to MELCOR groups
    
 '''  
 def __init__(self) :
  #list of elements ordered according to Z
  self.labr = [
  "H",                                     "He",
  "Li", "Be",  "B",  "C",  "N",  "O",  "F",  "Ne",
  "Na", "Mg", "Al", "Si",  "P",  "S", "Cl",  "Ar",
  "K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr",
  "Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe",
  "Cs","Ba","La",
  "Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu",
  "Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn",
  "Fr","Ra","Ac",
  "Th","Pa","U","Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr",
  "Ku","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg","Cn"
  ]
  # output will be calculated only for selected MELCOR elements
  self.lelmel= [
           "Kr","Xe","Rb","Cs","Sr","Ba","Br","I","Se","Te","Ru","Rh","Pd","Nb",
           "Mo","Tc","Zr","Ce","Np","Pu","Y","La","Pr","Nd","Pm","Sm","Eu","U",
           "Ag","Sn","As","Sb","Cd","Am","Cm"
  ]
  # isotopes to move, the first guess from ori2003 and update for endf.py in 2012
  self.lmove = [
   ("CU66  ","Ni"),
   ("SE77M ","As"),
   ("SE79M ","As"),
   ("KR83M ","Br"),
   ("Y89M  ","Sr"),
   ("Y90   ","Sr"),
   ("Y91M  ","Sr"),
   ("NB95  ","Zr"),
   ("NB95M ","Zr"),
   ("NB97  ","Zr"),
   ("NB97M ","Zr"),
#   ("TC99M ","Mo"), #removed
   ("TC103 ","Mo"), #new
   ("AG109M","Pd"),
   ("AG111M","Pd"),
   ("AG112 ","Pd"),
   ("IN115M","Cd"),
   ("IN117 ","Cd"),
   ("IN117M","Cd"),
   ("IN118 ","Cd"),
   ("XE134M","I" ),
   ("BA136M","Cs"),
   ("BA137M","Cs"),
   ("HO166 ","Dy"),
   ("W183M ","Ta"),
   ("RE188 ","W" ),
   ("RB90 ", "Kr"), #new
   ("RB88 ", "Kr"), #new
   ("I132",  "Te"), #new
   ("RH106", "Ru"), #new
   ("PR144", "Ce"), #new
   ("PR144M","Ce"), #new
   ("RH103M","Ru"), #new
   ("RH105M","Ru"), #new
   ("RH106", "Ru"), #new
   ("RH100", "Pd")  #new
  ]
  # 
  self.lmovei=[] # list of tuples Z,A,isomer for moved isotopes
  for move in self.lmove:
    t=self.fGetZAI(move[0])
    self.lmovei.append(t)
  pass  
  #
  self.lelmelz=[] # Z for each melcor element group
  for el in self.lelmel :
   i = self.labr.index(el) + 1
   self.lelmelz.append(i)
  pass
  #
  # list of dummy compounds
  self.ldummy=['CI'] 
  # list of lists of dummy compound recipe: tuple of name, weight in compound, average element mass number
  self.lldumycomp=[[('Cs',1.0,133),('I',1.0,127)]]
 pass
 def fPrint(self) :
  '''print out the data for checking'''   
  for i,sabr in enumerate(self.labr) :
   print("%3d %2s" % (i+1,sabr))
  pass
 pass
 def fPrintMELCORElements(self) :
  '''information print of MELCOR elements and compounds'''
  print("MELCOR elements list")
  for i,sel in enumerate(self.lelmel) :
   print("%2d %s" % (i+1,sel))
  pass
  print("MELCOR compounds")
  for i,(sdummy,ldc) in enumerate(zip(self.ldummy,self.lldumycomp)) :
   print("%2d %s, composed of" % (i+1,sdummy)) 
   for t in ldc : 
    print("%10s fraction %g mass %g " % t)
  pass
 pass
 def fGetZ(self,s) :
  '''return element Z for given element abbreviation,
     works with ORIGEN isotope format:
     N[N]X[X][X][M]
     where N is letter
           X is number
           M is isomer indicator
     character in [] is optional

     when the element is not recognized,
     return -1
  '''   
  sab = s.strip()
  if sab=="SUMTOT" :
   i=-1
   return i
  pass
  sab = sab[:2]
  if len(sab)<2 :
   i=-1
   return i   
  pass
  #s1=string.ascii_uppercase(sab[0])
  s1 = sab[0].upper()
  #i = string.letters.find(sab[1])
  i = string.ascii_letters.find(sab[1])
  if i<0 :
   s2=""
  else :
   #s2=string.lower(sab[1])
   s2 = sab[1].lower()
  pass
  sab=s1+s2
  try :
   i = self.labr.index(sab) + 1
  except : 
   i = -1
  pass
  return i
 pass
 def fGetA(self,s) :
  '''return element A and isomer state
     for given element abbreviation,
     works with ORIGEN isotope format:
     N[N]X[X][X][M]
     where N is letter
           X is number
           M is isomer indicator
     character in [] is optional      

     when the element is not recognized,
     return -1
  '''   
  sab = s.strip()
  iIsomer=0
  if len(sab)>=2 :
   if sab[-1]=="M" or sab[-1]=="m" :
    iIsomer=1
    sab=sab[:-1]
   else :
    iIsomer=0
   pass
   if len(sab)<2 :
    return (-1,0)
   pass
   i=1
   #j = string.letters.find(sab[i])
   j = string.ascii_letters.find(sab[i])
   if j>=0 :
    i+=1
   pass
   sab=sab[i:]
   try :
    i = int(sab)
   except :
    i=-1
   pass
  else:
   i=-1
  pass 
  return (i,iIsomer)
 pass
 def fGetZAI(self,s):
  '''input origen isotope name
     return Z,A,isomer
  '''
  iz = self.fGetZ(s)
  ia,ii = self.fGetA(s)
  return iz,ia,ii
 pass
 def fGetAbr(self,iz) :
  '''return element abbreviation
     for given element Z
  '''   
  i=iz-1
  if i<len(self.labr) and i>=0 :
   s=self.labr[i]
  else :
   s="none"
  pass
  return s
 pass
 def fGetOrigenName(self,t) :
  '''get ORIGEN isotope name
     input T is the tuple of integers containing
     Z,A,isomer
  '''
  sel=self.fGetAbr(t[0])
  sa = "%d" % (t[1])
  sm = " "
  if t[2]>0 : sm="M"
  return sel+sa+sm
 pass
pass
#******************************************
class elmass :
 '''class to store mass of elements
    it is stored in a scipy.array containing all
    elements from elements.labr 
 ''' 
 def __init__(self,sfn="") :
  global gcel 
  self.mass = scipy.zeros([len(gcel.labr)])
  if len(sfn)>0 :
   self.fRead(sfn)
  pass 
 pass
 #
 def fRead(self,sfn,bVerbose=True):
  global gcel
  lig=[]
  lel=[]
  for el in gcel.labr :
   lel.append(el.lower())
  pass
  print("Reading %s input file ..." % (sfn))
  f=open(sfn,'r')
  for line in f :
   s=line.strip().lower().split()
   if len(s)>1 :
    try :
     i = lel.index(s[0])
    except :
     i = -1
    pass
    if i>=0 : # if i>0 :# corrected 9.09.2015
     self.mass[i]+=float(s[1])
    else:
     lig.append(s[0]) 
    pass  
   pass 
  f.close()
  if len(lig)>0 and bVerbose :
   print("Items ignored from file %s :" % (sfn))
   #150513 print(string.join(sorted(set(lig))," "))
   print( "" .join(sorted(set(lig))) )
  pass
 pass
 #
 def fPrint(self) :
  '''print masses of elements to stdout'''
  global gcel  
  for el,xm in zip(gcel.labr,self.mass) :
   print(el,xm)
  pass 
 pass
 #
 def fPrintMelInc(self,sfn):
  '''print MELCOR 1.8.6 input data for masses of elements into 
     file sfn
  '''
  global gcel 
  iout = 0
  fo=open(sfn,"w")
  for iel,el in enumerate(gcel.lelmel):
    i=gcel.labr.index(el) 
    me=self.mass[i]
    fo.write("dchnem%02d%02d %s %f\n" % (iel,iout,el,me))
  pass
  fo.close()
 pass
 #
 def fGetElMass(self,el) :
  global gcel
  i=gcel.labr.index(el) 
  me=self.mass[i]
  return me  
 pass
 #
 def fPrintORIGENFormat(self,sout) :
  '''print masses of elements to stdout'''
  global gcel
  f = open(sout,'w')
  for el,xm in zip(gcel.labr,self.mass) :
   if xm>0.0 :
    f.write("%3s %g\n" % (el,xm))
   pass 
  pass
  f.close()
 pass
pass
#end of elmass class
#******************************************
class activity :
 '''activity class
    used to store data read from ORIGEN output
 '''  
 def __init__(self,abr = "",z = 0,a = 0,isomer=0,x = 0.0) :
  self.abr = abr
  self.z = z
  self.a = a
  self.isomer=isomer
  self.x = x
 pass
 def fPrint(self) :
  print(self.abr,self.x,self.z,self.a,self.isomer)
 pass
pass 
#******************************************
class lactivity :
 '''lactivity class --- list of activity classes'''
 def __init__(self) :
  self.l = []
 pass
 def fAdd(self,act) :
  self.l.append(act)
 pass
 def fRead(self,sfn,bVerbose=False) :
  '''read ORIGEN output segment'''
  global gcel
  sys.stdout.write("Reading %s input file ...\n" % (sfn))
  sys.stdout.flush()
  lig=[]
  f=open(sfn,'r')
  for line in f :
   s=line.split()
   if len(s) > 1 : #10.11.2013 check empty line 
    x = 0.0   
    z=gcel.fGetZ(s[0])
    if z>0 :
     ta=gcel.fGetA(s[0])
     if ta[0]>0 :
      x = float(s[1])
      if x>0.0 :
       ca=activity(s[0],z,ta[0],ta[1],x)
       self.fAdd(ca)
      pass
     pass
    pass
    if x<=0.0 :
     lig.append(s[0]) 
    pass
   pass
  pass 
  f.close()
  if len(lig)>0 and bVerbose:
   print("Items ignored from file %s :" % (sfn))
   #150513 print(string.join(sorted(set(lig))," "))
   print( " ".join(sorted(set(lig))) )
  pass
 pass
 def fMultiplyActi(self,x) :
  '''multiply activities by x '''
  for ci in self.l :
   ci.x*=x
  pass
 pass
 def fPrint(self) :
  for ca in self.l :
   ca.fPrint()
  pass
 pass
pass
#******************************************
class spectrum :
 def __init__(self) :
  self.styp=0.0 # Decay radiation type
  self.lcon=0   # Continuum spectrum flag
  self.ner=0    # Total number of tabulated discrete energies for a given spectral type (STYP).
  self.fd=0.0   # Discrete spectrum normalization factor (absolute intensity/relative intensity).
  self.dfd=0.0  # 
  self.erav=0.0 # Average decay energy of radiation produced
  self.drav=0.0 #
  self.fc=0.0   # Continuum spectrum normalization factor (absolute intensity/relative intensity).
  self.dfc=0.0  #
  self.lsd=[]
 pass 
 def fPrint(self) :
  if self.styp == 0.0 : 
   s1 = "Gamma rays"
  elif self.styp == 1.0 : 
   s1 = "Beta rays"
  elif self.styp == 2.0 : 
   s1 = "Electron capture and/or positron emission"
  elif self.styp == 4.0 : 
   s1 = "Alpha particles"
  elif self.styp == 5.0 :    
   s1 = "Neutrons"
  elif self.styp == 6.0 : 
   s1 = "Spontaneous fission fragments"
  elif self.styp == 7.0 : 
   s1 = "Protons"
  elif self.styp == 8.0 : 
   s1 = "Discrete electrons"
  elif self.styp == 9.0 : 
   s1 = "X-rays and annihilation radiation"
  else: 
   s1 = "Unknown radiation type %f" % self.styp
  pass
  if self.lcon == 0 :
   s2 = "Discrete"
  elif self.lcon == 1 :
   s2 = "Continuous"
  elif self.lcon == 2 :
   s2 = "Discrete and Continuous"
  else :
   s2 = "Uknown lcon = %d" % (self.lcon)
  pass                     
  print(s1, "-", s2)
  if self.lcon == 0 :
   print("Discrete normalization coefficient: %f" % self.fd)
  elif self.lcon == 1 :
   print("Continuous normalization coefficient: %f" % self.fc)
  elif self.lcon == 2 :
   print("Discrete normalization coefficient: %f" % self.fd)
   print("Continuous normalization coefficient: %f" % self.fc)
  else :
   pass
  pass
  for sd in self.lsd:
   sd.fPrint()     
 pass
pass    
#
class spectrumd :
 def __init__(self) :
  self.er = 0.0     # discrete energy (eV) of radiation produced
  self.der = 0.0    #
  self.rtyp = 0.0   # Mode of decay of the nuclide in its LIS state. ???
  self.type = 0.0   # Type of transition for beta and electron capture
  self.ri = 0.0     # intensity of discrete radiation produced (relative units).
  self.dri = 0.0    # 
  self.ris = 0.0    # Internal pair formation coefficient (STYP=0.0)
  self.dris = 0.0   #
  self.ricc = 0.0   # Total internal conversion coefficient
  self.dricc = 0.0  #
  self.rick = 0.0   # K-shell internal conversion coefficient
  self.drick = 0.0  #
  self.ricl = 0.0   # L-shell internal conversion coefficient
  self.dricl = 0.0  # 
 pass
 def fPrint(self):
   print("   ", self.er, self.ri)
 pass    
pass     
#
class spectra :
 '''Auxiliary class to store spectra in spectra.pickle'''
 def __init__(self) :
  self.lza = []
  self.llspectrum = [] # list of spectrums
 pass
 def fSavePickle(self,sfn="spectra.pickle") :
  '''save the database to a pickle file
  '''
  f=open(sfn,'w')
  pickle.dump(self.lza,f)
  pickle.dump(self.llspectrum,f)
  f.close()
  print(sfn, "written")
 pass
 def fLoadPickle(self,sfn="spectra.pickle") :
  '''load the database from the pickle file'''
  print("Reading ", sfn, " ...")
  #f=open(sfn,'r')
  f=open(sfn,'rb')
  self.lzaliso=pickle.load(f)
  self.llspectrum=pickle.load(f)
  f.close()
 pass 
pass
#
class isotope :
 '''isotope class:
    store isotope properties from the ENDF decay data,
    store activity
 '''  
 def __init__(self) :
  self.z = 0         # number of protons
  self.a = 0         # number of nucleaons
  self.liso = 0      # isomer 
  self.t12 = 0.0     # decay half time
  self.elp = 0.0
  self.eem = 0.0
  self.ehp = 0.0
  self.lrtyp = []   # list of tuples (rtyp,rfs,q,br)
  self.lchild = []
  self.acti = 0.0
  self.aacti = None # it will be scipy.array of activities
  self.lspectrum = []
 pass
 def fReadENDF(self,sfn) :
  '''reads endf data file'''  
  nndk=-1 # ==-1: ndk not read, >0: nndk=ndk, Total number of decay modes given.
  nst=-1 # -1 not read, Nucleus stability flag (NST=0, radioactive; NST=1, stable)
  istyp=-1 # auxiliary variable  
  iner=-1 # auxiliary variable  NER Total number of tabulated discrete energies for a given spectral type (STYP).
  f=open(sfn,'r')
  for line in f :
   i=0
   ii=66
   hl = line[i:i+ii]
   i+=ii
   ii=4
   mat = int(line[i:i+ii])
   i+=ii
   ii=2
   mf = int(line[i:i+ii])
   i+=ii
   ii=3
   mt = int(line[i:i+ii])
   i+=ii
   ii=5
   ns = int(line[i:i+ii]) # line counter
   if (mt==457) :
    if nst == 0 and nndk>0 : # radioactive and ndk read
     t = fHead(hl)
     rtyp=fFloat(t[0])
     rfs=fFloat(t[1])
     q = fFloat(t[2])
     br = fFloat(t[4])
     self.lrtyp.append( (rtyp,rfs,q,br) )
     nndk-=1   # decrease counter nndk
     continue 
    pass 
    if ns == 1 : # first line 
     za,awr,lis,liso,snst,snsp = fHead(hl)
     nst=int(snst)
     nsp=int(snsp)
     self.z,self.a = fZA(za)
     self.liso = int(liso)
     nndk=-1  # ndk not read, reset counter
     continue 
    pass
    if nst == 0 and ns == 2 :
     t12,dt12,l1,l2,npl,n2 = fHead(hl)
     self.t12 = fFloat(t12)
     continue 
    pass
    if nst == 0 and ns == 3 :
      t = fHead(hl)
      self.elp=fFloat(t[0])
      self.eem=fFloat(t[2])
      self.ehp=fFloat(t[4])
      continue 
    pass
    if nst ==  0 and ns > 3 and nndk<0 :  
     spi,par,l1,l2,ndk6,ndk = fHead(hl)
     nndk=int(ndk)
     continue 
    pass
    if nst ==  0 and ns > 3 and nndk==0 and istyp==-1 and iner<0 :  
     fnula,styp,lcon,inula,isest,ner = fHead(hl)
     self.lspectrum.append(spectrum())
     self.lspectrum[-1].styp=fFloat(styp) 
     self.lspectrum[-1].lcon=int(lcon)
     self.lspectrum[-1].lner=int(ner)
     istyp=0
     continue
    pass
    if nst ==  0 and ns > 3 and nndk==0 and istyp==0 and iner<0 :  
     fd,dfd,erav,derav,fc,dfc = fHead(hl)
     self.lspectrum[-1].fd=fFloat(fd)
     self.lspectrum[-1].dfd=fFloat(dfd)
     self.lspectrum[-1].erav=fFloat(erav)
     self.lspectrum[-1].derav=fFloat(derav)
     istyp=-1
     iner = int(ner)
     ner = "" # invalidate ner
     if (int(lcon)!=1): inl=2  # number of next records to read
     continue
    pass   
    # gamma, change conditions later
    if nst ==  0 and ns > 3 and nndk==0 and istyp==-1 and iner>0 and (int(lcon)!=1):  
     if inl==2 :    
      er,der,inula,inula,snt,inula = fHead(hl)
      self.lspectrum[-1].lsd.append(spectrumd())
      self.lspectrum[-1].lsd[-1].er=fFloat(er)
      self.lspectrum[-1].lsd[-1].der=fFloat(der)
      nt=int(snt) # Number of entries given for each discrete energy (ER).      
     elif inl==1 :
      rtyp,type,ri,dri,ris,dris = fHead(hl)
      self.lspectrum[-1].lsd[-1].rtyp=fFloat(rtyp)
      self.lspectrum[-1].lsd[-1].type=fFloat(type)
      self.lspectrum[-1].lsd[-1].ri=fFloat(ri)
      self.lspectrum[-1].lsd[-1].dri=fFloat(dri)
      self.lspectrum[-1].lsd[-1].ris=fFloat(ris)
      self.lspectrum[-1].lsd[-1].dris=fFloat(dris)
     elif inl==0 :
      ricc,dricc,rick,drick,ricl,dricl = fHead(hl)
      self.lspectrum[-1].lsd[-1].ricc=fFloat(ricc)
      self.lspectrum[-1].lsd[-1].dricc=fFloat(dricc)
      self.lspectrum[-1].lsd[-1].ricl=fFloat(ricl)
      self.lspectrum[-1].lsd[-1].dricl=fFloat(dricl)
      self.lspectrum[-1].lsd[-1].rick=fFloat(rick)
      self.lspectrum[-1].lsd[-1].drick=fFloat(drick)
     pass
     inl-=1
     if inl<0 or (inl==0 and nt==6) : # For gamma ray emission (STYP=0.0), no other information is required if X-ray, Auger electron, conversion electron, and pair formation intensities have not been calculated for these transitions. In this case NT=6.
      iner-=1
      if iner==0 : iner=-1
      if int(lcon)==0: inl=2   
     pass
    
     #print ns        
     continue
    pass   
   pass
   if (mt==454) :
    #not implemented yet
    pass
   pass
  pass
  f.close()
 pass
 def fPrint(self) :
  ''' debug printout
      print isotope data
  '''  
  print("Z = %d A = %d Isomer = %d T1/2 = %e s" % (self.z, self.a, self.liso, self.t12))
  print("ELP = %f EEM = %f EHP = %f" % (self.elp, self.eem, self.ehp))
  print("RTYP: ", self.lrtyp)
  print("CHILDS: ", self.lchild)
  print("Activity %e Bq" % (self.acti))
  if self.aacti!=None : print(self.aacti)
  for spec in self.lspectrum :
   spec.fPrint()
  pass    
 pass 
 def fEnergy(self) :
  '''return average released energy in eV per decay''' 
  p=0.0
  if (self.elp)>0.0 : p+=self.elp
  if (self.eem)>0.0 : p+=self.eem
  if (self.ehp)>0.0 : p+=self.ehp
  return p
 pass
 def fDecay(self,lt) :
  '''calculate decay of isotope without radioactive child'''
  global ln12,dtmin 
  if self.acti>0.0 :
   self.aacti[0] = self.acti
   a = self.aacti[0]
   nt = len(lt)
   for i in range(1,nt) :
    dt = lt[i]-lt[i-1]
    if dt>dtmin :
     xexp = -1.0*dt*ln12/self.t12
     a = a * math.exp(xexp) 
    pass
    self.aacti[i]+=a
   pass
  pass  
 pass
 def fSetChilds(self) :
  '''generate auxiliary index list of childs
     observed rtyp values:
     [5.5, 1.0, 2.0, 3.0, 4.0, 5.0, 1.5, 7.0, 1.1, 1.55, 2.77, 2.4, 2.7, 2.6, 7.7, 1.555, 1.4, 6.0, 1.5555]
     use lisotope.fGetLrtyp0() to get this list
     '''
  for rtyp in self.lrtyp :
   t = (0,0,0)
   if rtyp[0] == 1.0 :
    t = (self.z+1,self.a,int(rtyp[1]))
   if rtyp[0] == 2.0 :
    t = (self.z-1,self.a,int(rtyp[1]))
   if rtyp[0] == 3.0 :
    t = (self.z,self.a,int(rtyp[1]))
   if rtyp[0] == 4.0 :
    t = (self.z-2,self.a-4,int(rtyp[1]))
   if rtyp[0] == 5.0 :
    t = (self.z,self.a-1,int(rtyp[1]))
   if rtyp[0] == 6.0 :
    t = (0,0,0)
   if rtyp[0] == 7.0 :
    t = (self.z-1,self.a-1,int(rtyp[1]))
   if rtyp[0] >= 10.0 :
    t = (0,0,0)
   if rtyp[0] == 1.1 :
    t = (self.z+2,self.a,int(rtyp[1]))
   if rtyp[0] == 1.4 :
    t = (self.z-1,self.a-4,int(rtyp[1]))
   if rtyp[0] == 1.5 :
    t = (self.z+1,self.a-1,int(rtyp[1]))
   if rtyp[0] == 1.55 :
    t = (self.z+1,self.a-2,int(rtyp[1]))
   if rtyp[0] == 1.555 :
    t = (self.z+1,self.a-3,int(rtyp[1]))
   if rtyp[0] == 1.5555 :
    t = (self.z+1,self.a-4,int(rtyp[1]))   
   if rtyp[0] == 1.6 :
    t = (self.z-1,self.a-4,int(rtyp[1]))
   if rtyp[0] == 2.4 :
    t = (self.z-3,self.a-4,int(rtyp[1]))
   if rtyp[0] == 2.6 :
    t = (0,0,0)
   if rtyp[0] == 2.7 :
    t = (self.z-2,self.a-1,int(rtyp[1]))
   if rtyp[0] == 2.77 :
    t = (self.z-3,self.a-2,int(rtyp[1]))
   if rtyp[0] == 5.5 :
    t = (self.z-2,self.a-2,int(rtyp[1]))
   if rtyp[0] == 7.7 :
    t = (self.z-2,self.a-2,int(rtyp[1]))
   self.lchild.append(t)
  pass 
 pass
 def fGetLrtyp0(self) :
  '''return list of rtyp 
     generated from the list of tuples 
     (rtyp,rfs,q,br) 

     it is not used directly by the code,
     it is just called from lisotope.fGetLrtyp0()
     and the output was used to setup isotope.fSetChilds()
     function

     check for changes when ENDF is updated
  '''
  l=[] 
  for rtyp in self.lrtyp :
    l.append(rtyp[0])
  pass
  return l
 pass  
pass
#******************************************
class lisotope :
 '''lisotope class --- list of isotope classes'''  
 def __init__(self) :
  self.l = []   # list of isotope classes
  self.lza = [] # auxiliary list of (z,a,liso) tuples
  self.lt = []  # list of times for activities
  self.lg = [] # lists of indexes of MELCOR element groups for each isotope class
  self.llpower = [] # list of lists of element specific powers, one list per melcor element 
  self.lpower = [] # total power
  #
  self.llgamma = None
 pass
 def fAddSpectraPickle(self,sfn="spectra.pickle",speci=None) :
  if speci==None :
   spec=spectra()
   spec.fLoadPickle(sfn)
  else :
   spec=speci
  pass
  for lspectrum,cisot in zip(spec.llspectrum,self.l):
   cisot.lspectrum=lspectrum
  pass
  print("Spectra added to isotopes data")
 pass
 def fGammaSet(self):
  self.llgamma=[]
  emin=10000.0   # 10keV
  xminmax=5000.0 # discard lines with intensity xminmax times less than maximum
  for i in range(len(self.lt)) :
   xmax=0.0
   lgamma1 = []
   for ciso in self.l :
    if ciso.aacti[i] > 0.0 :
     for spectrum in ciso.lspectrum :
      if spectrum.styp==0.0 :
       for sd in spectrum.lsd :
        x = ciso.aacti[i]*sd.ri*spectrum.fd
        if x>xmax : xmax=x
        if sd.er > emin :
         tline = ( sd.er/1000.0 , x , ciso.z, ciso.a, ciso.liso)
         lgamma1.append(tline)
        pass
       pass
      pass
     pass
    pass
   pass
   xmin=xmax/xminmax
   lgamma2 = []
   for tline in lgamma1 :
    if tline[1]>xmin : 
     lgamma2.append((tline[0],tline[1]/xmax,tline[2],tline[3],tline[4]))
    pass
   pass
   lgamma1 = sorted(lgamma2, key=lambda tup: tup[0])  
   self.llgamma.append(lgamma1)
  pass
 pass
 def fGammaPrint(self,sfn="gamma.txt") :
  global gcel
  f=open(sfn,"w")
  for time,lgamma in zip(self.lt,self.llgamma) :
   f.write("********************************\n")
   f.write("Time = %g s (%g d) \n" % ( time,time/(24*3600.0)))
   f.write("* E [keV]    y [1]        Isot *\n")
   for tline in lgamma :
    f.write("%e %e %s \n" % (tline[0],tline[1], gcel.fGetOrigenName((tline[2],tline[3],tline[4]))))
   pass
  pass
  f.write("********************************\n")
  f.close()
 pass
 def fGetLrtyp0(self) :
  '''return list of rtyp 
     generated from the list of tuples 
     (rtyp,rfs,q,br) 
     ouput is used to code isotope.fSetChilds() function
  '''
  l=[]
  for ci in self.l :
   l+=ci.fGetLrtyp0()
  pass
  l=list(set(l))
  return l
 pass  
 def fPrintMelInc(self,sfn) :
  '''MELCOR 1.8.6
     output of elements powers 
     for DCH input 
     to the file sfn
  '''
  global gcel
  itf=999
#pv121218  nmaxchar=79
  nmaxchar=70
  fo=open(sfn,"a+")
  for iel,lpower in enumerate(self.llpower):
   iout=0
   nchar=2*nmaxchar
   for xt,p in zip(self.lt,lpower):
    sn = fMelFltStr(xt,p)
    nsn = len (sn)
    if nchar+nsn > nmaxchar :
     if iout>0 :
      fo.write("%s\n" % s)
     pass  
     iout+=1 
     s="dchnem%02d%02d" % (iel,iout)
    pass  
    s=s+sn
    nchar=len(s)
   pass
   fo.write("%s\n" % (s))  
  pass
  iout=0
  fo.write("dchdecpow  tf-%03d\n" % (itf))
  fo.write("tf%03d%02d total-power %d 1.0 0.0\n" % (itf,iout,len(self.lt)))
  nchar=2*nmaxchar
  s=""
  iout=10
  for xt,p in zip(self.lt,self.lpower):
   sn = fMelFltStr(xt,p)
   nsn = len (sn)
   if nchar+nsn > nmaxchar :
    if iout>10 : fo.write("%s\n" % s)
    iout+=1
    s="tf%03d%02d" % (itf,iout)
   pass
   s=s+sn
   nchar=len(s)   
  pass  
  fo.write("%s\n" % (s))  
  fo.write("**Obligatory Compounds**\n")
  inext=len(gcel.lelmel)
  for dummy,ldumcomp in zip(gcel.ldummy,gcel.lldumycomp) :
   inext+=1
   fo.write("dchnem%02d%02d %s %e\n" % (inext,0,dummy,1.0e-9))
   xnorm=0.0
   lpower=scipy.zeros(len(self.llpower[0]))
   for dumcomp in ldumcomp :
    xnorm+=dumcomp[1]*dumcomp[2]
    i=gcel.lelmel.index(dumcomp[0])
    lpower+=dumcomp[1]*dumcomp[2]*scipy.array(self.llpower[i])
   pass
   lpower=lpower/xnorm
   iout=0
   iel=inext
   nchar=2*nmaxchar
   for xt,p in zip(self.lt,lpower):
    sn = fMelFltStr(xt,p)
    nsn = len (sn)
    if nchar+nsn > nmaxchar :
     if iout>0 :
      fo.write("%s\n" % s)
     pass  
     iout+=1 
     s="dchnem%02d%02d" % (iel,iout)
    pass  
    s=s+sn
    nchar=len(s)
   pass
   fo.write("%s\n" % (s))  
  pass
  fo.write("%s\n" % ("."))  
  fo.close()   
 pass
 #
 def fAdd(self,ci) :
  '''add new isotope to the list'''
  self.l.append(ci)
 pass
 def fPrint(self) :
  '''debug print '''
  for ci in self.l : ci.fPrint()
 pass
 def fPrintAct(self,lpa,sfn="activity.txt") :
  '''print out of activities of selected 
     isotopes into column formated ascii file
  '''
  global gcel 
  laa = []
  for pa in lpa:
    iz = gcel.fGetZ(pa)
    ia,isom = gcel.fGetA(pa)
    t = (iz,ia,isom)
    i = self.fIndex(t)
    if i>=0 :
      l = self.l[i].aacti.tolist()
      laa.append(l)
    else :
      print("Isotope for output not found: %s" % (pa))
    pass
  pass  
  f=open(sfn,"w") 
  for i in range(len(self.lt)):
   f.write("%e" % (self.lt[i]))
   for aa in laa:
     f.write(" %e" % (float(aa[i])))
   pass  
   f.write("\n")  
  pass
  f.close()
 pass
 #
 def fPrintActCsv(self,lpa,sfn1) :
  '''print out of activities of selected 
     isotopes into a csv file for Nucleonica, in Bq
  '''
  global gcel 
  xmin=1.0e-20
  for i in range(len(self.lt)) :
   sfn = "%s%04d.csv" % (sfn1,i)
   f=open(sfn,"w") 
   f.write("Nuclide,  Activity (Bq)\n")
   for pa in lpa:
    iz = gcel.fGetZ(pa)
    ia,isom = gcel.fGetA(pa)
    t = (iz,ia,isom)
    j = self.fIndex(t)
    if j>=0 :
      x=self.l[j].aacti[i]
      if x>xmin :
       spa=pa[:1].upper() + pa[1:]
       f.write("%s, %e\n" % (spa,x))
      pass
    else :
      print("Isotope for output not found: %s" % (pa))
    pass    
   pass 
   f.close()
  pass
 pass  
 #
 def fPrintActInp(self,lpa,sfn1) :
  '''print out of activities of selected 
     isotopes into origen like output, in Bq
  '''
  global gcel
  xmin=1.0e-20 
  for i in range(len(self.lt)) :
   sfn = "%s%04d.txt" % (sfn1,i)
   f=open(sfn,"w") 
   for pa in lpa:
    iz = gcel.fGetZ(pa)
    ia,isom = gcel.fGetA(pa)
    t = (iz,ia,isom)
    j = self.fIndex(t)
    if j>=0 :
      x=self.l[j].aacti[i]
      if x>xmin :
       f.write("%s %e\n" % (pa,x))
      pass
    else :
      print("Isotope for output not found: %s" % (pa))
    pass    
   pass 
   f.close()
  pass
 pass  
 #
 def fGetChainInfo(self,s) :
  '''print out decay chain information for isotopes
     input s (string) is a space separated list of isotope names
  '''
  for ss in s.split() :
   self.fGetChainInfo1(ss)
  pass
 pass
 #
 def fGetChainInfo1(self,ss,n=0) :
  '''print out decay chain information for isotope 
     input ss (string) is an isotope name
           n  (integer) should be 0 for parent isotope
                        it is then >0 in recursive calls
                        for childs 
  '''
  global gcel
  nn=n
  if n>1000 :
   return 1
  pass
  t = gcel.fGetZAI(ss)
  i = self.fIndex(t)
  if i<0 : 
   print(ss,t,"Not found")
  else :
   print(ss, t)
   if len(self.l[i].lrtyp)!=len(self.l[i].lchild):
    self.fSetChilds()
   pass
   pass
   for rtyp,child in zip(self.l[i].lrtyp,self.l[i].lchild) :
    print(gcel.fGetOrigenName(child), child, rtyp)
    n+=1
   pass
   for child in self.l[i].lchild :
    ii = self.fIndex(child)
    if ii>=0 :
     self.fGetChainInfo1(gcel.fGetOrigenName(child),n)
    pass
   pass
   if nn==0:
    print("Decay matrix for :", t)
    lch=self.fGetChain(t)
    print(lch)
    print(self.fGetDecayMatrix(lch))
   pass
  pass
  return 0
 pass
 #
 def fCheckBpBmConflict(self) :
  '''not used any more'''
  global gcel
  for ci in self.l: 
   lBetap = []
   lBetam = []
   for i,rtyp in enumerate(ci.lrtyp) :
    if rtyp[0]>=1.0 and rtyp[0]<2.0 : lBetam.append(i)
    if rtyp[0]>=2.0 and rtyp[0]<3.0 : lBetap.append(i)
   pass
   if len(lBetam)>0 and len(lBetap)>0 :
    t=ci.z,ci.a,ci.liso
    print("Beta +- conflict", gcel.fGetOrigenName(t), t)
    xBetap=0.0
    xBetam=0.0
    for i in lBetam : xBetam+=ci.lrtyp[i][3]
    for i in lBetap : xBetap+=ci.lrtyp[i][3]
    if xBetam>=xBetap :
     pass
    pass
   pass 
  pass
 pass
 #
 def fPrintPower(self,sfn="power.txt") :
  '''print out of class specific powers (in W/kg)
     and total core power (in W for the whole core)
     into column formated ascii file     
  '''
  f=open(sfn,"w")
  for i,xtime in enumerate(self.lt) :
   f.write("%e" % (float(xtime)))
   for j in range(len(self.llpower)):
    f.write(" %g" % (self.llpower[j][i]))
   pass
   f.write(" %g" % (self.lpower[i]))
   f.write("\n")  
  pass
  f.close()
 pass
 #
 def fPrintTotalPower(self,sfn="powertot.txt",sunit="s") :
  '''print out total core power (in W for the whole core)
     into column formated ascii file     
  '''
  xk = 1.0 # time scale constant, xk=1.0 for seconds
  if sunit == "m" :
   xk = 60.0
  elif sunit == "h" :
   xk = 3600.0
  elif sunit == "d" :
   xk = 3600.0*24.0
  elif sunit == "y" :
   xk = 3600.0*24.0*365.2425
  pass
  f=open(sfn,"w")
  for i,xtime in enumerate(self.lt) :
   f.write("%g %g\n" % (float(xtime)/xk, self.lpower[i]))
  pass
  f.close()
 pass   
 #
 def fReadENDF(self,sdir) :
  '''reads the initial database the ENDF data files
     all data file should be located in the directory
     sdir
  '''
  lf=os.listdir(sdir)
  i=0
  j=0
  for sfn in lf :
   if sfn[0]=="." : continue # avoid failure due to hidden files
   ci = isotope()
   ci.fReadENDF(sdir+"/"+sfn)
   if ci.t12==0.0 :
    j+=1
    sys.stdout.write("x") # zero half time - discarded isotope
   else :
    sys.stdout.write(".") # included radioactive isotope
    self.fAdd(ci)
    i+=1
   sys.stdout.flush()
  pass
  sys.stdout.write("\n%4d endf files read\n" % (i+j))
  sys.stdout.write("%4d radioactive isotopes stored\n" % (i))
  sys.stdout.write("%4d stable isotopes discarded\n" % (j))
  sys.stdout.flush()
 pass
 #
 def fSavePickle(self,sfn="endf.pickle") :
  '''save the database to a pickle file
  '''
  spec=spectra()
  for cisot in self.l :
   za = (cisot.z,cisot.a,cisot.liso)
   spec.lza.append(za)
   spec.llspectrum.append(cisot.lspectrum)
   cisot.lspectrum=[] 
  pass 
  spec.fSavePickle()
  f=open(sfn,'w')
  pickle.dump(self.l,f)
  f.close()
  print(sfn, "written")
 pass
 #
 def fLoadPickle(self,sfn="endf.pickle",bVerbose=True,bMove=True) :
  '''load the database from the pickle file'''
  #15.04.2015 python3 #f=open(sfn,'r')
  f=open(sfn,'rb')
  self.l=pickle.load(f)
  f.close()
  self.fUpdateLZA()
  #self.fSetupMELCORelgr(bVerbose,bMove)
 pass
 #
 def fUpdateLZA(self) :
  '''update auxiliary lza index'''
  self.lza=[]
  for ci in self.l :
   t = (ci.z,ci.a,ci.liso)
   self.lza.append(t)
  pass
 pass
 #
 def fIndex(self,t) :
  '''get index of the isotope
     auxiliary index lza is
     updated if necessary
  '''
  if len (self.lza)==0 :
   self.fUpdateLZA()
  pass
  if len (self.lza)==0 :
   return -1
  pass
  try :
   i = self.lza.index(t)
  except :
   i = -1
  pass
  return i 
 pass
 #
 def fInitializeforDecay(self) :
  '''create array of zeros to store activities of 
     the isotopes in the decay chain
  '''
  nt = len(self.lt)
  for ci in self.l :
   ci.aacti = scipy.zeros([nt]) 
  pass
 pass
 #
 def fResetActi(self,i) :
  '''sets initial activity to activity at decay time i 
     and delete the decay table
  '''
  for ci in self.l :
   ci.acti = ci.aacti[i]
   ci.aacti=None
  pass
 pass
 #
 def fSetChilds(self) :
  '''generate auxiliary index list of childs'''
  for ci in self.l:
   ci.fSetChilds() 
  pass
 pass
 #
 def fDecay(self,bChain=True,bVerbose=False) :
  '''calculate activities for input times'''
  bChainEncountered=False
  if bVerbose : print("Calculation of decay chains ...")
  for ci,t in zip(self.l,self.lza) :
   if ci.acti>0.0:
    if bChain : 
     lch = self.fGetChain(t)
     if len(lch)<2 :
      ci.fDecay(self.lt)
     else:
      self.fDecayChain(lch,bVerbose) 
      bChainEncountered=True
     pass
    else :
     ci.fDecay(self.lt)
    pass 
   pass
  pass  
  if bChainEncountered and bVerbose : sys.stdout.write("\n")
 pass
 #
 def fGetDecayMatrix(self,lch) :
  '''set up decay matrix '''
  global ln12,dtmin 
  n = len(lch)
  em = scipy.zeros([n,n])
  lami = scipy.zeros([n])
  for i in range(n):
   j=self.lza.index(lch[i])
   lam = ln12/self.l[j].t12
   em[i][i]=-1.0*lam
   lami[i]=lam
   for k in range(len(self.l[j].lchild)):
    try : 
     m = lch.index(self.l[j].lchild[k])
    except:
     m=-1
    pass
    if m>=0 :
     em[m][i]=lam*self.l[j].lrtyp[k][3]
    pass 
   pass  
  pass
  return em,lami
 pass 
 pass
 #
 def fDecayChain(self,lch,bVerbose=False):
  '''calculate decay chain using matrix exponential'''
  global ln12,dtmin 
  global gcel
  if bVerbose: 
   sel=gcel.fGetOrigenName(lch[0])
   sys.stdout.write("%s %d" % (sel,len(lch)))
   sys.stdout.flush()
  pass
  n = len(lch)
  em,lami=self.fGetDecayMatrix(lch)
  j=self.fIndex(lch[0])
  aa = scipy.zeros([n])
  aa[0]=self.l[j].acti/float(lami[0])
  ab = scipy.mat(scipy.zeros([n]))
  ab = scipy.zeros([n])
  aa = scipy.mat(aa).transpose()
  self.l[j].aacti[0]=self.l[j].acti
  for i in range(1,len(self.lt)) :
   dt = self.lt[i]-self.lt[i-1]
   if dt > dtmin :
    emt=em*dt
    eemx = scipy.mat((scipy.linalg.expm(emt)))
    ab=eemx*aa
   else:
    ab=aa 
   pass 
   for j in range(n):
    k=self.lza.index(lch[j])
    x=float(ab[j,0])*float(lami[j])
    self.l[k].aacti[i]+=x
   pass
   aa=ab
  pass
  if bVerbose: 
   sys.stdout.write("|")
  pass
 pass
 #
 def fGetChain(self,t) :
  '''set up decay chain '''
  global gcel
  # avoid recursive infinite decay chain ?
  # check if it is still needed
  lInfi=[
   (36, 100, 0), # Kr100  
   (37, 100, 0), # Rb100  
   (38, 100, 0), # Sr100  
   (39, 100, 0), # Y100   
   (39, 100, 1), # Y100M  
   (40, 100, 0), # Zr100  
   (41, 100, 0), # Nb100  
   (41, 100, 1), # Nb100M 
   (42, 100, 0), # Mo100  
   (43, 100, 0), # Tc100  
   (43, 116, 0), # Tc116  
   (44, 116, 0), # Ru116  
   (45, 116, 0), # Rh116  
   (45, 116, 1), # Rh116M 
   (46, 116, 0), # Pd116  
   (47, 116, 0), # Ag116  
   (47, 116, 1), # Ag116M 
   (47, 116, 2), # Ag116M 
   (47, 128, 0), # Ag128  
   (48, 116, 0), # Cd116  
   (48, 128, 0), # Cd128  
   (49, 116, 0), # In116  
   (49, 128, 0), # In128  
   (49, 128, 1), # In128M 
   (50, 128, 0), # Sn128  
   (50, 128, 1), # Sn128M 
   (51, 128, 0), # Sb128  
   (51, 128, 1), # Sb128M 
   (52, 128, 0), # Te128  
   (53, 128, 0)  # I128   
  ]
  ichmaxlen=10000
  k=0
  lch=[]
  lchn=[t]
  lchnn=[]
  while len(lchn)>0 and len(lch)<ichmaxlen:
   for tt in lchn:
    try :
     k=lInfi.index(tt)
    except:
     k=-1
    pass
    if k>=0 : ichmaxlen=100
    j=self.lza.index(tt)
    for ttt in self.l[j].lchild:
     i=self.fIndex(ttt) 
     if i>=0 :
      if self.l[i].t12>0.0 :
       lchnn.append(ttt)
    pass  
    lch.append(tt)  
    if len(lch)>=ichmaxlen and ichmaxlen>100 :
     print("Decay chain truncated:", gcel.fGetOrigenName(t),t)
     break
    pass
   pass
   lchn=[]
   for ttt in lchnn :
    lchn.append(ttt) 
   pass
   lchnn=[]
  pass
  return lch
 pass
 #
 def fSetupMELCORelgr(self,bVerbose=True,bMove=True) :
  '''
     set up MELCOR elements groups to calculate power
  '''
  global gcel
  if len(self.lza)==0:
   self.fUpdateLZA()
  pass 
  iu=gcel.lelmel.index("U")
  self.lg = []
  self.llpower = []
  # lists of specific powers
  for iz in gcel.lelmelz :
   l=[]
   self.llpower.append(l)
  pass
  # list of melcor elements for each isotope
  if bVerbose :
   print("Isotopes moved to another element:")
  pass
  for i,ci in enumerate(self.l) :
   try :
    j=gcel.lelmelz.index(ci.z)
   except :
    j=iu
   pass
   if bMove :
    try:
     k=gcel.lmovei.index(self.lza[i])
    except:
     k=-1
    pass
    if k>=0 :
     try : 
      jj=gcel.lelmel.index(gcel.lmove[k][1])
     except : 
      jj=-1
     pass
     if jj>=0 :
      if bVerbose : print(gcel.lmove[k],": ",j,gcel.lelmel[j]," -> ",jj,gcel.lelmel[jj])
      j=jj
     pass 
    pass               
   pass
   self.lg.append(j)
  pass
 pass
 #
 def fScale(self,xk) :
  '''
     Scale calculated activities by factor xk
     xk is the ratio of core mass to irradiated mass
  '''
  for ci in self.l :
   ci.aacti = xk * ci.aacti
  pass
 pass
 def fPower(self, elmass) :
  '''calculate specific power of elements and total power of the core
     elmass is element class -- masses in the core 
     (converted already in config.fReadMasses())
     activities are in Bq in the core 
     (scaled by fScale)
  '''
  global gcel
  global xeVJ
  n = len(self.lt)
  self.lpower=scipy.zeros([n])
  for i in range(len(self.llpower)) :
   self.llpower[i]=scipy.zeros([n])
  for ci,gi in zip(self.l,self.lg) : # ci is isotope, gi is melcor element index for this isotope
   iz = gcel.lelmelz[gi] # iz is Z of MELCOR element group gi, ci belongs to group gi
   ed = xeVJ * ci.fEnergy()  
   for i in range(n) : # loop over all time points
    p =  ed * float(ci.aacti[i])   
    if  elmass[iz-1]>0.0 : self.llpower[gi][i]+=p/elmass[iz-1] # in W/(1kg of FP el), H with iz=1 has index 0!
    self.lpower[i]+=p                                          # in W in whole core
   pass
  pass
 pass
 #
 def fSetActivities(self,lcacti) :
  '''set activities from ORIGEN output'''
  lig=[] 
  for cacti in lcacti.l :
   t = (cacti.z,cacti.a,cacti.isomer)
   i = self.fIndex(t)
   if i >=0 :
    self.l[i].acti = cacti.x
   else :
    lig.append(cacti.abr) 
   pass
  pass
  return lig 
 pass
pass
#end of lisotope class
#******************************************
class llisotope :
 '''llisotope class --- list of lisotope classes'''
 def __init__(self) :
  self.l=[] 
 pass
 def fSum(self) :
  '''create new lisotope instance and
     calculate sum of activities for each isotope
  '''
  cli = lisotope()
  cli.fLoadPickle(bVerbose=True)
  for i in range(len(cli.l)) :
   for clii in self.l :
    cli.l[i].acti+=clii.l[i].acti 
  return cli
 pass  
pass
#end of llisotope class
#******************************************
class config :
 '''reads the configuration file,
    does the calculation
 '''  
 def __init__(self,sconf="",spectra=None) :
  self.bChain=True
  #*input
  # mass of U in the core [kg]
  self.massucore = 0.0
  # mass of U in the origen mass input [kg] (usually 1000.0)
  self.massuorad = 0.0
  # mass 
  self.lmassfile = []
  self.lmassfrac = []
  # activity
  self.lactifile = [] # filename
  self.lactifrac = [] # fraction to take
  self.lactitime = [] # time of activity data
  self.lactiunit = [] # unit optional: Ci (default) Bq
  self.loutisot = [] # isotopes to output activity
  # time
  self.ltime = []
  #*output
  self.elmass = None
  #self.lacti = None
  self.lisot = None
  self.outpow = "power.txt"
  self.outact = "activity.txt"
  self.outactcsv = ""
  self.outactinp = ""
  self.outgam = ""
  self.outpowtot = ""
  self.outpowtottimeunit = "s"
  self.outinc = "decay.inc"
  self.spectra = spectra
  self.soutinvacti = "inventory-acti-bq.txt" # output file for activities in ORIGEN format but in Bq, fission and activation products summed
  self.soutinvmass = "inventory-mass-kg.txt" # output file for element masses in ORIGEN format (kg)
  self.bOutInv = False
  self.xMelVer = 1.86 # melcor version
  #read input file if specified
  if len(sconf)>0 :
   self.fReadConf(sconf)
   self.fCleanOutputs()
   self.fPrintConf()
   self.fDoIt()
  pass
 pass
 #
 def fPrintMel2Inc(self) :
  global gcel
  fo=open("dch-"+self.outinc,"w")
  fo.write("dch_dpw tf total-power \n")
  for iel,el in enumerate(gcel.lelmel):
   i=gcel.labr.index(el)
   em=self.elmass.mass[i]
   lp=self.lisot.llpower[iel]
   n=len(lp)
   fo.write("dch_el %s %f %d \n" % (el,em,n) )
   for i,(xt,xp) in enumerate(zip(self.lisot.lt,lp)) :
    fo.write("%5d %s \n" % (i+1,fMelFltStr(xt,xp)))
   pass   
  pass
  fo.close()
  fo=open("tf-"+self.outinc,"w")
  fo.write("tf_id total-power 1.0 0.0\n")
  fo.write("tf_tab %d \n" % (len(self.lisot.lt)) )
  for i,(xt,p) in enumerate(zip(self.lisot.lt,self.lisot.lpower)):
   sn = fMelFltStr(xt,p)
   fo.write("%5d %s \n" % (i+1,sn) )
  pass 
  fo.close()
 pass
 #
 def fDoIt(self) :
  if len(self.lactifile)>0:
   self.fReadActivities()
   self.lisot.fDecay(self.bChain,bVerbose=True)
   if len(self.lmassfile)>0:
    #
    self.lisot.fSetupMELCORelgr()
    self.fReadMasses()
    self.lisot.fScale(self.massucore/self.massuorad)
    self.lisot.fPower(self.elmass.mass)
    if len(self.outpow)>0 : self.lisot.fPrintPower(self.outpow)
    if len(self.outpowtot)>0 : self.lisot.fPrintTotalPower(self.outpowtot,self.outpowtottimeunit)
    if len(self.outinc) > 0 :
     if self.xMelVer<2.0 :
      self.elmass.fPrintMelInc(self.outinc)
      self.lisot.fPrintMelInc(self.outinc)
     else :
      self.fPrintMel2Inc()
     pass 
    pass
   pass 
   if len(self.outact)>0 : self.lisot.fPrintAct(self.loutisot,self.outact)
   if len(self.outactinp)>0 : self.lisot.fPrintActInp(self.loutisot,self.outactinp)
   if len(self.outactcsv)>0 : self.lisot.fPrintActCsv(self.loutisot,self.outactcsv)
   if len(self.outgam)>0 : 
    self.lisot.fAddSpectraPickle(speci=self.spectra)
    self.lisot.fGammaSet()
    self.lisot.fGammaPrint(sfn=self.outgam)
   pass
   if self.bOutInv : self.fOutInv() 
  pass
 pass
 #
 def fOutInv(self) :
  '''output inventory in ORIGEN format'''
  global gcel
  print(("Writing inventory of activities in Bq to %s ..." % (self.soutinvacti) ))
  print(("Reference time is: %g s (=%g hours) (=%g days)" % (self.ltime[0],self.ltime[0]/3600.0,self.ltime[0]/(3600.0*24.0)) ))  
  f = open(self.soutinvacti,'w')
  for l in self.lisot.l :
   if l.aacti[0]>0.0 :
    s = gcel.fGetOrigenName( (l.z,l.a,l.liso) )
    f.write("%7s %g\n" % (s, l.aacti[0]) )
   pass
  pass
  f.close()
  print(("Writing initial inventory of element mass in kg to %s ..." % (self.soutinvmass)))
  self.elmass.fPrintORIGENFormat(self.soutinvmass)
 pass 
 #
 def fReadConf(self,sconf) :
  '''reads the configuration file'''
  bMass = False
  bActi = False
  bTime = False
  bOutA = False
  bOutI = False
  f=open(sconf,'r')
  for line in f :
   s=line.strip() #.lower()
   if len(s)==0 : continue
   if s[0]=="#" : continue
   ss = s.split()
   if ss[0]=="end" :
     bMass=False 
     bActi=False 
     bTime=False
     bOutA = False
     bOutI = False
     continue
   pass
   if bMass :
    self.lmassfile.append(ss[0])
    self.lmassfrac.append(float(ss[1]))    
   pass
   if bActi :
    self.lactifile.append(ss[0])
    self.lactifrac.append(float(ss[1]))
    self.lactitime.append(float(ss[2]))
    sunit = "Ci"
    if len(ss) > 3 :
     if ss[3]=="Bq" : sunit=ss[3]
    pass
    self.lactiunit.append(sunit)
   pass
   if bTime :
    for sss in ss :
     if sss[0]=="#" : break
     # 14.10.2014 check the time is monotonous
     xt=float(sss)
     nt = len(self.ltime)
     if nt>0 :  
      if xt>self.ltime[-1]:
       self.ltime.append(xt)
      else :
       print(" time is not monotonous %g > %s : " % (self.ltime[-1],sss))
       print(" check time input ")
       print(" exiting ")
       sys.exit(0)
      pass
     else :
      self.ltime.append(xt)
     pass
    pass
    continue
   pass
   if bOutA :
    for sss in ss :
     if sss[0]=="#" : break
     self.loutisot.append(sss)
    pass
    continue
   pass
   if bOutI :
    if ss[0]=="soutinvacti" :
     self.soutinvacti = ss[1].strip('\"')
     continue
    pass
    if ss[0]=="soutinvmass" :
     self.soutinvmass = ss[1].strip('\"')
     continue
    pass
    if ss[0]=="bOutInv" :
     self.bOutInv = bool(ss[1])
     continue
    pass
   pass
   if ss[0]=="massucore" :
    self.massucore = float(ss[1])
    continue
   pass
   if ss[0]=="massuorad" :
    self.massuorad = float(ss[1])
    continue
   pass
   if ss[0]=="outpow" :
    self.outpow = ss[1].strip('\"')
    continue
   pass
   if ss[0]=="outact" :
    self.outact = ss[1].strip('\"')
    continue
   pass
   if ss[0]=="outgam" :
    self.outgam = ss[1].strip('\"')
    continue
   pass
   if ss[0]=="outpowtot" :
    self.outpowtot = ss[1].strip('\"')
    if len(ss)>2 : self.outpowtottimeunit = ss[2].strip('\"')
    continue
   pass
   if ss[0]=="outinc" :
    self.outinc = ss[1].strip('\"')
    continue
   pass
   if ss[0]=="outactinp" :
    self.outactinp = ss[1].strip('\"')
    continue
   pass
   if ss[0]=="outactcsv" :
    self.outactcsv = ss[1].strip('\"')
    continue
   pass
   if ss[0].lower()=="xmelver" :
    self.xMelVer = float(ss[1])
    continue
   pass  
   if ss[0]=="begin" :
    bMass =  (ss[1]=="mass")
    bActi =  (ss[1]=="activity")
    bTime =  (ss[1]=="time")
    bOutA =  (ss[1]=="outisot")
    bOutI =  (ss[1]=="outinv")
    continue
   pass
  pass
 pass
 def fCleanOutputs(self) :
  # clean up of impossible output file names
  if len(self.loutisot)==0: 
   self.outact=""
   self.outactinp=""
  pass
  if len(self.lmassfile)==0: 
   self.outinc=""
   self.outpow=""
   self.outpowtot=""
  pass
 pass
 def fPrintConf(self) :
  '''config check printout '''
  print("*Config check printout")
  print("Total mass of U                     : %f kg" % self.massucore)
  print("Mass of U for mass normalization    : %f kg" % self.massuorad)
  print("Input files for mass :")
  for smfile,xmfrac in zip(self.lmassfile,self.lmassfrac) :
   print("%s %f" % (smfile,xmfrac))  
  pass
  print("Input files for activity :")
  for safile,xafrac,xatime,sunit in zip(self.lactifile,self.lactifrac,self.lactitime,self.lactiunit) :
   print("%s %f %f %s" % (safile,xafrac,xatime,sunit))  
  pass
  print("Times specified for output :")
  print(self.ltime)
  print("Outputs requested:")
  if len(self.outinc) > 0 : print(" MELCOR DCH input %s for MELCOR %4.2f" % (self.outinc,self.xMelVer))
  if len(self.outact)>0 :  print(" Activities in columns: %s" % self.outact)
  if len(self.outactinp)>0 :  print(" Activities : %sxxxx.txt" % self.outactinp)
  if len(self.outgam)>0 : print(" Gamma lines: %s" % self.outgam)
  if len(self.outpow)>0 : print(" Power of MELCOR groups in colums: %s" % self.outpow)
  if len(self.outpowtot)>0 : print(" Total MELCOR power in colums: %s" % self.outpowtot)
  if self.bOutInv :
   print("Initial inventory output requested")
   print("         Activity in Bq: %s" %  (self.soutinvacti))
   print("         (sum of activity from fission and activation for each isotope with non zero activity)")
   print(("        Reference time is: %g s (=%g hours) (=%g days)" % (self.ltime[0],self.ltime[0]/3600.0,self.ltime[0]/(3600.0*24.0)) ))  
   print("         Mass in kg: %s" %  (self.soutinvmass))   
  pass 
  print("*End of confing printout")
 pass
 def fReadMasses(self) :
  '''read masses of elements
     input files should be in two column format:

     element mass 

     where element is element name and mass is element mass in the 
     irradiated sample in g

     output is in kg in the core or pool !

     Note: 
     If mass of uranium is zero or negative, then it is replaced by
     initial irradiated mass of uranium (massuorad converted to grams)
  '''
  global gcel    
  cselmass=elmass() # total mass --- init by zeros
  iu = gcel.labr.index("U")
  for sfn,xfrac in zip(self.lmassfile,self.lmassfrac) :
   celmass=elmass(sfn)  
   # if mass of uranium is zero or negative, then replace it by irradiated mass in grams 
   if celmass.mass[iu]<=0.0 : celmass.mass[iu]=1000.0*self.massuorad # kg->g
   cselmass.mass+=xfrac*celmass.mass # it is scipy array, so it works
  pass
  for i in range(len(cselmass.mass)) :
   if cselmass.mass[i]<0.0 : cselmass.mass[i]=0.0
   # cselmass.mass[i] is in g
  pass
  # cselmass.fPrint()
  # cselmass.mass is scipy array, input is in grams in the irradiated sample and the result is in kg in the core
  cselmass.mass=cselmass.mass*self.massucore/(self.massuorad*1000.0)
  self.elmass = cselmass
 pass
 def fReadActivities(self) :
  '''reads activities in the irradiated sample
     input files should be in two column format:

     isotope activity 

     where isotope is the isotope name and activity is the isotope activity 
     in the irradiated sample in Ci

     output is in Bq

  '''
  global xCiBq
  lig=[]
  cllisot=llisotope()
  for sfn,xfrac,xtime,sunit in zip(self.lactifile,self.lactifrac,self.lactitime,self.lactiunit) :
   clacti=lactivity()
   clacti.fRead(sfn)
   if sunit=="Ci" :
    x = xfrac*xCiBq
   elif sunit=="Bq" :
    x = xfrac
   else :
    print("Wrong unit for activity input")
    print("File: ", sfn)
    print("Unit: ", sunit)
    sys.exit(0)
   pass
   clacti.fMultiplyActi(x)
   clisot=lisotope()
   clisot.fLoadPickle(bVerbose=False)
   clisot.lt = [xtime, self.ltime[0]]
   clisot.fInitializeforDecay()
   clisot.fSetChilds()
   lig+=clisot.fSetActivities(clacti) 
   clisot.fDecay(self.bChain,bVerbose=False)
   clisot.fResetActi(-1)
   cllisot.l.append(clisot)  
  pass
  clisot=cllisot.fSum()
  clisot.lt=self.ltime
  clisot.fSetChilds()
  clisot.fInitializeforDecay()
  self.lisot=clisot
  if len(lig)>0:
   print("Following isotopes were not found in the ENDF database:")
   #150513 print(string.join(sorted(set(lig))," "))
   print( " ".join( sorted(set(lig))) )
  pass  
 pass
pass
# end of config class

class ConvMass :
 '''auxiliary class for
    conversion of ORIGEN outputs to different irradiation mass    

    input: 
     sdirii  - directory with input files 
     muinp   - mass of uranium for irradiated sample in the input directory
     sdirio  - output directory
     muout   - mass of uranium for irradiated sample in the output directory
     suff    - suffix of data files, default ".txt"
     bDoIt   - do the conversin on class initiation, default True

    fConvMass does the conversion

 '''  
 def __init__(self,sdirii,muinp,sdirio,muout,suff  = ".txt", bDoIt=True) :
  # input data
  self.sdirii=sdirii
  self.muinp =muinp 
  self.sdirio=sdirio 
  self.muout =muout 
  self.suff  =suff
  # internal data
  self.sfo = "%-8s %6.3e\n"   # output format
  self.lst = []
  self.ll  = []
  # do it immediately if no changes necessary
  if bDoIt : self.fConvMass()
 pass
 def fReadFile(self,sf) :
  l1=[]
  l2=[]
  f = open(sf,"r")
  for line in f :
   s = line.split()
   if len(s)>1 :
    l1.append(s[0])
    l2.append(float(s[1]))
   pass
  pass 
  f.close()
  self.ll =  (l1,l2)
 pass
 def fWriteFile(self,sf) :
  f = open(sf,"w")
  for s,x in zip(self.ll[0],self.ll[1]) :
   if x>0.0 : f.write(self.sfo % (s,x))
  pass
  f.close()
 pass
 def fConvData(self) :
  n = len(self.ll[0])
  for ie in range(n) :
   self.ll[1][ie]=self.ll[1][ie]*self.muout/self.muinp
  pass
 pass
 def fConvDir(self) :
  for sf in self.lsf :
   print("Converting file " + sf)
   self.fReadFile(os.path.join(self.sdirii,sf))
   self.fConvData() 
   self.fWriteFile(os.path.join(self.sdirio,sf))
  pass
 pass
 def fGetFiles(self) :
  self.lsf = [ f for f in os.listdir(self.sdirii) if os.path.isfile(os.path.join(self.sdirii,f)) and f[-4:]==self.suff ]
 pass
 def fConvMass(self):
  '''do the mass conversion'''
  self.fGetFiles() # get files in the input directory
  if not os.path.exists(self.sdirio) : os.mkdir(self.sdirio)
  self.fConvDir()
 pass
pass
# end of ConvMass

#global elemens instance
gcel=elements()
#constants
xCiBq = 3.7e+10        # Ci to Bq conversion factor
xeVJ = 1.602176565e-19 # eV to J  conversion factor
ln12 = math.log(2.0)   # natural logarithm of 2
dtmin = 1.0e-10        # minimum time difference to neglect decay

#print some information when run directly
if __name__ == "__main__":
 print("module endf.py")
 print(eval('__doc__'))
 sys.stdout.write("Implemented classes:")
 for obj in dir():
  if obj not in ['__builtins__', '__doc__','__file__','__name__','__package__',
                 'sys','string','scipy','pickle','os','math']:
   print("")
   print(obj, ":")
   print(eval(obj).__doc__) 
 pass
 print("")
pass

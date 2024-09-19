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
  14.09.2017 : package melendfmod instead if single endf.py file
               new location of data files in endf format: data-endf (on the same folder as melendfmod package)
               new location of data files in pickle format: data-pickle (on the same folder as melendfmod package)
               endf data are read only once 
               optionaly read directly from endf format data (should I avoid pickle auxiliary files at all?)
               tests folder (on the same folder as melendfmod package)
'''
#import additional modules
import sys
import melendfmod.aux as aux
import melendfmod.g as g
import melendfmod.elmass as elmass
import melendfmod.activity as activity
import melendfmod.isotope as isotope
#

class config(object) :
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
  fo=open("dch-"+self.outinc,"w")
  fo.write("dch_dpw tf total-power \n")
  for iel,el in enumerate(g.gcel.lelmel):
   i=g.gcel.labr.index(el)
   em=self.elmass.mass[i]
   lp=self.lisot.llpower[iel]
   n=len(lp)
   fo.write("dch_el %s %f %d \n" % (el,em,n) )
   for i,(xt,xp) in enumerate(zip(self.lisot.lt,lp)) :
    fo.write("%5d %s \n" % (i+1,aux.fMelFltStr(xt,xp)))
   pass   
  pass
  fo.close()
  fo=open("tf-"+self.outinc,"w")
  fo.write("tf_id total-power 1.0 0.0\n")
  fo.write("tf_tab %d \n" % (len(self.lisot.lt)) )
  for i,(xt,p) in enumerate(zip(self.lisot.lt,self.lisot.lpower)):
   sn = aux.fMelFltStr(xt,p)
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
    if g.bPickle :
     #when lisot was read directly from endf format spectra data are already there
     self.lisot.fAddSpectraPickle(speci=self.spectra)
    pass 
    self.lisot.fGammaSet()
    self.lisot.fGammaPrint(sfn=self.outgam)
   pass
   if self.bOutInv : self.fOutInv() 
  pass
 pass
 #
 def fOutInv(self) :
  '''output inventory in ORIGEN format'''
  print(("Writing inventory of activities in Bq to %s ..." % (self.soutinvacti) ))
  print(("Reference time is: %g s (=%g hours) (=%g days)" % (self.ltime[0],self.ltime[0]/3600.0,self.ltime[0]/(3600.0*24.0)) ))  
  f = open(self.soutinvacti,'w')
  for l in self.lisot.l :
   if l.aacti[0]>0.0 :
    s = g.gcel.fGetOrigenName( (l.z,l.a,l.liso) )
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
 #
 def fCleanOutputs(self) :
  ''' clean up of impossible output file names '''
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
 #
 def fPrintConf(self) :
  '''config check printout'''
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
 #
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
  cselmass=elmass.elmass() # total mass --- init by zeros
  iu = g.gcel.labr.index("U")
  for sfn,xfrac in zip(self.lmassfile,self.lmassfrac) :
   celmass=elmass.elmass(sfn)  
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
 #
 def fReadActivities(self) :
  '''reads activities in the irradiated sample
     input files should be in two column format:

     isotope activity 

     where isotope is the isotope name and activity is the isotope activity 
     in the irradiated sample in Ci

     output is in Bq

  '''
  lig=[]
  cllisot=isotope.llisotope()
  clisot1=isotope.lisotope()
  if g.bPickle:
   clisot1.fLoadPickle(bVerbose=False)
  else: 
   clisot1.fReadENDF()
   clisot1.fUpdateLZA()
  pass
  for sfn,xfrac,xtime,sunit in zip(self.lactifile,self.lactifrac,self.lactitime,self.lactiunit) :
   clacti=activity.lactivity()
   clacti.fRead(sfn)
   if sunit=="Ci" :
    x = xfrac*g.xCiBq
   elif sunit=="Bq" :
    x = xfrac
   else :
    print("Wrong unit for activity input")
    print("File: ", sfn)
    print("Unit: ", sunit)
    sys.exit(0)
   pass
   clacti.fMultiplyActi(x)
   #
   clisot=clisot1.fCopyENDFdata()
   clisot.lt = [xtime, self.ltime[0]]
   clisot.fInitializeforDecay()
   clisot.fSetChilds()
   lig+=clisot.fSetActivities(clacti) 
   clisot.fDecay(self.bChain,bVerbose=False)
   clisot.fResetActi(-1)
   cllisot.l.append(clisot)  
  pass
  clisot=cllisot.fSum(clisot1.fCopyENDFdata())
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


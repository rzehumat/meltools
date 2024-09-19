#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scipy
import melendfmod.g as g

class elmass(object) :
 '''class to store mass of elements
    it is stored in a scipy.array containing all
    elements from elements.labr 
 ''' 
 def __init__(self,sfn="") :
  self.mass = scipy.zeros([len(g.gcel.labr)])
  if len(sfn)>0 :
   self.fRead(sfn)
  pass 
 pass
 #
 def fRead(self,sfn,bVerbose=True):
  lig=[]
  lel=[]
  for el in g.gcel.labr :
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
  for el,xm in zip(g.gcel.labr,self.mass) :
   print(el,xm)
  pass 
 pass
 #
 def fPrintMelInc(self,sfn):
  '''print MELCOR 1.8.6 input data for masses of elements into 
     file sfn
  '''
  iout = 0
  fo=open(sfn,"w")
  for iel,el in enumerate(g.gcel.lelmel):
    i=g.gcel.labr.index(el) 
    me=self.mass[i]
    fo.write("dchnem%02d%02d %s %f\n" % (iel,iout,el,me))
  pass
  fo.close()
 pass
 #
 def fGetElMass(self,el) :
  i=g.gcel.labr.index(el) 
  me=self.mass[i]
  return me  
 pass
 #
 def fPrintORIGENFormat(self,sout) :
  '''print masses of elements to stdout'''
  f = open(sout,'w')
  for el,xm in zip(g.gcel.labr,self.mass) :
   if xm>0.0 :
    f.write("%3s %g\n" % (el,xm))
   pass 
  pass
  f.close()
 pass
pass
#end of elmass class

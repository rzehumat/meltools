#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle

class spectrum(object) :
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
 #
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
class spectrumd(object) :
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
class spectra(object) :
 '''Auxiliary class to store spectra in spectra.pickle'''
 def __init__(self) :
  self.lza = []
  self.llspectrum = [] # list of spectrums
 pass
 def fSavePickle(self,sfn) :
  '''save the database to a pickle file
  '''
  f=open(sfn,'wb')
  pickle.dump(self.lza,f)
  pickle.dump(self.llspectrum,f)
  f.close()
  print(sfn, "written")
 pass
 #
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

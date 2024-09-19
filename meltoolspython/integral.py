#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

def main() :
 lxint=[0.0]
 x0=None
 y0=None
 f=sys.stdin.readlines()
 for line in f :
  s = line.split()
  x = float(s[0])
  y = float(s[1])
  if x0 is not None :
   xay = (y+y0)/2.0
   xdx = x-x0
   lxint.append(xay*xdx) 
  pass
  print (x,sum(lxint))
  x0 = x
  y0 = y 
 pass
pass
#
if __name__ == "__main__":
 main()
pass


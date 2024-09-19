#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def fPrintDict(data):
 for item in data:
  print(item, ":",end="")
  if isinstance(data[item],dict):
   print()
   fPrintDict(data[item])
  else:
   print(data[item])
  pass
 pass
pass

def fWrite(sf='example.json',data=None):
 with open(sf, 'w') as f:
  json.dump(data, f)
 pass
pass

def fRead(sf='example.json'):
 with open(sf, 'r') as f:
  data = json.load(f)
 pass
 return data
pass

def fSomeDataManipulation(data):
 #print("data[\"inputs\"]")
 #print(data["inputs"])
 #print("data[\"inputs\"][\"integer_array\"]")
 #print(data["inputs"]["integer_array"])
 xd={}
 xd["number"]=10
 xd["descr"]="description of number on pydata"
 data["inputs"]["pydata"]=xd
 data["inputs"]["k"]=5
 data["pydatatoplevel"]=8
 #print("data")
 #print(data)
pass

def fMain():
 sf="example.json"
 data=fRead(sf)
 fSomeDataManipulation(data)
 #fPrintDict(data)
 fWrite(sf,data)
pass 

if __name__ == '__main__':
 fMain()
pass


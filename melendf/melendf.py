#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""calls melendf to generate MELCOR RN/DCH input sections
   based on ORIGEN result 
"""
import melendfmod.endf as endf

cconf = endf.config("config.conf")

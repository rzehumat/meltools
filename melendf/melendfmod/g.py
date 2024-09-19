#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import melendfmod.elements as elements

#global elemens instance
gcel=elements.elements()

#constants
xCiBq = 3.7e+10        # Ci to Bq conversion factor
xeVJ = 1.602176565e-19 # eV to J  conversion factor
ln12 = math.log(2.0)   # natural logarithm of 2
dtmin = 1.0e-10        # minimum time difference to neglect decay

#options
bPickle=False # when True ENDF data will be read from auxiliary pickle files


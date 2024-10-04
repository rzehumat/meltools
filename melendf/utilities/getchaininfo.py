#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""example use of the melendfmod package
"""

import melendfmod.isotope as isotope

cli = isotope.lisotope()
# cli.fLoadPickle(bVerbose=False)
cli.fReadENDF(bVerbose=False)
print("*** Decay chain for CS137 and RB86***")
cli.fGetChainInfo("CS137 RB86")
print("*** cli.fGetLrtyp0() ***")
print(cli.fGetLrtyp0())

# # pickle
# real	0m1.931s
# user	0m1.691s
# sys	0m0.237s

# # endf
# real	0m11.092s
# user	0m10.893s
# sys	0m0.193s

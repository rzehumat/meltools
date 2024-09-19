#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""python script browseptf.py
Simple GUI for the MELCOR binary output in Linux.

written by Petr Vokac, UJV Rez, a.s
December 2008
March 2011: added comments
September 2017: changed structure of modules, created package browseptf
April 2018: on Mac aqua is used instead of X11, see readptf.py fGnuplotTerm

License: as-is

expects "readptf.exe" on PATH !

Default plot file is MELPTF in the current folder.  Alternative plot
file can be specified as the first command line argument.

--------------------------------

GUI Usage:

DblClik or Enter on variable item in the tree adds this variable to
the chart.

Buttons:

  Reset   - clears the variable list and adds just the current from the
            tree

  Options - allows to change the range of the chart

  Script  - shows the current script for GNUPlot and allows to copy it
            through clipboard

  Max     - maximum of given variable over all the nodes

  Min     - minimum of given variable over all the nodes

  Min>0   - minimum of given variable over all nodes with value > 0.0

  Sum     - sum of given variable over all the nodes

"1 series" check box - shows just the current variable in the chart
(on the next redraw)

------------------------------

Note for use on X11:

It can be recommended to switch off continuous screen redraw on window
resize.  This avoids multiple rereading of data when gnuplot window is
resized.

E.g.: in xfce4: Settings Editor: xfwm4 box_resize=True

------------------------------

gtk on Mac, I use :

port info py35-gobject3

see https://pygobject.readthedocs.io/

"""

import browseptf.pvgtkwrap as pvgtkwrap

if __name__ == "__main__":
    pvgtkwrap.main()
pass

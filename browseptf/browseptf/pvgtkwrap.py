#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 23.3.2016  gi.require_version('Gtk', '3.0')

import sys

t = sys.version_info
if t[0] >= 3:
    # python3
    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk as gtk
else:
    # python2
    import gtk
pass
import browseptf.browseptf_class as browseptf_class


def main():
    """just run  gtk.main()"""
    sptf = "MELPTF"  # default plot file
    if len(sys.argv) > 1:
        sptf = sys.argv[1]
    pass
    tb = browseptf_class.browseptf(sptf=sptf)
    gtk.main()


pass

if __name__ == "__main__":
    print("%s is only library" % (sys.argv[0]))
pass

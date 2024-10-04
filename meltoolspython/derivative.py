#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


def main():
    x0 = None
    y0 = None
    xd = None
    f = sys.stdin.readlines()
    for line in f:
        s = line.split()
        x = float(s[0])
        y = float(s[1])
        if x0 is not None:
            xdx = x - x0
            xdy = y - y0
            if xdx > 0.0:
                xd = xdy / xdx
            else:
                xd = None
            pass
        pass
        if xd is not None:
            print((x + x0) / 2.0, xd)
        pass
        if xd is not None or x0 is None:
            x0 = x
            y0 = y
        pass
    pass


pass
#
if __name__ == "__main__":
    main()
pass

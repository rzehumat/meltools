#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

module browseptf_module
implements windows:
   options
   gnuplot script
   plot selection

written by Petr Vokac, NRI Rez plc
December 2008
License: as-is

10.3.2011 added comments
10.4.2012 added comments
23.4.2015 python3, gtk3

"""
from browseptf.pvgtkwrap import gtk
import browseptf.readptf as readptf  # fFormatVar,fPlot


# *********************************************************
class plotlist(gtk.Window):
    """defines a plot list window
    it contains list of open gnuplot windows
    and allows to select active gnuplot window
    which will obtain subsequent commands from
    the main browseptf window
    """

    # plotlist
    def __init__(self, parent=None):
        """creates plot list window"""
        self.okno = gtk.Window()
        self.boxv = gtk.VBox(False, 5)
        self.lcurrplotindex = parent.lcurrplotindex
        self.treestore = gtk.TreeStore(str)
        for s in parent.lstitle:
            piter = self.treestore.append(None, [s])
            pindex = piter
        pass
        self.treeview = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn("Plots:")
        self.treeview.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, "text", 0)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.boxv.pack_start(self.scrolledwindow, True, True, 0)
        self.buttonbox = gtk.HBox(False, 0)
        self.button_set = gtk.Button("Set Active")
        self.button_set.connect("clicked", self.fset)
        self.buttonbox.pack_start(self.button_set, False, False, 0)
        self.button_quit = gtk.Button("Close")
        self.button_quit.connect("clicked", self.close)
        self.buttonbox.pack_end(self.button_quit, False, False, 0)
        self.boxv.pack_end(self.buttonbox, False, False, 0)
        self.okno.add(self.boxv)
        self.treeview.set_cursor(self.lcurrplotindex)
        self.okno.set_title("List of plots")
        self.okno.show_all()
        self.p = parent
        self.okno.set_size_request(300, 400)

    pass

    # plotlist
    def close(self, widget):
        """closes plot list window"""
        self.okno.destroy()

    pass

    # plotlist
    def fset(self, widget):
        """set selected plot to current"""
        t = self.treeview.get_cursor()
        self.lcurrplotindex = t[0][0]
        model = self.treeview.get_model()
        iter = model.get_iter(t[0])
        sTitle = model.get_value(iter, 0)
        if self.p.lcurrplotindex != self.lcurrplotindex:
            self.p.lastplotindex = self.p.lcurrplotindex
            self.p.lcurrplotindex = self.lcurrplotindex
            self.p.cplottitle.set_text(sTitle)
        pass

    pass


pass


# *********************************************************
class gplscr(gtk.Window):
    """defines the script window
    it contains gnuplot script for the active gnuplot window

    gnuplot script can be edited and stored
    (store button)
    then the stored gnuplot script is used instead of
    that created automatically from variable list

    when you add new variable from the main browseptf
    window, this stored gnuplot script is reset again
    to empty string

    """

    # gplscr
    def __init__(self, parent=None):
        """creates the script window"""
        self.okno = gtk.Window()
        self.boxv = gtk.VBox(False, 5)
        self.okno.set_title("Readptf - Script")
        self.lcurrplotindex = parent.lcurrplotindex
        self.p = parent
        # self.titleframe = gtk.Frame("Chart title:")
        self.titleframe = gtk.Frame(label="Chart title:")
        self.stitle = gtk.Entry()
        self.stitle.set_max_length(150)
        self.stitle.set_text(parent.lstitle[self.lcurrplotindex])
        self.titleframe.add(self.stitle)
        self.boxv.pack_start(self.titleframe, False, False, 0)
        if len(self.p.lstext[self.lcurrplotindex]) > 0:
            s = self.p.lstext[self.lcurrplotindex]
            sxy = ""
            st = ""
        else:
            s = readptf.fFormatVar(self.p.llvarplot[self.lcurrplotindex], parent.sptf)
            sxy, st = readptf.fFormatOptions(self.p.loptions[self.lcurrplotindex])
        pass
        # self.swf = gtk.Frame("Current gnuplot script:")
        self.swf = gtk.Frame(label="Current gnuplot script:")
        self.sw = gtk.ScrolledWindow()
        # self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        textbuffer = self.textview.get_buffer()
        self.sw.add(self.textview)
        textbuffer.set_text(st + sxy + s)
        self.swf.add(self.sw)
        self.boxv.pack_start(self.swf, True, True, 0)
        self.buttonbox = gtk.HBox(False, 0)
        self.button_replot = gtk.Button("Replot")
        self.button_replot.connect("clicked", self.function_replot)
        self.buttonbox.pack_start(self.button_replot, False, False, 0)
        self.button_store = gtk.Button("Store")
        self.button_store.connect("clicked", self.function_store)
        self.buttonbox.pack_start(self.button_store, False, False, 0)
        self.button_fromvars = gtk.Button("FromVars")
        self.button_fromvars.connect("clicked", self.function_fromvars)
        self.buttonbox.pack_start(self.button_fromvars, False, False, 0)
        self.button_quit = gtk.Button("Close")
        self.button_quit.connect("clicked", self.close)
        self.buttonbox.pack_end(self.button_quit, False, False, 0)
        self.boxv.pack_end(self.buttonbox, False, False, 0)
        self.okno.add(self.boxv)
        self.okno.set_size_request(500, 300)
        # self.okno.set_modal(True)
        self.okno.show_all()

    pass

    # gplscr
    def function_replot(self, widget, data=None):
        """replot the current chart with modified script
        do not forget to >>store<< edited script before
        """
        sTitle = self.stitle.get_text()
        # 11.4.2018
        sgt = readptf.fGnuplotTerm(sTitle)
        # sgt = "\nset term x11 title \"%s\"\n" % (sTitle)
        readptf.fPlot(sgt, lcp=self.lcurrplotindex)
        textbuffer = self.textview.get_buffer()
        istart = textbuffer.get_start_iter()
        iend = textbuffer.get_end_iter()
        s = textbuffer.get_text(istart, iend, True)
        readptf.fPlot(s, lcp=self.lcurrplotindex)
        return

    pass

    # gplscr
    def function_store(self, widget, data=None):
        """store modified script to be used instead
        of internal list of variables"""
        self.p.lstitle[self.lcurrplotindex] = self.stitle.get_text()
        textbuffer = self.textview.get_buffer()
        istart = textbuffer.get_start_iter()
        iend = textbuffer.get_end_iter()
        self.p.lstext[self.lcurrplotindex] = textbuffer.get_text(istart, iend, True)
        if self.p.lcurrplotindex == self.lcurrplotindex:
            self.p.cplottitle.set_text(self.p.lstitle[self.lcurrplotindex])
        pass

    pass

    # gplscr
    def function_fromvars(self, widget, data=None):
        """recreate script from the list of variables,
        i.e. set stored script to empty string"""
        s = readptf.fFormatVar(self.p.llvarplot[self.p.lcurrplotindex], self.p.sptf)
        sxy, st = readptf.fFormatOptions(self.p.loptions[self.lcurrplotindex])
        textbuffer = self.textview.get_buffer()
        textbuffer.set_text(st + sxy + s)
        self.p.lstext[self.lcurrplotindex] = ""

    pass

    # gplscr
    def close(self, widget):
        """close the script window"""
        self.okno.destroy()

    pass


pass


# *********************************************************
class options(gtk.Window):
    """defines window options"""

    # options
    def __init__(self, parent=None):
        """creates options window"""
        self.p = parent
        self.lcurrplotindex = parent.lcurrplotindex
        self.toptions = parent.loptions[self.lcurrplotindex]
        self.okno = gtk.Window()
        self.boxv = gtk.VBox(False, 5)
        self.boxh1 = gtk.HBox(False, 5)
        self.labelxrange = gtk.Label("x range: ")
        self.labelxrange.set_alignment(0, 0)
        #        self.labelxrange.set_justify(gtk.JUSTIFY_LEFT)
        self.boxh1.pack_start(self.labelxrange, False, False, 0)
        self.xmin = gtk.Entry()
        self.xmin.set_max_length(50)
        self.xmin.set_text(self.toptions[0])
        self.boxh1.pack_start(self.xmin, False, False, 0)
        self.xmax = gtk.Entry()
        self.xmax.set_max_length(50)
        self.xmax.set_text(self.toptions[1])
        self.boxh1.pack_end(self.xmax, False, False, 0)
        self.boxv.pack_start(self.boxh1, False, False, 0)
        self.boxh2 = gtk.HBox(False, 5)
        self.labelyrange = gtk.Label("y range: ")
        self.labelyrange.set_alignment(0, 0)
        # self.labelyrange.set_justify(gtk.JUSTIFY_LEFT)
        self.boxh2.pack_start(self.labelyrange, False, False, 0)
        self.ymin = gtk.Entry()
        self.ymin.set_max_length(50)
        self.ymin.set_text(self.toptions[2])
        self.boxh2.pack_start(self.ymin, False, False, 0)
        self.ymax = gtk.Entry()
        self.ymax.set_max_length(50)
        self.ymax.set_text(self.toptions[3])
        self.boxh2.pack_end(self.ymax, False, False, 0)
        self.boxv.pack_start(self.boxh2, False, False, 0)
        self.boxh3 = gtk.HBox(False, 5)
        self.labelxlabels = gtk.Label("x axis labels in: ")
        self.boxh3.pack_start(self.labelxlabels, False, False, 0)
        self.rbuttons = gtk.RadioButton.new_with_label_from_widget(None, "Seconds")
        self.rbuttons.connect("toggled", self.radiocallback, "Seconds")
        self.boxh3.pack_start(self.rbuttons, True, True, 0)
        if self.toptions[4] == "Seconds":
            self.rbuttons.set_active(True)
        pass
        self.rbuttonm = gtk.RadioButton.new_with_label_from_widget(
            self.rbuttons, "Minutes"
        )
        self.rbuttonm.connect("toggled", self.radiocallback, "Minutes")
        self.boxh3.pack_start(self.rbuttonm, True, True, 0)
        if self.toptions[4] == "Minutes":
            self.rbuttonm.set_active(True)
        pass
        self.rbuttonh = gtk.RadioButton.new_with_label_from_widget(
            self.rbuttonm, "Hours"
        )
        self.rbuttonh.connect("toggled", self.radiocallback, "Hours")
        self.boxh3.pack_end(self.rbuttonh, True, True, 0)
        if self.toptions[4] == "Hours":
            self.rbuttonh.set_active(True)
        pass
        self.boxv.pack_start(self.boxh3, False, False, 0)
        self.buttonbox = gtk.HBox(False, 0)
        self.button_ok = gtk.Button("Replot")
        self.button_ok.connect("clicked", self.function_ok)
        self.buttonbox.pack_start(self.button_ok, False, False, 0)
        self.button_quit = gtk.Button("Close")
        self.button_quit.connect("clicked", self.close)
        self.buttonbox.pack_start(self.button_quit, False, False, 0)
        self.boxv.pack_start(self.buttonbox, False, False, 0)
        self.okno.add(self.boxv)
        self.okno.connect("delete_event", self.delete_event)
        self.okno.set_title("Options " + self.p.lstitle[self.lcurrplotindex])
        self.okno.show_all()

    pass

    # options
    def close(self, widget):
        """close options window"""
        self.okno.destroy()

    pass

    # options
    def delete_event(widget, event, data=None):
        """close options window"""
        widget.close(widget)
        return True

    pass

    # options
    def radiocallback(self, widget, data=None):
        """save new radiobutton position when changed"""
        self.toptions[4] = data

    pass

    # options
    def function_ok(self, widget, data=None):
        """save options and replot the current chart"""
        self.toptions[0] = self.xmin.get_text()
        self.toptions[1] = self.xmax.get_text()
        self.toptions[2] = self.ymin.get_text()
        self.toptions[3] = self.ymax.get_text()
        s, st = readptf.fFormatOptions(self.toptions)
        readptf.fPlot(s, lcp=self.lcurrplotindex)
        readptf.fPlot(st, lcp=self.lcurrplotindex)
        readptf.fPlot("replot\n", lcp=self.lcurrplotindex)
        self.p.loptions[self.lcurrplotindex] = self.toptions
        return

    pass
    # def on_button_toggled(self, button, name):
    # if button.get_active():
    #  state = "on"
    # else:
    #  state = "off"
    # print("Button", name, "was turned", state)
    # pass


pass
if __name__ == "__main__":
    import sys

    print("%s is only library" % (sys.argv[0]))
pass

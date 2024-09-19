#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 module browseptf_class
 written by Petr Vokac, NRI Rez plc
 December 2008
 License: as-is

 10.3.2011 added comments, improved seek in lvarde
 10.4.2012 code cleanup
'''

from browseptf.pvgtkwrap import gtk
import browseptf.readptf as readptf
import browseptf.browseptf_module as bm
import browseptf.varde as varde


class browseptf:
    '''defines browseptf main window
       it contains list of variables and
       control buttons
    '''

    # browseptf
    def __init__(self, sptf='MELPTF'):
        '''Create a new browser window'''
        self.sptf = "MELPTF"  # MELCOR binary output file name
        self.llvarplot = []  # list of variable lists for all the plots 
        self.sTitle = ""      # title of the current plot
        self.lstitle = []   # list of plot titles        
        self.lstext = []  # list of gnuplot scripts for each plot, 
        #                  it is used instead of varlist when it is set
        self.loptions = []  # list of options
        # xmin,xmax,ymin,ymax,timedata
        self.tdoptions = ["*", "*", "*", "*", "Hours"]  # default options for the new chart
        self.lcurrplotindex = 0
        # self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window = gtk.Window()
        self.sptf = sptf
        s = readptf.fInitiate(sptf=sptf)
        try:
            self.window.set_title(s.decode('UTF-8'))
        except:
            print("Wrong letters in the sequence title:")
            print(s.decode('UTF-8'))
            print("Set default window title to BrowsePTF")
            self.window.set_title("BrowsePTF")
        pass
        self.sTitle = s.split()[0]
        self.fNewPlotc(self.window)
        # optimised to my 1600x1200 screen
        # self.window.set_size_request(400, 1100)
        self.window.set_size_request(450, 700)
        self.window.connect("delete_event", self.delete_event)
        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str)  # str is the type declaration of the column
        # we'll add some data now - 4 rows with 3 child rows each
        #        lvar = readptf.fListVar(sptf=sptf)
        ssold = ""
        ssold1 = ""
        # print(readptf.lVarKey)
        for tvar in readptf.lVarKey:
            ss = tvar[0].split("-")
            if (tvar[1] > 1):
                sh = ".#"
            else:
                if tvar[2][0] > 0:
                    sh = ".%d" % (tvar[2][0])
                else:
                    sh = ""
                pass
            pass
            if (len(ss) < 2):  # there is no dash in the variable name
                sss = tvar[0]
                piter = self.treestore.append(None, [sss+sh])
                pindex = piter
                ssold = ""
            else:
                if (len(ss) < 3):  # there is just one dash in the variable name
                    sss = ss[0]       # add the part before the dash as the first column
                    if sss != ssold:
                        piter = self.treestore.append(None, [sss])
                    ssold = sss
                    sd = ss[1].split(".")  # try to split the second part by dot
                    if (len(sd) < 2):    # split unsuccessful, add the whole variable name to the second column 
                        sss = tvar[0]
                        child1 = self.treestore.append(piter, [sss+sh])
                        pindex = child1
                    else:
                        sss = ss[0] + "-" + sd[0]  # split using dot successful
                        sn = readptf.fIsNCG(tvar[0])  # try special treatment for non-condensables
                        if (sss != ssold1):
                            child1 = self.treestore.append(piter, [sss])
                        ssold1 = sss
                        sss = tvar[0]
                        child2 = self.treestore.append(child1, [sss+sh+" "+sn])
                        pindex = child2
                    pass
                else:            # there are more than two dashes
                    sss = ss[0]
                    if sss != ssold:
                        # print("piter",sss,sh)
                        piter = self.treestore.append(None, [sss])
                    ssold = sss
                    sss = sss + "-" + ss[1]
                    if (sss != ssold1):
                        child1 = self.treestore.append(piter, [sss])
                    ssold1 = sss
                    if sss == "RN1-TYCLT":
                        i = int(ss[2])
                        lIndex = readptf.fGetVarIndex(sss)
                        if len(lIndex) > 0:
                            try:
                                sss = tvar[0] + sh + " " + lIndex[i-1]
                            except:
                                sss = tvar[0] + sh
                            pass
                        else:
                            sss = tvar[0] + sh
                        pass
                    else:
                        sss = tvar[0] + sh
                    pass
                    child2 = self.treestore.append(child1, [sss])
                    pindex = child2
                pass
            pass
            sss = tvar[0]
            if tvar[1] > 1:
                iIndex = -1
                for lv in readptf.lVarIndex:
                    try:
                        iIndex = lv[0].index(sss)
                        lIndex = lv[1]
                        iIndex = 1
                        break
                    except:
                        continue
                    pass
                pass
                if iIndex < 0:
                    for i in range(tvar[1]):
                        self.treestore.append(pindex, ['%s.#%i (%i)' % (sss, i+1, tvar[2][i])])
                    pass
                else:
                    for i in range(tvar[1]):
                     try :
                      self.treestore.append(pindex, ['%s.#%i %s' % (sss,i+1,lIndex[i])])
                     except :
                      self.treestore.append(pindex, ['%s.#%i' % (sss,i+1)])
                     pass
                    pass
                pass
            pass
        pass #for tvar in lvar
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)
        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn('Variable tree:')
        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)
        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)
        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        # make it searchable
        # self.treeview.set_search_column(0)
        # Allow sorting on the column
        # self.tvcolumn.set_sort_column_id(0)
        # Allow drag and drop reordering of rows
        # self.treeview.set_reorderable(True)
        self.treeview.connect('row-activated', self.function_row_activated)
        #self.window.add(self.treeview)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.box = gtk.VBox(False, 5) # 5 pixels space
        self.box.pack_start(self.scrolledwindow,True,True,0)
        self.labelbox = gtk.HBox(False,5) 
        self.box.pack_start(self.labelbox,False,False,0)
        self.label = gtk.Label("Variable not selected")
        self.label.set_alignment(0, 0)
        #python2 gtk        
        #self.label.set_justify(gtk.JUSTIFY_LEFT)
        #python3 gi
        #self.label.set_justify(gtk.Justification.LEFT)
        self.label.set_selectable(True)
        #self.framevar = gtk.Frame("Selected variable:")
        self.framevar = gtk.Frame()
        self.framevar.label="Selected variable:"
        self.framevar.add(self.label)
        self.labelbox.pack_start(self.framevar,True,True,0)
        #self.frameuni = gtk.Frame("Unit:")
        self.frameuni = gtk.Frame()
        self.uni = gtk.Label("")
        self.uni.set_alignment(0, 0)
        #self.uni.set_justify(gtk.JUSTIFY_RIGHT)
        #self.uni.set_justify(gtk.Justification.RIGHT)
        self.uni.set_selectable(True)
        self.frameuni.add(self.uni)
        self.labelbox.pack_end(self.frameuni,False,False,0)
        self.des = gtk.Label("No description")
        self.des.set_alignment(0, 0)
        #self.des.set_justify(gtk.JUSTIFY_LEFT)
        #self.des.set_justify(gtk.Justification.LEFT)
        self.des.set_selectable(False)
        self.des.set_line_wrap(True)
        #self.framedes = gtk.Frame("Variable description:")
        self.framedes = gtk.Frame()
        self.framedes.label = "Variable description:"
        self.framedes.add(self.des)
        self.box.pack_start(self.framedes,False,False,0)
        self.buttonbox = gtk.HBox(False, 0)
        self.button_reset = gtk.Button("Reset")
        self.button_reset.connect("clicked", self.function_reset)
        self.buttonbox.pack_start(self.button_reset,False,False,0)
        self.button_option = gtk.Button("Options")
        self.button_option.connect("clicked", self.function_option)
        self.buttonbox.pack_start(self.button_option,False,False,0)
        self.button_script = gtk.Button("Script")
        self.button_script.connect("clicked", self.function_script)
        self.buttonbox.pack_start(self.button_script,False,False,0)
        self.button_max = gtk.Button("Max")
        self.button_max.connect("clicked", self.function_max)
        self.buttonbox.pack_start(self.button_max,False,False,0)
        self.button_min = gtk.Button("Min")
        self.button_min.connect("clicked", self.function_min)
        self.buttonbox.pack_start(self.button_min,False,False,0)
        self.button_min0 = gtk.Button("Min>0")
        self.button_min0.connect("clicked", self.function_min0)
        self.buttonbox.pack_start(self.button_min0,False,False,0)
        self.button_sum = gtk.Button("Sum")
        self.button_sum.connect("clicked", self.function_sum)
        self.buttonbox.pack_start(self.button_sum,False,False,0)
        self.onlyone_button = gtk.CheckButton("1series")
        self.buttonbox.pack_start(self.onlyone_button,False,False,0)
        self.box.pack_start(self.buttonbox,False,False,0)
        self.buttonbox2 = gtk.HBox(False, 0)
        #self.cplotframe = gtk.Frame("Current plot: ")
        self.cplotframe = gtk.Frame()
        self.cplotframe.label="Current plot: "
        self.cplottitle = gtk.Label(self.sTitle.decode('UTF-8') + " Plot 1")
        self.cplottitle.set_alignment(0, 0)
        #self.cplottitle.set_justify(gtk.JUSTIFY_LEFT)
        #self.cplottitle.set_justify(gtk.Justification.LEFT)
        self.cplotframe.add(self.cplottitle)
        self.buttonbox2.pack_start(self.cplotframe,False,False,0)
        self.button_newplot = gtk.Button("NewPlot")
        self.button_newplot.connect("clicked", self.fNewPlotc )
        self.buttonbox2.pack_start(self.button_newplot,False,False,0)
        self.button_plots = gtk.Button("Plots")
        self.button_plots.connect("clicked", self.fPlots )
        self.buttonbox2.pack_start(self.button_plots,False,False,0)
        self.button_save = gtk.Button("Save")
        self.button_save.connect("clicked", self.fSave )
        self.buttonbox2.pack_start(self.button_save,False,False,0)
        self.button_load = gtk.Button("Load")
        self.button_load.connect("clicked", self.fLoad )
        self.buttonbox2.pack_start(self.button_load,False,False,0)
        self.button_replot = gtk.Button("Replot")
        self.button_replot.connect("clicked", self.fReplot )
        self.buttonbox2.pack_start(self.button_replot,False,False,0)
        self.box.pack_start(self.buttonbox2,False,False,0)
        self.buttonbox3 = gtk.HBox(False, 0)
        self.button_quit = gtk.Button("Quit")
        self.button_quit.connect("clicked", lambda w: gtk.main_quit())
        self.buttonbox3.pack_start(self.button_quit,False,False,0)
        self.box.pack_end(self.buttonbox3,False,False,0)
        self.window.add(self.box)
        # piece of code from 
        #          http://eccentric.cx/misc/pygtk/pygtkfaq.html
        #          13.11. 995
        ##self.treeView = gtk.TreeView(mymodel)
        self.selection = self.treeview.get_selection()
        self.selection.connect('changed', self.on_selection_changed)
        self.window.show_all()        
    pass
    #browseptf

    def fReplotAll(self) :
     '''replot all charts'''
     np = len (self.llvarplot)
     for i in range(np) :
      if len(self.lstext[i])>0 :
       s=self.lstext[i]
       readptf.fPlot(s,i,sTitle=self.lstitle[i])
      else :
       if len(self.llvarplot[i])>0 :
        sxy,st = readptf.fFormatOptions(self.loptions[i])
        sp=readptf.fFormatVar(self.llvarplot[i],sptf=self.sptf)
        s=sxy+sp
        readptf.fPlot(s,i,sTitle=self.lstitle[i],sfT=st)
       pass
      pass
     pass
    pass
    #browseptf
    def fSave(self,widget,data=None) :
     '''save current state to browseptf.pickle'''
     f=open("browseptf.pickle",'wb')
     pickle.dump(self.llvarplot,f)
     pickle.dump(self.lstitle  ,f)
     pickle.dump(self.lstext   ,f)
     pickle.dump(self.loptions ,f)
     f.close()
    pass
    #browseptf
    def fLoad(self,widget,data=None) :
     '''load charts definitions from browseptf.pickle
         and plots data
     '''
     f=open("browseptf.pickle",'rb')
     self.llvarplot=pickle.load(f)
     self.lstitle  =pickle.load(f)
     self.lstext   =pickle.load(f)
     self.loptions =pickle.load(f)
     f.close()
     self.fReplotAll()
    pass
    #browseptf
    def fReplot(self,widget,data=None) :
     '''just call fReplotAll'''
     self.fReplotAll()
    pass
    #browseptf
    def fNewPlotc(self,widget,data=None) :
     '''plot data in a new gnuplot instance'''
     sTitle=readptf.fNewPlot(self.sTitle)
     self.lstitle.append(sTitle)
     self.lstext.append("")
     self.llvarplot.append([])
     lo = [] # create a new copy of default options
     for o in self.tdoptions :
      lo.append(o) 
     self.loptions.append(lo)
     self.lcurrplotindex=len(self.lstitle)-1
     try :
      self.cplottitle.set_text(sTitle)
      self.fTryPlot()
     except :
      pass
     pass
    pass
    #browseptf
    def delete_event(self, widget, event, data=None):
     '''close the window and quit'''
     gtk.main_quit()
     return False
    pass
    #browseptf
    def fTryPlot(self) :
     '''try to plot selected variable'''
     value=self.label.get_text()
     iReset=self.onlyone_button.get_active()
     if iReset :
      print("Reset variable list")
      self.llvarplot[self.lcurrplotindex] = []
     pass
     iAdd=0
     try :
      i=self.llvarplot[self.lcurrplotindex].index(value)
     except :
      iAdd=1
     pass
     if (iAdd>0) :
      svarwi=value.split() 
      svar=svarwi[0].split("#")
      try :
       i=readptf.lvar1.index(svar[0])       
       iAdd=1
      except :
       iAdd=0
      pass
     pass
     if (iAdd>0) :
      if (len (self.lstext[self.lcurrplotindex]) > 0 ) : 
       # when variable is added : clean the stored gnuplot string
       self.lstext[self.lcurrplotindex]="" 
      pass
      self.llvarplot[self.lcurrplotindex].append(value)
      s=readptf.fFormatVar(self.llvarplot[self.lcurrplotindex],sptf=self.sptf)
      if len(s)>10 :
       readptf.fPlot(s,lcp=self.lcurrplotindex)
      else :
       self.label.set_text(value + " - not valid variable! (len<10)")
      pass
     else :
      self.label.set_text(value + " - not valid variable! (iAdd==0)")
     pass
    pass
    #browseptf
    def fTryFun(self,sfun) :
     '''tries to plot predefined function for selected variable
         variable is refused when it is already in the list
         or when it is not valid variable
     '''
     value=self.label.get_text()
     iReset=self.onlyone_button.get_active()
     if iReset :
      print("Reset variable list")
      self.llvarplot[self.lcurrplotindex] = []
     pass
     svarwi=value.split() 
     svar=svarwi[0].split("#")
     try :
      i=readptf.lvar1.index(svar[0])
      s="%s#%s" % (svar[0],sfun)       
      iAdd=1
     except :
      iAdd=0
     pass
     if (iAdd>0) :
      try :
       i=self.llvarplot[self.lcurrplotindex].index(s)
       iAdd=0
       self.label.set_text(value + " - not valid variable! (iAdd==0)")
      except :
       self.llvarplot[self.lcurrplotindex].append(s)
       iAdd=1
      pass
      s=readptf.fFormatVar(self.llvarplot[self.lcurrplotindex],sptf=self.sptf)
      if len(s)>10 :
       readptf.fPlot(s,lcp=self.lcurrplotindex)
      else :
       self.label.set_text(value + " - not valid variable! (len<10)")
      pass
     pass
    pass
    #browseptf
    def function_row_activated(self, treeview, path, column):
     '''plot variable on enter?'''
     model = treeview.get_model()
     iter = model.get_iter(path)
     value = model.get_value(iter, 0)
     self.label.set_text(value)
     self.fTryPlot()
    pass        
    #browseptf
    def function_move_cursor(self, treeview,step,count):
     '''currently do nothing'''
     pass   
    pass
    #browseptf
    def function_reset (self,widget,data=None) :
     '''resets variable list'''
     self.llvarplot[self.lcurrplotindex] = []
     print("Reset variable list")
     self.fTryPlot()
    pass
    #browseptf
    def function_max (self,widget,data=None) :
     '''calculate maximum for selected variable'''
     self.fTryFun("max")
    pass
    #browseptf
    def function_min (self,widget,data=None) :
     '''calculate minimum for selected variable'''
     self.fTryFun("min")
    pass
    #browseptf
    def function_min0 (self,widget,data=None) :
     '''calculate minimum for selected variable
        takes into account only values greater than zero
     '''
     self.fTryFun("min0")
    pass
    #browseptf
    def function_sum (self,widget,data=None) :
     '''calculate sum for selected variable'''
     self.fTryFun("sum")
    pass
    #browseptf
    def function_option (self,widget,data=None) :
     '''open window with options for the current plot'''
     try :
      self.gs.close(self.gs)
     except :
      pass
     pass
     self.gs = bm.options(self)
    pass
    #browseptf
    def function_script (self,widget,data=None) :
     '''open window with gnuplot script for the current chart'''
     try :
      self.gplscr.close(self.gplscr)
     except :
      pass
     pass
     self.gplscr = bm.gplscr(self) 
    pass
    #browseptf
    def fPlots (self,widget,data=None) :
     '''open window with list of plots'''
     try :
      self.plotlist.close(self.plotlist)
     except :
      pass
     pass
     self.plotlist = bm.plotlist(self) 
    pass
    #browseptf
    def on_selection_changed(self,selection): 
     '''tries to find variable explanation when selection changes'''
     model, paths = selection.get_selected_rows()
     if paths:
      #do the thing!
      #print "paths: ", paths
      iter = model.get_iter(paths[0])
      value = model.get_value(iter, 0)
      self.label.set_text(value)
      s=value.split("#")[0].lower()
      iHit=0
      lt=[]
      for t in varde.lvarde :
       il=len(s)
       if (t[0][:il].lower()==s) :
        su = t[1]
        sd = t[2]
        iHit+=1
        lt.append(t[0])
       pass
      pass
      if (iHit==0) :
       ss = s.split(".")
       if len(ss)>1 :
        sss = '.'.join(ss[0:-1])
        #print ss,sss
        for t in varde.lvarde :
         il=len(sss)
         if (t[0][:il].lower()==sss) :
          su = t[1]
          sd = t[2]
          iHit+=1
          lt.append(t[0])
         pass
        pass
       pass
      pass          
      if (iHit==0) :
       ss = s.split("-")
       if len(ss)>1 :
        sss = '-'.join(ss[0:-1])
        #print ss,sss
        for t in varde.lvarde :
         il=len(sss)
         if (t[0][:il].lower()==sss) :
          su = t[1]
          sd = t[2]
          iHit+=1
          lt.append(t[0])
         pass
        pass
       pass
      pass          
      if (iHit!=1) :
       sd = "No description (Hits: %d)" % (iHit)
       su = ""
      pass
      self.des.set_text(sd)
      self.uni.set_text(su)
      #if (iHit>1) :
      # print lt
      # print ""
      #pass
     pass 
    pass
pass  # end class browseptf

if __name__ == "__main__":
 import sys
 print ( "%s is only library" % (sys.argv[0]) )
pass

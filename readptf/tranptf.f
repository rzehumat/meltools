      programe tranptf
C
C     a utility to manipulate with 
c     MELCOR 1.8.6 and melcor 2.1 binary plot files
C
C     written by Petr Vokac, NRI Rez plc
C     January, February 2012
c
c     14.5.2012 added ievery(mptf)
c     17.5.2012 increased mptf = 20
c     18.5.2012 sFiltVars - the last requested variable should be scalar
c                         - check if the variable is found 
c     25.8.2014 dtmin to allow filter out records from BURN
c               modified input check output
c               some comments
c
c     12.5.2017 skip reading rest of the input file when sendtime reached
c      
      use tranptfmod
      use tranptfaux
      use tranptfvar
      implicit none
      character*250 sinput
      if (fGetArgs(sinput).eq.0) goto 900
      call inputread(sinput)
      call inputout()
      if (svarlist.ne."") then
       call sReadVar(svarlist)
c       listing of variables replaced by warnings in sFiltVars
c       call sPrintVar()
      end if
      call transfallfiles()
 900  continue
      END programe tranptf



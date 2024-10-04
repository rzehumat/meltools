      program tranptf
!
!     a utility to manipulate with 
!     MELCOR 1.8.6 and melcor 2.1 binary plot files
!
!     written by Petr Vokac, NRI Rez plc
!     January, February 2012
!
!     14.5.2012 added ievery(mptf)
!     17.5.2012 increased mptf = 20
!     18.5.2012 sFiltVars - the last requested variable should be scalar
!                         - check if the variable is found 
!     25.8.2014 dtmin to allow filter out records from BURN
!               modified input check output
!               some comments
!
!     12.5.2017 skip reading rest of the input file when sendtime reached
!      
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
!       listing of variables replaced by warnings in sFiltVars
!       call sPrintVar()
      end if
      call transfallfiles()
 900  continue
      END program tranptf



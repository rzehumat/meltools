      module tranptfaux
      implicit none
      contains
      integer function fGetArgs(sinput)
! get configuration file name from the command line
      use readptfmod, only: sinfo
      character*250 sinput
      integer i
      integer iRet
      i=IARGC()
      sinput=""
      IF (i.LT.1) then
       call sinfo("tranptf")
       call helpout
       iRet=0
      else
       CALL GETARG(1,sinput)
       iRet=1
      end if
      fGetArgs = iRet
      return
      end function fGetArgs

      subroutine helpout()
      WRITE (*,*) '-------------------------------------------------'
      WRITE (*,*) 'One obligatory command line argument:            '
      WRITE (*,*) '  configuration input file name                  '
      WRITE (*,*) '-------------------------------------------------'
      WRITE (*,*) 'Configuration file is in FORTRAN namelist fortmat'
      WRITE (*,*) 'Namelist name is "&INPUT" and the file should' 
      WRITE (*,*) 'end by "/". '
      WRITE (*,*) 'Input variables are:'
      WRITE (*,*) ' stitle        title of output file'
      WRITE (*,*) ' svarlist      file with variable list'
      WRITE (*,*) ' smelptfo      output file (obligatory)'
      WRITE (*,*) ' inrpd = 1    print dot per every inrpd record'
      WRITE (*,*) ' smelptfi(20) input file (at least one obligatory)'
      WRITE (*,*) ' sstarttime(20) start time'
      WRITE (*,*) ' sendtime(20)   end time'
      WRITE (*,*) ' ievery(20) integer output every ievery-th record'
      WRITE (*,*) ' sdtmin(20) skip records with time-timelast<dtmin'
      WRITE (*,*) '-------------------------------------------------'
      return
      end subroutine helpout

      end module tranptfaux

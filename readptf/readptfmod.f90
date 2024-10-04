      module readptfmod
      use globals
      implicit none
      contains
!     16.9.2015
!     20.2.2017 correction of NRECT, now the the last variable can be an array
!     13.4.2018 broken pipe error handling
!     8.1.2019 names processing ignored when index is larger than mvar      
      subroutine fIsSPName(SSP)
      CHARACTER(LEN = *) SSP
      CHARACTER(16) SOUT
      integer idash
      integer ibrl
      integer ibrr
      integer ilen
      integer iii
      SOUT = ""
      ilen = LEN_TRIM(SSP)
      idash = INDEX(SSP,'CVH-VOLUME-NAME')
      ibrl = INDEX(SSP,'((')
      ibrr = INDEX(SSP,'))')
      if ((ilen.gt.0).and.
     +     (idash.gt.0).and.
     +     (ibrl.gt.0).and.
     +     (ibrr.gt.0)) then
       SOUT=SSP(ibrr+2:ilen)
       read(SSP(ibrl+2:ibrr-1),*) iii
!         WRITE(*,*) ilen,idash,ibrl,ibrr      
!         write(*,*) SSP(ibrl+2:ibrr-1)
       if (iii.gt.mvar) then
!       ignore too large volume index        
        return
       endif
       sCvhVolumeName(iii)=SOUT
       if (iii.gt.nCvhVolumeName) nCvhVolumeName=iii
!      write(*,*) nCvhVolumeName
       return
      endif
      idash = INDEX(SSP,'FL-PATH-NAME')      
      if ((ilen.gt.0).and.
     +     (idash.gt.0).and.
     +     (ibrl.gt.0).and.
     +     (ibrr.gt.0)) then
       SOUT=SSP(ibrr+2:ilen)
       read(SSP(ibrl+2:ibrr-1),*) iii
!         WRITE(*,*) ilen,idash,ibrl,ibrr      
!         write(*,*) SSP(ibrl+2:ibrr-1)
       if (iii.gt.mvar) then
!       ignore too large flow path index        
        return
       endif       
       sFlPathName(iii)=SOUT
       if (iii.gt.nFlPathName) nFlPathName=iii
       return
      endif
      end subroutine fIsSPName
!
      subroutine fPrintSPNames()
      integer i,il
      write(*,*) "CVH volume names"
      do i=1,nCvhVolumeName
       il = LEN_TRIM(sCvhVolumeName(i))
       if (il.gt.0 .and. .not. sCvhVolumeName(i)=="") write(*,*) i,
     +  sCvhVolumeName(i),il
      enddo
      write(*,*) "FL path names"      
      do i=1,nFlPathName
       il = LEN_TRIM(sFlPathName(i))
       if (il.gt.0 .and. .not. sFlPathName(i)=="") write(*,*) i,
     +  sFlPathName(i),il
      enddo
      end subroutine fPrintSPNames
!
      integer function fGetCVHId(sname)
      CHARACTER(LEN = *) sname
      integer i
!      write(*,*) nCvhVolumeName
      do i=1,nCvhVolumeName
!       write(*,*) sname,sCvhVolumeName(i)    
       if (sCvhVolumeName(i).eq.sname) then
        fGetCVHId=i
        return
       endif  
      enddo
      fGetCVHId=0
      return
      end function fGetCVHId
!
      integer function fGetFLId(sname)
      CHARACTER(LEN = *) sname
      integer i
      do i=1,nFlPathName
       if (sFlPathName(i).eq.sname) then
        fGetFLId=i
        return
       endif  
      enddo
      fGetFLId=0
      return
      end function fGetFLId
!     
      integer function fGetArgs()
!     auxiliary variables
      CHARACTER*24 SAUX 
      integer i,j,k,iRet
!     function code
      i=IARGC()
      IF (i.LT.2) GOTO 10
      CALL GETARG(1,FNAME)
      CALL GETARG(2,SVOUT)
      IF (i.GT.2) THEN
        CALL GETARG(3,SAUX)
        READ(SAUX,*) iOpt
      ENDIF
      if (SVOUT.eq."varindex") then
       do j=4,i
        CALL GETARG(j,SAUX)
        READ(SAUX,*) iddo(j-3)
       enddo
       nddo=i-3
      endif
      iRet = -1
      goto 11
 10   CONTINUE
      call sinfo("readptf")
      call helpout
      iRet = 0
 11   continue
      fGetArgs = iRet
      return
      end function fGetArgs

      integer function fGetSVOUTidl(SVOUT)
!     input arguments
      CHARACTER(LEN = *) SVOUT
!     local variables
      integer i,j,iL,iLS,iK
      CHARACTER*24 SAUX
      integer iFound
!     code
      iLS=LEN_TRIM(SVOUT)
!     loop over all variable names to find exact match
      iFound=0
      DO i=1,NKEYT
       iL=LEN_TRIM(SVAR(i))
       if (iLS.EQ.iL) then 
        if (SVOUT(1:iL).EQ.SVAR(i)(1:iL)) then
         do j=ID(i),ID(i+1)-1
!          WRITE (*,*) j,nddo
          nddo=nddo+1
          iddo(nddo)=j
          iFound=iFound+1
         enddo
        endif
       endif
      enddo
      fGetSVOUTidl=iFound
      return
      end function fGetSVOUTidl

      integer function fGetSVOUTide(SVOUT)
!     input arguments
      CHARACTER(LEN = *) SVOUT
!     local variables
      integer i,j,iL,iLS,iK
      CHARACTER*24 SAUX
      integer iFound
!     code
      iLS=LEN_TRIM(SVOUT)
!     loop over all variable names to find match with
!     after dot spec
      iFound=0
      DO i=1,NKEYT
       iK=0
       iL=LEN_TRIM(SVAR(i))
       IF (iL+1.LT.iLS) THEN
!       variable name is shorter than input keyword
        IF (SVOUT(iL+1:iL+1).EQ.".") THEN
         WRITE(SAUX,*) '(I',iLS+2-iL,')'
         READ(SVOUT(iL+2:iLS),ERR=1000,FMT=SAUX) iK
 1000    CONTINUE
         if (iK.eq.0) then
          if (SVOUT(1:4).EQ."CVH-") then
           iK = fGetCVHId(SVOUT(iL+2:iLS))  
          endif
          if (SVOUT(1:3).EQ."FL-") then
           iK = fGetFLId(SVOUT(iL+2:iLS))  
          endif
         endif
        ENDIF
!        WRITE (*,*) SVOUT(1:iL),SVAR(i)(1:iL)
        IF (SVOUT(1:iL).EQ.SVAR(i)(1:iL)) then
         IF (iK.GT.0) THEN
          DO j=ID(i),ID(i+1)-1
!           WRITE (*,*) IDD(j),iK
           IF (IDD(j).EQ.iK) THEN
            iddo(nddo+1)=j
            nddo=nddo+1
            iFound=iFound+1
           ENDIF
          ENDDO
         endif
        endif
       endif
      enddo
      fGetSVOUTide=iFound
      return
      end function fGetSVOUTide

      subroutine sinfo(sexe)
      character*7 sexe
!
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,'("This is ",A)') sexe 
#ifdef __DATE__
      WRITE (*,*) 'build date: ', __DATE__
#endif
#ifdef __TIME__
      WRITE (*,*) 'build time: ', __TIME__
#endif
      WRITE (*,*) 'Fortran compiler info: '
#ifdef unix
      WRITE (*,*) '   for unix'
#endif
#ifdef windows
      WRITE (*,*) '   for windows'
#endif
#ifdef linux
      WRITE (*,*) '   for linux'
#endif
#ifdef __APPLE__
      WRITE (*,*) '   for MAC OS X' 
#endif
#ifdef __INTEL_COMPILER
      WRITE (*,*) '   Intel compiler version: ', 
     1  __INTEL_COMPILER
#endif
#ifdef __INTEL_COMPILER_BUILD_DATE
      WRITE (*,*) 
     1'   Intel compiler build date: ',
     2  __INTEL_COMPILER_BUILD_DATE
#endif
#ifdef __GFORTRAN__
      WRITE (*,*) '   gfortran v',__VERSION__
#endif
#ifdef __G95__
      WRITE (*,*) '   g95 v',__G95__,__G95_MINOR__
#endif
      end subroutine sinfo

      subroutine helpout()
!     readptf short info
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,*) 'Two obligatory command line arguments:      '
      WRITE (*,*) '1: plot file filename                       '
      WRITE (*,*) '2: variable name  or                        '
      WRITE (*,*) '   varindex     or                          '
      WRITE (*,*) '   list - time - sp - index - check         '
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,*) 'Optional parameters for "variable name":    '
      WRITE (*,*) '3: (integer) 0 - time not in output         '
      WRITE (*,*) '             1 - time in the first column,  '
      WRITE (*,*) '                 (default)                  '
      WRITE (*,*) '             2 - time max min imax imin     '
      WRITE (*,*) '             3 - like 2 but min>0.0         '
      WRITE (*,*) '             4 - time sum                   '
      WRITE (*,*) '             5 - variable indexes           '
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,*) 'for varindex:                               '
      WRITE (*,*) '     the third argument is obligatory,      '
      WRITE (*,*) '     followed by at least one variable index'
      WRITE (*,*) '     (integer value)                        '
      WRITE (*,*) '     up to 1000 indexes is accepted         '
      WRITE (*,*) '                                            '
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,*) 'Output:                                     '
      WRITE (*,*) '   variable: (TIME) value (value ... )      '
      WRITE (*,*) '   varindex: (TIME) value (value ... )      '
      WRITE (*,*) '   list:     variable list                  '
      WRITE (*,*) '   index:    MELCOR variable indexes        '
      WRITE (*,*) '   time:     TIME DT CPU CYCLE              '
      WRITE (*,*) '   sp:       72 characters following .SP/   '
      WRITE (*,*) '   check:    miscelaneous info              '
      WRITE (*,*) '                                            '
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,*) 'Note:                                       '
      WRITE (*,*) '      variable name can be followed by      '
      WRITE (*,*) '      dot                                   '
      WRITE (*,*) '      and (volume) index                    '
      WRITE (*,*) '--------------------------------------------'
      WRITE (*,*) 'Note:                                       '
      WRITE (*,*) '      variable name which includes          '
      WRITE (*,*) '      brackets ()                           '
      WRITE (*,*) '      should be protected in quotes         '
      WRITE (*,*) '--------------------------------------------'
      return
      end subroutine helpout

      subroutine scheck1(STIME,NCYCLE,NRECT,NKEYT)
      INTEGER, PARAMETER   :: KIND_PLOT=SELECTED_REAL_KIND(6)
      REAL(KIND=KIND_PLOT) :: STIME
      integer NCYCLE,NRECT,NKEYT
      write(*,*) "KEY reset after time ",STIME,"cycle",NCYCLE
      write(*,*) "    NRECT = ", NRECT, 
     +" (total number of real values in the time record)"
      write(*,*) "    NKEYT = ", NKEYT, 
     +" (total number of variables)"
      return
      end subroutine scheck1

      subroutine scheck2(iTitl,iKey,iTR,iSP)
      integer iTitl,iKey,iTR,iSP
      write(*,*) "*********************************"
      write(*,*) "TITL was found ", iTitl, " times"
      write(*,*) "KEY was found ", iKey, " times"
      write(*,*) "TR was found ", iTR, 
     +" times (= number of time records)"
      write(*,*) "SP was found ", iSP, " times"
      write(*,*) "*********************************"       
      return
      end subroutine scheck2

      subroutine sGetSVOUTid()
!     local variables
      integer i,j,iL1,iL2,iLT,iLS,iK
      integer iL(LEN(SVOUT))
      integer iFound      
!      CHARACTER*24 SAUX
!      CHARACTER*24 SVOUT1
      CHARACTER*100 SAUX
      CHARACTER*100 SVOUT1      
!     code
      iLT=LEN_TRIM(SVOUT)
!      write(*,*) iLT,LEN(SVOUT) 
      j=0
      do i=1,iLT
       if ((SVOUT(i:i).eq."#").or.(SVOUT(i:i).eq." ")) then
        j=j+1
        iL(j)=i
       end if
      end do
      if (iL(j).ne.iLT) then 
       j=j+1
       iL(j)=iLT+1
      end if
!      write(*,*) iL
      iL1=1
      do i=1,j
       iL2=iL(i)-1
       SVOUT1=SVOUT(iL1:iL2)
!       write(*,*) SVOUT1,SVOUT(iL1:iL2),iL1,iL2
       iFound=0
       iLS=LEN_TRIM(SVOUT1)
       if (SVOUT1(iLS:iLS).eq.".") then
        SAUX=SVOUT1(1:iLS-1) 
        iFound=fGetSVOUTidl(SAUX)
        if (iFound.eq.0) then 
          iFound=fGetSVOUTide(SAUX)
        endif
       else
         iFound=fGetSVOUTide(SVOUT1)
         if (iFound.eq.0) then 
          iFound=fGetSVOUTidl(SVOUT1)
         endif
       endif
       iL1=iL2+2
      enddo
      return
      end subroutine sGetSVOUTid

      subroutine sMaxMin()
!     local variables        
      REAL*8 dMax,dMin
      integer iMax,iMin,i
      dMax=-1.0D+39
      dMin=+1.0D+39
      iMax=0
      iMin=0
      DO i=1,nddo
       IF (D(iddo(i)).GT.dMax) THEN 
        dMax=D(iddo(i))
        iMax=i
       ENDIF
       IF (D(iddo(i)).LT.dMin) THEN 
        IF ((iOpt.EQ.2).OR.(D(iddo(i)).GT.0.0)) THEN
         dMin=D(iddo(i))
         iMin=i
        ENDIF
       ENDIF
      ENDDO
      IF (iMin.EQ.0) dMin=0.0
      WRITE (*,27) STIME,dMax,dMin,iMax,iMin
 27   FORMAT(G15.9E2,G16.9E2,G16.9E2,I5,I5)
      return
      end subroutine sMaxMin

!     13.4.2018 broken pipe error handling: subroutine -> function       
      integer function fOutData()
!     local variables
      integer i
      IF (iOpt.EQ.1) WRITE(*,'(G15.9E2)',ADVANCE='NO',ERR=33) STIME
      DO i=1,nddo
       WRITE(*,'(1X,G15.9E2)',ADVANCE='NO',ERR=33) D(iddo(i))
      ENDDO
      WRITE(*,'("")',ERR=33)
      fOutData=1
      return 
 33   continue
      fOutData=0
      return      
      end function fOutData

      subroutine sOutIndex(SVOUT,RETITL,NKEYT,SVAR,ID,IDD,SUNIT)
!     arguments
      CHARACTER(LEN = *) SVOUT
      CHARACTER(LEN = *) RETITL
      integer NKEYT
      CHARACTER(LEN = *) SVAR(*)
      INTEGER      ID(*)
      INTEGER      IDD(*)
      CHARACTER(LEN = *) SUNIT(*)       
!     local variables
      integer i,ii,j,k,l
      integer, parameter :: m = 10
!     code
      IF (SVOUT.EQ.'list') then
       WRITE(*,*) TRIM(RETITL)
       DO i=1,NKEYT
        WRITE(*,*) i,SVAR(i),ID(i),SUNIT(i)
       ENDDO
      elseif (SVOUT.EQ.'index') then
       DO i=1,NKEYT
        WRITE(*,*) SVAR(i)
        l=ID(i+1)-1
        do ii=ID(i),l,m
         k=ii+m-1
         if (k.gt.l) k=l 
         WRITE(*,*) (IDD(j),j=ii,k)
        enddo
        WRITE(*,*) "*"
       ENDDO
!       WRITE(*,*) (IDD(j),j=i,ID(NKEYT))
!       WRITE(*,*) IDD(ID(NKEYT)),ID(NKEYT),NKEYT,NRECT
      end if
      return 
      end subroutine sOutIndex

      subroutine sReadList (NOUP,NKEYT,NRECT,SVAR,ID,SUNIT,IDD)
!     subroutine arguments
!       input argument
      integer :: NOUP
!       output 
      integer :: NKEYT
      integer :: NRECT
      CHARACTER(LEN = *) :: SVAR(*)
      INTEGER    ::  ID(*)
      CHARACTER(LEN = *) :: SUNIT(*)
      INTEGER :: IDD(*)
!     auxiliary local variables
      integer i
!     subroutine code
      NRECT=-1
!170130  READ(NOUP,ERR=33,END=33) NKEYT
!170130  on error continue: NRECT may not be present when the plotfile was produced by previous tranptf version
      READ(NOUP,ERR=35,END=33) NKEYT,NRECT
 35   continue
      if (NKEYT+1.gt.mvar) then
       write(*,*) "Too many variables", NKEYT 
       write(*,*) "Increase parameter mvar in globals.f", mvar
       write(*,*) "and recompile readptf"
       return
      endif
      READ(NOUP,ERR=33,END=38) (SVAR(i),i=1,NKEYT)
      READ(NOUP,ERR=33,END=38) (ID(i),i=1,NKEYT)
      READ(NOUP,ERR=33,END=38) (SUNIT(i),i=1,NKEYT)
      if (NRECT.eq.-1) then
       NRECT=ID(NKEYT)
      end if
      READ(NOUP,ERR=33,END=38) (IDD(i),i=1,NRECT)
!      add value to ID(NKEYT+1) to simplify later loops               
      ID(NKEYT+1)=NRECT+1      
 33   continue
 38   continue
      return
      end subroutine sReadList

!170130      subroutine sWriteList(NOUP,NKEYT,SVAR,ID,SUNIT,IDD)
      subroutine sWriteList(NOUP,NKEYT,NRECT,SVAR,ID,SUNIT,IDD)      
!     subroutine input arguments
      integer NOUP
      integer NKEYT
!170130 added parameter      
      integer NRECT
      CHARACTER(LEN = *) SVAR(*)
      INTEGER      ID(*)
      CHARACTER*16 SUNIT(*)
      INTEGER      IDD(*)
!     auxiliary local variables
      integer i
!     subroutine code
!170130     write(NOUP,ERR=33) NKEYT
      write(NOUP,ERR=33) NKEYT,NRECT       
      write(NOUP,ERR=33) (SVAR(i),i=1,NKEYT)
      write(NOUP,ERR=33) (ID(i),i=1,NKEYT)
      write(NOUP,ERR=33) (SUNIT(i),i=1,NKEYT)
!170221      write(NOUP,ERR=33) (IDD(i),i=1,ID(NKEYT))
      write(NOUP,ERR=33) (IDD(i),i=1,NRECT)
 33   continue
      return 
      end subroutine sWriteList

      subroutine sSum()
!     local variables        
      REAL*8 dSum
      integer i
      dSum=0.0
      DO i=1,nddo
       dSum=dSum+D(iddo(i))
      ENDDO
      WRITE(*,*) STIME, dSum
      return 
      end subroutine sSum

      end module readptfmod

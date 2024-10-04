      PROGRAM READPTF
!
!     Reads MELCOR 1.8.6 binary plot file
!     and writes requested data to stdout
!
!     written by Petr Vokac, UJV Rez, a.s.
!     10.7.2008,
!     using pieces of source code from MELCOR 1.8.6.      
!
!-----------------------------------------------
!
!     revision 27.12.2011
!     split main.f into functions and subroutines
!    
!     tested with g95, gfortran, ifort
!-----------------------------------------------
!
!     revision 28.12.2011
!     backup old sources to readptf.111228
!     created iddo()
!-----------------------------------------------
!
!     revision 26.9.2015
!     backup old sources to readptf-140825
!     support for names of CVH volume names
!     removed global variables subroutine arguments
!-----------------------------------------------
!
!     revision february 2017
!     read  NKEYT and NRECT in one READ statement:    
!     READ(NOUP,ERR=33,END=33) NKEYT,NRECT
!      
!     corresponding changes to write statement for tranptf         
!
!     Note: plotfiles transformed using previous versions of tranptf
!           are still readable by new readptf version.
!           See also comments in subroutine sReadList.
!      
      use globals
      use readptfmod
      IMPLICIT NONE
      CHARACTER*4 aux1,aux2
      CHARACTER*24 aux24
      INTEGER iaux1, iaux2
!     initialize variables
      call initglobals()
!     read command line arguments
      if (fGetArgs().eq.0) GOTO 900
!      open melptf      
      OPEN(IUNIT,FILE=FNAME,STATUS=FSTAT,FORM=FFORM,ERR=901,IOSTAT=IOS,ACTION='READ')
      NOUP=IUNIT
!      main cycle - label 24
 24   CONTINUE
      READ(NOUP,ERR=33,END=38) BTYPE
      IF(BTYPE.EQ.'.TR/') THEN
       if (iTR.eq.0) then
        nddo=0
        call sGetSVOUTid()
        if (iOpt.eq.5) then
         write(*,*) "Key: ", iKey  
         write(*,*) (iddo(I),I=1,nddo)
         write(*,*) "*"
        endif
        IF (SVOUT.EQ.'check') call scheck1(STIME,NCYCLE,NRECT,NKEYT)
       endif
       IF ((SVOUT.EQ.'list').OR.(SVOUT.EQ.'index')) THEN 
        call sOutIndex(SVOUT,RETITL,NKEYT,SVAR,ID,IDD,SUNIT)
        GO TO 38
       ENDIF
!       sp section is only at the beginning of the melptf ?
       if (SVOUT.EQ.'sp') GO TO 38
       READ(NOUP,ERR=33,END=33) STIME,SDT,SCPU,NCYCLE,(D(I),I=1,NRECT)
       iTR=iTR+1
       if (iOpt.eq.5) GO TO 24
       IF (SVOUT.EQ.'time') THEN
        WRITE(*,*) STIME,SDT,SCPU,NCYCLE
        GO TO 24
       endif
       if (SVOUT.eq.'check') goto 24
       IF (nddo.eq.0) goto 24
       IF ((iOpt.EQ.2).OR.(iOpt.EQ.3)) THEN
        call sMaxMin()
       ELSE
        IF (iOpt.EQ.4) THEN
         call sSum()
        ELSE
         if (fOutData().eq.0) goto 38
        ENDIF
       ENDIF 
       GO TO 24       
      endif
      IF(BTYPE.EQ.'.SP/') THEN
       READ(NOUP,ERR=33,END=33) SAUXA
       iSP=iSP+1
       call fIsSPName(SAUXA)
       IF (SVOUT.EQ.'sp') WRITE(*,*) SAUXA
       GO TO 24
      endif
      IF(BTYPE.NE.PTYPE) THEN 
       if (SVOUT.EQ.'check') write(*,*) 'BTYPE.NE.PTYPE',BTYPE  
       GO TO 24
      endif
!      BTYPE.EQ.PTYPE read BTYPE again      
      READ(NOUP,ERR=33,END=33) BTYPE
      IF (BTYPE.EQ.'KEY ') THEN
       call sReadList(NOUP,NKEYT,NRECT,SVAR,ID,SUNIT,IDD)
       if (NKEYT+1.gt.mvar) go to 38  
       iKey=iKey+1
       BTYPEO='KEY '
      ENDIF
      IF(BTYPE.EQ.'TITL') THEN
       READ(NOUP,ERR=33,END=33) RETITL
       iTitl=iTitl+1
       IF (SVOUT.EQ.'check') THEN
        write(*,*) "TITL=",TRIM(RETITL)
       endif
      ENDIF
      GO TO 24
!      end of the main cycle - label 24
 33   CONTINUE
      WRITE(*,*) "File:", FNAME
      WRITE(*,*) "Error reading the file or" 
      WRITE(*,*) "unexpected end of file encountered"
      GO TO 900
 38   CONTINUE
      CLOSE(IUNIT)
      GO TO 900
 901  CONTINUE
      WRITE(*,'("Error opening file: ",A)') FNAME
 900  CONTINUE
      IF (SVOUT.EQ.'check') call scheck2(iTitl,iKey,iTR,iSP)
      if (SVOUT.EQ.'names') call fPrintSPNames()
      END PROGRAM READPTF


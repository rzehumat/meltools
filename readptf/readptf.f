      PROGRAME READPTF
C
C     Reads MELCOR 1.8.6 binary plot file
C     and writes requested data to stdout
C
C     written by Petr Vokac, UJV Rez, a.s.
C     10.7.2008,
C     using pieces of source code from MELCOR 1.8.6.      
C
C-----------------------------------------------
C
C     revision 27.12.2011
C     split main.f into functions and subroutines
C    
c     tested with g95, gfortran, ifort
C-----------------------------------------------
C
C     revision 28.12.2011
C     backup old sources to readptf.111228
C     created iddo()
C-----------------------------------------------
C
C     revision 26.9.2015
C     backup old sources to readptf-140825
C     support for names of CVH volume names
C     removed global variables subroutine arguments
C-----------------------------------------------
C
C     revision february 2017
C     read  NKEYT and NRECT in one READ statement:    
C     READ(NOUP,ERR=33,END=33) NKEYT,NRECT
C      
C     corresponding changes to write statement for tranptf         
C
C     Note: plotfiles transformed using previous versions of tranptf
C           are still readable by new readptf version.
C           See also comments in subroutine sReadList.
C      
      use globals
      use readptfmod
      IMPLICIT NONE
      CHARACTER*4 aux1,aux2
      CHARACTER*24 aux24
      INTEGER iaux1, iaux2
c     initialize variables
      call initglobals()
c     read command line arguments
      if (fGetArgs().eq.0) GOTO 900
c      open melptf      
      OPEN(IUNIT,FILE=FNAME,STATUS=FSTAT,FORM=FFORM,ERR=901,
     +       IOSTAT=IOS,ACTION='READ')
      NOUP=IUNIT
c      main cycle - label 24
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
        IF (SVOUT.EQ.'check') 
     +      call scheck1(STIME,NCYCLE,NRECT,NKEYT)
       endif
       IF ((SVOUT.EQ.'list').OR.(SVOUT.EQ.'index')) THEN 
        call sOutIndex(SVOUT,RETITL,NKEYT,SVAR,ID,IDD,SUNIT)
        GO TO 38
       ENDIF
c       sp section is only at the beginning of the melptf ?
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
c      BTYPE.EQ.PTYPE read BTYPE again      
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
c      end of the main cycle - label 24
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
      END PROGRAME READPTF


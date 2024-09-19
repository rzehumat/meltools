      module globals
      implicit none
c     maximum dimension of the output vector
      integer, parameter :: mddo=10000
c     maximum number of variable names
      integer, parameter :: mvar=10000
c     maximum dimension of the input vector 
      integer, parameter :: md=500000
c     output index of variables, created 29.12.2011
      integer :: nddo
      integer :: iddo(mddo)
c      input file (melptf) handling 
      INTEGER IUNIT,IOS,NOUP
      CHARACTER*250 FNAME
      CHARACTER*50 FSTAT,FFORM
      integer NKEYT,NRECT,NCYCLE 
c      list of variables
      CHARACTER*24 SVAR(mvar)
      INTEGER      ID(mvar)
      CHARACTER*16 SUNIT(mvar)
c      simulation title
      CHARACTER*110 RETITL
c      data type selectors in melptf
      CHARACTER*4 BTYPE,PTYPE,BTYPEO
      DATA PTYPE/'./*/'/
c      real data from melptf
      INTEGER, PARAMETER   :: KIND_PLOT=SELECTED_REAL_KIND(6)
      REAL(KIND=KIND_PLOT) :: STIME,SDT,SCPU
      REAL(KIND=KIND_PLOT) :: D(md)
c      definition of the output vector D(IDD(i))
      INTEGER      IDD(md)
c      auxiliary variables      
      integer i
      CHARACTER*10000 SVOUT ! 15.5.2012 increased to accomodate large number of variables
      CHARACTER*72 SAUXA
      INTEGER iOpt
c      melptf accounting variables
      integer iTitl,iKey,iTR,iSP
c      object names, added 16.9.2015    
      CHARACTER*16 sCvhVolumeName(mvar) 
      integer nCvhVolumeName
      CHARACTER*16 sFlPathName(mvar) 
      integer nFlPathName

      contains 

      subroutine initglobals()
      nCvhVolumeName=0
      nFlPathName=0
      FSTAT='OLD'
      FFORM='UNFORMATTED'
      IOS=0
      IUNIT=1
      iOpt=1
      nddo=0
      iTitl=0
      iTR=0
      iSP=0
      iKey=0
      STIME=-1.0
      NCYCLE=-1
      BTYPEO=''
      end subroutine initglobals

      end module globals


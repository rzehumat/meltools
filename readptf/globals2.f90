!     8.1.2019 mvar increased to 100000
      module globals
      implicit none
!     maximum dimension of the output vector
      integer, parameter :: mddo=100000
!     maximum number of variable names
      integer, parameter :: mvar=100000
!     maximum dimension of the input vector 
      integer, parameter :: md=500000
!     output index of variables, created 29.12.2011
      integer :: nddo
      integer :: iddo(mddo)
!      
!     12.2.2021 tested on PWR_v2-0.PTF
!     variable length of SVAR, I do not know to find its value
!     at run time      
!     value 28 currently works with:
!     MELCOR-2.2.18019/testing/gendist_test_cases_2.2.18019/Linux
!            PWR/PWR_v2-0.PTF
!            
      integer, parameter :: lsvar=28
!     note that dependent files should be recompiled
!     when module is changed
!      
!     input file (melptf) handling      
      INTEGER IUNIT,IOS,NOUP
      CHARACTER*250 FNAME
      CHARACTER*50 FSTAT,FFORM
      integer NKEYT,NRECT,NCYCLE 
!      list of variables
      CHARACTER(LEN=lsvar) :: SVAR(mvar)
      INTEGER      ID(mvar)
      CHARACTER(LEN=16) :: SUNIT(mvar)
!      simulation title
      CHARACTER*110 RETITL
!      data type selectors in melptf
      CHARACTER*4 BTYPE,PTYPE,BTYPEO
      DATA PTYPE/'./*/'/
!      real data from melptf
      INTEGER, PARAMETER   :: KIND_PLOT=SELECTED_REAL_KIND(6)
      REAL(KIND=KIND_PLOT) :: STIME,SDT,SCPU
      REAL(KIND=KIND_PLOT) :: D(md)
!      definition of the output vector D(IDD(i))
      INTEGER      IDD(md)
!      auxiliary variables      
      integer i
      CHARACTER*10000 SVOUT ! 15.5.2012 increased to accomodate large number of variables
      CHARACTER*72 SAUXA
      INTEGER iOpt
!      melptf accounting variables
      integer iTitl,iKey,iTR,iSP
!      object names, added 16.9.2015    
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


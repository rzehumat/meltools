      module tranptfvar
      implicit none
c     maximum number of variable names
      integer, parameter :: mvaro=10000
c     maximum number of indexes
      integer, parameter :: mdo=500000
c     list of variables
      integer nvarreq            
      CHARACTER*24 SVARREQ(mvaro) 
      integer nvarout            
      CHARACTER*24 SVAROUT(mvaro) 
      INTEGER      IDOUT(mvaro)
      CHARACTER*16 SUNITOUT(mvaro)
      INTEGER      IDDOUT(mdo)
      integer      iddd(mdo) ! list of indexes to output

      contains

      subroutine sFiltVars(NKEYT,SVAR,ID,SUNIT,IDD,ivo,nid)
c      needs scalar as the last variable, no longer needed but let it be for now 21.2.2017  
      integer NKEYT
      CHARACTER*24 SVAR(*)
      INTEGER      ID(*)
      CHARACTER*16 SUNIT(*)
      INTEGER      IDD(*)
      integer ivo, nid
      integer iddlast,idolast
      integer ivreq,ivi,ii,iii     
      integer iFound
      ivo=0     ! new value of NKEYT
      idolast=0 ! index of the last output variable
      nid=0     ! the last index of the iddd array
      iddlast=1 ! dimension of the last output variable
      do ivreq=1,nvarreq 
       iFound=0
       do ivi=1,NKEYT
        if (SVARREQ(ivreq).eq.SVAR(ivi)) then
         ivo=ivo+1
         SVAROUT(ivo)=SVAR(ivi)
         SUNITOUT(ivo)=SUNIT(ivi)
         IDOUT(ivo)=idolast+iddlast
         iddlast=ID(ivi+1)-ID(ivi)
         idolast=IDOUT(ivo)
         iii=IDOUT(ivo)
         do ii=ID(ivi),ID(ivi+1)-1
          nid=nid+1
          iddd(nid)=ii
          IDDOUT(iii)=IDD(ii)
          iii=iii+1
         end do
         iFound=iddlast
        end if
       end do
       if (iFound.eq.0) then
        iii=LEN_TRIM(SVARREQ(ivreq))
        write (*,'("Requested variable: ", A ," not found!")') 
     +    SVARREQ(ivreq)(1:iii)
       end if
      end do
c 11.4.2018 allow to create melptf with vector last variable      
c      if (iFound.gt.1) then
c       iii=LEN_TRIM(SVARREQ(nvarreq))
c       write (*,'("The last requested variable should be scalar!")')
c       write (*,'("Variable: ", A, " would not be accesible!")') 
c     +    SVARREQ(nvarreq)(1:iii)
c       write (*,'("Transformation canceled")')
c       stop
c      end if
      end subroutine sFiltVars

      subroutine sReadVar(svarfile)
      character*20 svarfile
      integer i,IUNIT
      character*24 saux
      i=0
      OPEN(IUNIT,FILE=svarfile,ACTION='READ',STATUS='OLD',ERR=998)
 1    continue
      read(IUNIT,END=996, ERR=997,FMT="(A)") saux
      i=i+1
      SVARREQ(i)=saux
      goto 1
 996  continue
      close(IUNIT)
      goto 999
 997  continue 
      WRITE(*,'("Error reading file: ",A)') svarfile
      goto 999
 998  continue
      WRITE(*,'("Error opening file: ",A)') svarfile
 999  continue
      nvarreq=i
      return
      end subroutine sReadVar

      subroutine sPrintVar()
      integer i
      do i=1,nvarreq
       write(*,*) SVARREQ(i)
      end do
      return
      end subroutine sPrintVar

      end module tranptfvar

      module tranptfmod
      implicit none
! global variables from the input configuration file 
!      11.4.2012 stitle should be the same size as RETITL      
!      2.8.2012 increase dimension of smelptfi to 250
!      25.8.2014 dtmin to allow filter out records from BURN
!                modified input check
!                some comments
      character*110 stitle 
      integer, parameter :: mptf=20 
      character*250 smelptfi(mptf)
      character*20 svarlist
      character*20 smelptfo
      integer inrpd
      character*20 sstarttime(mptf)      
      character*20 sendtime(mptf)      
      integer ievery(mptf) ! 14.5.2012 take only every i-th record
      character*20 sdtmin(mptf)      
      contains
      
      subroutine inputread(sinput)
! reads input parameters from the configuration file 
      namelist /input/ stitle,smelptfi,svarlist,smelptfo,inrpd,
     + sstarttime,sendtime,ievery,sdtmin
      integer i,IUNIT
      character*250 sinput
      stitle=""
      do i=1,mptf
       smelptfi(i)=""
       sstarttime(i)=""
       sendtime(i)=""
       ievery(i)=1
       sdtmin(i)=""
      enddo
      svarlist=""
      smelptfo=""
      inrpd=1
      OPEN(IUNIT,FILE=sinput,ACTION='READ')
      read(IUNIT,input,END=999, ERR=999)
      close(IUNIT) 
 999  continue
      return 
      end subroutine inputread

      subroutine inputout()
! check input parameters
      integer i,j
      write(*,"('------------ Input check ------------------------')") 
      write(*,"('Title: ', A)") stitle
      do i=1,mptf
       if (len_trim(smelptfi(i)).gt.0) then
        j=len_trim(smelptfi(i))
        write(*,"('Input file ',I2,' : ',A,' start: ',A,
     +         ' end: ', A,' every: ', I2,' dtmin: ',A)") 
     +        i, trim(smelptfi(i)),trim(sstarttime(i)),
     +        trim(sendtime(i)),ievery(i),trim(sdtmin(i))
       endif
      enddo
      write(*,"('Output file : ',A)") smelptfo
      write(*,"('Variable list : ',A)") svarlist 
      write(*,"('Records per dot : ',I3)") inrpd 
      write(*,"('------------ Input check end --------------------')") 
      return 
      end subroutine inputout

      subroutine transfile(iinp,iuout)
! do the transformation for all the input files
      use globals
      use readptfmod, only: sReadList, sWriteList
      use tranptfvar
      integer iinp,iuout,ir,iev
!      integer ivreq,ivo,ivi,idlast
!      integer idolast,ii,iii,nid
      integer ivo,nid
      integer ior ! 12.5.2017: ior==1 write output record, ior==-1 skip rest of the input file     
!     initialize variables
      call initglobals()
      nid=0
      ir=0
      iev=0
      FNAME=smelptfi(iinp)
      write(*,FMT='("Processing file: ", A, " : ")') trim(FNAME)
      OPEN(IUNIT,FILE=FNAME,STATUS=FSTAT,FORM=FFORM,ERR=901,
     +       IOSTAT=IOS,ACTION='READ')
      NOUP=IUNIT
!      main cycle - label 24
 24   CONTINUE
      READ(NOUP,ERR=33,END=38) BTYPE
      IF(BTYPE.EQ.'.TR/') THEN
       READ(NOUP,ERR=33,END=38) STIME,SDT,SCPU,NCYCLE,(D(I),I=1,NRECT)
       ior=fOutRec(iinp,STIME)  
       if ( 0.lt.ior ) then
        iev=iev+1
        if (iev.ge.ievery(iinp)) then 
         write(iuout,ERR=34) BTYPE 
         if (nid.eq.0) then 
          write(iuout,ERR=34) STIME,SDT,SCPU,NCYCLE,(D(I),I=1,NRECT)
         else
          write(iuout,ERR=34) STIME,SDT,SCPU,NCYCLE,(D(iddd(I)),I=1,nid) 
         end if
         ir=ir+1
         if ((ir.ge.inrpd).or.(ievery(iinp).gt.1)) then
          write(*,ADVANCE='NO',FMT='(".")') 
          flush(iuout)
          ir=0
         end if
         iev=0
        else
         write(*,ADVANCE='NO',FMT='("x")')
        end if
       else
         if (ior.eq.0) then
          write(*,ADVANCE='NO',FMT='("x")')
         else
          write(*,ADVANCE='NO',FMT='(" skipped rest of the file ")')
          GO TO 38              !12.5.2017 ior==-1
         endif 
       end if
      else
       write(iuout,ERR=34) BTYPE
      endif
      IF(BTYPE.EQ.'.SP/') THEN
       READ(NOUP,ERR=33,END=38) SAUXA
       write(iuout,ERR=34) SAUXA
      endif
      IF(BTYPE.NE.PTYPE) THEN 
       GO TO 24
      endif
      READ(NOUP,ERR=33,END=38) BTYPE
      write(iuout,ERR=34) BTYPE
      IF (BTYPE.EQ.'KEY ') THEN
       call sReadList (NOUP,NKEYT,NRECT,SVAR,ID,SUNIT,IDD)
       if (svarlist.eq."") then 
!     170130        call sWriteList (iuout,NKEYT,SVAR,ID,SUNIT,IDD)
        call sWriteList(iuout,NKEYT,NRECT,SVAR,ID,SUNIT,IDD)
       else
        call sFiltVars(NKEYT,SVAR,ID,SUNIT,IDD,ivo,nid)
!     170130        call sWriteList (iuout,ivo,SVAROUT,IDOUT,SUNITOUT,IDDOUT)
        call sWriteList(iuout,ivo,nid,SVAROUT,IDOUT,SUNITOUT,IDDOUT)
       end if 
      ENDIF
      IF(BTYPE.EQ.'TITL') THEN
       READ(NOUP,ERR=33,END=38) RETITL
!       11.4.2012 
       if (stitle.ne."") RETITL=stitle
       write(iuout,ERR=34) RETITL
      ENDIF
      GO TO 24
 34   continue
      WRITE(*,'("Error writing to output")')
 33   continue
      WRITE(*,'("Error reading file: ",A)')  FNAME
 38   continue
      CLOSE(IUNIT)
      write(*,*) ""
      GO TO 900
 901  CONTINUE
      WRITE(*,'("Error opening file: ",A)')  FNAME
 900  CONTINUE
      return
      end subroutine transfile

      integer function fOutRec(i,x)
!      checks whether to output current record or not
!      real data from melptf
      INTEGER, PARAMETER   :: KIND_PLOT=SELECTED_REAL_KIND(6)
      integer :: i,ifirst
      REAL(KIND=KIND_PLOT) :: x
      integer iRet
      real xt,xp,dtmin
      save ifirst, xp ! xp is time of the previous record in the output
      data ifirst /1/
      iRet = 1
      if (sstarttime(i).ne."") then 
       read(sstarttime(i),*) xt
!       write(*,*) xt,x
       if (xt.gt.x) iRet = 0
      end if 
      if (sendtime(i).ne."") then 
       read(sendtime(i),*) xt
       if (xt.lt.x) iRet = -1 ! 12.5.2017: return -1 when sendtime is exceeded
      end if 
      if (ifirst.eq.1) then
       ifirst=0 
       xp=x
      else
       if (x.lt.xp) then
        iRet=0
! debug print         write (*,*) "record refused:",x,xp
       else 
! 25.8.2014 check dtmin        
        if (sdtmin(i).ne."") then
         read(sdtmin(i),*) dtmin
         if ((x-xp).lt.dtmin) iRet=0
        end if
       end if
      end if
! 2.4.2012 if the record is not for output, keep the previous last time
! 25.8.2014 put this at the end 
      if (iRet.eq.1) xp=x
      fOutRec=iRet
      return
      end function fOutRec

      subroutine transfallfiles()
! do the transformation for all the input files
      integer i,iuout
      iuout=0
      OPEN(iuout,FILE=smelptfo,STATUS='NEW',
     +       FORM='UNFORMATTED',ERR=901,
     +       ACTION='WRITE')

      do i=1,mptf
       if (len_trim(smelptfi(i)).gt.0) then
        call transfile(i,iuout)
       endif
      enddo      
      close(iuout)
      goto 902
 901  continue
      WRITE(*,'("Error creating new file: ",A)')  smelptfo
 902  continue
      WRITE(*,'("tranptf finished")')
      return
      end subroutine transfallfiles
      end module tranptfmod

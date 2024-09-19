       program fjr

       use json_module

       implicit none

       type(json_file) :: json
       logical :: found
       integer :: i,j,k
       real(json_rk), dimension(:), allocatable :: rArray
       character(len=*), parameter :: &
       filename = "example.json"

       ! initialize the class
       call json%initialize()

       ! read the file
       call json%load_file(filename)

       ! print the file to the console
       call json%print_file()

       ! extract data from the file
       ! [found can be used to check if the data was really there]
       call json%get('inputs.integer_scalar', i, found)
       write(*,*) "inputs.integer_scalar is now i =", i
       if ( .not. found ) stop 1
       call json%get('inputs.float_vector', rArray, found)
       if ( .not. found ) then
        write(*,*) "inputs.float_vector not found in the file"
        stop 1
       else
        write(*,*) "rArray=",rArray
       endif
       call json%get('inputs.k', k, found)
       if ( .not. found ) then
        write(*,*) "inputs.k not found in the file"
        stop 1
       else
        write(*,*) "k=",k 
       endif
       call json%get('inputs.pydata.number', j, found)
       if ( .not. found ) then
        write(*,*) "inputs.pydata.number not found in the file"
        stop 1
       else
        write(*,*) "j=",j 
       endif
       ! clean up
       call json%destroy()
       if (json%failed()) stop 1

       end program fjr
      

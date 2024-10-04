# tests of JSON fortran 
# libraries needed: FoBiS-2.2.8, json-fortran-6.1.0

ALL: fjw.o fjw fjr.o fjr

GCF=-c -O2 -fbacktrace -Wall -Wextra -Wno-maybe-uninitialized -Wno-unused-function -pedantic -std=f2008 -fno-omit-frame-pointer -ffree-form 

fjw.o: fjw.f90
	gfortran -I ../json-fortran-6.1.0/lib/ $(GCF) fjw.f90 

fjw: fjw.o
	gfortran -L ../json-fortran-6.1.0/lib/ -o fjw fjw.o -ljsonfortran

fjr.o: fjr.f90
	gfortran -I ../json-fortran-6.1.0/lib/ $(GCF) fjr.f90

fjr: fjr.o
	gfortran -L ../json-fortran-6.1.0/lib/ -o fjr fjr.o -ljsonfortran

clean:
	rm -f *~ *.o example.json fjw fjr 

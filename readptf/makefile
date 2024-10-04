#
SHELL=/bin/sh
#
# Fortran compiler and compilation flags
#
#FCOMPL=g95
FCOMPL=gfortran
FFLAGC=-O2 -cpp 
##with ifort use the same flags as for optimised MELCOR 1.8.6
#FCOMPL=ifort
#FFLAGC=-u -save -w -i-static -check nooutput_conversion -align all -real-size 64 -zero -common-args -O1 -D PRECISION_64 -D ARCH_INT -fpp
#
#
OBJR = globals.o readptfmod.o readptf.o 

OBJT = globals.o tranptfvar.o tranptfaux.o readptfmod.o tranptfmod.o tranptf.o

readptf = readptf.exe
tranptf = tranptf.exe

all: $(readptf) $(tranptf)

$(readptf): $(OBJR) 
	$(FCOMPL) -o $(readptf) $(OBJR)

$(tranptf): $(OBJT) 
	$(FCOMPL) -o $(tranptf) $(OBJT) 

%.o: %.f90
	$(FCOMPL) $(FFLAGC) -c $< -o $@

clean:
	rm -f *.o *.mod *~ $(readptf) $(tranptf)


all: goes-demod gen-syncword vcdu-channelize

clean:
	rm -f goes-demod gen-syncword vcdu-channelize

LIQUID=../../src/liquid-dsp
CORRECT=../../src/libcorrect
LIBS=-L$(LIQUID) -lliquid -L$(CORRECT) -lcorrect
INC=-I$(LIQUID)/include -I$(CORRECT)/include
CFLAGS=-ggdb -Wall -O2 


goes-demod: goes-demod.c
	gcc -o goes-demod goes-demod.c $(CFLAGS) $(LIBS) $(INC) 

gen-syncword: gen-syncword.c
	gcc -o gen-syncword gen-syncword.c $(CFLAGS) $(LIBS) $(INC) 

vcdu-channelize: vcdu-channelize.c
	gcc -o vcdu-channelize vcdu-channelize.c $(CFLAGS)


#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define N 892

/*
 * Split raw data file from goes-demod into virtual channels
 * Create one file in the channels folder for each channel
 */

int main(int argc, char **argv)
{
	if(argc != 2) {
		fprintf(stderr,"usage: ./vcdu-channelize <input file>\n");
		return 1;
	}
	const char *fn = argv[1];
	FILE *fin = fopen(fn,"rb");

	FILE *fout[64] = {NULL};

	uint8_t buf[N];
	while(fread(buf,N,1,fin) == 1) {
		int vcid = buf[1]&0x3f;
		if(vcid == 63) {
			continue;
		}
		if(fout[vcid] == NULL) {
			char fname[256];
			sprintf(fname,"channels/vcid%02d.raw",vcid);
			fout[vcid] = fopen(fname,"wb");
			if(fout[vcid] == NULL) {
				fprintf(stderr,"Error, could not open %s\n",fname);
			}
		}
		fwrite(&buf[6],N-6,1,fout[vcid]);
	}

	fclose(fin);
	for(int i=0;i<64;i++) {
		if(fout[i] != NULL) {
			fclose(fout[i]);
		}
	}
}

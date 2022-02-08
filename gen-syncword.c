
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include <correct.h>
#include <liquid.h>

/*
 * Generate the convolutionally and differentially encoded GOES syncwords.
 * Generate many instances with different random data enveloping the syncword, to see which bits are determinate and which are influenced by surrounding data.
 */

int main(void)
{
	uint16_t vpoly[2] = {0x4F,0x6D};
	correct_convolutional *correct_viterbi = correct_convolutional_create(2,7,vpoly);
	uint8_t inbuf[6] = {0x00,0x1A,0xCF,0xFC,0x1D,0x00};
	int noutbit = correct_convolutional_encode_len(correct_viterbi,6);
	int nout = noutbit / 8;
	uint8_t outbuf[14];
	uint8_t vbits[48];
	uint8_t dbits[48];
	uint8_t dbytes[6];

	uint32_t nw;
	int nmc = 1000;
	for(int i=0;i<nmc;i++) {
		inbuf[0] = rand() % 256;
		inbuf[5] = rand() % 256;

		liquid_unpack_bytes(inbuf,6,vbits,48,&nw);
		dbits[0] = 0;
		for(int j=1;j<48;j++) {
			dbits[j] = vbits[j] ^ dbits[j-1];
		}
		liquid_pack_bytes(dbits,48,dbytes,6,&nw);

		correct_convolutional_encode(correct_viterbi,dbytes,6,outbuf);

		
		for(int j=0;j<nout;j++) {
			printf("%02x ",outbuf[j]);
		}
		printf("\n");
		
		//fwrite(outbuf,14,1,stdout);
	}
	correct_convolutional_destroy(correct_viterbi);
}



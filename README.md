# goeshrit

February 7, 2022

These programs receive data from the GOES HRIT signals on L-band and extract the full disk images. I wrote this to learn about digital communications, with a goal of receiving a 24 hour sequence of images to produce an animation of sunrise through sunset across the full disk.

goes-demod reads complex float samples and does:
 * resampling input rate to twice the symbol rate
 * automatic gain control
 * BPSK symbol synchronization and decimation to the symbol rate
 * carrier recovery
 * synchronization word search through correlation
 * convolutional decode
 * differential decode
 * Reed Solomon decode
Valid reed solomon decodes are written to the output file.

vcdu-channelize splits out the virtual channels from the stream of bits provided by goes-demod. Each virtual channel is output to a separate file in a subfolder called channels.

pdu-assemble.py extracts the full disk images from the channels and saves them in png format. Szip is used to decompress the images via libaec.

There are more complete projects to receive images from GOES goestools and one in Open Satellite Project. I used these codes as references, in particular for the digital deframing of the image containing packets.

## RF hardware

To receive the L-band signal, I used a 39" x 24" 2.4 GHz wifi dish. I extended the secondary reflector further from the feed by 1", which improved the S11 at 1.7 GHz from about -6 dB to -12 dB. The antenna feeds a Nooelec Sawbird GOES LNA, powered over internal bias tee by an Airspy R2. This set up gave me an SNR of 4-5 in an open area, and 2.5-3 on my patio obscured by trees. Either was adequate for Reed Solomon error rates better than 1-2 bytes per 223/255 byte block.

## Dependencies
 * libcorrect
 * liquid-dsp
 * libaec
 * numpy
 * PIL

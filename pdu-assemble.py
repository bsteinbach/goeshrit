
import os,sys
import numpy as np
import crc16
import xritparse
import PIL.Image

fn = sys.argv[1]
x = np.fromfile(fn,dtype=np.uint8)

bs = 886
nb = x.size // bs
x = x.reshape((nb,bs))


fhp = x[:,1] + (x[:,0]&0x07)*256

#print(fhp.shape)
#print(fhp)

def tonum(mat):
	n = mat.shape[-1]
	return np.dot(mat,[2**(n-i-1) for i in range(n)])

class CCSDSHDR():
	def __init__(self,x):
		bits = np.unpackbits(x)
		self.version = tonum(bits[:3])
		self.type = bits[3]
		self.shf = bits[4]
		self.apid = tonum(bits[5:16])
		self.seqflag = tonum(bits[16:18])
		self.counter = tonum(bits[18:32])
		self.length = tonum(bits[32:48])+1

data = x[:,2:].flatten()
data = data[fhp[0]:]

streams = {}
i = 0
while i + 6 < len(data):
	hdr = CCSDSHDR(data[i:i+6])
	i += 6
	n = hdr.length
	if i + n >= len(data):
		break
	if hdr.apid == 2047:
		i += n
		continue
	if hdr.apid not in streams:
		streams[hdr.apid] = []
	chunk = data[i:i+n-2]
	#crc = data[i+n-2:i+n]
	#crc = crc[0]*256 + crc[1]
	#check = crc16.crc16(chunk)
	#print("%04x %04x"%(crc,check))
	#assert crc == check
	#print("%02x%02x"%(crc[0],crc[1]),"%04x"%check)

	streams[hdr.apid].append((hdr.seqflag,hdr.counter,chunk))
	i += n


'''
Rewrite this part so that each packet is one scan line
The first packet is big because it's the LRIT header
Then decompress one line at a time.
'''

filemap = {}
for k in streams:
	stream = streams[k]
	state = 0
	data = []
	for i in range(len(stream)):
		seqflag,counter,chunk = stream[i]
		try:
			if state == 0:
				if seqflag == 1:
					#print(seqflag,counter,chunk.size)
					headers = xritparse.XRITHeaders(chunk)
					state = 1
			elif state == 1:
				if seqflag == 0 or seqflag == 2:
					chunk = xritparse.rice_decomp(chunk,headers)
					data.append(chunk)
				if seqflag == 1:
					print("error, got bad seq flag")
					exit(1)
				if seqflag == 2:
					data = np.vstack(data)
					#fn = 'xrits/apid%04d_%02d.xrit'%(k,n)
					#data.tofile(fn)
					name = headers.anno.info
					if name not in filemap:
						img = np.zeros((headers.imageseg.nline,headers.struct.ncol),dtype=np.uint8)
						filemap[name] = img
					line0 = headers.imageseg.line0
					img = filemap[name]
					nline = data.shape[0]
					img[line0:line0+nline,:] = data
					data = []
					state = 0
		except:
			state = 0
			data = []

for k in filemap.keys():
	im = PIL.Image.fromarray(filemap[k])
	name = os.path.splitext(k)[0]+'.png'
	im.save(os.path.join('images',name))


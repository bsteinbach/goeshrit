
import os
import numpy as np

def tonumbyte(mat):
	n = mat.shape[-1]
	return np.dot(mat,[2**(8*(n-i-1)) for i in range(n)])

class XRITHeader():
	def __init__(self,data):
		self.type = data[0]
		self.hdrlen = tonumbyte(data[1:3])

class XRITPrimaryHeader(XRITHeader):
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 0
		assert self.hdrlen == 16
		self.file_type = data[3]
		self.total_len = tonumbyte(data[4:8])
		self.data_len = tonumbyte(data[8:16])
		'''
		print("file_type: ",self.file_type)
		print("total_len: ",self.total_len)
		print("data_len: ",self.data_len)
		'''

class XRITImageStructureHeader(XRITHeader):
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 1
		assert self.hdrlen == 9
		self.bpp = data[3]
		self.ncol = tonumbyte(data[4:6])
		self.nline = tonumbyte(data[6:8])
		self.compress = data[8]
		assert self.bpp == 8
		#print("bitsPerPixel: ",self.bpp)
		#print("ncol: ",self.ncol)
		#print("nline: ",self.nline)
		#print("compress: ",self.compress)

def tostr(x):
	return ''.join([chr(c) for c in x])

class XRITImageNavigationHeader(XRITHeader):
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 2
		assert self.hdrlen == 51
		self.projection = tostr(data[3:35])
		self.cfac = data[35:39]
		self.lfac = data[39:43]
		self.coff = data[43:47]
		self.loff = data[47:51]
		#print("projection: ",self.projection)

class XRITTextHeader():
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		self.info = tostr(data[3:self.hdrlen])

class XRITImageCompensationHeader():
	def __init__(self,data):
		XRITTextHeader.__init__(self,data)
		assert self.type == 130

class XRITImageDataFunctionHeader():
	def __init__(self,data):
		XRITTextHeader.__init__(self,data)
		assert self.type == 3

class XRITAnnotationHeader():
	def __init__(self,data):
		XRITTextHeader.__init__(self,data)
		assert self.type == 4
		#print("annotation: ",self.info)

class XRITAncillaryHeader():
	def __init__(self,data):
		XRITTextHeader.__init__(self,data)
		assert self.type == 6
		#print("ancillary: ",self.info)

class XRITTimeStampHeader():
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 5
		assert self.hdrlen == 10
		self.b1 = data[3]
		self.days = tonumbyte(data[4:6])
		self.millis = tonumbyte(data[6:10])
		#print(self.days,self.millis)

class XRITImageSegHeader():
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 128
		assert self.hdrlen == 17
		self.imageid = tonumbyte(data[3:5])
		self.seg = tonumbyte(data[5:7])
		self.col0 = tonumbyte(data[7:9])
		self.line0 = tonumbyte(data[9:11])
		self.nseg = tonumbyte(data[11:13])
		self.ncol = tonumbyte(data[13:15])
		self.nline = tonumbyte(data[15:17])
		#print("seq: %d / %d"%(self.seg,self.nseg))
		#print("col: %d / %d"%(self.col0,self.ncol))
		#print("line: %d / %d"%(self.line0,self.nline))

class XRITNOAALRITHeader():
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 129
		assert self.hdrlen == 14
		self.sig = tostr(data[3:7])
		self.prodid = tonumbyte(data[7:9])
		self.subid = tonumbyte(data[9:11])
		self.param = tonumbyte(data[11:13])
		self.compress = data[13]
		'''
		print("sig: ",self.sig)
		print("prodid: ",self.prodid)
		print("subid: ",self.subid)
		print("param: ",self.param)
		print("compress: ",self.compress)
		'''
	
ALLOW_K13_OPTION_MASK = 1
CHIP_OPTION_MASK = 2
EC_OPTION_MASK = 4
LSB_OPTION_MASK = 8
MSB_OPTION_MASK = 16
NN_OPTION_MASK = 32
RAW_OPTION_MASK = 128

class XRITRiceHeader():
	def __init__(self,data):
		XRITHeader.__init__(self,data)
		assert self.type == 131
		assert self.hdrlen == 7
		self.flags = tonumbyte(data[3:5])
		self.pixPerBlock = data[5]
		self.scanLinesPerPacket = data[6]
		'''
		print("flags: %04x"%self.flags)
		print("pixPerBlock: ",self.pixPerBlock)
		print("scanLinesPerPacket: ",self.scanLinesPerPacket)
		if self.flags & ALLOW_K13_OPTION_MASK:
			print("allow_k13")
		if self.flags & CHIP_OPTION_MASK:
			print("chip")
		if self.flags & EC_OPTION_MASK:
			print("ec")
		if self.flags & LSB_OPTION_MASK:
			print("LSB")
		if self.flags & MSB_OPTION_MASK:
			print("MSB")
		if self.flags & NN_OPTION_MASK:
			print("NN")
		if self.flags & RAW_OPTION_MASK:
			print("RAW")
		'''

class XRITHeaders():
	def __init__(self,lrit):
		lrit = lrit[10:]
		i = 0
		self.pri = XRITPrimaryHeader(lrit)
		i += self.pri.hdrlen
		#print("total length of header: ",self.pri.total_len)
		#print("data length: ",lrit.size)
		while i < self.pri.total_len:
			#print("Found header of type",lrit[i])
			if lrit[i] == 1:
				hdr = XRITImageStructureHeader(lrit[i:])
				self.struct = hdr
			elif lrit[i] == 2:
				hdr = XRITImageNavigationHeader(lrit[i:])
				self.nav = hdr
			elif lrit[i] == 3:
				hdr = XRITImageDataFunctionHeader(lrit[i:])
				self.function = hdr
			elif lrit[i] == 4:
				hdr = XRITAnnotationHeader(lrit[i:])
				self.anno = hdr
			elif lrit[i] == 5:
				hdr = XRITTimeStampHeader(lrit[i:])
				self.timestamp = hdr
			elif lrit[i] == 6:
				hdr = XRITAncillaryHeader(lrit[i:])
				self.ancil = hdr
			elif lrit[i] == 128:
				hdr = XRITImageSegHeader(lrit[i:])
				self.imageseg = hdr
			elif lrit[i] == 129:
				hdr = XRITNOAALRITHeader(lrit[i:])
				self.noaa = hdr
			elif lrit[i] == 130:
				hdr = XRITImageCompensationHeader(lrit[i:])
				self.compensation = hdr
			elif lrit[i] == 131:
				hdr = XRITRiceHeader(lrit[i:])
				self.rice = hdr
			else:
				print("Unknown header",lrit[i])
				exit(1)
			#print("hdr.hdrlen: ",hdr.hdrlen)
			i += hdr.hdrlen
		#print(i,self.pri.total_len)

from ctypes import *
folder = 'D:/msys64/mingw64/bin'
szip = CDLL(os.path.join(folder,'libsz.dll'))
decompress = szip.SZ_BufftoBuffDecompress
decompress.argtypes = (c_char_p,POINTER(c_size_t),c_char_p,c_size_t,POINTER(c_int))
decompress.restype = c_int

def rice_decomp(buf_in,headers):
	flags = headers.rice.flags
	bitsPerPixel = headers.struct.bpp
	pixPerBlock = headers.rice.pixPerBlock
	pixPerScanline = headers.struct.ncol

	buf_out = np.zeros(pixPerScanline,dtype=np.uint8)
	buf_in_len = c_size_t(buf_in.size)
	buf_out_len = c_size_t(buf_out.size)

	szcom = np.zeros(4,dtype=np.int32)
	szcom[0] = flags
	szcom[1] = bitsPerPixel
	szcom[2] = pixPerBlock
	szcom[3] = pixPerScanline

	retval = decompress(buf_out.ctypes.data_as(c_char_p),byref(buf_out_len),buf_in.ctypes.data_as(c_char_p),buf_in_len,szcom.ctypes.data_as(POINTER(c_int)))

	assert retval == 0
	return buf_out


import socket,os,struct
from ctypes import *

host = input("Enter IP Address: ")

class IP(Structure):
	_fields_ = [
		("ihl",           c_ubyte, 4),
		("version",       c_ubyte, 4),
		("tos",           c_ubyte),
		("len",           c_ushort),
		("id",            c_ushort),
		("offset",        c_ushort),
		("ttl",           c_ubyte),
		("protocol_num",  c_ubyte),
		("sum",           c_ushort),
		("src",           c_uint32),
		("dst",           c_uint32)
	]
	
	def __new__(cls, socket_buffer=None):
		return cls.from_buffer_copy(socket_buffer)
	
	def __init__(self, socket_buffer=None):
		self.socket_buffer = socket_buffer
		self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
		self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
		self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))
		try:
			self.protocol = self.protocol_map[self.protocol_num]

		except IndexError:
			self.protocol = str(self.protocol_num)

class ICMP(Structure):
	_fields_ = [
		("type",         c_ubyte),
		("code",         c_ubyte),
		("checksum",     c_ushort),
		("unused",       c_ushort),
		("next_hop_mtu", c_ushort)
	]

	def __new__(cls, socket_buffer):
		return cls.from_buffer_copy(socket_buffer)

	def __init__(self, socket_buffer):
		self.socket_buffer = socket_buffer

if os.name == "nt":
	socket_protocol = socket.IPPROTO_IP 
else:
	socket_protocol = socket.IPPROTO_ICMP
	
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
if os.name == "nt":
	sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
	while True:
		raw_buffer = sniffer.recvfrom(65535)[0]
		ip_header = IP(raw_buffer[:20])
		print("Protocol: %s %s -> %s" % (ip_header.protocol,ip_header.src_address,ip_header.dst_address))
		if ip_header.protocol == "ICMP":
			offset = ip_header.ihl * 4
			buf = raw_buffer[offset:offset + sizeof(ICMP)]
			icmp_header = ICMP(buf)
			print("ICMP -> Type: %d Code: %d" % (icmp_header.type,icmp_header.code))

except KeyboardInterrupt:
	if os.name == "nt":
		sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

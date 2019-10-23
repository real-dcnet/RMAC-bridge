from .globals import *
from .Crypto import Crypto

import socket

class OutwardSocket:
	def __init__(self, iface, ip, port, key):
		from .InwardSocket import InwardSocket
		self.iface = iface
		self.ip = ip
		self.port = port
		self.key = key
	
	def set_in(self, in_sock):
		self.in_sock = in_sock
	
	"""
	Accept packets from connection c until "\r\n" received
	"""
	def forward_packets(self, c, iface):
		incoming_packet = lambda: bytes(c.recv(4096))
		bytes_packet = incoming_packet()
		while bytes_packet:
			self.in_sock.srp_packet(bytes_packet, iface)
			bytes_packet = incoming_packet()
	
	"""
	Initialize the globally-facing socket
	"""
	def init_outward_socket(self):
		recieving_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		recieving_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		recieving_sock.bind((self.ip, self.port))
		recieving_sock.listen(1)
		print("Now listening on OUTWARD", self.ip, ":", self.port)
		connection, client_address = recieving_sock.accept()
		self.forward_packets(connection, self.iface)
		print("Remote connection closed")
		recieving_sock.close()

	"""
	Send a packet to the other bridge endpoint
	"""
	def send_over_bridge(self, sock, pkt):
		print(GREEN + "PACKET RECEIVED, FORWARDING TO BRIDGE" + RESET)
		pkt.show()
		packet_bytes = bytes(pkt)
		encrypted = self.key.encrypt(packet_bytes)
		sock.send(encrypted)

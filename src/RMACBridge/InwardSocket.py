from .Crypto import Crypto
from .globals import *

from scapy.all import *
from scapy.layers.l2 import Ether

import socket

class InwardSocket:
	def __init__(self, iface, ip, port, key):
		from .OutwardSocket import OutwardSocket
		self.iface = iface
		self.ip = ip
		self.port = port
		self.key = key

	def set_out(self, out_sock):
		self.out_sock = out_sock

	"""
	Initialize the DCnet-facing socket
	"""
	def init_inward_socket(self):
		print("Now listening on INWARD", self.ip, ":", self.port)
		sending_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connected = False
		while not connected:
			try:
				sending_sock.connect((REMOTE_IP, REMOTE_PORT))
				connected = True
			except ConnectionRefusedError as e:
				print("Connection refused, retrying in 5s...")
				time.sleep(5)
		print("Connection to remote established!")
		sniff(iface=INWARD_FACING_IFACE,
			prn=lambda pkt: self.out_sock.send_over_bridge(sending_sock, pkt))


	"""
	Sends an RMAC packet in to DCnet
	"""
	def srp_packet(self, packet_bytes, iface):
		decrypted = self.key.decrypt(packet_bytes)
		packet = Ether(decrypted)
		# This check makes sure to not forward local loopback heartbeat packets
		if not packet[Ether].type == 0x9000:
			print(RED + "PACKET RECIEVED, FORWARDING TO DCNET" + RESET)
			packet.show()
		# Uncomment the following line to actually send the packet to DCnet
		# srp(packet, iface=iface)

from scapy.all import *
from scapy.layers.l2 import Ether

import socket
import sys
import time
import threading
import pickle as pk

OUTWARD_FACING_IFACE = "eth0" # Network interface connected to Internet
OUTWARD_FACING_IP = "169.254.67.254" # Public-facing IP of this Raspberry Pi
OUTWARD_FACING_PORT = 5551 # Port associated with above IP

INWARD_FACING_IFACE = "lo" # Network interface connected to DCnet
INWARD_FACING_IP = "127.0.0.1" # DCnet-facing IP of this Raspberry Pi
INWARD_FACING_PORT = 5552 # Port associated with above IP

REMOTE_IP = "bridge" # Public-facing IP of other Raspberry Pi
REMOTE_PORT = 5551 # Port associated with above IP

RED = "\033[31m"
RESET = "\033[0m"

"""
Sends an RMAC packet out on the given interface
"""
def srp_packet(pickled_packet, iface):
	packet = Ether(pk.loads(pickled_packet))
	# Check not keepalive, would print loop infinitely without this
	if not packet[Ether].type == 0x9000:
		print(RED + "PACKET RECIEVED, FORWARDING TO DCNET" + RESET)
		packet.show()
	# TEST ONLY UNCOMMENT LATER
	# srp(packet, iface=iface)

"""
Accept packets from connection c until "\r\n" received
"""
def forward_packets(c, iface):
	incoming_packet = lambda: pk.dumps(c.recv(4096))
	
	pickled_pkt = incoming_packet()
	while pickled_pkt:
		srp_packet(pickled_pkt, iface)
		pickled_pkt = incoming_packet()

"""
Initialize the globally-facing socket
"""
def init_outward_socket():
	recieving_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	recieving_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	recieving_sock.bind((OUTWARD_FACING_IP, OUTWARD_FACING_PORT))
	recieving_sock.listen(1)
	print("Now listening on OUTWARD", OUTWARD_FACING_IP, ":", OUTWARD_FACING_PORT)
	connection, client_address = recieving_sock.accept()
	
	forward_packets(connection, INWARD_FACING_IFACE)
	print("Closing connection")
	recieving_sock.close()

"""
Initialize the DCnet-facing socket
"""

def send_over_bridge(sock, pkt):
	print("Sending packet here")
	pkt.show()
	pickled_packet = pk.dumps(pkt)
	sock.send(pickled_packet)

def init_inward_socket():
	print("Now listening on INWARD", INWARD_FACING_IP, ":", INWARD_FACING_PORT)
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
	fil = "dst port " + str(INWARD_FACING_PORT)
	sniff(iface=INWARD_FACING_IFACE, filter=fil, prn=lambda pkt: send_over_bridge(sending_sock, pkt))

def main():
	print("Beginning threadpool...")
	outward_task = threading.Thread(target=init_outward_socket, args=(), daemon=True)
	inward_task = threading.Thread(target=init_inward_socket, args=(), daemon=True)
	outward_task.start()
	inward_task.start()
	outward_task.join()
	inward_task.join()
	print("All tasks complete")

if __name__ == "__main__":
	main()

from scapy.all import *
import socket
import sys
import pickle as pk
from concurrent.futures import ThreadPoolExecutor

OUTWARD_FACING_IFACE = "lo" # Network interface connected to Internet
OUTWARD_FACING_IP = "127.0.0.1" # Public-facing IP of this Raspberry Pi
OUTWARD_FACING_PORT = 5551 # Port associated with above IP

INWARD_FACING_IFACE = "lo" # Network interface connected to DCnet
INWARD_FACING_IP = "127.0.0.1" # DCnet-facing IP of this Raspberry Pi
INWARD_FACING_PORT = 5552 # Port associated with above IP

REMOTE_IP = "127.0.0.2" # Public-facing IP of other Raspberry Pi
REMOTE_PORT = 5553 # Port associated with above IP

"""
Sends an RMAC packet out on the given interface
"""
def srp_packet(pickled_packet, iface):
	packet = pk.loads(pickled_packet)
	print("Incoming packet: ", packet.decode("utf-8")[: -2])
	srp(pkt=packet, iface=iface)

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
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((OUTWARD_FACING_IP, OUTWARD_FACING_PORT))
	sock.listen(1)
	print(f"Now listening on {OUTWARD_FACING_IP}:{OUTWARD_FACING_PORT}")
	connection, client_address = sock.accept()
	
	forward_packets(connection, INWARD_FACING_IFACE)
	print("Closing connection")
	sock.close()

"""
Initialize the DCnet-facing socket
"""
def init_inward_socket():
	print(f"Now listening on {INWARD_FACING_IP}:{INWARD_FACING_PORT}")
	fil = f"dst port {INWARD_FACING_PORT}"
	sniff(iface=INWARD_FACING_IFACE, filter=fil, prn=lambda x: x.show())

def main():
	pool = ThreadPoolExecutor(2)
	pool.submit(init_outward_socket)
	pool.submit(init_inward_socket)

if __name__ == "__main__":
	main()

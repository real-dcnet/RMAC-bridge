from .globals import *
from .Crypto import Crypto
from .OutwardSocket import OutwardSocket
from .InwardSocket import InwardSocket

import threading

def main():
	key = Crypto("../keys/bridge.key")
	out_sock = OutwardSocket(OUTWARD_FACING_IFACE, OUTWARD_FACING_IP, OUTWARD_FACING_PORT, key)
	in_sock = InwardSocket(INWARD_FACING_IFACE, INWARD_FACING_IP, INWARD_FACING_PORT, key)
	out_sock.set_in(in_sock)
	in_sock.set_out(out_sock)
	print("Beginning threadpool...")
	outward_task = threading.Thread(target=out_sock.init_outward_socket, args=(), daemon=True)
	inward_task = threading.Thread(target=in_sock.init_inward_socket, args=(), daemon=True)
	outward_task.start()
	inward_task.start()
	outward_task.join()
	inward_task.join()
	print("All tasks complete")

if __name__ == "__main__":
	main()

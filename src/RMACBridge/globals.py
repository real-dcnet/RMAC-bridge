OUTWARD_FACING_IFACE = "eth0" # Network interface connected to Internet
OUTWARD_FACING_IP = "169.254.67.254" # Public-facing IP of this Raspberry Pi
OUTWARD_FACING_PORT = 5551 # Port associated with above IP

INWARD_FACING_IFACE = "lo" # Network interface connected to DCnet
INWARD_FACING_IP = "127.0.0.1" # DCnet-facing IP of this Raspberry Pi
INWARD_FACING_PORT = 5552 # Port associated with above IP

REMOTE_IP = "bridge" # Public-facing IP of other Raspberry Pi
REMOTE_PORT = 5551 # Port associated with above IP

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

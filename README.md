# RMAC bridge
An RMAC bridge to create a virtual network between two remote data centers.

## Purpose
DCnet proposes using a modified MAC-adressing scheme which would be erased by sending 
our data out over a typical connection to the Internet. The RMAC bridge serves as an
intermediary, encapsulating a DCnet packet within an ordinary TCP/IP header. 

## How it works
Each bridge endpoint sits just outside an egress switch in either remote data center.
Both endpoints consist of a Raspberry Pi with two network interfaces: one is the
default machine's NIC and the other is a USB-to-Ethernet adapter. One is connected to
the DCnet network and the other is connected to the global Internet. When receiving a
packet from within a DCnet data center, each bridge endpoint wraps the DCnet packet
in TCP/IP headers and sends it to the remote endpoint.

![RMAC bridge diagram](https://i.ibb.co/k0bCRV2/RMAC-Bridge-2.png)

Once the remote endpoint receives a TCP/IP-wrapped packet, it will unwrap the packet
and send the it into the receiving DCnet network. In the above diagram, blue edges
represent DCnet packets and red represents an encapsulated packet.

## Setup
To set up the RMAC bridge, clone the repository and run

```
sudo pip install -r requirements.txt
```

To configure RMAC Bridge for your environment, change the following settings at the
top of `incoming.py`:

```
OUTWARD_FACING_IFACE = "eth0" # Network interface connected to Internet
OUTWARD_FACING_IP = "169.254.67.254" # Public-facing IP of this Raspberry Pi
OUTWARD_FACING_PORT = 5551 # Port associated with above IP

INWARD_FACING_IFACE = "lo" # Network interface connected to DCnet
INWARD_FACING_IP = "127.0.0.1" # DCnet-facing IP of this Raspberry Pi
INWARD_FACING_PORT = 5552 # Port associated with above IP

REMOTE_IP = "bridge" # Public-facing IP of other Raspberry Pi
REMOTE_PORT = 5551 # Port associated with above IP
```

All settings prefixed with "OUTWARD" indicates a red edge in the above diagram.
All settings prefixed with "INWARD" indicates a blue edge in the above diagram.
`REMOTE_IP` corresponds to the IP of the other RMAC endpoint on the other side
of the red link in the above diagram. In the above, we have aliased the remote
IP of each endpoint to "bridge" in our `/etc/hosts` file.

## Running the application
On each endpoint, run:

```
sudo python3 incoming.py
```

Each endpoint will attempt to establish a connection with the other every five
seconds. You can verify the connection works with 
`echo -n "Hello World!" > /dev/udp/localhost/5552` (assuming that we're
listening for DCnet packets on localhost:5552). You should see the packet
appear at the other end.

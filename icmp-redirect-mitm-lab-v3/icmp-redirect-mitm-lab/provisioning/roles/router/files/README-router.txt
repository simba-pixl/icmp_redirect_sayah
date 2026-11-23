Role of this machine: LEGITIMATE ROUTER (10.9.0.11 / 192.168.60.11)

This is the real default gateway victim normally uses to reach
192.168.60.0/24. It simply forwards IPv4 traffic between the two
subnets (net.ipv4.ip_forward=1) and otherwise plays no active part in the
attack - it is here so that, before the attack, the victim's legitimate
route via 10.9.0.11 actually works and can be observed and compared to the
state after the redirect.

You should not need to change anything here; it is provided mainly for
inspection (e.g. to confirm the victim's pre-attack route really is valid).

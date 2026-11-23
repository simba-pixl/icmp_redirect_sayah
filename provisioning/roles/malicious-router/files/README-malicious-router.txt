Role of this machine: MALICIOUS ROUTER (10.9.0.111)

Current sysctl defaults (check with `sysctl net.ipv4.ip_forward` etc.):
    net.ipv4.ip_forward              = 1   (so Task 1's redirect genuinely
                                             relays traffic through here)
    net.ipv4.conf.all.send_redirects = 0
    net.ipv4.conf.default.send_redirects = 0
    net.ipv4.conf.eth0.send_redirects    = 0

For Task 1 you do not need to run anything here - the attack packets are
crafted and sent from the attacker machine (10.9.0.105); this box just
needs to keep forwarding so the redirected traffic actually flows.

For Question 3, flip the three send_redirects values to 1 on this machine
(sysctl -w ...=1) and re-run the Task 1 attack from the attacker machine to
see whether it still works.

For Task 2:
    1. sysctl net.ipv4.ip_forward=0
    2. Edit and run mitm-sample.py (the secret word to replace is in
       secret_word.txt)

This exercise is for educational purposes only, against your own lab
sandbox.

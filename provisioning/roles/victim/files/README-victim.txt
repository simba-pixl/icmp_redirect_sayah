Role of this machine: VICTIM (10.9.0.5)

This machine's countermeasure against ICMP redirects is deliberately
disabled (net.ipv4.conf.all.accept_redirects=1), as instructed in the lab.

Useful for Task 1 / Q1 / Q2 / Q3:
    ip route                 # the routing table (unaffected by redirects)
    ip route get <ip>        # which gateway would be used right now
    ip route show cache      # the routing CACHE - this is what redirects change
    ip route flush cache     # clear it, to test again from a clean state
    mtr -n 192.168.60.5      # see which path packets actually take
    ping 192.168.60.5        # generate traffic that CAN be redirected
    sudo /usr/local/sbin/check-flag1
                              # securely checks the redirect and prints Task 1 flag

Useful for Task 2:
    nc <target-ip> <port>    # connect to the netcat-like service on target
    # Read secret_word.txt for the word to send.

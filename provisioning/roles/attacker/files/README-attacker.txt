Role of this machine: ATTACKER (10.9.0.105)

This is where you craft and send the spoofed ICMP Redirect packets for
Task 1 and its three follow-up questions. A code skeleton is at:

    icmp-redirect-skeleton.py

Useful aliases are already in /etc/hosts: attacker, victim,
malicious-router, router.

You also have console/GUI access to the other machines in this topology
(victim, malicious-router, router, target) - you will need them too:
  - victim:            check/trigger the routing table and cache
  - malicious-router:  Task 2 (disable IP forwarding, run the MITM script)
  - target:            start/observe the netcat "service" you are attacking

Remember: this exercise is for educational purposes only, against your own
lab sandbox. Unauthorized use of these techniques against real networks is
illegal.

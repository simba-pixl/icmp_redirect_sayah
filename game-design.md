# ICMP Redirect & MITM Attack Lab

Adapted for CyberRangeCZ Platform from the SEED Labs "ICMP Redirect Attack
Lab" (Wenliang Du), for a System Security course TP.

## Storyline

You are auditing a flat office network for a client. The client's hosts
(`victim`, 10.9.0.5) reach a partner network (`192.168.60.0/24`, reachable
through `router` at `10.9.0.11`) for a file-sharing service. Your job is to
demonstrate, end to end, that an on-path attacker who can merely send
spoofed packets - without ever touching the real router - can hijack that
route and read/modify the victim's traffic. You control two machines: the
`attacker` (10.9.0.105), from which you send the spoofed packets, and the
`malicious-router` (10.9.0.111), the box you want the victim's traffic to
actually flow through.

## Learning outcomes

- Understand the IP and ICMP protocols well enough to forge a valid-looking
  ICMP Redirect message with Scapy.
- Understand the difference between the Linux routing **table** and routing
  **cache**, and how a redirect only affects the latter.
- Understand the on-link/same-subnet validation the kernel performs before
  accepting a redirect, and why it limits where an attacker can redirect
  traffic to.
- Perform a full sniff-and-spoof Man-in-the-Middle attack on a TCP stream
  without breaking the TCP sequence numbers.
- Reason about capture-filter choices (direction, IP vs. MAC) in an
  on-path/MITM setting.

## Topology summary

| Host              | Image | mgmt_user | Flavor    | IP(s)                      |
|-------------------|-------|-----------|-----------|-----------------------------|
| attacker          | seed  | ubuntu    | m1.medium | 10.9.0.105                  |
| victim            | seed  | ubuntu    | m1.medium | 10.9.0.5                    |
| malicious-router  | seed  | ubuntu    | m1.medium | 10.9.0.111                  |
| router (router)   | seed  | ubuntu    | m1.medium | 10.9.0.11 / 192.168.60.11   |
| target            | seed  | ubuntu    | m1.medium | 192.168.60.5                |

Networks: `attacker-switch` (10.9.0.0/24) and `target-switch`
(192.168.60.0/24), both reachable by the student, bridged only by `router`.
`malicious-router` is deliberately **not** connected to `target-switch` -
exactly like Figure 1 of the original lab - to make the point that an
ICMP-redirect MITM does not require the attacker to be physically on the
victim's destination network, only on the same LAN segment as the victim.

## Scoring and anti-cheat design

Total score: **20 points**, spread over 9 graded levels (table below).
Hint penalties range from **-0.5 to -2 points** per hint.

Two levels (Task 1's core attack, and Task 2's core MITM) are graded with
**per-sandbox randomized flags** (CyberRangeCZ APG / `variables.yml`):
a student only receives their flag by running a provided checker script
*on their own sandbox* once the attack has genuinely succeeded, so a flag
copied from a classmate will not validate. Two more APG variables
(`nc_port`, `secret_word`) randomize the practical details of Task 2 (which
port the service listens on, which word must be redacted) so the attack
itself can't be done "by memory" from another student's session either.

The five "Question" levels (Q1-Q5) test understanding of fixed OS/network
behaviour that is identical on every sandbox (e.g. "can you redirect to an
off-subnet gateway?") - there is nothing sandbox-specific to leak there, so
they keep static answers, same as the template's own precedent.

| # | Level                                                   | Type           | Max score | Flag type        |
|---|----------------------------------------------------------|----------------|-----------|-------------------|
| 0 | Introduction                                              | INFO_LEVEL     | -         | -                 |
| 1 | Get Access                                                | ACCESS_LEVEL   | -         | static (`start`)  |
| 2 | Recon: mapping the victim's current route                | TRAINING_LEVEL | 2         | static            |
| 3 | Task 1: spoof the ICMP Redirect                           | TRAINING_LEVEL | 4         | **APG** (`flag_task1`) |
| 4 | Question 1: redirecting to a remote (off-subnet) host     | TRAINING_LEVEL | 1         | static            |
| 5 | Question 2: redirecting to a non-existent local host      | TRAINING_LEVEL | 1         | static            |
| 6 | Question 3: does `send_redirects` matter here?            | TRAINING_LEVEL | 2         | static            |
| 7 | Task 2 setup: disable forwarding, find the service        | TRAINING_LEVEL | 2         | **APG** (`nc_port`) |
| 8 | Task 2: execute the MITM and redact the traffic           | TRAINING_LEVEL | 5         | **APG** (`flag_task2`) |
| 9 | Question 4: which direction do you need to capture?       | TRAINING_LEVEL | 1         | static            |
| 10| Question 5: filter by IP or by MAC address?               | TRAINING_LEVEL | 2         | static            |

20 points total across levels 2-10.

## Deviation from the original PDF worth noting

The original lab asks students to replace occurrences of their **real first
name** in the MITM demo, "so we know the work is done by you" - a
human-graded, report-based anti-cheat measure. Since this version is
auto-graded by flag string, that mechanism doesn't translate directly (a
name isn't something the platform can generate or verify per sandbox), so
it is replaced with a per-sandbox random `secret_word` that plays exactly
the same pedagogical role (redact a word of a given length without
desyncing TCP) while remaining machine-checkable. The instructor report/
screenshot requirement from the PDF's own "Submission" section still
applies on top of this if you want the human-verification layer back - see
README.md.

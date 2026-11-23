# ICMP Redirect & MITM Attack Lab (CyberRangeCZ)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Lab%20content-CC%20BY--NC--SA%204.0-orange.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

Linear game for [CyberRangeCZ Platform](https://docs.platform.cyberrange.cz/),
adapted from the **SEED Labs "ICMP Redirect Attack Lab"** (System Security
TP) and built on the structure of the `library-junior-hacker` scenario.

## Game Levels Summary
- recon: compare the routing table vs. the routing cache on the victim
- Task 1: forge and send a spoofed ICMP Redirect with Scapy to hijack the
  victim's route
- 3 analysis questions on the limits of the attack (off-subnet gateways,
  non-existent gateways, the `send_redirects` sysctl)
- Task 2: disable IP forwarding and run a full sniff-and-spoof TCP MITM that
  redacts a word in flight without breaking the TCP stream
- 2 analysis questions on capture-filter design (direction, IP vs. MAC)

## Topology summary
| Host              | Image | mgmt_user | Flavor    |
|-------------------|-------|-----------|-----------|
| attacker          | seed  | ubuntu    | m1.medium |
| victim            | seed  | ubuntu    | m1.medium |
| malicious_router  | seed  | ubuntu    | m1.medium |
| router (router)   | seed  | ubuntu    | m1.medium |
| target            | seed  | ubuntu    | m1.medium |

See `topology.yml` for the full network layout (two subnets,
`10.9.0.0/24` and `192.168.60.0/24`, matching Figure 1 of the original lab).

## Scoring
- **20 points total**, across 9 graded levels (2 points up to 5 points each).
- Hint penalties range from **-0.5 to -2 points** per hint.
- See `game_design.md` for the full level-by-level score and hint table.

## Anti-cheat: per-sandbox randomized flags (APG)
Four values are randomized per sandbox via CyberRangeCZ's Automatic Problem
Generation feature (`variables.yml`):

| Variable      | Used for                                                        |
|---------------|-------------------------------------------------------------------|
| `flag_task1`  | Awarded by a checker script on `victim`, only if the redirect genuinely took effect |
| `nc_port`     | The port Task 2's listener runs on, discovered via a file on `target` |
| `secret_word` | The word that must be redacted in Task 2's MITM traffic, delivered via a file on `victim`/`malicious_router` |
| `flag_task2`  | Awarded by a checker script on `target`, only if the word arrived correctly redacted |

The 5 "Question" levels keep static answers - they test understanding of OS/
network behaviour that is identical on every sandbox, so there's nothing
sandbox-specific to leak there.

**To deploy with unique flags for ~30 students:** import this repository as
a Sandbox Definition, create a pool of (at least) 30 sandboxes from it, then
upload `training.json` as a Linear Training Definition with "Generate
variant sandboxes" / `variant_sandboxes` enabled (it already is, in the
JSON). CyberRangeCZ regenerates `variables.yml`'s values independently for
every sandbox in the pool, and grades each student against their own
sandbox's values.

## A note on the original lab's "use your real first name" instruction
The PDF's Task 2 asks students to redact their own first name, as a
human-graded, report-based anti-cheat measure. Since this version is
auto-graded, that's replaced by the per-sandbox `secret_word` above, which
tests the exact same skill (redact a word of a given length without
desyncing TCP) in a way the platform can verify automatically. If you also
want to keep the original human-verification layer (e.g. for a
plagiarism-resistant written report), you can still ask students to submit
a short report/screenshots per the PDF's own "Submission" section on top of
the automated flags - the two are not mutually exclusive.

## Repository contents
```
├── topology.yml          # 5 nodes, all "seed" image / mgmt_user ubuntu, 2 networks
├── variables.yml         # APG variables for the 4 randomized values above
├── training.json         # Importable CyberRangeCZ linear training definition
├── game_design.md        # Full storyline + level/score/hint breakdown
├── ATTRIBUTION.txt       # Credits for the SEED lab and the junior-hacker template
├── build/
│   └── build_training.py # Source-of-truth script that generates training.json
└── provisioning/
    ├── playbook.yml
    ├── requirements.yml
    ├── host_vars/
    └── roles/
        ├── hosts/             # common packages on every host-type node
        ├── attacker/          # scapy + Task 1 skeleton
        ├── victim/            # accept_redirects=1, secret word, flag-1 checker
        ├── malicious_router/  # scapy + sysctls + Task 2 MITM skeleton
        ├── router/            # plain IPv4 forwarding between the two subnets
        └── target/            # netcat-like logging listener + flag-2 checker
```

To change wording, scoring, or hints, edit `build/build_training.py` and
re-run `python3 build/build_training.py` rather than hand-editing
`training.json`, so the two stay in sync.

## Assumptions made while building this (flag me if any are wrong)
1. **Image name**: "seed" is used literally, as requested, on all five nodes
   (attacker, victim, malicious_router, router, target), with `mgmt_user:
   ubuntu`. Please confirm these are the exact values in your cloud's image
   catalog - some deployments register the image as e.g.
   `seed-ubuntu-20.04`, or use a different default admin account name.
2. **Flavor**: `m1.medium` is applied to *every* node for simplicity. If you
   want the plain `router`/`target` nodes (which do almost no work) kept on
   a smaller flavor, that's a one-line change in `topology.yml`.
3. **Topology simplification**: the original lab's Figure 1 shows a second,
   unused host (`192.168.60.6`) on the partner network; it's omitted here
   since no task touches it. Say the word if you'd like it added back in
   as a decoy/distractor for the nmap-style recon step.
4. **Console access**: per your confirmation, all 5 machines are reachable
   by the student (`accessible_by_user: True` on both networks), since the
   lab genuinely requires actions on victim, malicious_router and target,
   not just on the attacker.
5. **Total duration**: levels 2-10 sum to about 76 minutes of estimated
   solve time (plus intro/access), which is a reasonable single TP session;
   adjust `estimated_duration` per level in `build_training.py` if your
   session is shorter/longer.

Let me know if you'd like any of these changed, additional hints, a harder/
easier scoring curve, the decoy host added back, or a written
instructor-answer-key document generated separately from `training.json`.

## License
This repository uses a dual licensing approach:
* The code (Ansible, topology/training definitions, custom scripts) is
  licensed under the MIT License.
* The lab content is adapted from SEED Labs (CC BY-NC-SA 4.0) and the
  junior-hacker game design (CC BY 4.0) - see `ATTRIBUTION.txt`.

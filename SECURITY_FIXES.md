# Security fixes in this package

## Flag protection
- Task 1 and Task 2 checkers are installed as root-owned executables in
  `/usr/local/sbin/` with mode `0700`.
- The flag-bearing checker templates are not copied into student home
  directories.
- Students on `victim` and `target` do not receive general sudo access.
- Each of those hosts has a sudoers rule allowing only its own fixed checker
  command to run as root, without arguments.
- Task 2's listener runs as root and writes to
  `/var/log/icmp-redirect-lab/received.log`, under a root-only directory.
  The student account cannot directly read or modify that evidence log.

## Commands students use
- On `victim`: `sudo /usr/local/sbin/check-flag1`
- On `target`: `sudo /usr/local/sbin/check-flag2`

## Important deployment note
This package has been statically patched and its ZIP/JSON/YAML structure
validated. It has not been deployed to a live CyberRangeCZ/OpenStack
environment. Confirm the image names and management usernames in your
CyberRangeCZ catalog, then test provisioning and both checkers in one
disposable sandbox before publishing the scenario.

The Task 2 checker validates the protected target-side log for the expected
same-length replacement. This protects the flag and log from simple local
file editing, but it is not a cryptographic proof that the traffic traversed
the malicious router: a determined student with control of the victim could
send the replacement string directly. For high-stakes grading, add an
independent packet-evidence check on `malicious_router` or an external
grader before awarding Task 2.

## Fixes applied on top of this pass (by Claude, after review)

Two issues were found while verifying this patch and have been corrected
in this package; the security design above (root-owned checkers, scoped
sudoers, protected log) is unchanged and intact.

1. **`check-flag2.sh.j2` failed to render at all.** The new version of the
   script used bash's `${#SECRET}` (string-length) syntax outside of a
   Jinja2 `{% raw %}` block. Jinja2's lexer misreads the `${#` sequence as
   the start of a `{# ... #}` comment tag and throws
   `TemplateSyntaxError: Missing end of comment tag`. Ansible's `template`
   module would have failed during provisioning, so `check-flag2` would
   never have been created on `target` at all - Task 2's flag could never
   have been awarded to anyone. Re-wrapped the bash body in `{% raw %}`
   (keeping only the two real Jinja substitutions, `secret_word` and
   `flag_task2`, outside it) and re-verified the file renders and passes
   `bash -n`.
2. **`build/build_training.py` had drifted out of sync with the shipped
   `training.json`.** The security-fix pass hand-edited `training.json`
   directly (new `sudo /usr/local/sbin/check-flag1/2` wording, "root-
   protected log" phrasing) but never updated the generator script that
   produces it. Since the README tells you to edit `build_training.py` and
   re-run it for any future change, running it as shipped would have
   silently regenerated a `training.json` that told students to run
   `check-flag1.sh` / `check-flag2.sh` - files that no longer exist
   anywhere once the security fix is applied. Updated the six stale
   strings in `build_training.py` so it now regenerates byte-for-byte the
   same `training.json` that ships in this package (verified with `diff`).
   Also fixed `OUT`'s hardcoded absolute path (a pre-existing issue, not
   introduced by this patch) to be computed relative to the script's own
   location, so the script is portable to any machine/checkout.

Full validation re-run after these fixes: all YAML/JSON parses, all Jinja
templates render, all rendered `.sh` files pass `bash -n`, the two sample
Python scripts (`mitm_sample.py`, `nc_logger.py`) compile, and
`training.json`'s levels still sum to exactly 20 points.

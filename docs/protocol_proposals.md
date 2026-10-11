# Protocol ideas to approve later

**Proposal only, not implemented.** Hardware use is untested. The current
T format, empty sensor fields, 256-byte limit and D/STOP commands are unchanged.
No line counter, checksum or boot message has been added.

The prepared logger splits when time does not increase or either raw encoder
count decreases. It stops on a serial error rather than silently reconnecting.
This catches visible resets and rollovers, but a reboot between observations
can be invisible if every received counter is still greater than the last one.
These fields alone cannot prove that a reboot never happened.

A possible next contract version could carry a boot identifier with each
snapshot. A sequence counter could expose lost or repeated lines. A checksum
could reject some corruption that still looks like valid numeric text. They
answer different questions; a checksum alone cannot identify a new boot.

Before implementing anything, agree the exact message layout, identifier and
counter sizes, rollover rules, checksum method and which bytes it covers.
Check that the longest line still fits 256 bytes, and how schema versions and
CSV readers would handle the change. Any example values would be SIMULATED DATA.

**Waiting for approval.** Keep the current format until an exact proposal is
reviewed. There is no command acknowledgement, motor speed limit or command
timeout in milestone 1; those belong to later firmware before motors are used.

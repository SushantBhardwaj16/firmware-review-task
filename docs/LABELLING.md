# How to label a finding

Every finding gets exactly one verdict.

| Verdict | Use it when |
|---|---|
| `real` | The files show the finding is true for this image |
| `real-with-condition` | It is true, but only matters once something changes that the device allows: say what |
| `false` | The files show the finding is not true for this image |
| `unverified` | The files cannot settle it. Say what is missing and what would settle it |

## Evidence

A verdict without evidence is an opinion. For every verdict give:

- the **path** of each file in the image that shows it;
- what the file shows: the line, the setting or the text;
- how you found it: the command, so someone else can repeat it in two minutes.

To call a finding `real`, show that what it describes is there. For an advisory, show all three conditions in
the primer.

To call a finding `false`, show what contradicts it. If your reason is that something is absent, show how you
looked for it.

## Rules that settle the hard cases

- **Judge the finding as the report states it, with the evidence it cites.** If the claim is true only
  because of another file, one the report does not cite, the finding is `false` and the other file is a
  missed problem.
- **An advisory whose condition does not hold for this image is `false`,** not `real-with-condition`.
- **A condition is a change to the device that the device allows:** a setting, a feature switched on. What
  an attacker needs first (a place on the network, an account on the device) is not a condition.
- **A file name is a hint, not evidence of a version.**

Never guess. `unverified`, with what you would need, is a good answer when it is the true one. A wrong `real`
wastes an engineer's week. A wrong `false` leaves a hole in a device.

## An example, from another device

> **Finding:** "ftpd-mini 2.1.0: login bypass (ADV-7)". ADV-7 affects ftpd-mini from 2.0.0 to below 2.2.0.
>
> **Verdict:** `real`.
> **Evidence:** `usr/sbin/ftpd` holds the text `ftpd-mini/2.1.0` (found with `strings`), so the version is in
> the affected range. `etc/init.d/S45ftpd` starts it at boot. ADV-7 has no condition.

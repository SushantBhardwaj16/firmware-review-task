# S5: Read a C function

**Area:** C. **Type:** judge. **Points:** 10. Optional.

`c/linkcfgd_packet.c` is a function from a made-up device program. It handles one kind of network packet.
It has one security bug.

## What to do

Read the function and fill in `answers/S5.json`:

```json
{
  "line": 0,
  "trigger_length": 0,
  "effect": "What happens in memory, and what that means for the device.",
  "fix": "The corrected line."
}
```

- `line` is the number of the line that must change.
- `trigger_length` is a value of `len`, the length byte of the packet, that triggers the bug.

You do not need to compile or run anything.

## Done means

- A reader who knows C can follow your `effect` step by step, down to which byte is written.

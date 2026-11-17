# S6: Look inside a program

**Area:** reverse engineering. **Type:** judge. **Points:** 20. Bonus.

`usr/sbin/kc-maintd` in the image is a small ARM program. It starts at boot (`etc/init.d/S65maint`) and
answers commands on a network port. Three of its commands are plain to see in its text. It has one more
command, and its text does not show that one.

## What to do

Open the program in a disassembler (Ghidra, objdump, radare2 or any other), find the hidden command, and
fill in `answers/S6.json`:

```json
{
  "command": "",
  "password": "",
  "key": "",
  "effect": "What the program does when it receives them, and what that means for the device.",
  "how": "The tool you used and the steps, in a few lines."
}
```

- `command` is the hidden command word.
- `password` is what must follow it.
- `key` is the one byte the program uses to hide both, written in hex, such as `0x1F`.

You do not need to run the program, and you do not need an ARM device.

## Done means

- Someone else can find the same bytes in the file by following your `how`.

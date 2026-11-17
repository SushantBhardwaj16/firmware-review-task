#!/usr/bin/env python3
"""Decode the S6 static-analysis byte sequences; this does not execute the ELF."""
KEY = 0xA7
SAMPLES = {
    "command": bytes.fromhex("f2 e9 eb e6 f3 e4 ef"),
    "password": bytes.fromhex("cf c2 d5 c8 c9 8a c0 c6 d3 c2 8a 93 95"),
}
for label, encoded in SAMPLES.items():
    decoded = bytes(value ^ KEY for value in encoded)
    print(f"{label}: {decoded.decode('ascii')}")
print(f"xor_key: 0x{KEY:02X}")

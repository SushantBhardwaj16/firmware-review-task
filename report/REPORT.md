# Engine report: Kestrel Dome 2 (KC-DOME-2), firmware 1.4.2

- Image: `images/kestrel-dome2-1.4.2.bin` (build 20260214)
- Findings: 12 (2 critical, 5 high, 4 medium, 1 low)
- Status: engine output, not yet checked by a person

| Id | Severity | Finding | Evidence |
|---|---|---|---|
| F-01 | critical | Telnet service starts at boot | `etc/init.d/S40telnetd` |
| F-02 | critical | Default password for the admin account | `etc/shadow` |
| F-03 | high | fernhttpd 2.4.1: CGI handler overflow (DVS-2026-0101) | `usr/sbin/fernhttpd` |
| F-04 | high | zpack 1.2.3: inflate overflow (DVS-2026-0102) | `usr/lib/libzebra.so.1.2.3` |
| F-05 | high | linkcfgd 1.8: config import flaw (DVS-2026-0103) | `usr/share/doc/linkcfgd/CHANGES` |
| F-06 | high | upnp-relay 3.0.2: port mapping without authentication (DVS-2026-0104) | `usr/sbin/upnp-relay` |
| F-07 | high | Kernel 5.10.88: packet filter flaw (DVS-2026-0105) | `boot/config` |
| F-08 | medium | Private key shipped in the image | `usr/share/doc/libcrypt-lite/examples/test-key.pem` |
| F-09 | medium | Firmware update fetched over HTTP without verification | `etc/config/updater` |
| F-10 | medium | bootwarden 0.9: boot check bypass (DVS-2026-0106) | `boot/bootwarden-0.9.bin` |
| F-11 | medium | Start-up script writable by any user | `etc/init.d/S90custom` |
| F-12 | low | Debug shell on the serial console | `etc/inittab` |

## F-01: Telnet service starts at boot

- Severity: critical
- Evidence: `etc/init.d/S40telnetd`

A start-up script starts a telnet service on every boot. Telnet is not encrypted, so anyone on the same network can read the session or connect to the device.

## F-02: Default password for the admin account

- Severity: critical
- Evidence: `etc/shadow`

The admin account has a password that is set in the image. Every device starts with the same password.

## F-03: fernhttpd 2.4.1: CGI handler overflow (DVS-2026-0101)

- Severity: high
- Component: fernhttpd 2.4.1
- Advisory: DVS-2026-0101 (affected: 2.0.0 to below 2.5.0)
- Evidence: `usr/sbin/fernhttpd`

The image contains fernhttpd 2.4.1, which is in the affected range of DVS-2026-0101. A long request header can overflow a buffer in the CGI handler of the web server.

## F-04: zpack 1.2.3: inflate overflow (DVS-2026-0102)

- Severity: high
- Component: zpack 1.2.3
- Advisory: DVS-2026-0102 (affected: below 1.2.12)
- Evidence: `usr/lib/libzebra.so.1.2.3`

The image contains zpack 1.2.3, which is in the affected range of DVS-2026-0102. A damaged compressed stream can make inflate write outside its window.

## F-05: linkcfgd 1.8: config import flaw (DVS-2026-0103)

- Severity: high
- Component: linkcfgd 1.8
- Advisory: DVS-2026-0103 (affected: below 2.0.0)
- Evidence: `usr/share/doc/linkcfgd/CHANGES`

The image contains linkcfgd 1.8, which is in the affected range of DVS-2026-0103. The configuration import does not check the length of a record.

## F-06: upnp-relay 3.0.2: port mapping without authentication (DVS-2026-0104)

- Severity: high
- Component: upnp-relay 3.0.2
- Advisory: DVS-2026-0104 (affected: 3.0.0 to below 3.0.6)
- Evidence: `usr/sbin/upnp-relay`

The image contains upnp-relay 3.0.2, which is in the affected range of DVS-2026-0104. Any host on the local network can ask the relay to open the device's ports to the internet.

## F-07: Kernel 5.10.88: packet filter flaw (DVS-2026-0105)

- Severity: high
- Component: kernel 5.10.88
- Advisory: DVS-2026-0105 (affected: 5.10.0 to below 5.10.120)
- Evidence: `boot/config`

The image contains kernel 5.10.88, which is in the affected range of DVS-2026-0105. A short packet can crash the kernel in the packet filter.

## F-08: Private key shipped in the image

- Severity: medium
- Evidence: `usr/share/doc/libcrypt-lite/examples/test-key.pem`

The image contains a private key that the device uses to protect its connections. A key shipped in firmware is the same on every device, and anyone who has the image can read it.

## F-09: Firmware update fetched over HTTP without verification

- Severity: medium
- Evidence: `etc/config/updater`

The updater fetches firmware over plain HTTP and does not verify it. Someone on the network path can replace the update with their own image.

## F-10: bootwarden 0.9: boot check bypass (DVS-2026-0106)

- Severity: medium
- Component: bootwarden 0.9
- Advisory: DVS-2026-0106 (affected: 0.9.0 to below 0.9.4)
- Evidence: `boot/bootwarden-0.9.bin`

The image contains bootwarden 0.9, which is in the affected range of DVS-2026-0106. The boot loader can skip the check of the next stage.

## F-11: Start-up script writable by any user

- Severity: medium
- Evidence: `etc/init.d/S90custom`

A start-up script has mode 0777. Any user on the device can change it, and it runs as root at the next boot.

## F-12: Debug shell on the serial console

- Severity: low
- Evidence: `etc/inittab`

The init table starts a shell on the serial console without a login. Anyone who can reach the serial pins gets a root shell.

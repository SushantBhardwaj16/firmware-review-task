# Firmware review: Kestrel Dome 2, firmware 1.4.2

## Summary

The 12 reported findings were checked against the supplied image. The current verdict set is three confirmed, one conditional, seven false as stated, and one unverified. The most urgent confirmed issue is boot-enabled Telnet configured to launch a shell. The UPnP relay is also enabled in an affected version, while a world-writable startup script creates a local privilege-escalation path.

## What the report missed

The image contains a concealed maintenance interface that can provide a shell to a peer who knows its embedded command and password. It also starts an unauthenticated clip-download service on port 8600 in an affected version range and passes a cloud-sync credential directly in a startup command. The quick-start guide documents the default admin credential; the factory shadow template matches the active admin hash. Since F-02 cites only the hash file, record this separately as a missed issue. It proves the default for this image, not every device. The F-08 example key is test-only, not the live service key.

## Why the engine was wrong

The library detector used prefix matching, so libzebra was misidentified as zpack. The version resolver allowed documentation to override installed-package evidence. Component identification should use exact library stems and prefer executable banners over package metadata; documentation is not proof of an installed version.

## What I could not verify

The bootwarden filename suggests version 0.9, but no authoritative version evidence was established. The related advisory remains under investigation rather than being inferred from the filename.

## Recommended actions

Disable or restrict Telnet; remove the maintenance interface or replace it with a properly authenticated channel; restrict clip downloads; rotate the cloud credential; correct startup-script permissions; and require authenticated, integrity-protected updates before enabling the updater. Review the live TLS key's provisioning and rotation.

## Method and limitations

Verdicts use image-relative evidence and reproducible inspection commands. The ARM review is static. The C proof of concept reproduces the boundary overwrite in an isolated struct; it is not execution against device firmware. On Python 3.13.5, all 53 tests passed against this source. The firmware unpacked 115 entries; component discovery and advisory analysis completed. The version-only matcher flags fernhttpd 2.4.1, but VEX correctly marks DVS-2026-0101 not affected because CGI is disabled. Re-run tests on the final commit.

# Firmware review: Kestrel Dome 2, firmware 1.4.2

## Summary

The 12 reported findings do not all withstand verification: three are confirmed, one is conditional, seven are false as stated, and one remains unverified. The most urgent confirmed issue is boot-enabled Telnet launching a root shell without authentication. The UPnP relay is also enabled in an affected version, while a world-writable startup script creates a local privilege-escalation path.

## What the report missed

The image contains a concealed maintenance interface that can provide a shell to a peer who knows its embedded command and password. It also starts an unauthenticated clip-download service on port 8600 in an affected version range and passes a cloud-sync credential directly in a startup command. The factory-account credential and live TLS private-key concern are discussed with their related S1 evidence rather than counted again as unrelated S2 findings.

## Why the engine was wrong

The library detector used prefix matching, so libzebra was misidentified as zpack. The version resolver allowed documentation to override installed-package evidence. Component identification should use exact library stems and prefer executable banners over package metadata; documentation is not proof of an installed version.

## What I could not verify

The bootwarden filename suggests version 0.9, but no authoritative version evidence was established. The related advisory remains under investigation rather than being inferred from the filename.

## Recommended actions

Disable or restrict Telnet; remove the maintenance interface or replace it with a properly authenticated channel; restrict clip downloads; rotate the cloud credential; correct startup-script permissions; and require authenticated, integrity-protected updates before enabling the updater. Review the live TLS key's provisioning and rotation.

## Method and limitations

Verdicts use image-relative evidence and reproducible inspection commands. The ARM review is static. The C proof of concept reproduces the boundary overwrite in an isolated struct; it is not execution against device firmware. GitHub Actions ran the complete repository unittest suite successfully on Python 3.10, 3.11 and 3.12 at the reviewed commit.
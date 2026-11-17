# Firmware review: Kestrel Dome 2, firmware 1.4.2

## Summary

The 12 reported findings do not all withstand verification. Three are confirmed, one is conditional, seven are false as stated, and one remains unverified. The most urgent issue is the boot-enabled Telnet service, which starts a shell directly as root. The UPnP relay is also enabled in an affected version, while a world-writable startup script creates a local privilege-escalation path.

## What the report missed

The image contains a concealed maintenance interface that can provide a shell to a peer who knows its embedded command and password. It also starts a clip-download service on port 8600 in an affected version range and passes a cloud-sync credential directly in a startup command. The factory account credential and live TLS private key are noted alongside their related S1 evidence rather than double-counted as separate S2 items.

## Why the engine was wrong

The library detector used prefix matching, so libzebra was misidentified as zpack. The version resolver allowed documentation to override installed-package evidence. Component identification should use exact library stems and prefer executable banners over package metadata, with documentation excluded as proof of the installed version.

## What I could not verify

The bootwarden filename suggests version 0.9, but no authoritative version evidence was found in the binary. I have left the related advisory under investigation rather than infer a version from its filename.

## Recommended actions

Disable or restrict Telnet; remove or strongly authenticate the maintenance interface; restrict clip downloads; rotate the cloud credential; correct startup-script permissions; and require authenticated, integrity-protected updates before enabling the updater. Review the live TLS key's provisioning and rotation.

## Method and limitations

Verdicts are tied to image-relative file evidence and reproducible inspection commands. The ARM review is static. The C proof of concept is an isolated reproduction of the boundary overwrite, not execution against a device. Component regression tests passed locally; the complete repository test suite still requires execution in the full checkout.
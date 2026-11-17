# Firmware review: Kestrel Dome 2, firmware 1.4.2

## Summary

The 12 reported findings were checked against the supplied image. The current verdict set is three confirmed, one conditional, seven false as stated, and one unverified. The most urgent confirmed issue is boot-enabled Telnet configured to launch a shell. The UPnP relay is also enabled in an affected version, while a world-writable startup script creates a local privilege-escalation path.

## What the report missed

The image contains a concealed maintenance interface that can provide a shell to a peer who knows its embedded command and password. It also starts an unauthenticated clip-download service on port 8600 in an affected version range and passes a cloud-sync credential directly in a startup command. The factory shadow template contains an admin hash identical to the active admin hash; this supports credential reuse in the supplied image, but does not by itself prove that every manufactured device has the same password. A live TLS private-key concern is documented separately and should be assessed against the service configuration before claiming that the example key is in use.

## Why the engine was wrong

The library detector used prefix matching, so libzebra was misidentified as zpack. The version resolver allowed documentation to override installed-package evidence. Component identification should use exact library stems and prefer executable banners over package metadata; documentation is not proof of an installed version.

## What I could not verify

The bootwarden filename suggests version 0.9, but no authoritative version evidence was established. The related advisory remains under investigation rather than being inferred from the filename.

## Recommended actions

Disable or restrict Telnet; remove the maintenance interface or replace it with a properly authenticated channel; restrict clip downloads; rotate the cloud credential; correct startup-script permissions; and require authenticated, integrity-protected updates before enabling the updater. Review the live TLS key's provisioning and rotation.

## Method and limitations

Verdicts use image-relative evidence and reproducible inspection commands. The ARM review is static. The C proof of concept reproduces the boundary overwrite in an isolated struct; it is not execution against device firmware. The complete repository test suite passed in the recorded GitHub Actions matrix on Python 3.10, 3.11 and 3.12. Re-run the suite on the final commit before submission.

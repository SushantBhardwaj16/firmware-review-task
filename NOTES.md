Reviewed against the Kestrel checklist.

# Candidate notes

## Work completed

- **S1 – Finding validation:** Reviewed all 12 reported findings against the firmware filesystem, package database, executable banners, startup scripts, configuration and file permissions. Each verdict includes image-relative evidence and a verification command.
- **S2 – Additional issues:** Recorded three distinct issues not already represented in the original report: the hidden maintenance command, the exposed clip-download service and a credential passed to the cloud-sync process. Related factory-account and TLS-key details are discussed with their S1 findings to avoid double-counting.
- **S3 – Component discovery:** Added ELF banner parsing for the six requested directory families. The implementation records the byte offset of each component name and applies the specified source precedence.
- **S4 – Component corrections:** Replaced prefix-based library matching with exact matching and removed the documentation-based version override. Added regression tests for both failure modes.
- **S5 – C review:** Traced the length-32 boundary case to a terminating NUL written one byte beyond the name buffer, into the adjacent `auth_required` field. The proposed correction rejects lengths greater than or equal to the buffer capacity.
- **S6 – ARM review:** Analysed the maintenance daemon's encoded strings and control flow. The answer records the decoded command, password, XOR byte, listener and shell-execution behaviour.
- **S7 – Standards:** Prepared a CycloneDX SBOM, OpenVEX triage, and CWE/CVSS classifications for the requested findings.

## Remaining uncertainty and limitations

The version of `bootwarden` is **unverified**. Its filename contains `0.9`, but a filename alone is not reliable evidence of the installed version. The related advisory is therefore left `under_investigation` rather than assigned a speculative result.

The two component test modules included with this work passed locally: **15 tests passed**. The complete repository test suite has not yet been run in this environment. The included S5 C proof of concept is an isolated reproduction of the adjacent-field overwrite; it is not a test against a running device. The S6 analysis is static and does not execute the daemon.

## Verification approach

I prioritised evidence that can be independently checked over assumptions based on filenames or documentation. Evidence paths are relative to the unpacked image. Commands in the answer files are intended to be run from the unpacked firmware root unless stated otherwise.

## AI assistance

AI assistance was used to help draft code, organise evidence and support static analysis. I reviewed the resulting artefacts and recorded the checks performed. I understand that I must be able to explain a verdict and the code changes during the review call.

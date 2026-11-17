Reviewed against the Kestrel checklist.

# Candidate notes

## Work completed

- **S1 – Finding validation:** The answer file contains a verdict, image-relative evidence and a reason for each of the 12 findings. F-02 is labelled false as stated because the report cites only `etc/shadow`, which establishes a stored hash but not a shared factory password. The separate factory shadow template has an identical admin hash in this image; that observation is recorded as a limitation and must not be overstated as proof about every manufactured device.
- **S2 – Additional issues:** Three additional issues are documented: the hidden maintenance interface, the clip-download service and a cloud-sync credential in a startup command. Each must be reproducible from the cited image files before submission.
- **S3 – Component discovery:** The scanner checks ELF banners in the six requested directory families, recognises both specified banner forms, records byte offsets and applies the required source precedence.
- **S4 – Component corrections:** Library matching uses exact stems, preventing `libzebra` from being identified as `zpack`. Documentation no longer overrides installed package evidence. Regression tests cover both errors.
- **S5 – C review:** The length-32 boundary case is documented: the check accepts a length equal to the 32-byte array capacity, and the terminating NUL is written one byte beyond the array into the adjacent field in the supplied structure. The proposed correction rejects `len >= NAME_MAX_LEN`.
- **S6 – ARM review:** The answer records the decoded maintenance command and password, XOR key, listener and shell-execution path. This is static analysis; the daemon is not executed.
- **S7 – Standards:** CycloneDX SBOM, OpenVEX triage and CWE/CVSS classifications are included. Validate the final documents and cross-check them against S1 and S2 before submission.

## Remaining uncertainty and limitations

The version of `bootwarden` is **unverified**. Its filename contains `0.9`, but a filename alone is not reliable version evidence. The related advisory remains `under_investigation`.

The complete repository test suite previously passed in GitHub Actions on Python 3.10, 3.11 and 3.12 at commit `b9e56c3d6a15e43ddf549d539490854b72248918`. That result predates the latest edits; the final commit must pass CI before submission. The S5 proof of concept is an isolated reproduction, not a test against running device firmware. The S6 analysis is static and does not execute the daemon.

## Evidence and reproducibility

Evidence paths are relative to the unpacked image. Commands should be run from the repository root unless a ticket says otherwise. Every final verdict must be checked against the original report's cited evidence and the labelling rules. Do not infer a version from a filename or infer fleet-wide provisioning from a single firmware image.

## AI assistance

AI assistance was used to review and edit parts of the code and written answers. The candidate must personally rerun the commands and tests, inspect the evidence, understand every submitted line and be able to explain the reasoning during the review call.

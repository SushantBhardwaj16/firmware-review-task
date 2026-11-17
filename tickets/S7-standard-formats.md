# S7: Say it in the standard formats

**Area:** standards. **Type:** judge. **Points:** 20. Bonus.

Customers and test labs do not read our notes. They read standard formats: an SBOM for what is inside a
product, VEX for which advisories apply to it, CWE for the kind of weakness, and CVSS for how severe it is.
If one of them is new to you, each has a short public specification.

## What to do

1. **SBOM.** `report/sbom.cdx.json` is the engine's list of components, in the CycloneDX format. It has the
   same mistakes as the report. Write the corrected list to `answers/S7-sbom.cdx.json`: a valid CycloneDX
   document with the components that are really in the image, each with its `type` and `name`, and its
   `version` where the image proves one. You may leave out the maker's own programs that carry no version.
2. **VEX.** In `answers/S7-triage.json`, give each of the seven advisories its status for this image. Use the
   status labels of OpenVEX, and for every `not_affected` add the OpenVEX justification label that fits.
   Leave `justification` empty for the other statuses.
3. **CWE and CVSS.** In the same file, for findings F-01 and F-11, give the CWE id that fits best and a CVSS
   vector with its version prefix, 3.1 or 4.0. Classify what the image shows, which can be worse than what
   the report says.

## Done means

- Your SBOM has the fields CycloneDX requires, at the top and in every component.
- Every status agrees with your S1 verdicts and with what you found in S2.

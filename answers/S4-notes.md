# S4 root causes and fixes

1. **False library identification:** the previous implementation used prefix matching, so `libzebra.so.1.2.3` matched the known `z` stem and was reported as zpack. Matching now requires the complete library stem.
2. **Incorrect installed version:** documentation could override the package database version. Documentation is not authoritative evidence of the installed binary, so the override was removed. ELF banners now take precedence when present, followed by package metadata and finally a library filename.

Regression tests reproduce both original errors and verify the corrected behaviour.
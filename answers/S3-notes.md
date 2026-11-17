# S3 implementation notes

The component scanner checks ELF files recursively beneath all six requested directory roots. It recognises both `name/version` and `name version` banners, enforces the specified token boundary and dotted-numeric version format, and records the byte offset at which the component name begins.

Results are deduplicated by component name using the required precedence: banner, package database, then library filename. Traversal and output ordering are deterministic, symbolic links are not followed, and returned paths use forward slashes.

Regression tests cover both banner forms, multiple banners, token boundaries, non-ELF files, nested paths, source precedence and exact library-stem matching.
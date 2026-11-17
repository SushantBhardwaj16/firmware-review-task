# Evidence and proof-of-concept notes

The repository includes two reproducible local demonstrations:

- `poc/s5_adjacent_field_overwrite.c`: compile with `cc -Wall -Wextra -O0 poc/s5_adjacent_field_overwrite.c -o /tmp/s5_poc` and run `/tmp/s5_poc`. The output demonstrates the length-32 terminator write clearing the adjacent flag in the isolated struct layout. It is not a test against device firmware.
- `poc/s6_decode_banner.py`: run with `python3 poc/s6_decode_banner.py`. It decodes the byte sequences established by static inspection; it does not execute the ARM daemon.

The accompanying text output files record the expected results. Screenshots in the downloadable work package are labelled as local demonstrations, not live-device captures. For independent verification, rerun the commands rather than relying on the images.
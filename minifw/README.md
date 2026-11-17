# minifw

A mini engine that unpacks a firmware image and lists the software components inside it.
Python 3.10+, standard library only.

Run everything from the repository root:

```
python3 -m minifw unpack <image> <dir>               # unpack a KFW1 image; also writes <dir>/MANIFEST.txt
python3 -m minifw components <dir>                   # name, version, source, file and byte offset
python3 -m minifw analyse <dir> <advisories.json>    # components and the advisories that affect them, as JSON
python3 -m minifw strings <file>                     # the readable text in a file, with byte offsets
python3 -m minifw elfinfo <file>                     # the class, endian and machine of an ELF file
```

Exit status: 0 on success, 2 with `error: ...` when the input is bad, 64 with the usage text when the
arguments are wrong.

| File | What |
|---|---|
| `unpack.py` | `unpack(image_path, out_dir)`: checks the image, writes the files and the manifest |
| `components.py` | `find_components(root)`: the components of an unpacked image |
| `advisories.py` | `load(path)` and `match(components, advisories)` |
| `tools.py` | `strings(path)` and `elfinfo(path)` |

The tests:

```
python3 -m unittest discover -s minifw/tests -t .
```

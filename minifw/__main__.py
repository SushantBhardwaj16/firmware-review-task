"""Command line: python -m minifw <command> ...

Exit status: 0 on success, 2 with "error: ..." when the input is bad, 64 with
the usage text when the arguments are wrong.
"""

import dataclasses
import json
import os
import sys

from . import advisories, tools
from .components import find_components
from .unpack import unpack

USAGE = """usage: python -m minifw <command> ...

  unpack <image> <dir>               unpack a KFW1 image into a folder
  components <dir>                   list the components in an unpacked image
  analyse <dir> <advisories.json>    components and the advisories that affect them, as JSON
  strings <file>                     the readable text in a file, with byte offsets
  elfinfo <file>                     the class, endian and machine of an ELF file
"""


def _root(folder: str) -> str:
    if not os.path.isdir(folder):
        raise ValueError(f"{folder}: not a folder")
    return folder


def _unpack(image: str, folder: str) -> None:
    print(f"unpacked {len(unpack(image, folder))} entries into {folder}")


def _components(folder: str) -> None:
    for component in find_components(_root(folder)):
        print(f"{component.name:<18} {component.version:<10} {component.source:<13} {component.path} @ {component.offset}")


def _analyse(folder: str, advisories_path: str) -> None:
    components = find_components(_root(folder))
    affected = advisories.match(components, advisories.load(advisories_path))
    print(json.dumps({"components": [dataclasses.asdict(c) for c in components], "affected": affected}, indent=2))


def _strings(path: str) -> None:
    for offset, text in tools.strings(path):
        print(f"{offset:>8} {text}")


def _elfinfo(path: str) -> None:
    for key, value in tools.elfinfo(path).items():
        print(f"{key}: {value}")


COMMANDS = {
    "unpack": (_unpack, 2),
    "components": (_components, 1),
    "analyse": (_analyse, 2),
    "strings": (_strings, 1),
    "elfinfo": (_elfinfo, 1),
}


def main(args: list[str] | None = None) -> int:
    args = sys.argv[1:] if args is None else args
    command, count = COMMANDS.get(args[0] if args else "", (None, 0))
    if command is None or len(args) - 1 != count:
        print(USAGE, file=sys.stderr, end="")
        return 64
    try:
        command(*args[1:])
        sys.stdout.flush()
    except BrokenPipeError:  # the reader, such as head, has seen enough
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

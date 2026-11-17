# Primer: what is inside a firmware image

Read this once. It takes ten minutes.

## A firmware image

A device such as a camera runs a small Linux system. The maker ships that whole system as one file, the
firmware image. Inside it is a root file system: folders and files, like on any Linux computer.

This task's image uses a made-up container format. You do not need to know it: the engine unpacks it.

```
python3 -m minifw unpack images/kestrel-dome2-1.4.2.bin work
```

That writes the files under `work/`, and `work/MANIFEST.txt`: one line per file with its permissions (mode),
size and path. Read permissions there, because not every operating system keeps them when files are unpacked.

## Where things usually are

| Path | What you find there |
|---|---|
| `etc/` | Settings: accounts (`passwd`, `shadow`), services, keys |
| `etc/init.d/` | Start-up scripts. They run at boot, in the order of their names. What a device starts by itself is decided here |
| `etc/inittab` | What runs on the device's consoles |
| `bin/`, `sbin/`, `usr/bin/`, `usr/sbin/` | Programs |
| `lib/`, `usr/lib/` | Libraries: code that programs share |
| `lib/modules/` | Kernel modules: parts of the kernel shipped as files |
| `boot/` | The boot loader, and often the kernel's build settings |
| `var/lib/pkgs/status` | The package database: what the maker's build system says it installed |
| `usr/share/` | Documents, web pages, defaults |

## Programs are not text

A program or a library is a binary file in the ELF format. You cannot read it like a script, but it holds
readable pieces of text: messages, option names, and often a line that names the program and its version.

```
python3 -m minifw strings work/usr/sbin/<program>     # the readable text inside, with byte offsets
python3 -m minifw elfinfo work/usr/sbin/<program>     # what kind of ELF file it is
```

If you have the usual tools (`strings`, `grep`, `file`, `readelf`), use them: they do the same job.

## Components, versions and advisories

A **component** is one piece of software in the image, with a **version**. An **advisory** says: this
component, in these versions, has this weakness, sometimes only under a **condition** (for example, only when
a feature is built in).

An advisory applies to an image only when all of these hold:

1. the component is really in the image;
2. its version is in the affected range;
3. the advisory's condition, if it has one, holds for this image.

An engine can get any of the three wrong. Checking them against the files is the job.

## Reading what you find

- **Comments.** In scripts, `etc/inittab` and most settings files, a line that starts with `#` does nothing.
- **Permissions.** A mode such as `0755` gives, in its last three digits, the rights of the owner, the group
  and everyone else. 7 is read, write and run; 5 is read and run; 4 is read only. A link always shows as
  `0777` with size 0: that says nothing about the file it points to.
- **Accounts.** In `etc/shadow`, the second field of a line is the password. `*` or `!` means nobody can sign
  in with a password. A long text starting with `$` is the hash of a password.
- **Keys and certificates.** A PEM file is text whose first line names what it holds. A certificate is
  public. A private key must stay secret.

## Looking inside a program (ticket S6)

`strings` shows only text that is stored as it is. To see what a program does, a disassembler turns its
bytes back into instructions: Ghidra and radare2 are free, and `objdump -d` is enough for a small program.
The programs in this image are for 32-bit ARM, little-endian.

## Standard formats (ticket S7)

- **SBOM:** a list of the components inside a product. CycloneDX and SPDX are the two common formats.
- **VEX:** a statement, per advisory, of whether it affects a product, and why not when it does not.
- **CWE:** a public catalogue of kinds of weakness, each with a number.
- **CVSS:** a way to score how severe a vulnerability is, written as a short vector.

## Kernel settings

`boot/config` lists how the kernel was built. `CONFIG_SOMETHING=y` means the feature is built in, `=m` means it
is shipped as a module file, and `# CONFIG_SOMETHING is not set` means it is not there at all.

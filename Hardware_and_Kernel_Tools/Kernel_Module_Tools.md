# Kernel Module Tools

## Description:

## Table of Contents

- `lsmod`
- `modinfo`
- `modprobe`

# Command: lsmod (List Modules)

## Description: Displays information on the currently loaded kernel modules on a Linux system

## Syntax

- `lsmod`

## Options

- `No flags or options`

# Command: modinfo

## Description: Lists detailed information about a given Linux kernel module

## Syntax

- `modinfo [Options] [module_file] | module_name`

## Options

| Options | Descriptions | Examples |
|---------|--------------|----------|
| `-a` | Shows author of the module | `modinfo -a i915` |
| `-d` | Show description | `modinfo -d e1000e` |
| `-l` | Show license type | `modinfo -l snd_hda_intel` |
| `-p` | Show parameters the module accepts | `modinfo -p snd_hda_intel` |
| `-n` | Show the filename of the module | `modinfo -n i915` |
| `-F<field>` | Displays only a specific field | `modinfo -F license i915` |
| `-k<kernel>` | Query module info for a specific kernel version | `modinfo -k 6.8.0-31-generic i915` |
| `-O` | Seperate output fields with NUL instead of newline | `modinfo -O i915` |

## Examples

## Retrieve information about a module by name

```bash
modinfo i915
```

### Breakdown

| Breakdown | Description |
|-----------|-------------|
| `modinfo` | Kernel command |
| `i915` | Target module |

# Command: modprobe

## Description: Used to add or remove kernel modules intelligently

## Syntax

- `modprobe [Options] <module_name> [parameters ...]`

## Options

| Options | Descriptions | Examples |
|---------|--------------|----------|
| `-a` | Inserts all listed modules | `modprobe -a i915 e1000e` |
| `-r` | Remove a module | `modprobe -r i915` |
| `-r -a` | Remove multiple modules | `modprobe -r -a e1000e i915` |
| `--show`or`-n` | Dry-run | `modprobe -n i915` |
| `-v` | Verbose mode | `modprobe -v` |
| `--first-time` | Fail if module already loaded | `modprobe --first-time i915` | 
| `--remove-dependencies` | Remove a module and its unused dependencies | `modprobe -r --remove-dempendencies snd_hda_intel` |
| `--set-version<version>` | Act as if running under a specific kernel version | `modprobe --set-version 5.15.0 i915` |
| `--dirname` | Show the base directory of modules | `modprobe --dirname` |
| `--show-depends` | Show all modules that would be inserted | `modprobe --show-depends e1000e` |
| `--quiet` | Supress errors | `modprobe --quiet badmodule` |
| `-C<file>` | Use alternate config file | `modprobe -C /tmp/custom.conf e1000e` |

## Examples

## Remove a module

```bash
sudo modprobe -r i915
```

### Breakdown

| Breakdown | Description |
|-----------|-------------|
| `sudo` | Superuser command |
| `modprobe` | Kernel command |
| `-r` | Remove multiple modules |
| `i915` | Target module |
# Hardware Discovery

## Description: Commands involved with Discovering Hardware information

## Tables of Contents

- `lspci`
- `lsusb`
- `sensors`
- `hwinfo`

# Command: lspci

## Description: Lists all PCI (Perioheral Component Interconnect) buses and the devices connected to them

## Syntax

- `lspci [Options]`

## Options

| Options | Descriptions | Examples |
|---------|--------------|----------|
| `-v` | Verbose mode | `lspci -v` |
| `-vv` | Extra Verbose Mode | `lspci -vv` |
| `-n` | Shows numeric IDs instead of text | `lspci -n` |
| `-nn` | Both numeric and human readable form | `lspci -nn` |
| `-xxx` | Detailed dump of config space | `lspci -xxx` |
| `-k` | Show kernel driver in use | `lspci -k` |
| `-mm` | Show machine-readable/ scripting format | `lspci -mm` |
| `-t` | Tree view | `lspci -t` |

## Examples

## Show IDs instead of text

```bash
lspci -n
```

### Breakdown

| Breakdown | Description |
|-----------|-------------|
| `lspci` | Discovery command |
| `-n` | Directs to show IDs instead of text  for output |

# Command: lsusb

## Description: Used to inspect USB devices. Lists information about USB buses and devices connected to the system

## Syntax

- `lsusb [Options]`

## Options

| Options | Descriptions | Examples |
|---------|--------------|----------|
| `(none)` | Lists all USB buses and devices with their IDS and vendor/product strings | `lsusb` |
| `-v` | Verbose Mode | `lsusb -v` | 
| `-s [[bus]:[device]]` | Shows only devices on a specific bus and/or device number | `lsusb -s 001:002` |
| `-d [vendor]:[product]` | Shows only devices matching the given vendor ID and product ID | `lsusb -d 046d:c543` |
| `-t` | Displays USB devices as a tree view | `lsusb -t` |
| `-v -s` | Great for troubleshooting or reverse-engineering | `sudo lsusb -s 001:002 -v` |

## Examples

## USB Port Tree layout

```bash
lsusb -t
```

### Breakdown

| Breakdown | Description |
|-----------|-------------|
| `lsusb` | Discovery command |
| `-t` | Displays USB devices as a tree view |

# Command: sensors

## Description: Monitors hardware along with related metrics in real time

## Syntax

- `sensors [Options]`

## Options

|Options | Descriptions | Examples |
|--------|--------------|----------|
| `(none)` | Shows all detected sensor readings | `sensors` |
| `-s`or`--set` | Apply settings from `/etc/sensors.conf` | `sudo sensors -s` |
| `-f`or`--fahrenheit` | Display temperature in Fahrenheit instead of Celsius | `sensors -f` |
| `-A`or`--no-adapter` | Hides 'Adapter' lines in the output, showing only sensor readings | `sensors -A` |
| `-u`or`--units` | Displays raw sensor values | `sensors -u` | 
| `-j`or`--json` | Outputs results in JSON format | `sensors -j` |
| `-j<chip>` | JSON output for a specific chip only | `sensonrs -j coretemp-isa 0000` |
| `-jA` | JSON output with no adapter lines | `sensors -jA` |
| `-c<file>`or`--config-file=<file>` | Use an alternate config file | `sensors -c /etc/sensors3.conf` |

## Examples

## Check CPU temps in Fahrenheit

```bash
sensors -f
```

### Breakdown

| Breakdown | Description |
|-----------|-------------|
| `sensors` | Discovery command |
| `-f` | Directs to check CPU temps |

# Command: hwinfo

## Description: Probes and displays detailed harware information

## Syntax

- `hwinfo [Options]`

## Options

| Options | Descriptions | Examples |
|---------|--------------|----------|
| `(none)` | Shows a complete dump of hardware info | `hwinfo` | 
| `--short` | Summarized hardware list | `hwinfo --short` |
| `--very-verbose` | Ultra-detailed verbose mode | `hwinfo --very-verbose` |
| `--all` | Shows all available info | `hwinfo --all` |
| `--cpu` | Show only CPU details | `hwinfo -cpu` | 
| `--disk` | Show only storage devices | `hwinfo --disk` |
| `--usb` | Show only USB devices | `hwinfo --usb` | 
| `--gfxcard` | Show details of the graphics card | `hwinfo --gfxcard` |
| `--netcard` | Show details of network interfaces | `hwinfo --netcard` | 
| `--sound` | Show sound card info | `hwinfo --sound` |
| `--printer` | Show printers detected | `hwinfo --printer` |
| `--monitor` | Show details of connected monitors | `hwinfo --monitor` |
| `--mouse` | Show details about the mouse | `hwinfo --mouse` |
| `--keyboard` | Show keybaord device info | `hwinfo --keyboard` |
| `--bios` | Shows BIOS/UEFI details | `hwinfo --bios` |
| `--framebuffer` | Show framebuffer | `hwinfo --framebuffer` |
| `--partition` | Show partition table info | `hwinfo --partition` |
| `--bridge` | Show info aobut PCI/USB/ISA bridges | `hwinfo --bridge` |
| `--memory` | Show RAM info | `hwinfo --memory` |
| `--ide` `--cdrom` `--scsi` `--pcmcia` | All show info on specific storage buses/devices | `hwinfo --cdrom` |
| `--listmd` | Show RAID devices | `hwinfo --listmd` |
| `--wlan` | Shows wireless LAN devices | `hwinfo --wlan` |
| `--bluetooth` | Show Bluetooth devices | `hwinfo --bluetooth` |
| `--debug<N>` | Set debug level 0-10 | `hwinfo --cpu --debug 2` |
| `--log<file>` | Save output to a log file | `sudo hwinfo --all --log hwinfo_full.txt` |

## Examples

## Check GPU vendor and driver

```bash
hwinfo --gfxcard
```

### Breakdown

| Breakdown | Description |
|-----------|-------------|
| `hwinfo` | Discovery command |
| `--gfxcard` | Directs to check GPU vendor and driver |

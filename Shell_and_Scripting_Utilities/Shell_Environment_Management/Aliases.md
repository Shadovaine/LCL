# Alias Overview

## Description: Overview of what aliases are, what they do, and how they help a user

# Why are aliases important?

| Alias Characteristic | Description |
|----------------------|-------------|
| `Speed` |Saves keystrokes and time, especially for commands you type often |
| `Safety` | Prevents costly typos |
| `Customization` | Tailor your terminal to match your workflow. |
| `Readability` | Makes complex commands easier to remember and share |

## Pro Tips

- `Hackers and sysadmins often create aliases for pentesting tools, log monitoring, or jumping into certain directories`
- `Instead of typing `rm -rf /path/to/something`; you can create a safer alias `alias rm='rm -i``
- `The -i flag asks before deleting files. (This has saved countless beginners from nuking their systems.)`
- `Red-teamers use aliases to create quick commands for common tasks like scanning (alias scan='nmap -sV -Pn') or to hide their tracks`
- `But as a defender, you can use them to automate monitoring tools and harden systems`

# When should you set one up

## You set up an alias when You use a command frequently

- `ls -alh` is long to type, so make `alias ll=ls -alh``

## You want safer defaults

- `alias cp=cp -i`
- `To make cp interactive, asking before overwriting files`

## Update and upgrade apt packages

- `sudo apt update && sudo apt upgrade -y`

- `alias update=`sudo apt update && sudo apt upgrade -y`

# How do you set up an alias

# Temporary (lasts only in current session)

- `alias gs=git status`

# Permanent (loads every time you open terminal)

## To make an alias named `alias gs` to represent `git status`

- Step 1: Edit your shell config file (~/.bashrc for bash, ~/.zshrc for zsh) with a text editor `nano` or `vim`

    - `nano ~/.bashrc`

- Step 2: Add the following to the bottom of the shell config file 

    - `alias gs=git status`

- Step 3: Save and Reload (nano = Ctl + o, ENTER, Ctl + x; vim wq!, ENTER)

    - `source ~/.bashrc`

# Common Alias Examples

- alias ll='ls -alF'
- alias la='ls -A'
- alias ..='cd ..'
- alias ...='cd ../..'
- alias cls='clear'
- alias update='sudo apt update && sudo apt upgrade -y'
- alias grep='grep --color=auto'
- alias h='history'

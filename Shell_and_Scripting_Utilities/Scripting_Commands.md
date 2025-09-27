# Shell and Scripting Utilities

## Description: Commands involved with developing, modifying, and running scripts and shell Emulators

## Table of Contents

- `echo`
- `read`
- `export`
- `history`
- `cron`
- `at`
- `zi`
- `which`
- `type`
- `set`
- `bash`
- `exit`

# Command: echo

## Description: Print text or variables to the terminal

## Syntax

- `echo [OPTIONS] [STRING...]`

## Options

-n	Do not output the trailing newline.
-e	Enable interpretation of backslash escapes.

### Examples

### Print text

echo "Hello, dragon rider!"

### Print without newline

echo -n "Enter your name: "

### Print with escape characters

echo -e "Line 1\nLine 2\tTabbed"

### Print environment variable

echo $HOME

# Command: read

## Description: Read a line of input from the user

## Syntax

- `read [OPTIONS] VARIABLE`

### Options

-p PROMPT	Display a prompt before reading input.
-s	Silent mode (hide input, e.g., passwords).

### Examples

### Read user input

read name
echo "Hello, $name!"

### Prompt for input

read -p "Enter your username: " username

### Silent read (for passwords)

read -sp "Enter password: " password

# Command: export

## Description: Set environment variables for the current session

## Syntax

- `export VARIABLE=VALUE`

### Options

### Examples

### Set a variable

export EDITOR=nano

### Set PATH

export PATH=$PATH:/opt/myapp/bin

### Make a variable available to child processes

export LANG=en_US.UTF-8

# Command: History

## Description: Show command history

## Syntax

- `history [OPTIONS]`

### Options

(no args)	List command history.
-c	Clear the history.
!N	Run command number N from history.

### Examples

### Show last 10 commands

history | tail -10

### Re-run command #42

!42

### Clear history

history -c

# Command: cron

## Description: Runs scheduled tasks repeatedly at specified times. You use crontab to manage your cron jobs

## Syntax

- `crontab [OPTIONS]`

### Options

-e	Edit the crontab file.
-l	List current user’s cron jobs.
-r	Remove current user’s crontab.

### Examples

### Edit cron jobs

crontab -e

### List cron jobs

crontab -l

### Example cron job (run backup.sh daily at 2AM)

0 2 * * * /home/jake/scripts/backup.sh

# Command: at

## Description: Schedule a one-time task to run in the future

## Syntax

- `at TIME`

### Options

-l	List pending at jobs.
-c JOB	View commands for a scheduled job.
-r JOB	Remove a scheduled job.

### Examples

### Schedule task to run at 5 PM

at 17:00

### List scheduled tasks

atq

### Remove job #2

atrm 2

# Command: zi

## Description: Fast, modular Zsh plugin manager

## Syntax

- `zi load username/repo`

### Options

### Examples


- zi load zsh-users/zsh-autosuggestions

# Command: which

## Descriptions:

## Syntax

### Options

### Examples

# Command: type

## Description:

## Syntax

### Options

### Examples

# Command: set

## Description:

## Syntax

### Options

### Examples

# Command: bash

## Descriptions:

## Syntax

### Options

### Examples

# Command: exit

## Description:

## Syntax

### Options

### Examples

## **lazygit – TUI interface for Git inside terminal**
	•	Category: Git / Dev Tooling
	•	Syntax: lazygit
	•	Features:
	•	View branches, diffs, stashes
	•	Commit & push without typing Git CLI



## **zellij – Terminal multiplexer (like tmux, but modular)**
	•	Category: Workflow / DevOps Enhancement
	•	Syntax: zellij
	•	Features:
	•	Tabbed terminal interface
	•	Resize panes, plugins, floating windows
	•	Beginner-friendly, config file is sane
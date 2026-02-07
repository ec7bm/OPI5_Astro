#!/bin/bash
# AstroOrange Wizard Launcher with Privilege Escalation
# Preserves X11 DISPLAY for GUI while running with sudo

# Preserve X11 environment
export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

# Allow root to access the X server
xhost +local:root 2>/dev/null

# Run the wizard with sudo
sudo -E python3 "$@"

# Revoke root access after execution
xhost -local:root 2>/dev/null

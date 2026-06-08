#!/bin/bash
# Switch to rv window in anny tmux session
SESSION="anny"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux select-window -t "$SESSION:rv"
    guake --show
else
    ~/Documents/coding/anny/streamdeck/anny-start.sh
fi

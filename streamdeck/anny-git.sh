#!/bin/bash
# Switch to git window in anny tmux session
SESSION="anny"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux select-window -t "$SESSION:git"
    guake --show
else
    ~/Documents/coding/anny/streamdeck/anny-start.sh
fi

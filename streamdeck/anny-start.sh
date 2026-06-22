#!/bin/bash
# Bootstrap the anny tmux session
# Run this once to set everything up, or call it from your shell rc

SESSION="anny"
PROJECT="/home/mswed/Documents/coding/anny"

# Only create if session doesn't already exist
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION" -n nvim -c "$PROJECT"
  tmux send-keys -t "$SESSION:nvim" "source .venv/bin/activate" Enter
  tmux send-keys -t "$SESSION:nvim" "nvim ." Enter

  tmux new-window -t "$SESSION" -n git -c "$PROJECT"
  tmux send-keys -t "$SESSION:git" "git status" Enter

  tmux new-window -t "$SESSION" -n rv -c "$HOME"
  tmux send-keys -t "$SESSION:rv" "~/openrv.sh" Enter
fi

# Attach in guake
guake --show
guake -e "tmux attach -t $SESSION"

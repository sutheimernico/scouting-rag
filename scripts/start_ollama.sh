#!/usr/bin/env bash
# Start the user-space Ollama server if it is not already running.
# (No systemd: Ollama was installed without sudo to ~/.local — see README.)
set -euo pipefail

OLLAMA_BIN="$HOME/.local/bin/ollama"

if curl -s --max-time 2 http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "ollama already running"
    exit 0
fi

nohup "$OLLAMA_BIN" serve >"$HOME/.ollama/serve.log" 2>&1 &
sleep 2
curl -s --max-time 5 http://localhost:11434/api/tags >/dev/null && echo "ollama started (log: ~/.ollama/serve.log)"

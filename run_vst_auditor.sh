#!/bin/bash
# Ableton VST Auditor - macOS/Linux Launcher
# Make executable with: chmod +x run_vst_auditor.sh
# Run with: ./run_vst_auditor.sh

echo "Starting Ableton VST Auditor..."
echo

# Check if python3 is available
if command -v python3 &> /dev/null; then
    echo "Using python3 command"
    python3 ableton_vst_audit.py
elif command -v python &> /dev/null; then
    # Check if python is actually Python 3
    python_version=$(python -c 'import sys; print(sys.version_info.major)')
    if [ "$python_version" = "3" ]; then
        echo "Using python command (Python 3)"
        python ableton_vst_audit.py
    else
        echo "ERROR: Python 3 required, but python command is Python 2"
        echo "Please install Python 3 or use python3 command"
        exit 1
    fi
else
    echo "ERROR: Python not found!"
    echo "Please install Python 3:"
    echo "  macOS: Install from https://python.org/downloads/ or use 'brew install python3'"
    echo "  Linux: Use your package manager (e.g., 'sudo apt install python3')"
    exit 1
fi

echo
echo "VST Auditor finished."
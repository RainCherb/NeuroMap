#!/bin/bash

cd "$(dirname "$0")"

python -m pip install -e . 2>&1 | head -100

if [ $? -eq 0 ]; then
    echo "✅ NeuroMap installed successfully!"
    echo "You can now run: neuro-map --help"
else
    echo "❌ Installation failed"
    echo "Please install manually with: python -m pip install -e ."
fi

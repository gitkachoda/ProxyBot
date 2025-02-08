#!/bin/bash
echo "🚀 Starting Proxy Bot..."
python3 proxychor.py &
waitress-serve --listen=0.0.0.0:5000 proxychor:app

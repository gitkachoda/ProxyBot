#!/bin/bash
echo "🚀 Starting Proxy Bot & Flask Server..."
gunicorn -b 0.0.0.0:10000 proxychor:app &  # Flask ko background me run karega
python3 proxychor.py  # Telegram bot ko start karega

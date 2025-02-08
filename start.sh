#!/bin/bash

# ✅ Run the bot and Flask server with Gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT proxychor:app

#!/bin/bash

# ✅ Flask aur bot ko Gunicorn ke saath run karo
exec gunicorn --workers 4 --bind 0.0.0.0:$PORT proxychor:app

python3 proxychor.py & 
waitress-serve --listen=0.0.0.0:$PORT proxychor:app

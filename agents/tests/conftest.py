import os

# Nei test la sessione dell'API non scrive il registro su file.
os.environ.setdefault("NAPOLES_REGISTRO", "")

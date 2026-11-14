import os

# Nei test la sessione dell'API non scrive il registro su file.
os.environ.setdefault("NAPOLES_REGISTRO", "")

# Nei test nessuna chiamata al modello linguistico, anche se l'ambiente ha una chiave.
os.environ["LLM_PROVIDER"] = "finto"

"""Nomi leggibili dei luoghi e degli agenti, per ciò che vedono operatore e cittadini."""

LUOGHI = {
    "piazzale_tecchio": "Piazzale Tecchio",
    "viale_giochi_del_mediterraneo": "Viale Giochi del Mediterraneo",
    "via_terracina": "Via Terracina",
}

AGENTI = {
    "rischio": "Rischio",
    "mobilita": "Mobilità",
    "folla": "Folla",
    "comunicazione": "Comunicazione",
}


def luogo(identificativo: str) -> str:
    return LUOGHI.get(identificativo, identificativo.replace("_", " "))


def agente(ambito: str) -> str:
    return AGENTI.get(ambito, ambito)

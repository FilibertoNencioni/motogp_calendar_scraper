from datetime import datetime

class Circuit:
    pk_circuit: int
    guid: str
    name: str
    country: str
    flag_path: str | None
    placeholder_path: str | None
    doi: datetime | None
    dou: datetime | None

    def __init__(self, pk_circuit: int, guid: str, name: str, country: str, flag_path: str | None, placeholder_path: str | None, doi: datetime | None, dou: datetime | None):
        self.pk_circuit = pk_circuit
        self.guid = guid
        self.name = name
        self.country = country
        self.flag_path = flag_path
        self.placeholder_path = placeholder_path
        self.doi = doi
        self.dou = dou
        
    
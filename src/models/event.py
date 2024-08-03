from datetime import datetime

class Event:
    pk_event: int
    fk_circuit: int
    guid: str
    name: str
    kind: str 
    season: str
    start_date: datetime
    end_date: datetime
    doi: datetime
    dou: datetime | None

    def __init__(self, pk_event: int, fk_circuit: int, guid: str, name: str, kind: str, season: str, start_date: datetime, end_date: datetime, doi: datetime | None, dou: datetime | None):
        self.pk_event = pk_event
        self.fk_circuit = fk_circuit
        self.guid = guid
        self.name = name
        self.kind = kind
        self.season = season
        self.start_date = start_date
        self.end_date = end_date
        self.doi = doi
        self.dou = dou
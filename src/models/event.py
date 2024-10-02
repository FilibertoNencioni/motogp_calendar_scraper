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

    @staticmethod
    def from_motogp_service(parsed_json: dict, fk_circuit: int):
        return Event(
            pk_event=0,
            fk_circuit=fk_circuit,
            guid=parsed_json["id"],
            name=str(parsed_json["name"]).strip(),
            kind=parsed_json["kind"],
            season= str(parsed_json["season"]["year"]),
            start_date=datetime.fromisoformat(parsed_json["date_start"]),
            end_date=datetime.fromisoformat(parsed_json["date_end"]),
            doi=None,
            dou=None
        )
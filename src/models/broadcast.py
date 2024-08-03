from datetime import datetime

class Broadcast:
    pk_broadcast: int
    fk_event: int
    fk_broadcaster: int
    fk_category: int
    guid: str
    name: str
    kind: str
    is_live: bool
    start_date: datetime
    end_date: datetime
    doi: datetime | None
    dou: datetime | None

    def __init__(self, pk_broadcast: int, fk_event: int, fk_broadcaster: int, fk_category: str, guid: str, name: str, kind: str, is_live: bool, start_date: datetime, end_date: datetime, doi: datetime | None, dou: datetime | None):
        self.pk_broadcast = pk_broadcast
        self.fk_event = fk_event
        self.fk_broadcaster = fk_broadcaster
        self.fk_category = fk_category
        self.guid = guid
        self.name = name
        self.kind = kind
        self.is_live = is_live
        self.start_date = start_date
        self.end_date = end_date
        self.doi = doi
        self.dou = dou
from datetime import datetime
from enum import Enum

class Broadcaster:
    pk_broadcaster: int
    name: str
    doi: datetime | None
    dou: datetime | None

    def __init__(self, pk_broadcaster: int, name: str, doi: datetime | None, dou: datetime | None):
        self.pk_broadcaster = pk_broadcaster
        self.name = name
        self.doi = doi
        self.dou = dou

    


class BroadcasterEnum(Enum):
    MOTOGP = Broadcaster(1, "Motogp", None, None),
    TV8 = Broadcaster(2, "Tv8", None, None)

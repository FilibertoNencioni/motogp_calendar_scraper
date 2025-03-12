from datetime import datetime
from common.enum.broadcaster_enum import BroadcasterEnum
from common.enum.kind_enum import KindEnum
class Broadcast:
    pk_broadcast: int
    fk_event: int
    fk_broadcaster: int
    fk_category: int | None
    fk_kind: int | None
    guid: str | None
    name: str
    is_live: bool
    start_date: datetime
    end_date: datetime | None
    doi: datetime | None
    dou: datetime | None

    def __init__(self, pk_broadcast: int, fk_event: int, fk_broadcaster: int, fk_category: int | None, fk_kind:int | None, guid: str | None, name: str, is_live: bool, start_date: datetime, end_date: datetime | None, doi: datetime | None, dou: datetime | None):
        self.pk_broadcast = pk_broadcast
        self.fk_event = fk_event
        self.fk_broadcaster = fk_broadcaster
        self.fk_category = fk_category
        self.fk_kind = fk_kind
        self.guid = guid
        self.name = name
        self.is_live = is_live
        self.start_date = start_date
        self.end_date = end_date
        self.doi = doi
        self.dou = dou


    @staticmethod
    def from_motogp_service(parsed_json: dict, fk_event: int, fk_category: int):
        pk_kind = None
        if parsed_json["kind"] is not None:
            if parsed_json["kind"] == "RACE":
                pk_kind = KindEnum.RACE.value
            elif parsed_json["kind"] == "QUALIFYING":
                pk_kind = KindEnum.QUALIFYING.value
        
        return Broadcast(
            pk_broadcast=0,
            fk_event=fk_event,
            fk_broadcaster=BroadcasterEnum.MOTOGP_OFFICIAL.value,
            fk_category=fk_category,
            fk_kind=pk_kind,
            guid=parsed_json["id"],
            name=parsed_json["name"],
            is_live=True,
            start_date=datetime.fromisoformat(parsed_json["date_start"]),
            end_date= None if parsed_json["date_end"] is None else datetime.fromisoformat(parsed_json["date_end"]),
            doi=None,
            dou=None
        )
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
        
    @staticmethod
    def from_motogp_service(parsed_json: dict):
        assets: list = parsed_json["assets"]
        
        #finding flag path
        flag_path = None
        for asset in assets:
            if asset["type"] == "FLAG":
                flag_path = asset["path"]
                break

        #finding placeholder path
        placeholder_path = None
        for asset in assets:
            if asset["type"] == "BACKGROUND":
                placeholder_path = asset["path"]
                break

        return Circuit(
            pk_circuit=0,
            guid=parsed_json["circuit"]["id"],
            name=parsed_json["circuit"]["name"],
            country=parsed_json["circuit"]["country"],
            flag_path=flag_path,
            placeholder_path=placeholder_path,
            doi=None,
            dou=None
        )
    
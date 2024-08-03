from datetime import datetime

class Category:
    pk_category: int
    guid: str
    name: str
    acronym: str
    doi: datetime | None
    dou: datetime | None

    def __init__(self, pk_category: int, guid: str, name: str, acronym: str, doi: datetime | None, dou: datetime | None):
        self.pk_category = pk_category
        self.guid = guid
        self.name = name
        self.acronym = acronym
        self.doi = doi
        self.dou = dou
from dataclasses import dataclass
import datetime


@dataclass
class Purchase:
    # id and date will be assigned by db
    id: int = -1
    date: datetime.datetime = datetime.datetime.now()
    info: str = ""
    status: str = "Pending"
    bought_by: int = -1
    verified_by: int = -1
    productid_count: dict[int, int] | None = None

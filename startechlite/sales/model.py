from dataclasses import dataclass
import datetime

from startechlite.product.model import Product


@dataclass
class Purchase:
    # id and date will be assigned by db
    id: int = -1
    purchase_date: datetime.datetime = datetime.datetime.now()
    approval_date: datetime.datetime | None = None
    info: str = ""
    address: str = ""
    bought_by: int = -1
    productid_count: dict[int, int] | None = None

    # used when we render products from purchase (order history)
    _products: list[Product] | None = None

    @property
    def due_date(self):
        """If admin has approved, due date is approval date + 7 days. If admin has not approved, due date
        is current date + 7 days.

        Returns:
            datetime.datetime: tentative due date
        """        
        if self.approval_date:
            return self.approval_date + datetime.timedelta(days=7)
        else:
            return datetime.datetime.now() + datetime.timedelta(days=7)

    @property
    def is_shipped(self) -> bool:
        return self.due_date < datetime.datetime.now()

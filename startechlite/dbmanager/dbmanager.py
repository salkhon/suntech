import flask_paginate
import re

from startechlite.product.model import Item


class DBManager:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls, *args, **kwargs)
            cls.instance._establish_db_connection()
        return cls.instance

    def _establish_db_connection(self):
        pass

    def _pagination_indices(self, pagination: flask_paginate.Pagination) -> tuple[int, int]:
        infostr = pagination.info  # div tag but we only need to extract the ints
        start_index, end_index, _ = [int(num) for num in re.findall(r"[0-9]+", infostr)]
        num_items = end_index - start_index + 1
        return (start_index, num_items)

    def get_components(self, page: int = 1, per_page: int = 15) -> tuple[list[Item], flask_paginate.Pagination]:
        # TODO:
        # query basic attrs of the items for preliminery display
        # also need to query total number of items for pagination
        total_num_items = 47  # query this
        pagination = flask_paginate.Pagination(
            page=page, per_page=per_page, total=total_num_items)
        start_index, num_items = self._pagination_indices(
            pagination)  # for querying
        items = [Item("Some item title", "Some item name", "Some Brand", "#", [
            "Property1: Something", "Property2: Something", "Property3: Something"])] * num_items

        return (items, pagination)

    def get_item_by_name(self, itemname: str) -> Item:
        # TODO:
        # query item with itemname, so all detailed info is available
        item = Item(itemname, itemname, "Some Brand", "#", [
                    "Property1: Something", "Property2: Something", "Property3: Something"])
        return item

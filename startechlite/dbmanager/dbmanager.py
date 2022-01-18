import flask_paginate
import re
from startechlite.constants import *
import startechlite
from startechlite.account.model import User
from startechlite.product.model import Product


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
        start_index, end_index, _ = [int(num)
                                     for num in re.findall(r"[0-9]+", infostr)]
        num_items = end_index - start_index + 1
        return (start_index, num_items)

    def get_product_by_handle(self, handle: str) -> Product:
        # TODO: query product by handle, and populate its model class
        product = Product(handle, "Name", "Category", "Subcategory", "Brand", 1.0, 0.1, 2022, 5, ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
            "Property 1": "Awesome",
            "Property 2": "Great stuff",
            "Property 3": "Nice"
        })
        return product

    def get_category(self, category: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        # TODO:
        # query basic attrs of the items for preliminery display
        # also need to query total number of items for pagination
        total_num_items = 47  # query this
        pagination = flask_paginate.Pagination(
            page=page, per_page=per_page, total=total_num_items)
        start_index, num_items = self._pagination_indices(
            pagination)  # for querying

        items = [Product("product-handle", "Name", "Category", "Subcategory", "Brand", 1.0, 0.1, 2022, 5, ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
            "Property 1": "Awesome",
            "Property 2": "Great stuff",
            "Property 3": "Nice"
        })] * num_items

        return (items, pagination)

    def get_category_subcategory(self, category: str, subcategory: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        total_num_items = 47
        pagination = flask_paginate.Pagination(
            page=page, per_page=per_page, total=total_num_items)
        start_index, num_items = self._pagination_indices(
            pagination)

        items = [Product("product-handle", "Name", "Category", "Subcategory", "Brand", 1.0, 0.1, 2022, 5, ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
            "Property 1": "Awesome",
            "Property 2": "Great stuff",
            "Property 3": "Nice"
        })] * num_items
        return (items, pagination)

    def get_category_subcategory_brand(self, category: str, subcategory: str, brand: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        total_num_items = 47
        pagination = flask_paginate.Pagination(
            page=page, per_page=per_page, total=total_num_items)
        start_index, num_items = self._pagination_indices(
            pagination)

        items = [Product("product-handle", "Name", "Category", "Subcategory", "Brand", 1.0, 0.1, 2022, 5, ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
            "Property 1": "Awesome",
            "Property 2": "Great stuff",
            "Property 3": "Nice"
        })] * num_items
        return (items, pagination)

    @startechlite.login_manager.user_loader
    def get_user(self, userid: int) -> User:
        # TODO: Query and build user
        user = User(userid, "salman", "khon",
                    "sal@gmail.com", "123", "911", "#",)
        return user

    def get_user_by_email(self, email: str) -> User:
        user = User(111111, "salman", "khon",
                    email, "123", "911", "#",)
        return user

    def insert_user(self, user: User):
        # TODO:
        # insert user
        print(f"user {user.email} insert")

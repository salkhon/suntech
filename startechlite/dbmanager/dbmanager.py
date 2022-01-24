import contextlib
from importlib.resources import Resource
import random
import flask_paginate
import re
from startechlite.config import Config
from startechlite.constants import *
import startechlite
from startechlite.account.model import User
from startechlite.product.model import Product
import cx_Oracle


class DBManager:
    TABLE_USERS = "users"
    INSERT_USERS_SQL = "INSERT INTO users (first_name, last_name, email, pass_word, phone_number, user_address) VALUES (:first_name, :last_name, :email, :pass_word, :phone_number, :user_address)"
    SELECT_USERS_BY_EMAIL = "SELECT * FROM users WHERE email = :email"
    SELECT_USERS_BY_ID = "SELECT * FROM users WHERE id = :id"

    class ConnectionAndCursor(contextlib.ExitStack):
        def __init__(self) -> None:
            super().__init__()
            connection = cx_Oracle.connect(
                user=Config.DB_USER,
                password=Config.DB_PASS,
                dsn=Config.DB_CONNECTION_STR,
                encoding="UTF-8"
            )
            connection.autocommit = True
            self.connection = self.enter_context(connection)
            self.cursor = self.enter_context(connection.cursor())

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def _pagination_indices(self, pagination: flask_paginate.Pagination) -> tuple[int, int]:
        infostr = pagination.info  # div tag but we only need to extract the ints
        start_index, end_index, _ = [int(num)
                                     for num in re.findall(r"[0-9]+", infostr)]
        num_items = end_index - start_index + 1
        return (start_index, num_items)

    def get_product_by_handle(self, handle: str) -> Product:
        # TODO: query product by handle, and populate its model class
        id = random.randint(100000, 999999)
        product = Product(id, handle, "Name", "Category", "Subcategory", "Brand",
                          1.0, 0.1, 2022, 5,
                          ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
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

        items = []
        for _ in range(num_items):
            id = random.randint(100000, 999999)
            items.append(Product(id, "product-handle", "Name", "Category", "Subcategory", "Brand",
                                 1.0, 0.1, 2022, 5,
                                 ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
                                     "Property 1": "Awesome",
                                     "Property 2": "Great stuff",
                                     "Property 3": "Nice"
                                 }))

        return (items, pagination)

    def get_category_subcategory(self, category: str, subcategory: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        total_num_items = 47
        pagination = flask_paginate.Pagination(
            page=page, per_page=per_page, total=total_num_items)
        start_index, num_items = self._pagination_indices(
            pagination)

        items = []
        for _ in range(num_items):
            id = random.randint(100000, 999999)
            items.append(Product(id, "product-handle", "Name", "Category", "Subcategory", "Brand",
                                 1.0, 0.1, 2022, 5,
                                 ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
                                     "Property 1": "Awesome",
                                     "Property 2": "Great stuff",
                                     "Property 3": "Nice"
                                 }))
        return (items, pagination)

    def get_category_subcategory_brand(self, category: str, subcategory: str, brand: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        total_num_items = 47
        pagination = flask_paginate.Pagination(
            page=page, per_page=per_page, total=total_num_items)
        start_index, num_items = self._pagination_indices(
            pagination)

        items = []
        for _ in range(num_items):
            id = random.randint(100000, 999999)
            items.append(Product(id, "product-handle", "Name", "Category", "Subcategory", "Brand",
                                 1.0, 0.1, 2022, 5,
                                 ["sick", "awesome"], ["/static/img/dummy.jpg", "#"], {
                                     "Property 1": "Awesome",
                                     "Property 2": "Great stuff",
                                     "Property 3": "Nice"
                                 }))
        return (items, pagination)

    def get_user(self, userid: int) -> User | None:
        user = None
        with self.ConnectionAndCursor() as conncur:
            user = conncur.cursor.execute(
                self.SELECT_USERS_BY_ID, id=userid).fetchone()

        if user:
            user = User(*user)

        return user

    def get_user_by_email(self, email: str) -> User | None:
        # TODO: make email a primary key, or THE primary key
        user = None
        with self.ConnectionAndCursor() as connection_cursor:
            user = connection_cursor.cursor.execute(
                self.SELECT_USERS_BY_EMAIL, email=email).fetchone()

        if user:
            user = User(*user)

        return user

    def insert_user(self, user: User):
        """Inserts a user into the "users" table.

        Args:
            user (User): User model for the data.
        """
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(self.INSERT_USERS_SQL,
                                             first_name=user.first_name,
                                             last_name=user.last_name,
                                             email=user.email,
                                             pass_word=user.password,
                                             phone_number=user.phone_number,
                                             user_address=user.address)


@ startechlite.login_manager.user_loader
def load_user(userid):
    dbman = DBManager()
    return dbman.get_user(userid)

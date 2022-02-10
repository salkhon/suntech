import contextlib
from importlib.resources import Resource
import random
import flask_login
import flask_paginate
import re
from startechlite.config import Config
from startechlite.constants import *
import startechlite
from startechlite.account.model import User
from startechlite.product.model import Product
import cx_Oracle

from startechlite.sales.model import Purchase


class DBManager:
    INSERT_USERS_SQL = "INSERT INTO users (first_name, last_name, email, pass_word, phone_number, user_address) VALUES (:first_name, :last_name, :email, :pass_word, :phone_number, :user_address)"
    SELECT_USERS_BY_EMAIL = "SELECT * FROM users WHERE email = :email"
    SELECT_USERS_BY_ID = "SELECT * FROM users WHERE id = :id"
    INSERT_PURCHASE = "INSERT INTO salman.purchase (payment_info, bought_by) VALUES (:info, :bought_by) RETURNING purchase_id INTO :id_output"
    INSERT_PURCHASE_PRODUCT = "INSERT INTO salman.purchase_product (purchase_id, product_id, product_count) VALUES (:purchase_id, :product_id, :product_count)"

    SELECT_PRODUCT_BY_ID = "SELECT * FROM products WHERE id = :id"
    SELECT_PRODUCT_SPECS_BY_ID = "SELECT * FROM spec_table WHERE product_id = :id"
    SELECT_PRODUCT_IMG_URLS_BY_ID = "SELECT * FROM images WHERE product_id  = :id"

    SELECT_PRODUCT_COUNT_BY_CATEGORY = "SELECT COUNT(*) FROM products WHERE LOWER(category) = :category"
    SELECT_PRODUCT_ID_BY_CATEGORY = "SELECT id FROM products WHERE LOWER(category) = :category OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY"

    SELECT_PRODUCT_COUNT_BY_CATEGORY_SUBCATEGORY = "SELECT COUNT(*) FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory"
    SELECT_PRODUCT_ID_BY_CATEGORY_SUBCATEGORY = "SELECT id FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY"

    SELECT_PRODUCT_COUNT_BY_CATEGORY_SUBCATEGORY_BRAND = "SELECT COUNT(*) FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory AND LOWER(brand) = :brand"
    SELECT_PRODUCT_ID_BY_CATEGORY_SUBCATEGORY_BRAND = "SELECT id FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory AND LOWER(brand) = :brand OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY"

    SELECT_PURCHASES_BY_USERID = "SELECT * FROM purchase WHERE bought_by = :bought_by"

    SELECT_PRODUCTS_BY_PURCHASEID = "SELECT * FROM purchase_product WHERE purchase_id = :purchase_id"

    class ConnectionAndCursor(contextlib.ExitStack):
        def __init__(self, is_autocommit: bool = True, is_scrollable: bool = False) -> None:
            super().__init__()
            connection = cx_Oracle.connect(
                user=Config.DB_USER,
                password=Config.DB_PASS,
                dsn=Config.DB_CONNECTION_STR,
                encoding="UTF-8"
            )
            connection.autocommit = is_autocommit
            self.connection = self.enter_context(connection)
            self.cursor = self.enter_context(
                connection.cursor(scrollable=is_scrollable))

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def _pagination_indices(self, pagination: flask_paginate.Pagination) -> tuple[int, int]:
        infostr = pagination.info  # div tag but we only need to extract the ints
        start_index, end_index, _ = [int(num)
                                     for num in re.findall(r"[0-9]+", infostr)]
        start_index -= 1
        num_items = end_index - start_index
        return (start_index, num_items)

    def get_product_by_id(self, id: int) -> Product | None:
        product = None
        with self.ConnectionAndCursor() as connection_cursor:
            cursor = connection_cursor.cursor

            # query product attrs
            _, base_price, discount, rating, category, subcategory, brand, stock = cursor.execute(
                self.SELECT_PRODUCT_BY_ID, id=id).fetchone()

            product = Product(
                id=id, name="", base_price=base_price, discount=discount,
                rating=rating, category=category, subcategory=subcategory, brand=brand,
                stock=stock, year=0, tags=[], img_urls=[], spec_dict={}, EMI=base_price//12
            )

            # query product specs
            for spec_name, spec_val, _ in cursor.execute(self.SELECT_PRODUCT_SPECS_BY_ID, id=id):
                product.spec_dict[spec_name] = spec_val

            product.name = product.spec_dict["Name"]

            # querying img urls
            for _, img_url in cursor.execute(self.SELECT_PRODUCT_IMG_URLS_BY_ID, id=id):
                img_url = f"/static/img/{img_url}"
                product.img_urls.append(img_url)

        return product

    def _get_category_subcategory_brand_helper(self, category: str, subcategory: str = None, brand: str = None, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:

        def execute_count_query():
            if category and subcategory and brand:
                connection_cursor.cursor.execute(
                    self.SELECT_PRODUCT_COUNT_BY_CATEGORY_SUBCATEGORY_BRAND, category=category, subcategory=subcategory, brand=brand)
            elif category and subcategory:
                connection_cursor.cursor.execute(
                    self.SELECT_PRODUCT_COUNT_BY_CATEGORY_SUBCATEGORY, category=category, subcategory=subcategory)
            else:
                connection_cursor.cursor.execute(
                    self.SELECT_PRODUCT_COUNT_BY_CATEGORY, category=category)

        def execute_select_productid_query():
            if category and subcategory and brand:
                connection_cursor.cursor.execute(
                    self.SELECT_PRODUCT_ID_BY_CATEGORY_SUBCATEGORY_BRAND, category=category, subcategory=subcategory, brand=brand, offset=offset, maxnumrows=num_products)
            elif category and subcategory:
                connection_cursor.cursor.execute(
                    self.SELECT_PRODUCT_ID_BY_CATEGORY_SUBCATEGORY, category=category, subcategory=subcategory, offset=offset, maxnumrows=num_products)
            else:
                connection_cursor.cursor.execute(
                    self.SELECT_PRODUCT_ID_BY_CATEGORY, category=category, offset=offset, maxnumrows=num_products)

        products = []
        pagination = flask_paginate.Pagination()

        with self.ConnectionAndCursor() as connection_cursor:
            execute_count_query()
            total_num_products = connection_cursor.cursor.fetchone()[0]

            pagination = flask_paginate.Pagination(
                page=page, per_page=per_page, total=total_num_products)
            offset, num_products = self._pagination_indices(pagination)

            execute_select_productid_query()

            products = []
            for product in connection_cursor.cursor:
                products.append(self.get_product_by_id(product[0]))

        return (products, pagination)

    def get_category(self, category: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        return self._get_category_subcategory_brand_helper(category=category, page=page, per_page=per_page)

    def get_category_subcategory(self, category: str, subcategory: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        print("here", subcategory)
        return self._get_category_subcategory_brand_helper(category=category, subcategory=subcategory, page=page, per_page=per_page)

    def get_category_subcategory_brand(self, category: str, subcategory: str, brand: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination]:
        return self._get_category_subcategory_brand_helper(category=category, subcategory=subcategory, brand=brand, page=page, per_page=per_page)

    def get_user(self, userid: int) -> User | None:
        user = None
        with self.ConnectionAndCursor() as connection_cursor:
            user = connection_cursor.cursor.execute(
                self.SELECT_USERS_BY_ID, id=userid).fetchone()

        if user:
            user = User(*user)

        return user

    def get_user_by_email(self, email: str) -> User | None:
        # TODO: make email a primary key, or THE primary key
        user = None
        with self.ConnectionAndCursor() as connection_cursor:
            user = connection_cursor.cursor.execute(
                self.SELECT_USERS_BY_EMAIL, email=email
            ).fetchone()

        if user:
            user = User(*user)

        return user

    def insert_user(self, user: User):
        """Inserts a user into the "users" table.

        Args:
            user (User): User model for the data.
        """
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.INSERT_USERS_SQL,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                pass_word=user.password,
                phone_number=user.phone_number,
                user_address=user.address
            )

    def insert_purchase(self, purchase: Purchase):
        with self.ConnectionAndCursor() as connection_cursor:
            id_output = connection_cursor.cursor.var(int)

            # insert purchase
            connection_cursor.cursor.execute(
                self.INSERT_PURCHASE,
                info=purchase.info,
                bought_by=purchase.bought_by,
                id_output=id_output
            )

            assert purchase.productid_count

            # insert purchase products
            for product_id in purchase.productid_count:
                connection_cursor.cursor.execute(
                    self.INSERT_PURCHASE_PRODUCT,
                    purchase_id=id_output.getvalue()[0],
                    product_id=product_id,
                    product_count=purchase.productid_count.get(product_id)
                )

    def get_products_counts_for_purchase(self, purchase_id: int) -> list[tuple[Product, int]]:
        products = []
        with self.ConnectionAndCursor() as connection_cursor:
            for _, product_id, count in connection_cursor.cursor.execute(self.SELECT_PRODUCTS_BY_PURCHASEID, purchase_id=purchase_id):
                products.append((self.get_product_by_id(product_id), count))
        return products

    def get_user_purhcases(self) -> list[Purchase]:
        purchases: list[Purchase] = []
        with self.ConnectionAndCursor() as connection_cursor:
            current_userid = flask_login.current_user.id  # type: ignore

            # query purchase ids
            for id, date, _, status, _, _ in connection_cursor.cursor.execute(
                    self.SELECT_PURCHASES_BY_USERID,
                    bought_by=current_userid):
                purchase = Purchase(id=id, date=date, status=status)
                purchases.append(purchase)

            # query products for purchase ids
            for purchase in purchases:
                purchase.productid_count = {}
                purchase._products = []
                for product, count in self.get_products_counts_for_purchase(purchase.id):
                    purchase.productid_count[product.id] = count
                    purchase._products.append(product)

        return purchases


@startechlite.login_manager.user_loader
def load_user(userid):
    dbman = DBManager()
    return dbman.get_user(userid)

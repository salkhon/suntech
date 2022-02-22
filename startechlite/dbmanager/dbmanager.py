import contextlib
import os
from typing import Iterator
import flask_login
import flask_paginate
import numpy
from werkzeug.datastructures import FileStorage
import re
from startechlite.config import Config
from startechlite.constants import *
import startechlite
from startechlite.account.model import User
from startechlite.product.model import Bundle, Product
from startechlite.sales.model import Purchase
import cx_Oracle


laptop_filters = {
    'Processor': ['Core i3', 'Core i5', 'Core i7', 'Core i9', 'AMD Athlon', 'AMD Ryzen 3', 'AMD Ryzen 5', 'AMD Ryzen 7', 'AMD Ryzen 9', 'Apple M1', 'Pentium'],
    'Ram': ['2GB', '4GB', '8GB', '16GB', '32GB'],
    'Display': ['13.3', '14', '15.6'],
    'Storage': ['256GB', '512GB', '1TB', '1 TB'],
    'Graphics': ['Radeon', 'GTX1650', 'GTX1650', 'GTX 1660', 'RTX 2060', 'RTX 2070', 'RTX 2080', 'RTX 3050', 'RTX 3060', 'RTX 3070', 'RTX 3080', 'MX450', 'Integrated', 'Iris', 'UHD']
}
desktop_filters = {
    'Processor': ['Core i3', 'Core i5', 'Core i7', 'Core i9', 'AMD Athlon', 'AMD Ryzen 3', 'AMD Ryzen 5', 'AMD Ryzen 7', 'AMD Ryzen 9', 'Apple M1', 'Pentium'],
    'Ram': ['2GB', '4GB', '8GB', '16GB', '32GB'],
    'Storage': ['256GB', '512GB', '1TB', '1 TB'],
    'Graphics': ['Radeon', 'GTX1650', 'GTX1650', 'GTX 1660', 'RTX 2060', 'RTX 2070', 'RTX 2080', 'RTX 3050', 'RTX 3060', 'RTX 3070', 'RTX 3080', 'MX450', 'Integrated', 'Iris', 'UHD']
}


class DBManager:

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
            cls.instance.insert_init_admin()
        return cls.instance

    def _pagination_indices(self, pagination: flask_paginate.Pagination) -> tuple[int, int]:
        infostr = pagination.info  # div tag but we only need to extract the ints
        start_index, end_index, _ = [int(num)
                                     for num in re.findall(r"[0-9]+", infostr)]
        start_index -= 1
        num_items = end_index - start_index
        return (start_index, num_items)

    # USERS
    INSERT_USERS_SQL = "INSERT INTO users (first_name, last_name, email, pass_word, phone_number, user_address) VALUES (:first_name, :last_name, :email, :pass_word, :phone_number, :user_address)"
    SELECT_USERS_BY_EMAIL = "SELECT * FROM users WHERE email = :email"
    SELECT_USERS_BY_ID = "SELECT * FROM users WHERE id = :id"
    SELECT_USER_COUNT = "SELECT COUNT(*) FROM users"
    SELECT_USERS = """
        SELECT * FROM users
        OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY
    """
    UPDATE_USER = "UPDATE users SET first_name = :first_name, last_name = :last_name, phone_number = :phone_number, user_address = :user_address WHERE id = :id"
    DELETE_USER = "DELETE FROM users WHERE id = :id"

    def get_user_by_id(self, userid: int) -> User | None:
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

    def insert_init_admin(self):
        # there will be only one admin, so admin table is redundant
        with self.ConnectionAndCursor() as connection_cursor:
            admin = connection_cursor.cursor.execute(
                self.SELECT_USERS_BY_EMAIL, email=ADMIN_EMAIL
            ).fetchone()

            if not admin:
                password = startechlite.bcrypt.generate_password_hash(
                    ADMIN_PASS_UNENCRYPTED).decode("utf-8")
                connection_cursor.cursor.execute(
                    self.INSERT_USERS_SQL, first_name=ADMIN_FIRST_NAME, last_name=ADMIN_LAST_NAME,
                    email=ADMIN_EMAIL, pass_word=password, phone_number="", user_address=""
                )

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

    def update_user(self, user: User):
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.UPDATE_USER,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number,
                user_address=user.address,
                id=user.id
            )

    def get_user_list(self, page: int = 1, per_page: int = 15) -> tuple[list[User], flask_paginate.Pagination]:
        users = []
        pagination = flask_paginate.Pagination()

        with self.ConnectionAndCursor() as connection_cursor:
            cursor = connection_cursor.cursor

            user_count, = cursor.execute(self.SELECT_USER_COUNT).fetchone()
            pagination = flask_paginate.Pagination(
                page=page, per_page=per_page, total=user_count)
            offset, num_users = self._pagination_indices(pagination)

            users = cursor.execute(
                self.SELECT_USERS, offset=offset, maxnumrows=num_users).fetchall()
            users = [User(*user) for user in users if user[3] != ADMIN_EMAIL]

        return users, pagination

    # BANS
    SELECT_ALL_BANS = "SELECT * FROM bans"
    INSERT_INTO_BANS = "INSERT INTO bans (email) VALUES (:email)"

    def ban_user(self, userid: int, email: str):
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.DELETE_USER,
                id=userid
            )
            connection_cursor.cursor.execute(
                self.INSERT_INTO_BANS,
                email=email
            )

    def get_banned_emails(self) -> list[str]:
        banned_emails = []
        with self.ConnectionAndCursor() as connection_cursor:
            banned_emails = [banned_email for banned_email, ban_date in connection_cursor.cursor.execute(
                self.SELECT_ALL_BANS
            ).fetchall()]
        return banned_emails

    # PRODUCTS
    SELECT_PRODUCT_BY_ID = "SELECT * FROM products WHERE id = :id"
    SELECT_PRODUCT_SPECS_BY_ID = "SELECT * FROM spec_table WHERE product_id = :id"
    SELECT_PRODUCT_IMG_URLS_BY_ID = "SELECT * FROM images WHERE product_id  = :id"

    SELECT_PRODUCT_COUNT_BY_CATEGORY = "SELECT COUNT(*) FROM products WHERE LOWER(category) = :category"
    SELECT_PRODUCT_ID_BY_CATEGORY = "SELECT id FROM products WHERE LOWER(category) = :category OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY"

    SELECT_PRODUCT_COUNT_BY_CATEGORY_SUBCATEGORY = "SELECT COUNT(*) FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory"
    SELECT_PRODUCT_ID_BY_CATEGORY_SUBCATEGORY = "SELECT id FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY"

    SELECT_PRODUCT_COUNT_BY_CATEGORY_SUBCATEGORY_BRAND = "SELECT COUNT(*) FROM products WHERE LOWER(category) = :category AND LOWER(subcategory) = :subcategory AND LOWER(brand) = :brand"
    SELECT_PRODUCT_ID_BY_CATEGORY_SUBCATEGORY_BRAND = """
        SELECT id FROM products
        WHERE LOWER(category) = :category AND
            LOWER(subcategory) = :subcategory AND
            LOWER(brand) = :brand
        OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY
    """

    INSERT_PRODUCT = "INSERT INTO products (name, base_price, discount, rating, category, subcategory, brand, stock) VALUES (:name, :base_price, :discount, :rating, :category, :subcategory, :brand, :stock)"

    DELETE_PRODUCT_BY_ID = "DELETE FROM products WHERE id = :id"
    UPDATE_PRODUCT_BY_ID = """
        UPDATE products
        SET name = :name, base_price = :base_price, discount = :discount, rating = :rating, stock = :stock
        WHERE id = :id
    """

    UPDATE_SPEC_TABLE_BY_PRODUCT_ID_AND_ATTR_NAME = """
        UPDATE spec_table
        SET attr_value = :attr_value
        WHERE product_id = :product_id AND attr_name = :attr_name
    """
    INSERT_ATTR_IN_SPEC_TABLE_BY_PRODUCT_ID = """
        INSERT INTO spec_table (product_id, attr_name, attr_value)
        VALUES (:product_id, :attr_name, :attr_value)
    """
    SELECT_PRODUCT_SPEC_ATTR_VALUE_BY_ID_AND_ATTR_NAME = "SELECT attr_value FROM spec_table WHERE product_id = :product_id AND attr_name = :attr_name"

    SELECT_IMG_COUNT_BY_PRODUCT_ID = "SELECT COUNT(*) FROM images WHERE product_id = :product_id"

    INSERT_IMG_URL_INTO_IMAGES = "INSERT INTO images (product_id, img_url) VALUES (:product_id, :img_url)"

    SELECT_PRODUCTS_BY_PURCHASE_ID = "SELECT * FROM purchase_product WHERE purchase_id = :purchase_id"

    SELECT_PRODUCTS_BOUGHT_WITH_ANOTHER_PRODUCT = """
        SELECT product_id, COUNT(purchase_id) "purchase_count" FROM purchase_product
        WHERE purchase_id IN (
            SELECT purchase_id FROM purchase_product
            WHERE product_id = :product_id
        ) AND product_id != :product_id
        GROUP BY product_id
        ORDER BY "purchase_count" DESC
    """

    populate_filters = {
        'price': "select min(BASE_PRICE),max(base_price) from PRODUCTS where lower(category) like :category and lower(subcategory) like :subcategory and lower(brand) like :brand",
        'subcategory': "Select subcategory, count(*) from products where lower(category) like :category and lower(subcategory) like :subcategory and lower(brand) like :brand group by subcategory",
        'brand': "Select brand, count(*) from products where lower(category) like :category and lower(subcategory) like :subcategory and lower(brand) like :brand group by brand"
    }

    search_query = "select id from products where lower(name) like :key_word "

    filter_by = {

        'spec': "SELECT PRODUCT_ID FROM SPEC_TABLE WHERE ATTR_NAME = :spec AND ATTR_VALUE like :spec_value ",
        'price':  "SELECT id FROM products WHERE base_price between :price_from and :price_to ",
        'category': "SELECT id FROM products WHERE LOWER(category) like :category ",
        'price_category': "SELECT id FROM products WHERE LOWER(category) like :category and base_price between :price_from and :price_to",
        'brand': "SELECT id FROM products WHERE LOWER(category) like :category and LOWER(subcategory) like :subcategory and LOWER(brand) like :brand ",
        'subcategory': "SELECT id FROM products WHERE LOWER(category) like :category and LOWER(subcategory) like :subcategory ",
        'brand_arr':  "SELECT id FROM products WHERE LOWER(category) like :category and LOWER(subcategory) like :subcategory and LOWER(brand) in  ",
        'subcat_arr': "SELECT id FROM products WHERE LOWER(category) like :category and LOWER(subcategory) in    "
    }

    def get_bought_togethers_by_id(self, id: int) -> list[tuple[int, int]]:
        """Queries product id s from purchases in purchase_product table where target product is
        present. Then counts the number of time each product pairs with the target product in distinct
        purchases by grouping by products.

        Args:
            id (int): Target product id

        Returns:
            list[tuple[int, int]]: Tuples of product id and its corresponding count of pairs
            with target product in distinct purchases.
        """
        product_pair_count = []
        with self.ConnectionAndCursor() as connection_cursor:
            cursor = connection_cursor.cursor
            product_pair_count = cursor.execute(
                self.SELECT_PRODUCTS_BOUGHT_WITH_ANOTHER_PRODUCT, product_id=id).fetchall()
        return product_pair_count

    def get_product_by_id(self, id: int, bought_togethers_included: bool = False) -> Product | None:
        product = None
        with self.ConnectionAndCursor() as connection_cursor:
            cursor = connection_cursor.cursor

            # query product attrs
            _, name, base_price, discount, rating, category, subcategory, brand, stock = cursor.execute(
                self.SELECT_PRODUCT_BY_ID, id=id).fetchone()

            product = Product(
                id=id, name=name, base_price=base_price, discount=discount,
                rating=rating, category=category, subcategory=subcategory, brand=brand,
                stock=stock, year=0, img_urls=[], spec_dict={}, EMI=base_price//12,
                bought_together=[]
            )

            # query product specs
            for spec_name, spec_val, _ in cursor.execute(self.SELECT_PRODUCT_SPECS_BY_ID, id=id):
                product.spec_dict[spec_name] = spec_val

            # querying img urls
            for _, img_url in cursor.execute(self.SELECT_PRODUCT_IMG_URLS_BY_ID, id=id):
                img_url = f"/static/img/products/{img_url}"
                product.img_urls.append(img_url)

            # querying frequently bought together products
            if bought_togethers_included:
                product_count_tuples = self.get_bought_togethers_by_id(id)[:5]
                for productid, _ in product_count_tuples:
                    # bought_togethers_included MUST be False to stop starting a chain of calls
                    paired_prod = self.get_product_by_id(
                        productid, bought_togethers_included=False)

                    if not paired_prod:
                        continue

                    product.bought_together.append(paired_prod)

        return product

    def _get_category_subcategory_brand_helper(self, category: str, subcategory: str = None, brand: str = None, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination, dict]:

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

        def load_filters() -> dict:
            if subcategory or brand:
                return {}

            what_to_get = ["subcategory", "brand"]
            side_filters = {}

            connection_cursor.cursor.execute(
                self.populate_filters['price'], category=category, subcategory='%%', brand='%%')
            side_filters["price"] = connection_cursor.cursor.fetchone()

            for criteria in what_to_get:
                connection_cursor.cursor.execute(
                    self.populate_filters[criteria], category=category, subcategory='%%', brand='%%')
                temp = []
                for row in connection_cursor.cursor:
                    temp.append(row[0])

                side_filters[criteria.capitalize()] = temp

            if category == 'laptop':
                side_filters.update(laptop_filters)
            if category == 'desktop':
                side_filters.update(desktop_filters)

            return side_filters

        products = []
        pagination = flask_paginate.Pagination()
        side_filters = {}

        with self.ConnectionAndCursor() as connection_cursor:
            execute_count_query()
            total_num_products = connection_cursor.cursor.fetchone()[0]

            pagination = flask_paginate.Pagination(
                page=page, per_page=per_page, total=total_num_products)
            offset, num_products = self._pagination_indices(pagination)

            execute_select_productid_query()

            for product in connection_cursor.cursor:
                products.append(self.get_product_by_id(product[0]))

            side_filters = load_filters()

        if subcategory or brand:
            return (products, pagination, {})
        else:
            return (products, pagination, side_filters)

    def get_category(self, category: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination, dict]:
        return self._get_category_subcategory_brand_helper(category=category, page=page, per_page=per_page)

    def get_category_subcategory(self, category: str, subcategory: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination, dict]:
        print("here", subcategory)
        return self._get_category_subcategory_brand_helper(category=category, subcategory=subcategory, page=page, per_page=per_page)

    def get_category_subcategory_brand(self, category: str, subcategory: str, brand: str, page: int = 1, per_page: int = 15) -> tuple[list[Product], flask_paginate.Pagination, dict]:
        return self._get_category_subcategory_brand_helper(category=category, subcategory=subcategory, brand=brand, page=page, per_page=per_page)

    def delete_product(self, id: int):
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.DELETE_PRODUCT_BY_ID,
                id=id
            )

    def update_product_by_id(self, id: int, updated_product: Product, uploaded_images: list[FileStorage]):
        with self.ConnectionAndCursor() as connection_cursor:
            # update basic attrs
            connection_cursor.cursor.execute(
                self.UPDATE_PRODUCT_BY_ID,
                id=id,
                name=updated_product.name, 
                base_price=updated_product.base_price,
                discount=updated_product.discount,
                rating=updated_product.rating,
                stock=updated_product.stock
            )

            # update spec table attrs
            for attr_name in updated_product.spec_dict:
                connection_cursor.cursor.execute(
                    self.UPDATE_SPEC_TABLE_BY_PRODUCT_ID_AND_ATTR_NAME,
                    product_id=id,
                    attr_name=attr_name,
                    attr_value=updated_product.spec_dict[attr_name]
                )

            # update image table urls
            existing_image_count, = connection_cursor.cursor.execute(
                self.SELECT_IMG_COUNT_BY_PRODUCT_ID,
                product_id=id
            ).fetchone()

            DEST = os.path.join(os.getcwd(), "startechlite",
                                "static", "img", "products", f"{id}")
            if not os.path.exists(DEST):
                os.makedirs(DEST)

            connection_cursor.connection.autocommit = False
            for image in uploaded_images:
                assert image.filename

                EXTENSION = os.path.splitext(image.filename)[1]
                image.filename = f"img{existing_image_count+1}{EXTENSION}"
                DB_URL = f"{id}/{image.filename}"

                try:
                    image.save(os.path.join(DEST, image.filename))
                    connection_cursor.cursor.execute(
                        self.INSERT_IMG_URL_INTO_IMAGES,
                        product_id=id,
                        img_url=DB_URL
                    )
                    existing_image_count += 1
                    connection_cursor.connection.commit()
                except Exception as e:
                    connection_cursor.connection.rollback()
                    print("Failed to save image")
                    print(e)

    def get_product_spec_attr_val_by_id_and_attr_name(self, id: int, attr_name: str) -> str | None:
        attr_val = None
        with self.ConnectionAndCursor() as connection_cursor:
            attr_val = connection_cursor.cursor.execute(
                self.SELECT_PRODUCT_SPEC_ATTR_VALUE_BY_ID_AND_ATTR_NAME,
                product_id=id,
                attr_name=attr_name
            ).fetchone()
        return attr_val

    def add_new_spec_for_product_by_id(self, id: int, attr_name: str, attr_value: str):
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.INSERT_ATTR_IN_SPEC_TABLE_BY_PRODUCT_ID,
                product_id=id,
                attr_name=attr_name,
                attr_value=attr_value
            )

    def create_new_product(self, product: Product):
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.INSERT_PRODUCT,
                name=product.name,
                base_price=product.base_price,
                discount=product.discount,
                rating=product.rating,
                category=product.category,
                subcategory=product.subcategory,
                brand=product.brand,
                stock=product.stock
            )

    def get_bundles(self, page: int = 1, per_page: int = 15) -> tuple[list, flask_paginate.Pagination]:
        bundles = []
        pagination = flask_paginate.Pagination()
        with self.ConnectionAndCursor() as connection_cursor:

            count_query = 'SELECT count(*) from bundles'
            connection_cursor.cursor.execute(count_query)

            total_num_bundles = connection_cursor.cursor.fetchone()[0]
            pagination = flask_paginate.Pagination(
                page=page, per_page=per_page, total=total_num_bundles)

            query = 'select id, name from bundles'

            connection_cursor.cursor.execute(query)

            bundles_temp = []
            for row in connection_cursor.cursor:
                bundles_temp.append(row)

            print("Fresh hot bundles here", bundles_temp, flush=True)
            bundles = []
            for row in bundles_temp:
                products_list = []
                query2 = 'select product_id from bundle_products where bundle_id=:id'
                connection_cursor.cursor.execute(query2, id=row[0])
                for con_row in connection_cursor.cursor:
                    products_list.append(con_row[0])
                print("Take it or leave it ", products_list, flush=True)
                Products = []
                for id in products_list:
                    Products.append(self.get_product_by_id(id))

                temp_bundle = Bundle(
                    id=row[0], name=row[1], products_list=Products)
                bundles.append(temp_bundle)

        return bundles, pagination

    def filters_as_tuples(self, filters):
        Tuple = "("
        for x in filters:
            filterString = x.lower()
            Tuple = Tuple+"'"+filterString+"',"
        Tuple = Tuple[0:-1]+")"
        return Tuple

    def get_Id_AsSet_FromCursor(self, c):
        products = set()
        for product_id in c:
            products.add(product_id[0])

        return products

    def get_Id_AsList_FromCursor(self, c):
        products = []
        for product_id in c:
            products.append(product_id[0])

        return products

    def get_by_filters(self, filters, category: str, subcategory="%%", brand="%%", page: int = 1, per_page: int = 20) -> tuple[list, flask_paginate.Pagination, dict]:

        print(filters, flush=True)
        products = []
        pagination = flask_paginate.Pagination()
        side_filters = {}

        def load_filters() -> dict:
            what_to_get = ["subcategory", "brand"]
            side_filters = {}

            connection_cursor.cursor.execute(
                self.populate_filters['price'], category=category, subcategory='%%', brand='%%')
            side_filters["price"] = connection_cursor.cursor.fetchone()

            for criteria in what_to_get:
                connection_cursor.cursor.execute(
                    self.populate_filters[criteria], category=category, subcategory='%%', brand='%%')
                temp = []
                for row in connection_cursor.cursor:
                    temp.append(row[0])

                side_filters[criteria.capitalize()] = temp

            if category == 'laptop':
                side_filters.update(laptop_filters)
            if category == 'desktop':
                side_filters.update(desktop_filters)
            return side_filters

        with self.ConnectionAndCursor() as connection_cursor:

            products_ids = set()

            price_range = filters[0]
            sub_cat_filters = filters[1]
            brand_filters = filters[2]

            processor_filters = filters[3]
            ram_filters = filters[4]
            display_filters = filters[5]
            storage_filters = filters[6]
            graphics_filters = filters[7]

            subcat_string = self.filters_as_tuples(sub_cat_filters)

            brands_string = self.filters_as_tuples(brand_filters)

            print("we got em", subcat_string, flush=True)

            if len(sub_cat_filters) > 0:
                connection_cursor.cursor.execute(
                    self.filter_by['subcat_arr']+subcat_string, category=category)
                products_ids = products_ids.union(
                    self.get_Id_AsSet_FromCursor(connection_cursor.cursor))
            else:
                connection_cursor.cursor.execute(
                    self.filter_by['category'], category=category)
                products_ids = products_ids.union(
                    self.get_Id_AsSet_FromCursor(connection_cursor.cursor))

            print(products_ids, flush=True)

            print("we got em1", brands_string, flush=True)
            if len(brand_filters) > 0:
                connection_cursor.cursor.execute(
                    self.filter_by['brand_arr'] + brands_string, category=category, subcategory="%%")
                temp = self.get_Id_AsSet_FromCursor(connection_cursor.cursor)
                # print(temp, flush=True)
                products_ids = products_ids.intersection(temp)

            print(products_ids, flush=True)

            connection_cursor.cursor.execute(
                self.filter_by['price_category'], category=category, price_from=price_range[0], price_to=price_range[1])
            price_set = self.get_Id_AsSet_FromCursor(connection_cursor.cursor)
            products_ids = products_ids.intersection(price_set)

            if len(processor_filters) > 0:
                temp_set = set()
                for item in processor_filters:
                    temp = '%'+item+'%'
                    connection_cursor.cursor.execute(
                        self.filter_by['spec'], spec='Processor', spec_value=temp)
                    temp_set = temp_set.union(
                        self.get_Id_AsSet_FromCursor(connection_cursor.cursor))
                products_ids = products_ids.intersection(temp_set)
                print("in the end ", temp_set, flush=True)

            if len(display_filters) > 0:
                temp_set = set()
                for item in display_filters:
                    temp = '%'+item+'%'
                    connection_cursor.cursor.execute(
                        self.filter_by['spec'], spec='Display', spec_value=temp)
                    temp_set = temp_set.union(
                        self.get_Id_AsSet_FromCursor(connection_cursor.cursor))
                products_ids = products_ids.intersection(temp_set)
                print("in the end ", temp_set, flush=True)

            if len(ram_filters) > 0:
                temp_set = set()
                for item in ram_filters:
                    temp = '%'+item+'%'
                    connection_cursor.cursor.execute(
                        self.filter_by['spec'], spec='RAM', spec_value=temp)
                    temp_set = temp_set.union(
                        self.get_Id_AsSet_FromCursor(connection_cursor.cursor))
                products_ids = products_ids.intersection(temp_set)
                print("in the end ", temp_set, flush=True)

            if len(storage_filters) > 0:
                temp_set = set()
                for item in storage_filters:
                    temp = '%'+item+'%'
                    connection_cursor.cursor.execute(
                        self.filter_by['spec'], spec='Storage', spec_value=temp)
                    temp_set = temp_set.union(
                        self.get_Id_AsSet_FromCursor(connection_cursor.cursor))
                products_ids = products_ids.intersection(temp_set)
                print("in the end ", temp_set, flush=True)

            if len(graphics_filters) > 0:
                temp_set = set()
                for item in graphics_filters:
                    temp = '%'+item+'%'
                    connection_cursor.cursor.execute(
                        self.filter_by['spec'], spec='Graphics_Card', spec_value=temp)
                    temp_set = temp_set.union(
                        self.get_Id_AsSet_FromCursor(connection_cursor.cursor))
                products_ids = products_ids.intersection(temp_set)
                print("in the end ", temp_set, flush=True)

            total_num_products = len(products_ids)
            pagination = flask_paginate.Pagination()
            pagination = flask_paginate.Pagination(
                page=page, per_page=per_page, total=total_num_products)

            offset, num_products = self._pagination_indices(pagination)

            print(products_ids, flush=True)
            for id in products_ids:
                products.append(self.get_product_by_id(id))

            side_filters = load_filters()

            products = products[offset: offset + num_products]

        return (products, pagination, side_filters)

    def ranking_searches(self, all_ids):

        np_arr = numpy.array(all_ids)
        np_arr.sort()

        d = {}

        for id in np_arr:
            if id in d:
                d[id] += 1
            else:
                d[id] = 1

        sorted_tuples = sorted(d.items(), key=lambda x: int(x[1]))
        res = [int(x[0]) for x in sorted_tuples]
        res.reverse()
        return res

    def get_by_search(self, search_string, page: int = 1, per_page: int = 20):

        key_words = search_string.split(" ")
        with self.ConnectionAndCursor() as connection_cursor:
            list_of_repeated_ids = []
            for key_word in key_words:
                if len(key_word) < 2:
                    continue
                fmt_key_word = "%"+key_word.lower()+"%"
                connection_cursor.cursor.execute(
                    self.search_query, key_word=fmt_key_word)
                temp = self.get_Id_AsList_FromCursor(
                    connection_cursor.cursor)

                list_of_repeated_ids += temp

            products_ids = self.ranking_searches(list_of_repeated_ids)

            total_num_products = len(products_ids)
            pagination = flask_paginate.Pagination()
            pagination = flask_paginate.Pagination(
                page=page, per_page=per_page, total=total_num_products)

            offset, num_products = self._pagination_indices(pagination)

            products = []

            print(products_ids, flush=True)
            for id in products_ids:
                products.append(self.get_product_by_id(id))

            return (products[offset: offset+num_products], pagination)

    def get_comments(self, product_id):

        get_comments = "select user_id, comment_id, comment_on , text from COMMENTS where product_id=:p_id"

        with self.ConnectionAndCursor() as connection_cursor:

            connection_cursor.cursor.execute(get_comments, p_id=product_id)

            # the comments with null comment_on will be a list of list
            # sub_comments will be a dict of list of list

            main_comments = []
            sub_comments = {}

            all_comments = []
            for row in connection_cursor.cursor:
                all_comments.append(list(row))

            for row in all_comments:

                query = "select first_name||' '||last_name from users where id = :id"

                connection_cursor.cursor.execute(query, id=row[0])
                row[0] = connection_cursor.cursor.fetchone()[0]

                if row[2] == None:
                    main_comments.append(row)
                else:
                    if row[2] in sub_comments:
                        sub_comments[row[2]].append(row)
                    else:
                        sub_comments[row[2]] = [row]

            # print(main_comments, flush=True)
            # print(sub_comments, flush=True)
            return main_comments, sub_comments

    def add_comment(self, comment_form):

        p_id = comment_form[0][0]
        comment_txt = comment_form[1][0]

        if not flask_login.current_user.is_authenticated:  # type: ignore
            return False

        user_id = flask_login.current_user.id  # type: ignore

        insert_comment = "insert into comments (user_id, product_id, text) values (:user_id, :product_id, :text)"
        insert_subcomment = "insert into comments (comment_on, user_id, product_id, text) values (:comment_on, :user_id, :product_id, :text)"

        with self.ConnectionAndCursor() as connection_cursor:

            if len(comment_form[2]) > 0:
                comment_on_id = comment_form[2][0]
                print("subcomment_on addded", comment_form, flush=True)
                connection_cursor.cursor.execute(
                    insert_subcomment, comment_on=comment_on_id, user_id=user_id, product_id=p_id, text=comment_txt)
            else:
                print("main_comment added", flush=True)
                connection_cursor.cursor.execute(
                    insert_comment, user_id=user_id, product_id=p_id, text=comment_txt)

        return True

    def add_review(self, review_form):
        print("VINNI VICCI VIDI", review_form, flush=True)
        product_id = review_form[0][0]
        rating = review_form[1][0]
        text = review_form[2][0]

        if not flask_login.current_user.is_authenticated:  # type: ignore
            return False

        user_id = flask_login.current_user.id  # type: ignore

        has_purchased_count = 'select count(*) from purchase join PURCHASE_PRODUCT  using (PURCHASE_ID) where BOUGHT_BY=:user_id and PRODUCT_ID=:p_id'

        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                has_purchased_count, user_id=user_id, p_id=product_id)
            pCount = connection_cursor.cursor.fetchone()[0]
            if pCount == 0:
                return False

            review_insert = 'insert into review (user_id, product_id, rating, text) values (:user_id, :product_id, :rating, :text)'
            connection_cursor.cursor.execute(
                review_insert, user_id=user_id, product_id=product_id, rating=rating, text=text)

        return True

    def get_reviews(self, product_id) -> list:

        get_reviews = "select user_id, rating, text from REVIEW where product_id=:p_id"

        all_reviews = []
        with self.ConnectionAndCursor() as connection_cursor:

            connection_cursor.cursor.execute(get_reviews, p_id=product_id)

            # the comments with null comment_on will be a list of list
            # sub_comments will be a dict of list of list

            for row in connection_cursor.cursor:
                all_reviews.append(list(row))

            for review in all_reviews:
                query = "select first_name||' '||last_name from users where id = :id"
                connection_cursor.cursor.execute(query, id=review[0])
                review[0] = connection_cursor.cursor.fetchone()[0]

        # print("REVIEWS YAYYY", all_reviews, flush=True)
        return all_reviews

    # PURCHASES
    INSERT_PURCHASE = "INSERT INTO salman.purchase (payment_info, address, bought_by) VALUES (:info, :address, :bought_by) RETURNING purchase_id INTO :id_output"
    INSERT_PURCHASE_PRODUCT = "INSERT INTO salman.purchase_product (purchase_id, product_id, product_count) VALUES (:purchase_id, :product_id, :product_count)"
    SELECT_PURCHASE_IDS_BY_USER_ID = "SELECT purchase_id FROM purchase WHERE bought_by = :bought_by"
    SELECT_PURCHASE_BY_ID = "SELECT * FROM purchase WHERE purchase_id = :purchase_id"
    APPROVE_PURCHASE_BY_ID = "UPDATE purchase SET approval_date = CURRENT_TIMESTAMP WHERE purchase_id = :purchase_id"
    UPDATE_PURCHASE_ADDRESS_BY_ID = "UPDATE purchase SET address = :address WHERE purchase_id = :purchase_id"
    SELECT_ALL_PURCHASES = "SELECT * FROM purchase"

    def get_products_counts_for_purchase(self, purchase_id: int, connection_cursor: "ConnectionAndCursor") -> list[tuple[Product, int]]:
        products = []
        for _, product_id, count in connection_cursor.cursor.execute(self.SELECT_PRODUCTS_BY_PURCHASE_ID, purchase_id=purchase_id):
            products.append((self.get_product_by_id(product_id), count))
        return products

    def get_purchase_by_id(self, id: int, with_products_counts: bool = True) -> Purchase | None:
        purchase = None

        with self.ConnectionAndCursor() as connection_cursor:
            purchase = connection_cursor.cursor.execute(
                self.SELECT_PURCHASE_BY_ID,
                purchase_id=id
            ).fetchone()

            if purchase:
                purchase = Purchase(
                    *purchase, productid_count={}, _products=[])
                assert purchase.productid_count is not None and purchase._products is not None

                if with_products_counts:
                    # query purchase associated products and counts for detailed view
                    for product, count in self.get_products_counts_for_purchase(purchase.id, connection_cursor):
                        purchase.productid_count[product.id] = count
                        purchase._products.append(product)

        return purchase

    def insert_purchase(self, purchase: Purchase):
        with self.ConnectionAndCursor() as connection_cursor:
            id_output = connection_cursor.cursor.var(int)

            # insert purchase
            connection_cursor.cursor.execute(
                self.INSERT_PURCHASE,
                info=purchase.info,
                address=purchase.address,
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

    def get_user_purhcases(self) -> list[Purchase]:
        purchases: list[Purchase] = []
        with self.ConnectionAndCursor() as connection_cursor:
            current_userid = flask_login.current_user.id  # type: ignore

            # query purchase ids
            for id, in connection_cursor.cursor.execute(
                    self.SELECT_PURCHASE_IDS_BY_USER_ID,
                    bought_by=current_userid):
                purchase = self.get_purchase_by_id(id)
                assert purchase
                purchases.append(purchase)

        return purchases

    def approve_purchase(self, id: int):
        with self.ConnectionAndCursor() as connection_cursor:
            purchase = self.get_purchase_by_id(id, False)

            if purchase and purchase.approval_date:
                return

            connection_cursor.cursor.execute(
                self.APPROVE_PURCHASE_BY_ID,
                purchase_id=id
            )

    def update_purchase_address_by_id(self, id, new_address):
        with self.ConnectionAndCursor() as connection_cursor:
            connection_cursor.cursor.execute(
                self.UPDATE_PURCHASE_ADDRESS_BY_ID,
                purchase_id=id,
                address=new_address
            )

    def get_all_purchases(self) -> list[Purchase]:
        purchases = []

        with self.ConnectionAndCursor() as connection_cursor:
            for purchase in connection_cursor.cursor.execute(
                self.SELECT_ALL_PURCHASES
            ):
                purchases.append(Purchase(*purchase))

        return purchases


@startechlite.login_manager.user_loader
def load_user(id):
    dbman = DBManager()
    return dbman.get_user_by_id(id)

from startechlite.account.model import User
from startechlite.product.model import Product
import flask


def _make_updated_user_from_form() -> User:
    id, first_name, last_name, email, phone_number, address, _ = flask.request.form.values()
    return User(int(id), first_name, last_name, email, "", phone_number, address)


def _make_updated_product_from_form() -> Product:
    """
    Updated users have updated properties, except the image urls and bought together lists.
    img_urls is empty, dbmanager will save the uploaded pictures on the appropriate directory and 
    store the correspoinding image urls.
    bought together will not be updated. 
    """
    prop_dict: dict[str, int | float | str | list | dict] = {
        "img_urls": [],
        "bought_together": []
    }

    # specs
    spec_dict = {}
    for attr_name in flask.request.form:
        attr_val = flask.request.form.get(attr_name)
        assert attr_val is not None

        if attr_name.startswith("specdict-"):
            spec_dict[attr_name.removeprefix(
                "specdict-")] = attr_val
        elif attr_name == "action":
            continue
        else:
            prop_dict[attr_name] = attr_val

    prop_dict["spec_dict"] = spec_dict

    # basic attrs
    prop_dict["id"] = int(prop_dict.get("id"))  # type: ignore
    prop_dict["base_price"] = float(
        prop_dict.get("base_price"))  # type: ignore
    prop_dict["discount"] = float(
        prop_dict.get("discount"))  # type: ignore
    prop_dict["rating"] = float(
        prop_dict.get("rating"))  # type: ignore
    prop_dict["EMI"] = float(prop_dict.get("EMI"))  # type: ignore

    updated_product = Product(**prop_dict)  # type: ignore
    return updated_product


def _get_deleted_product_basic_info_from_form() -> tuple[int, str, str, str]:
    form = flask.request.form
    id = form.get("id")
    cat = form.get("category")
    subcat = form.get("subcategory")
    brand = form.get("brand")

    assert id and cat and subcat and brand

    return int(id), cat, subcat, brand


def _make_new_basic_product_from_form() -> Product:
    name, base_price, discount, rating, category, subcategory, brand, stock, _ = flask.request.form.values()
    new_basic_product = Product(
        -1, name, int(base_price), float(discount),
        float(rating), category, subcategory, brand, int(stock),
        year=-1, img_urls=[], spec_dict={}, EMI=int(base_price)//12, bought_together=[]
    )
    return new_basic_product

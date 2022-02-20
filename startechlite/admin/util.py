from startechlite.account.model import User
from startechlite.product.model import Product
import flask


def _make_updated_user_from_form() -> User:
    id, first_name, last_name, email, phone_number, address, _ = flask.request.form.values()
    return User(int(id), first_name, last_name, email, "", phone_number, address)


def _make_updated_product_from_form() -> Product:
    """
    Updated users have updated properties, except the image urls, which only contains the new image.
    bought together will not be updated. That will be empty. 
    """
    form = flask.request.form
    main_prop_dict: dict[str, int | float | str | list] = {
        "tags": [],
        "img_urls": [],
        "bought_together": []
    }
    spec_dict = {}

    for attr_name in form:
        attr_val = form.get(attr_name)
        assert attr_val

        if attr_name.startswith("specdict-"):
            spec_dict[attr_name.removeprefix(
                "specdict-")] = attr_val
        elif attr_name == "action":
            continue
        else:
            main_prop_dict[attr_name] = attr_val

    main_prop_dict["id"] = int(main_prop_dict.get("id"))  # type: ignore
    main_prop_dict["base_price"] = float(
        main_prop_dict.get("base_price"))  # type: ignore
    main_prop_dict["discount"] = float(
        main_prop_dict.get("discount"))  # type: ignore
    main_prop_dict["rating"] = float(
        main_prop_dict.get("rating"))  # type: ignore
    main_prop_dict["EMI"] = float(main_prop_dict.get("EMI"))  # type: ignore

    updated_product = Product(
        **main_prop_dict, spec_dict=spec_dict)  # type: ignore
    return updated_product


def _get_deleted_product_basic_info_from_form() -> tuple[int, str, str, str]:
    form = flask.request.form
    id = form.get("id")
    cat = form.get("category")
    subcat = form.get("subcategory")
    brand = form.get("brand")

    assert id and cat and subcat and brand

    return int(id), cat, subcat, brand

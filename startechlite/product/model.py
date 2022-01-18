from dataclasses import dataclass


@dataclass
class Product:
    handle: str
    name: str
    category: str
    subcategory: str
    brand: str
    base_price: float
    discount: float
    year: int
    rating: float
    tags: list[str]
    img_urls: list[str]
    basic_properties: dict[str, str]
    description: str = ""

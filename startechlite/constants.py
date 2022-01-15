"""Any changes here need to be reflected back on the templates manually"""


class Component:
    COMPONENT = "component"

    class Processor:
        PROCESSOR = "processor"
        AMD = "amd-processor"
        INTEL = "intel-processor"


class Desktop:
    SUBCATEGORIES = [
        "special-pc", "star-pc", "gaming-pc", "brand-pc", "all-in-one-pc", "portable-mini-pc",
        "apple-mini-pc", "apple-imac-desktop-pc", "economy-pc"
    ]
    BRANDS = [
        "ryzen-pc", "intel-pc", "lenovo-desktop", "hp-desktop", "dell-dekstop", "acer-dekstop",
        "asus-desktop", "walton-brand-pc", "dell-all-in-one", "i-life-all-in-one", "hp-all-in-one",
        "asus-all-in-one", "lenovo-all-in-one", "asrock-portable-mini-pc", "viewsonic-mini-pc",
        "mini-pc-asus", "intel-mini-pc", "gigabyte-mini-pc", "zotac-portable-mini-pc", "/chuwi-mini-pc",
        "apple-mini-pc", "apple-imac-desktop-pc"
    ]

class Item:
    def __init__(self, title: str, name: str, brand_title: str, img_url: str, short_descriptions: list[str] = []):
        self.title = title
        self.name = name # website internal name
        self.brand_title = brand_title
        self.img_url = img_url
        self.short_descriptions = short_descriptions

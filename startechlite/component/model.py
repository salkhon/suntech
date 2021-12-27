class Item:
    def __init__(self, title: str, img_url: str, short_descriptions: list[str] = []):
        self.title = title
        self.img_url = img_url
        self.short_descriptions = short_descriptions

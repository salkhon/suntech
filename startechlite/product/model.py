from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    base_price: float
    discount: float
    rating: float
    category: str
    subcategory: str
    brand: str
    stock: int
    year: int
    img_urls: list[str]
    spec_dict: dict[str, str]
    EMI: float
    bought_together: list["Product"]

    def inStock(self) -> str:
        if self.stock > 0:
            # return str(self.stock)
            return "In Stock"
        else:
            return "Currently Unavailable"

    def summaryProperties(self) -> OrderedDict:
        # Same as mainProperties() but with shorted values
        if self.category == 'Laptop':
            d = OrderedDict()

            if 'Processor' in self.spec_dict:
                d['Processor'] = self.spec_dict['Processor'].split('(')[
                    0]
            if 'Graphics Card' in self.spec_dict:
                d['Graphics Card'] = self.spec_dict['Graphics Card']
            if 'RAM' in self.spec_dict:
                d['RAM'] = self.spec_dict['RAM']
            if 'Operating System' in self.spec_dict:
                d['Operating System'] = self.spec_dict['Operating System']
            if 'Display' in self.spec_dict:
                d['Display'] = self.spec_dict['Display'].split('(')[0]
            if 'Storage' in self.spec_dict:
                d['Storage'] = self.spec_dict['Storage'].split(' ')[0]

            return d

        if self.category == 'Desktop':
            d = OrderedDict()

            if 'Processor' in self.spec_dict:
                d['Processor'] = self.spec_dict['Processor'].split('(')[
                    0]
            if 'Graphics Card' in self.spec_dict:
                d['Graphics Card'] = self.spec_dict['Graphics Card']
            if 'RAM' in self.spec_dict:
                d['RAM'] = self.spec_dict['RAM']
            if 'Motherboard' in self.spec_dict:
                d['Motherboard'] = self.spec_dict['Motherboard']
            if 'Storage' in self.spec_dict:
                d['Storage'] = self.spec_dict['Storage'].split(' ')[0]

            return d

        if self.category == 'Monitor':
            d = OrderedDict()
            if 'Screen Size' in self.spec_dict:
                d['Screen Size'] = self.spec_dict['Screen Size']
            if 'Refresh Rate' in self.spec_dict:
                d['Refresh Rate'] = self.spec_dict['Refresh Rate']
            if 'Resolution' in self.spec_dict:
                d['Resolution'] = self.spec_dict['Resolution']
            if 'Brightness' in self.spec_dict:
                d['Brightness'] = self.spec_dict['Brightness']

            return d

        return OrderedDict()

    def mainProperties(self) -> OrderedDict:
        if self.category == 'Laptop':
            d = OrderedDict()

            if 'Processor' in self.spec_dict:
                d['Processor'] = self.spec_dict['Processor']
            if 'Graphics Card' in self.spec_dict:
                d['Graphics Card'] = self.spec_dict['Graphics Card']
            if 'RAM' in self.spec_dict:
                d['RAM'] = self.spec_dict['RAM']
            if 'Operating System' in self.spec_dict:
                d['Operating System'] = self.spec_dict['Operating System']
            if 'Display' in self.spec_dict:
                d['Display'] = self.spec_dict['Display']
            if 'Storage' in self.spec_dict:
                d['Storage'] = self.spec_dict['Storage']

            return d

        if self.category == 'Desktop':

            d = OrderedDict()

            if 'Processor' in self.spec_dict:
                d['Processor'] = self.spec_dict['Processor']
            if 'Graphics Card' in self.spec_dict:
                d['Graphics Card'] = self.spec_dict['Graphics Card']
            if 'RAM' in self.spec_dict:
                d['RAM'] = self.spec_dict['RAM']
            if 'Motherboard' in self.spec_dict:
                d['Motherboard'] = self.spec_dict['Motherboard']
            if 'Storage' in self.spec_dict:
                d['Storage'] = self.spec_dict['Storage']

            return d

        if self.category == 'Monitor':
            d = OrderedDict()
            if 'Screen Size' in self.spec_dict:
                d['Screen Size'] = self.spec_dict['Screen Size']
            if 'Refresh Rate' in self.spec_dict:
                d['Refresh Rate'] = self.spec_dict['Refresh Rate']
            if 'Resolution' in self.spec_dict:
                d['Resolution'] = self.spec_dict['Resolution']
            if 'Brightness' in self.spec_dict:
                d['Brightness'] = self.spec_dict['Brightness']
            return d

        return OrderedDict(self.spec_dict)

    def otherProperties(self) -> dict:

        mainDict = self.mainProperties()
        d = {}
        for key in self.spec_dict:
            if key == 'Name' or key in mainDict:
                continue
            d[key] = self.spec_dict[key]

        return d

    def compareWith(self, product2):
        d = OrderedDict()
        dict1 = self.mainProperties()
        dict2 = product2.mainProperties()

        for key in dict1:
            if key in dict2:
                d[key] = [dict1[key], dict2[key]]
            else:
                d[key] = [dict1[key], ' ']

        for key in dict2:
            if key in d:
                continue
            else:
                d[key] = [' ', dict2[key]]

        d2 = {}

        dict1 = self.otherProperties()
        dict2 = product2.otherProperties()

        for key in dict1:
            if key in dict2:
                d2[key] = [dict1[key], dict2[key]]
            else:
                d2[key] = [dict1[key], ' ']

        for key in dict2:
            if key in d2:
                continue
            else:
                d2[key] = [' ', dict2[key]]

        return d, d2


@dataclass
class Bundle:
    id: int
    name: str
    products_list: list[Product]

    def inStock(self):
        for product in self.products_list:
            if product.stock == 0:
                return False

        return True

    def total_price(self) -> int:
        total = 0

        for product in self.products_list:
            total += product.base_price

        return int(total)

# type: ignore
from math import nan
from unicodedata import category
import pandas as pd
import cx_Oracle


def is_number(s):
    if len(s) == 0:
        return False
    if s[0] in '0123456789':
        return True
    return False


def insert_Products_Specs(c, csv_location, range_start):
    """change csv file name, id, range for each product type """
    dataX = pd.read_csv(csv_location)

    for i in range(dataX.shape[0]):

        id = dataX.loc[i]["Index"]
        base_price = dataX.loc[i]["Price"]
        category = dataX.loc[i]["Category"]
        subcategory = dataX.loc[i]["Subcategory"]
        brand = dataX.loc[i]["Brand"]

        print(id, brand)

        if base_price == '' or str(base_price) == 'nan':
            # skipping stuff that has no price mentioned
            continue

        # Some products have a format like 16,000 and others have two prices.

        base_price = base_price.replace(',', '')
        base_price = base_price.split(' ')[0]
        base_price = base_price.split('\n')[0]

        if is_number(base_price) == False:
            continue

        discount = 0

        stock = 10

        product_insert_sql = "insert into salman.products (id, base_price, discount, category, subcategory, brand, stock) values("+str(
            id)+f","+str(base_price)+","+str(discount)+",\'"+str(category)+"\',\'"+str(subcategory)+"\',\'"+str(brand)+"\',"+str(stock)+")"

        print(product_insert_sql)
        c.execute(product_insert_sql)

        print("Inserted item "+str(i))


# SPEC TABLE INSERTION
    for column in dataX:

        if column in ["Unnamed: 0", "Price", "Category", "Subcategory", "Brand"]:
            continue

        temp = dataX[column].dropna()
        df = temp.to_frame()

        for index, attr_value in df.iterrows():
            values = "values ("+str(range_start+index)+", \'" + \
                str(column)+"\' ,\'"+str(attr_value[column])+"\')"
            insert_to_spec_table = "insert into salman.spec_table (product_id, attr_name, attr_value)" + values
            # print(insert_to_spec_table)
            try:
                c.execute(insert_to_spec_table)
                print(insert_to_spec_table)
            except:
                continue
            print("inserted attribute of item "+str(index))


def insert_images(c, csv_location):

    img_data = pd.read_csv(csv_location)

    for i in range(img_data.shape[0]):
        product_id = img_data.iloc[i]["Index"]
        img_url = img_data.iloc[i]["Link"]
        insert_img_sql = "insert into salman.images(product_id,img_url) values ("+str(
            product_id)+", \'"+img_url+"\')"
        try:
            c.execute(insert_img_sql)
        except:
            continue
        # print("inserted image of item: "+str(product_id))


conn = cx_Oracle.connect(user=r'salman', password='salman',
                         dsn="localhost/startechlite", encoding="UTF-8")
c = conn.cursor()

insert_Products_Specs(c, "data\monitor.csv", 2500)
c.execute("commit")
insert_images(c, "data\monitorImg.csv")
c.execute("commit")


insert_Products_Specs(c, "data\desktop.csv", 1)
c.execute("commit")
insert_images(c, "data\desktopImg.csv")
c.execute("commit")


insert_Products_Specs(c, "data\laptops.csv", 1001)
c.execute("commit")
insert_images(c, "data\laptopImg.csv")
c.execute("commit")
c.execute(" delete FROM salman.spec_table where ATTR_NAME like '%Unnamed%' ")

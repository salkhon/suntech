# SunTech
SunTech is a project for the database course CSE216 of L2T2. The purpose of this project is to use databases to emulate a real world application. In this project we use databases in a webapp that sells tech products, mainly PC components.

## Running on your PC

### 1. Cloning repo
Copy the repo link from the code section:\
![repo](/startechlite/static/img/clone.png)
\
Run `git clone <repo link>` on your terminal at the appropriate directory.

### 2. Downloading images
The images for this webapp exceed github's file size restriction, so you have to download them from the following google drive link:
[SunTech Images](https://drive.google.com/drive/folders/1-tysqCQBnzjx3oBqQWv6LcE-A8N-R-kM?usp=sharing).\
\
The downloaded `products` folder will contain the images in their corresponding id folder. Put this folder in the following directory **relative** to the project root:
`/startechlite/static/img/`\
\
So after putting `products` in the appropriate directory the folders containing the images should be in:
`/startechlite/static/img/products/`

### 3. Preparing database
This project uses oracle as its backend database. So having oracle client installed in your machine is essential. Therefore you have to log in as the appropriate user, and have permissions to manipulate the database accordingly.

There are 3 steps to perform to set up your database as per the webapp's needs. 
#### a. Setting username and password
You have to open a database user by the name `salman` and set its password to `salman`. You also have to open a pluggable database session with the dsn `localhost/startechlite`.\
\
Or, if you want to use your existing user and pdbs session, open `startechlite/config.py`. In that file, inside the `Config` class, set its following attributes:
```
DB_USER = "<your db username>"
DB_PASS = "<your db pass>"
DB_CONNECTION_STR = "localhost/<your pluggable database>"
```
#### b. Creating tables
After you have logged in as the database user using any of the two methods on step a, run the sql file: `data\CREATE_TABLES.sql` to create the tables. 
#### c. Inserting data
Then run: `data\INSERT_DATA.sql` to insert the data. It is advisable to run the insertion sql using sqlplus in the terminal to have it done quicker. 
### 4. Installing dependencies
To install all the dependencies of the webapp run the following pip command:
```
pip install requirements.txt
```
### 5. Running
After completing these steps run the webapp by executing the file: `run.py`. 

## Features
This webapp is designed to sell PC related products, and the features revolve around that goal. There are two types of access to the webapp:
### 1. User 
#### - Registration
#### - Login
#### - Browse Products
#### - Compare Products
#### - Search Products
#### - Filter Products
#### - Add Products to Cart
#### - Purchase Products
#### - Update and Delete Purchase
#### - Logout

### 2. Admin
#### - Login
Admins can login with a special account that can be accessed by loggin in using the email: `admin@suntech.com`, and the password `admin`. Further features can be accessed through the navigation bar after loggin in. 
#### - View Users
Clicking on the `Users` link on the navigation bar the admin can see the list of suntech users currently registered. By clicking on any of the fields of the list, admin can visit the user specific page. 
#### - Update Users
By visiting the user's page, the admin can change the user's name, phone number and address. After performing the changes, the admin has to click the update button at the bottom of the page to complete that update. 
#### - Ban Users
Admin can also ban misbehaving users. Banned users lose access to their account. Moreover, they can never register another account with that banned email. 
#### - View Purchases
Clicking on the `Purchases` option from the navbar, admin can see the list of purchases made on suntech. Clicking on any of the fields of each purchase, admin can visit purchase specific page. 
#### - Approve Purchases
On the puchase list, those that have not been approved, have an approve button. Admin can click the approve button to approve the purchase to "lock in" the purchase. 
#### - Update Purchases
In the purchase specific page, admin can view the details of the purchase. Before approving the purchase, admin can change the purchase address. 
#### - Delete Purchases
Before approving the purchase, admin can also delete the purchase. 
#### - Create Product
Admins can create new products to be viewed on the site. By clicking on the `Create Product` option from the navbar, admin can go to the product creation page. By entering appropriate values for each fields of the new product, and then clicking on the create button, admin can create a product. It will then show up as a bare-bone product on its respective "Category", "Subcategory" and "Brand".
#### - Edit Product
Admins can edit existing and newly created product. After creating a bare-bone product, admin must edit and decorate a product to make it attractive. By clicking on any product, admin can go to the editing page. There admin can edit the product's name, base price, discount, rating, stock, year etc attributes. Admin can also upload any image that corresponds to the product. That image will show up on the product's individual page. 
#### - Add Product Specification
Implementing the Entity Attribute Value model for our database design, we can allow products to have variable number of attrbutes, according to the product's unique features. The admin simply has to visit the bottom part of the edit product page, and add an attribute name and it's corresponding value and click the add button. That new attribute will show up on the product's page. Moreover, that attribute is now directly comparable with other product's having the same attribute name using SunTech's compare now feature. 
#### - Delete Product
Beside the update button for each product is a delete button, that deletes a product. 
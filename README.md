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
## 1. User 
### a. Registration
### b. Login
### c. Browse Products
### d. Compare Products
### e. Search Products
### f. Filter Products
### g. Add Products to Cart
### h. Purchase Products
### i. Update and Delete Purchase
### j. Logout

## 2. Admin
### a. View Users
### b. Update Users
### c. Ban Users
### d. View Purchases
### e. Approve Purchases
### f. Update Purchases
### g. Delete Purchases
### h. Create Product
### i. Edit Product
### j. Add Product Specification
### k. Delete Product
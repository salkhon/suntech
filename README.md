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
The downloaded `products` folder will contain the images. Put this folder in the following directory **relative** to the project root:
`/startechlite/static/img/`\
\
So after putting `products` in the appropriate directory the folders containing the images should be in:
`/startechlite/static/img/products/`

### 3. Preparing database
There are 3 steps to perform to set up your database as per the webapp's needs. 
#### a. Setting username and password
You have to open a database user by the name `salman` and set its password to `salman`. You also have to open a pluggable database session with the dsn `localhost/startechlite`.\
\
Or, If you want to use your user and pdbs session, the process is a bit more tedious. Open `startechlite/config.py`. In that file, inside the `Config` class, set its following attributes:\
```
DB_USER = "<your db username>"
DB_PASS = "<your db pass>"
DB_CONNECTION_STR = "localhost/<your pluggable database>"
```
Then open `data\CREATE_TABLES.sql` and rename all the tables from `salman.tablename` to `<your username>.tablename`. Do the same in `data\INSERT_DATA.sql`.
#### b. Creating tables
After you have logged in after performing any of the two methods on step a, run the sql file: `data\CREATE_TABLES.sql` to create the tables. 
#### b. Inserting data
Then run: `data\INSERT_DATA.sql` to insert the data. It is advisable to run the insertion sql using sqlplus in the terminal to have it done quicker. 
### 4. Installing dependencies
To install all the dependecies of the webapp run the following pip command:\
```
pip install requirements.txt
```
### 5. Running
After completing these steps run the webapp by executing the file: `run.py`. 

## Features

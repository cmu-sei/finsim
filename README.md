FinSim

Copyright 2018 Carnegie Mellon University. All Rights Reserved.

NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.

Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

# Financial Simulator

## v2.0, Updated AO 29 May 2019

## Brief:
- Simulates a financial system
- Involves merchants, cc processors, and banks
- Transactions are generated at merchant point of sale (PoS) systems and sent to credit card processors to banks and back

## Initial Setup
- [Optional] `nano .bashrc` to change the `HISTSIZE` and `HISTFILESIZE` to `-1` - not needed for setting up the environment, just to have all commands history kept
    - Feel free to use your preferred text editor in lieu of nano
- `sudo apt update`
- `sudo apt install mysql-client mysql-server python3-dev gcc libmysqlclient-dev python3-venv python3-virtualenv python3-pip apache2 libapache2-mod-wsgi-py3 virtualenv python3-flask`
- `virtualenv -p python3 venv`
- `. venv/bin/activate`
- `pip3 install flask flask-restful flask_cors flask-jwt-extended passlib flask-sqlalchemy mysqlclient requests Faker pyyaml`
- `mysql -u root -p`
    - At a minimum, you need a database for finsim-cc and finsim-trans (1 finsim-merch, 1 finsim-cc, and 1 finsim-trans/web)
    - in mysql, call the following commands:
        - `set sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';`
        - `create database cc; create database trans;`
        - `grant usage on *.* to cc@localhost identified by ''; grant usage on *.* to trans@localhost identified by '';`
        - `grant all privileges on cc.* to cc@localhost; grant all privileges on trans.* to trans@localhost;`
        - `set sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';`
- Download nodejs and npm
- npm install -g @angular/cli
- ng add @angular/material

## Description:

### Uses:
- Python 3.6.5
- Flask 1.0.2
- mysql 5.7.24-0
- ubuntu0.18.04.1
- flask-restful flask-jwt-extended flask-sqlalchemy flask_cors
- Apache and WSGI
- NodeJs v8.10.0
- npm v3.5.2
- Angular CLI 6.0.8
- *See additional dependencies for FinSim-web in /finsim-web/packages.json*

### Project Overview:

#### /finsim-merch:
- FinSim-merch acts as a merchant Point of Sale (PoS) system - generates transactions to send to FinSim-cc to be processed

#### /finsim-cc:
- FinSim-cc acts as a credit card processor - a medium between FinSim-merch and FinSim-trans

#### /finsim-trans:
- FinSim-trans acts as a bank - processes transactions passed on from FinSim-cc and holds account information, allowing for deposits/withdrawals

#### /finsim-web:
- FinSim-web is the frontend for the transaction server - allows users to access accounts to view balances and transaction logs with a web browser

#### init_script.py:
- `init_script.py` generates and can populate databases with all of the account information and login info needed for each component based on a random seed for Faker and Random libraries
- `init_script.py` is critical for setup prior to deployment! Run `python3 init_script.py --h` to learn how to use it
- Used by finsim-merch, finsim-cc, and finsim-trans. Each component directory contains a symlink to this file

#### url_list.txt:
- List of cc and bank IDs and urls. In deployment, its full path is `/home/url_list.txt`

#### clear_tables.sql:
- Quick MySQL script to drop tables for each database


## Known Issues:
- Some seeds may generate duplicate accounts (i.e. seed '2' can generate two of the same user accounts but with different passwords - resulting in the init_script failing to move past the second user account during initialization)
    - Will need to add checks in init_script.py to check for duplicates during account generation
- Issue with Angular production project code (moved .vmdks from one deployment to another. Kept same IP configs. User machine gets 200 OK responses when accessing the frontend via Firefox but the '/' url does not get routed to the /login component). Recompiled without the production flag set and the second deployment worked
    - Need to troubleshoot it further
- Need to introduce a finsim-atm component or something else that strictly generates deposits/withdrawals, and remove deposit generation from finsim-merch
    - Not very realistic to have merchants generate deposits as well as transactions
- Many more deposits than transactions for individual accounts due to how finsim-merch works
    - 70% of the time, generate a deposit for a randomly selected account. Otherwise, a transaction will be generated for a randomly selected account
- [Low] Need to add error-checking into the various endpoints and functions at a later point in development (input sanitation/error-catching) - primarily to prevent errors causing app crashes
- [Medium] Standardize the returns of all endpoints so that it always includes a message regardless of result - primarily for marshal_with/formatting purposes
- Need to add more e2e testing and code-level documentation to finsim-web


## Changelog:

### May:
- Restructured project structure
- Added additional documentation for Apache/WSGI, and cleaned up this README
- Added doc markings to prepare for open-source

### April:
- Finished up FinSim for X-Games 2019. Implemented with production server, merchant scripts, init_scripts

### Prior:
- Basic functionality for finsim-cc
- Used script to register users with finsim-cc for testing


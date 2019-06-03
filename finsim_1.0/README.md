FinSim
Copyright 2018 Carnegie Mellon University. All Rights Reserved.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

FinSim Documentation – Use and High-level Overview
FinSim is divided into two parts – transaction and web.

Quick Usage:
- To run the web server:
	- Run "systemctl start httpd.service"
	- Double check that it has successfully started by
		- run "systemctl status httpd.service"
		- access ehg.com with a browser
- To run the transaction clients/server (Assuming you have one instance of server, separate from n clients):
	- For the server instance, cd to the directory that has the Finance code
	- Run "python main.py config Server"
	- If it ran correctly, "Ready to transfer....." will print out to the terminal.
	- For the clients, cd to the directory that has the Finance code
	- Run "python main.py config Merchant Company"
		- This will generate all merchants and card companies listed in the current config file. Look at the description below to find out how to run only select merchants and companies"
	- If it is successful, there should be no output to the terminal
	- And the logs in the current directory for each merchant/card company should be opened and being written to by the python script
- If there are issues following these steps, read further into the README for a more thorough description on how to set up FinSim 1.0 properly


Description:
- Transaction client/server
	- Used Windows Server 2012
		- If more than 1 instance, make sure to have just one instance running the database server
- Web Server
	- Used CentOS 7
- There is always only one instance of the web server code
	- Uses Django
	- Uses Apache
- Anywhere from 1-n instances of the transaction client/server code
	- Clients generated can be on any of the instances
	- 1 transaction instance - all clients generated on the same instance hosting the transaction server
	- 2 instances - 1 designated as transaction server, and the clients can be split up between the two instances
	- For realism, it is recommended to have multiple instances of transaction where one is the transaction server and n-1 instances represent a client
- Transaction server uses Microsoft SQL
- Make sure you have or do the following:
	- Python 2.7
	- pymssql-2.1.1
	- Faker (pip install Faker)
	- Modify firewall rules to accept tcp connections on the ports used in FinSim (check the config file to see which ones - these can be changed, as long as no two ports are the same)
	- Modify IPv4 and etc to make sure that all instances can interact with each other
	- If you want to use a different port than 1433 for the web server, add the port to allow connections


Transaction Overview:
- main.py, when called, parses through the config file and based on how main.py was called, starts the simulations for the server, card companies, and merchants
    - main.py has a Config class that parses through the config file so that the data is returned in dictionaries to easily use
    - starting the simulations depend on what type of role the current actor will play
        - server – sets up the database and transaction servers
            - uses Sqlserver.py and transaction_server.py
        - merchant – sets up the merchant
            - uses merchant.py
        - card – sets up the card company
            - uses card_co.py
    - [IMPORTANT] To start up the transaction server, run main.py.
        - “python main.py arg0 arg1 arg2 …”
        - if main.py is called with “–h”, “—help”, or “help”, instructions on how to run main.py are printed out to the screen
        - arg0 is the location of the config file (if in the same folder as main.py, simply put the name of the config file
        - The following arguments can be any combination of the following:
            - “Server”
                - Starts the simulation for the server
            - “Company” or “–c”
                - If “–c“ is used, the name of the card companies should be listed as arguments after (same notation as –m)
                - Only “Company” or “–c” should be used, not both
            - “Merchant” or “–m”
                - If “–m” is used, the name of the merchants should be listed as arguments after (i.e. “–m merchantA merchantB merchantC”)
                - Only “Merchant” or “–m” should be used, not both
- card_co.py is called by main.py when the simulation starts for a card company
    - Connects to the server
    - Maintains a log that is written to a txt file called “<Name of Card>_log.txt”
    - Reads any requests from the server to store in the log file, verify the card information, and write the results back to the server
- merchant.py is called by main.py when the simulation starts for a merchant
    - merchant is divided into two parts – customer_in and customer_out
    - connects to the server
    - customer_in calls traffic_out while customer_out calls traffic_in
        - traffic_out does the following:
            - generate random traffic and write it back to server
                - Uses users.txt to pick a random user to be the subject of the transaction – with a random amount withdrawn or deposited
        - traffic_in does the following:
            - maintains a log that is written to a txt file called “<Name of Merchant>_log.txt”
            - reads any requests from the server and writes down the results into the log
- transaction_server.py is called by main.py when the simulation starts for a server
    - handles the requests appropriately by calling deal_with_customer_in/out or deal_with_card
    - all will be handled with the database/config, or added to the queue
- Sqlserver.py is also called by main.py when the simulation starts for a server
    - Sets up the database and checks the tables if need be
    - Can print out the results
    - Generate fake data for merchants/finance to be added to the specific table
    - Adds an entry to the transactions table
    - The 4 tables used by Sqlserver.py on the transaction server end is Finance, Merchants, Transactions, and TransRecord
        - Finance is the list of card companies used by the transaction server
        - Merchants is the list of merchants used by the transaction server
        - Transactions are the list of transactions that are generated by the transaction server code
        - TransRecord has 3 columns: Invoice, Confirmation Code, and ResponseCode for every transaction in the Transactions table
            - ResponseCode determines whether the transaction was approved/denied/etc
    - Sqlserver opens up the connection to the database and executes the specific queries to/from the database
- sock.py binds the address and port for the transaction server and begins listening/accepting connections
    - When accepting connections, print the address and close the connection
    - Socket is used for clients and the transaction server in order for communication to take place (i.e. between a merchant and the transaction server)
- users.txt is a list of entries of users and their information, used by merchants in the config file. Each entry has the following:
    - firstname
    - lastname
    - middleinitial
    - address
    - city
    - state
    - zipcode
    - cardnumber
    - expdate
    - cvv2
    - invoice
    - avs
    - authtype
    - primaryamount
    - secondaryamount
- ssl_cert folder contains .pem files for every merchant and card company
    - Which contains the certificate and key
Current issues with Transaction:
- main.py line 50 in the getConfig method – if/elif logic
- card_co.py line 93 in the expVer method – checks year and day, not year and month like most credit cards have as an expiration date
- merchant.py:
    - line 55 in the run method of the merchant class – if/elif logic
    - line 134 in the traffic_out method – repetitive traffic.close()?
- transaction_server.py:
    - line 67 and 226 – pass as class
    - line 133 in the deal_with_customer_in stores the same value as the previous line?
- [TEMPORARILY RESOLVED] SSL Certificate Verify failed - (ssl.c:661) for each merchant and company
    - This error occurs if main.py is run with the Server included
    - Without the Server included as one of the arguments, the error for each is:
        - [Errno 10061] 'No connection could be made because the target machine actively refused it')
        - This makes sense because the merchants/companies need to interact with the SQL transaction server.
        - Changed to not require certificates to make sure the rest of the code works. cert_reqs changed from CERT_REQUIRED to CERT_NONE in both card_co.py and merchant.py
        - MAKE SURE TO BE AWARE OF THIS WHEN DEPLOYING


Web Server Overview:
- [IMPORTANT] To start up the web server:
    - [FOR TESTING PURPOSES – this is only the development server] Start up the server using the host IP and the port added to the firewall rules:
        - “python manage.py runserver 10.16.241.114:8000”
    - Make sure the router/firewalls are configured correctly in order to allow the connections
        - Web Server needs to establish a connection with the VM the database is on in order to start up
        - Make sure the other machines you will be using will in fact be able to connect to the web server (usually through a web browser)
    - Systemctl httpd.service start/stop/restart in order to manage the production web server
        - Note that you must restart the web server if you ever make any changes to the code
    - To run any Django commands…
        - “python manage.py <Django command>”
        - For example, “python manage.py makemigrations” followed by “python manage.py migrate” will save and apply any changes made to the models/views/serializers files in the app folder.
        - HTML file changes can be applied/saved by using the previous command (systemctl httpd.service restart)
- bin
    - xyzbank.conf:
        - Sets up web framework/server info
- www
    - [CHANGED dir name, was originally bancodelaargentina] ehg 
        - manage.py:
            - Executes the following Django commands – is the main python file to call to work with the web server
            - “python manage.py runserver 10.16.241.114:8000” will start the development web server on the host IP (for the AR version, 10.16.241.114 is the host ip) for port 8000
                - Ignore IP addresses and ports listed above – use the actual topology info
        - [dir] app:
            - Forms/models/serializers/views is mainly used for the frontend – what is seen by the user. Models specifically lays out the format of the database tables used by the web server
            - [dir] Templates/app contains the html files that is seen by the user when they access the website
            - [dir] templatetags contains the customtags.py file that is mainly just used by history.html in templates/apps
                - Contains withdraw_balance and deposit_balance – does not actually modify the balance saved in the database tables but is for visual purposes
                - [NOTE] The operations are swapped because when history.html is calling withdraw or deposit, the balance is already added to/subtracted from
        - xyzbank:
            - process_request.py:
                - Handles requests received by clients
            - Settings.py is the config file for the Django framework
    - migrations
        - 0001_initial.py
            - Contains the models for commercial/user accounts and transactions
        - _init_.py:
            - Contains all of the accounts that are added to for use in FinSim
            - Saved to CommercialAccounts and UserAccounts


Current issues with Web:
- (in bancodelaargentina/xyzbank folder) _init_.py is empty
    - Probably insignificant – maybe a file that gets created when a django project is created with a template?


Changelog:
 Changes made to 2017 X-Games code for 2018 X-Games:
- Transaction Server:
    - Did not have python installed
        - Had a folder called “Python27” in the recycle bin. Restored it, hoping it would have Python. Has pymssql, specifically for python 2.7, but not python itself
    - Did not have Faker module installed either.
    - Installed python 2.7.14, and then run “pip install Faker” to install the module
    - To start the transaction server, run “main.py /location/of/config Server –c Company1 Company2 … CompanyN –m Merchant1 Merchant2 … MerchantN”
    - I run it with “main.py “C:/Users/share/Finance/config” Server –c Amex –m Walmart just to test
    - (In the config file) Changed DB name from "Transactions" to "TransactionServer" (there was no DB named "Transactions" found)
    - (In the config file) Changed the IP addresses and port numbers listed to match the host IP address and to use different ports for the server/merchants/companies listed
    - (Windows Firewall with Advanced Security app) added inbound and outbound rules to accept TCP connections for ports 3500-3512 (which are collectively used by the server/merchants/companies)
    - (In sock.py file) Changed IP address to match the host IP address
    - merchant.py:
        - Sleep from 10 seconds - flow seconds (2018 x-games flow value is set as 20 seconds)
        - Generate 20,000,000 transactions per merchant
        - 2 to 1 ratio of generating a deposit or withdrawal transaction
    - Sqlserver.py
        - Added in additional queries to update both CommercialAccounts and CommercialTransaction tables
- Web Server:
    - [IMPORTANT] REMOVED SECRET KEY FROM THE FOLLOWING FILES (Make sure to add in your own secret key):
        - /web/bin/mysql.py
        - /web/bin/oracle.py
        - /web/bin/postges.py
        - /web/bin/sqlite.py
        - /web/www/bancodelaargentina/xyzbank/settings.py
    - Added in logoff functionality in loginpartial.html
    - Added in functionality of the history and profile html pages to properly show updated balances and transactions in real time by modifying models.py, views.py, and html files on the web server side (check transaction client/server documentation on what was changed there)
    - Changed scenario from Banco dela Argentina to Equity Holdings Group (html files, settings.py, wsgi.py, etc - check gitlab repo for commit history)
    - Also changed the directory name to ehg rather than bancodelaargentina
    - Edited banking.conf - the Apache config file
    - All instances of bancodelaargentina (as a directory, url, etc) to ehg
        - /etc/httpd/conf.d/banking.conf

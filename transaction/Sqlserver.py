# FinSim
#
# Copyright 2019 Carnegie Mellon University. All Rights Reserved.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#
# Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#
# [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#
# This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#
# 1. Django (https://www.djangoproject.com/foundation/faq/) Copyright 2005-2018 Django Software Foundation.
# 2. bootstrap (https://getbootstrap.com/docs/4.0/about/license/) Copyright 2018 Twitter.
# 3. glyphicons (https://www.glyphicons.com/license/) Copyright 2010-2018 GLYPHICONS.
# 4. jquery (https://jquery.org/license/) Copyright 2018 jquery foundation.
# 5. jquery tablesorter (https://mottie.github.io/tablesorter/docs/) Copyright 2007-2018 Christian Bach, Rob Garrison and Contributing Authors (see AUTHORS file).
# 6. jquery validate (https://jqueryvalidation.org/) Copyright 2006-2018 J�rn Zaefferer,  Markus Staab, Brahim Arkni, and contributors .
# 7. jquery validate unobtrusive (https://github.com/aspnet/jquery-validation-unobtrusive/blob/master/LICENSE.txt) Copyright 2014-2018 .NET Foundation.
# 8. modernizr (https://github.com/Modernizr/Modernizr/blob/master/LICENSE) Copyright 2009-2018 https://github.com/Modernizr/Modernizr/graphs/contributors.
# 9. respond.js (https://github.com/scottjehl/Respond) Copyright 2011 Scott Jehl.
# 10. roboto fonts (https://fonts.google.com/specimen/Roboto) Copyright 2015-2018 Google, Inc..
# 11. xregexp (http://xregexp.com/) Copyright 2007-2012 Steven Levithan.
#
# DM19-0396
#

import _mssql
from faker import Factory
from datetime import datetime

class Sqlserver:
    #__init__(...) tries to connect to the database with the specified parameter info
	def __init__(self, server, database, user, password):
		try:
			self.conn = _mssql.connect(server=server, database=database, user=user, password=password)      #try to connect to the database
		except _mssql.MssqlDatabaseException as e:      #catch any errors
			print "Error in connection to the database server: " + repr(e)      #print the db connection error
			raise Exception('BAD DB CONNECT')

    #resultsStream(self, entry)  obtains the entries in transactions, merchants, and finance that match what are found in the entry parameter
    #   and updates the sets based on approved/denied, and adds the results into transrecord
	def resultsStream(self, entry):
		self.conn.execute_query("Select * from Transactions where Invoice = '" + str(entry['invoice']) + "'")       #select entries in the transaction table from the database where invoice values match what is found in the specified entry list
		trans_row_entry = [l for l in self.conn]    #store query results in trans_row_entry
		balance = trans_row_entry[0]['PrimaryAmount']   
		self.conn.execute_query("Select * from Merchants where ID = '" + str(entry['invoice'][:5]) + "'")       #select entries in the merchants table where the id matches what is found in the entry list excluding the last 5 elements
		update_mer = [l for l in self.conn]     #store query results in update_mer
		self.conn.execute_query("Select * from Finance where ID = '" + str(entry['confirmation_code'][:5]) + "'")   #select entries in the finance table where the id matches what is found in the entry list for confirmation codes excluding the last 5 elements
		update_fin = [l for l in self.conn]     #store query results in update_fin
		command = "UPDATE Finance SET "
		command2 = "UPDATE app_commercialaccounts SET "
		if str(entry['response_code']) != '0':      #if response code is not equal to 0
			command = command + "Denied = " + str(update_fin[0]['Denied'] + 1)      #denied, with what is denied appended to the end of command
			command2 = command2 + "Denied = " + str(update_fin[0]['Denied'] + 1)
		else:       #response code is equal to 0
		    if trans_row_entry[0]['AuthType'] == "Minus":
    			command = command + "Approved = " + str(update_fin[0]['Approved'] + 1) + ", Balance = " + str(update_fin[0]['Balance'] - balance)   #approved, with what is approved appended to the end of the command with the balance as well
    			command2 = command2 + "Approved = " + str(update_fin[0]['Approved'] + 1) + ", Balance = " + str(update_fin[0]['Balance'] - balance)
	        else:
	            command = command + "Approved = " + str(update_fin[0]['Approved'] + 1) + ", Balance = " + str(update_fin[0]['Balance'] + balance) 
	            command2 = command2 + "Approved = " + str(update_fin[0]['Approved'] + 1) + ", Balance = " + str(update_fin[0]['Balance'] + balance)
		command = command + ", Transactions = " + str(update_fin[0]['Transactions'] + 1) + " where ID = " + str(entry['confirmation_code'][:5])     #after denied/approved, add transactions to end of command
		command2 = command2 + ", Transactions = " + str(update_fin[0]['Transactions'] + 1) + " where ID = " + str(entry['confirmation_code'][:5])
		self.conn.execute_non_query(command)	#execute the command - update finance set denied/approved, transactions
		self.conn.execute_non_query(command2)
		command = "UPDATE Merchants SET "
		command2 = "UPDATE app_commercialaccounts SET"
		if str(entry['response_code']) != '0':
			command = command + "Denied = " + str(update_mer[0]['Denied'] + 1)
			command2 = command2 + "Denied = " + str(update_mer[0]['Denied'] + 1)
		else:
		    if trans_row_entry[0]['AuthType'] == "Minus":
    			command = command + "Approved = " + str(update_mer[0]['Approved'] + 1) + ", Balance = " + str(update_mer[0]['Balance'] - balance)
    			command2 = command2 + "Approved = " + str(update_mer[0]['Approved'] + 1) + ", Balance = " + str(update_mer[0]['Balance'] - balance)
            else:
                command = command + "Approved = " + str(update_mer[0]['Approved'] + 1) + ", Balance = " + str(update_mer[0]['Balance'] + balance)
    			command2 = command2 + "Approved = " + str(update_mer[0]['Approved'] + 1) + ", Balance = " + str(update_mer[0]['Balance'] + balance)
		command = command + ", Transactions = " + str(update_mer[0]['Transactions'] + 1) + " where ID = " + str(entry['invoice'][:5])
		command2 = command2 + ", Transactions = " + str(update_mer[0]['Transactions'] + 1) + " where ID = " + str(entry['invoice'][:5])
		self.conn.execute_non_query(command)	#Similar to finance, updating merchants - update merchants set denied/approved, transactions
		self.conn.execute_non_query(command2)
		command = "INSERT INTO TransRecord (Invoice, Confirmation, ResponseCode) VALUES ( '" + str(entry['invoice']) + "', '" + str(entry['confirmation_code']) + "', '" + str(entry['response_code']) + "')" 
		self.conn.execute_non_query(command)    #execute the command above - inserting values into transrecord - invoice, confirmation code, and responsecode
		
		command = "INSERT INTO app_commercialtransaction (created, FirstName, LastName, MiddleIntial, Address, City, State, ZipCode, Invoice, Confirmations, AuthType, PrimaryAmount, CardNumber, ExpDate, CVV2, ResponseCode, AVS) VALUES ( '" + datetime.today().strftime("%Y-%m-%d %H:%M:%S") + "', '" + str(trans_row_entry[0]['FirstName']) + "', '" + str(trans_row_entry[0]['LastName']) + "', '" + str(trans_row_entry[0]['MiddleIntial']) + "', '" + str(trans_row_entry[0]['Address']) + "', '" + str(trans_row_entry[0]['City']) + "', '" + str(trans_row_entry[0]['State']) + "', '" + str(trans_row_entry[0]['ZipCode']) + "', '" + str(entry['invoice']) + "', '" + str(entry['confirmation_code']) + "', '" + str(trans_row_entry[0]['AuthType']) + "', '" + str(trans_row_entry[0]['PrimaryAmount']) + "', '" + str(trans_row_entry[0]['CardNumber']) + "', '" + str(trans_row_entry[0]['ExpDate']) + "', '" + str(trans_row_entry[0]['CVV2']) + "', '" + str(entry['ResponseCode']) + "', '" + str(trans_row_entry[0]['AVS']) + "')"
        self.conn.execute_non_query(command)
		
	#merchantStream(...) creates fake data and adds to merchant for the specific id parameter
	def merchantStream(self, id, name):
		self.conn.execute_query("Select * from Merchants where ID = '" + id + "'")      #find the merchant from the database that matches the specified id parameter
		if not [l for l in self.conn]:
			fake = Factory.create()     #create fake data
			address = "'"
			while "'" in address:
				address = fake.address()
			address = address[:address.index('\n')] + address[address.index('\n') + 1:]     #all characters of address except newline plus an extra space
			contact = "'"
			while "'" in contact:
				contact = "Name: " + str(fake.name()) + " Phone Number: " + str(fake.phone_number()) + " Email: " + str(fake.email())   #generate a fake name, number, and email
			command = "INSERT INTO Merchants (ID, Name, Address, Transactions, Approved, Denied, Balance, ContactInfo) VALUES ( " + id + ", '" + name + "', '" + address + "', 0, 0, 0, 0.0, '" +  contact + "')"       #add the values to merchants
			self.conn.execute_non_query(command)    #execute the command

	#financeStream(...) creates fake data and adds to finance for the specific id parameter		
	def financeStream(self, id, name):
		self.conn.execute_query("Select * from Finance where ID = '" + id + "'")    #find the entry in finance from the database that matches the specified id parameter
		if not [l for l in self.conn]:
			fake = Factory.create()     #create fake data
			address = "'"
			while "'" in address:
				address = fake.address()
			address = address[:address.index('\n')] + address[address.index('\n') + 1:]     #all characters of address except newline plus an extra space
			contact = "'"
			while "'" in contact:
				contact = "Name: " + str(fake.name()) + " Phone Number: " + str(fake.phone_number()) + " Email: " + str(fake.email())   #generate fake name, number, and email
			command = "INSERT INTO Finance (ID, Name, Address, Transactions, Approved, Denied, Balance, ContactInfo) VALUES ( " + id + ", '" + name + "', '" + address + "', 0, 0, 0, 0.0, '" +  contact + "')"         #add the values to finance
			self.conn.execute_non_query(command)    #execute the command

    #transStream(self, entry) executes a db command to insert data into the transactions table
	def transStream(self, entry):
		command = "INSERT INTO Transactions (FirstName, LastName, MiddleIntial, Address, City, State, ZipCode, CardNumber, ExpDate, CVV2, Invoice, AVS, AuthType, PrimaryAmount, SecondaryAmount) VALUES ( '" \
			+ entry["firstname"] + "', '" + entry["lastname"] + "', '" +  entry["middleintial"] + "', '" +  entry["address"] + "', '" +  entry["city"] + "', '" +  entry["state"] + "', '" +  entry["zipcode"] + "', '" \
			+  entry["cardnumber"] + "', '" +  entry["expdate"] + "', '" +  entry["cvv2"] + "', '" +  entry["invoice"] + "', '" +  entry["avs"] + "', '" +  entry["authtype"] + "', '" +  entry["primaryamount"] \
			+ "', '" +  entry["secondaryadmount"] + "')" 
		self.conn.execute_non_query(command)    #execute the command
		
	#createTables(self) creates the tables that have not been created yet	
	def createTables(self):
		table_list = ['Merchants','TransRecord','Transactions', 'Finance']      #4 tables necessary
		self.conn.execute_query('SELECT * FROM INFORMATION_SCHEMA.tables')      #find what tables currently exist in the schema
		
		tables = [str(l['TABLE_NAME']) for l in self.conn]      #get the results of the schema query in tables
		for l in set(table_list) ^ set(tables) & set(table_list):   #if not found in tables and found in table_list
			self.conn.execute_non_query("CREATE TABLE " + l + " " + self.getTableDef(l))    #create the table specified in table_list with the specific table's variables, found in getTableDef
		for i in set(tables) & set(table_list):     #for all tables in both tables and table_list
				self.checkTable(i)      #check whether the table was successfully created

	#getTableDef(self, name) returns the specific table's variables
	def getTableDef(self, name):
		if name == 'TransRecord':
			return "(Invoice varchar(30), Confirmation varchar(30), ResponseCode varchar(3))"
		elif name == 'Merchants':
			return "(ID varchar(10), Name varchar(30),  Address varchar(255), Transactions int, Approved int, Denied int, Balance money, ContactInfo varchar(255))"
		elif name == "Transactions":
			return "(FirstName varchar(15), LastName varchar(15), MiddleIntial varchar(3), Address varchar(50), City varchar(30), State varchar(3), ZipCode varchar(15), CardNumber varchar(16), ExpDate varchar(5), CVV2 varchar(4), Invoice varchar(30), AVS varchar(5), AuthType varchar(5), PrimaryAmount smallmoney, SecondaryAmount smallmoney)"
		elif name == "Finance":
			return "(ID varchar(10), Name varchar(30),  Address varchar(255), Transactions int, Approved int, Denied int, Balance money, ContactInfo varchar(255))"

    #checkTable(self, name) checks to make sure the specific table has the correct variables
    #   if it is missing a variable, add it to the table
	def checkTable(self, name):
		trans = {'Invoice' : 'Invoice varchar(30)', 'Confirmation' : 'Confirmation varchar(30)', 'ResponseCode' : 'ResponseCode varchar(3)'}
		merch = { 'ID' : 'ID varchar(10)', 'Name' : 'Name varchar(30)',  'Address' : 'Address varchar(255)', 'Transactions' : 'Transactions int', 'Approved' : 'Approved int', 'Denied' : 'Denied int', 'Balance' : 'Balance money', 'ContactInfo' : 'ContactInfo varchar(255)'}
		request = { 'FirstName' : 'FirstName varchar(15)', 'LastName' : 'LastName varchar(15)', 'MiddleIntial' : 'MiddleIntial varchar(3)', 'Address' : 'Address varchar(50)', 'City' : 'City varchar(50)', 'State' : 'State varchar(15)', 'ZipCode' : 'ZipCode varchar(10)', 'CardNumber' : 'CardNumber varchar(16)', 'ExpDate' : 'ExpDate varchar(5)', 'CVV2' : 'CVV2 varchar(4)', 'Invoice' : 'Invoice varchar(30)', 'AVS' : 'AVS varchar(5)', 'AuthType' : 'AuthType varchar(5)', 'PrimaryAmount' : 'PrimaryAmount smallmoney', 'SecondaryAmount' : 'SecondaryAmount smallmoney'}
		finance = { 'ID' : 'ID varchar(10)', 'Name' : 'Name varchar(30)',  'Address' : 'Address varchar(255)', 'Transactions' : 'Transactions int', 'Approved' : 'Approved int', 'Denied' : 'Denied int', 'Balance' : 'Balance money', 'ContactInfo' : 'ContactInfo varchar(255)'}
		self.conn.execute_query("Select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + name + "'")
		columns = [l[3] for l in self.conn]
		command = "ALTER TABLE dbo." + name + " ADD "   #add whatever variables are missing
		if name == 'TransRecord':
			for l in (set(trans.keys()) ^ set(columns)) & set(trans.keys()):
						command = command + trans[l] + ", "
		elif name == 'Merchant':
			for l in (set(merch.keys()) ^ set(columns)) & set(merch.keys()):
						command = command + merch[l] + ", "
		elif name == "Transactions":
			for l in set(request.keys()) ^ set(columns) & set(request.keys()):
						command = command + request[l] + ", "
		elif name == "Financial":
			for l in (set(finance.keys()) ^ set(columns)) & set(finance.keys()):
						command = command + finance[l] + ", "
		if 	command != "ALTER TABLE dbo." + name + " ADD ":     #if the command has variables to add
			self.conn.execute_non_query(command[:-2])       #execute the command for everything but the last two items
		return


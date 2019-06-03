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

import os
import sys
import json
import threading
import time
import merchant
import transaction_server
import card_co
from Sqlserver import Sqlserver
import _mssql

#main.py starts everything up for the transaction server of FinSim
#main.py has two classes - Config and startSim
#Instructions on properly running main.py can be found at the end of the program

#Config class reads in the config file to set up the server, merchants, and card companies for the transaction server.
#3 functions and init: __init__(self, file), create_config(self), getConfig(self, buffer, start, finish), and getNestedConfig(self, buffer, start, finish)
class Config:
    #init simply sets the class's file variable to the filename specified in the supplied parameter "file"
	def __init__ (self, file):
		self.file = file
    
    #create_config(self) reads from the config file, line by line to set values for server, merchants, and card companies
	def create_config(self):
		buffer = [line.strip() for line in self.file if line.strip() != ""]     #gets rid of whitespace in every line that has characters and stores only those lines in buffer
		try:		
			return {"server" : self.getConfig(buffer, buffer.index("Transaction_Server:") + 1, buffer.index("Merchant:")),  #calls getConfig function to parse through the transaction server information
					"merchant" : self.getNestedConfig(buffer, buffer.index("Merchant:") + 1, buffer.index("Card_Companies:")),  #getNestedConfig function to parse through merchant information listed
					"card_co" : self.getNestedConfig(buffer, buffer.index("Card_Companies:") + 1, len(buffer))}     #getNestedConfig function to parse through the card company information listed
		except Exception as e:          #catch any errors trying to parse through the config file
			print "Configuration Error: " +  repr(e)        #print the following along with the specific error
			print "Ensure that your configuration file is properly formated and that the following fields are defined: "
			print "Merchant: "
			print "Card_Companies: "
			print "Server: "
			sys.exit()  #and exit the program because the user incorrectly wrote up the config file

    #getConfig(self, buffer, start, finish) parses through the buffer from the index 'start' until 'finish' and adds them to a config dictionary for easy access later on
    #   The function returns the populated config dictionary after reaching 'finish'
    #   The config dictionary is set up so that the keys - how the dictionary is indexed - is the data field names, and the value is the data value (or values if there were multiple data values)
	def getConfig(self, buffer, start, finish):
		config = {}     #declares a dictionary, called config
		for line in buffer[start:finish]:   #line by line
			i = line.split()    #splits the line by space and the array of substrings is stored in i
			if len(i) > 2:      #if the line had more than 2 substrings after the split
				lane = []       #create an empty array "lane"
				for l in i[1:]:     #store all substrings except for the first one - the first one is usually the variable description, like name or address
					lane.append(l)  
				config[i[0][:-1]] = lane    #add lane to config - key being the name of the data field and value being the data values
			else:                       #the line only had two substrings or less. [FOR ALEX] Recommend changing from else to elif len(i) == 2, because if the config incorrectly had an empty line or only one substring, there would be an array out of bounds exception error
				config[i[0][:-1]] = i[1]    #only store the second substring - key being the name of the data field, and value being the data value
		return config   #return the config

    #getNestedConfig(self, buffer, start, finish) is virtually the same as getConfig but it instead parses a buffer of multiple sub-entries rather than one
    #   The function returns a dictionary of dictionaries, where each sub-dictionary is for each sub-entry in the buffer
    #   For example, the dictionary contains multiple merchants, with a dictionary for each merchant to store their information
	def getNestedConfig(self, buffer, start, finish):
		name = ""
		buffer_config = {}  #declares a dictionary
		for line in buffer[start:finish]:   #goes through buffer line by line, from 'start' to 'finish'
			i = line.split()
			if len(i) == 1:     #if there is only one substring on this line, it is the name of the sub-entry (i.e. name of merchant)
				name = line[:-1]    #store that value
				buffer_config[name] = {}    #declare a sub-dictionary for that merchant name
			elif len(i) == 2 and name != "":    #otherwise, there are 2 substrings on the current line and the name (the first line) has been taken care of already
				buffer_config[name][i[0][:-1]] = i[1]   #key/value pair is stored in the merchant dictionary
			elif len(i) > 2 and name != "":     #otherwise, there are more than 2 substrings and the name has been taken care of already
				lane = []       #create an array to store the data values
				for l in i[1:]:
					lane.append(l)
				buffer_config[name][i[0][:-1]] = lane   #key/value pair is stored in the merchant dictionary
		return buffer_config    #return the dictionary of dictionaries

#startSim class creates different threads of main.py to act as different actors of the simulation.
#1 function and init: __init__(self, config, role, server, name) and run(self)
class startSim(threading.Thread):
    #__init__(self, config, role, server, name) sets up the current thread with the specific role, name, and server
    def __init__(self, config, role, server, name):
		threading.Thread.__init__(self)
		self.config = config
		self.role = role
		self.name = name
		self.server = server

    #run(self) calls a method specific for the role value
    def run(self):
    	if self.role == 0:  #0 = server
    		start_server(self.config)
    	elif self.role == 1:    #1 = merchant
    		start_merchant(self.config['merchant'][self.name], self.server, self.name)
    	elif self.role == 2:    #2 = card company
    		start_card(self.name, self.config["card_co"][self.name], self.server)

#start_server(config) runs the SQL database server
def start_server(config):
	db = False
	if config["server"]["database_Type"] == 'SQLSERVER':    #execute the following code only if the config specified SQLSERVER for the server
		try:
			db = Sqlserver(config["server"]["server-name"], config["server"]["database_Name"], config["server"]["username"], config["server"]["password"])      #create a new SqlServer with parameters - server name, database name, username, and password
			db.createTables()      
		except _mssql.MssqlDatabaseException as e:      #catch MssqlDatabaseException errors
			print "Database Connection Error" + repr(e)     #print the error
			sys.exit(1)                                     #and exit the program
	transaction_server.start(config,db)             #start the transaction server with the server config dictionary and the database value (or just false) as arguments - code is in transaction_server.py

#start_merchant(config, server, name) runs the specified merchant
def start_merchant(config, server, name):   
	time.sleep(3)   #Wait for 3 seconds
	merchant.start(config, server, name)    #start the merchant with the merchant config dictionary, server, and name - code is in merchant.py

#start_card(config, server, name) runs the specific card company
def start_card(config, server, name):
	time.sleep(3)   #Wait for 3 seconds
	card_co.start(config, server, name)     #start the card company with the card config dictionary, server, and name - code is in card_co.py

server = ()
config = {}
validmerch = True
validcard = True
try:
	sys.argv.pop(0)     #remove the main.py name from the list of arguments
	if bool(sum(map(lambda x: x in ['-h','--help','help'], sys.argv))):     #if main.py was called with -h, --help, or 'help'
		raise NameError('help')     #raise an exception
	
	config = Config(open(sys.argv.pop(0))).create_config()      #parse through the config file
	server = (config['server']['connection'][0], int(config['server']['connection'][1]))    #create server tuple from the server sub-dictionary in config

	if 'Merchant' in sys.argv and '-m' in sys.argv:     #raise an exception if main.py was called with both -m and Merchant
		raise NameError('You cannot have multiple instances of merchant use either -m or Merchant')
	if 'Company' in sys.argv and '-c' in sys.argv:      #raise an exception if main.py was called with both -c and Company
		raise NameError('You cannot have multiple instances of company use either -c or Company')
	if 'Server' in sys.argv:        #if main.py was called with Server as an argument
		sys.argv.pop(sys.argv.index('Server'))  
		startSim(config, 0, '', '').start()     #call startSim to run the server (role 0)
	if 'Company' in sys.argv:       #if main.py was called with Company as an argument
		sys.argv.pop(sys.argv.index('Company')) 
		for card in config['card_co']:  #for every card in the card_co dictionary
			startSim(config, 2, server, card).start()   #call startSim to run the card companies
	if "-c" in sys.argv:    #if main.py was called with -c as an argument
		index = sys.argv.index('-c')
		sys.argv.pop(index)
		if "-c" in sys.argv or index == len(sys.argv):  #raise an exception if -c was an argument in running main.py but there were no following arguments
			raise NameError('The -c argument must be the following -c arg1 arg2 arg3')		
		while sys.argv and sys.argv[index] != '-m':
			if not sys.argv[index] in config['card_co']:    #make sure all of the card companies listed are found in the config file
				raise NameError(sys.argv[index] + ' is not in the company section of the configuration file')   #raise exception if not found
			else:		
				startSim(config, 2, server, sys.argv.pop(index)).start()    #call startSim to run the card companies
	if 'Merchant' in sys.argv:      #if main.py was called with Merchant as an argument
		sys.argv.pop(sys.argv.index('Merchant'))
		for merch in config['merchant']:    #for every merchant in the merchant dictionary
			startSim(config, 1, server, merch).start()  #call startSim to run the merchants
	if "-m" in sys.argv:    #if main.py was called with -m as an argument
		index = sys.argv.index('-m')
		sys.argv.pop(index)
		if "-m" in sys.argv or index == len(sys.argv):  #raise an exception if -m was an argument in running main.py bu there were no following arguments
			raise NameError('The -m argument must be the following -m arg1 arg2 arg3')	
		while sys.argv:     #until the last argument
			if not sys.argv[index] in config['merchant']:       #make sure all of the merchants listed are found in the config file
				raise NameError(sys.argv[index] + ' is not in the Merchant section of the configuration file')      #raise exception if not found
			else:		
				startSim(config, 1, server, sys.argv.pop(index)).start()    #call startSim to run the merchants
	if sys.argv:    #if there are still arguments after everything else is done (since each argument handling removes the argument afterwards)
		raise NameError('Invalid Input Error see the following instructions')       #raise an exception for running main.py incorrectly
except Exception as e:      #catch all exceptions to print out the error and how to properly run main.py
	print "***********************************************************************************************"
	if str(e) != 'help':
		print "Error: " + repr(e)
	print "The Traffic Generation Application command arguments are as follows:"
	print "python main.py ~/location/of/config arg1 arg2 etc...."
	print "The first argument must be the location of the configuration file"
	print "The next set of arguments can be any combination of the following: "
	print "Server - Maintains the role as the transaction server"
	print "Merchant - Maintains the role for all Merchants"
	print "Company - Maintains the role for all Companies"
	print "-c [Company_Name] - list any combination of companies defined in the Company section within the configuration file."
	print "-m [Merchant_Name] - list any combination of merchant defined in the Merchant section within the configuration file."
	print "***********************************************************************************************"
	sys.exit(1)
















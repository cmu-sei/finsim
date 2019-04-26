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

import time
from datetime import date
import datetime
import os
import socket
import ssl
import json
import random 
import sys

#Custom exception called ValidCardFound
class ValidCardFound(Exception):
     def __init__(self):
        self.message = "The card number matches the configuration requirements"     #exception message is set

#cardCompany class
#7 functions and init: confirm_code(self), card_ver(self, request, decision), cvvVer(self, request, decision), avsVer(self, request, decision), expVer(self, request, decision), accountVer(self, request, decision), transResults(self, complete, decision), and __init__(self, config, name, trans_count)
class cardCompany:
	def __init__(self, config, name, trans_count):	
		self.trans_count = trans_count
		self.config = config
		self.name = name

	def confirm_code(self):
		return self.config["id"] + "%08d" % self.trans_count + "{:%m%d%Y%M}".format(datetime.datetime.now())


    #card_ver(self, request, decision) verifies the card and then calls cvvVer to verify the cvv number
    #sets decision["card_ver"] to 0 if approved, and 56 if denied
	def card_ver(self, request, decision):
		card_decision = False
		try:
			card_var = self.config['card_Verification']     #the config file for the card_Verification field contains an array of characters/integers
			for index in range(0, len(card_var)):   #go through all entries in card_var

			    if card_var[index] == 'and':        #if 'and' is found
			        while index > len(card_var) and card_var[index + 1].isdigit():      #while the current index is greater than the number of entries in card_var AND the next array entry is a integers
			            if request['cardnumber'][:len(card_var[index + 1])] == card_var[index + 1]:     #if the next integers is found in request
			                raise ValidCardFound    #valid card found
			            index = index + 1           #increment index by 1

			    elif card_var[index] == 'thru':     #if 'thru' is found
			        if card_var[index + 1].isdigit() and card_var[index + 2].isdigit():     #if the next entries are integers
			            minMax = (card_var[index + 1], card_var[index + 2]) if int(card_var[index + 1]) > \     #create tuple with the two integers where the first one is greater than the other
			            	int(card_var[index + 2]) else (card_var[index + 2], card_var[index + 1])
			            
			            if int(minMax[0]) <= int(request['cardnumber'][:len(minMax[0])]) and int(minMax[1]) >= int(request['cardnumber'][:len(minMax[1])]):     #if the greater int is less than or equal to the greater int found in request and the lesser int is greater than or equal to the lesser int found in request
			                raise ValidCardFound    #valid card found

			        else:       #invalid card verification - thru must have 2 integers afterwards
			            raise ValueError("Invalid Card Verification Check your config file for " + request['cardnumber'])

			    elif card_var[index].isdigit():     #if an integer is found
			        if request['cardnumber'][:len(card_var[index])] == card_var[index]:     #if the int matches the int in request
			            raise ValidCardFound    #valid card found
			        index = index + 1       #increment index - move onto the next entry in the array

		except ValidCardFound:          #if the card is determined to be valid, catch the exception
			decision["card_ver"] = 0    #return that the card is approved for this aspect
			return self.cvvVer(request, decision)      #call cvvVer method with the updated decision

		decision["card_ver"] = 56       #if the ValidCardFound exception is never raised and the array has been iterated through, set decision for card_ver to 56 (card is not approved)
		return self.cvvVer(request, decision)   #call cvvVer method with the updated decision

    #cvvVer(self, request, decision) is called by card_ver method
    #Uses a randomly generated number from 0 to 100 to set the decision
    #Calls avsVer method
	def cvvVer(self, request, decision):
		ran = random.randint(0,100)     #random int from 0 to 100
		if self.name == "Visa":         #if Visa
			decision["cvv_ver"] = 'M' if ran > 5 else 'N7'      #decision is 'M' for cvv_ver if the random number is greater than 5. else, decision is 'N7'
		else:                           #else
			decision["cvv_ver"] = 'M' if ran > 5 else 'N'       #decision is 'M' for cvv_ver if the random number is greater than 5. else, decision is 'N'
		return self.avsVer(request, decision)   #call avsVer method with the updated decision

    #avsVer(self, request, decision) is called by cvvVer method
    #Uses a randomly generated number from 0 to 100 to set the decision
	def avsVer(self, request, decision):
		ran = random.randint(0,100)
		if ran > 50:    #if the integer is greater than 50 and less than or equal to 100
			decision["avs_ver"] = 'Y'
		elif ran > 5:   #or if the integer is greater than 5 but less than 51
			decision["avs_ver"] = 'Z'
		elif ran > 2 and self.name == 'Visa':   #or if the integer is 3, 4, or 5 and is a Visa
			decision["avs_ver"] = 'P2'
		elif ran > 2:       #or if the integer is 3, 4 or 5 and is not a Visa
			decision["avs_ver"] = 'N'
		else:   #or if the integer is 0, 1 or 2. 
			decision["avs_ver"] = 'E'
		return self.expVer(request, decision)   #call expVer method with the updated decision

    #expVer(self, request, decision) is called by avsVer method
    #Checks whether the card has expired or not [FOR ALEX] METHOD CHECKS YEAR AND DAY - BUT MOST CREDIT CARDS USE YEAR AND MONTH
	def expVer(self, request, decision):
		today = date.today()        #get today's date
		exp = request["expdate"].split("/")     #get the request date
		if int(exp[1]) > today.year % 2000:     #expiration date year has not passed
			decision["exp_ver"] = 0
		elif int(exp[1]) == today.year % 2000 and today.day > int(exp[0]):      #expiration date has not passed, even though both are in the same year
			decision["exp_ver"] = 0	
		else:                                   #expired
			decision["exp_ver"] = 54
		return self.accountVer(request, decision)       #call accountVer method with the updated decision

    #accountVer(self, request, decision) is called by expVer method
    #Uses a random number to determine decision for the account
	def accountVer(self, request, decision):
		ran = random.randint(0,100)
		if ran > 5:     #if int is greater than 5
			decision["account_var"] = 0     #approved
		else:           #if int is less than or equal to 5
			decision["account_var"] = 51    #declined
		return self.transResults(request, decision)     #call transResults method with the updated decision

    #transResults(self, complete, decision) is called by accountVer
    #goes through the decisions in previous methods to only approve the request
	def transResults(self, complete, decision):
		results = json.loads('{"response_code" : "", "confirmation_code" : "", "invoice" : "", "results" : ""}')
		results["confirmation_code"] = self.confirm_code()
		results["invoice"] = complete["invoice"]
		if decision["card_ver"] > 0:
			results["response_code"] = 56
			results["results"] = 'DENIED'
			return results

		if decision["cvv_ver"] == 'N':
			results["response_code"] = 82
			results["results"] = 'DENIED'
			return results

		if decision["cvv_ver"] == 'N7':
			results["response_code"] = 'N7'
			results["results"] = 'DENIED'
			return results

		if decision["avs_ver"] == 'N':
			results["response_code"] = 'N'
			results["results"] = 'DENIED'
			return results		
		elif decision["avs_ver"] == 'P2':
			results["response_code"] = 'P2'
			results["results"] = 'DENIED'
			return results	
		elif decision["avs_ver"] == 'E':
			results["response_code"] = 'E'
			results["results"] = 'DENIED'
			return results

		if decision["exp_ver"] > 0:
			results["response_code"] = 54
			results["results"] = 'DENIED'
			return results

		if decision["account_var"] > 0:
			results["response_code"] = 51
			results["results"] = 'DENIED'
			return results

		results["response_code"] = 0        #if this is reached, there were no denied decision codes.
		results["results"] = 'APPROVED'     #card is approved
		return results

#start(config, server, name) connects to the server, maintains a log, and reads in requests from the server to verify and determine whether to approve or decline
#continues to handle any requests from the server until there is an error with the socket connection to the server or the server terminates the connection
def start(config, server, name):
	try:        #try to connect to the server
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		ssl_sock = ssl.wrap_socket(s,
		                           ca_certs=config['cert'],
		                           cert_reqs=ssl.CERT_NONE,                         #NOTE THAT THIS MEANS THE CONNECTION IS SUSCEPTIBLE TO MAN IN THE MIDDLE ATTACKS
		                           ssl_version=ssl.PROTOCOL_TLSv1)
		ssl_sock.bind((config["connection"][0], int(config["connection"][1])))
		ssl_sock.connect(server)
	except socket.error as e:       #catch any errors connecting to the server socket
		print "Name: " + name + " Issue: " + str(e)     #print out the error caught
		sys.exit(1)                 #exit the program


	log = open(config["log"], "wb")     #open a log file in the listing specified in the config file
	log.write("************************************************************************************************************************\n")
	log.write("*                                                                                                                      *\n")
	log.write("*                                                                                                                      *\n")

	middle = ""
	today_date = "{:%m%d%Y%M}".format(datetime.datetime.now())
	for x in range(0, (71 - len(name + today_date))/2):
		middle = middle + " "
	if len(name + today_date) % 2 == 0:
		log.write("*" + middle + "The following output is the logged traffic for " + name + " " + today_date + middle +"*\n")
	else:
		log.write("*" + middle + " The following output is the logged traffic for " + name + " " + today_date + middle +"*\n")

	log.write("*                                                                                                                      *\n")
	log.write("*                                                                                                                      *\n")
	log.write("************************************************************************************************************************\n")
	
	index = 1
	while True:
		request = ssl_sock.read()       #accept requests from the server
		if '***end***' in request:      #server request to terminate the connection
			ssl_sock.close()    #terminate server socket connection
			log.close()     #close the logfile
			return      #exit
		request = json.loads(request)
		decision = json.loads('{"card_ver" : "", "cvv_ver" : "", "avs_ver" : "", "exp_ver" : "", "account_var" : "" }')
		results = cardCompany(config, name, index).card_ver(request, decision)      #call first function - card_ver
		try:
			ssl_sock.write(json.dumps(results))     #Send the results of verifying the request back to the server
		except socket.error as e:   #catch any errors with this write back to server
			log.close()     #close the logfile
			sys.exit(1)     #exit the program
		log.write(results["results"] + " **** " + results["confirmation_code"] + " **** " + results["invoice"] + " **** " + str(results["response_code"]) + " **** " + request["primaryamount"] + "\n")     #Log the results in the logfile
		index = index + 1   #increment index by 1





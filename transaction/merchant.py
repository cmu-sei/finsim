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
import socket
import ssl
import random 
import json
import threading
import time
from datetime import date
import datetime
import sys
import random

#dictionary of integers matching responses (i.e. expired credit card or invalid information)
response_codes = {  '0' : 'Approved', '54' : 'Expired Card', '1' : 'Refer to Card Issuer', '55' : 'Incorrect PIN', '2' : 'Refer to Issuer\'s special conditions', 
					'56' : 'No Card Record', '3' : 'Invalid Merchant', '57' : 'Trans. not Permitted to Cardholder', 
					'4' : 'Pick Up Card', '58' : 'Transaction not Permitted to Terminal', '5' : 'Do Not Honor', '59' : 'Suspected Fraud', 
					'6' : 'Error', '60' : 'Card Acceptor Contact Acquirer', '7' : 'Pick Up Card, Special Conditions', '61' : 'Exceeds Withdrawal Amount Limits', 
					'8' : 'Honor with identification', '62' : 'Restricted Card', '9' : 'Request in Progress', '63' : 'Security Violation', 
					'10' : 'Partial Amount Approved', '64' : 'Original Amount Incorrect', '11' : 'VIP Approval', '65' : 'Exceeds Withdrawal Frequency Limit', 
					'12' : 'Invalid Transaction', '66' : 'Card Acceptor Call Acquirer Security', '13' : 'Invalid Amount', '67' : 'Hard Capture - Pick Up Card at ATM', 
					'14' : 'Invalid Card Number', '68' : 'Response Received Too Late', '15' : 'No Such Issuer', '75' : 'Allowable PIN Tries Exceeded', 
					'16' : 'Approved, update track 3', '76' : 'Previous message not found', '17' : 'Customer Cancellation', '77' : 'Data does not match original message', 
					'18' : 'Customer Dispute', '80' : 'Invalid Date', '19' : 'Re-enter Transaction', '81' : 'Cryptographic failure', '20' : 'Invalid Response', 
					'82' : 'Incorrect CVV', '21' : 'No Action Taken (no match)', '83' : 'Unable to verify PIN', '22' : 'Suspected Malfunction', 
					'84' : 'Invalid authorization life cycle', '23' : 'Unacceptable Transaction Fee', '85' : 'No reason to decline', '24' : 'File Update not Supported by Receiver',
					'86' : 'ATM Malfunction', '25' : 'Unable to Locate Record on File', '87' : 'No Envelope Inserted', '26' : 'Duplicate File Update Record', 
					'88' : 'Unable to Dispense', '27' : 'File Update Field Edit Error', '89' : 'Administration Error', '28' : 'File Update File Locked Out', 
					'90' : 'Cut-off in Progress', '29' : 'File Update not Successful', '91' : 'Issuer or Switch is Inoperative', '30' : 'Format Error', 
					'92' : 'Financial Institution Not Found', '31' : 'Bank not Supported by Switch', '93' : 'Trans Cannot be Completed', '32' : 'Completed Partially', 
					'94' : 'Duplicate Transmission', '33' : 'Expired Card - Pick Up', '95' : 'Reconcile Error', '34' : 'Suspected Fraud - Pick Up', '96' : 'System Malfunction', 
					'35' : 'Contact Acquirer - Pick Up', '97' : 'Reconciliation Totals Reset', '36' : 'Restricted Card - Pick Up', '98' : 'MAC Error', 
					'37' : 'Call Acquirer Security - Pick Up', '99' : 'Reserved for National Use', '38' : 'Allowable PIN Tries Exceeded', 'N0' : 'Force STIP (VISA)', 
					'39' : 'No CREDIT Account', 'N3' : 'Cash Service Not Available (VISA)', '40' : 'Requested Function not Supported', 
					'N4' : 'Cash request exceeds issuer limit (VISA)', '41' : 'Lost Card - Pick Up', 'N7' : 'Decline for CVV2 failure (VISA)', '42' : 'No Universal Amount', 
					'P2' : 'Invalid biller information (VISA)', '43' : 'Stolen Card - Pick Up', 'P5' : 'PIN Change Unblock Declined (VISA)', 
					'44' : 'No Investment Account', 'P6' : 'Unsafe PIN (VISA)', '51' : 'Insufficient Funds', 'XA' : 'Forward to issuer', '52' : 'No Cheque Account', 
					'XD' : 'Forward to issuer', '53' : 'No Savings Account', 'N' : 'AVS No Match', 'E' : 'AVS data is invalid'}

#merchant class
#run and init methods: run(self) connects the current merchant to the server, while __init__(self, config, server, role, name) sets up the current merchant variables
class merchant (threading.Thread):
		def __init__(self, config, server, role, name):
			threading.Thread.__init__(self)
			self.config = config
			self.server = server
			self.role = role
			self.name = name

		def run(self):
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			ssl_sock = ssl.wrap_socket(s,
                           ca_certs=self.config["cert"],
                           cert_reqs=ssl.CERT_NONE,                     #NOTE THAT THIS MEANS THE CONNECTION IS SUSCEPTIBLE TO MAN IN THE MIDDLE ATTACKS
                           ssl_version=ssl.PROTOCOL_TLSv1)

			if self.config['connection'][1].isdigit() and self.config['connection'][1].isdigit():   #[FOR ALEX] BOTH REFERENCE the same thing
				connected = False
				if self.role == "Customer_In":      #either customer_in, which will call traffic_out
					while not connected:
						try:        #try to connect to the server
							ssl_sock.bind((self.config["connection"][0], int(self.config["connection"][1])))
							ssl_sock.connect(self.server)
							connected = True
						except socket.error as e:       #catch any errors with trying to connect to the server
							print "Name: " + self.name + " In Issue: " + repr(e)
							sys.exit(1)
					packets = int(self.config['packet']) if self.config['packet'].isdigit() else -1     #set packets/flow values if they are found in the config file
					flow = float(self.config['flow']) if self.config['flow'].isdigit() else -1          #   otherwise return -1
					traffic_out(ssl_sock, self.config['users'], self.config["id"], packets, flow)       #call traffic_out method
				elif self.role == "Customer_Out":   #or customer_out, which will call traffic_in
					while not connected:
						try:        #try to connect to the server
							ssl_sock.bind((self.config["connection"][0], int(self.config["connection"][2])))
							ssl_sock.connect(self.server)
							connected = True
						except socket.error as e:       #catch any errors with trying to connect to the server
							print "Name: " + self.name + " Out Issue: " + repr(e)
							sys.exit(1)
					traffic_in(ssl_sock, self.config['log'], self.name)         #call traffic_in method
			else:
				ValueError("Configuration is Invalid Check Config File for Merchant connection")


#traffic_in(connstream, log_file, name) logs the traffic that comes in
def traffic_in(connstream, log_file, name):
	log = open(log_file, "wb")		
	log.write("************************************************************************************************************************\n")
	log.write("*                                                                                                                      *\n")
	log.write("*                                                                                                                      *\n")

	middle = ""
	today_date = "{:%m%d%Y%M}".format(datetime.datetime.now())
	for x in range(0, (62 - len(today_date) - len(name))/2):
		middle = middle + " "
	if len(today_date) % 2 == 0:
		log.write("*" + middle + "The following output is the logged traffic for " + name +today_date + middle +"*\n")
	else:
		log.write("*" + middle + " The following output is the logged traffic for "  + name + today_date + middle +"*\n")

	log.write("*                                                                                                                      *\n")
	log.write("*                                                                                                                      *\n")
	log.write("************************************************************************************************************************\n")

	while True:
		try:    #keep reading in traffic until an error occurs
			results = json.loads(connstream.read())
		except Exception as e:
			connstream.close()
			log.close()
			return
		log.write(results["results"] + " **** " + str(results["response_code"]) + " **** " + response_codes[str(results["response_code"])] + " **** " + results["confirmation_code"] + " **** " + results["invoice"] + "\n")
		#write down the results into the log

#traffic_out(connstream, users, merch_id, packets, flow) adds the user list to traffic_list, then randomly picks a user to send a randomized amount of money until packets equal 0
def traffic_out(connstream, users, merch_id, packets, flow):
	traffic = open(users, "r")
	traffic_list = []
	for line in traffic:
		if line != "\n":
			traffic_list.append(json.loads(line))   #add each line in the user list to traffic_list
	traffic.close()
	index = 1
	while packets > 0:      #stop loop when packets = 0
		entry = traffic_list[random.randint(0,len(traffic_list) - 1)]   #pick a random user from the traffic_list
		entry["invoice"] = merch_id + "%08d" % index + "{:%m%d%Y%M}".format(datetime.datetime.now())    #invoice - merchant id, index, and current date
		entry["primaryamount"] = "%.2f" % random.uniform(1,1000)    #random amount of money
		entry["secondaryamount"] = "00"     #secondary amount
		if random.randint(1, 3) % 2 == 0:   #2 out of 3 times, the random transaction is a deposit (plus). else, withdrawal (minus)
		    entry["authtype"] = "Minus"
		else:
		    entry["authtype"] = "Plus"
		index = index + 1       #increment index by one - used for invoice counting
		if flow > 0:        #how long to wait until writing the entry/
			time.sleep(random.uniform(10, flow))
		connstream.write(json.dumps(entry))
		packets = packets - 1   #decrement packets by 1 each iteration of the loop

	connstream.write(json.dumps({'***end***' : 'Complete'}))    #indicate completion
	traffic.close()
	connstream.close()



#start(config, server, name) simply calls start methods for two merchants, customer_in and customer_out
def start(config, server, name):
	merchant(config, server, "Customer_In", name).start()
	merchant(config, server, "Customer_Out", name).start()















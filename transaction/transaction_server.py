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

from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler
import threading
import ssl
import json
import Queue
import sys
from Sqlserver import Sqlserver

queue_list = {}
DBQ = Queue.Queue()
lock = threading.Lock()
DBQLock = ''
logged_in = [[],[],[]]
STOP = 0
IN = 0
OUT = 1
CARD = 2


#MySSL_TCPServer class accepts and obtains requests from merchants/card companies
#get_request and init: get_request(self) accepts socket connections from clients and tries to determine if it is a merchant/card company that is listed in the config file.
#                           if found, get the cert and key and set-up the connstream
#                       __init__(...) initializes the ssl/config/database and TCP server information
class MySSL_TCPServer(TCPServer):
	def __init__(self, config, db, RequestHandlerClass, ssl_version=ssl.PROTOCOL_TLSv1,bind_and_activate=True):
		self.ssl_version = ssl_version
		self.config = config
		self.db = db
		print "Ready for transfer....."
		TCPServer.__init__(self,(config['server']['connection'][0], int(config['server']['connection'][1])), RequestHandlerClass,bind_and_activate)

	def get_request(self):
		newsocket, fromaddr = self.socket.accept()      #accepts a connection from the client
		cert = ""
		key = ""
		found = False
		for merch in self.config['merchant']:       #first tries to find if the client address matches one of the listed addresses of the merchants in the config file
			if self.config['merchant'][merch]['connection'][0] == fromaddr[0] and int(self.config['merchant'][merch]['connection'][1]) == fromaddr[1]:      #see if the ip address and first port number matches
				cert = self.config['merchant'][merch]['cert']
				key = self.config['merchant'][merch]['key']
				found = True
				break
			elif self.config['merchant'][merch]['connection'][0] == fromaddr[0] and int(self.config['merchant'][merch]['connection'][2]) == fromaddr[1]:    #otherwise see if the ip address and second port number matches
				cert = self.config['merchant'][merch]['cert']
				key = self.config['merchant'][merch]['key']
				found = True
				break
		if not found:       #otherwise, the client could not be matched to one of the merchants
			for card in self.config['card_co']:     #next, try to find if the client matches one of the listed addresses of the card companies in the config file
				if self.config['card_co'][card]['connection'][0] == fromaddr[0] and int(self.config['card_co'][card]['connection'][1]) == fromaddr[1]:      #see if the ip address and port number matches
					cert = self.config['card_co'][card]['cert']
					key = self.config['card_co'][card]['key']
					break

		if cert == "" or key == "":     #if any matches were found, cert and key were set to the values found in config for the merchant/card company
			raise ValueError("Unable to verify CERT/KEY Check your config file")    #but if they were empty in the config file, an exception is raised

		connstream = ssl.wrap_socket(newsocket,     #otherwise, set-up the connstream with cert and key from the config file
									server_side = True,
									certfile = cert,
									keyfile = key,
									ssl_version = self.ssl_version)
		return connstream, fromaddr     #return both connstream and fromaddr


class MySSL_ThreadingTCPServer(ThreadingMixIn, MySSL_TCPServer): pass       #pass acts as a placeholder so that an empty class does not cause errors OR is derived
    #[FOR ALEX] May consider removing this if it isn't being used elsewhere?

#handler class has one method - handle(self) method, which queues the merchant/card company for the database and calls deal_with_customer_in/out or deal_with_card
class handler(StreamRequestHandler):
	def handle(self): 
		try:
			db = self.server.db
			config = self.server.config
			fromaddr = self.connection.getpeername()
			found = False
			for merch in config['merchant']:        #try to match the client to a merchant listed in the config file
				if config['merchant'][merch]['connection'][0] == fromaddr[0] and int(config['merchant'][merch]['connection'][1]) == fromaddr[1]:    #ip address and first port number matched
					logged_in[IN].append(merch)     #update logged_in for the in list for the client merchant
					setQueue(merch)     #add to queue
					if db:
						DBQ.put({'type' : 'Merchant', 'id' : config['merchant'][merch]['id'], 'name' : merch})      #add to db queue if db exists/is running
					deal_with_customer_in(self.connection, config['card_co'], merch, db)        #call deal_with_customer_in method
					found = True
					break
				elif config['merchant'][merch]['connection'][0] == fromaddr[0] and int(config['merchant'][merch]['connection'][2]) == fromaddr[1]:  #ip address and second port number matched
					logged_in[OUT].append(merch)    #update logged_in for the out list for the client merchant
					deal_with_customer_out(self.connection, self.server, merch, db)     #call deal_with_customer_out method
					found = True
					break
			if not found:   #gone through list of merchants, no match found
				for card in config['card_co']:      #next, try to match client with card company listed in the config file
					if config['card_co'][card]['connection'][0] == fromaddr[0] and int(config['card_co'][card]['connection'][1]) == fromaddr[1]:    #ip address and port number matched
						logged_in[CARD].append(card)    #update logged_in for the card list for the client card
						setQueue(card)  #add to queue
						if db:
							DBQ.put({'type' : 'Finance', 'id' : config['card_co'][card]['id'], 'name' : card})  #add to db queue if db exists/is running
						deal_with_card(self.connection, card)   #call deal_with_card method
						break

		except Exception as e:      #catch any exceptions raised
			print "Client Server Issue: " + repr(e)      #print the error, shutdown the server and exit the program     #[FOR ALEX] Spelling error found and fixed
			self.server.shutdown()
			self.server.server_close()
			sys.exit(1)

class ValidCardFound(Exception):    #custom exception used when a valid card is found
	 def __init__(self):
		self.message = "The card number matches the configuration requirements"


#deal_with_customer_in(connstream, config, name, db) reads in data from the client until there are no more reads
def deal_with_customer_in(connstream, config, name, db):
	data = json.loads(connstream.read())
	num = 0
	while '***end***' not in data:
		num = num + 1
		try:
			for card in config:
				card_var = config[card]['card_Verification']        #read in the card verification section of the config file
				for index in range(0, len(card_var)):
					if card_var[index] == 'and':        #if 'and' is found
						index = index + 1
						while index < len(card_var) and card_var[index].isdigit():  #if the second entry is an integer
							if data['cardnumber'][:len(card_var[index])] == card_var[index]:    #if the int is found in the data sent by client
								queue_list[card].put({ name: data})     #queue the data for the card
								raise ValidCardFound        #card is valid
							index = index + 1   #continue until end of card_var

					elif card_var[index] == 'thru':     #if 'thru' is found
						if card_var[index + 1].isdigit() and card_var[index + 2].isdigit():     #if next two entries are integers
							num1 = int(data['cardnumber'][:len(card_var[index + 1])])       #save the corresponding integers in data as num1 and num2
							num2 = int(data['cardnumber'][:len(card_var[index + 1])])       #[FOR ALEX] Doesn't make sense to store the same value in two separate values, maybe meant to make num2 [index+2], not [index+1]?
							if num1 in range(*sorted((int(card_var[index + 1]), int(card_var[index + 2])))):    #if num1 is found in card_var (config)
								queue_list[card].put({ name: data})     #queue the data in card list
								raise ValidCardFound	                #card is valid
							elif num2 in range(*sorted((int(card_var[index + 1]), int(card_var[index + 2])))):  #if num2 is found in card_var (config)
								queue_list[card].put({ name: data})     #queue the data in card list
								raise ValidCardFound	                #card is valid
						else:   #otherwise, invalid card/config
							raise ValueError("Invalid Card Verification Check your config file for " + card)

					elif card_var[index].isdigit():     #if integer is found
						if data['cardnumber'][:len(card_var[index])] == card_var[index]:    #if integer matches what is found in data
							queue_list[card].put({ name : data})    #queue the data in card list
							raise ValidCardFound                    #card is valid
		except ValidCardFound:      #catch any ValidCardFound exceptions
			if db:
				DBQ.put({'type' : 'Transactions', 'data' : data})       #add to DB queue if db exists/is running
			data = json.loads(connstream.read())    #read in the next data
		else:
			print "Invalid Card Error " + data['cardnumber']            #otherwise, invalid card
			data = json.loads(connstream.read())    #read in the next data
	logged_in[IN].pop()     #at this point, all requests/data from the client have been serviced - ***end*** received as data from client. remove client from list of in clients
	global STOP     #end the program
	STOP = 1
	return


#deal_with_customer_out(connstream, server, name, db) writes out data to the client until there are no more reads
def deal_with_customer_out(connstream, server, name, db):
	complete = 0
	global lock
	global DBQLock
	if db:      #if db exists/is running
		if DBQLock == '':   
			lock.acquire()      #acquire the db queue lock in order to have access to the db queue
			if DBQLock == '':
				DBQLock = name
			lock.release

	while True:
		while name in queue_list and not queue_list[name].empty():      #if "name" is in queue and has data sets
			data = queue_list[name].get()       #get data
			connstream.write(json.dumps(data))      #write the data out
			if db:
				DBQ.put({'type' : 'Results', 'data' : data})    #add to db queue
				if DBQLock == name:     #if they have access to db queue
					while not DBQ.empty():      #until the db queue is empty
						dbWrite(DBQ.get(), db, name)    #write the entry in db queue to the db
						if name in queue_list and not queue_list[name].empty():
							data = queue_list[name].get()       #get next data
							connstream.write(json.dumps(data))      #write the data out
							DBQ.put({'type' : 'Results', 'data' : data})    #add to db queue

		if not logged_in[CARD] and not logged_in[IN]:       #if neither card or in lists
			connstream.close()
			logged_in[OUT].pop()    #remove card from out list
			if not logged_in[OUT] and STOP == 1:    #end the program
				server.shutdown()
				server.server_close()
			return
			
#deal_with_card(connstream, name) 
def deal_with_card(connstream, name):
	while True:
		if not queue_list[name].empty():        #data sets for card in queue_list is not empty
			data = queue_list[name].get()       #get the next set of data
			merchant = data.keys()
			connstream.write(json.dumps(data[merchant[0]]))     #write the data out
			queue_list[merchant[0]].put(json.loads(connstream.read()))      #add to queue list for the card 
		elif not logged_in[IN] and STOP == 1:   #else if queue for the card is empty - and not logged_in plus stop == 1
			connstream.write(json.dumps({'***end***' : 'Complete'}))        #end the writes
			connstream.close()      #close connection
			logged_in[CARD].pop()   #remove card from list
			return


def setQueue(name):
	queue_list[name] = Queue.Queue()    #create a new queue for the client

#dbWrite(request, db, name) sends a request to a different stream based on what type of request is being sent
def dbWrite(request, db, name):
	if request['type'] == 'Merchant':           #merchant
		db.merchantStream(request['id'],  request['name'])
	elif request['type'] == 'Finance':          #finance
		db.financeStream(request['id'],  request['name'])
	elif request['type'] == 'Transactions':     #transactions
		db.transStream(request['data'])
	elif request['type'] == 'Results':          #results
		db.resultsStream(request['data'])
	return
	
def start(config, db):
	try:
		MySSL_ThreadingTCPServer(config,db,handler).serve_forever()     #[FOR ALEX] MySSL_ThreadingTCPServer has not been implemented or is derived 
	except Exception as e:
		print "Server Issue: " + repr(e)    #catch any exceptions and print out the error
		sys.exit(1)












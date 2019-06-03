#!/usr/bin/python3

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

import requests

ccUrl = "http://localhost:5000/"

baseUrl  = "http://localhost:10000/"
baseUrl2 = "http://localhost:10100/"

try:
  input( "Press enter to test ccProcessor processing a transaction..." )
except SyntaxError:
  pass
print( "Testing processTransaction..." )

loginForm = {"username":'target', "password":'tartans@1'}
token = requests.post( ccUrl + "login", json = loginForm ).json()
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
transactionResponse = requests.post( ccUrl + "processTransaction", json = { "amount": 1000.00, 'card_num': '0001222233334879' }, headers = header )
print( transactionResponse.text )
transactionResponse = requests.post( ccUrl + "processTransaction", json = { "amount": 1001.00, 'card_num': '0012222233334879' }, headers = header )
print( transactionResponse.text )

loginForm = {"username":'amazon', "password":'tartans@1'}
token = requests.post( ccUrl + "login", json = loginForm ).json()
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }

transactionResponse = requests.post( ccUrl + "processTransaction", json = { "amount": 2000.00, 'card_num': '0001222233334880' }, headers = header )
print( transactionResponse.text )

transactionResponse = requests.post( ccUrl + "processTransaction", json = { "amount": 2001.00, 'card_num': '0011222233334880' }, headers = header )
print( transactionResponse.text )



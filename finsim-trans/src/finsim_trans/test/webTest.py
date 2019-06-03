#!/usr/bin/python3

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

import requests

baseUrl  = "http://localhost:10000/"
user = 'jjones'
password = 'tartans@1'

loginForm = {"username":user,"password":password}
token = requests.post( baseUrl + "login", json = loginForm ).json()
print( token['access_token'] )
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }

'''
accountsResponse = requests.get( baseUrl + 'web/accounts', headers = header )
print( "Response Text: " + accountsResponse.text )


#list of transactions from one of jjones's accounts
transResponse = requests.get( baseUrl + 'web/transactions', json = { "number": "0001222233334879" }, headers = header )
print( "Response Text: " + transResponse.text )
'''
'''
#test obtaining specific account info from one of jjones's accounts
acctResponse = requests.get( baseUrl + 'web/account', json = { "number": "0001222233334879" }, headers = header )
print( "Response Text: " + acctResponse.text )
'''

#test flagging a transaction as fraud
flagResponse = requests.post( baseUrl + 'flag/fraud', json = { 'account':'0001222233334879', 'transaction': '1' }, headers = header )
print( "Response Text: " + flagResponse.text )

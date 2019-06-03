#!/usr/bin/python3

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

import requests

ccUrl = "http://localhost:5000/"
transUrl  = "http://localhost:10000/"
trans2Url = "http://localhost:10100/"

ccProcessorReg = (
                  ( 'target', 'tartans@1', '0001222233334567' ),
                  ( 'amazon', 'tartans@1', '0011112223334446' )
                )

userReg  = (
            ( 'jjones', 'tartans@1', 'USER', [ '0001222233334879', '0001222233334880', '0001222233334881' ] ),
            ( 'vgs', 'tartans@1', 'USER', [ '0005111122223333' ] ),
            ( 'pnc_000', 'tartans@1', 'BANK', [] ),
            ( 'cc_000', 'tartans@1', 'CC'  , [] ),
            ( 'bnk_001', 'tartans', 'BANK'  , [] ),
            ( 'target', 'tartans@1', 'USER', [ '0001222233334567' ] )
          )

userReg2 = (
            ( 'jjones2', 'tartans@1', 'USER', [ '0012222233334879', '0011222233334880', '0011222233334881' ] ),
            ( 'vgs2', 'tartans@1', 'USER', [ '0015111122223333' ] ),
            ( 'pnc_001', 'tartans@1', 'BANK', [] ),
            ( 'cc_000', 'tartans@1', 'CC'  , [] ),
            ( 'bnk_000', 'tartans', 'BANK'  , [] ),
            ( 'amazon', 'tartans@1', 'USER', [ '0011112223334446' ] )
          )

print( "Creating users..." )

for user, password, role, accountNumbers in userReg:
    userReg = {"username":user,"password":password,"role": role }
    regMessage = requests.post( transUrl + "registration", json = userReg  )
    print( "Reg Message: " + regMessage.text )
    loginForm = {"username":user,"password":password}
    token = requests.post( transUrl + "login", json = loginForm ).json()
    print( token['access_token'] )
    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
    for accountNum in accountNumbers:
        print( accountNum )
        accountReg = { "number": "{}".format( accountNum ) }
        accountResponse = requests.post( transUrl + 'account/create', json = accountReg, headers = header )
        print( "Response Text: " + accountResponse.text )
    #print( token )
    print( requests.get( transUrl + "secret", headers = header ).json()['answer'] )

for user, password, role, accountNumbers in userReg2:
    userReg = {"username":user,"password":password,"role": role }
    regMessage = requests.post( trans2Url + "registration", json = userReg  )
    print( "Reg Message: " + regMessage.text )
    loginForm = {"username":user,"password":password}
    token = requests.post( trans2Url + "login", json = loginForm ).json()
    print( token['access_token'] )
    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
    for accountNum in accountNumbers:
        print( accountNum )
        accountReg = { "number": "{}".format( accountNum ) }
        accountResponse = requests.post( trans2Url + 'account/create', json = accountReg, headers = header )
        print( "Response Text: " + accountResponse.text )
    #print( token )
    print( requests.get( trans2Url + "secret", headers = header ).json()['answer'] )

for user, password, bank_acct in ccProcessorReg:
    userReg = {"username":user, "password":password, "bank_acct": bank_acct}
    regMessage = requests.post( ccUrl + "registration", json = userReg )
    print( "Reg Message: " + regMessage.text )
    loginForm = {"username":user, "password":password}
    token = requests.post( ccUrl + "login", json = loginForm ).json()
    print( token['access_token'] )
    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }

try:
  input( "Press enter to continue to deposit tests..." )
except SyntaxError:
  pass

print( "Testing deposits for accounts for first finsim-trans..." )

loginForm = {"username":'pnc_000',"password":'tartans@1'}
token = requests.post( transUrl + "login", json = loginForm ).json()
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
depositResponse = requests.post( transUrl + "bank/deposit", json = { 'amount': 10000.00, 'account': '0001222233334879', 'counterpart_name': 'pnc_000', fraud_flag = FraudType.NONE }, headers = header )
print( depositResponse.text )
depositResponse = requests.post( transUrl + "bank/deposit", json = { 'amount': 10001.00, 'account': '0001222233334880', 'counterpart_name': 'pnc_000', fraud_flag = FraudType.NONE }, headers = header )
print( depositResponse.text )

loginForm = {"username":'pnc_001',"password":'tartans@1'}
token = requests.post( trans2Url + "login", json = loginForm ).json()
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
depositResponse = requests.post( trans2Url + "bank/deposit", json = { 'amount': 10100.00, 'account': '0012222233334879', 'counterpart_name': 'pnc_001', 'fraud_flag': 0 }, headers = header )
print( depositResponse.text )
depositResponse = requests.post( trans2Url + "bank/deposit", json = { 'amount': 10101.00, 'account': '0011222233334880', 'counterpart_name': 'pnc_001', 'fraud_flag': 0 }, headers = header )
print( depositResponse.text )


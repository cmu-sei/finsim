#!/usr/bin/python3

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

import requests

ccUrl = "http://localhost:5000/"
'''
baseUrl  = "http://localhost:10000/"
#baseUrl2 = "http://localhost:10100/"

userReg  = (
            ( 'jjones', 'tartans@1', 'USER', [ '0001222233334879', '0001222233334880', '0001222233334881' ] ),
            ( 'vgs', 'tartans@1', 'USER', [ '000511112222' ] ),
            ( 'pnc_000', 'tartans@1', 'BANK', [] ),
            ( 'cc_000', 'tartans@1', 'CC'  , [] ),
            ( 'bnk_001', 'tartans', 'BANK'  , [] ),
            ( 'target', 'tartans@1', 'USER', [ '0001222233334567' ] )
          )

userReg2 = (
            ( 'jjones2', 'tartans@1', 'USER', [ '0012222233334879', '0011222233334880', '0011222233334881' ] ),
            ( 'vgs2', 'tartans@1', 'USER', [ '001511112222' ] ),
            ( 'pnc_001', 'tartans@1', 'BANK', [] ),
            ( 'cc_001', 'tartans@1', 'CC'  , [] ),
            ( 'bnk_000', 'tartans', 'BANK'  , [] ),
          )
'''
ccProcessorReg = (
                  ( 'target', 'tartans@1', '0001222233334567' ),
                  ( 'amazon', 'tartans@1', '0001112223334446' )
                )

print( "Creating users..." )
'''
for user, password, role, accountNumbers in userReg:
    userReg = {"username":user,"password":password,"role": role }
    regMessage = requests.post( baseUrl + "registration", json = userReg  )
    print( "Reg Message: " + regMessage.text )
    loginForm = {"username":user,"password":password}
    token = requests.post( baseUrl + "login", json = loginForm ).json()
    print( token['access_token'] )
    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
    for accountNum in accountNumbers:
        print( accountNum )
        accountReg = { "number": "{}".format( accountNum ) }
        accountResponse = requests.post( baseUrl + 'account/create', json = accountReg, headers = header )
        print( "Response Text: " + accountResponse.text )
    #print( token )
    print( requests.get( baseUrl + "secret", headers = header ).json()['answer'] )

for user, password, role, accountNumbers in userReg2:
    userReg = {"username":user,"password":password,"role": role }
    regMessage = requests.post( baseUrl2 + "registration", json = userReg  )
    print( "Reg Message: " + regMessage.text )
    loginForm = {"username":user,"password":password}
    token = requests.post( baseUrl2 + "login", json = loginForm ).json()
    print( token['access_token'] )
    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
    for accountNum in accountNumbers:
        print( accountNum )
        accountReg = { "number": "{}".format( accountNum ) }
        accountResponse = requests.post( baseUrl2 + 'account/create', json = accountReg, headers = header )
        print( "Response Text: " + accountResponse.text )
    #print( token )
    print( requests.get( baseUrl2 + "secret", headers = header ).json()['answer'] )

for user, password, bank_acct in ccProcessorReg:
    userReg = {"username":user, "password":password, "bank_acct": "0001222233334567"}
    regMessage = requests.post( ccUrl + "registration", json = userReg )
    print( "Reg Message: " + regMessage.text )
    loginForm = {"username":user, "password":password}
    token = requests.post( ccUrl + "login", json = loginForm ).json()
    print( token['access_token'] )
    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
'''
userReg = {"username":'target', "password":'tartans@1', "bank_acct":'0001222233334567'}
regMessage = requests.post( ccUrl + "registration", json = userReg )
print( "Reg Message: " + regMessage.text )
loginForm = {"username":'target', "password":'tartans@1'}
token = requests.post( ccUrl + "login", json = loginForm ).json()
print( token['access_token'] )
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
'''
input( "Press enter to continue to deposit tests..." )

print( "Testing deposit..." )

loginForm = {"username":'pnc_000',"password":'tartans@1'}
token = requests.post( baseUrl + "login", json = loginForm ).json()
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
depositResponse = requests.post( baseUrl + "bank/deposit", json = { 'amount': 1000.00, 'account': '0001222233334879' }, headers = header )

print( depositResponse.text )

loginForm = {"username":'pnc_001',"password":'tartans@1'}
token = requests.post( baseUrl2 + "login", json = loginForm ).json()
header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
depositResponse = requests.post( baseUrl2 + "bank/deposit", json = { 'amount': 100.00, 'account': '0012222233334879' }, headers = header )
'''


#!/usr/bin/python3

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

#Acts as a merchant PoS system - generates transactions
#Passes on transactions to merchant's CC processor to get finalized

import requests, random, time
from init_script import gen_all_data, handle_current_component

#gen_all_data( rand_seed, num_banks, num_ccs, num_mercs, num_users, url_list_filepath )
#handle_current_component( gen_all, component_id, num_banks, num_ccs, num_mercs, register_to_db=False, return_all=False )

gen_all = gen_all_data('3', 1, 1, 1, 50, '/home/url_list.txt')
current_component = handle_current_component( gen_all, 'm0', 1, 1, 1, False, False )

while True:
    time.sleep(random.randrange(3, 10))
    try:
        if random.randint(0, 10) < 8:
            current_user_acct = current_component[1][random.randrange( 0, len(current_component[1]) )]
            if current_user_acct.startswith( str( current_component[0][3][4] ) ):
                bnk_loginForm = {"username":current_component[0][1], "password":current_component[0][3][3]}
                bnk_token = requests.post( current_component[0][3][1] + "login", json = bnk_loginForm, verify=False ).json()
                print( bnk_token )
                bnk_header = { "Authorization": "Bearer " + bnk_token['access_token'], "Content-Type": "application/json" }
                depositResponse = requests.post( current_component[0][3][1] + "bank/deposit", json = { 'amount': random.randint(1, 250), 'account': current_user_acct, 'counterpart_name': current_component[0][1], 'fraud_flag': 0 }, headers = bnk_header, verify=False )
                print( depositResponse.text )
        else:
            loginForm = {"username":current_component[0][1], "password":current_component[0][2][2]}
            token = requests.post( current_component[0][2][1] + "login", json = loginForm, verify=False ).json()
            print( token )
            header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
            transactionResponse = requests.post( current_component[0][2][1] + "processTransaction", json = { "amount": random.randrange(1, 25), 'card_num': current_component[1][random.randrange(0, len(current_component[1]))] }, headers = header, verify=False )
            print( transactionResponse.text )
    except Exception as e:
        print( e )
        print( "Issue with sending request. Trying again." )

#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

### ---
# @file  resources.py
# @brief endpoints to interact with finsim-cc server
## @list of endpoints
#	ProcessTransaction
#	UserRegistration
#       UserLogin
#	TokenRefresh
### ---

import requests, random
from finsim_cc.helper import cc_login, check_login_list
from flask_restful import Resource, reqparse
from finsim_cc.models import UserModel, TransactionModel, TxType, TxStatus
from flask_jwt_extended import ( create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt )
from flask import jsonify


current_component = []

#user_reg_parser is used in UserRegistration resource
user_reg_parser = reqparse.RequestParser()
user_reg_parser.add_argument( 'username', help = 'This field cannot be blank', required = True )
user_reg_parser.add_argument( 'password', help = 'This field cannot be blank', required = True )
user_reg_parser.add_argument( 'bank_acct', help = 'This field cannot be blank', required = True )

#user_parser is used in UserLogin resource
user_parser = reqparse.RequestParser()
user_parser.add_argument( 'username', help = 'This field cannot be blank', required = True )
user_parser.add_argument( 'password', help = 'This field cannot be blank', required = True )

#trans_parser is used in ProcessTransaction resource
trans_parser = reqparse.RequestParser()
trans_parser.add_argument( 'amount', help = 'This field cannot be blank', required = True )
trans_parser.add_argument( 'card_num', help = 'This field cannot be blank', required = True )

## ---
# @brief  ProcessTransaction is the endpoint that receives transactions from a Point of Sale (PoS) system
#           It logs the transaction and determines the bank that the merchant is associated with
#           Passes on customer's card number, merchant's bank account number, and the amount to charge the customer's card
# @input  amount, card_num
#           uses trans_parser
#           Merchant must be logged into finsim-cc in order for transaction to be successful
#             done via @jwt_required
# @return status from finsim-trans /processCard endpoint
#           after sending card_num, bank_acct, amount 
## ---
class ProcessTransaction( Resource ):
    @jwt_required
    def post( self ):
        global current_component
        #Always start by checking whether current_component is filled out or not
        if len(current_component) == 0:
            current_component = check_login_list()
            if len(current_component) == 0:
                return { 'message': 'There was a problem with the current component functionality.' }
        data = trans_parser.parse_args()	#process input from merchant PoS
        if float(data['amount']) <= 0.00:
            return { 'message': 'Invalid amount for transaction. Must be greater than $0.00.' }
        merchant_user = UserModel.find_by_username( get_jwt_identity() )		#Find the merchant given jwt_identity
        trans = TransactionModel( amount = data['amount'], type = TxType.CREDIT, user_id = merchant_user.id, acct_num = data.card_num )

	#Login to the trans server, format the return value in JSON, then send to finsim-trans /processCard endpoint
	#  Update log after receiving response, and pass it on back to merchant PoS
        try:
            #UPDATED FUNCTIONALITY - to use current_component populated by helper function check_login_list rather than hard-coded list of bank info
            for bank in current_component[4]:
                bnk_id, url, password, prefix = bank[0], bank[1], bank[2], bank[3]
                if merchant_user.bank_acct.startswith( str(prefix) ):
                    #cc_login is a helper function in helper.py used to take care of logging into the correct bank
                    token = cc_login(url, current_component[3], password)
                    header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
                    transReg = { "source": data.card_num, "destination": merchant_user.bank_acct, "amount": data.amount }
                    #output - source (customer's card num), dest (merchant's bank_acct), and amount
                    acctResponse = requests.post( url + "card/process", json = transReg, headers = header, verify=False ).json()	#post this to /card/process
                    if(acctResponse['message'] == "Card processed successfully."):	#if the process was successful
                        trans.status = TxStatus.APPROVED	#update transaction log appropriately
                    else:
                        trans.status = TxStatus.DECLINED
                    trans.save_to_db()				#save updated transaction log
                    return acctResponse		#return result to merchant
                    break
            
        except Exception as e:
            print( e )
            return { 'message': 'There was a problem processing the transaction.' }       

## ---
# @brief  UserRegistration is the endpoint used to register merchants to be able to connect to finsim-cc
# @input  username, password
#           uses user_parser
# @return  success response, access_token, refresh_token
#           or failure response
## ---
class UserRegistration( Resource ):
    def post( self ):
        data = user_reg_parser.parse_args()

        if UserModel.find_by_username( data['username'] ):
            return { 'message': 'User {} already exists.'.format(data['username']) }

        new_user = UserModel( username = data['username'], password = UserModel.generate_hash( data['password'] ), bank_acct = data['bank_acct'] )
        try:
            new_user.save_to_db()
            access_token = create_access_token( identity = data['username'] )
            refresh_token = create_refresh_token( identity = data['username'] )
            return { 'message': 'User {} was created.'.format( data['username'] ), 'access_token': access_token, 'refresh_token': refresh_token }
        except:
            return { 'message': 'Something went wrong.' }, 500

## ---
# @brief  UserLogin is used by merchants to connect to finsim-cc
# @input  username, password
#           uses user_parser
# @return  success response, access_token, refresh_token
#           or failure response
## ---
class UserLogin( Resource ):
    def post( self ):
        data = user_parser.parse_args()
        current_user = UserModel.find_by_username( data['username'] )
        if not current_user:
            return {'message':'User {} does not exist.'.format(data['username']) }

        if UserModel.verify_hash( data['password'], current_user.password ):
            access_token = create_access_token( identity = data['username'] )
            refresh_token = create_refresh_token( identity = data['username'] )
            return {'message': 'Logged in as {}.'.format( current_user.username ), 'access_token': access_token, 'refresh_token': refresh_token}
        else:
            return {'message': 'Wrong credentials'}
## ---
# @brief  TokenRefresh endpoint to provide a new access_token
# @return  access_token
## ---
class TokenRefresh( Resource ):
    @jwt_refresh_token_required
    def post( self ):
        current_user = get_jwt_identity()
        access_token = create_access_token( identity = current_user )
        return { 'access_token': access_token }


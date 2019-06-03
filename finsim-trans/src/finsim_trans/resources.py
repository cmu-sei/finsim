#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

### ---
# @file  resources.py
# @brief endpoints to interact with finsim-trans server
## @list of endpoints
#	ListAccounts (frontend)
#	GetAccountInfo (frontend)
#       ListTransactions (frontend)
#	FlagAsFraud
#	ProcessCard
#	BankWithdrawal
#	BankDeposit
#	AccountCreation
#	UserRegistration
#	UserLogin
#	TokenRefresh
### ---

from finsim_trans.helper import bnk_login, check_login_list
from flask_restful import Resource, reqparse, marshal_with, fields
from finsim_trans.models import UserModel, AccountModel, TransactionModel, TxType, FraudType, RoleType
from flask_jwt_extended import ( create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt )
from flask import jsonify
from decimal import Decimal 
import requests


current_component = []

#Used to control what exactly gets returned by resources as a response
#account_fields used by ListAccounts and GetAccountInfo resources
account_fields = { 'id': fields.String, 'account_number': fields.String, 'balance': fields.String }
#transaction fields used by ListTransactions resource
transaction_fields = { 'id': fields.String, 'amount': fields.String, 'type': fields.String, 'account_id': fields.String, 'account': fields.String, 'counterpart_name': fields.String, 'counterpart_acct': fields.String }

# These nearly identical parsers pull arguments out of the request and return an error if anything is missing

#parser is used in UserRegistration
parser = reqparse.RequestParser()
parser.add_argument( 'username', help = 'This field cannot be blank', required = True )
parser.add_argument( 'password', help = 'This field cannot be blank', required = True )
parser.add_argument( 'role', help = 'This field cannot be blank', required = True )

#parserLogin is used in UserLogin resource
parserLogin = reqparse.RequestParser()
parserLogin.add_argument( 'username', help = 'This field cannot be blank', required = True )
parserLogin.add_argument( 'password', help = 'This field cannot be blank', required = True )

#accountParser is used in GetAccountInfo, ListTransactions, and AccountCreation resources
accountParser = reqparse.RequestParser()
accountParser.add_argument( 'number', help = 'This field cannot be blank', required = True )

#depositParser is used in BankDeposit resource
depositParser = reqparse.RequestParser()
depositParser.add_argument( 'amount', help = 'This field cannot be blank', required = True )
depositParser.add_argument( 'account', help = 'This field cannot be blank', required = True )
depositParser.add_argument( 'counterpart_name', help = 'This field cannot be blank', required = True )
depositParser.add_argument( 'counterpart_acct', help = 'This field cannot be blank', required = False )

#withdrawalParser is used in BankWithdrawal resource
withdrawalParser = reqparse.RequestParser()
withdrawalParser.add_argument( 'amount', help = 'This field cannot be blank', required = True )
withdrawalParser.add_argument( 'account', help = 'This field cannot be blank', required = True )
withdrawalParser.add_argument( 'counterpart_name', help = 'This field cannot be blank', required = True )
withdrawalParser.add_argument( 'counterpart_acct', help = 'This field cannot be blank', required = True )

#cardParser is used in ProcessCard resource
cardParser = reqparse.RequestParser()
cardParser.add_argument( 'source', help = 'This field cannot be blank', required = True )
cardParser.add_argument( 'destination', help = 'This field cannot be blank', required = True )
cardParser.add_argument( 'amount', help = 'This field cannot be blank', required = True )

#fraudParser is used in FlagAsFraud resource
fraudParser = reqparse.RequestParser()
fraudParser.add_argument( 'account', help = 'This field cannot be blank', required = True )
fraudParser.add_argument( 'transaction', help = 'This field cannot be blank', required = True )

## ---
# @brief ListAccounts returns a list of all the accounts that the currently logged in user owns
#   Primarily used by finsim-web Angular frontend for bank
#   User must be logged into finsim-web/trans in order to be able to get their account information (authenticated via @jwt_required)
# @return list of accounts
## ---
class ListAccounts( Resource ):
    @jwt_required
    @marshal_with( account_fields )
    def get( self ):
        user = UserModel.find_by_username( get_jwt_identity()['username'] )
        accounts = AccountModel.find_all_by_id( user.id );

        for a in accounts:
            print( a.id, a.account_number, a.balance )
        print( type( accounts ) )
        return accounts

## ---
# @brief GetAccountInfo returns the account info for one bank account owned by the logged in user
#   Primarily used by finsim-web Angular frontend for bank
# @input number - account number that the user account wants to access
#   User must be logged into finsim-web/trans in order to be able to get their account information (authenticated via @jwt_required)
# @return account id, number, and balance for the requested account number IF the user does own the requested account
## ---
class GetAccountInfo( Resource ):
    @jwt_required
    @marshal_with( account_fields )
    def get( self ):
        data = accountParser.parse_args()
        user = UserModel.find_by_username( get_jwt_identity()['username'] )
        if AccountModel.account_exists( user.id, data['number'] ) == True:
            account = AccountModel.find_by_account_number( data['number'] )
            return { 'id': account.id, 'account_number': account.account_number, 'balance': account.balance }
        return { 'message': 'Account does not exist or is not owned by current user.' }

## ---
# @brief ListTransactions returns a list of all the transactions that involves the input account
#   Primarily used by finsim-web Angular frontend for bank
# @input number - account number they want the transactions history of
#   User must be logged into finsim-web/trans in order to be able to get their account information (authenticated via @jwt_required)
# @return list of transactions
## ---
class ListTransactions( Resource):
    @jwt_required
    @marshal_with( transaction_fields )
    def get( self ):
        data = accountParser.parse_args()
        user = UserModel.find_by_username( get_jwt_identity()['username'] )
        if AccountModel.account_exists( user.id, data['number'] ) == True:
            account = AccountModel.find_by_account_number( data['number'] )
            transactions = TransactionModel.find_all_by_account_id( account.id )

            for t in transactions:
                print( t.id, t.amount, t.type, t.account_id )
            return transactions
        return { 'message': 'Account does not exist or is not owned by current user.' }

## ---
# @brief FlagAsFraud flags a transaction as fraud
# @input account, transaction - account number and the transaction the user wants to flag as fraud
#   User must be logged into finsim-trans in order to successfully flag a transaction as fraud
# @return message specifiying success or failure with flagging the transaction
## ---
class FlagAsFraud( Resource ):
    @jwt_required
    def post( self ):
        data = fraudParser.parse_args()
        user = UserModel.find_by_username( get_jwt_identity()['username'] )
        if AccountModel.account_exists( user.id, data['account'] ) == True:
            account = AccountModel.find_by_account_number( data['account'] )
            transaction = TransactionModel.find_by_id( account.id, data['transaction'] )
            if transaction != None:
                transaction.fraud_flag = FraudType.FLAG
                transaction.save_to_db()
                print(transaction.fraud_flag)
                return { 'message': 'Selected transaction has been flagged as fraud.' }
            return { 'message': 'Transaction does not exist or is not made by the specified account.' }
        return { 'message': 'Account does not exist or is not owned by current user.' }

## ---
# @brief ProcessCard flags a transaction as fraud
#  Primarily used by finsim-cc. finsim-trans responding to this web request is always the bank for the destination account
#  If source account is with another bank, this bank will make login and make a web request to the other bank's /bank/withdrawal endpoint
# @input source, destination, amount - source is the user account, destination is the merchant account, amount is what will be transferred from user to destination accounts
#   finsim-cc component must be logged into finsim-trans
# @return message specifiying success or failure with processing the transaction
## ---
class ProcessCard( Resource ):
    @jwt_required
    def post( self ):
        global current_component
        #Always start by checking whether current_component is filled out or not
        if len(current_component) == 0:
            current_component = check_login_list()
            if len(current_component) == 0:
                return { 'message': 'There was a problem with the current component functionality.' }
        data = cardParser.parse_args()

        if get_jwt_identity()['role'] != 'CC': #maybe compare this using the enum instead of a string?
            return { 'message': 'Only a credit card processor can initiate a card processing transaction.' }

        user = UserModel.find_by_username( get_jwt_identity()['username'] )

        destAccount = AccountModel.find_by_account_number( data['destination'] )
        destUser = UserModel.find_by_id( destAccount.owner_id )
        depositTrans = TransactionModel( amount = Decimal( data['amount'] ), type = TxType.CREDIT, account_id = destAccount.id, counterpart_acct = data['source'][-4:], fraud_flag = FraudType.NONE )

        # First we have to confirm that the destination account resides at this bank
        # If not, send an error message.
        if not destAccount.account_number.startswith( str(current_component[5]) ):
            return { 'message': 'Cannot process a card transaction that does not terminate at this bank.' }

        # Next, figure out if this transaction takes place within this bank or across different banks
        if not data['source'].startswith( str(current_component[5]) ):
            # For a back-to-bank transaction
            for bank in current_component[4]:
                if len(bank) != 1:
                    if data['source'].startswith( str(bank[3]) ):
                        #cc_login is a helper function in helper.py used to take care of logging into the correct bank
                        token = bnk_login(bank[1], current_component[3], bank[2])
                        header = { "Authorization": "Bearer " + token['access_token'], "Content-Type": "application/json" }
                        # Make the request to the remote bank
                        bankResponse = requests.post( bank[1] + "/bank/withdrawal", json = { 'amount': data['amount'], 'account': data['source'], 'counterpart_name': destUser.username, 'counterpart_acct': destAccount.account_number[-4:] }, headers = header, verify=False ).json()
                        print( "Withdrawal request response: " )
                        print( bankResponse['message'] )
                        if bankResponse['message'] == "Withdrawal successful.":
                            depositTrans.counterpart_name = bankResponse['counterpart_name']
                            destAccount.applyTransaction( depositTrans )
                            depositTrans.save_to_db()
                            destAccount.save_to_db()
                            return { 'message': 'Card processed successfully 2.' }
                        else:
                            return { 'message': 'Insufficient funds in source account 2.' }
                        break
        else:
            # For a local transaction
            srcAccount  = AccountModel.find_by_account_number( data['source'] )
            withdrawalTrans = TransactionModel( amount = Decimal( data['amount'] ), type = TxType.DEBIT, account_id = srcAccount.id, counterpart_acct = destAccount.account_number[-4:], fraud_flag = FraudType.NONE )
            try:
                withdrawalTrans.counterpart_name = destUser.username
                debitOk = srcAccount.applyTransaction( withdrawalTrans )
                if debitOk:
                    srcUser = UserModel.find_by_id( srcAccount.owner_id )
                    depositTrans.counterpart_name = srcUser.username
                    destAccount.applyTransaction( depositTrans )
                    depositTrans.save_to_db()
                    withdrawalTrans.save_to_db()
                    srcAccount.save_to_db()
                    destAccount.save_to_db()
                    return { 'message': 'Card processed successfully.' }
                else:
                    return { 'message': 'Insufficient funds in source account.' }

            except Exception as e:
                print( e )
                return { 'message': 'There was a problem processing this card transaction.' }


## ---
# @brief BankWithdrawal withdraws a specified amount from the bank account
# @input amount, account, counterpart_name, counterpart_acct - account is the account that will potentially have the amount taken out of it's balance. Counterpart refers to who initiated the withdrawal
#   A BANK user must be logged in in order to initiate a withdrawal. No other users may do so
# @return id, balance, owner, message, counterpart - counterpart indicates who initiated the withdrawal
## ---
class BankWithdrawal( Resource ):
    @jwt_required
    def post( self ):
        data = withdrawalParser.parse_args()
        
        if get_jwt_identity()['role'] != 'BANK': #maybe compare this using the enum instead of a string?
            return { 'message': 'Only a bank can initiate a withdrawal.' }

        user = UserModel.find_by_username( get_jwt_identity() )

        try:
            account = AccountModel.find_by_account_number( data['account'] )
            #TODO Add logic to prevent account from going negative
            #     Good approach would be to do this in the applyTransaction() method. make it return a bool
            #     True signifies successful transaction, False means it failed (would go negative) then check
            #     the result here and react accordingly.
            trans = TransactionModel( amount = data['amount'], type = TxType.DEBIT, account_id = account.id, counterpart_name = data['counterpart_name'], counterpart_acct = data['counterpart_acct'], fraud_flag = FraudType.NONE )
            acctUser = UserModel.find_by_id( account.owner_id )
            trans.save_to_db()
            account.applyTransaction( trans )
            account.save_to_db()
            return { 'id': account.id, 'balance': str(account.balance), 'owner': account.owner_id, 'message': 'Withdrawal successful.', 'counterpart_name': acctUser.username}
        except Exception as e:
            print( e )
            return { 'message': 'There was a problem processing the credit transaction.' }

## ---
# @brief BankDeposit deposits a specified amount into the bank account
# @input amount, account, counterpart_name, counterpart_acct - account is the account that will potentially have the amount added to its balance. Counterpart refers to who initiated the deposit
#   A user must be logged in in order to initiate a deposit
# @return id, balance, owner - counterpart indicates who initiated the deposit
## ---
class BankDeposit( Resource ):
    @jwt_required
    def post( self ):
        data = depositParser.parse_args()
        user = UserModel.find_by_username( get_jwt_identity() )

        try:
            account = AccountModel.find_by_account_number( data['account'] )
            trans = TransactionModel( amount = data['amount'], type = TxType.CREDIT, account_id = account.id, counterpart_name = data['counterpart_name'], counterpart_acct = data['counterpart_acct'], fraud_flag = FraudType.NONE )
            trans.save_to_db()
            account.applyTransaction( trans )
            account.save_to_db()
            return jsonify( { 'id': account.id, 'balance': str(account.balance), 'owner': account.owner_id } )
        except Exception as e:
            print( e )
            return { 'message': 'There was a problem processing the credit transaction.' }

## ---
# @brief AccountCreation creates a bank account for the logged in user
# @input number - account number to create
#   A user must be logged in in order to create an account
# @return message - indicates result of account creation
## ---
class AccountCreation( Resource ):
    @jwt_required
    def post( self ):
        # TODO maybe restrict this feature to certain roles (admin only)
        data = accountParser.parse_args()
        identity = get_jwt_identity()
        print( "{}".format( identity['role'] ) )
        user = UserModel.find_by_username( identity['username'] )
        print( "Creating account for {}".format( user.username ) )
        newAccount = AccountModel( balance = 0.0, owner_id = user.id, account_number = data['number'] )

        try:
            newAccount.save_to_db()
            return { 'message': 'Account created successfully' }
        except Exception as e:
            print( e )
            return { 'message': 'Could not create account' }

## ---
# @brief UserRegistration is the endpoint used to register users to finsim-trans
# @input  username, password, role
# @return  message, access_token, refresh_token - message indicates successful registration
#           or failure message
## ---
class UserRegistration( Resource ):
    def post( self ):
        data = parser.parse_args()

        if UserModel.find_by_username( data['username'] ):
            return { 'message': 'User {} already exists.'.format(data['username']) }

        new_user = UserModel( username = data['username'], password = UserModel.generate_hash( data['password'] ), role = RoleType[data['role']] )
        try:
            new_user.save_to_db()
            identity = { 'username': new_user.username, 'role': new_user.role.name }
            access_token = create_access_token( identity = identity )
            refresh_token = create_refresh_token( identity = identity )
            return { 'message': 'User {} was created.'.format( data['username'] ), 'access_token': access_token, 'refresh_token': refresh_token }
        except Exception as e:
            print( e )
            return { 'message': 'Something went wrong.' }, 500

## ---
# @brief  UserLogin is used by users to connect to finsim-trans
# @input  username, password
# @return  message, access_token, refresh_token - message indicates successful login
#           or failure message
## ---
class UserLogin( Resource ):
    def post( self ):
        data = parserLogin.parse_args()
        current_user = UserModel.find_by_username( data['username'] )
        if not current_user:
            return {'message':'User {} does not exist.'.format(data['username']) }, 401

        if UserModel.verify_hash( data['password'], current_user.password ):
            identity = { 'username': data['username'], 'role':  current_user.role.name }
            access_token = create_access_token( identity = identity )
            refresh_token = create_refresh_token( identity = identity )
            return {'message': 'Logged in as {}.'.format( current_user.username ), 'access_token': access_token, 'refresh_token': refresh_token}
        else:
            return {'message': 'Wrong credentials'}, 401

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

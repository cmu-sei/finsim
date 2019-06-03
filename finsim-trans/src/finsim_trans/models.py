#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

import enum
from finsim_trans import db
from passlib.hash import pbkdf2_sha256 as sha256

class TxType( enum.Enum ):
    CREDIT = 1
    DEBIT = 2

class FraudType( enum.Enum ):
    NONE = 0
    FLAG = 1

class RoleType( enum.Enum ):
    USER = 1
    BANK = 2
    CC = 3

class TransactionModel( db.Model ):
    __tablename__ = 'transaction'

    id = db.Column( db.Integer, primary_key = True )
    amount = db.Column( db.Numeric( precision = 19, scale = 2, asdecimal = True, decimal_return_scale = 2 ), nullable = False )
    type = db.Column( db.Enum( TxType ), nullable = False )
    account_id = db.Column( db.Integer, db.ForeignKey( 'account.id' ) )
    account = db.relationship( "AccountModel", back_populates="transactions" )
    counterpart_name = db.Column( db.String( 120))
    counterpart_acct = db.Column( db.String( 4 ))
    fraud_flag = db.Column( db.Enum( FraudType ), nullable = False )

    def save_to_db( self ):
        db.session.add( self )
        db.session.commit()

    @classmethod
    def find_all_by_account_id( cls, id ):
        return cls.query.filter_by( account_id = id ).all()

    @classmethod
    def find_by_id( cls, account_id, id ):
        return cls.query.filter_by( id = id, account_id = account_id ).first()

class AccountModel( db.Model ):
    __tablename__ = 'account'

    id = db.Column( db.Integer, primary_key = True )
    balance = db.Column( db.Numeric( precision = 19, scale = 2, asdecimal = True, decimal_return_scale = 2 ), nullable = False )
    account_number = db.Column( db.String( 16 ), unique = True, nullable = False )
    owner_id = db.Column( db.Integer, db.ForeignKey( 'user.id' ) )
    owner = db.relationship( "UserModel", back_populates="accounts" )
    transactions = db.relationship( "TransactionModel", back_populates="account" )

    def save_to_db( self ):
        db.session.add( self )
        db.session.commit()

    def applyTransaction( self, trans ):
        print( "Internal balance: " + str( self.balance ) )
        print( "amount type: {}".format( type( trans.amount ) ) )
        print( "balance type: {}".format( type( self.balance ) ) )
        if trans.type == TxType.CREDIT:
            self.balance = self.balance + trans.amount
        elif trans.type == TxType.DEBIT:
            self.balance = self.balance - trans.amount
            if self.balance < 0:
                self.balance = self.balance + trans.amount
                return False
        else:
            print( "Transaction not applied." )
            pass
        print( "Internal balance: " + str( self.balance ) )
        return True

    @classmethod
    def find_by_account_number( cls, account_number ):
        return cls.query.filter_by( account_number = account_number ).first()

    @classmethod
    def find_by_id( cls, id ):
        return cls.query.filter_by( id = id ).first()

    @classmethod
    def find_all_by_id( cls, id ):
        return cls.query.filter_by( owner_id = id ).all()

    @classmethod
    def account_exists( cls, id, account_number ):
        if cls.query.filter_by( owner_id = id, account_number = account_number ).first() != None:
            return True
        return False

class UserModel( db.Model ):
    __tablename__ = 'user'

    id = db.Column( db.Integer, primary_key = True )
    username = db.Column( db.String( 120 ), unique = True, nullable = False )
    password = db.Column( db.String( 120 ), nullable = False )
    accounts = db.relationship( "AccountModel", back_populates="owner" )
    role = db.Column( db.Enum( RoleType ), nullable = False )

    @classmethod
    def find_by_username( cls, username ):
        return cls.query.filter_by( username = username ).first()

    @classmethod
    def find_by_id( cls, id ):
        return cls.query.filter_by( id = id ).first()

    @classmethod
    def return_all( cls ):
        def to_json( x ):
            return { 'username': x.username, 'password': x.password, 'role': x.role }
        return { 'users': list( map( lambda x: to_json( x ), UserModel.query.all() ) ) }

    @classmethod
    def delete_all( cls ):
        try:
            num_rows_deleted = db.session.query( cls ).delete()
            db.session.commit()
            return { 'message': '{} rows deleted.'.format( num_rows_deleted ) }
        except:
            return { 'message': 'Something went wrong deleting all users.' }

    @staticmethod
    def generate_hash( password ):
        return sha256.hash( password )

    @staticmethod
    def verify_hash( password, hash ):
        return sha256.verify( password, hash )

    def save_to_db( self ):
        db.session.add( self )
        db.session.commit()


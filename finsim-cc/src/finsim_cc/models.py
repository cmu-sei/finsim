#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

### ---
# @file  models.py
# @brief tables that make up the finsim-cc database
## @list of models
#	TransactionModel
#	UserModel
#		@classmethods
#			find_by_username
#			return_all
#			delete_all
#		@staticmethods
#			generate_hash
#			verify_hash
### ---

import enum
from finsim_cc import db
from passlib.hash import pbkdf2_sha256 as sha256

### ---
# @brief TxType enum to differentiate between credit or debit for each transaction
### ---
class TxType( enum.Enum ):
    CREDIT = 1
    DEBIT = 2

### ---
# @brief TxStatus enum to log whether a transactin was approved or denied
### ---
class TxStatus( enum.Enum ):
    APPROVED = 1
    DECLINED = 2

### ---
# @brief Used to log transactions
#          status is updated after finsim-trans processes the transaction sent by finsim-cc processTransaction
### ---
class TransactionModel( db.Model ):
    __tablename__ = 'transaction'

    id = db.Column( db.Integer, primary_key = True )
    amount = db.Column( db.Numeric( precision = 19, scale = 2, asdecimal = True, decimal_return_scale = 2 ), nullable = False )
    type = db.Column( db.Enum( TxType ), nullable = False )
    user_id = db.Column(db.Integer, db.ForeignKey( 'user.id'), nullable = False)
    acct_num = db.Column( db.String( 16 ), unique = False )
    status = db.Column( db.Enum( TxStatus ))

    def save_to_db( self ):
        db.session.add( self )
        db.session.commit()

### ---
# @brief Used by merchants to connect to finsim-cc
### ---
class UserModel( db.Model ):
    __tablename__ = 'user'

    id = db.Column( db.Integer, primary_key = True )
    username = db.Column( db.String( 120 ), unique = True, nullable = False )
    password = db.Column( db.String( 120 ), nullable = False )
    bank_acct = db.Column( db.String( 16 ), unique = True, nullable = False )
    transactions = db.relationship('TransactionModel', backref='usermodel', lazy = True)

    @classmethod
    def find_by_username( cls, username ):
        return cls.query.filter_by( username = username ).first()

    @classmethod
    def return_all( cls ):
        def to_json( x ):
            return { 'username': x.username, 'password': x.password }
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


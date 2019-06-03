#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

### ---
# @file  __init__.py
# @brief Main file called to start up finsim-trans
#	   configures the database backend
#	   and matches the resources to their endpoints
#	   before creating database tables
### ---

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging

appLogger = logging.getLogger()

app = Flask( __name__ )
CORS( app )
app.debug=True

#Logging used in dev mode
fileHandler = logging.FileHandler( filename = "bnk_000_log.txt" )
fileHandler.setLevel(logging.NOTSET)
appLogger.addHandler(fileHandler)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://trans:@localhost/trans'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

db  = SQLAlchemy( app )
api = Api( app )
jwt = JWTManager( app )

import finsim_trans.views, finsim_trans.models, finsim_trans.resources

#Routes in which to access each endpoint for finsim-trans
api.add_resource( resources.UserRegistration, '/registration' )
api.add_resource( resources.UserLogin, '/login' )
api.add_resource( resources.TokenRefresh, '/token/refresh' )

api.add_resource( resources.AccountCreation, '/account/create' )
api.add_resource( resources.BankDeposit, '/bank/deposit' )
api.add_resource( resources.BankWithdrawal, '/bank/withdrawal' )

api.add_resource( resources.ProcessCard, '/card/process' )
api.add_resource( resources.FlagAsFraud, '/flag/fraud' )

# Endpoints for the web frontend
api.add_resource( resources.ListAccounts, '/web/accounts' )
api.add_resource( resources.GetAccountInfo, '/web/account' )
api.add_resource( resources.ListTransactions, '/web/transactions' )

@app.before_first_request
def create_tables():
    db.create_all()

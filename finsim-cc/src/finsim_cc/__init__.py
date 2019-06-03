#  FinSim
#  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
#  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.

### ---
# @file  __init__.py
# @brief Main file called to start up finsim-cc
#	   configures the database backend
#	   and matches the resources to their endpoints
#	   before creating database tables
### ---

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import logging

appLogger = logging.getLogger()

app = Flask( __name__ )

#Logging used in dev mode
fileHandler = logging.FileHandler( filename = "cc_000_log.txt" )
fileHandler.setLevel(logging.NOTSET)
appLogger.addHandler(fileHandler)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cc:@localhost/cc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

db  = SQLAlchemy( app )
api = Api( app )
jwt = JWTManager( app )

import finsim_cc.views, finsim_cc.models, finsim_cc.resources

#Routes in which to access each endpoint for finsim-cc
api.add_resource( resources.UserRegistration, '/registration' )
api.add_resource( resources.UserLogin, '/login' )
api.add_resource( resources.TokenRefresh, '/token/refresh' )

api.add_resource( resources.ProcessTransaction, '/processTransaction' )

@app.before_first_request
def create_tables():
    db.create_all()

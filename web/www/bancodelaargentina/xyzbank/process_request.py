# FinSim
#
# Copyright 2019 Carnegie Mellon University. All Rights Reserved.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
#
# Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
#
# [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
#
# This Software includes and/or makes use of the following Third-Party Software subject to its own license:
#
# 1. Django (https://www.djangoproject.com/foundation/faq/) Copyright 2005-2018 Django Software Foundation.
# 2. bootstrap (https://getbootstrap.com/docs/4.0/about/license/) Copyright 2018 Twitter.
# 3. glyphicons (https://www.glyphicons.com/license/) Copyright 2010-2018 GLYPHICONS.
# 4. jquery (https://jquery.org/license/) Copyright 2018 jquery foundation.
# 5. jquery tablesorter (https://mottie.github.io/tablesorter/docs/) Copyright 2007-2018 Christian Bach, Rob Garrison and Contributing Authors (see AUTHORS file).
# 6. jquery validate (https://jqueryvalidation.org/) Copyright 2006-2018 J�rn Zaefferer,  Markus Staab, Brahim Arkni, and contributors .
# 7. jquery validate unobtrusive (https://github.com/aspnet/jquery-validation-unobtrusive/blob/master/LICENSE.txt) Copyright 2014-2018 .NET Foundation.
# 8. modernizr (https://github.com/Modernizr/Modernizr/blob/master/LICENSE) Copyright 2009-2018 https://github.com/Modernizr/Modernizr/graphs/contributors.
# 9. respond.js (https://github.com/scottjehl/Respond) Copyright 2011 Scott Jehl.
# 10. roboto fonts (https://fonts.google.com/specimen/Roboto) Copyright 2015-2018 Google, Inc..
# 11. xregexp (http://xregexp.com/) Copyright 2007-2012 Steven Levithan.
#
# DM19-0396
#
import ast
import datetime
from decimal import Decimal

from app.models import CommercialAccounts
from app.models import UserAccounts
from django.db.models import Q


class ValidCardFound(Exception):        #raise exception when the current card is determined to be valid
    def __init__(self):
        self.message = "The card number matches the configuration requirements"

#Request class handles the requests that are sent in - both validating and processing
#5 methods and init: __init__(self, obj), get_url(self), user_account_transaction(self), user_account_deposit(self), valid_merchant(account_id), and proccess_merchant(self, results)
class Request:
    def __init__(self, obj):
        self.obj = obj
        self.index = 0

    #get_url(self) checks card number against account number before printing out company and returning domain and key location info
    #   if card and account numbers do not match, the method returns nothing
    def get_url(self):
        card = self.obj["CardNumber"]   #set card variable to what is found in the obj dictionary
        accounts = CommercialAccounts.objects.filter(~Q(Identifier="[]"))   #get all filtered accounts
        for i in accounts:  #for every account in the accounts list
            id = ast.literal_eval(i.Identifier)     #get account id
            for j in id:
                if int(card[:len(str(j))]) == j:    #card number matches the account id
                    print i.Company     #print the account's company
                    return {"Domain": i.Domain, "Cert": i.KeyLocation}  #return domain and cert/key location
        return None     #otherwise return nothing

    #user_account_transaction(self) verifies user account information and then accepts the transaction if it is valid
    #   or declines the transaction. Account info is saved either way afterwards, and obj is returned
    def user_account_transaction(self):
        if not UserAccounts.objects.filter(AccountNumber=self.obj['AccountNumber']).exists():   #if the current user account doesn't exist
            self.obj['AuthType'] = "N"      #set AuthType to "N"
            return self.obj     #and return obj
        account = UserAccounts.objects.get(AccountNumber=self.obj['AccountNumber'])     #otherwise, get the account of the current user
        #checking to make sure account isn't just empty, has the right address/city/state/zipcode
        if account and account.Address == self.obj['Address'] and account.City == self.obj['City'] and account.State == \
                self.obj['State'] and account.ZipCode == self.obj['ZipCode']:
            if account.Balance - Decimal(self.obj['PrimaryAmount']) > 0:    #checks to make sure that the amount being taken from the balance is a valid transaction
                account.Approved += 1   #if so, approved counter is incremented
                account.Transactions += 1   #transactions counter is incremented
                account.Balance -= Decimal(self.obj['PrimaryAmount'])   #update to new running balance
                account.save()  #update account information
                self.obj['Confirmations'] = "%010d%010d" % (10001, (self.index % 10000)) + "{:%m%d%Y%M}".format(datetime.datetime.now())    #Update confirmations
                self.obj['AuthType'] = "0"  #AuthType set to 0
            else:   #invalid transaction - trying to use more than what is in the balance
                account.Denied += 1     #denied counter is incremented
                account.Transactions += 1   #transactions counter is incremented
                account.save()      #update account information
                self.obj['Confirmations'] = ""      #Nothing in confirmations
                self.obj['AuthType'] = "51"     #AuthType set to 51
        else:       #if account is empty or address info does not match up
            self.obj['AuthType'] = "N"      #AuthType set to N
        return self.obj     #return obj

    #user_account_deposit(self) verifies user account information and then accepts the transaction
    def user_account_deposit(self):
        if not UserAccounts.objects.filter(AccountNumber=self.obj['AccountNumber']).exists():   #if current user account does not exist
            self.obj['AuthType'] = "N"      #set AuthType to N
            return self.obj     #return obj
        account = UserAccounts.objects.get(AccountNumber=self.obj['AccountNumber'])     #get account
        #verify that account is not empty and address info matches what is in obj
        if account and account.Address == self.obj['Address'] and account.City == self.obj['City'] and account.State == \
                self.obj['State'] and account.ZipCode == self.obj['ZipCode']:
                account.Balance += Decimal(self.obj['PrimaryAmount'])   #increment balance by the deposit amount
                account.Approved += 1       #approved counter is incremented
                account.Transactions += 1   #transactions counter is incremented
                account.save()      #update account information
                self.obj['Confirmations'] = "%010d%010d" % (10001, (self.index % 10000)) + "{:%m%d%Y%M}".format(datetime.datetime.now())    #Update confirmations
                self.obj['AuthType'] = "Deposit"    #AuthType set to Deposit
        return self.obj     #return obj

    #valid_merchant(account_id) tries to find whether the specified account_id in the method call is found in the list of merchants
    @staticmethod
    def valid_merchant(account_id):
        buf = CommercialAccounts.objects.all()  #get list of all merchants
        for i in buf:   #iterate through the list
            if i.AccountNumber == account_id:   #if the current merchant from the list matches the account_id
                return True     #match found
        return False    #else, reached the end of the list and no match found

    #[FOR ALEX] misspelled "proccess" for both method and name of python file
    #process_merchant(self, results) updates all merchant information based on the request and results lists
    def proccess_merchant(self, results):
        a_request = results["Invoice"][:10]     #all invoices, truncating the last 10 characters of the invoice value
        a_approve = results["Confirmations"][:10]   #all confirmations, truncating the last 10 characters of the confirmations value
        account = CommercialAccounts.objects.all()      #get all merchant accounts
        for i in account:   #for every merchant
            if i.AccountNumber in a_request and results["AuthType"] == "Approved":      #if in a_request and is approved in results
                i.Balance += Decimal(results["PrimaryAmount"])      #add to merchant balance
                i.Approve += 1      #approve counter incremented
                i.Transactions += 1     #transactions counter incremented
                i.save()            #update merchant account information
            elif i.AccountNumber in a_request:                                          #in a_request but not approved
                i.Denied += 1       #denied counter incremented
                i.Transactions += 1     #transactions counter incremented
                i.save()            #update merchant account information
            elif i.AccountNumber in a_approve and results["AuthType"] == "Approved":    #in a_approve and is approved in results
                i.Balance -= Decimal(results["PrimaryAmount"])
                i.Approve += 1      #approve counter incremented
                i.Transactions += 1     #transactions counter incremented
                i.save()            #update merchant account information
            elif i.AccountNumber in a_approve:                                          #in a_approve but not approved
                i.Denied += 1       #denied counter incremented
                i.Transactions += 1     #transactions counter incremented
                i.save()            #update merchant account information

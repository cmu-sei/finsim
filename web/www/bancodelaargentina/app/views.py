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

"""
Definition of views.
"""
import json
from datetime import datetime
import sys
import requests
from app.models import CommercialAccounts
from app.models import CommercialTransaction
from app.models import UserAccounts
from app.models import UserTransaction
from app.serializers import CommercialTransactionSerializer
from app.serializers import UserTransactionSerializer
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from xyzbank.process_request import Request


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def commercialTransaction(request, id=None):
    """
    List all code Transactions, or create a new Transactions.
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        r = Request(data)
        decision = None
        if not r.valid_merchant(id):        #if not a valid merchant
            return JSONResponse("DNF Credit Card Account", status=400)
        elif "AVS" in data and data["AVS"] == "Deposit":    #else if AVS
            serializer = UserTransactionSerializer(data=r.user_account_deposit())
        else:       #otherwise, get the URL
            url = r.get_url()
            if url:     #if URL exists
                decision = requests.post("https://www.%s/" % url["Domain"], data=json.dumps(data), verify=False).json()     #get the decision of the transaction
                serializer = CommercialTransactionSerializer(data=decision)     #serialize the transaction data
            else:       #otherwise, account is invalid
                return JSONResponse("DNF Credit Card Account", status=400)
        if serializer.is_valid():   
            serializer.save()   #save the serializer of the commercial transaction
            r.proccess_merchant(decision)       #process merchant for the decision
            return JSONResponse(serializer.data, status=201)
        else:       #invalid serializer
            return JSONResponse(serializer.errors, status=400)
    else:
        return redirect('home')


@csrf_exempt
def userTransaction(request, id=None):
    """
    List all code Transactions, or create a new Transactions.
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserTransactionSerializer(data=Request(data).user_account_transaction())   #serialize the transaction data
        if serializer.is_valid():
            serializer.save()   #save the serializer
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)
    else:
        return redirect('home')


def profile(request, id=None):      #returns account id, username, email, and account type if user or commercial
    u = User.objects.get(id=int(id))
    if UserAccounts.objects.filter(user_id=u.id).exists():  #if user and the given id exists
        account_type = "User"
        account = UserAccounts.objects.get(user_id=u.id)
    elif CommercialAccounts.objects.filter(user_id=u.id).exists():  #if commercial and the given id exists
        account_type = "Commercial"
        account = CommercialAccounts.objects.get(user_id=u.id)
    assert isinstance(request, HttpRequest)     #makes sure that it is an http request instance
    return render(  #return through app/profile.html
        request,
        'app/profile.html',
        {
            'account': account,
            'username': u.username,
            'email': u.email,
            'account_type': account_type
        }
    )


def account(request, first=1, id=None):     #returns specific user greeting, title, and account id based on the type of account
    u = User.objects.get(id=id)
    assert isinstance(request, HttpRequest)     #makes sure that it is an http request instance
    if UserAccounts.objects.filter(user_id=u.id).exists():      #if user account and exists
        account = UserAccounts.objects.get(user_id=u.id)
        user_greeting = "First Name: %s Last Name: %s" % (u.first_name, u.last_name)
    elif CommercialAccounts.objects.filter(user_id=u.id).exists():  #if commercial account and exists
        account = CommercialAccounts.objects.get(user_id=u.id)
        user_greeting = "Company Name: %s " % str(account.Company)
    else:       #otherwise, admin account
        user_greeting = "Admin Account"

    if first == 0:      #first time logging in
        title = 'Welcome back %s it is nice to see you again' % user_greeting
    else:       #logged in recently
        title = 'Logged in as: %s' % user_greeting
    return render(  #return through app/account.html
        request,
        'app/account.html',
        {
            'user_greeting': user_greeting,
            'title': title,
            'account': account,
        }
    )


def history(request, start=0, id=None):     #returns transaction history, account id, title, balance, and username for either a user or commercial account
    assert isinstance(request, HttpRequest)     #makes sure that it is an http request instance
    u = User.objects.get(id=id)
    history = []
    account = None
    if UserAccounts.objects.filter(user_id=u.id).exists():      #if user account and exists
        account = UserAccounts.objects.get(user_id=u.id)        
        history = UserTransaction.objects.filter(AccountNumber=account.AccountNumber).order_by('id')        #get all transactions that involve the current account
    elif CommercialAccounts.objects.filter(user_id=u.id).exists():      #if commercial account and exists
        account = CommercialAccounts.objects.get(user_id=u.id)
        c = CommercialTransaction.objects.all()
        ctr = 0
        for i in c:     #go through all commercial transactions
            print >> sys.stderr, i
            if account.AccountNumber in i.Invoice[:10] or account.AccountNumber in i.Confirmations[:10]:    #if found in either lists of invoices or confirmations - excluding the last 10 entries
                ctr += 1
                if ctr >= int(start) + 25:
                    history.append(i)   #add to the history list
    if history and len(history) > int(start) + 25:
        history = history[int(start):int(start) + 25]
    elif history:
        history = history[int(start):]
    return render(  #return through app/history.html
        request,
        'app/history.html',
        {
            'history': history,
            'account': account,
            'title': 'Your account history is as follows: ',
            'bal': account.Balance,
            'username': u.username,
        }
    )


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
    )


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title': 'Contact',
            'message': 'Your contact page.',
            'year': datetime.now().year,
        }
    )


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title': 'About',
            'message': 'Your application description page.',
            'year': datetime.now().year,
        }
    )

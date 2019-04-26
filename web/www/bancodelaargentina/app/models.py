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
Definition of models.
"""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models


class AbstractTransaction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    FirstName = models.CharField(max_length=30, blank=True, default='')
    LastName = models.CharField(max_length=30, blank=True, default='')
    MiddleIntial = models.CharField(max_length=2, blank=True, default='')
    Address = models.CharField(max_length=80, blank=True, default='')
    City = models.CharField(max_length=30, blank=True, default='')
    State = models.CharField(max_length=30, blank=True, default='')
    ZipCode = models.CharField(max_length=30, blank=True, default='')
    Invoice = models.CharField(max_length=30, blank=True, default='')
    Confirmations = models.CharField(max_length=30, blank=True, default='')
    AuthType = models.CharField(max_length=20, blank=True, default='')
    PrimaryAmount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.0)

    class Meta:
        abstract = True
        ordering = ('-created', '-Invoice')

    def __unicode__(self):
        return self.Invoice


class AbstractAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    Address = models.CharField(max_length=80, blank=True, default='')
    City = models.CharField(max_length=30, blank=True, default='')
    State = models.CharField(max_length=30, blank=True, default='')
    ZipCode = models.CharField(max_length=30, blank=True, default='')
    Balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.0)
    Approved = models.IntegerField(validators=[MaxValueValidator(999999999), ], blank=True, default=0)
    Denied = models.IntegerField(validators=[MaxValueValidator(999999999), ], blank=True, default=0)
    Transactions = models.IntegerField(validators=[MaxValueValidator(999999999), ], blank=True, default=0)
    AccountNumber = models.CharField(max_length=30, blank=True, default='', unique=True)

    class Meta:
        abstract = True
        ordering = ('Balance', 'AccountNumber',)

    def __unicode__(self):
        return self.user.username

#CUSTOM MODELS FOR FINSIM BEGIN HERE
# Create your models here.
class CommercialTransaction(AbstractTransaction):       #storing credit card information, response code, and avs for a commercial transaction (in addition to the fields in AbstractTransaction)
    CardNumber = models.CharField(max_length=16, blank=True, default='')
    ExpDate = models.CharField(max_length=5, blank=True, default='')
    CVV2 = models.CharField(max_length=4, blank=True, default='')
    ResponseCode = models.CharField(max_length=30, blank=True, default='')
    AVS = models.CharField(max_length=5, blank=True, default='')


class UserAccounts(AbstractAccount):        #storing middle initial and ssn for a user account (in addition to the fields in AbstractAccount)
    MiddleInitialntial = models.CharField(max_length=30, blank=True, default='')
    SSN = models.CharField(max_length=30, blank=True, default='', unique=True)


class UserTransaction(AbstractTransaction):     #storing account number for a user transcation (in addition to the fields in AbstractTransaction)
    AccountNumber = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        ordering = ('AccountNumber',)


class CommercialAccounts(AbstractAccount):      #storing company, POC, identifier, key location, and domain for a commercial account (in addition to the fields in AbstractAccount)
    Company = models.CharField(max_length=30, blank=True, default='')
    PointOfContact = models.TextField(max_length=255, blank=True)
    Identifier = models.TextField(max_length=255, blank=True, default="[]")
    KeyLocation = models.FilePathField(blank=True, default='DNF')
    Domain = models.URLField(blank=True, default='DNF')

    class Meta:
        ordering = ('Balance', 'AccountNumber', 'Company')

/*FinSim
Copyright 2018 Carnegie Mellon University. All Rights Reserved.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
*/

import { Component, OnInit } from '@angular/core';
import { BankAccount } from '../bank-account';
import { Transaction } from '../transaction';
import { FinSimService } from '../fin-sim.service';

import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

@Component({
  selector: 'app-account-details',
  templateUrl: './account-details.component.html',
  styleUrls: ['./account-details.component.css']
})
export class AccountDetailsComponent implements OnInit {

  bank_acct: BankAccount;
  transactions: Transaction[];

  constructor( 
    private finSimService: FinSimService,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  ngOnInit() {
    var service = this;
    const acct_num = this.route.snapshot.paramMap.get('acct_num');
    this.finSimService.getAccountInfo(acct_num).subscribe
    ({
      next( bank_acct )
      {
        service.bank_acct = bank_acct;
      },
      error( msg )
      {
        console.log( msg );
      }
    });

    this.finSimService.getTransactions(acct_num).subscribe
    ({
      next( transactions )
      {
        service.transactions = transactions;
      },
      error( msg )
      {
        console.log( msg );
      }
    });
  }

}

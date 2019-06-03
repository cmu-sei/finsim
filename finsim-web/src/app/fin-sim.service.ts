<!--
  FinSim
  Copyright 2018 Carnegie Mellon University. All Rights Reserved.
  NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
  Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
-->

import { Injectable } from '@angular/core';
import { LoginData } from './login-data';
import { AccessToken } from './access-token';
import { Observable, of } from 'rxjs';
import { flatMap, map, take } from 'rxjs/operators';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { User } from './user';
import { BankAccount } from './bank-account';
import { Transaction } from './transaction';
import { AccountCreationMessage } from './account-creation-message';
import { JwtHelperService } from '@auth0/angular-jwt';

@Injectable
({
  providedIn: 'root'
})

export class FinSimService
{
  amIAdmin(): boolean
  {
    const helper = new JwtHelperService();
    const decodedToken = helper.decodeToken( localStorage.getItem( 'currentUser' ) );
    console.log( decodedToken );
    if( decodedToken.authorities.indexOf( 'ROLE_ADMIN' ) > -1 )
      return true;

    return false;
  }

  getAccessToken(): any
  {
    const helper = new JwtHelperService();
    const decodedToken = helper.decodeToken( localStorage.getItem( 'currentUser' ) );
    return decodedToken;
  }

  amILoggedIn(): boolean
  {
    //    const helper = new JwtHelperService();
    //    const decodedToken = helper.decodeToken( localStorage.getItem( 'currentUser' ) );
    //    console.log( decodedToken );
    //    if( !decodedToken.isTokenExpired() )
    //      return true;
    //
    //    return false;


    console.log( "Checking if logged in..." );
    const helper = new JwtHelperService();
    const rawToken = localStorage.getItem( 'currentUser' );
    console.log( "about to decode raw token: " + rawToken );
    const decodedToken = helper.decodeToken( rawToken );
    console.log( "Type of decoded token:" + typeof decodedToken );
    console.log( "About to print decoded token..." );
    console.log( decodedToken );
    console.log( "End of decoded token." );
    if( !helper.isTokenExpired( rawToken ) )
      return true;

    console.log( "NOT LOGGED IN" );

    return false;
  }

  getAccounts(): Observable<BankAccount[]>
  {
    return this.http.get<BankAccount[]>( this.listAccountsUrl );
  }

  getAccountInfo( acct_num ): Observable<BankAccount>
  {
    return <any> this.http.get<BankAccount>( this.bankAccountUrl + '?number=' + acct_num);
  }

  getTransactions( acct_num ): Observable<Transaction[]>
  {
    return <any> this.http.get<Transaction[]>( this.listTransactionsUrl + '?number=' + acct_num);
  }

  postLogin( username: string, password: string): Observable<AccessToken>
  {

    const body = new HttpParams()
      .set( 'username', username )
      .set( 'password', password );

      return this.http.post<AccessToken>( this.loginUrl, { 'username': username, 'password': password } );
  }


  login( user: User )
  {
    //this.loggedIn.next( false );

    if( user.username !== '' && user.password !== '' )
    {
      var service = this
      this.postLogin( user.username, user.password ).subscribe(
      {
        next( accessToken )
        {
          console.log( 'Current access token: ', accessToken.access_token );
	  //service.accessToken = accessToken
	  //service.tokenExpiration = ( new Date().getTime() / 1000 ) + accessToken.expires_in;
	  //service.loggedIn.next( true );
	  localStorage.setItem( 'currentUser', JSON.stringify( accessToken.access_token ) );
          service.router.navigate( ['/accounts'] );
	  //service.cartUpdaterService.filter( 'UPDATE CART PLS' );
        },
        error( msg ) { console.log( 'Error logging in: ', msg.error.message); }
      });
    }
  }

  logout()
  {
    //this.loggedIn.next( false );
    localStorage.removeItem( 'currentUser' );
    this.router.navigate( ['/login'] );
  }

  constructor( private http: HttpClient, private router: Router ){}

  //Edit the domain here with what the actual bank IP is, and change to http if not using SSL
  private domain = '206.120.254.4';   // us
  private urlPrefix = 'https://' + this.domain; // for typical ports

  private serviceUrl = this.urlPrefix + '/api/client';
  private registerUrl = this.urlPrefix + '/api/account/register';
  private regTokenUrl = this.urlPrefix + '/oauth/token';
  private adminUrl = this.urlPrefix + '/api/admin';
  private loginUrl = this.urlPrefix + '/login';
  private listAccountsUrl = this.urlPrefix + '/web/accounts';
  private bankAccountUrl = this.urlPrefix + '/web/account';
  private listTransactionsUrl = this.urlPrefix + '/web/transactions';

}



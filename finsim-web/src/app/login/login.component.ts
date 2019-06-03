/*FinSim
Copyright 2018 Carnegie Mellon University. All Rights Reserved.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
*/

import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { FinSimService } from '../fin-sim.service';

@Component
({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})

export class LoginComponent implements OnInit
{
  form: FormGroup;                    // {1}
  private formSubmitAttempt: boolean; // {2}

  constructor
  (
    private fb: FormBuilder,         // {3}
    private finSimService: FinSimService // {4}
  ){}

  ngOnInit()
  {
    this.form = this.fb.group(
    {
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  isFieldInvalid( field: string )
  {
    return ( (!this.form.get(field).valid && this.form.get(field).touched) || (this.form.get(field).untouched && this.formSubmitAttempt) );
  }

  onSubmit()
  {
    if( this.form.valid )
    {
      this.finSimService.login( this.form.value );
    }

    this.formSubmitAttempt = true;
  }
}

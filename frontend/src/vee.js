// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

/**
 * Imports and set up vee-validate.
 * If more filters are needed, remember to import them here!
 * See more at: https://baianat.github.io/vee-validate/concepts/bundle-size.html
 */

import Vue from 'vue'
import { Validator, install as VeeValidate } from 'vee-validate/dist/vee-validate.minimal.esm.js'
import { required, url, digits, email, min, max, numeric, max_value } from 'vee-validate/dist/rules.esm.js' // eslint-disable-line
import veeDa from 'vee-validate/dist/locale/da'
import ActiveEngagements from './validators/ActiveEngagements'
import Address from './validators/Address'
import CandidateParentOrgUnit from './validators/CandidateParentOrgUnit'
import Cpr from './validators/Cpr'
import Employee from './validators/Employee'
import ExistingAssociations from './validators/ExistingAssociations'
import DateInRange from './validators/DateInRange'
import OrgUnit from './validators/OrgUnit'
import MovableOrgUnit from "./validators/MovableOrgUnit";

/**
 * See configuration options here:
 * https://baianat.github.io/vee-validate/configuration.html
 */
const veeConfig = {
  dateFormat: 'DD-MM-YYYY',
  delay: 100,
  locale: 'da',
  inject: false
}

Validator.localize('da', veeDa)

Validator.extend('required', required)
Validator.extend('digits', digits)
Validator.extend('min_value', max_value)
Validator.extend('email', email)
Validator.extend('url', url)
Validator.extend('numeric', numeric)
Validator.extend('min', min)
Validator.extend('max', max)

Validator.extend('active_engagements', ActiveEngagements)
Validator.extend('address', Address)
Validator.extend('candidate_parent_org_unit', CandidateParentOrgUnit)
Validator.extend('cpr', Cpr)
Validator.extend('employee', Employee)
Validator.extend('existing_associations', ExistingAssociations)
Validator.extend('date_in_range', DateInRange)
Validator.extend('movable_org_unit', MovableOrgUnit)
Validator.extend('orgunit', OrgUnit)

Vue.use(VeeValidate, veeConfig)

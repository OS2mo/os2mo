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
import Cpr from './validators/Cpr'
import Employee from './validators/Employee'
import DateInRange from './validators/DateInRange'
import OrgUnit from './validators/OrgUnit'

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
Validator.extend('cpr', Cpr)
Validator.extend('employee', Employee)
Validator.extend('date_in_range', DateInRange)
Validator.extend('orgunit', OrgUnit)

Vue.use(VeeValidate, veeConfig)

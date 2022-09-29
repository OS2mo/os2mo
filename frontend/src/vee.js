// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

/**
 * Imports and set up vee-validate.
 * If more filters are needed, remember to import them here!
 */

/* Vue and vee imports */
import Vue from "vue"
import {
  Validator,
  install as VeeValidate,
} from "vee-validate/dist/vee-validate.minimal.esm.js"
import {
  required,
  url,
  digits,
  email,
  min,
  max,
  numeric,
  max_value,
} from "vee-validate/dist/rules.esm.js" // eslint-disable-line

/* Import vee i18n content */
import veeEn from "vee-validate/dist/locale/en"
import veeDa from "vee-validate/dist/locale/da"

/* Local imports */
import i18n from "@/i18n.js"
import ActiveEngagements from "./validators/ActiveEngagements"
import Address from "./validators/Address"
import CandidateParentOrgUnit from "./validators/CandidateParentOrgUnit"
import Cpr from "./validators/Cpr"
import Employee from "./validators/Employee"
import ExistingEngagementAssociations from "./validators/ExistingEngagementAssociations"
import DateInRange from "./validators/DateInRange"
import OrgUnit from "./validators/OrgUnit"

/**
 * Integration with `vue-i18n`:
 * https://github.com/logaretm/vee-validate/blob/2.1.2/docs/guide/localization.md#vuei18n-integration
 */
const veeConfig = {
  i18n,
  dictionary: {
    en: veeEn,
    da: veeDa,
  },
  inject: false,
  delay: 100,
  dateFormat: "DD-MM-YYYY", // TODO: Should probably depend on the locale?
}

Validator.extend("required", required)
Validator.extend("digits", digits)
Validator.extend("min_value", max_value)
Validator.extend("email", email)
Validator.extend("url", url)
Validator.extend("numeric", numeric)
Validator.extend("min", min)
Validator.extend("max", max)

Validator.extend("active_engagements", ActiveEngagements)
Validator.extend("address", Address)
Validator.extend("candidate_parent_org_unit", CandidateParentOrgUnit)
Validator.extend("cpr", Cpr)
Validator.extend("employee", Employee)
Validator.extend("existing_engagement_associations", ExistingEngagementAssociations)
Validator.extend("date_in_range", DateInRange)
Validator.extend("orgunit", OrgUnit)

Vue.use(VeeValidate, veeConfig)

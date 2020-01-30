// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from '@/api/Validate'
import common from './common.js'

export default {
  validate (value, args) {
    let employee = args[0]
    let orgUnit = args[1]
    let validity = args[2]
    let associationUuid = args[3]

    // A plethora of null and false checks to stop everything from breaking
    if (!validity || !validity.from ||
      Object.keys(employee).length === 0 || !employee) {
      return true
    }

    return Validate.existingAssociations(orgUnit, employee, validity,
      associationUuid)
  },

  getMessage: common.getMessage
}

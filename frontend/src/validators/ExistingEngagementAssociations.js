// SPDX-FileCopyrightText: 2021- Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from "@/api/Validate"
import common from "./common.js"

export default {
  validate(value, args) {
    let orgUnit = args[0]
    let validity = args[1]
    let associationUuid = args[2]

    // A plethora of null and false checks to stop everything from breaking
    if (!validity || !validity.from || !orgUnit) {
      return true
    }
    return Validate.existingEngagementAssociations(orgUnit, validity, associationUuid)
  },

  getMessage: common.getMessage,
}

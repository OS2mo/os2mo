// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from "@/api/Validate"
import common from "./common.js"

export default {
  validate(value, args) {
    let orgUnit = args[0]
    let parent = args[1]
    let validity = args[2]

    // A plethora of null and false checks to stop everything from breaking
    if (!orgUnit.uuid || !parent.uuid || !validity || !validity.from) {
      return true
    }

    return Validate.candidateParentOrgUnit(orgUnit, parent, validity)
  },

  getMessage: common.getMessage,
}

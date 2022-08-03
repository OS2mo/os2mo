// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from "@/api/Validate"
import common from "./common.js"

export default {
  validate(value, args) {
    let validity = args[0]
    let employee = value

    // A plethora of null and false checks to stop everything from breaking
    if (
      !validity ||
      !validity.from ||
      Object.keys(employee).length === 0 ||
      !employee
    ) {
      return true
    }

    return Validate.activeEngagements(employee, validity)
  },

  getMessage: common.getMessage,
}

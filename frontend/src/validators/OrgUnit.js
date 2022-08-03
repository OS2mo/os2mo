// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from "@/api/Validate"
import common from "./common.js"

export default {
  validate(value, args) {
    let validity = args[0]
    let orgUuid = args[1]

    if (!orgUuid || !validity || !validity.from) {
      return true
    }

    return Validate.orgUnit(orgUuid, validity)
  },

  getMessage: common.getMessage,
}

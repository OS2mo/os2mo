// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from "@/api/Validate"
import common from "./common.js"

export default {
  validate(value, orgUuids) {
    return Validate.cpr(value, orgUuids[0])
  },

  getMessage: common.getMessage,
}

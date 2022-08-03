// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Validate from "@/api/Validate"
import common from "./common.js"

export default {
  validate(value, args) {
    let addressType = args

    return Validate.address(value, addressType)
  },

  getMessage: common.getMessage,
}

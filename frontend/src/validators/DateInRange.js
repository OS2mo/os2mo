// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const moment = require("moment")

export default {
  getMessage(field, range) {
    if (range.from && !range.to) {
      return `${field} skal være over ${moment(range.from).format("DD-MM-YYYY")}`
    }

    if (range.to && !range.from) {
      return `${field} skal være under ${moment(range.to).format("DD-MM-YYYY")}`
    }

    return `${field} skal være mellem ${moment(range.from).format(
      "DD-MM-YYYY"
    )} og ${moment(range.to).format("DD-MM-YYYY")}`
  },

  validate(value, range) {
    value = new Date(value)

    let aboveMin = range.from ? value >= new Date(range.from) : true
    let belowMax = range.to ? value <= new Date(range.to) : true

    return aboveMin && belowMax
  },
}

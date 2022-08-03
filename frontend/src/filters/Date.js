// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"

const moment = require("moment")

Vue.filter("date", function (value) {
  if (value === null || value === undefined) return
  return moment(value).format("DD-MM-YYYY")
})

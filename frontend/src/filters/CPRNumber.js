// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Vue from "vue"

Vue.filter("CPRNumber", (value) => {
  if (!value) return ""
  if (value.length !== 10) return value

  value = value.toString()
  return value.slice(0, 6) + "-" + value.slice(6)
})

// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"

let username = "bruce",
  password = "bruce"

export async function login(t, user, pass) {
  // Can be called with optional parameters for username and password
  if (user) {
    username = user
  }
  if (pass) {
    password = pass
  }

  if (Selector(".logintext").exists) {
    await t
      .typeText("#username", username)
      .typeText("#password", password)
      .pressKey("down enter")
  }
}

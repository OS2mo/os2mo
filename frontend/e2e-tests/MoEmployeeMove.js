// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import VueSelector from "testcafe-vue-selectors"
import { login } from "./login"

let moment = require("moment")

fixture("MoEmployeeMove")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/liste`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector("#employeeMove")

const searchEmployeeInput = dialog.find(
  '.search-employee .v-autocomplete[data-vv-as="Medarbejder"]'
)
const searchEmployeeItem = searchEmployeeInput.find(".v-autocomplete-list-item")

const engagementSelect = dialog.find('select[data-vv-as="Engagementer"]')
const engagementOption = engagementSelect.find("option")

const unitInput = dialog.find('input[data-vv-as="Flyt til"]')

const fromInput = dialog.find(".from-date input.form-control")

const checkbox = Selector('input[data-vv-as="checkbox"]')

test("Workflow: move employee", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 100 })
    .click(".btn-employee-move")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .click(searchEmployeeInput)
    .typeText(searchEmployeeInput.find("input"), "erik")
    .expect(searchEmployeeItem.withText(" ").visible)
    .ok("no employee found")
    .pressKey("down enter")

    .click(engagementSelect)

    .expect(engagementOption.withText("Fakultet").exists)
    .ok("employee lacks an engagement")
    .click(engagementOption.withText("Fakultet"))

    .click(unitInput)
    .click(dialog.find("li.tree-node span.tree-anchor span"))

    .click(fromInput)

    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(checkbox)
    .expect(checkbox.checked)
    .ok()

    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(/Medarbejderen (.+) er blevet flyttet til (.+)\./)

    .expect(dialog.exists)
    .notOk()
})

test("The input field doesn't swallow characters", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 100 })
    .click(".btn-employee-move")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .click(searchEmployeeInput)
    .typeText(searchEmployeeInput.find("input"), "kaflaflibob")
    .expect(searchEmployeeInput.find("input").value)
    .eql("kaflaflibob", "it ate something")
})

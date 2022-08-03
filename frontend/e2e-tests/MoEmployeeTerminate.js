// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import VueSelector from "testcafe-vue-selectors"
import { login } from "./login"

let moment = require("moment")

fixture("MoEmployeeTerminate")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/liste`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector("#employeeTerminate")

const searchEmployeeField = dialog.find(
  '.search-employee .v-autocomplete[data-vv-as="Medarbejder"]'
)
const searchEmployeeItem = searchEmployeeField.find(".v-autocomplete-list-item")
const searchEmployeeInput = searchEmployeeField.find("input")

const mainSearchField = Selector("div").withAttribute("class", "search")
const mainSearchItem = mainSearchField.find(".autocomplete-result-list > li")
const mainSearchInput = mainSearchField.find(".input-group input")

const presentDetails = Selector(".tabs .detail-present")
const fromField = presentDetails.find("td.column-from")
const toField = presentDetails.find("td.column-to")

const fromInput = dialog.find(".from-date input.form-control")

const checkbox = Selector('input[data-vv-as="checkbox"]')

test("Workflow: terminate employee by search", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 180 })
    .click(".btn-employee-terminate")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .click(searchEmployeeField)
    .typeText(searchEmployeeInput, "Lis")

    .expect(searchEmployeeInput.value)
    .eql("Lis")

    .expect(searchEmployeeItem.withText(" ").visible)
    .ok("no user found - did test data change?")
    .pressKey("down enter")
    .expect(searchEmployeeInput.value)
    .match(/Lis/)

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
    .match(/Medarbejderen (.+) er blevet afsluttet\./)

    .expect(dialog.exists)
    .notOk()
})

test("Workflow: terminate employee from page", async (t) => {
  let today = moment()

  await t
    .click(mainSearchField)
    .typeText(mainSearchField, "erik")
    .expect(mainSearchInput.value)
    .eql("erik")

    .navigateTo(`${baseURL}/medarbejder/236e0a78-11a0-4ed9-8545-6286bb8611c7`)

    .click(
      VueSelector("employee-detail-tabs bTabButtonHelper").withText("Engagementer")
    )

  let fromDate = await fromField.innerText
  let name = "Erik Smidt Hansen"

  await t
    .expect(toField.innerText)
    .eql("")

    .hover("#mo-workflow", { offsetX: 10, offsetY: 180 })
    .click(".btn-employee-terminate")

    .expect(dialog.exists)
    .ok("Opened dialog")

    // TODO: we shouldn't need to fill in the employee
    .click(searchEmployeeField)
    .typeText(searchEmployeeInput, "erik")
    .expect(searchEmployeeItem.withText(" ").visible)
    .ok()
    .pressKey("down enter")
    .expect(searchEmployeeInput.value)
    .eql(name)

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

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .eql(`Medarbejderen ${name} er blevet afsluttet.`)

    .expect(fromField.innerText)
    .eql(fromDate)
    .expect(toField.innerText)
    .eql(today.format("DD-MM-YYYY"))
})

test("Workflow: terminate employee role", async (t) => {
  const today = moment()
  const expectedTerminationDate = today.format("DD-MM-YYYY")
  const entryModal = VueSelector("mo-entry-terminate-modal")
  const terminateDialog = entryModal.find("*[role=dialog]")

  await t
    .click(mainSearchField)
    .typeText(mainSearchField, "Anders")
    .expect(mainSearchInput.value)
    .eql("Anders")

    .navigateTo(`${baseURL}/medarbejder/53181ed2-f1de-4c4a-a8fd-ab358c2c454a`)

    .click(VueSelector("employee-detail-tabs bTabButtonHelper").withText("Roller"))

  let fromDate = await fromField.innerText

  await t
    .expect(entryModal.count)
    .eql(1)

    .click(entryModal.find("button"))

    .expect(terminateDialog.visible)
    .ok()

    .click(entryModal.find(".from-date input"))

    .hover(
      entryModal
        .find(".vdp-datepicker .day:not(.blank)")
        .withText(today.date().toString())
    )
    .click(
      entryModal
        .find(".vdp-datepicker .day:not(.blank)")
        .withText(today.date().toString())
    )
    .expect(entryModal.find(".from-date input").value)
    .eql(expectedTerminationDate)

    .click(entryModal.find("button.btn-primary"))

    .expect(terminateDialog.exists)
    .notOk()

    .expect(fromField.innerText)
    .eql(fromDate)
    .expect(toField.innerText)
    .eql(expectedTerminationDate)

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(
      new RegExp(
        `Et \"Rolle\" felt for (.+) er blevet afsluttet pr\. ${today.format(
          "YYYY-MM-DD"
        )}\.`
      )
    )
})

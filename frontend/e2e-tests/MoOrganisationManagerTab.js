// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import VueSelector from "testcafe-vue-selectors"
import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import { login } from "./login"

let moment = require("moment")

fixture("MoOrganisationManagerTab")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/organisation/2874e1dc-85e6-4269-823a-e1125484dfd3`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector(".modal-content")

// Manager
const searchManagerEmployee = dialog.find('.v-autocomplete[data-vv-as="Medarbejder"]')
const searchManagerItem = searchManagerEmployee.find(".v-autocomplete-list-item")

const managerTypeSelect = dialog.find('.select-manager select[data-vv-as="Ledertype"]')
const managerTypeOption = managerTypeSelect.find("option")

const levelManagerSelect = dialog.find(
  '.select-manager select[data-vv-as="Lederniveau"]'
)
const levelManagerOption = levelManagerSelect.find("option")

const responsibilityManagerSelect = dialog.find(
  '.responsibility-manager select[data-vv-as="Lederansvar"]'
)
const responsibilityManagerOption = responsibilityManagerSelect.find("option")

const fromRemoveInput = dialog.find(".vdp-datepicker__clear-button")
const fromInput = dialog.find(".from-date input.form-control")

test("Workflow: organisation manager tab", async (t) => {
  let today = moment()

  await t
    .click(VueSelector("organisation-detail-tabs bTabButtonHelper").withText("Ledere"))

    // Create manager
    .click(Selector(".btn-outline-primary").withText("Opret ny"))

    .click(managerTypeSelect)
    .click(managerTypeOption.withText("Direktør"))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText("Niveau 3"))

    .click(responsibilityManagerSelect)
    .click(responsibilityManagerOption.withText("Beredskabsledelse"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Et "Leder" felt er blevet oprettet\./)

    .expect(dialog.exists)
    .notOk()

    // Edit manager
    .click(Selector(".edit-entry .btn-outline-primary"))

    .click(searchManagerEmployee)
    .typeText(searchManagerEmployee.find("input"), "jens")

    .expect(searchManagerItem.withText(" ").visible)
    .ok()
    .pressKey("down enter")
    .expect(searchManagerEmployee.find("input").value)
    .match(/Jens/)

    .click(managerTypeSelect)
    .click(managerTypeOption.withText("Leder"))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText("Niveau 1"))

    .click(fromRemoveInput)
    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Et "Leder" felt for (.+) er blevet redigeret\./)

    .expect(dialog.exists)
    .notOk()

    // Terminate association
    .click(Selector(".terminate-entry .btn-outline-danger"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(
      new RegExp(
        `Et \"Leder\" felt for (.+) er blevet afsluttet pr\. ${today.format(
          "YYYY-MM-DD"
        )}\.`
      )
    )
})

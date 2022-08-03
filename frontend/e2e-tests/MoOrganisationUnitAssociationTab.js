// SPDX-FileCopyrightText: 2019-2021 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import VueSelector from "testcafe-vue-selectors"
import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import { login } from "./login"

let moment = require("moment")

fixture("MoOrganisationUnitAssociationTab")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/organisation/2874e1dc-85e6-4269-823a-e1125484dfd3`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector(".modal-content")

// Manager
const searchAssociationEmployee = dialog.find(
  '.v-autocomplete[data-vv-as="Medarbejder"]'
)
const searchAssociationItem = searchAssociationEmployee.find(
  ".v-autocomplete-list-item"
)

dialog.find(".from-date input.form-control")

// Association
const associationTypeSelect = dialog.find(
  '.select-association select[data-vv-as="Tilknytningsrolle"]'
)
const associationTypeOption = associationTypeSelect.find("option")

const fromDateInput = dialog.find(".from-date .form-control")

const primaryAssociationType = dialog.find('select[data-vv-as="Primær"]')
const primaryAssociationTypeOption = primaryAssociationType.find("option")

const submitButton = dialog.find("button .btn .btn-primary")

test("Workflow: organisation association tab empty association", async (t) => {
  let today = moment()

  await t
    .click(
      VueSelector("organisation-detail-tabs bTabButtonHelper").withText("Tilknytninger")
    )
    // Create association
    .click(Selector(".btn-outline-primary").withText("Opret ny"))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText("Projektleder"))

    .click(fromDateInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromDateInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(primaryAssociationType)
    .click(primaryAssociationTypeOption.withText("Sekundær"))
    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Et "Tilknytning" felt er blevet oprettet\./)

    .expect(dialog.exists)
    .notOk()

    // Edit association
    .click(Selector(".edit-entry .btn-outline-primary"))

    .click(searchAssociationEmployee)
    .typeText(searchAssociationEmployee.find("input"), "jens")
    .expect(searchAssociationItem.withText(" ").visible)
    .ok()
    .pressKey("down enter")
    .expect(searchAssociationEmployee.find("input").value)
    .match(/Jens/)

    .click(associationTypeSelect)
    .click(associationTypeOption.withText("Teammedarbejder"))

    .click(dialog.find(".btn-primary"))
    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Et "Tilknytning" felt for (.+) er blevet redigeret\./)

    .expect(dialog.exists)
    .notOk()

    // Terminate association
    .click(Selector(".terminate-entry .btn-outline-danger"))

    .click(fromDateInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromDateInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(
      new RegExp(
        `Et \"Tilknytning\" felt for (.+) er blevet afsluttet pr\. ${today.format(
          "YYYY-MM-DD"
        )}\.`
      )
    )
})

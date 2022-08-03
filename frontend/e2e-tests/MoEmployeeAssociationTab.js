// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import VueSelector from "testcafe-vue-selectors"
import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import { login } from "./login"

let moment = require("moment")

fixture("MoEmployeeAssociationTab")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/liste/`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector(".modal-content")
const searchField = Selector("div").withAttribute("class", "search")

const searchItem = searchField.find(".autocomplete-result-list > li")
const searchInput = searchField.find(".input-group input")

// Association
const parentAssociationInput = dialog.find('input[data-vv-as="Angiv enhed"]')
const associationTypeSelect = dialog.find(
  '.select-association select[data-vv-as="Tilknytningsrolle"]'
)
const associationTypeOption = associationTypeSelect.find("option")
const primaryAssociationType = dialog.find('select[data-vv-as="Primær"]')
const primaryAssociationTypeOption = primaryAssociationType.find("option")
const fromDateInput = dialog.find(".from-date .form-control")
const submitButton = dialog.find("button .btn .btn-primary")

// TODO: Test substitute when conf_db allows
// https://redmine.magenta-aps.dk/issues/34509

test("Workflow: employee association tab", async (t) => {
  let today = moment()

  await t
    .click(searchField)
    .typeText(searchField, "jens")
    .expect(searchInput.value)
    .eql("jens")

    .expect(searchItem.withText(" ").visible)
    .ok("no user found - did test data change?")
    .pressKey("down enter")

    .click(
      VueSelector("employee-detail-tabs bTabButtonHelper").withText("Tilknytninger")
    )

    // Create association
    .click(Selector(".btn-outline-primary"))

    .click(primaryAssociationType)
    .click(primaryAssociationTypeOption.withText("Sekundær"))

    .click(parentAssociationInput)
    .click(dialog.find(".unit-association span.tree-anchor"))

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

    .click(dialog.find(".btn-primary"))

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Et "Tilknytning" felt er blevet oprettet\./)

    // Edit association
    .click(Selector(".edit-entry .btn-outline-primary"))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText("Teammedarbejder"))

    .click(dialog.find(".btn-primary"))

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Et "Tilknytning" felt for (.+) er blevet redigeret\./)

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

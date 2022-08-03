// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import VueSelector from "testcafe-vue-selectors"
import { login } from "./login"

let moment = require("moment")

fixture("MoOrganisationUnitCreate")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/organisation/2874e1dc-85e6-4269-823a-e1125484dfd3`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector("#orgUnitCreate")

const timeSelect = dialog.find('select[data-vv-as="Tidsregistrering"]')
const timeOption = timeSelect.find("option")

const levelSelect = dialog.find('select[data-vv-as="Enhedsniveau"]')
const levelOption = levelSelect.find("option")

const unitSelect = dialog.find('select[data-vv-as="Enhedstype"]')
const unitOption = unitSelect.find("option")

const addressInput = dialog.find('.v-autocomplete[data-vv-as="Postadresse"]')
const addressItem = addressInput.find(".v-autocomplete-list-item label")

const addressVisibility = dialog.find('select[data-vv-as="Synlighed"]')
const addressVisibilityOption = addressVisibility.find("option")

const parentInput = dialog.find('input[data-vv-as="Angiv overenhed"]')

const fromInput = dialog.find(".from-date input.form-control")

const addressTypeSelect = dialog
  .find('.address select[data-vv-as="Adressetype"]')
  .nth(-1)
const addressTypeOption = addressTypeSelect.find("option")

const addressEmailInput = dialog.find('input[data-vv-as="Email"]')

test("Workflow: create unit", async (t) => {
  let today = moment()

  // Some notes:
  //
  // You may notice that we have a few 'expects' waiting for an
  // autocomplete to be visible. They exist to ensure that the
  // autocomplete is properly rendered prior to attempting to select
  // an item. This can occur when TestCafe runs at full speed.
  //
  // Likewise, not hovering over an item prior to clicking it can lead
  // to the click not having any effect.
  //
  // We do autocomplete selection using the keyboard. In order to make
  // this work, we use our own, fixed, version of 'v-autocomplete'
  // that suppresses form submit in these cases.
  //
  // I quite deliberately added a lot of expects that verify that e.g.
  // selecting something in a drop-down has the desired effect. This
  // ensures that we yield more helpful error messages should the test
  // fail, rather than merely failing at form submit.

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-unit-create")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .typeText(dialog.find('input[data-vv-as="Navn"]'), "Økonomi")

    .click(unitSelect)
    .click(unitOption.withText("Fakultet"))

    .click(parentInput)
    .click(dialog.find("li.tree-node span.tree-anchor span"))

    .click(timeSelect)
    .click(timeOption.withText("Tjenestetid"))

    .click(levelSelect)
    .click(levelOption.withText("Niveau 10"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(dialog.find(".btn-outline-success"))

    .click(addressTypeSelect)
    .click(addressTypeOption.withText("Postadresse"))

    .click(addressInput)
    .typeText(addressInput.find("input"), "hovedvejen 2")
    .expect(addressItem.withText(" ").visible)
    .ok()
    .pressKey("down enter")
    .expect(addressInput.find("input").value)
    .eql("Hovedvejen 27, 8361 Hasselager")

    .click(dialog.find(".btn-outline-success"))

    .click(addressTypeSelect)
    .click(addressTypeOption.withText("Telefon"))

    .typeText(dialog.find('input[data-vv-as="Telefon"]'), "44772000")

    .click(addressVisibility)
    .click(addressVisibilityOption.nth(1))

    .click(dialog.find(".btn-outline-success"))

    .click(addressTypeSelect)
    .click(addressTypeOption.withText("Email"))

    .click(addressEmailInput)
    .typeText(addressEmailInput, "magenta@gmail.dk")

    .click(dialog.find(".btn-primary"))

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(/Organisationsenheden (.+) er blevet oprettet under (.+)\./)

    .expect(dialog.exists)
    .notOk()

  // TODO: verify that the unit was actually created, somehow?
})

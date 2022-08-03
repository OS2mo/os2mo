// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import VueSelector from "testcafe-vue-selectors"
import { login } from "./login"

let moment = require("moment")

fixture("MoOrganisationUnitMove")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/organisation/fa2e23c9-860a-4c90-bcc6-2c0721869a25`)
  .beforeEach(async (t) => {
    await login(t)
  })

const dialog = Selector("#orgUnitMove")

const parentInput = dialog.find('.parentUnit input[data-vv-as="Angiv ny overenhed"]')

const fromInput = dialog.find(".moveDate input.form-control")

const tree = VueSelector("mo-tree-view")

const currentUnitName = Selector(".orgunit .orgunit-name").with({
  visibilityCheck: true,
})

test("Workflow: move unit", async (t) => {
  let today = moment()

  await t
    .expect(currentUnitName.innerText)
    .eql("IT-Support")
    .expect(tree.find(".selected").exists)
    .ok()
    .expect(tree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Lønorganisation",
      {
        "Overordnet Enhed": [
          "> Humanistisk fakultet",
          "Samfundsvidenskabelige fakultet",
          {
            "Skole og Børn": ["=+= IT-Support =+="],
          },
          "Social og sundhed",
        ],
      },
    ])

    .hover("#mo-workflow", { offsetX: 10, offsetY: 90 })
    .click(".btn-unit-move")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .click(parentInput)
    .click(
      dialog
        .find(".parentUnit .tree-content")
        .withText("Overordnet Enhed")
        .find(".tree-arrow")
    )
    .click(dialog.find(".parentUnit .tree-anchor").withText("Social og sundhed"))
    .expect(dialog.find('.parentUnit input[data-vv-as="Angiv ny overenhed"]').value)
    .eql("Social og sundhed")

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

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(/Organisationsenheden (.+) er blevet flyttet til (.+)\./)

    .expect(dialog.exists)
    .notOk()

    .expect(tree.find(".selected").exists)
    .ok()

  await t
    .expect(tree.getVue(({ computed }) => computed.contents))
    .eql([
      "> Lønorganisation",
      {
        "Overordnet Enhed": [
          "> Humanistisk fakultet",
          "Samfundsvidenskabelige fakultet",
          "Skole og Børn",
          {
            "Social og sundhed": ["=+= IT-Support =+="],
          },
        ],
      },
    ])
    .expect(Selector(".orgunit-name").textContent)
    .eql("IT-Support")
    .expect(Selector(".orgunit-location").textContent)
    .eql("Overordnet Enhed\\Social og sundhed")
    .expect(Selector(".detail-present .parent-name").textContent)
    .match(/Social og sundhed/)

    .click(Selector(".detail-past .card-header"))
    .expect(Selector(".detail-past .parent-name").textContent)
    .match(/Skole og Børn/)

    .click(Selector(".detail-future .card-header"))
    .expect(Selector(".detail-future .parent-name").exists)
    .notOk()
})

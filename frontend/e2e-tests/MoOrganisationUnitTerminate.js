// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import VueSelector from "testcafe-vue-selectors"
import { login } from "./login"

let moment = require("moment")

fixture("MoOrganisationUnitTerminate")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/organisation/`)
  .beforeEach(async (t) => {
    await login(t)
  })

const createDialog = Selector("#orgUnitCreate")

const createTimeSelect = createDialog.find('select[data-vv-as="Tidsregistrering"]')
const createTimeOption = createTimeSelect.find("option")

const levelSelect = createDialog.find('select[data-vv-as="Enhedsniveau"]')
const levelOption = levelSelect.find("option")

const createUnitSelect = createDialog.find('select[data-vv-as="Enhedstype"]')
const createUnitOption = createUnitSelect.find("option")

const createParentInput = createDialog.find('input[data-vv-as="Angiv overenhed"]')

const createFromInput = createDialog.find(".from-date input.form-control")

const dialog = Selector("#orgUnitTerminate")

const parentInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const fromInput = dialog.find(".from-date input.form-control")

const renameDialog = Selector("#orgUnitRename")

const renameFromInput = renameDialog.find(".from-date input.form-control")

const lastLogMessage = VueSelector("MoLog").find(".alert").nth(0)

test("Workflow: terminate and rename org unit, selecting date first", async (t) => {
  let today = moment()
  let yesterday = moment().subtract(1, "days")
  let lastMonth = moment().date(1).subtract(1, "months")
  let thisMonth = moment().date(1)
  let nextMonth = moment().date(1).add(1, "months")
  let lastDayOfNextMonth = moment().date(1).add(2, "months").subtract(1, "days")
  let twoMonths = moment().date(1).add(2, "months")

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-unit-create")

    .expect(createDialog.exists)
    .ok("Opened dialog")

    .click(createFromInput)

    .hover(createDialog.find(".vdp-datepicker .prev"))
    .click(createDialog.find(".vdp-datepicker .prev"))

    .hover(createDialog.find(".vdp-datepicker .day:not(.blank)"))
    .click(createDialog.find(".vdp-datepicker .day:not(.blank)"))
    .expect(createFromInput.value)
    .eql(lastMonth.format("DD-MM-YYYY"))

    .typeText(createDialog.find('input[data-vv-as="Navn"]'), "Hjørring VM 2018")

    .click(createUnitSelect)
    .click(createUnitOption.withText("Institut"))

    .click(createParentInput)
    .click(createDialog.find("li.tree-node span.tree-anchor span"))

    .click(createTimeSelect)
    .click(createTimeOption.withText("Tjenestetid"))

    .click(levelSelect)
    .click(levelOption.withText("Niveau 10"))

    .click(createDialog.find(".btn-primary"))

  const logPattern = /Organisationsenheden (.+) er blevet oprettet under (.+)./

  await t
    .expect(lastLogMessage.innerText)
    .match(logPattern)

    .expect(createDialog.exists)
    .notOk()

  const match = logPattern.exec(await lastLogMessage.innerText)
  const name = match[1]
  const parent = match[2]

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 130 })
    .click(".btn-unit-terminate")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .click(fromInput)

    .hover(dialog.find(".vdp-datepicker .next"))
    .click(dialog.find(".vdp-datepicker .next"))
    .click(dialog.find(".vdp-datepicker .next"))

    .hover(dialog.find(".vdp-datepicker .day:not(.blank)"))
    .click(dialog.find(".vdp-datepicker .day:not(.blank)"))

    .expect(fromInput.value)
    .eql(twoMonths.format("DD-MM-YYYY"))

    .click(parentInput)
    .click(dialog.find(".tree-node").withText("Lønorganisation").find(".tree-arrow"))
    .click(dialog.find(".tree-anchor").withText("VM 2018"))

    // verify that the details render as expected
    .expect(dialog.find(".detail-present ul.name").withText("VM 2018").exists)
    .ok()

    .click(dialog.find(".btn-primary"))

    .expect(lastLogMessage.innerText)
    .eql(
      `Organisationsenheden ${name} er blevet afsluttet pr. ${twoMonths.format(
        "YYYY-MM-DD"
      )}.`
    )

    .expect(dialog.exists)
    .notOk()

    .hover("#mo-workflow", { offsetX: 10, offsetY: 50 })
    .click(".btn-unit-rename")

    .expect(renameDialog.exists)
    .ok("Opened dialog")

    .click(renameFromInput)
    .hover(
      renameDialog
        .find(".vdp-datepicker .day:not(.blank)")
        .withText(today.date().toString())
    )
    .click(
      renameDialog
        .find(".vdp-datepicker .day:not(.blank)")
        .withText(today.date().toString())
    )
    .expect(renameFromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .typeText(renameDialog.find('input[data-vv-as="Nyt navn"]'), "Hjørring VM 2019")

    .click(renameDialog.find(".btn-primary"))

    .expect(lastLogMessage.innerText)
    .eql(`Organisationsenheden ${name} er blevet omdøbt til Hjørring VM 2019.`)

    .expect(renameDialog.exists)
    .notOk()

    .expect(Selector(".orgunit .orgunit-name").innerText)
    .eql("Hjørring VM 2019")

    .click(Selector(".detail-future .card-header"))
    .click(Selector(".detail-past .card-header"))

  // verify the results
  await t
    .expect(Selector(".detail-future tr").count)
    .eql(1)
    .expect(Selector(".detail-present tr").count)
    .eql(2)
    .expect(Selector(".detail-past tr").count)
    .eql(2)

    .expect(Selector(".detail-future tr").textContent)
    .eql("Intet at vise")

  let present = await Selector(".detail-present tr").nth(1).innerText
  let past = await Selector(".detail-past tr").nth(1).innerText

  let actualPast = past
    .split(/[\n\t]+/)
    .map((s) => s.trim())
    .join("|")
  let actualPresent = present
    .split(/[\n\t]+/)
    .map((s) => s.trim())
    .join("|")

  let expectedPast = [
    "Hjørring VM 2018",
    "Institut",
    "Niveau 10",
    "Tjenestetid",
    "Lønorganisation",
    lastMonth.format("DD-MM-YYYY"),
    yesterday.format("DD-MM-YYYY"),
    "",
  ].join("|")
  let expectedPresent = [
    "Hjørring VM 2019",
    "Institut",
    "Niveau 10",
    "Tjenestetid",
    "Lønorganisation",
    today.format("DD-MM-YYYY"),
    twoMonths.format("DD-MM-YYYY"),
    "",
  ].join("|")

  await t
    .expect(actualPast)
    .eql(expectedPast)
    .expect(actualPresent)
    .eql(expectedPresent)
})

test("Workflow: terminate and rename org unit, selecting unit first", async (t) => {
  let lastMonth = moment().date(1).subtract(1, "months")
  let lastDayOfThisMonth = moment().date(1).add(1, "months").subtract(1, "days")
  let nextMonth = moment().date(1).add(1, "months")
  let lastDayOfNextMonth = moment().date(1).add(2, "months").subtract(1, "days")
  let twoMonths = moment().date(1).add(2, "months")

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-unit-create")

    .expect(createDialog.exists)
    .ok("Opened dialog")

    .typeText(createDialog.find('input[data-vv-as="Navn"]'), "Hjørring VM 2018")

    .click(createUnitSelect)
    .click(createUnitOption.withText("Institut"))

    .click(createParentInput)
    .click(createDialog.find("li.tree-node span.tree-anchor span"))

    .click(createTimeSelect)
    .click(createTimeOption.withText("Tjenestetid"))

    .click(levelSelect)
    .click(levelOption.withText("Niveau 10"))

    .click(createFromInput)

    .hover(createDialog.find(".vdp-datepicker .prev"))
    .click(createDialog.find(".vdp-datepicker .prev"))

    .hover(createDialog.find(".vdp-datepicker .day:not(.blank)"))
    .click(createDialog.find(".vdp-datepicker .day:not(.blank)"))
    .expect(createFromInput.value)
    .eql(lastMonth.format("DD-MM-YYYY"))

    .click(createDialog.find(".btn-primary"))

  const logPattern = /Organisationsenheden (.+) er blevet oprettet under (.+)./

  await t
    .expect(lastLogMessage.innerText)
    .match(logPattern)

    .expect(createDialog.exists)
    .notOk()

  const match = logPattern.exec(await lastLogMessage.innerText)
  const name = match[1]
  const parent = match[2]

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 130 })
    .click(".btn-unit-terminate")

    .expect(dialog.exists)
    .ok("Opened dialog")

    .click(parentInput)
    .click(dialog.find(".tree-node").withText("Lønorganisation").find(".tree-arrow"))
    .click(dialog.find(".tree-anchor").withText("VM 2018"))

    .click(fromInput)

    .hover(dialog.find(".vdp-datepicker .next"))
    .click(dialog.find(".vdp-datepicker .next"))
    .click(dialog.find(".vdp-datepicker .next"))

    .hover(dialog.find(".vdp-datepicker .day:not(.blank)"))
    .click(dialog.find(".vdp-datepicker .day:not(.blank)"))

    .expect(fromInput.value)
    .eql(twoMonths.format("DD-MM-YYYY"))

    // verify that the details render as expected
    .expect(dialog.find(".detail-present ul.name").withText("VM 2018").exists)
    .ok()

    .click(dialog.find(".btn-primary"))

    .expect(lastLogMessage.innerText)
    .eql(
      `Organisationsenheden ${name} er blevet afsluttet pr. ${twoMonths.format(
        "YYYY-MM-DD"
      )}.`
    )

    .expect(dialog.exists)
    .notOk()

    .hover("#mo-workflow", { offsetX: 10, offsetY: 50 })
    .click(".btn-unit-rename")

    .expect(renameDialog.exists)
    .ok("Opened dialog")

    .click(renameFromInput)
    .click(renameDialog.find(".vdp-datepicker .next"))
    .hover(renameDialog.find(".vdp-datepicker .day:not(.blank)"))
    .click(renameDialog.find(".vdp-datepicker .day:not(.blank)"))
    .expect(renameFromInput.value)
    .eql(nextMonth.format("DD-MM-YYYY"))

    .typeText(renameDialog.find('input[data-vv-as="Nyt navn"]'), "Hjørring VM 2019")

    .click(renameDialog.find(".btn-primary"))

    .expect(renameDialog.exists)
    .notOk()

    .expect(lastLogMessage.innerText)
    .eql(`Organisationsenheden ${name} er blevet omdøbt til Hjørring VM 2019.`)

    .expect(Selector(".orgunit .orgunit-name").innerText)
    .eql("Hjørring VM 2018")

    .click(Selector(".detail-future .card-header"))
    .click(Selector(".detail-past .card-header"))

  // verify the results
  await t
    .expect(Selector(".detail-future tr").count)
    .eql(2)
    .expect(Selector(".detail-present tr").count)
    .eql(2)
    .expect(Selector(".detail-past tr").count)
    .eql(1)

    .expect(Selector(".detail-past tr").textContent)
    .eql("Intet at vise")

  let present = await Selector(".detail-present tr").nth(1).innerText
  let future = await Selector(".detail-future tr").nth(1).innerText

  let actualPresent = present
    .split(/[\n\t]+/)
    .map((s) => s.trim())
    .join("|")
  let actualFuture = future
    .split(/[\n\t]+/)
    .map((s) => s.trim())
    .join("|")

  let expectedPresent = [
    "Hjørring VM 2018",
    "Institut",
    "Niveau 10",
    "Tjenestetid",
    "Lønorganisation",
    lastMonth.format("DD-MM-YYYY"),
    lastDayOfThisMonth.format("DD-MM-YYYY"),
    "",
  ].join("|")
  let expectedFuture = [
    "Hjørring VM 2019",
    "Institut",
    "Niveau 10",
    "Tjenestetid",
    "Lønorganisation",
    nextMonth.format("DD-MM-YYYY"),
    twoMonths.format("DD-MM-YYYY"),
    "",
  ].join("|")

  await t
    .expect(actualPresent)
    .eql(expectedPresent)
    .expect(actualFuture)
    .eql(expectedFuture)
})

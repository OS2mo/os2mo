// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { Selector } from "testcafe"
import { baseURL, setup, teardown } from "./support"
import VueSelector from "testcafe-vue-selectors"
import { login } from "./login"

let moment = require("moment")

const dialog = Selector("#employeeCreate")

// CPR Number
const checkbox = dialog.find('input[data-vv-as="checkbox"]')
const cprInput = dialog.find('input[data-vv-as="CPR nummer"]')

// Engagement
const engagementCheckbox = dialog.find(".container")

const parentEngagementInput = dialog.find('input[data-vv-as="Angiv enhed"]')

const engagementBoarder = dialog.find(".btn-engagement")
const engagementButton = engagementBoarder.find(".btn-outline-success")

const jobFunctionEngagementSelect = dialog.find(
  'select[data-vv-as="Stillingsbetegnelse"]'
)
const jobFunctionEngagementOption = jobFunctionEngagementSelect.find("option")

const primaryEngagementSelect = dialog.find(
  '.btn-engagement select[data-vv-as="Primær"]'
)
const primaryEngagementOption = primaryEngagementSelect.find("option")

const engagementTypeSelect = dialog.find('select[data-vv-as="Engagementstype"]')
const engagementTypeOption = engagementTypeSelect.find("option")

const fromInput = dialog.find(".from-date input.form-control")

// Address
const addressTypeSelect = dialog.find('select[data-vv-as="Adressetype"]')
const addressTypeOption = addressTypeSelect.find("option")

const addressInput = dialog.find('input[data-vv-as="Telefon"]')

const addressVisibility = dialog.find('select[data-vv-as="Synlighed"]')
const addressVisibilityOption = addressVisibility.find("option")

// Association
const associationCheckbox = dialog.find('[data-vv-as="Primær tilknytning"] .container')

const parentAssociationInput = dialog.find(
  '.unit-association input[data-vv-as="Angiv enhed"]'
)

const primaryAssociationSelect = dialog.find(
  '.btn-association select[data-vv-as="Primær"]'
)
const primaryAssociationOption = primaryAssociationSelect.find("option")

const associationTypeSelect = dialog.find(
  '.select-association select[data-vv-as="Tilknytningsrolle"]'
)
const associationTypeOption = associationTypeSelect.find("option")

// Role
const parentRoleInput = dialog.find('.unit-role input[data-vv-as="Angiv enhed"]')

const roleTypeSelect = dialog.find('.select-role select[data-vv-as="Rolletype"]')
const roleTypeOption = roleTypeSelect.find("option")

// IT System
const itSystemSelect = dialog.find('.select-itSystem select[data-vv-as="IT systemer"]')
const itSystemOption = itSystemSelect.find("option")
const itSystemInput = dialog.find('.input-itSystem input[data-vv-as="Kontonavn"]')

// Manager
const parentManagerInput = dialog.find('.unit-manager input[data-vv-as="Angiv enhed"]')

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

// Search field
const searchField = Selector("div").withAttribute("class", "search")
const searchFieldItem = searchField.find(".autocomplete-result-list")

fixture("MoEmployeeCreate")
  .before(setup)
  .after(teardown)
  .page(`${baseURL}/medarbejder/liste/`)
  .beforeEach(async (t) => {
    await login(t)
  })

test("Workflow: create employee", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-employee-create")

    .expect(dialog.exists)
    .ok("Opened dialog")

    // CPR Number
    .typeText(cprInput, "010101")
    .expect(dialog.find(".alert-danger").withText("Ugyldigt").exists)
    .ok()

    .typeText(cprInput, "-0000")
    .expect(Selector(".alert-danger").withText("ikke i registret").exists)
    .ok()

    .selectText(cprInput)
    .pressKey("delete")
    .expect(dialog.find(".alert").visible)
    .notOk()

    .typeText(cprInput, "2003920008")
    .click(checkbox)
    .expect(checkbox.checked)
    .ok()

    // Engagement
    .click(engagementButton)

    .click(parentEngagementInput)
    .expect(dialog.find("span.tree-anchor").exists)
    .ok()
    .click(dialog.find("span.tree-anchor"))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText("Specialist"))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText("Ansat"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(primaryEngagementSelect)
    .click(primaryEngagementOption.withText("Sekundær"))

    // Address
    .click(dialog.find(".btn-address .btn-outline-success"))

    .click(addressTypeSelect)
    .click(addressTypeOption.withText("Telefon"))

    .click(addressInput)
    .typeText(addressInput, "35502010")

    .click(addressVisibility)
    .click(addressVisibilityOption.nth(1))

    // Association
    .click(dialog.find(".btn-association .btn-outline-success"))

    .click(parentAssociationInput)
    .click(dialog.find(".unit-association span.tree-anchor"))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText("Projektleder"))

    .click(primaryAssociationSelect)
    .click(primaryAssociationOption.withText("Sekundær"))

    // Role
    .click(dialog.find(".btn-role .btn-outline-success"))

    .click(parentRoleInput)
    .click(dialog.find(".unit-role span.tree-anchor"))

    .click(roleTypeSelect)
    .click(roleTypeOption.withText("Tillidsrepræsentant"))

    // IT System
    .click(dialog.find(".btn-itSystem .btn-outline-success"))

    .click(itSystemSelect)
    .click(itSystemOption.withText("Active Directory"))
    .click(itSystemInput)
    .typeText(itSystemInput, "chefen")

    // Manager
    .click(dialog.find(".btn-manager .btn-outline-success"))

    .click(parentManagerInput)
    .click(dialog.find(".unit-manager .tree-anchor"))

    .click(managerTypeSelect)
    .click(managerTypeOption.withText("Direktør"))

    .click(levelManagerSelect)
    .click(levelManagerOption.withText("Niveau 3"))

    .click(responsibilityManagerSelect)
    .click(responsibilityManagerOption.withText("Beredskabsledelse"))

    // Submit button
    .click(dialog.find(".btn-primary"))

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(0).innerText)
    .match(/Medarbejderen (.+) er blevet oprettet under (.+)\./)

    // Verify that we can search for the newly created employee
    .navigateTo(`${baseURL}/medarbejder/liste/`)
    .click(searchField)
    .typeText(searchField.find("input"), "sig")
    .expect(searchFieldItem.withText("Signe Kristensen").visible)
    .ok()
})

test("Workflow: create employee with role only", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-employee-create")

    .expect(dialog.exists)
    .ok("Opened dialog")

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), "2003920009")
    .click(checkbox)
    .expect(checkbox.checked)
    .ok()

    // Engagement
    .click(engagementButton)

    .click(parentEngagementInput)
    .click(dialog.find("span.tree-anchor"))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText("Skolepsykolog"))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText("Ansat"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(primaryEngagementSelect)
    .click(primaryEngagementOption.withText("Sekundær"))
    // Role
    .click(dialog.find(".btn-role .btn-outline-success"))

    .click(parentRoleInput)
    .click(dialog.find(".unit-role span.tree-anchor"))

    .click(roleTypeSelect)
    .click(roleTypeOption.withText("Tillidsrepræsentant"))

    // Submit button
    .click(dialog.find(".btn-primary"))

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(/Medarbejderen (.+) er blevet oprettet under (.+)\./)
    .expect(Selector(".card-title").textContent)
    .match(/Oliver Jensen \(200392-0009\)/)
    .expect(VueSelector("bTabButtonHelper").exists)
    .ok()
    .expect(VueSelector("bTabButtonHelper").withText("Roller").exists)
    .ok()
    .click(VueSelector("bTabButtonHelper").withText("Roller"))
    .expect(Selector("ul.role_type-name").textContent)
    .match(/Tillidsrepræsentant/)
})

test("Workflow: create employee with association to unit lacking address", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-employee-create")

    .expect(dialog.exists)
    .ok("Opened dialog")

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), "2003920010")
    .click(checkbox)
    .expect(checkbox.checked)
    .ok()

    // Engagement
    .click(engagementButton)

    .click(parentEngagementInput)
    .expect(dialog.find("span.tree-anchor").exists)
    .ok()
    .click(dialog.find("span.tree-anchor"))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText("Skolepsykolog"))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText("Ansat"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(primaryEngagementSelect)
    .click(primaryEngagementOption.withText("Sekundær"))

    // Association
    .click(dialog.find(".btn-association .btn-outline-success"))

    .click(parentAssociationInput)
    .expect(dialog.find(".unit-association .tree-arrow").exists)
    .ok()
    .click(dialog.find(".unit-association .tree-arrow"), { offsetX: 0, offsetY: 0 })
    .expect(
      dialog
        .find(".unit-association .tree-node .tree-content")
        .withText("Social og sundhed").exists
    )
    .ok()
    .click(
      dialog
        .find(".unit-association .tree-node .tree-content")
        .withText("Social og sundhed")
    )

    .click(primaryAssociationSelect)
    .click(primaryAssociationOption.withText("Sekundær"))

    .click(associationTypeSelect)
    .click(associationTypeOption.withText("Projektleder"))

    // Submit button
    .click(dialog.find(".btn-primary"))

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(/Medarbejderen (.+) er blevet oprettet under (.+)\./)

    // verify whom we created
    .expect(Selector(".card-title").textContent)
    .match(/Sarah Mortensen \(200392-0010\)/)

    // and the association
    .click(VueSelector("bTabButtonHelper").withText("Tilknytninger"))
    .expect(Selector("ul.first_party_association_type-name").textContent)
    .match(/Projektleder/)
})

test("Workflow: create employee with itsystem only", async (t) => {
  let today = moment()

  await t
    .hover("#mo-workflow", { offsetX: 10, offsetY: 10 })
    .click(".btn-employee-create")

    .expect(dialog.exists)
    .ok("Opened dialog")

    // CPR Number
    .typeText(dialog.find('input[data-vv-as="CPR nummer"]'), "2104930010")
    .click(checkbox)
    .expect(checkbox.checked)
    .ok()

    // Engagement
    .click(engagementButton)

    .click(parentEngagementInput)
    .click(dialog.find("span.tree-anchor"))

    .click(jobFunctionEngagementSelect)
    .click(jobFunctionEngagementOption.withText("Bogopsætter"))

    .click(engagementTypeSelect)
    .click(engagementTypeOption.withText("Ansat"))

    .click(fromInput)
    .hover(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .click(
      dialog.find(".vdp-datepicker .day:not(.blank)").withText(today.date().toString())
    )
    .expect(fromInput.value)
    .eql(today.format("DD-MM-YYYY"))

    .click(primaryEngagementSelect)
    .click(primaryEngagementOption.withText("Sekundær"))

    // IT System
    .click(dialog.find(".btn-itSystem .btn-outline-success"))

    .click(itSystemSelect)
    .click(itSystemOption.withText("SAP"))
    .click(itSystemInput)
    .typeText(itSystemInput, "admin")

    // Submit button
    .click(dialog.find(".btn-primary"))

    .expect(dialog.exists)
    .notOk()

    .expect(VueSelector("MoLog").find(".alert").nth(-1).innerText)
    .match(/Medarbejderen (.+) er blevet oprettet under (.+)\./)
    .expect(Selector(".card-title").textContent)
    .match(/Nanna Jensen \(210493-0010\)/)
    .expect(VueSelector("bTabButtonHelper").exists)
    .ok()
    .expect(VueSelector("bTabButtonHelper").withText("IT").exists)
    .ok()
    .click(VueSelector("bTabButtonHelper").withText("IT"))
    .expect(VueSelector("mo-link").filter(".itsystem-name").textContent)
    .match(/SAP/)
    .expect(VueSelector("mo-link").filter(".user_key").textContent)
    .match(/admin/)
})
